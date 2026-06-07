from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from after_effects_pipeline.ae_preferences import inspect_scripting_access
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    status = _run_harness(
        runner_path=args.runner,
        app_name=args.app_name,
        timeout_seconds=args.timeout_seconds,
        dry_run=args.dry_run,
        process_runner=subprocess.run,
    )
    write_json(args.output, status)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(status))
    print(status["summary"])
    if not status["summary"]["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_render_unlocks/run_all_harnesses.jsx")
    parser.add_argument("--app-name", default="Adobe After Effects 2026")
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_render_unlocks/run-status.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_render_unlocks/run-status.md")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _run_harness(
    *,
    runner_path: Path,
    app_name: str,
    timeout_seconds: int,
    process_runner: Callable[..., subprocess.CompletedProcess[str]],
    dry_run: bool = False,
    preferences_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prefs = preferences_report or inspect_scripting_access()
    if not runner_path.exists():
        return _blocked("missing_runner", runner_path, prefs, dry_run, "run_all_harnesses.jsx was not found")
    if dry_run:
        return _status(True, runner_path, prefs, dry_run, 0, "", "", "dry_run")
    if prefs.get("ok") is not True:
        return _blocked("scripting_access_disabled", runner_path, prefs, dry_run, prefs.get("advice", ""))
    report_path = runner_path.parent / "runner_report.txt"
    if report_path.exists():
        report_path.unlink()
    result = process_runner(
        _osascript_command(runner_path, app_name=app_name, timeout_seconds=timeout_seconds),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout_seconds + 30,
        check=False,
    )
    report = _runner_report(runner_path)
    if result.returncode == 0 and not report["exists"]:
        return _status(
            False,
            runner_path,
            prefs,
            dry_run,
            result.returncode,
            result.stdout[-2000:],
            "After Effects did not write runner_report.txt; DoScriptFile may not have executed.",
            "missing_runner_report",
            report,
        )
    if result.returncode == 0 and report["error_chunks"]:
        return _status(
            False,
            runner_path,
            prefs,
            dry_run,
            result.returncode,
            result.stdout[-2000:],
            "\n".join(report["errors"])[-2000:],
            "runner_chunk_errors",
            report,
        )
    if result.returncode == 0 and report["expected_chunks"] and report["completed_chunks"] < report["expected_chunks"]:
        return _status(
            False,
            runner_path,
            prefs,
            dry_run,
            result.returncode,
            result.stdout[-2000:],
            "After Effects wrote an incomplete runner_report.txt.",
            "incomplete_runner_report",
            report,
        )
    return _status(
        result.returncode == 0 and report["exists"],
        runner_path,
        prefs,
        dry_run,
        result.returncode,
        result.stdout[-2000:],
        result.stderr[-2000:],
        "completed" if result.returncode == 0 else "osascript_failed",
        report,
    )


def _osascript_command(runner_path: Path, *, app_name: str, timeout_seconds: int) -> list[str]:
    skip_on = "$.global.AEFT_SKIP_CONFIRM = true; $.global.AEFT_SKIP_ALERT = true; $.global.AEFT_THROW_ON_ERRORS = true;"
    skip_off = "$.global.AEFT_SKIP_CONFIRM = false; $.global.AEFT_SKIP_ALERT = false; $.global.AEFT_THROW_ON_ERRORS = false;"
    return [
        "osascript", "-e", f"with timeout of {timeout_seconds} seconds",
        "-e", f"tell application {_applescript_string(app_name)}",
        "-e", f"DoScript {_applescript_string(skip_on)}",
        "-e", "try",
        "-e", f"DoScriptFile {_applescript_string(str(runner_path))}",
        "-e", "on error errMsg number errNum",
        "-e", f"DoScript {_applescript_string(skip_off)}",
        "-e", "error errMsg number errNum",
        "-e", "end try",
        "-e", f"DoScript {_applescript_string(skip_off)}",
        "-e", "end tell", "-e", "end timeout",
    ]


def _blocked(reason: str, runner_path: Path, prefs: dict[str, Any], dry_run: bool, message: str) -> dict[str, Any]:
    return _status(False, runner_path, prefs, dry_run, 1, "", message, reason)


def _status(
    ok: bool,
    runner_path: Path,
    prefs: dict[str, Any],
    dry_run: bool,
    returncode: int,
    stdout: str,
    stderr: str,
    reason: str,
    runner_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = runner_report or _empty_runner_report(runner_path)
    return {
        "summary": {
            "ok": ok,
            "reason": reason,
            "dry_run": dry_run,
            "returncode": returncode,
            "runner_path": str(runner_path),
            "script_file_network_access": prefs.get("script_file_network_access"),
            "javascript_debugger": prefs.get("javascript_debugger"),
            "runner_report_exists": report["exists"],
            "completed_chunks": report["completed_chunks"],
            "error_chunks": report["error_chunks"],
        },
        "stdout": stdout,
        "stderr": stderr,
        "preferences": prefs,
        "runner_report": report,
    }


def _runner_report(runner_path: Path) -> dict[str, Any]:
    report_path = runner_path.parent / "runner_report.txt"
    expected = len(list(runner_path.parent.glob("manual_harness_*.jsx")))
    if not report_path.exists():
        return _empty_runner_report(runner_path, expected_chunks=expected)
    lines = [line.strip() for line in report_path.read_text(errors="replace").splitlines() if line.strip()]
    errors = [line for line in lines if line.startswith("error:")]
    completed = [line for line in lines if line.startswith("ok:")]
    return {
        "exists": True,
        "path": str(report_path),
        "expected_chunks": expected,
        "completed_chunks": len(completed),
        "error_chunks": len(errors),
        "errors": errors,
        "lines": lines,
    }


def _empty_runner_report(runner_path: Path, *, expected_chunks: int | None = None) -> dict[str, Any]:
    expected = len(list(runner_path.parent.glob("manual_harness_*.jsx"))) if expected_chunks is None else expected_chunks
    return {
        "exists": False,
        "path": str(runner_path.parent / "runner_report.txt"),
        "expected_chunks": expected,
        "completed_chunks": 0,
        "error_chunks": 0,
        "errors": [],
        "lines": [],
    }


def _markdown(status: dict[str, Any]) -> str:
    summary = status["summary"]
    return "\n".join([
        "# AE Render-Unlock Runner Status",
        "",
        f"- ok: {summary['ok']}",
        f"- reason: {summary['reason']}",
        f"- dry run: {summary['dry_run']}",
        f"- returncode: {summary['returncode']}",
        f"- file/network access: {summary['script_file_network_access']}",
        f"- JavaScript debugger: {summary['javascript_debugger']}",
        f"- runner report exists: {summary['runner_report_exists']}",
        f"- completed chunks: {summary['completed_chunks']}",
        f"- error chunks: {summary['error_chunks']}",
        f"- runner: {summary['runner_path']}",
        f"- stderr: {(status.get('stderr') or '-')[:500]}",
    ]) + "\n"


def _applescript_string(value: str) -> str:
    return json.dumps(value)


if __name__ == "__main__":
    main()
