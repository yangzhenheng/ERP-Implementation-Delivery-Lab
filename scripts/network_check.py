import argparse
import socket
import sys
from urllib.error import URLError
from urllib.request import urlopen


def resolve_host(host: str) -> tuple[bool, str]:
    try:
        ip = socket.gethostbyname(host)
        return True, ip
    except socket.gaierror as exc:
        return False, str(exc)


def check_tcp(host: str, port: int, timeout: float) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{host}:{port}"
    except OSError as exc:
        return False, str(exc)


def check_http(url: str, timeout: float) -> tuple[bool, str]:
    try:
        with urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 500, f"HTTP {response.status}"
    except URLError as exc:
        return False, str(exc.reason)
    except OSError as exc:
        return False, str(exc)


def line(status: str, message: str) -> None:
    print(f"[{status}] {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="ERP network troubleshooting check for Windows and Linux.")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    failed = 0
    ok, detail = resolve_host(args.host)
    line("PASS" if ok else "FAIL", f"DNS {args.host} -> {detail}")
    failed += 0 if ok else 1

    for port in [80, 8000, 3306, 6379]:
        ok, detail = check_tcp(args.host, port, args.timeout)
        line("PASS" if ok else "FAIL", f"TCP {args.host}:{port} {detail if not ok else ''}".strip())
        failed += 0 if ok else 1

    for url in [f"http://{args.host}/health", f"http://{args.host}:8000/health"]:
        ok, detail = check_http(url, args.timeout)
        line("PASS" if ok else "FAIL", f"HTTP {url} {detail}")
        failed += 0 if ok else 1

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
