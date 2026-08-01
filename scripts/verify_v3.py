import argparse
import socket
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen


API_PATHS = [
    "/health",
    "/api/dashboard",
    "/api/customers",
    "/api/products",
    "/api/inventory",
    "/api/orders",
    "/api/issues",
    "/api/implementation",
    "/api/implementation/tasks",
    "/api/commercial",
    "/api/commercial/summary",
    "/api/system/status",
]

FRONTEND_PATHS = [
    "/dashboard",
    "/customers",
    "/orders",
    "/commercial",
]

TCP_CHECKS = [
    ("FastAPI local", "localhost", 8000, "required"),
    ("Nginx Docker", "localhost", 80, "docker_optional"),
    ("MySQL Docker", "localhost", 3306, "docker_optional"),
    ("Redis Docker", "localhost", 6379, "docker_optional"),
]


def print_result(status: str, name: str, detail: str = "") -> None:
    suffix = f" - {detail}" if detail else ""
    print(f"[{status}] {name}{suffix}")


def check_http(base: str, path: str) -> bool:
    url = f"{base.rstrip('/')}{path}"
    try:
        req = Request(url, headers={"x-request-id": "verify-v3"})
        with urlopen(req, timeout=5) as response:
            ok = 200 <= response.status < 300
            print_result("PASS" if ok else "FAIL", path, f"HTTP {response.status}")
            return ok
    except URLError as exc:
        print_result("FAIL", path, str(exc.reason))
    except OSError as exc:
        print_result("FAIL", path, str(exc))
    return False


def check_tcp(name: str, host: str, port: int, mode: str, require_full_stack: bool) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            print_result("PASS", f"TCP {name}", f"{host}:{port}")
            return True
    except OSError as exc:
        if mode == "docker_optional" and not require_full_stack:
            print_result("SKIP", f"TCP {name}", f"{host}:{port} unavailable: {exc}")
            return True
        print_result("FAIL", f"TCP {name}", f"{host}:{port} unavailable: {exc}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="V3 ERP interview edition verification.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--require-full-stack", action="store_true", help="Require Docker/Nginx/MySQL/Redis ports to be reachable. No SKIP is allowed.")
    args = parser.parse_args()

    ok = True
    print("== HTTP API ==")
    for path in API_PATHS:
        ok = check_http(args.base_url, path) and ok

    print("== Frontend ==")
    for path in FRONTEND_PATHS:
        ok = check_http(args.base_url, path) and ok

    print("== TCP ==")
    for name, host, port, mode in TCP_CHECKS:
        ok = check_tcp(name, host, port, mode, args.require_full_stack) and ok

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
