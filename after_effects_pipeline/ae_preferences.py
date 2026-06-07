from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

SCRIPT_ACCESS_KEY = "Pref_SCRIPTING_FILE_NETWORK_SECURITY"
JAVASCRIPT_DEBUGGER_KEY = "Pref_JAVASCRIPT_DEBUGGER"
MAIN_PREF_SECTION = "Main Pref Section v2"


def inspect_scripting_access(preferences_root: Path | None = None) -> dict[str, Any]:
    root = preferences_root or _default_preferences_root()
    versions = [_version_payload(path) for path in _version_dirs(root)]
    active = versions[0] if versions else None
    script_access = active.get("script_file_network_access") if active else None
    return {
        "ok": script_access is True,
        "preferences_root": str(root),
        "active_version": active.get("version") if active else "",
        "active_preferences_path": active.get("preferences_path") if active else "",
        "active_scripting_preferences_path": active.get("scripting_preferences_path") if active else "",
        "javascript_debugger": active.get("javascript_debugger") if active else None,
        "script_file_network_access": script_access,
        "versions": versions,
        "advice": _advice(active),
    }


def enable_scripting_access_preference(
    preferences_root: Path | None = None,
    *,
    apply: bool = False,
    after_effects_running: bool | None = None,
) -> dict[str, Any]:
    root = preferences_root or _default_preferences_root()
    active = next((_version_payload(path) for path in _version_dirs(root)), None)
    pref_path = Path(active["scripting_preferences_path"]) if active and active["scripting_preferences_path"] else None
    before = active.get("script_file_network_access") if active else None
    running = _after_effects_is_running() if after_effects_running is None else after_effects_running
    report = {
        "ok": before is True,
        "applied": False,
        "would_apply": False,
        "after_effects_running": running,
        "active_version": active.get("version") if active else "",
        "preferences_path": active.get("preferences_path") if active else "",
        "scripting_preferences_path": str(pref_path) if pref_path else "",
        "before": before,
        "after": before,
        "advice": "",
    }
    if not pref_path:
        report["advice"] = "No active After Effects general preference file was found."
        return report
    if before is True:
        report["advice"] = "After Effects scripting file/network access is already enabled."
        return report

    original = pref_path.read_text(errors="replace")
    updated = _set_preference_text(original, SCRIPT_ACCESS_KEY, "1")
    report["would_apply"] = True
    report["advice"] = "Close After Effects, then rerun with --apply to update the preference file."
    if not apply:
        return report
    if running:
        report["advice"] = "After Effects is running; close it before applying so it does not overwrite preferences on quit."
        return report

    backup_path = pref_path.with_name(pref_path.name + ".aeft-backup")
    if not backup_path.exists():
        backup_path.write_text(original)
    pref_path.write_text(updated)
    after = _version_payload(pref_path.parent).get("script_file_network_access")
    report.update(
        {
            "ok": after is True,
            "applied": after is True,
            "after": after,
            "backup_path": str(backup_path),
            "advice": "Preference file updated; restart After Effects before rerunning live verification.",
        }
    )
    return report


def render_scripting_access_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# After Effects Scripting Access",
        "",
        f"- ok: {report['ok']}",
        f"- active version: {report['active_version'] or '-'}",
        f"- JavaScript debugger: {_flag(report['javascript_debugger'])}",
        f"- file/network access: {_flag(report['script_file_network_access'])}",
        f"- advice: {report['advice']}",
        "",
        "## Preference Files",
        "",
        "| version | JavaScript debugger | file/network access | general path | security path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report["versions"]:
        lines.append(
            f"| {item['version']} | {_flag(item['javascript_debugger'])} | "
            f"{_flag(item['script_file_network_access'])} | {item['preferences_path'] or '-'} | "
            f"{item['scripting_preferences_path'] or '-'} |"
        )
    if not report["versions"]:
        lines.append("| - | - | - | - | - |")
    return "\n".join(lines) + "\n"


def render_enable_scripting_access_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Enable After Effects Scripting Access",
        "",
        f"- ok: {report['ok']}",
        f"- applied: {report['applied']}",
        f"- would apply: {report['would_apply']}",
        f"- After Effects running: {report['after_effects_running']}",
        f"- active version: {report['active_version'] or '-'}",
        f"- before: {_flag(report['before'])}",
        f"- after: {_flag(report['after'])}",
        f"- preferences: {report['preferences_path'] or '-'}",
        f"- scripting preferences: {report.get('scripting_preferences_path') or '-'}",
        f"- advice: {report['advice']}",
    ]
    if report.get("backup_path"):
        lines.append(f"- backup: {report['backup_path']}")
    return "\n".join(lines) + "\n"


