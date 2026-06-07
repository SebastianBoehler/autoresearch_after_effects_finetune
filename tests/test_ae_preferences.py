from pathlib import Path

from after_effects_pipeline.ae_preferences import (
    enable_scripting_access_preference,
    inspect_scripting_access,
    render_enable_scripting_access_markdown,
    render_scripting_access_markdown,
)


def test_inspect_scripting_access_reports_debugger_without_file_access(tmp_path):
    _write_general_prefs(
        tmp_path / "26.2",
        {
            "Pref_JAVASCRIPT_DEBUGGER": '"1"',
        },
    )

    report = inspect_scripting_access(tmp_path)

    assert not report["ok"]
    assert report["active_version"] == "26.2"
    assert report["javascript_debugger"] is True
    assert report["script_file_network_access"] is None
    assert "debugger checkbox is already enabled" in report["advice"]


def test_inspect_scripting_access_accepts_file_access(tmp_path):
    _write_general_prefs(
        tmp_path / "25.1",
        {
            "Pref_JAVASCRIPT_DEBUGGER": "00",
            "Pref_SCRIPTING_FILE_NETWORK_SECURITY": "01",
        },
    )
    _write_general_prefs(
        tmp_path / "26.2",
        {
            "Pref_JAVASCRIPT_DEBUGGER": '"1"',
        },
    )
    _write_main_prefs(tmp_path / "26.2", {"Pref_SCRIPTING_FILE_NETWORK_SECURITY": '"1"'})

    report = inspect_scripting_access(tmp_path)

    assert report["ok"]
    assert report["active_version"] == "26.2"
    assert report["script_file_network_access"] is True
    assert "enabled" in render_scripting_access_markdown(report)


def test_inspect_scripting_access_handles_missing_preferences(tmp_path):
    report = inspect_scripting_access(tmp_path)

    assert not report["ok"]
    assert report["active_version"] == ""
    assert "No After Effects preference folder" in report["advice"]


def test_enable_scripting_access_dry_run_does_not_write(tmp_path):
    pref_path = _write_general_prefs(
        tmp_path / "26.2",
        {
            "Pref_JAVASCRIPT_DEBUGGER": '"1"',
        },
    )
    before = pref_path.read_text()

    report = enable_scripting_access_preference(
        tmp_path,
        apply=False,
        after_effects_running=False,
    )

    assert report["would_apply"]
    assert not report["applied"]
    assert pref_path.read_text() == before
    assert "rerun with --apply" in render_enable_scripting_access_markdown(report)


def test_enable_scripting_access_refuses_to_write_while_ae_runs(tmp_path):
    pref_path = _write_general_prefs(
        tmp_path / "26.2",
        {
            "Pref_JAVASCRIPT_DEBUGGER": '"1"',
        },
    )
    before = pref_path.read_text()

    report = enable_scripting_access_preference(
        tmp_path,
        apply=True,
        after_effects_running=True,
    )

    assert report["would_apply"]
    assert not report["applied"]
    assert pref_path.read_text() == before
    assert "After Effects is running" in report["advice"]


def test_enable_scripting_access_applies_when_ae_is_closed(tmp_path):
    pref_path = _write_general_prefs(
        tmp_path / "26.2",
        {
            "Pref_JAVASCRIPT_DEBUGGER": '"1"',
        },
    )

    report = enable_scripting_access_preference(
        tmp_path,
        apply=True,
        after_effects_running=False,
    )

    assert report["ok"]
    assert report["applied"]
    assert report["after"] is True
    assert '"Pref_SCRIPTING_FILE_NETWORK_SECURITY" = "1"' in pref_path.read_text()
    assert Path(report["backup_path"]).exists()
    assert inspect_scripting_access(tmp_path)["ok"]


def test_enable_scripting_access_updates_main_preferences_when_present(tmp_path):
    general_path = _write_general_prefs(
        tmp_path / "26.2",
        {
            "Pref_JAVASCRIPT_DEBUGGER": '"1"',
        },
    )
    main_path = _write_main_prefs(tmp_path / "26.2", {})

    report = enable_scripting_access_preference(
        tmp_path,
        apply=True,
        after_effects_running=False,
    )

    assert report["ok"]
    assert report["applied"]
    assert report["preferences_path"] == str(general_path)
    assert report["scripting_preferences_path"] == str(main_path)
    assert '"Pref_SCRIPTING_FILE_NETWORK_SECURITY" = "1"' in main_path.read_text()
    assert '"Pref_SCRIPTING_FILE_NETWORK_SECURITY" = "1"' not in general_path.read_text()


def _write_general_prefs(version_dir: Path, values: dict[str, str]) -> None:
    version_dir.mkdir(parents=True)
    lines = ["# Text File Version 1.1", "# After Effects Preferences", "", '["Main Pref Section v2"]']
    lines.extend(f'\t"{key}" = {value}' for key, value in values.items())
    pref_path = version_dir / f"Adobe After Effects {version_dir.name} Einstellungen-indep-general.txt"
    pref_path.write_text("\n".join(lines) + "\n")
    return pref_path


def _write_main_prefs(version_dir: Path, values: dict[str, str]) -> Path:
    version_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Text File Version 1.1", "# After Effects Preferences", "", '["Main Pref Section v2"]']
    lines.extend(f'\t"{key}" = {value}' for key, value in values.items())
    pref_path = version_dir / f"Adobe After Effects {version_dir.name} Einstellungen.txt"
    pref_path.write_text("\n".join(lines) + "\n")
    return pref_path
