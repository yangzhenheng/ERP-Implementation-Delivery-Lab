import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
CORE_BLOCKING = {
    "Docker",
    "Compose syntax",
    "Docker services",
    "Nginx and FastAPI",
    "MySQL business link",
    "Redis degraded recovery",
    "Backup restore",
    "Nginx 502 recovery",
    "pytest",
    "E2E",
    "Linux container runtime",
}


class AcceptanceRunner:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.output_dir = args.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: list[dict[str, str]] = []
        self.log_lines: list[str] = []

    def emit(self, status: str, name: str, detail: str = "") -> None:
        line = f"[{status}] {name}" + (f" - {detail}" if detail else "")
        print(line, flush=True)
        self.log_lines.append(line)
        self.results.append({"name": name, "status": status, "detail": detail})

    def run_cmd(self, name: str, cmd: list[str], artifact: str | None = None, env: dict[str, str] | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        result = subprocess.run(cmd, cwd=ROOT_DIR, env=merged_env, text=True, capture_output=True, timeout=timeout)
        output = result.stdout + result.stderr
        if artifact:
            (self.output_dir / artifact).write_text(output, encoding="utf-8", errors="replace")
        if result.returncode == 0:
            self.emit("PASS", name)
        else:
            self.emit("FAIL", name, f"exit={result.returncode}")
        return result

    def update_last_result(self, status: str, detail: str) -> None:
        self.results[-1]["status"] = status
        self.results[-1]["detail"] = detail
        name = self.results[-1]["name"]
        self.log_lines[-1] = f"[{status}] {name}" + (f" - {detail}" if detail else "")

    def write_artifact(self, filename: str, content: str) -> None:
        (self.output_dir / filename).write_text(content, encoding="utf-8")

    def command_available(self, command: str) -> bool:
        probe = "where" if os.name == "nt" else "which"
        return subprocess.run([probe, command], cwd=ROOT_DIR, text=True, capture_output=True).returncode == 0

    def check_git(self) -> None:
        status = subprocess.run(["git", "status", "--short"], cwd=ROOT_DIR, text=True, capture_output=True)
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT_DIR, text=True, capture_output=True)
        self.write_artifact("git_status.txt", branch.stdout + status.stdout + status.stderr)
        self.emit("PASS" if status.returncode == 0 else "FAIL", "Git status", branch.stdout.strip())

    def check_env_safety(self) -> None:
        ignored = subprocess.run(["git", "check-ignore", ".env"], cwd=ROOT_DIR, text=True, capture_output=True)
        tracked = subprocess.run(["git", "status", "--short", ".env"], cwd=ROOT_DIR, text=True, capture_output=True)
        if ignored.returncode == 0 and not tracked.stdout.strip():
            self.emit("PASS", ".env safety", ".env ignored and not in git status")
        else:
            self.emit("FAIL", ".env safety", ".env is not safely ignored")

    def check_docker(self) -> bool:
        if not self.command_available("docker"):
            self.write_artifact("docker_ps.txt", "[BLOCKED] docker command not found in PATH\n")
            self.emit("BLOCKED", "Docker", "docker command not found in PATH")
            return False
        result = self.run_cmd("Docker", ["docker", "version"], "docker_version.txt", timeout=30)
        if result.returncode != 0:
            self.write_artifact("docker_ps.txt", "[BLOCKED] Docker engine is not available\n")
            self.results[-1]["status"] = "BLOCKED"
            self.log_lines[-1] = self.log_lines[-1].replace("[FAIL]", "[BLOCKED]", 1)
            return False
        return True

    def compose_up(self) -> bool:
        if self.run_cmd("Compose syntax", ["docker", "compose", "config", "--quiet"], "compose_config.txt").returncode != 0:
            return False
        if self.run_cmd("Docker services", ["docker", "compose", "up", "-d", "--build"], "docker_up.txt", timeout=600).returncode != 0:
            return False
        deadline = time.time() + 180
        last_ps = ""
        while time.time() < deadline:
            ps = subprocess.run(["docker", "compose", "ps"], cwd=ROOT_DIR, text=True, capture_output=True)
            last_ps = ps.stdout + ps.stderr
            if all(name in last_ps and "healthy" in last_ps for name in ["mysql", "redis", "app", "nginx"]):
                self.write_artifact("docker_ps.txt", last_ps)
                self.emit("PASS", "Docker services healthy")
                return True
            time.sleep(5)
        self.write_artifact("docker_ps.txt", last_ps)
        self.emit("FAIL", "Docker services healthy", "Timed out waiting for healthy services")
        return False

    def verify_http(self) -> None:
        lines = []
        ok = True
        for url in ["http://localhost/health", "http://localhost/api/dashboard", "http://localhost/dashboard", "http://localhost/customers", "http://localhost/orders", "http://localhost/issues", "http://localhost/commercial", "http://localhost/system", "http://localhost/docs", "http://localhost:8000/health"]:
            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    status = response.status
                    body = response.read(300).decode("utf-8", errors="replace")
                lines.append(f"{url} {status} {body}")
                ok = ok and status == 200
            except Exception as exc:
                lines.append(f"{url} FAIL {exc}")
                ok = False
        self.write_artifact("http_checks.txt", "\n".join(lines) + "\n")
        self.emit("PASS" if ok else "FAIL", "Nginx and FastAPI")

    def verify_mysql(self) -> None:
        sql = (
            "USE erp_demo;\nSHOW TABLES;\n"
            "SELECT COUNT(*) FROM customers;\nSELECT COUNT(*) FROM products;\n"
            "SELECT COUNT(*) FROM inventory;\nSELECT COUNT(*) FROM sales_orders;\nSELECT COUNT(*) FROM issues;\n"
        )
        shell = 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --default-character-set=utf8mb4'
        result = subprocess.run(["docker", "compose", "exec", "-T", "mysql", "sh", "-lc", shell], cwd=ROOT_DIR, input=sql, text=True, capture_output=True)
        self.write_artifact("mysql_queries.txt", result.stdout + result.stderr)
        self.emit("PASS" if result.returncode == 0 else "FAIL", "MySQL business link")

    def verify_redis(self) -> None:
        lines = []
        ok = True
        for cmd in [
            ["docker", "compose", "exec", "-T", "redis", "redis-cli", "ping"],
            ["docker", "compose", "stop", "redis"],
        ]:
            result = subprocess.run(cmd, cwd=ROOT_DIR, text=True, capture_output=True)
            lines.append("$ " + " ".join(cmd) + "\n" + result.stdout + result.stderr)
            ok = ok and result.returncode == 0
        try:
            with urllib.request.urlopen("http://localhost/api/system/status", timeout=10) as response:
                degraded = response.read().decode("utf-8", errors="replace")
            lines.append(degraded)
            ok = ok and "unavailable_degraded" in degraded
        except Exception as exc:
            lines.append(str(exc))
            ok = False
        subprocess.run(["docker", "compose", "start", "redis"], cwd=ROOT_DIR, text=True, capture_output=True)
        time.sleep(8)
        pong = subprocess.run(["docker", "compose", "exec", "-T", "redis", "redis-cli", "ping"], cwd=ROOT_DIR, text=True, capture_output=True)
        lines.append(pong.stdout + pong.stderr)
        ok = ok and "PONG" in pong.stdout
        self.write_artifact("redis_test.txt", "\n".join(lines))
        self.emit("PASS" if ok else "FAIL", "Redis degraded recovery")

    def verify_backup_restore(self) -> None:
        result = self.run_cmd("Backup restore", [sys.executable, "scripts/mysql_backup_restore_lab.py", "--output-dir", str(self.output_dir)], "backup_restore.txt", timeout=600)
        if result.returncode == 0 and "PASS" not in (self.output_dir / "backup_restore.txt").read_text(encoding="utf-8", errors="ignore"):
            self.emit("FAIL", "Backup restore report", "PASS marker missing")

    def verify_nginx_502(self) -> None:
        lines = []
        ok = True
        for cmd in [
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts/fault_lab/create_nginx_502.ps1"],
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts/fault_lab/fix_nginx_502.ps1"],
        ]:
            result = subprocess.run(cmd, cwd=ROOT_DIR, text=True, capture_output=True, timeout=120)
            lines.append("$ " + " ".join(cmd) + "\n" + result.stdout + result.stderr)
            ok = ok and result.returncode == 0
        self.write_artifact("nginx_502.txt", "\n".join(lines))
        self.emit("PASS" if ok else "FAIL", "Nginx 502 recovery")

    def verify_sqlserver(self) -> None:
        if self.args.skip_sqlserver:
            self.write_artifact("sqlserver.txt", "[SKIP] --skip-sqlserver\n")
            self.emit("SKIP", "SQL Server")
            return
        result = subprocess.run(["docker", "compose", "-f", "docker-compose.database-lab.yml", "config", "--quiet"], cwd=ROOT_DIR, text=True, capture_output=True)
        self.write_artifact("sqlserver.txt", result.stdout + result.stderr)
        self.emit("PASS" if result.returncode == 0 else "FAIL", "SQL Server")

    def verify_e2e(self) -> None:
        if self.args.skip_e2e:
            self.write_artifact("e2e.txt", "[SKIP] --skip-e2e\n")
            self.emit("SKIP", "E2E")
            return
        env = {"RUN_E2E": "1"}
        if self.args.ci or os.getenv("E2E_BASE_URL"):
            env["E2E_BASE_URL"] = os.getenv("E2E_BASE_URL", "http://localhost")
        result = self.run_cmd("E2E", ["pytest", "tests/e2e", "-q"], "e2e.txt", env=env, timeout=300)
        output = (self.output_dir / "e2e.txt").read_text(encoding="utf-8", errors="ignore")
        if result.returncode == 0 and "skipped" in output and "passed" not in output:
            self.update_last_result("BLOCKED", "E2E tests skipped; browser dependency or environment not verified")

    def verify_linux_runtime(self) -> None:
        result = subprocess.run(["docker", "compose", "exec", "-T", "app", "sh", "-lc", "cat /etc/os-release; uname -a; df -h; ps; python --version"], cwd=ROOT_DIR, text=True, capture_output=True)
        self.write_artifact("linux_runtime.txt", result.stdout + result.stderr)
        self.emit("PASS" if result.returncode == 0 else "FAIL", "Linux container runtime")

    def run(self) -> int:
        self.check_git()
        self.check_env_safety()
        docker_ok = self.check_docker()
        if docker_ok and self.compose_up():
            self.verify_http()
            self.verify_mysql()
            self.verify_redis()
            self.verify_backup_restore()
            self.verify_nginx_502()
            self.verify_sqlserver()
            self.verify_e2e()
            self.verify_linux_runtime()
            self.run_cmd("docker ps", ["docker", "compose", "ps"], "docker_ps.txt")
            if not self.args.keep_services:
                subprocess.run(["docker", "compose", "down"], cwd=ROOT_DIR, text=True, capture_output=True)
        else:
            for artifact in ["mysql_queries.txt", "redis_test.txt", "backup_restore.txt", "nginx_502.txt", "sqlserver.txt", "e2e.txt", "linux_runtime.txt"]:
                self.write_artifact(artifact, "[BLOCKED] Docker engine is not available; no full-stack claim made.\n")
            for name in ["Compose syntax", "Docker services", "Nginx and FastAPI", "MySQL business link", "Redis degraded recovery", "Backup restore", "Nginx 502 recovery"]:
                self.emit("BLOCKED", name, "Docker unavailable")
            self.emit("SKIP" if self.args.skip_sqlserver else "BLOCKED", "SQL Server", "--skip-sqlserver" if self.args.skip_sqlserver else "Docker unavailable")
            self.emit("SKIP" if self.args.skip_e2e else "BLOCKED", "E2E", "--skip-e2e" if self.args.skip_e2e else "Docker unavailable")
            self.emit("BLOCKED", "Linux container runtime", "Docker unavailable")

        self.run_cmd("pytest", ["pytest", "-q"], "pytest.txt", timeout=180)
        self.run_cmd("compileall", [sys.executable, "-m", "compileall", "app", "scripts", "tests"], "compileall.txt", timeout=180)
        return self.finalize()

    def finalize(self) -> int:
        acceptance = {
            "version": "3.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": "ci" if self.args.ci else "local",
            "results": self.results,
        }
        self.write_artifact("acceptance.json", json.dumps(acceptance, indent=2, ensure_ascii=False) + "\n")
        self.write_artifact("acceptance.log", "\n".join(self.log_lines) + "\n")
        has_bad_core = any(row["name"] in CORE_BLOCKING and row["status"] in {"FAIL", "BLOCKED"} for row in self.results)
        local_status = "LOCAL WINDOWS BLOCKED" if has_bad_core else "LOCAL WINDOWS PASS"
        ci_status = "CI VERIFIED" if self.args.ci and not has_bad_core else "NOT VERIFIED"
        report = [
            "# V3.1 Acceptance Report",
            "",
            f"- Version: 3.1.0",
            f"- Generated: {acceptance['generated_at']}",
            f"- Local Windows status: {local_status}",
            f"- CI status: {ci_status}",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
        ]
        report += [f"| {row['name']} | {row['status']} | {row['detail']} |" for row in self.results]
        report += ["", "Final grade: NOT VERIFIED until local or CI evidence shows all core checks passing.", ""]
        self.write_artifact("V31_ACCEPTANCE_REPORT.md", "\n".join(report))
        return 1 if has_bad_core else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ERP V3.1 strict full-stack acceptance.")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--skip-sqlserver", action="store_true")
    parser.add_argument("--skip-e2e", action="store_true")
    parser.add_argument("--keep-services", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=ROOT_DIR / "artifacts" / "v31")
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(AcceptanceRunner(parse_args()).run())