def _version_payload(version_dir: Path) -> dict[str, Any]:
    pref_path = _general_preferences_path(version_dir)
    scripting_pref_path = _scripting_preferences_path(version_dir) or pref_path
    prefs = _parse_preferences(pref_path) if pref_path else {}
    scripting_prefs = _parse_preferences(scripting_pref_path) if scripting_pref_path else prefs
    return {
        "version": version_dir.name,
        "preferences_path": str(pref_path) if pref_path else "",
        "scripting_preferences_path": str(scripting_pref_path) if scripting_pref_path else "",
        "javascript_debugger": _bool_pref(prefs.get(JAVASCRIPT_DEBUGGER_KEY)),
        "script_file_network_access": _bool_pref(scripting_prefs.get(SCRIPT_ACCESS_KEY)),
        "script_file_network_access_present": SCRIPT_ACCESS_KEY in scripting_prefs,
    }


def _default_preferences_root() -> Path:
    return Path.home() / "Library/Preferences/Adobe/After Effects"


def _version_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    dirs = [path for path in root.iterdir() if path.is_dir()]
    return sorted(dirs, key=lambda path: _version_key(path.name), reverse=True)


def _version_key(name: str) -> tuple[int, ...]:
    parts = []
    for part in name.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(-1)
    return tuple(parts)


def _general_preferences_path(version_dir: Path) -> Path | None:
    candidates = sorted(version_dir.glob("*indep-general.txt"))
    return candidates[0] if candidates else None


def _scripting_preferences_path(version_dir: Path) -> Path | None:
    candidates = [
        path
        for path in sorted(version_dir.glob("Adobe After Effects *.txt"))
        if "-indep-" not in path.name and path.stem.count("-") == 0
    ]
    return candidates[0] if candidates else None


def _parse_preferences(path: Path) -> dict[str, str]:
    prefs = {}
    for line in path.read_text(errors="replace").splitlines():
        match = re.match(r'\s*"(?P<key>[^"]+)"\s*=\s*(?P<value>.*)\s*$', line)
        if match:
            prefs[match.group("key")] = match.group("value").strip()
    return prefs


def _set_preference_text(
    text: str,
    key: str,
    value: str,
    *,
    section: str = MAIN_PREF_SECTION,
) -> str:
    line_break = _line_break(text)
    lines = text.splitlines()
    header = f'["{section}"]'
    pref_line = f'\t"{key}" = "{value}"'
    in_section = False
    insert_at: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == header:
            in_section = True
            insert_at = index + 1
            continue
        if in_section and stripped.startswith('["') and stripped.endswith('"]'):
            lines.insert(insert_at if insert_at is not None else index, pref_line)
            return line_break.join(lines) + line_break
        if in_section and re.match(rf'\s*"{re.escape(key)}"\s*=', line):
            lines[index] = pref_line
            return line_break.join(lines) + line_break
        if in_section and stripped:
            insert_at = index + 1
    if in_section:
        lines.insert(insert_at if insert_at is not None else len(lines), pref_line)
    else:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([header, pref_line])
    return line_break.join(lines) + line_break


def _line_break(text: str) -> str:
    if "\r\n" in text:
        return "\r\n"
    if "\r" in text:
        return "\r"
    return "\n"


def _bool_pref(raw: str | None) -> bool | None:
    if raw is None:
        return None
    value = raw.strip().strip('"').lower()
    if value in {"1", "01", "true"}:
        return True
    if value in {"0", "00", "false"}:
        return False
    return None


def _flag(value: bool | None) -> str:
    if value is True:
        return "enabled"
    if value is False:
        return "disabled"
    return "not set"


def _advice(active: dict[str, Any] | None) -> str:
    if not active:
        return "No After Effects preference folder was found."
    if active["script_file_network_access"] is True:
        return "After Effects scripting file/network access is enabled."
    if active["javascript_debugger"] is True:
        return "Enable Allow Scripts to Write Files and Access Network; the debugger checkbox is already enabled but is separate. Close After Effects and run scripts/enable_ae_scripting_access.py --apply if the UI does not persist it."
    return "Enable Allow Scripts to Write Files and Access Network before running live verification, or close After Effects and run scripts/enable_ae_scripting_access.py --apply."


def _after_effects_is_running() -> bool:
    result = subprocess.run(
        ["pgrep", "-fl", "Adobe After Effects"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and bool(result.stdout.strip())
