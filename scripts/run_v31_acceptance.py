import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REQUIRED_SERVICES = ("mysql", "redis", "app", "nginx")
CORE_BLOCKING = {
    ".env safety",
    "Docker",
    "Compose syntax",
    "Docker services healthy",
    "Nginx and FastAPI",
    "MySQL business link",
    "Redis degraded recovery",
    "Backup restore",
    "Nginx 502 recovery",
    "SQL Server",
    "pytest",
    "E2E",
    "Linux container runtime",
}


def _normalize_service_record(record: dict) -> dict[str, str] | None:
    service = str(record.get("Service") or record.get("service") or "").strip()
    if not service:
        return None
    state = str(record.get("State") or record.get("state") or "").strip().lower()
    health = str(record.get("Health") or record.get("health") or "").strip().lower()
    status = str(record.get("Status") or record.get("status") or "").strip().lower()
    if not state and status:
        state = "running" if status.startswith("up") or status.startswith("running") else status.split()[0]
    if not health and "(healthy)" in status:
        health = "healthy"
    return {"service": service, "state": state, "health": health}


def parse_compose_ps_output(output: str) -> dict[str, dict[str, str]]:
    """Parse Compose JSON arrays, newline JSON, or the default table output."""
    text = output.strip()
    if not text:
        return {}

    raw_records: list[dict] = []
    try:
        parsed = json.loads(text)
        raw_records = parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        for line in text.splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                raw_records = []
                break
            if isinstance(item, dict):
                raw_records.append(item)

    if raw_records:
        records = (_normalize_service_record(item) for item in raw_records)
        return {item["service"]: item for item in records if item}

    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return {}
    headers = re.split(r"\s{2,}", lines[0].strip())
    try:
        service_index = headers.index("SERVICE")
        status_index = headers.index("STATUS")
    except ValueError:
        return {}

    services: dict[str, dict[str, str]] = {}
    for line in lines[1:]:
        columns = re.split(r"\s{2,}", line.strip())
        if len(columns) <= max(service_index, status_index):
            continue
        normalized = _normalize_service_record(
            {"Service": columns[service_index], "Status": columns[status_index]}
        )
        if normalized:
            services[normalized["service"]] = normalized
    return services


def unhealthy_services(
    services: dict[str, dict[str, str]], required: tuple[str, ...] = REQUIRED_SERVICES
) -> dict[str, str]:
    problems: dict[str, str] = {}
    for name in required:
        record = services.get(name)
        if not record:
            problems[name] = "missing"
        elif record["state"] != "running":
            problems[name] = f"state={record['state'] or 'empty'}"
        elif record["health"] != "healthy":
            problems[name] = f"health={record['health'] or 'empty'}"
    return problems


