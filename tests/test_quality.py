from after_effects_pipeline.quality import score_case


def test_score_case_rewards_required_snippets():
    case = {
        "case_id": "demo",
        "prompt": "Create a comp",
        "completion": """
app.beginUndoGroup("Demo");
var comp = app.project.items.addComp("Demo Comp", 1920, 1080, 1, 5, 30);
comp.layers.addText("Hi");
app.endUndoGroup();
""",
        "must_contain": ["layers.addText"],
        "must_not_contain": ["fetch("],
        "expected": {"comp_name": "Demo Comp"},
        "license": "MIT",
    }
    result = score_case(case)
    assert result["quality_score"] > 0.9
    assert result["required_snippet_ratio"] == 1.0

