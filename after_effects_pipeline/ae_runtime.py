from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from after_effects_pipeline.ae_preferences import inspect_scripting_access
from after_effects_pipeline.types import AfterEffectsRuntimeConfig
from after_effects_pipeline.utils import ensure_dir

SCRIPT_ACCESS_HELP = "Restart After Effects into a clean session, then confirm After Effects > Preferences > Scripting & Expressions > Allow Scripts to Write Files and Access Network is enabled. The JavaScript Debugger checkbox is separate and is not enough."
SCRIPT_NO_REPORT_ERROR = "After Effects returned from the live verifier preflight without writing its report. The JSX body may not have executed, or AE may have denied script file/network access."
SCRIPT_NO_REPORT_WITH_ACCESS_ERROR = "After Effects accepted the live verifier AppleScript command but did not write its report. DoScriptFile may not be executing in the current AE session."
SCRIPT_ACCESS_PREF = "Enable After Effects > Preferences > Scripting & Expressions > Allow Scripts to Write Files and Access Network, then rerun the live check."

def preflight_live_runtime(
    *, runtime: AfterEffectsRuntimeConfig, output_dir: Path,
    timeout_seconds: int, preferences_root: Path | None = None,
) -> dict[str, Any]:
    ensure_dir(output_dir)
    preflight_dir = output_dir / "_preflight"
    ensure_dir(preflight_dir)
    preference_report = inspect_scripting_access(preferences_root)
    if preference_report["active_version"] and not preference_report["ok"]:
        return _preference_preflight_failure(preference_report)
    report_path = preflight_dir / "report.txt"
    script_path = preflight_dir / "preflight.jsx"
    report_path.write_text("")
    script_path.write_text(_build_preflight(report_path))

    result = _run_doscript_file(runtime=runtime, script_path=script_path, timeout_seconds=timeout_seconds)
    report = _parse_report(report_path)
    report.update(
        {
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
            "script_path": str(script_path),
            "report_path": str(report_path),
            "ok": result.returncode == 0 and report.get("ok") == "true",
        }
    )
    if not report["ok"] and not report_path.read_text().strip():
        output = f"{result.stdout}\n{result.stderr}".lower()
        timed_out = result.returncode == 124 or "timed out" in output or "zeitüberschreitung" in output or "-1712" in output
        if timed_out:
            report["error"] = "After Effects did not respond to the live verifier preflight."
            report["advice"] = "Restart After Effects, then rerun the live check."
        elif preference_report.get("ok") is True:
            report["error"] = SCRIPT_NO_REPORT_WITH_ACCESS_ERROR
            report["advice"] = "Restart After Effects into a visible clean session, then rerun the live check. If it still no-ops, run the generated JSX via File > Scripts > Run Script File."
        else:
            report["error"] = SCRIPT_NO_REPORT_ERROR
            report["advice"] = SCRIPT_ACCESS_HELP
    return report


def _preference_preflight_failure(preference_report: dict[str, Any]) -> dict[str, Any]:
    error = (
        "After Effects scripting file/network access is not enabled "
        f"(active version {preference_report['active_version']}; "
        f"JavaScript debugger={preference_report['javascript_debugger']}; "
        f"file/network access={preference_report['script_file_network_access']})."
    )
    return {
        "ok": False, "returncode": None, "stdout": "", "stderr": "",
        "script_path": "", "report_path": "", "preference_report": preference_report,
        "error": error, "advice": preference_report["advice"],
    }


def describe_live_preflight_error(report: dict[str, Any]) -> str:
    details = report.get("error") or "After Effects live runtime preflight failed."
    advice = report.get("advice") or SCRIPT_ACCESS_PREF
    script_path = report.get("script_path", "")
    location = f"\nPreflight script: {script_path}" if script_path else ""
    return f"{details}\n{advice}{location}"


def run_live_check(
    *, case: dict[str, Any], code: str, runtime: AfterEffectsRuntimeConfig,
    output_dir: Path, timeout_seconds: int, render: bool,
) -> dict[str, Any]:
    ensure_dir(output_dir)
    case_dir = output_dir / case["case_id"]
    ensure_dir(case_dir)
    report_path = case_dir / "report.txt"
    project_path = case_dir / "project.aep"
    project_tmp_path = case_dir / "project.next.aep"
    script_path = case_dir / "harness.jsx"
    report_path.write_text("")
    if project_tmp_path.exists():
        project_tmp_path.unlink()
    script_path.write_text(_build_harness(case, code, report_path, project_tmp_path))

    result = _run_doscript_file(runtime=runtime, script_path=script_path, timeout_seconds=timeout_seconds)
    report = _parse_report(report_path)
    report.update(
        {
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
            "script_path": str(script_path),
            "project_path": str(project_path),
            "ok": result.returncode == 0 and report.get("ok") == "true" and project_tmp_path.exists(),
        }
    )
    if report["ok"]:
        project_tmp_path.replace(project_path)
    if render and report["ok"]:
        report["render_ok"] = _run_aerender(case, runtime, project_path, case_dir)
    elif result.returncode == 124 and not report.get("error"):
        report["error"] = f"After Effects DoScriptFile timed out after {timeout_seconds}s."
    return report


