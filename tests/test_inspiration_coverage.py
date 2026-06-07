from after_effects_pipeline.inspiration_coverage import (
    build_inspiration_coverage,
    render_inspiration_coverage_markdown,
)


def test_inspiration_coverage_tracks_train_ready_motif_gaps():
    records = [
        _record("ready_logo", ["logo-sting", "branding"]),
        _record("missing_hud", ["hud", "command-palette", "workflow-ui"]),
        _record("stale_glass", ["liquid-glass", "product", "chromatic"]),
    ]
    queue = {
        "items": [
            _item("ready_logo", "promote_rendered", train_ready=True),
            _item("missing_hud", "render_missing"),
            _item("stale_glass", "rerender_stale"),
        ]
    }
    readiness = {
        "render_debt": [
            {"case_id": "stale_glass"},
            {"case_id": "missing_hud"},
        ]
    }

    payload = build_inspiration_coverage(
        records,
        render_queue=queue,
        readiness_report=readiness,
    )

    assert payload["summary"]["source_covered_motifs"] >= 3
    assert payload["summary"]["train_ready_gap_count"] >= 2
    by_motif = {item["motif"]: item for item in payload["motifs"]}
    assert by_motif["hud_interface"]["first_unlock_case"] == "missing_hud"
    assert by_motif["liquid_glass"]["first_unlock_case"] == "stale_glass"
    assert by_motif["logo_reveal"]["train_ready_cases"] == ["ready_logo"]


def test_inspiration_coverage_markdown_lists_unlocks():
    payload = {
        "summary": {
            "motif_count": 1,
            "source_covered_motifs": 1,
            "train_ready_motifs": 0,
            "train_ready_gap_count": 1,
        },
        "motifs": [
            {
                "motif": "hud_interface",
                "source_count": 1,
                "train_ready_count": 0,
                "render_missing_count": 1,
                "rerender_stale_count": 0,
                "first_unlock_case": "missing_hud",
            }
        ],
        "train_ready_gaps": [
            {
                "motif": "hud_interface",
                "first_unlock_case": "missing_hud",
                "source_cases": ["missing_hud"],
            }
        ],
        "recommendations": ["render/promote missing_hud for hud_interface"],
    }

    markdown = render_inspiration_coverage_markdown(payload)

    assert "# Web Inspiration Coverage Audit" in markdown
    assert "| hud_interface | 1 | 0 | 1 | 0 | missing_hud |" in markdown
    assert "- hud_interface: first unlock=missing_hud; source=missing_hud" in markdown


def _record(case_id, tags):
    return {"case_id": case_id, "tags": tags}


def _item(case_id, decision, train_ready=False):
    return {"case_id": case_id, "decision": decision, "train_ready": train_ready}
