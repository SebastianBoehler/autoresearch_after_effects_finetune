from after_effects_pipeline.source_animation_quality import (
    audit_source_animation_quality,
    render_source_animation_quality_markdown,
)


def test_source_animation_quality_flags_dense_text_without_bounds():
    payload = audit_source_animation_quality(
        [
            {
                "case_id": "dense_text",
                "completion": """
var comp = app.project.items.addComp("Demo", 1920, 1080, 1, 6, 30);
comp.layers.addText("Line 1");
comp.layers.addText("Line 2");
comp.layers.addText("Line 3");
comp.layers.addText("Line 4");
var a = comp.layers.addShape();
a.property("Transform").property("Opacity").setValueAtTime(0, 0);
a.property("Transform").property("Opacity").setValueAtTime(1, 100);
""",
                "expected": {"duration_seconds": 6},
            }
        ]
    )

    case = payload["cases"][0]

    assert "dense_text_without_bounds" in case["issues"]
    assert "short_temporal_span" in case["issues"]


def test_source_animation_quality_recognizes_rich_motion_signals():
    payload = audit_source_animation_quality(
        [
            {
                "case_id": "rich",
                "completion": """
var comp = app.project.items.addComp("Demo", 1920, 1080, 1, 6, 30);
var ease = new KeyframeEase(0, 80);
var t = comp.layers.addText("Title");
t.sourceRectAtTime(0, false);
t.threeDLayer = true;
t.property("Effects").addProperty("ADBE Glow");
t.property("Effects").addProperty("ADBE Gaussian Blur 2");
t.property("Transform").property("Position").setValueAtTime(0, [0, 0]);
t.property("Transform").property("Position").setValueAtTime(4.5, [100, 100]);
t.property("Transform").property("Position").setTemporalEaseAtKey(1, [ease], [ease]);
t.property("Transform").property("Position").expression = "value + [Math.sin(time), 0]";
comp.layers.addCamera("Camera", [960, 540]);
""",
                "expected": {"duration_seconds": 6},
            }
        ]
    )

    case = payload["cases"][0]

    assert case["issues"] == []
    assert "full_span_motion" in case["strengths"]
    assert "effects_driven" in case["strengths"]
    assert "camera_or_3d" in case["strengths"]
    assert "text_layout_bounds" in case["strengths"]


def test_source_animation_quality_markdown_lists_review_rows():
    payload = audit_source_animation_quality(
        [
            {
                "case_id": "thin",
                "completion": 'comp.layers.addText("Only");',
                "expected": {"duration_seconds": 4},
            }
        ]
    )

    markdown = render_source_animation_quality_markdown(payload)

    assert "# Source Animation Quality Audit" in markdown
    assert "thin" in markdown
    assert "low_animation_signal_count" in markdown
