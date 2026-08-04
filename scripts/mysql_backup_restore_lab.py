import argparse
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REQUIRED_TABLES = ["customers", "products", "inventory", "sales_orders", "issues"]


class LabError(RuntimeError):
    pass


class MysqlLab:
    def __init__(self, compose_file: str, db_name: str, output_dir: Path, base_url: str = "http://localhost"):
        if db_name != "erp_demo":
            raise LabError("Refusing restore: target database must be erp_demo")
        self.compose_file = compose_file
        self.db_name = db_name
        self.output_dir = output_dir
        self.backup_dir = ROOT_DIR / "backups"
        self.base_url = base_url.rstrip("/")
        self.lines: list[str] = []
        self.http_lines: list[str] = []

    def log(self, status: str, message: str) -> None:
        line = f"[{status}] {message}"
        self.lines.append(line)
        print(line, flush=True)

    def docker_mysql(self, sql: str, database: str | None = None, check: bool = True) -> subprocess.CompletedProcess:
        db_arg = f" {shlex.quote(database)}" if database else ""
        shell = f'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --default-character-set=utf8mb4{db_arg}'
        return subprocess.run(
            ["docker", "compose", "-f", self.compose_file, "exec", "-T", "mysql", "sh", "-lc", shell],
            cwd=ROOT_DIR,
            input=sql,
            text=True,
            capture_output=True,
            check=check,
        )

    def dump_database(self, backup_file: Path) -> None:
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        shell = (
            'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot '
            "--single-transaction --routines --triggers --default-character-set=utf8mb4 "
            f"{shlex.quote(self.db_name)}"
        )
        result = subprocess.run(
            ["docker", "compose", "-f", self.compose_file, "exec", "-T", "mysql", "sh", "-lc", shell],
            cwd=ROOT_DIR,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise LabError(f"mysqldump failed: {result.stderr.strip()}")
        backup_file.write_text(result.stdout, encoding="utf-8", newline="\n")
        self.validate_dump_file(backup_file)
        self.log("PASS", f"Created backup file {backup_file}")

    def validate_dump_file(self, backup_file: Path) -> None:
        if not backup_file.exists():
            raise LabError(f"Backup file not found: {backup_file}")
        if backup_file.stat().st_size <= 0:
            raise LabError(f"Backup file is empty: {backup_file}")
        content = backup_file.read_text(encoding="utf-8", errors="replace")
        upper = content.upper()
        if "CREATE TABLE" not in upper:
            raise LabError("Backup validation failed: CREATE TABLE not found")
        if "INSERT INTO" not in upper:
            raise LabError("Backup validation failed: INSERT INTO not found")
        self.log("PASS", "Backup file structure validation passed")

    def count_table(self, database: str, table: str) -> int:
        result = self.docker_mysql(f"SELECT COUNT(*) FROM `{table}`;\n", database=database)
        return int(result.stdout.strip().splitlines()[-1])

    def collect_counts(self, database: str) -> dict[str, int]:
        counts = {table: self.count_table(database, table) for table in REQUIRED_TABLES}
        self.log("PASS", f"{database} counts: {json.dumps(counts, sort_keys=True)}")
        return counts

    def import_dump(self, database: str, backup_file: Path) -> None:
        sql = backup_file.read_text(encoding="utf-8")
        result = self.docker_mysql(sql, database=database, check=False)
        if result.returncode != 0:
            raise LabError(f"Import failed for {database}: {result.stderr.strip()}")

    def validate_database(self, database: str) -> None:
        for table in REQUIRED_TABLES:
            rows = self.count_table(database, table)
            self.log("PASS", f"{database}.{table} SELECT COUNT(*) = {rows}")

    def request_json(self, path: str, timeout: int = 60) -> dict:
        deadline = time.time() + timeout
        last_error = ""
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"{self.base_url}{path}", timeout=10) as response:
                    status = response.status
                    payload = json.loads(response.read().decode("utf-8"))
                if status != 200:
                    raise LabError(f"HTTP status was {status}")
                if payload.get("code") != 0:
                    raise LabError(f"JSON code was {payload.get('code')}")
                self.http_lines.append(f"[PASS] GET {path} status=200 code=0")
                return payload
            except Exception as exc:
                last_error = str(exc)
                time.sleep(2)
        self.http_lines.append(f"[FAIL] GET {path}: {last_error}")
        raise LabError(f"GET {path} failed after restore: {last_error}")

    def validate_application_http(self) -> None:
        health = self.request_json("/health").get("data")
        if not isinstance(health, dict) or health.get("status") != "ok" or health.get("database") != "mysql":
            raise LabError(f"Invalid /health data after restore: {health}")
        self.http_lines.append("[PASS] /health data.status=ok data.database=mysql")

        customers = self.request_json("/api/customers").get("data")
        if not isinstance(customers, list) or not customers:
            raise LabError("/api/customers did not return a non-empty list after restore")
        self.http_lines.append(f"[PASS] /api/customers returned {len(customers)} rows")

        dashboard = self.request_json("/api/dashboard").get("data")
        if not isinstance(dashboard, dict) or not dashboard:
            raise LabError("/api/dashboard did not return a non-empty object after restore")
        self.http_lines.append("[PASS] /api/dashboard returned valid data")
        self.log("PASS", "Application HTTP validation passed after MySQL restore")

    def restore_formal_database(self, backup_file: Path, rollback_file: Path) -> None:
        try:
            self.docker_mysql(
                f"DROP DATABASE IF EXISTS `{self.db_name}`;\n"
                f"CREATE DATABASE `{self.db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n"
            )
            self.import_dump(self.db_name, backup_file)
        except Exception as exc:
            self.log("FAIL", f"Formal restore failed, attempting rollback: {exc}")
            self.docker_mysql(
                f"DROP DATABASE IF EXISTS `{self.db_name}`;\n"
                f"CREATE DATABASE `{self.db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n"
            )
            self.import_dump(self.db_name, rollback_file)
            raise

    def run_restore_lab(self, backup_file: Path | None) -> int:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        temp_db = f"erp_demo_restore_validation_{timestamp}"
        pre_restore = self.backup_dir / f"erp_demo_pre_restore_{timestamp}.sql"
        backup_file = backup_file or (self.backup_dir / f"erp_demo_{timestamp}.sql")

        try:
            original_counts = self.collect_counts(self.db_name)
            self.dump_database(pre_restore)
            if not backup_file.exists():
                self.dump_database(backup_file)
            self.validate_dump_file(backup_file)

            self.docker_mysql(
                f"DROP DATABASE IF EXISTS `{temp_db}`;\n"
                f"CREATE DATABASE `{temp_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n"
            )
            self.import_dump(temp_db, backup_file)
            self.validate_database(temp_db)

            code = f"BACKUP-RESTORE-V31-{timestamp}"
            self.docker_mysql(
                "INSERT INTO customers (customer_code, customer_name, contact, phone, address, status) "
                f"VALUES ('{code}', 'Backup Restore V31 Customer', 'Lab', '13800009999', 'Restore lab', 'active');\n",
                database=self.db_name,
            )
            self.log("PASS", "Inserted restore validation customer before formal restore")

            self.restore_formal_database(backup_file, pre_restore)
            self.validate_database(self.db_name)
            restored_counts = self.collect_counts(self.db_name)
            if restored_counts != original_counts:
                raise LabError(f"Restored counts differ: original={original_counts} restored={restored_counts}")

            found = self.count_matching_customer(code)
            if found != 0:
                raise LabError("Restore validation customer still exists after restore")

            self.validate_application_http()
            self.log("PASS", "MySQL backup restore lab completed")
            return 0
        except Exception as exc:
            self.log("FAIL", str(exc))
            return 1
        finally:
            self.docker_mysql(f"DROP DATABASE IF EXISTS `{temp_db}`;\n", check=False)
            self.log("PASS", f"Cleaned validation database {temp_db}")
            self.write_report()

    def count_matching_customer(self, code: str) -> int:
        result = self.docker_mysql(
            f"SELECT COUNT(*) FROM customers WHERE customer_code = '{code}';\n",
            database=self.db_name,
        )
        return int(result.stdout.strip().splitlines()[-1])

    def write_report(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        report = self.output_dir / "backup_restore.txt"
        report.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
        http_report = self.output_dir / "backup_restore_http.txt"
        http_content = self.http_lines or ["[NOT RUN] Application HTTP validation is not required for backup-only mode."]
        http_report.write_text("\n".join(http_content) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe MySQL backup/restore validation lab for ERP V3.1.")
    parser.add_argument("--compose-file", default="docker-compose.yml")
    parser.add_argument("--db-name", default=os.getenv("DB_NAME", "erp_demo"))
    parser.add_argument("--backup-file", type=Path)
    parser.add_argument("--backup-only", action="store_true")
    parser.add_argument("--base-url", default="http://localhost")
    parser.add_argument("--output-dir", type=Path, default=ROOT_DIR / "artifacts" / "v31")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lab = MysqlLab(args.compose_file, args.db_name, args.output_dir, args.base_url)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if args.backup_only:
        backup_file = args.backup_file or (lab.backup_dir / f"{args.db_name}_{timestamp}.sql")
        try:
            lab.dump_database(backup_file)
            lab.write_report()
            print("PASS")
            return 0
        except Exception as exc:
            lab.log("FAIL", str(exc))
            lab.write_report()
            return 1

    code = lab.run_restore_lab(args.backup_file)
    print("PASS" if code == 0 else "FAIL")
    return code


if __name__ == "__main__":
    sys.exit(main())