class AcceptanceRunner:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.output_dir = args.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: list[dict[str, str]] = []
        self.log_lines: list[str] = []

    def emit(self, status: str, name: str, detail: str = "") -> None:
        line = f"[{status}] {name}" + (f" - {detail}" if detail else "")
        for index, row in enumerate(self.results):
            if row["name"] == name:
                self.results[index] = {"name": name, "status": status, "detail": detail}
                self.log_lines[index] = line
                print(line, flush=True)
                return
        print(line, flush=True)
        self.log_lines.append(line)
        self.results.append({"name": name, "status": status, "detail": detail})

    def emit_if_missing(self, status: str, name: str, detail: str = "") -> None:
        if not any(row["name"] == name for row in self.results):
            self.emit(status, name, detail)

    def run_cmd(
        self,
        name: str,
        cmd: list[str],
        artifact: str | None = None,
        env: dict[str, str] | None = None,
        timeout: int = 120,
    ) -> subprocess.CompletedProcess:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        try:
            result = subprocess.run(
                cmd,
                cwd=ROOT_DIR,
                env=merged_env,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            output = stdout + stderr
            result = subprocess.CompletedProcess(cmd, 124, output, "command timed out")
        output = result.stdout + result.stderr
        if artifact:
            self.write_artifact(artifact, output)
        self.emit("PASS" if result.returncode == 0 else "FAIL", name, "" if result.returncode == 0 else f"exit={result.returncode}")
        return result

    def update_last_result(self, status: str, detail: str) -> None:
        self.emit(status, self.results[-1]["name"], detail)

    def write_artifact(self, filename: str, content: str) -> None:
        (self.output_dir / filename).write_text(content, encoding="utf-8", errors="replace")

    def command_available(self, command: str) -> bool:
        return shutil.which(command) is not None

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
            self.emit("BLOCKED", "Docker", "Docker engine is not available")
            return False
        return True

    def read_compose_services(self) -> tuple[dict[str, dict[str, str]], str]:
        attempts = [
            ["docker", "compose", "ps", "--format", "json"],
            ["docker", "compose", "ps", "--format", "{{json .}}"],
            ["docker", "compose", "ps"],
        ]
        combined: list[str] = []
        for cmd in attempts:
            result = subprocess.run(cmd, cwd=ROOT_DIR, text=True, capture_output=True)
            output = result.stdout + result.stderr
            combined.append("$ " + " ".join(cmd) + "\n" + output)
            services = parse_compose_ps_output(result.stdout) if result.returncode == 0 else {}
            if services:
                return services, "\n".join(combined)
        return {}, "\n".join(combined)

    def compose_up(self) -> bool:
        if self.run_cmd("Compose syntax", ["docker", "compose", "config", "--quiet"], "compose_config.txt").returncode != 0:
            self.emit("BLOCKED", "Docker services healthy", "Compose syntax failed")
            return False
        startup = subprocess.run(
            ["docker", "compose", "up", "-d", "--build"],
            cwd=ROOT_DIR,
            text=True,
            capture_output=True,
            timeout=600,
        )
        self.write_artifact("docker_up.txt", startup.stdout + startup.stderr)
        if startup.returncode != 0:
            self.emit("FAIL", "Docker services healthy", f"compose up exit={startup.returncode}")
            return False

        deadline = time.time() + 180
        last_output = ""
        last_problems: dict[str, str] = {}
        while time.time() < deadline:
            services, last_output = self.read_compose_services()
            last_problems = unhealthy_services(services)
            if not last_problems:
                self.write_artifact("docker_ps.txt", last_output)
                self.emit("PASS", "Docker services healthy", "mysql, redis, app, nginx running and healthy")
                return True
            time.sleep(5)
        self.write_artifact("docker_ps.txt", last_output)
        self.emit("FAIL", "Docker services healthy", json.dumps(last_problems, sort_keys=True))
        return False

    def verify_http(self) -> None:
        lines = []
        ok = True
        urls = [
            "http://localhost/health",
            "http://localhost/api/dashboard",
            "http://localhost/dashboard",
            "http://localhost/customers",
            "http://localhost/orders",
            "http://localhost/issues",
            "http://localhost/commercial",
            "http://localhost/system",
            "http://localhost/docs",
            "http://localhost:8000/health",
        ]
        for url in urls:
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
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "mysql", "sh", "-lc", shell],
            cwd=ROOT_DIR,
            input=sql,
            text=True,
            capture_output=True,
        )
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
            ok = ok and response.status == 200 and "unavailable_degraded" in degraded
        except Exception as exc:
            lines.append(str(exc))
            ok = False
        subprocess.run(["docker", "compose", "start", "redis"], cwd=ROOT_DIR, text=True, capture_output=True)
        time.sleep(8)
        pong = subprocess.run(
            ["docker", "compose", "exec", "-T", "redis", "redis-cli", "ping"],
            cwd=ROOT_DIR,
            text=True,
            capture_output=True,
        )
        lines.append(pong.stdout + pong.stderr)
        ok = ok and pong.returncode == 0 and "PONG" in pong.stdout
        self.write_artifact("redis_test.txt", "\n".join(lines))
        self.emit("PASS" if ok else "FAIL", "Redis degraded recovery")

    def verify_backup_restore(self) -> None:
        self.run_cmd(
            "Backup restore",
            [
                sys.executable,
                "scripts/mysql_backup_restore_lab.py",
                "--base-url",
                "http://localhost",
                "--output-dir",
                str(self.output_dir),
            ],
            "backup_restore.txt",
            timeout=600,
        )

    def verify_nginx_502(self) -> None:
        self.run_cmd(
            "Nginx 502 recovery",
            [sys.executable, "scripts/fault_lab/nginx_502_lab.py", "--run-all"],
            "nginx_502.txt",
            timeout=240,
        )

    def verify_sqlserver(self) -> None:
        if self.args.skip_sqlserver:
            self.write_artifact("sqlserver.txt", "[SKIP] --skip-sqlserver\n")
            self.emit("SKIP", "SQL Server", "explicit --skip-sqlserver")
            return
        self.run_cmd(
            "SQL Server",
            [sys.executable, "scripts/sqlserver_lab.py", "--output-dir", str(self.output_dir)],
            "sqlserver.txt",
            timeout=420,
        )

    def verify_e2e(self) -> None:
        if self.args.skip_e2e:
            self.write_artifact("e2e.txt", "[SKIP] --skip-e2e\n")
            self.emit("SKIP", "E2E", "explicit --skip-e2e")
            return
        env = {"RUN_E2E": "1"}
        if self.args.ci or os.getenv("E2E_BASE_URL"):
            env["E2E_BASE_URL"] = os.getenv("E2E_BASE_URL", "http://localhost")
        result = self.run_cmd("E2E", [sys.executable, "-m", "pytest", "tests/e2e"], "e2e.txt", env=env, timeout=300)
        output = (self.output_dir / "e2e.txt").read_text(encoding="utf-8", errors="ignore")
        if result.returncode == 0 and ("skipped" in output or "4 passed" not in output):
            self.update_last_result("BLOCKED", "E2E must report exactly four passed tests and no skips")

    def verify_linux_runtime(self) -> None:
        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "app",
                "sh",
                "-lc",
                "cat /etc/os-release; uname -a; df -h; ps; python --version",
            ],
            cwd=ROOT_DIR,
            text=True,
            capture_output=True,
        )
        self.write_artifact("linux_runtime.txt", result.stdout + result.stderr)
        self.emit("PASS" if result.returncode == 0 else "FAIL", "Linux container runtime")

    def mark_stack_unavailable(self, detail: str) -> None:
        artifacts = [
            "mysql_queries.txt",
            "redis_test.txt",
            "backup_restore.txt",
            "backup_restore_http.txt",
            "nginx_502.txt",
            "sqlserver.txt",
            "e2e.txt",
            "linux_runtime.txt",
        ]
        for artifact in artifacts:
            if not (self.output_dir / artifact).exists():
                self.write_artifact(artifact, f"[BLOCKED] {detail}; no full-stack claim made.\n")
        names = [
            "Compose syntax",
            "Docker services healthy",
            "Nginx and FastAPI",
            "MySQL business link",
            "Redis degraded recovery",
            "Backup restore",
            "Nginx 502 recovery",
        ]
        for name in names:
            self.emit_if_missing("BLOCKED", name, detail)
        self.emit_if_missing("SKIP" if self.args.skip_sqlserver else "BLOCKED", "SQL Server", "explicit --skip-sqlserver" if self.args.skip_sqlserver else detail)
        self.emit_if_missing("SKIP" if self.args.skip_e2e else "BLOCKED", "E2E", "explicit --skip-e2e" if self.args.skip_e2e else detail)
        self.emit_if_missing("BLOCKED", "Linux container runtime", detail)

    def run(self) -> int:
        self.check_git()
        self.check_env_safety()
        stack_started = False
        try:
            if self.check_docker():
                stack_started = self.compose_up()
                if stack_started:
                    self.verify_http()
                    self.verify_mysql()
                    self.verify_redis()
                    self.verify_backup_restore()
                    self.verify_nginx_502()
                    self.verify_sqlserver()
                    self.verify_e2e()
                    self.verify_linux_runtime()
                else:
                    self.mark_stack_unavailable("ERP Compose stack did not become healthy")
            else:
                self.mark_stack_unavailable("Docker unavailable")
        except Exception as exc:
            self.emit("FAIL", "Acceptance runner", f"unexpected error: {exc}")
            self.mark_stack_unavailable("Acceptance runner interrupted")
        finally:
            if stack_started:
                ps = subprocess.run(["docker", "compose", "ps"], cwd=ROOT_DIR, text=True, capture_output=True)
                self.write_artifact("docker_ps_final.txt", ps.stdout + ps.stderr)
            if stack_started and not self.args.keep_services:
                subprocess.run(["docker", "compose", "down"], cwd=ROOT_DIR, text=True, capture_output=True)

        self.run_cmd(
            "pytest",
            [sys.executable, "-m", "pytest"],
            "pytest.txt",
            env={"RUN_E2E": "0", "E2E_BASE_URL": ""},
            timeout=300,
        )
        self.run_cmd("compileall", [sys.executable, "-m", "compileall", "app", "scripts", "tests"], "compileall.txt", timeout=180)
        return self.finalize()

    def finalize(self) -> int:
        execution_mode = "CI" if self.args.ci else "LOCAL"
        execution_platform = platform.system()
        core_rows = [row for row in self.results if row["name"] in CORE_BLOCKING]
        has_failure = any(row["status"] == "FAIL" for row in core_rows)
        has_blocked = any(row["status"] == "BLOCKED" for row in core_rows)
        skipped = {row["name"] for row in core_rows if row["status"] == "SKIP"}
        allowed_skips = set()
        if self.args.skip_sqlserver:
            allowed_skips.add("SQL Server")
        if self.args.skip_e2e:
            allowed_skips.add("E2E")
        has_unexpected_skip = bool(skipped - allowed_skips)
        all_core_pass = len(core_rows) == len(CORE_BLOCKING) and all(row["status"] == "PASS" for row in core_rows)

        if self.args.ci:
            local_status = "NOT RUN"
            local_windows_status = "NOT RUN"
            ci_status = "FAIL" if has_failure or has_blocked or has_unexpected_skip else "PASS"
        else:
            if has_failure:
                local_status = "FAIL"
            elif has_blocked or has_unexpected_skip:
                local_status = "BLOCKED"
            else:
                local_status = "PASS"
            local_windows_status = local_status if execution_platform == "Windows" else "NOT RUN"
            ci_status = "NOT RUN"

        acceptance = {
            "version": "3.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "execution_mode": execution_mode,
            "execution_platform": execution_platform,
            "local_status": local_status,
            "local_windows_status": local_windows_status,
            "ci_status": ci_status,
            "results": self.results,
        }
        self.write_artifact("acceptance.json", json.dumps(acceptance, indent=2, ensure_ascii=False) + "\n")
        self.write_artifact("acceptance.log", "\n".join(self.log_lines) + "\n")
        grade = "C" if all_core_pass else "B (partial verification)"
        report = [
            "# V3.1 Acceptance Report",
            "",
            "- Version: 3.1.0",
            f"- Generated: {acceptance['generated_at']}",
            f"- Execution mode: {execution_mode}",
            f"- Execution platform: {execution_platform}",
            f"- Local status: {local_status}",
            f"- Local Windows status: {local_windows_status}",
            f"- CI status: {ci_status}",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
        ]
        report += [f"| {row['name']} | {row['status']} | {row['detail']} |" for row in self.results]
        report += ["", f"Final grade: {grade}", ""]
        self.write_artifact("V31_ACCEPTANCE_REPORT.md", "\n".join(report))
        return 1 if has_failure or has_blocked or has_unexpected_skip else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ERP V3.1 strict full-stack acceptance.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--local", action="store_true")
    mode.add_argument("--ci", action="store_true")
    parser.add_argument("--skip-sqlserver", action="store_true")
    parser.add_argument("--skip-e2e", action="store_true")
    parser.add_argument("--keep-services", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=ROOT_DIR / "artifacts" / "v31")
    args = parser.parse_args(argv)
    if not args.local and not args.ci:
        args.local = True
    return args


if __name__ == "__main__":
    sys.exit(AcceptanceRunner(parse_args()).run())
