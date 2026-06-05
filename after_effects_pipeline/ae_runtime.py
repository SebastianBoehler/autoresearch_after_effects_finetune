from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from after_effects_pipeline.types import AfterEffectsRuntimeConfig
from after_effects_pipeline.utils import ensure_dir


def run_live_check(
    *,
    case: dict[str, Any],
    code: str,
    runtime: AfterEffectsRuntimeConfig,
    output_dir: Path,
    timeout_seconds: int,
    render: bool,
) -> dict[str, Any]:
    ensure_dir(output_dir)
    case_dir = output_dir / case["case_id"]
    ensure_dir(case_dir)
    report_path = case_dir / "report.txt"
    project_path = case_dir / "project.aep"
    script_path = case_dir / "harness.jsx"
    script_path.write_text(_build_harness(case, code, report_path, project_path))

    command = [
        "osascript",
        "-e",
        f'tell application "{runtime.app_name}" to DoScriptFile "{script_path}"',
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    report = _parse_report(report_path)
    report.update(
        {
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
            "script_path": str(script_path),
            "project_path": str(project_path),
            "ok": result.returncode == 0 and report.get("ok") == "true",
        }
    )
    if render and report["ok"]:
        report["render_ok"] = _run_aerender(case, runtime, project_path, case_dir)
    return report


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
  try {{
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
    case: dict[str, Any],
    runtime: AfterEffectsRuntimeConfig,
    project_path: Path,
    case_dir: Path,
) -> bool:
    aerender = runtime.aerender_path
    if not aerender or not Path(aerender).exists():
        return False
    expected = case.get("expected", {})
    comp_name = expected.get("comp_name") or runtime.composition_name_fallback
    output_path = case_dir / f"render.{runtime.output_extension}"
    command = [
        aerender,
        "-project",
        str(project_path),
        "-comp",
        comp_name,
        "-output",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    (case_dir / "aerender.log").write_text(result.stdout + result.stderr)
    return result.returncode == 0 and output_path.exists()


def _parse_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload: dict[str, Any] = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            payload[key] = value
    return payload


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line if line else "" for line in text.splitlines())


def _jsx_path(path: Path) -> str:
    return _jsx_string(str(path))


def _jsx_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')

