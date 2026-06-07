from after_effects_pipeline.source_capability_audit import (
    audit_source_capabilities,
    render_source_capability_markdown,
)


def test_source_capability_audit_counts_core_features():
    payload = audit_source_capabilities(
        [
            _record(
                "rich",
                """
                app.project.items.addComp("Main", 10, 10, 1, 1, 24);
                app.project.items.addComp("Nested", 10, 10, 1, 1, 24);
                comp.layers.addText("T");
                comp.layers.addShape();
                comp.layers.addNull();
                comp.layers.addCamera("Cam", [5, 5]);
                layer.threeDLayer = true;
                layer.timeRemapEnabled = true;
                layer.property("ADBE Time Remapping").setValueAtTime(0, 0);
                layer.property("Marker").setValueAtTime(0.5, new MarkerValue("hit"));
                layer.property("Opacity").expression = "time";
                new KeyframeEase(0, 72);
                group.property("Contents").addProperty("ADBE Vector Filter - Trim");
                """,
            )
        ]
    )

    assert payload["summary"]["core_gap_count"] == 0
    assert payload["capability_counts"]["camera_3d"] == 1
    assert payload["capability_counts"]["nested_comps"] == 1
    assert payload["capability_counts"]["time_remap"] == 1


def test_source_capability_audit_tracks_train_ready_gaps():
    payload = audit_source_capabilities(
        [
            _record("ready", "comp.layers.addText('T'); comp.layers.addShape(); new KeyframeEase(0, 72);"),
            _record("missing", "comp.layers.addCamera('Cam', [5, 5]); layer.timeRemapEnabled = true;"),
        ],
        train_ready_case_ids={"ready"},
    )

    assert payload["summary"]["train_ready_case_count"] == 1
    assert "camera_3d" in payload["train_ready_core_gaps"]
    assert "time_remap" in payload["train_ready_core_gaps"]
    unlocks = {item["capability"]: item["case_ids"] for item in payload["train_ready_gap_unlocks"]}
    assert unlocks["camera_3d"] == ["missing"]


def test_source_capability_audit_flags_low_variety_cases():
    payload = audit_source_capabilities([_record("thin", "comp.layers.addText('T');")])

    assert payload["cases"][0]["issues"] == ["low_capability_variety"]


def test_source_capability_markdown_lists_gaps_and_review_cases():
    payload = audit_source_capabilities([_record("thin", "comp.layers.addText('T');")])

    markdown = render_source_capability_markdown(payload)

    assert "# Source Capability Audit" in markdown
    assert "- camera_3d" in markdown
    assert "## Train-Ready Core Gaps" in markdown
    assert "## Train-Ready Gap Unlocks" in markdown
    assert "| thin | text_layers | low_capability_variety |" in markdown


def _record(case_id, code):
    return {
        "case_id": case_id,
        "completion": f"(function () {{\n{code}\n}})();",
        "source_repo_path": f"data/{case_id}.jsx",
    }
