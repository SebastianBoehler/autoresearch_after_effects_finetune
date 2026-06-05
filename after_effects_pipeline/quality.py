from __future__ import annotations

from typing import Any

from after_effects_pipeline.static_check import analyze_static_jsx
from after_effects_pipeline.types import MetricWeights


def score_case(
    case: dict[str, Any],
    code: str | None = None,
    weights: MetricWeights | None = None,
    live_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    effective_weights = weights or MetricWeights()
    source = code if code is not None else case["completion"]
    static = analyze_static_jsx(source, case.get("expected", {}))
    required = case.get("must_contain", [])
    forbidden = case.get("must_not_contain", [])
    required_ratio = (
        sum(1 for snippet in required if snippet in source) / len(required)
        if required
        else 1.0
    )
    forbidden_ok = all(snippet not in source for snippet in forbidden)

    live_ok = None
    render_ok = None
    if live_result is not None:
        live_ok = bool(live_result.get("ok"))
        render_ok = live_result.get("render_ok")

    weighted_parts = {
        "static_syntax": float(static.syntax_ok),
        "ae_contract": float(static.ae_contract_ok),
        "required_snippets": required_ratio,
        "forbidden_snippets": float(forbidden_ok),
    }
    active_weights = {
        "static_syntax": effective_weights.static_syntax,
        "ae_contract": effective_weights.ae_contract,
        "required_snippets": effective_weights.required_snippets,
        "forbidden_snippets": effective_weights.forbidden_snippets,
    }
    if live_ok is not None:
        weighted_parts["live_execution"] = float(live_ok)
        active_weights["live_execution"] = effective_weights.live_execution
    if render_ok is not None:
        weighted_parts["render"] = float(bool(render_ok))
        active_weights["render"] = effective_weights.render

    total_weight = sum(active_weights.values()) or 1.0
    quality_score = sum(
        weighted_parts[key] * active_weights[key] for key in active_weights
    ) / total_weight

    return {
        "case_id": case["case_id"],
        "quality_score": quality_score,
        "static_syntax_ok": static.syntax_ok,
        "ae_contract_ok": static.ae_contract_ok,
        "required_snippet_ratio": required_ratio,
        "forbidden_ok": forbidden_ok,
        "live_ok": live_ok,
        "render_ok": render_ok,
        "issues": static.issues,
        "signals": static.signals,
        "live_result": live_result,
    }


def summarize_scores(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {"num_cases": 0}
    return {
        "num_cases": len(results),
        "mean_case_score": sum(item["quality_score"] for item in results)
        / len(results),
        "static_success_rate": _rate(results, "static_syntax_ok"),
        "contract_success_rate": _rate(results, "ae_contract_ok"),
        "forbidden_success_rate": _rate(results, "forbidden_ok"),
        "live_success_rate": _optional_rate(results, "live_ok"),
        "render_success_rate": _optional_rate(results, "render_ok"),
    }


def _rate(results: list[dict[str, Any]], key: str) -> float:
    return sum(bool(item.get(key)) for item in results) / len(results)


def _optional_rate(results: list[dict[str, Any]], key: str) -> float | None:
    values = [item.get(key) for item in results if item.get(key) is not None]
    return sum(bool(value) for value in values) / len(values) if values else None

