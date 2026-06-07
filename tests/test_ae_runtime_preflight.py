from subprocess import CompletedProcess

from after_effects_pipeline import ae_runtime
from after_effects_pipeline.types import AfterEffectsRuntimeConfig


def test_preflight_fails_fast_when_active_preferences_deny_file_access(tmp_path):
    _write_general_prefs(
        tmp_path / "prefs" / "26.2",
        {
            "Pref_JAVASCRIPT_DEBUGGER": '"1"',
        },
    )

    report = ae_runtime.preflight_live_runtime(
        runtime=AfterEffectsRuntimeConfig(),
        output_dir=tmp_path / "out",
        timeout_seconds=1,
        preferences_root=tmp_path / "prefs",
    )

    assert not report["ok"]
    assert report["preference_report"]["active_version"] == "26.2"
    assert "file/network access is not enabled" in report["error"]
    assert "debugger checkbox is already enabled" in report["advice"]


def test_preflight_reports_ae_script_file_access_denial(monkeypatch, tmp_path):
    def fake_run_doscript_file(**_kwargs):
        return CompletedProcess(args=[], returncode=0, stdout="1\n", stderr="")

    monkeypatch.setattr(ae_runtime, "_run_doscript_file", fake_run_doscript_file)

    report = ae_runtime.preflight_live_runtime(
        runtime=AfterEffectsRuntimeConfig(),
        output_dir=tmp_path,
        timeout_seconds=1,
        preferences_root=tmp_path / "prefs",
    )

    assert not report["ok"]
    assert "without writing" in report["error"]
    assert "Restart After Effects" in report["advice"]
    assert "Allow Scripts to Write Files" in report["advice"]


def test_preflight_reports_doscriptfile_noop_when_preferences_allow_access(monkeypatch, tmp_path):
    _write_general_prefs(tmp_path / "prefs" / "26.2", {"Pref_JAVASCRIPT_DEBUGGER": '"1"'})
    _write_main_prefs(tmp_path / "prefs" / "26.2", {"Pref_SCRIPTING_FILE_NETWORK_SECURITY": '"1"'})

    def fake_run_doscript_file(**_kwargs):
        return CompletedProcess(args=[], returncode=0, stdout="1\n", stderr="")

    monkeypatch.setattr(ae_runtime, "_run_doscript_file", fake_run_doscript_file)

    report = ae_runtime.preflight_live_runtime(
        runtime=AfterEffectsRuntimeConfig(),
        output_dir=tmp_path,
        timeout_seconds=1,
        preferences_root=tmp_path / "prefs",
    )

    assert not report["ok"]
    assert "DoScriptFile may not be executing" in report["error"]
    assert "visible clean session" in report["advice"]
    assert "Allow Scripts to Write Files" not in report["advice"]


def test_preflight_accepts_written_report(monkeypatch, tmp_path):
    def fake_run_doscript_file(**_kwargs):
        (tmp_path / "_preflight" / "report.txt").write_text("ok=true\n")
        return CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(ae_runtime, "_run_doscript_file", fake_run_doscript_file)

    report = ae_runtime.preflight_live_runtime(
        runtime=AfterEffectsRuntimeConfig(),
        output_dir=tmp_path,
        timeout_seconds=1,
        preferences_root=tmp_path / "prefs",
    )

    assert report["ok"]


def test_preflight_reports_ae_timeout(monkeypatch, tmp_path):
    def fake_run_doscript_file(**_kwargs):
        return CompletedProcess(args=[], returncode=124, stdout="", stderr="AppleEvent timed out.")

    monkeypatch.setattr(ae_runtime, "_run_doscript_file", fake_run_doscript_file)

    report = ae_runtime.preflight_live_runtime(
        runtime=AfterEffectsRuntimeConfig(),
        output_dir=tmp_path,
        timeout_seconds=1,
        preferences_root=tmp_path / "prefs",
    )

    assert not report["ok"]
    assert "did not respond" in report["error"]
    assert "Restart After Effects" in report["advice"]


def test_preflight_reports_german_appleevent_timeout(monkeypatch, tmp_path):
    def fake_run_doscript_file(**_kwargs):
        return CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="AppleEvent lieferte eine Zeitüberschreitung. (-1712)",
        )

    monkeypatch.setattr(ae_runtime, "_run_doscript_file", fake_run_doscript_file)

    report = ae_runtime.preflight_live_runtime(
        runtime=AfterEffectsRuntimeConfig(),
        output_dir=tmp_path,
        timeout_seconds=1,
        preferences_root=tmp_path / "prefs",
    )

    assert not report["ok"]
    assert "did not respond" in report["error"]
    assert "Restart After Effects" in report["advice"]


def _write_general_prefs(version_dir, values):
    version_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Text File Version 1.1", '["Main Pref Section v2"]']
    lines.extend(f'\t"{key}" = {value}' for key, value in values.items())
    pref_path = version_dir / f"Adobe After Effects {version_dir.name} Einstellungen-indep-general.txt"
    pref_path.write_text("\n".join(lines) + "\n")


def _write_main_prefs(version_dir, values):
    version_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Text File Version 1.1", '["Main Pref Section v2"]']
    lines.extend(f'\t"{key}" = {value}' for key, value in values.items())
    pref_path = version_dir / f"Adobe After Effects {version_dir.name} Einstellungen.txt"
    pref_path.write_text("\n".join(lines) + "\n")
