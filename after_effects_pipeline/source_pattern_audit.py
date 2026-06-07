from __future__ import annotations

import re
from collections import Counter
from typing import Any

from after_effects_pipeline.static_check import extract_code

TIME_PATTERN = re.compile(r"\.setValueAtTime\(\s*([0-9]+(?:\.[0-9]+)?)")
EFFECT_PATTERN = re.compile(r'\.property\(["\']Effects["\']\)\.addProperty')
PROPERTY_PATTERN = re.compile(r'\.property\(["\']([^"\']+)["\']\)')
LOW_VALUE_GAPS = {"layer_mix:simple_scene"}
OVERLAP_IGNORE = {
    "feature:eased_keyframes",
    "feature:loop_generated",
    "property:opacity", "property:position", "property:source_text",
}


def build_source_pattern_audit(
    records: list[dict[str, Any]],
    *,
    render_queue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ready_ids = {
        item["case_id"]
        for item in (render_queue or {}).get("items", [])
        if item.get("train_ready")
    }
    cases = [_case_patterns(record, record["case_id"] in ready_ids) for record in records]
    source_counts = _pattern_counts(cases)
    ready_counts = _pattern_counts([case for case in cases if case["train_ready"]])
    gaps = [
        {"pattern": pattern, "source_count": count, "case_ids": _cases_with(cases, pattern)}
        for pattern, count in source_counts.items()
        if pattern not in ready_counts and pattern not in LOW_VALUE_GAPS
    ]
    return {
        "summary": {
            "case_count": len(cases),
            "train_ready_count": len(ready_ids),
            "source_pattern_count": len(source_counts),
            "train_ready_pattern_count": len(ready_counts),
            "train_ready_pattern_gap_count": len(gaps),
            "pattern_overlap_pair_count": len(_overlap_pairs(cases)),
        },
        "source_pattern_counts": dict(sorted(source_counts.items())),
        "train_ready_pattern_counts": dict(sorted(ready_counts.items())),
        "train_ready_pattern_gaps": gaps,
        "cases": cases,
        "pattern_overlap_pairs": _overlap_pairs(cases),
        "recommendations": _recommendations(gaps),
    }


def render_source_pattern_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Source Animation Pattern Audit",
        "",
        "Static audit of JSX animation construction patterns.",
        "",
        "## Summary",
        "",
        f"- cases: {summary['case_count']}",
        f"- train-ready cases: {summary['train_ready_count']}",
        f"- source patterns: {summary['source_pattern_count']}",
        f"- train-ready patterns: {summary['train_ready_pattern_count']}",
        f"- train-ready pattern gaps: {summary['train_ready_pattern_gap_count']}",
        f"- pattern overlap pairs: {summary['pattern_overlap_pair_count']}",
        "",
        "## Train-Ready Pattern Gaps",
        "",
    ]
    if payload["train_ready_pattern_gaps"]:
        for gap in payload["train_ready_pattern_gaps"]:
            lines.append(
                f"- {gap['pattern']}: source={gap['source_count']}; "
                f"first={gap['case_ids'][0]}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Case Patterns", ""])
    lines.extend([
        "| case | ready | layer mix | motion driver | temporal stage | patterns |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for case in payload["cases"]:
        lines.append(
            f"| {case['case_id']} | {case['train_ready']} | {case['layer_mix']} | "
            f"{case['motion_driver']} | {case['temporal_stage']} | "
            f"{', '.join(case['patterns'])} |"
        )
    lines.extend(["", "## Pattern Overlaps", ""])
    if payload["pattern_overlap_pairs"]:
        for pair in payload["pattern_overlap_pairs"]:
            lines.append(
                f"- {pair['a']} / {pair['b']}: {pair['score']:.2f} "
                f"({', '.join(pair['shared_patterns'])})"
            )
    else:
        lines.append("- none above threshold")
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    return "\n".join(lines) + "\n"


def _case_patterns(record: dict[str, Any], train_ready: bool) -> dict[str, Any]:
    code = extract_code(record["completion"])
    times = _times(code)
    duration = float(record.get("expected", {}).get("duration_seconds") or 0.0)
    metrics = _metrics(code, times, duration)
    layer_mix = _layer_mix(metrics)
    motion_driver = _motion_driver(metrics)
    temporal_stage = _temporal_stage(metrics)
    patterns = sorted({layer_mix, motion_driver, temporal_stage, *_feature_patterns(metrics)})
    return {
        "case_id": record["case_id"],
        "train_ready": train_ready,
        "source_repo_path": record.get("source_repo_path", ""),
        "layer_mix": layer_mix,
        "motion_driver": motion_driver,
        "temporal_stage": temporal_stage,
        "patterns": patterns,
        "metrics": metrics,
    }


def _metrics(code: str, times: list[float], duration: float) -> dict[str, Any]:
    props = Counter(PROPERTY_PATTERN.findall(code))
    text_layers = _estimated_layer_calls(code, ".layers.addText")
    shape_layers = _estimated_layer_calls(code, ".layers.addShape")
    solid_layers = code.count(".layers.addSolid")
    camera_layers = code.count(".layers.addCamera")
    null_layers = code.count(".layers.addNull")
    expression_count = code.count(".expression")
    effect_count = len(EFFECT_PATTERN.findall(code))
    latest = max(times, default=0.0)
    return {
        "duration_seconds": duration,
        "text_layers": text_layers,
        "shape_layers": shape_layers,
        "solid_layers": solid_layers,
        "camera_layers": camera_layers,
        "null_layers": null_layers,
        "total_layers": text_layers + shape_layers + solid_layers + camera_layers + null_layers,
        "three_d_signals": code.count("threeDLayer = true"),
        "keyframe_count": len(times),
        "distinct_time_count": len(set(times)),
        "middle_keyframes": sum(duration * 0.33 <= time < duration * 0.66 for time in times) if duration else 0,
        "late_keyframes": sum(time >= duration * 0.66 for time in times) if duration else 0,
        "temporal_span_ratio": latest / duration if duration else 0.0,
        "expression_count": expression_count,
        "effect_count": effect_count,
        "easing_count": code.count("KeyframeEase") + code.count("setTemporalEaseAtKey"),
        "loop_count": code.count("for ("),
        "marker_count": code.count("MarkerValue") + code.count(".marker"),
        "time_remap_count": props.get("Time Remap", 0),
        "trim_path_count": code.count("Trim Paths") + code.count("ADBE Vector Filter - Trim"),
        "mask_or_matte_count": code.count("alpha matte") + code.count("trackMatteType") + code.count("ADBE Mask"),
        "layout_bounds_count": code.count("sourceRectAtTime"),
        "rect_shape_count": code.count("ADBE Vector Shape - Rect"),
        "ellipse_shape_count": code.count("ADBE Vector Shape - Ellipse"),
        "path_shape_count": code.count("ADBE Vector Shape - Star") + code.count("createPath"),
        "property_families": sorted(_property_families(props)),
    }


def _layer_mix(metrics: dict[str, Any]) -> str:
    if metrics["camera_layers"] or metrics["three_d_signals"] >= 2:
        return "layer_mix:camera_3d"
    if metrics["text_layers"] >= 8 and metrics["shape_layers"] >= 8:
        return "layer_mix:dense_text_shape_system"
    if metrics["text_layers"] >= 5 and metrics["text_layers"] >= metrics["shape_layers"]:
        return "layer_mix:text_system"
    if metrics["shape_layers"] >= 10 and metrics["text_layers"] <= 4:
        return "layer_mix:shape_system"
    if metrics["shape_layers"] >= 4 and metrics["text_layers"] >= 2:
        return "layer_mix:mixed_scene"
    return "layer_mix:simple_scene"


def _motion_driver(metrics: dict[str, Any]) -> str:
    if metrics["time_remap_count"]:
        return "motion_driver:time_remap"
    if metrics["expression_count"] >= 4:
        return "motion_driver:expression_rich"
    if metrics["expression_count"] and metrics["keyframe_count"] >= 8:
        return "motion_driver:hybrid"
    if metrics["effect_count"] >= 2:
        return "motion_driver:effects_driven"
    return "motion_driver:keyframed"


def _temporal_stage(metrics: dict[str, Any]) -> str:
    if metrics["expression_count"] >= 3:
        return "temporal:continuous_expression"
    if metrics["middle_keyframes"] and metrics["late_keyframes"]:
        return "temporal:full_span_staged"
    if metrics["late_keyframes"]:
        return "temporal:late_reveal"
    return "temporal:intro_weighted"


def _feature_patterns(metrics: dict[str, Any]) -> list[str]:
    patterns = []
    for family in metrics["property_families"]:
        patterns.append(f"property:{family}")
    if metrics["easing_count"]:
        patterns.append("feature:eased_keyframes")
    if metrics["marker_count"]:
        patterns.append("feature:markers")
    if metrics["trim_path_count"]:
        patterns.append("feature:trim_paths")
    if metrics["mask_or_matte_count"]:
        patterns.append("feature:masks_or_mattes")
    if metrics["layout_bounds_count"]:
        patterns.append("feature:text_layout_bounds")
    if metrics["loop_count"]:
        patterns.append("feature:loop_generated")
    if metrics["total_layers"] >= 20:
        patterns.append("feature:dense_layer_system")
    if metrics["rect_shape_count"]:
        patterns.append("shape:rectangles")
    if metrics["ellipse_shape_count"]:
        patterns.append("shape:ellipses")
    if metrics["path_shape_count"]:
        patterns.append("shape:paths")
    return patterns


def _property_families(props: Counter[str]) -> set[str]:
    families = set()
    mapping = {
        "Position": "position",
        "Scale": "scale",
        "Opacity": "opacity",
        "Rotation": "rotation",
        "Source Text": "source_text",
        "Fill Color": "color",
    }
    for prop, family in mapping.items():
        if props.get(prop):
            families.add(family)
    return families


def _times(code: str) -> list[float]:
    return [round(float(match.group(1)), 3) for match in TIME_PATTERN.finditer(code)]


def _estimated_layer_calls(code: str, direct_token: str) -> int:
    total = code.count(direct_token)
    function_starts = list(re.finditer(r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", code))
    for index, match in enumerate(function_starts):
        end = function_starts[index + 1].start() if index + 1 < len(function_starts) else len(code)
        body = code[match.start():end]
        if direct_token not in body:
            continue
        name = match.group(1)
        call_count = len(re.findall(rf"\b{re.escape(name)}\s*\(", code)) - 1
        total += max(call_count, 0)
    return total


def _pattern_counts(cases: list[dict[str, Any]]) -> Counter[str]:
    return Counter(pattern for case in cases for pattern in case["patterns"])


def _cases_with(cases: list[dict[str, Any]], pattern: str) -> list[str]:
    return [case["case_id"] for case in cases if pattern in case["patterns"]]


def _overlap_pairs(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs = []
    for index, first in enumerate(cases):
        for second in cases[index + 1 :]:
            a = set(first["patterns"]) - OVERLAP_IGNORE
            b = set(second["patterns"]) - OVERLAP_IGNORE
            shared = sorted(a & b)
            score = len(shared) / len(a | b) if a or b else 0.0
            if score >= 0.78 and len(shared) >= 5:
                pairs.append({
                    "a": first["case_id"],
                    "b": second["case_id"],
                    "score": round(score, 4),
                    "shared_patterns": shared,
                })
    return sorted(pairs, key=lambda item: (-item["score"], item["a"], item["b"]))[:20]


def _recommendations(gaps: list[dict[str, Any]]) -> list[str]:
    if not gaps:
        return ["train-ready subset covers all observed source animation patterns"]
    return [
        f"render/promote {gap['case_ids'][0]} for animation pattern {gap['pattern']}"
        for gap in gaps[:12]
    ]
