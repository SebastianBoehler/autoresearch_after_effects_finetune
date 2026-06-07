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


runner_script = _load_script("run_ae_play_session_harnesses")


def test_play_runner_builds_osascript_command_with_error_throwing(tmp_path):
    script = tmp_path / "play_review_01.jsx"

    command = runner_script._osascript_command(
        script,
        app_name="Adobe After Effects 2026",
        timeout_seconds=120,
    )
    joined = " ".join(command)

    assert command[:2] == ["osascript", "-e"]
    assert "AEFT_THROW_ON_ERRORS = true" in joined
    assert "AEFT_THROW_ON_ERRORS = false" in joined
    assert str(script) in joined


def test_play_runner_records_successful_chunks(tmp_path):
    _write_script(tmp_path, 1)
    _write_script(tmp_path, 2)
    calls = []

    def runner(command, cwd, capture_output, text, timeout, check):
        calls.append(command)
        script = _script_from_command(command)
        script.with_suffix(".probe.txt").write_text("done\n")
        return SimpleNamespace(returncode=0, stdout="1\n", stderr="")

    status = runner_script._run_harnesses(
        harness_dir=tmp_path,
        app_name="AE",
        timeout_seconds=30,
        runner=runner,
    )

    assert len(calls) == 2
    assert status["summary"]["ok"] is True
    assert status["summary"]["completed_chunks"] == 2
    assert status["summary"]["failed_chunks"] == 0


def test_play_runner_fails_when_probe_is_missing(tmp_path):
    _write_script(tmp_path, 1)

    def runner(command, cwd, capture_output, text, timeout, check):
        return SimpleNamespace(returncode=0, stdout="1\n", stderr="")

    status = runner_script._run_harnesses(
        harness_dir=tmp_path,
        app_name="AE",
        timeout_seconds=30,
        runner=runner,
    )

    assert status["summary"]["ok"] is False
    assert status["summary"]["completed_chunks"] == 0
    assert status["summary"]["failed_chunks"] == 1
    assert "play-session probe" in status["chunks"][0]["stderr"]


def test_play_runner_stops_on_first_failed_chunk(tmp_path):
    _write_script(tmp_path, 1)
    _write_script(tmp_path, 2)
    calls = []

    def runner(command, cwd, capture_output, text, timeout, check):
        calls.append(command)
        return SimpleNamespace(returncode=1, stdout="", stderr="bad jsx")

    status = runner_script._run_harnesses(
        harness_dir=tmp_path,
        app_name="AE",
        timeout_seconds=30,
        runner=runner,
    )

    assert len(calls) == 1
    assert status["summary"]["ok"] is False
    assert status["summary"]["completed_chunks"] == 0
    assert status["summary"]["failed_chunks"] == 1
    assert status["chunks"][0]["stderr"] == "bad jsx"


def test_play_runner_dry_run_does_not_call_runner(tmp_path):
    _write_script(tmp_path, 1)
    calls = []

    status = runner_script._run_harnesses(
        harness_dir=tmp_path,
        app_name="AE",
        timeout_seconds=30,
        runner=lambda *args, **kwargs: calls.append((args, kwargs)),
        dry_run=True,
    )

    assert calls == []
    assert status["summary"]["ok"] is True
    assert status["summary"]["dry_run"] is True


def _write_script(path, index):
    (path / f"play_review_{index:02d}.jsx").write_text("// jsx\n")


def _script_from_command(command):
    for index, token in enumerate(command):
        if token == "DoScriptFile":
            return Path(command[index + 1].strip('"'))
    for token in command:
        if token.startswith("DoScriptFile "):
            return Path(token.split("DoScriptFile ")[1].strip('"'))
    raise AssertionError(command)
