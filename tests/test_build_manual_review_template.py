from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script(name):
    path = REPO_ROOT / "scripts" / f"{name}.py"
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


builder = _load_script("build_manual_review_template")


def test_manual_review_template_includes_only_rendered_review_cases():
    template = builder._build_template(
        {
            "items": [
                _item("fix", "fix_render", render=True),
                _item("manual", "manual_review_render", render=True),
                _item("watch", "watch_quality", render=True),
                _item("missing", "render_missing", render=False),
                _item("stale", "rerender_stale", render=True),
                _item("promoted", "promote_rendered", render=True),
            ]
        }
    )

    assert template["summary"]["case_count"] == 3
    assert [item["case_id"] for item in template["cases"]] == ["fix", "manual", "watch"]
    assert {item["decision"] for item in template["cases"]} == {"pending"}
    assert template["cases"][0]["suggested_decision"] == "fix"
    assert template["cases"][1]["suggested_decision"] == "promote_if_visual_intentional_else_fix"
    assert template["cases"][2]["suggested_decision"] == "watch"


def test_manual_review_template_markdown_links_contact_sheet():
    template = builder._build_template({"items": [_item("case", "manual_review_render", render=True)]})

    markdown = builder._markdown(template)

    assert "# Manual Review Decisions Template" in markdown
    assert "allowed decisions: promote, fix, watch" in markdown
    assert "[open](contact_sheets/case.png)" in markdown


def _item(case_id, decision, *, render):
    return {
        "case_id": case_id,
        "decision": decision,
        "quality_score": 0.7,
        "warnings": ["dense_foreground"] if decision == "manual_review_render" else [],
        "reasons": [f"reason:{case_id}"],
        "render_path": f"/tmp/{case_id}/render.mp4" if render else None,
        "contact_sheet_path": f"/tmp/contact_sheets/{case_id}.png" if render else None,
    }
