import argparse
import sys
from urllib.error import URLError
from urllib.request import urlopen


def check_url(name: str, url: str) -> bool:
    try:
        with urlopen(url, timeout=5) as response:
            ok = 200 <= response.status < 300
    except URLError as exc:
        print(f"[失败] {name}: {exc}")
        return False
    except Exception as exc:
        print(f"[失败] {name}: {exc}")
        return False
    print(f"[通过] {name}: {url}" if ok else f"[失败] {name}: HTTP {response.status}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="通过真实 API 请求验证 ERP 实施实验室部署状态。")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    checks = [
        check_url("API 健康检查", f"{base}/health"),
        check_url("驾驶舱 API", f"{base}/api/dashboard"),
        check_url("客户 API", f"{base}/api/customers"),
        check_url("系统状态", f"{base}/api/system/status"),
    ]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
