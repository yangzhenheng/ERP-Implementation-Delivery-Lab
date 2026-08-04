import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SQLCMD_PATHS = ("/opt/mssql-tools18/bin/sqlcmd", "/opt/mssql-tools/bin/sqlcmd")
SQL_FILES = ("01_schema.sql", "02_seed.sql", "03_queries.sql")
REQUIRED_QUERY_FEATURES = (
    "TOP",
    "JOIN",
    "GROUP BY",
    "HAVING",
    "OFFSET",
    "FETCH",
    "ISNULL",
    "GETDATE",
    "UPDATE",
    "DELETE",
)


class LabError(RuntimeError):
    pass


class SqlServerLab:
    def __init__(self, compose_file: str, output_dir: Path, keep_service: bool):
        self.compose_file = compose_file
        self.output_dir = output_dir
        self.keep_service = keep_service
        self.lines: list[str] = []
        self.started = False
        self.sqlcmd_path = ""

    def log(self, status: str, message: str) -> None:
        line = f"[{status}] {message}"
        self.lines.append(line)
        print(line, flush=True)

    def compose(self, *args: str, input_text: str | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["docker", "compose", "-f", self.compose_file, *args],
            cwd=ROOT_DIR,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
        )

    def record_result(self, label: str, result: subprocess.CompletedProcess) -> None:
        self.lines.append(f"$ {label}")
        if result.stdout:
            self.lines.append(result.stdout.rstrip())
        if result.stderr:
            self.lines.append(result.stderr.rstrip())

    def require_environment(self) -> None:
        if shutil.which("docker") is None:
            raise LabError("docker command not found")
        env_file = ROOT_DIR / ".env"
        if not os.getenv("SQLSERVER_SA_PASSWORD") and env_file.exists():
            for raw_line in env_file.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if line.startswith("SQLSERVER_SA_PASSWORD="):
                    os.environ["SQLSERVER_SA_PASSWORD"] = line.split("=", 1)[1]
                    break
        password = os.getenv("SQLSERVER_SA_PASSWORD", "")
        categories = [
            any(char.isupper() for char in password),
            any(char.islower() for char in password),
            any(char.isdigit() for char in password),
            any(not char.isalnum() for char in password),
        ]
        if len(password) < 16 or not all(categories):
            raise LabError("SQLSERVER_SA_PASSWORD must be at least 16 characters with upper, lower, digit, and special characters")

    def validate_compose(self) -> None:
        result = self.compose("config", "--quiet")
        self.record_result("docker compose config --quiet", result)
        if result.returncode != 0:
            raise LabError("SQL Server Compose syntax validation failed")
        self.log("PASS", "SQL Server Compose syntax")

    def start(self) -> None:
        result = self.compose("up", "-d", "sqlserver", timeout=180)
        self.record_result("docker compose up -d sqlserver", result)
        if result.returncode != 0:
            raise LabError("SQL Server container failed to start")
        self.started = True
        self.log("PASS", "SQL Server container started")

    def detect_sqlcmd(self) -> str:
        probe = "for p in " + " ".join(SQLCMD_PATHS) + '; do if test -x "$p"; then echo "$p"; exit 0; fi; done; '
        probe += 'echo "sqlcmd not found; inspected: ' + " ".join(SQLCMD_PATHS) + '" >&2; exit 1'
        result = self.compose("exec", "-T", "sqlserver", "sh", "-lc", probe)
        self.record_result("inspect sqlcmd paths", result)
        if result.returncode != 0:
            raise LabError(result.stderr.strip() or "sqlcmd was not found in the SQL Server container")
        path = result.stdout.strip().splitlines()[-1]
        if path not in SQLCMD_PATHS:
            raise LabError(f"Unexpected sqlcmd path returned: {path}")
        self.log("PASS", f"Detected sqlcmd at {path}")
        return path

    def sqlcmd(self, *args: str, timeout: int = 120) -> subprocess.CompletedProcess:
        command = (
            f'{self.sqlcmd_path} -S localhost -U sa -P "$MSSQL_SA_PASSWORD" '
            "-C -b -r1 -W " + " ".join(args)
        )
        return self.compose("exec", "-T", "sqlserver", "sh", "-lc", command, timeout=timeout)

    def wait_ready(self) -> None:
        deadline = time.time() + 300
        last_result: subprocess.CompletedProcess | None = None
        while time.time() < deadline:
            try:
                self.sqlcmd_path = self.detect_sqlcmd()
                last_result = self.sqlcmd('-Q "SET NOCOUNT ON; SELECT 1 AS ready"')
                if last_result.returncode == 0 and "1" in last_result.stdout:
                    self.record_result("sqlcmd readiness query", last_result)
                    self.log("PASS", "SQL Server became ready")
                    return
            except LabError as exc:
                self.lines.append(f"[WAIT] {exc}")
            time.sleep(5)
        if last_result:
            self.record_result("last sqlcmd readiness query", last_result)
        ps = self.compose("ps", "-a")
        self.record_result("docker compose ps -a", ps)
        raise LabError("SQL Server did not become ready within 300 seconds")

    def verify_query_coverage(self) -> None:
        query_file = ROOT_DIR / "sql" / "sqlserver" / "03_queries.sql"
        query_text = query_file.read_text(encoding="utf-8").upper()
        missing = [feature for feature in REQUIRED_QUERY_FEATURES if feature not in query_text]
        if missing:
            raise LabError(f"SQL Server query coverage is missing: {', '.join(missing)}")
        self.log("PASS", "SQL query file covers TOP, JOIN, GROUP BY, HAVING, OFFSET FETCH, ISNULL, GETDATE, UPDATE, DELETE")

    def run_sql_files(self) -> None:
        self.verify_query_coverage()
        for filename in SQL_FILES:
            result = self.sqlcmd(f'-i "/sqlserver-lab/{filename}"', timeout=180)
            self.record_result(f"sqlcmd {filename}", result)
            if result.returncode != 0:
                raise LabError(f"SQL Server script failed: {filename}")
            self.log("PASS", f"Executed {filename}")

    def verify_data(self) -> None:
        tables = ("customers", "products", "inventory", "sales_orders", "issues")
        for table in tables:
            query = f'SET NOCOUNT ON; USE erp_demo_lab; SELECT COUNT(*) FROM dbo.{table};'
            result = self.sqlcmd(f'-Q "{query}"')
            self.record_result(f"count {table}", result)
            if result.returncode != 0:
                raise LabError(f"Failed to query table {table}")
            values = [line.strip() for line in result.stdout.splitlines() if line.strip().isdigit()]
            if not values or int(values[-1]) <= 0:
                raise LabError(f"Table {table} did not contain verified rows")
            self.log("PASS", f"Verified {table} row count={values[-1]}")

        mutation_query = (
            "SET NOCOUNT ON; USE erp_demo_lab; "
            "INSERT INTO dbo.issues(title,module,severity,status) VALUES(N'Delete verification',N'Database',N'P4',N'open'); "
            "UPDATE dbo.issues SET status=N'closed' WHERE title=N'Delete verification'; "
            "DELETE FROM dbo.issues WHERE title=N'Delete verification' AND status=N'closed'; "
            "SELECT COUNT(*) FROM dbo.issues WHERE title=N'Delete verification';"
        )
        result = self.sqlcmd(f'-Q "{mutation_query}"')
        self.record_result("verify UPDATE and DELETE effects", result)
        values = [line.strip() for line in result.stdout.splitlines() if line.strip().isdigit()]
        if result.returncode != 0 or not values or values[-1] != "0":
            raise LabError("UPDATE/DELETE verification did not leave the expected zero rows")
        self.log("PASS", "Verified UPDATE and DELETE effects")

    def write_report(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "sqlserver.txt").write_text("\n".join(self.lines) + "\n", encoding="utf-8")

    def run(self) -> int:
        try:
            self.require_environment()
            self.validate_compose()
            self.start()
            self.wait_ready()
            self.run_sql_files()
            self.verify_data()
            self.log("PASS", "SQL Server acceptance lab completed")
            return 0
        except Exception as exc:
            self.log("FAIL", str(exc))
            return 1
        finally:
            if self.started and not self.keep_service:
                result = self.compose("stop", "sqlserver", timeout=120)
                self.record_result("docker compose stop sqlserver", result)
                self.log("PASS" if result.returncode == 0 else "FAIL", "Stopped only the SQL Server lab service")
            self.write_report()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the real SQL Server compatibility acceptance lab.")
    parser.add_argument("--compose-file", default="docker-compose.database-lab.yml")
    parser.add_argument("--output-dir", type=Path, default=ROOT_DIR / "artifacts" / "v31")
    parser.add_argument("--keep-service", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(SqlServerLab(args.compose_file, args.output_dir, args.keep_service).run())
