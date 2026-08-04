import argparse
import subprocess
import sys
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = ROOT_DIR / "docs" / "screenshots"
EVIDENCE_DIR = ROOT_DIR / "docs" / "evidence"
PAGES = {
    "dashboard": "/dashboard",
    "customers": "/customers",
    "orders": "/orders",
    "inventory": "/inventory",
    "issues": "/issues",
    "commercial": "/commercial",
    "system_status": "/system",
}


def run_cmd(cmd: list[str], output: Path) -> None:
    result = subprocess.run(cmd, cwd=ROOT_DIR, text=True, capture_output=True, timeout=120)
    output.write_text(result.stdout + result.stderr, encoding="utf-8", errors="replace")


def capture_screenshots(base_url: str) -> int:
    playwright = __import__("playwright.sync_api", fromlist=["sync_playwright"])
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        for name, path in PAGES.items():
            page.goto(f"{base_url.rstrip('/')}{path}")
            page.wait_for_selector("#app .section, #app .grid", timeout=7000)
            page.screenshot(path=SCREENSHOT_DIR / f"{name}.png", full_page=True)
        browser.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture V3.1 screenshots and command evidence.")
    parser.add_argument("--base-url", default="http://localhost")
    parser.add_argument("--skip-screenshots", action="store_true")
    args = parser.parse_args()

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    commands = {
        "docker_ps.txt": ["docker", "compose", "ps"],
        "mysql_queries.txt": ["python", "scripts/run_v31_acceptance.py", "--skip-e2e", "--skip-sqlserver", "--keep-services"],
        "redis_pong.txt": ["docker", "compose", "exec", "-T", "redis", "redis-cli", "ping"],
        "backup_restore.txt": ["python", "scripts/mysql_backup_restore_lab.py"],
        "nginx_502.txt": ["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts/fault_lab/verify_nginx_502.ps1"],
        "sqlserver_queries.txt": ["docker", "compose", "-f", "docker-compose.database-lab.yml", "config", "--quiet"],
        "linux_runtime.txt": ["docker", "compose", "exec", "-T", "app", "sh", "-lc", "cat /etc/os-release; uname -a; python --version"],
    }
    for filename, cmd in commands.items():
        try:
            run_cmd(cmd, EVIDENCE_DIR / filename)
        except Exception as exc:
            (EVIDENCE_DIR / filename).write_text(f"[BLOCKED] {exc}\n", encoding="utf-8")

    if not args.skip_screenshots:
        try:
            urllib.request.urlopen(f"{args.base_url.rstrip('/')}/health", timeout=10).close()
            capture_screenshots(args.base_url)
        except Exception as exc:
            (EVIDENCE_DIR / "screenshots.txt").write_text(f"[BLOCKED] {exc}\n", encoding="utf-8")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
