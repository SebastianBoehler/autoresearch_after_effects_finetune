from subprocess import CompletedProcess

from after_effects_pipeline import ae_runtime
from after_effects_pipeline.types import AfterEffectsRuntimeConfig


def test_decode_process_output_replaces_invalid_utf8():
    assert "bad�log" == ae_runtime._decode_process_output(b"bad\xa4log")


def test_build_harness_removes_existing_named_comp_before_case(tmp_path):
    script = ae_runtime._build_harness(
        {"expected": {"comp_name": "Demo Comp"}},
        "var marker = 1;",
        tmp_path / "report.txt",
        tmp_path / "project.aep",
    )

    assert "function removeGeneratedComps" in script
    assert "removeGeneratedComps();" in script
    assert "function removeCompsByName" in script
    assert 'removeCompsByName("Demo Comp");' in script
    assert script.index("removeGeneratedComps();") < script.index("var marker = 1;")
    assert script.index('removeCompsByName("Demo Comp");') < script.index("var marker = 1;")


def test_run_doscript_file_wraps_appleevent_timeout(monkeypatch, tmp_path):
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["timeout"] = kwargs["timeout"]
        return CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(ae_runtime.subprocess, "run", fake_run)

    result = ae_runtime._run_doscript_file(
        runtime=AfterEffectsRuntimeConfig(app_name="AE Test"),
        script_path=tmp_path / "case.jsx",
        timeout_seconds=180,
    )

    assert result.returncode == 0
    assert "with timeout of 180 seconds" in captured["command"]
    assert captured["timeout"] == 195


def test_run_doscript_file_reports_python_timeout(monkeypatch, tmp_path):
    def fake_run(command, **_kwargs):
        raise ae_runtime.subprocess.TimeoutExpired(command, timeout=2)

    monkeypatch.setattr(ae_runtime.subprocess, "run", fake_run)

    result = ae_runtime._run_doscript_file(
        runtime=AfterEffectsRuntimeConfig(),
        script_path=tmp_path / "case.jsx",
        timeout_seconds=2,
    )

    assert result.returncode == 124
    assert "timed out after 2s" in result.stderr


def test_run_live_check_swaps_project_after_success(monkeypatch, tmp_path):
    case = {"case_id": "demo", "expected": {"comp_name": "Demo"}}
    case_dir = tmp_path / "demo"
    case_dir.mkdir()
    report = case_dir / "report.txt"
    project = case_dir / "project.aep"
    project_next = case_dir / "project.next.aep"
    render = case_dir / "render.mp4"
    report.write_text("ok=true\n")
    project.write_text("stale")
    render.write_text("stale")

    def fake_run_doscript_file(**_kwargs):
        assert report.read_text() == ""
        assert project.read_text() == "stale"
        assert render.read_text() == "stale"
        report.write_text("ok=true\ncompFound=true\n")
        project_next.write_text("fresh")
        return CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    def fake_run_aerender(*_args, **_kwargs):
        assert project.read_text() == "fresh"
        render.write_text("fresh-render")
        return True

    monkeypatch.setattr(ae_runtime, "_run_doscript_file", fake_run_doscript_file)
    monkeypatch.setattr(ae_runtime, "_run_aerender", fake_run_aerender)

    result = ae_runtime.run_live_check(
        case=case,
        code='app.project.items.addComp("Demo", 10, 10, 1, 1, 1);',
        runtime=AfterEffectsRuntimeConfig(output_extension="mp4"),
        output_dir=tmp_path,
        timeout_seconds=1,
        render=True,
    )

    assert result["ok"]
    assert result["render_ok"]
    assert project.read_text() == "fresh"
    assert render.read_text() == "fresh-render"
    assert not project_next.exists()


def test_run_live_check_preserves_outputs_on_doscript_failure(monkeypatch, tmp_path):
    case = {"case_id": "demo", "expected": {"comp_name": "Demo"}}
    case_dir = tmp_path / "demo"
    case_dir.mkdir()
    project = case_dir / "project.aep"
    project_next = case_dir / "project.next.aep"
    render = case_dir / "render.mp4"
    project.write_text("stale-project")
    project_next.write_text("stale-next")
    render.write_text("stale-render")

    def fake_run_doscript_file(**_kwargs):
        assert not project_next.exists()
        return CompletedProcess(args=[], returncode=124, stdout="", stderr="timeout")

    monkeypatch.setattr(ae_runtime, "_run_doscript_file", fake_run_doscript_file)

    result = ae_runtime.run_live_check(
        case=case,
        code='app.project.items.addComp("Demo", 10, 10, 1, 1, 1);',
        runtime=AfterEffectsRuntimeConfig(output_extension="mp4"),
        output_dir=tmp_path,
        timeout_seconds=1,
        render=True,
    )

    assert not result["ok"]
    assert "timed out" in result["error"]
    assert project.read_text() == "stale-project"
    assert render.read_text() == "stale-render"


def test_run_aerender_replaces_existing_output(monkeypatch, tmp_path):
    aerender = tmp_path / "aerender"
    aerender.write_text("#!/bin/sh\n")
    project = tmp_path / "project.aep"
    project.write_text("project")
    output = tmp_path / "render.mp4"
    tmp_output = tmp_path / "render.next.mp4"
    output.write_text("old")

    def fake_run(command, **_kwargs):
        assert str(tmp_output) in command
        tmp_output.write_text("new")
        return CompletedProcess(args=command, returncode=0, stdout=b"", stderr=b"")

    monkeypatch.setattr(ae_runtime.subprocess, "run", fake_run)

    ok = ae_runtime._run_aerender(
        {"expected": {"comp_name": "Demo"}},
        AfterEffectsRuntimeConfig(aerender_path=str(aerender), output_extension="mp4"),
        project,
        tmp_path,
    )

    assert ok
    assert output.read_text() == "new"
    assert not tmp_output.exists()


def test_run_aerender_preserves_existing_output_on_failure(monkeypatch, tmp_path):
    aerender = tmp_path / "aerender"
    aerender.write_text("#!/bin/sh\n")
    project = tmp_path / "project.aep"
    project.write_text("project")
    output = tmp_path / "render.mp4"
    output.write_text("old")

    def fake_run(command, **_kwargs):
        return CompletedProcess(args=command, returncode=1, stdout=b"bad", stderr=b"")

    monkeypatch.setattr(ae_runtime.subprocess, "run", fake_run)

    ok = ae_runtime._run_aerender(
        {"expected": {"comp_name": "Demo"}},
        AfterEffectsRuntimeConfig(aerender_path=str(aerender), output_extension="mp4"),
        project,
        tmp_path,
    )

    assert not ok
    assert output.read_text() == "old"
