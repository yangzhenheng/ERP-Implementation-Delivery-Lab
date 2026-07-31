import argparse
import sys
from urllib.error import URLError
from urllib.request import urlopen


def check_url(name: str, url: str) -> bool:
    try:
        with urlopen(url, timeout=5) as response:
            ok = 200 <= response.status < 300
    except URLError as exc:
        print(f"[FAIL] {name}: {exc}")
        return False
    except Exception as exc:
        print(f"[FAIL] {name}: {exc}")
        return False
    print(f"[PASS] {name}: {url}" if ok else f"[FAIL] {name}: HTTP {response.status}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify ERP lab deployment through real API checks.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    checks = [
        check_url("API health", f"{base}/health"),
        check_url("Dashboard API", f"{base}/api/dashboard"),
        check_url("Customers API", f"{base}/api/customers"),
        check_url("System status", f"{base}/api/system/status"),
    ]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
