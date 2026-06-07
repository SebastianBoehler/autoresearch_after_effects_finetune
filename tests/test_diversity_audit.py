from after_effects_pipeline.diversity_audit import (
    build_diversity_audit,
    render_diversity_markdown,
)


def test_diversity_audit_reports_train_ready_animation_gaps():
    records = [
        _record("glitch_a", ["glitch", "title-sequence"], "CRT glitch title"),
        _record("hud_a", ["hud", "interface"], "Command palette HUD"),
        _record("promo_a", ["product", "promo"], "Product preorder promo"),
    ]
    queue = {
        "items": [
            {"case_id": "hud_a", "train_ready": True, "decision": "promote_rendered"},
            {"case_id": "glitch_a", "train_ready": False, "decision": "render_missing"},
            {"case_id": "promo_a", "train_ready": False, "decision": "rerender_stale"},
        ]
    }

    payload = build_diversity_audit(records, render_queue=queue)

    gaps = {item["bucket"] for item in payload["train_ready_animation_gaps"]}
    assert "glitch_datamosh" in gaps
    assert "product_promo" in gaps
    assert "hud_interface" not in gaps
    assert payload["render_debt_by_animation"]["glitch_datamosh"]["render_missing"] == ["glitch_a"]
    assert payload["render_debt_by_animation"]["product_promo"]["rerender_stale"] == ["promo_a"]


def test_diversity_audit_finds_prompt_overlap_pairs():
    records = [
        _record("route_a", ["map", "route-reveal"], "Map route reveal with target rings"),
        _record("route_b", ["map", "route-reveal"], "Map route reveal with data rings"),
        _record("paint_a", ["brush", "grunge"], "Brush title with paint chips"),
    ]

    payload = build_diversity_audit(records)

    pair_ids = {(item["a"], item["b"]) for item in payload["overlap_pairs"]}
    assert ("route_a", "route_b") in pair_ids
    assert ("route_a", "paint_a") not in pair_ids


def test_render_diversity_markdown_lists_recommendations():
    records = [_record("logo_a", ["logo-sting", "branding"], "Logo reveal")]
    payload = build_diversity_audit(records)

    markdown = render_diversity_markdown(payload)

    assert "# Dataset Diversity Audit" in markdown
    assert "Train-Ready Animation Gaps" in markdown
    assert "render/promote animation bucket" in markdown


def _record(case_id, tags, prompt):
    return {
        "case_id": case_id,
        "prompt": f"Create a 6-second {prompt}",
        "tags": tags,
        "completion": prompt,
        "expected": {"width": 1920, "height": 1080},
    }
