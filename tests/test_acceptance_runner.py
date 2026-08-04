import argparse
import json
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.run_v31_acceptance import (
    CORE_BLOCKING,
    AcceptanceRunner,
    parse_compose_ps_output,
    unhealthy_services,
)


def json_services(**overrides):
    records = []
    for name in ("mysql", "redis", "app", "nginx"):
        state, health = overrides.get(name, ("running", "healthy"))
        records.append({"Service": name, "State": state, "Health": health})
    return json.dumps(records)


def test_all_four_services_healthy_pass():
    assert unhealthy_services(parse_compose_ps_output(json_services())) == {}


def test_redis_unhealthy_fails_even_when_mysql_is_healthy():
    problems = unhealthy_services(
        parse_compose_ps_output(json_services(redis=("running", "unhealthy")))
    )
    assert problems == {"redis": "health=unhealthy"}


def test_one_healthy_service_does_not_cover_other_service_names():
    output = json.dumps([{"Service": "mysql", "State": "running", "Health": "healthy"}])
    assert unhealthy_services(parse_compose_ps_output(output)) == {
        "redis": "missing",
        "app": "missing",
        "nginx": "missing",
    }


def test_missing_nginx_fails():
    records = json.loads(json_services())
    records = [record for record in records if record["Service"] != "nginx"]
    assert unhealthy_services(parse_compose_ps_output(json.dumps(records)))["nginx"] == "missing"


def test_exited_service_fails():
    problems = unhealthy_services(
        parse_compose_ps_output(json_services(app=("exited", "healthy")))
    )
    assert problems == {"app": "state=exited"}


def test_empty_health_fails():
    problems = unhealthy_services(
        parse_compose_ps_output(json_services(nginx=("running", "")))
    )
    assert problems == {"nginx": "health=empty"}


def test_newline_delimited_compose_json_is_supported():
    output = "\n".join(json.dumps(item) for item in json.loads(json_services()))
    assert unhealthy_services(parse_compose_ps_output(output)) == {}


def test_compose_table_fallback_is_parsed_per_service():
    output = "\n".join(
        [
            "NAME                 IMAGE          COMMAND       SERVICE   CREATED       STATUS                   PORTS",
            "erp-mysql-1          mysql:8.0      cmd           mysql     1 minute ago  Up 1 minute (healthy)   3306/tcp",
            "erp-redis-1          redis:7        cmd           redis     1 minute ago  Up 1 minute (healthy)   6379/tcp",
            "erp-app-1            erp-app        cmd           app       1 minute ago  Up 1 minute (healthy)   8000/tcp",
            "erp-nginx-1          nginx:1.27     cmd           nginx     1 minute ago  Up 1 minute (healthy)   80/tcp",
        ]
    )
    assert unhealthy_services(parse_compose_ps_output(output)) == {}


def make_runner(tmp_path: Path, *, ci: bool = False, skip_sqlserver: bool = False, skip_e2e: bool = False):
    args = argparse.Namespace(
        output_dir=tmp_path,
        ci=ci,
        local=not ci,
        skip_sqlserver=skip_sqlserver,
        skip_e2e=skip_e2e,
        keep_services=False,
    )
    return AcceptanceRunner(args)


def emit_core_passes(runner: AcceptanceRunner):
    for name in sorted(CORE_BLOCKING):
        runner.emit("PASS", name)


def test_ci_success_reports_ci_pass_and_local_windows_not_run(tmp_path):
    runner = make_runner(tmp_path, ci=True)
    emit_core_passes(runner)
    assert runner.finalize() == 0
    report = (tmp_path / "V31_ACCEPTANCE_REPORT.md").read_text(encoding="utf-8")
    assert "Execution mode: CI" in report
    assert "Local Windows status: NOT RUN" in report
    assert "CI status: PASS" in report


def test_ci_failure_reports_ci_fail(tmp_path):
    runner = make_runner(tmp_path, ci=True)
    emit_core_passes(runner)
    runner.emit("FAIL", "Docker services healthy", "redis unhealthy")
    assert runner.finalize() == 1
    assert "CI status: FAIL" in (tmp_path / "V31_ACCEPTANCE_REPORT.md").read_text(encoding="utf-8")


def test_windows_local_success_reports_windows_pass(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.run_v31_acceptance.platform.system", lambda: "Windows")
    runner = make_runner(tmp_path)
    emit_core_passes(runner)
    assert runner.finalize() == 0
    payload = json.loads((tmp_path / "acceptance.json").read_text(encoding="utf-8"))
    assert payload["local_status"] == "PASS"
    assert payload["local_windows_status"] == "PASS"
    assert payload["ci_status"] == "NOT RUN"


def test_linux_local_success_does_not_claim_windows_pass(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.run_v31_acceptance.platform.system", lambda: "Linux")
    runner = make_runner(tmp_path)
    emit_core_passes(runner)
    assert runner.finalize() == 0
    payload = json.loads((tmp_path / "acceptance.json").read_text(encoding="utf-8"))
    assert payload["local_status"] == "PASS"
    assert payload["local_windows_status"] == "NOT RUN"


def test_blocked_core_check_returns_nonzero_and_keeps_unique_names(tmp_path):
    runner = make_runner(tmp_path)
    emit_core_passes(runner)
    runner.emit("BLOCKED", "Docker", "engine unavailable")
    assert runner.finalize() == 1
    assert len({row["name"] for row in runner.results}) == len(runner.results)
    payload = json.loads((tmp_path / "acceptance.json").read_text(encoding="utf-8"))
    assert payload["local_status"] == "BLOCKED"


@pytest.mark.parametrize("skip_name,flag", [("SQL Server", "skip_sqlserver"), ("E2E", "skip_e2e")])
def test_explicit_skip_cannot_receive_grade_c(tmp_path, skip_name, flag):
    runner = make_runner(tmp_path, **{flag: True})
    emit_core_passes(runner)
    runner.emit("SKIP", skip_name, f"explicit --{flag.replace('_', '-')}")
    assert runner.finalize() == 0
    report = (tmp_path / "V31_ACCEPTANCE_REPORT.md").read_text(encoding="utf-8")
    assert "Final grade: B (partial verification)" in report
    assert "Final grade: C" not in report
