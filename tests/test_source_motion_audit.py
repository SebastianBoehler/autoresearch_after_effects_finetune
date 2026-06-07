from after_effects_pipeline.source_motion_audit import (
    audit_source_motion,
    render_source_motion_markdown,
)


def test_source_motion_audit_flags_intro_weighted_scripts():
    payload = audit_source_motion(
        [
            {
                "case_id": "intro_only",
                "completion": """
app.project.items.addComp("Demo", 1920, 1080, 1, 6, 30);
var layer = comp.layers.addText("Demo");
layer.property("Transform").property("Opacity").setValueAtTime(0.2, 0);
layer.property("Transform").property("Opacity").setValueAtTime(1.0, 100);
""",
                "expected": {"duration_seconds": 6},
            }
        ]
    )

    case = payload["cases"][0]

    assert case["profile"] == "intro_weighted"
    assert case["latest_keyframe_time"] == 1.0
    assert "no_late_motion_signal" in case["issues"]


def test_source_motion_audit_treats_expressions_as_full_span_motion():
    payload = audit_source_motion(
        [
            {
                "case_id": "expression_rich",
                "completion": """
app.project.items.addComp("Demo", 1920, 1080, 1, 8, 30);
var a = comp.layers.addShape(); a.property("Transform").property("Position").expression = "value + [Math.sin(time), 0]";
var b = comp.layers.addShape(); b.property("Transform").property("Position").expression = "value + [Math.sin(time), 0]";
var c = comp.layers.addShape(); c.property("Transform").property("Position").expression = "value + [Math.sin(time), 0]";
var d = comp.layers.addShape(); d.property("Transform").property("Position").expression = "value + [Math.sin(time), 0]";
var e = comp.layers.addShape();
var f = comp.layers.addShape();
var g = comp.layers.addShape();
var h = comp.layers.addShape();
""",
                "expected": {"duration_seconds": 8},
            }
        ]
    )

    case = payload["cases"][0]

    assert case["profile"] == "expression_rich"
    assert case["issues"] == []


def test_source_motion_markdown_lists_review_cases():
    payload = audit_source_motion(
        [
            {
                "case_id": "needs_review",
                "completion": 'comp.layers.addText("Demo");',
                "expected": {"duration_seconds": 4},
            }
        ]
    )

    report = render_source_motion_markdown(payload)

    assert "# Source Motion Audit" in report
    assert "needs_review" in report
    assert "low_motion_signal_count" in report
