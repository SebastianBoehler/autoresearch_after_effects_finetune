from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script(name):
    path = REPO_ROOT / "scripts" / f"{name}.py"
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner_script = _load_script("run_ae_render_unlock_harnesses")


def test_render_unlock_runner_blocks_when_scripting_access_is_disabled(tmp_path):
    runner = tmp_path / "run_all_harnesses.jsx"
    runner.write_text("// runner\n")

    status = runner_script._run_harness(
        runner_path=runner,
        app_name="AE",
        timeout_seconds=30,
        process_runner=lambda *args, **kwargs: None,
        preferences_report={"ok": False, "advice": "enable pref"},
    )

    assert status["summary"]["ok"] is False
    assert status["summary"]["reason"] == "scripting_access_disabled"
    assert "enable pref" in status["stderr"]


def test_render_unlock_runner_builds_noninteractive_osascript_command(tmp_path):
    runner = tmp_path / "run_all_harnesses.jsx"
    command = runner_script._osascript_command(
        runner,
        app_name="Adobe After Effects 2026",
        timeout_seconds=120,
    )
    joined = " ".join(command)

    assert command[:2] == ["osascript", "-e"]
    assert "AEFT_SKIP_CONFIRM = true" in joined
    assert "AEFT_SKIP_ALERT = true" in joined
    assert "AEFT_THROW_ON_ERRORS = true" in joined
    assert str(runner) in joined


def test_render_unlock_runner_calls_ae_when_preflight_passes(tmp_path):
    runner = tmp_path / "run_all_harnesses.jsx"
    runner.write_text("// runner\n")
    (tmp_path / "manual_harness_01.jsx").write_text("// harness\n")
    calls = []

    def process_runner(command, cwd, capture_output, text, timeout, check):
        calls.append(command)
        (tmp_path / "runner_report.txt").write_text(f"ok:{tmp_path / 'manual_harness_01.jsx'}\n")
        return SimpleNamespace(returncode=0, stdout="done", stderr="")

    status = runner_script._run_harness(
        runner_path=runner,
        app_name="AE",
        timeout_seconds=30,
        process_runner=process_runner,
        preferences_report={"ok": True, "script_file_network_access": True},
    )

    assert calls
    assert status["summary"]["ok"] is True
    assert status["summary"]["reason"] == "completed"
    assert status["summary"]["runner_report_exists"] is True


def test_render_unlock_runner_fails_when_ae_writes_no_runner_report(tmp_path):
    runner = tmp_path / "run_all_harnesses.jsx"
    runner.write_text("// runner\n")
    (tmp_path / "manual_harness_01.jsx").write_text("// harness\n")

    def process_runner(command, cwd, capture_output, text, timeout, check):
        return SimpleNamespace(returncode=0, stdout="1\n", stderr="")

    status = runner_script._run_harness(
        runner_path=runner,
        app_name="AE",
        timeout_seconds=30,
        process_runner=process_runner,
        preferences_report={"ok": True, "script_file_network_access": True},
    )

    assert status["summary"]["ok"] is False
    assert status["summary"]["reason"] == "missing_runner_report"
    assert status["summary"]["runner_report_exists"] is False


def test_render_unlock_runner_markdown_summarizes_status(tmp_path):
    status = runner_script._status(
        False,
        tmp_path / "run_all_harnesses.jsx",
        {"script_file_network_access": None, "javascript_debugger": True},
        False,
        1,
        "",
        "blocked",
        "scripting_access_disabled",
    )

    markdown = runner_script._markdown(status)

    assert "# AE Render-Unlock Runner Status" in markdown
    assert "scripting_access_disabled" in markdown
