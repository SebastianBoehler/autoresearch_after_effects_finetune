import os

from after_effects_pipeline.dataset_audit import audit_dataset, render_audit_markdown


def test_audit_dataset_counts_categories_and_aspect_ratios():
    records = [
        _record("lower", 1920, 1080, ["broadcast", "lower-third"]),
        _record("story", 1080, 1920, ["vertical", "social"]),
        _record("logo", 1080, 1080, ["logo-sting", "branding"]),
    ]

    audit = audit_dataset(records)

    assert audit["case_count"] == 3
    assert audit["aspect_ratios"] == {
        "landscape_16x9": 1,
        "square_1x1": 1,
        "vertical_9x16": 1,
    }
    assert audit["category_counts"]["broadcast_package"] == 1
    assert audit["category_counts"]["logo_branding"] == 1
    assert audit["category_counts"]["social_vertical"] == 1


def test_audit_dataset_includes_render_warning_cases():
    records = [_record("transition", 1920, 1080, ["transition"])]
    render_analysis = {
        "cases": [
            {
                "case_id": "transition",
                "warnings": ["dense_foreground"],
                "notes": ["full_frame_coverage"],
            }
        ]
    }

    audit = audit_dataset(records, render_analysis)

    assert audit["render_warning_count"] == 1
    assert audit["render_warning_cases"][0]["case_id"] == "transition"
    assert audit["intentional_render_warning_cases"][0]["case_id"] == "transition"
    assert "manual-review intentional full-frame warning cases" in audit["recommendations"]


def test_audit_dataset_keeps_non_full_frame_warnings_actionable():
    records = [_record("hud", 1920, 1080, ["hud", "interface"])]
    render_analysis = {
        "cases": [
            {
                "case_id": "hud",
                "warnings": ["low_contrast"],
                "notes": ["steady_motion"],
            }
        ]
    }

    audit = audit_dataset(records, render_analysis)

    assert audit["actionable_render_warning_count"] == 1
    assert audit["actionable_render_warning_cases"][0]["case_id"] == "hud"
    assert "fix actionable render warning cases" in audit["recommendations"]


def test_audit_dataset_reports_missing_render_cases():
    records = [
        _record("rendered", 1920, 1080, ["broadcast"]),
        _record("missing", 1080, 1920, ["vertical"]),
    ]
    render_analysis = {"cases": [{"case_id": "rendered", "warnings": [], "notes": []}]}

    audit = audit_dataset(records, render_analysis)

    assert audit["missing_render_count"] == 1
    assert audit["missing_render_cases"] == ["missing"]
    assert "rerender missing render cases" in audit["recommendations"]


def test_audit_dataset_reports_stale_render_cases(tmp_path):
    template = tmp_path / "template.jsx"
    render = tmp_path / "render.mp4"
    template.write_text("new")
    render.write_text("old")
    os.utime(render, (100, 100))
    os.utime(template, (200, 200))
    record = _record("stale", 1920, 1080, ["broadcast"])
    record["source_repo_path"] = "template.jsx"
    render_analysis = {
        "cases": [{"case_id": "stale", "video_path": str(render), "warnings": []}]
    }

    audit = audit_dataset([record], render_analysis, repo_root=tmp_path)

    assert audit["stale_render_count"] == 1
    assert audit["stale_render_cases"] == ["stale"]
    assert "rerender stale render cases" in audit["recommendations"]


def test_singleton_marketplace_categories_are_undercovered():
    records = [
        _record("logo", 1920, 1080, ["logo-sting", "branding"]),
        _record("hud", 1920, 1080, ["hud", "interface"]),
        _record("music", 1080, 1080, ["music", "visualizer"]),
    ]

    audit = audit_dataset(records)

    assert "logo_branding" in audit["undercovered_categories"]
    assert "hud_interface" in audit["undercovered_categories"]
    assert "music_visualizer" in audit["undercovered_categories"]


def test_render_audit_markdown_lists_recommendations():
    payload = audit_dataset([_record("story", 1080, 1920, ["vertical", "social"])])

    markdown = render_audit_markdown(payload)

    assert "# Dataset Coverage Audit" in markdown
    assert "social_vertical" in markdown
    assert "Stale Render Cases" in markdown
    assert "add more" in markdown


def _record(case_id, width, height, tags):
    return {
        "case_id": case_id,
        "tags": tags,
        "expected": {"width": width, "height": height},
    }