def _run_doscript_file(
    *, runtime: AfterEffectsRuntimeConfig, script_path: Path, timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    command = [
        "osascript",
        "-e",
        f"with timeout of {timeout_seconds} seconds",
        "-e",
        f'tell application "{runtime.app_name}" to DoScriptFile "{script_path}"',
        "-e",
        "end timeout",
    ]
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 15,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        stdout = _stringify_timeout_payload(error.stdout)
        stderr = _stringify_timeout_payload(error.stderr)
        if stderr:
            stderr += "\n"
        stderr += f"After Effects DoScriptFile timed out after {timeout_seconds}s."
        return subprocess.CompletedProcess(
            args=command,
            returncode=124,
            stdout=stdout,
            stderr=stderr,
        )


def _build_preflight(report_path: Path) -> str:
    return f"""
(function() {{
  var f = new File("{_jsx_path(report_path)}");
  f.encoding = "UTF-8";
  f.open("w");
  f.writeln("ok=true");
  f.close();
}})();
""".strip() + "\n"


def _build_harness(
    case: dict[str, Any],
    code: str,
    report_path: Path,
    project_path: Path,
) -> str:
    expected = case.get("expected", {})
    comp_name = expected.get("comp_name", "")
    return f"""
(function() {{
  function writeReport(fields) {{
    var f = new File("{_jsx_path(report_path)}");
    f.encoding = "UTF-8";
    f.open("w");
    for (var key in fields) {{
      f.writeln(key + "=" + String(fields[key]));
    }}
    f.close();
  }}
  function findCompByName(name) {{
    for (var i = 1; i <= app.project.numItems; i++) {{
      var item = app.project.item(i);
      if (item instanceof CompItem && item.name === name) return item;
    }}
    return null;
  }}
  function removeCompsByName(name) {{
    if (!name) return;
    for (var i = app.project.numItems; i >= 1; i--) {{
      var item = app.project.item(i);
      if (item instanceof CompItem && item.name === name) {{
        item.remove();
      }}
    }}
  }}
  function removeGeneratedComps() {{
    for (var i = app.project.numItems; i >= 1; i--) {{
      var item = app.project.item(i);
      if (item instanceof CompItem && item.name.indexOf("AEFT ") === 0) {{
        item.remove();
      }}
    }}
  }}
  try {{
    removeGeneratedComps();
    removeCompsByName("{_jsx_string(comp_name)}");
    $.global.AEFT_ASSET_ROOT = "{_jsx_path(Path(__file__).resolve().parents[1] / "data" / "synthetic" / "assets")}";
{_indent(code, "    ")}
    var comp = findCompByName("{_jsx_string(comp_name)}");
    if (comp === null && app.project.numItems > 0) {{
      for (var j = 1; j <= app.project.numItems; j++) {{
        var candidate = app.project.item(j);
        if (candidate instanceof CompItem) {{ comp = candidate; break; }}
      }}
    }}
    app.project.save(new File("{_jsx_path(project_path)}"));
    writeReport({{
      ok: comp !== null,
      compFound: comp !== null,
      compName: comp !== null ? comp.name : "",
      width: comp !== null ? comp.width : 0,
      height: comp !== null ? comp.height : 0,
      duration: comp !== null ? comp.duration : 0,
      frameRate: comp !== null ? comp.frameRate : 0,
      numLayers: comp !== null ? comp.numLayers : 0
    }});
  }} catch (e) {{
    writeReport({{ ok: false, error: e.toString(), line: e.line || "" }});
    app.exitCode = 1;
  }}
}})();
""".strip() + "\n"


def _run_aerender(
    case: dict[str, Any], runtime: AfterEffectsRuntimeConfig, project_path: Path, case_dir: Path,
) -> bool:
    aerender = runtime.aerender_path
    if not aerender or not Path(aerender).exists():
        return False
    expected = case.get("expected", {})
    comp_name = expected.get("comp_name") or runtime.composition_name_fallback
    output_path = case_dir / f"render.{runtime.output_extension}"
    tmp_output_path = case_dir / f"render.next.{runtime.output_extension}"
    if tmp_output_path.exists():
        tmp_output_path.unlink()
    command = [
        aerender,
        "-project",
        str(project_path),
        "-comp",
        comp_name,
        "-output",
        str(tmp_output_path),
    ]
    result = subprocess.run(command, capture_output=True, check=False)
    log = _decode_process_output(result.stdout) + _decode_process_output(result.stderr)
    (case_dir / "aerender.log").write_text(log)
    ok = result.returncode == 0 and tmp_output_path.exists()
    if ok: tmp_output_path.replace(output_path)
    return ok


def _parse_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload: dict[str, Any] = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            payload[key] = value
    return payload


def _decode_process_output(payload: bytes) -> str:
    return payload.decode("utf-8", errors="replace")


def _stringify_timeout_payload(payload: bytes | str | None) -> str:
    if payload is None: return ""
    return _decode_process_output(payload) if isinstance(payload, bytes) else payload


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line if line else "" for line in text.splitlines())


def _jsx_path(path: Path) -> str:
    return _jsx_string(str(path))


def _jsx_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
