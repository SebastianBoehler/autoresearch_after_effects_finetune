from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    status = _run_harnesses(
        harness_dir=args.harness_dir,
        app_name=args.app_name,
        timeout_seconds=args.timeout_seconds,
        runner=subprocess.run,
        dry_run=args.dry_run,
    )
    write_json(args.output, status)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(status))
    print(status["summary"])
    if not status["summary"]["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness-dir", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_play_session_harnesses")
    parser.add_argument("--app-name", default="Adobe After Effects 2026")
    parser.add_argument("--timeout-seconds", type=int, default=360)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_play_session_harnesses/status.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_play_session_harnesses/status.md")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _run_harnesses(
    *,
    harness_dir: Path,
    app_name: str,
    timeout_seconds: int,
    runner: Callable[..., subprocess.CompletedProcess[str]],
    dry_run: bool = False,
) -> dict[str, Any]:
    scripts = _script_paths(harness_dir)
    chunks = []
    for script in scripts:
        result = _run_script(
            script,
            app_name=app_name,
            timeout_seconds=timeout_seconds,
            runner=runner,
            dry_run=dry_run,
        )
        chunks.append(result)
        if not result["ok"] and not dry_run:
            break
    failed = [chunk for chunk in chunks if not chunk["ok"]]
    return {
        "summary": {
            "ok": bool(scripts) and not failed and len(chunks) == len(scripts),
            "dry_run": dry_run,
            "script_count": len(scripts),
            "completed_chunks": sum(1 for chunk in chunks if chunk["ok"]),
            "failed_chunks": len(failed),
            "harness_dir": str(harness_dir),
            "app_name": app_name,
        },
        "chunks": chunks,
    }


def _script_paths(harness_dir: Path) -> list[Path]:
    return sorted(harness_dir.glob("play_review_*.jsx"))


def _run_script(
    script: Path,
    *,
    app_name: str,
    timeout_seconds: int,
    runner: Callable[..., subprocess.CompletedProcess[str]],
    dry_run: bool,
) -> dict[str, Any]:
    probe_path = script.with_suffix(".probe.txt")
    if probe_path.exists():
        probe_path.unlink()
    command = _osascript_command(script, app_name=app_name, timeout_seconds=timeout_seconds, probe_path=probe_path)
    if dry_run:
        return {
            "script_path": str(script),
            "returncode": 0,
            "ok": True,
            "stdout": "",
            "stderr": "",
            "dry_run": True,
        }
    result = runner(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout_seconds + 15,
        check=False,
    )
    probe = _probe_status(probe_path)
    missing_probe = result.returncode == 0 and probe != "done"
    return {
        "script_path": str(script),
        "returncode": result.returncode,
        "ok": result.returncode == 0 and not missing_probe,
        "stdout": result.stdout[-2000:],
        "stderr": (
            "After Effects did not write the play-session probe; DoScriptFile may not have executed."
            if missing_probe else result.stderr[-2000:]
        ),
        "probe_path": str(probe_path),
        "probe": probe,
        "dry_run": False,
    }


def _osascript_command(script: Path, *, app_name: str, timeout_seconds: int, probe_path: Path | None = None) -> list[str]:
    skip_on = "$.global.AEFT_SKIP_CONFIRM = true; $.global.AEFT_SKIP_ALERT = true; $.global.AEFT_THROW_ON_ERRORS = true;"
    skip_off = "$.global.AEFT_SKIP_CONFIRM = false; $.global.AEFT_SKIP_ALERT = false; $.global.AEFT_THROW_ON_ERRORS = false;"
    command = [
        "osascript",
        "-e",
        f"with timeout of {timeout_seconds} seconds",
        "-e",
        f"tell application {_applescript_string(app_name)}",
        "-e",
        f"DoScript {_applescript_string(skip_on)}",
    ]
    if probe_path:
        command.extend(["-e", f"DoScript {_applescript_string(_probe_script(probe_path, 'start'))}"])
    command.extend([
        "-e",
        "try",
        "-e",
        f"DoScriptFile {_applescript_string(str(script))}",
        "-e",
        "on error errMsg number errNum",
        "-e",
        f"DoScript {_applescript_string(skip_off)}",
        "-e",
        "error errMsg number errNum",
        "-e",
        "end try",
        "-e",
        f"DoScript {_applescript_string(skip_off)}",
    ])
    if probe_path:
        command.extend(["-e", f"DoScript {_applescript_string(_probe_script(probe_path, 'done'))}"])
    command.extend([
        "-e",
        "end tell",
        "-e",
        "end timeout",
    ])
    return command


def _probe_script(path: Path, value: str) -> str:
    return (
        f'var f = new File({_applescript_string(str(path))}); '
        f'f.encoding = "UTF-8"; f.open("w"); f.writeln("{value}"); f.close();'
    )


def _probe_status(path: Path) -> str:
    return path.read_text(errors="replace").strip() if path.exists() else ""


def _applescript_string(value: str) -> str:
    return json.dumps(value)


def _markdown(status: dict[str, Any]) -> str:
    summary = status["summary"]
    lines = [
        "# AE Play Session Harness Status",
        "",
        f"- ok: {summary['ok']}",
        f"- dry run: {summary['dry_run']}",
        f"- scripts: {summary['script_count']}",
        f"- completed chunks: {summary['completed_chunks']}",
        f"- failed chunks: {summary['failed_chunks']}",
        "",
        "| ok | script | returncode | error |",
        "| --- | --- | ---: | --- |",
    ]
    for chunk in status["chunks"]:
        error = (chunk.get("stderr") or "-").replace("\n", " ")[:240]
        lines.append(
            f"| {chunk['ok']} | {Path(chunk['script_path']).name} | "
            f"{chunk['returncode']} | {error} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
