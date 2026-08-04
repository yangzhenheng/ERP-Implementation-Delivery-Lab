import argparse
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
GOOD_UPSTREAM = "proxy_pass http://app:8000;"
BAD_UPSTREAM = "proxy_pass http://app:8999;"


class LabError(RuntimeError):
    pass


class Nginx502Lab:
    def __init__(self, config_path: Path, compose_file: str, base_url: str, direct_url: str):
        self.config_path = config_path if config_path.is_absolute() else ROOT_DIR / config_path
        self.compose_file = compose_file
        self.base_url = base_url.rstrip("/")
        self.direct_url = direct_url.rstrip("/")
        self.backup_path = self.config_path.with_name(self.config_path.name + ".v3_502_backup")

    def log(self, status: str, message: str) -> None:
        print(f"[{status}] {message}", flush=True)

    def compose(self, *args: str, timeout: int = 120) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["docker", "compose", "-f", self.compose_file, *args],
            cwd=ROOT_DIR,
            text=True,
            capture_output=True,
            timeout=timeout,
        )

    def require_tools(self) -> None:
        if shutil.which("docker") is None:
            raise LabError("docker command not found")
        if not self.config_path.exists():
            raise LabError(f"Nginx config not found: {self.config_path}")

    def read_config(self) -> str:
        content = self.config_path.read_text(encoding="utf-8")
        if GOOD_UPSTREAM not in content and BAD_UPSTREAM not in content:
            raise LabError("Expected Nginx proxy_pass was not found")
        return content

    def restart(self) -> None:
        result = self.compose("restart", "nginx")
        if result.returncode != 0:
            raise LabError(f"Nginx restart failed: {result.stderr.strip()}")
        self.log("PASS", "Nginx restarted")

    def create(self) -> None:
        self.require_tools()
        content = self.read_config()
        if GOOD_UPSTREAM not in content:
            raise LabError("Nginx fault is already present; refusing a second injection")
        shutil.copyfile(self.config_path, self.backup_path)
        self.config_path.write_text(content.replace(GOOD_UPSTREAM, BAD_UPSTREAM, 1), encoding="utf-8", newline="\n")
        self.restart()
        self.log("PASS", "Injected Nginx upstream fault app:8999")

    def fix(self) -> None:
        self.require_tools()
        if self.backup_path.exists():
            shutil.copyfile(self.backup_path, self.config_path)
            self.backup_path.unlink()
        else:
            content = self.read_config()
            if BAD_UPSTREAM in content:
                self.config_path.write_text(content.replace(BAD_UPSTREAM, GOOD_UPSTREAM, 1), encoding="utf-8", newline="\n")
        self.restart()
        self.log("PASS", "Restored Nginx upstream app:8000")

    @staticmethod
    def status_code(url: str) -> int:
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                response.read(128)
                return response.status
        except urllib.error.HTTPError as exc:
            return exc.code

    def wait_for(self, expected_nginx: int, expected_direct: int, timeout: int = 60) -> tuple[int, int]:
        deadline = time.time() + timeout
        nginx_status = 0
        direct_status = 0
        while time.time() < deadline:
            try:
                nginx_status = self.status_code(f"{self.base_url}/health")
            except Exception:
                nginx_status = 0
            try:
                direct_status = self.status_code(f"{self.direct_url}/health")
            except Exception:
                direct_status = 0
            if nginx_status == expected_nginx and direct_status == expected_direct:
                return nginx_status, direct_status
            time.sleep(2)
        raise LabError(
            f"Expected Nginx/FastAPI {expected_nginx}/{expected_direct}, got {nginx_status}/{direct_status}"
        )

    def verify_fault(self) -> None:
        nginx_status, direct_status = self.wait_for(502, 200)
        self.log("PASS", f"Fault verified: nginx={nginx_status}, fastapi={direct_status}")

    def verify_recovery(self) -> None:
        nginx_status, direct_status = self.wait_for(200, 200)
        self.log("PASS", f"Recovery verified: nginx={nginx_status}, fastapi={direct_status}")

    def log_summary(self) -> None:
        result = self.compose("logs", "--no-color", "--tail=100", "nginx")
        print("--- nginx log summary ---")
        print((result.stdout + result.stderr).strip())
        print("--- end nginx log summary ---")

    def assert_clean_config(self, original: bytes) -> None:
        if self.config_path.read_bytes() != original:
            raise LabError("Nginx config was not restored byte-for-byte")
        diff = subprocess.run(
            ["git", "diff", "--exit-code", "--", str(self.config_path.relative_to(ROOT_DIR))],
            cwd=ROOT_DIR,
            text=True,
            capture_output=True,
        )
        if diff.returncode != 0:
            raise LabError("Nginx config still has a git diff after recovery")
        self.log("PASS", "Nginx config restored with no git diff")

    def run_all(self) -> None:
        self.require_tools()
        original = self.config_path.read_bytes()
        if GOOD_UPSTREAM not in original.decode("utf-8"):
            raise LabError("Expected proxy_pass http://app:8000; before fault injection")
        primary_error: Exception | None = None
        try:
            self.verify_recovery()
            self.create()
            self.verify_fault()
            self.log_summary()
        except Exception as exc:
            primary_error = exc
            self.log("FAIL", str(exc))
        finally:
            try:
                self.config_path.write_bytes(original)
                if self.backup_path.exists():
                    self.backup_path.unlink()
                self.restart()
                self.verify_recovery()
                self.assert_clean_config(original)
            except Exception as recovery_error:
                raise LabError(f"Unconditional recovery failed: {recovery_error}") from recovery_error
        if primary_error:
            raise primary_error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inject, verify, and recover the ERP Nginx 502 lab.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--create", action="store_true")
    action.add_argument("--verify-fault", action="store_true")
    action.add_argument("--fix", action="store_true")
    action.add_argument("--verify-recovery", action="store_true")
    action.add_argument("--run-all", action="store_true")
    parser.add_argument("--config-path", type=Path, default=Path("deploy/nginx/erp.conf"))
    parser.add_argument("--compose-file", default="docker-compose.yml")
    parser.add_argument("--base-url", default="http://localhost")
    parser.add_argument("--direct-url", default="http://localhost:8000")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lab = Nginx502Lab(args.config_path, args.compose_file, args.base_url, args.direct_url)
    try:
        if args.create:
            lab.create()
        elif args.verify_fault:
            lab.verify_fault()
        elif args.fix:
            lab.fix()
        elif args.verify_recovery:
            lab.verify_recovery()
        else:
            lab.run_all()
        return 0
    except Exception as exc:
        lab.log("FAIL", str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
