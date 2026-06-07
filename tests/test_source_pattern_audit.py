from after_effects_pipeline.source_pattern_audit import (
    build_source_pattern_audit,
    render_source_pattern_markdown,
)


def test_source_pattern_audit_finds_train_ready_pattern_gaps():
    payload = build_source_pattern_audit(
        [
            {
                "case_id": "ready_text",
                "completion": """
var comp = app.project.items.addComp("Demo", 1920, 1080, 1, 6, 30);
for (var i = 0; i < 4; i++) {
  var t = comp.layers.addText("Line");
  t.property("Transform").property("Position").setValueAtTime(0, [0, 0]);
  t.property("Transform").property("Position").setValueAtTime(4.5, [100, 100]);
}
""",
                "expected": {"duration_seconds": 6},
            },
            {
                "case_id": "missing_3d",
                "completion": """
var comp = app.project.items.addComp("Demo 3D", 1920, 1080, 1, 8, 30);
var camera = comp.layers.addCamera("Camera", [960, 540]);
var a = comp.layers.addShape(); a.threeDLayer = true;
var b = comp.layers.addShape(); b.threeDLayer = true;
a.property("Transform").property("Position").expression = "value + [Math.sin(time), 0]";
b.property("Transform").property("Position").expression = "value + [Math.cos(time), 0]";
camera.property("Transform").property("Position").expression = "value + [0, 0, Math.sin(time)]";
""",
                "expected": {"duration_seconds": 8},
            },
        ],
        render_queue={"items": [{"case_id": "ready_text", "train_ready": True}]},
    )

    gaps = {gap["pattern"] for gap in payload["train_ready_pattern_gaps"]}

    assert "layer_mix:camera_3d" in gaps
    assert "temporal:continuous_expression" in gaps
    assert payload["summary"]["train_ready_count"] == 1


def test_source_pattern_audit_detects_features_and_overlap():
    records = [
        _hybrid_case("one"),
        _hybrid_case("two"),
    ]

    payload = build_source_pattern_audit(records)
    case = payload["cases"][0]

    assert "feature:eased_keyframes" in case["patterns"]
    assert "feature:markers" in case["patterns"]
    assert "feature:trim_paths" in case["patterns"]
    assert payload["pattern_overlap_pairs"][0]["a"] == "one"


def test_source_pattern_markdown_lists_gaps():
    payload = build_source_pattern_audit(
        [_hybrid_case("not_ready")],
        render_queue={"items": []},
    )

    markdown = render_source_pattern_markdown(payload)

    assert "# Source Animation Pattern Audit" in markdown
    assert "not_ready" in markdown
    assert "train-ready pattern gaps" in markdown


def _hybrid_case(case_id):
    return {
        "case_id": case_id,
        "completion": """
var comp = app.project.items.addComp("Demo", 1920, 1080, 1, 6, 30);
var ease = new KeyframeEase(0, 80);
var marker = new MarkerValue("beat");
var a = comp.layers.addText("Title");
a.property("Marker").setValueAtTime(1, marker);
a.sourceRectAtTime(0, false);
var g = a.property("Contents").addProperty("ADBE Vector Group");
g.property("Contents").addProperty("ADBE Vector Filter - Trim");
a.property("Transform").property("Position").setValueAtTime(0, [0, 0]);
a.property("Transform").property("Position").setValueAtTime(4.5, [100, 100]);
a.property("Transform").property("Position").setTemporalEaseAtKey(1, [ease], [ease]);
a.property("Transform").property("Scale").expression = "value + [Math.sin(time), 0]";
""",
        "expected": {"duration_seconds": 6},
    }
