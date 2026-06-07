from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
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


render_aep_queue = _load_script("render_aep_queue")


def test_case_ids_from_status_filters_renderable_cases(tmp_path):
    path = tmp_path / "status.json"
    path.write_text(json.dumps({
        "cases": [
            {"case_id": "ready", "status": "project_ready"},
            {"case_id": "stale_render", "status": "render_stale"},
            {"case_id": "not_run", "status": "not_run"},
        ]
    }))

    case_ids = render_aep_queue._case_ids_from_status(
        path,
        {"project_ready", "render_stale"},
    )

    assert case_ids == {"ready", "stale_render"}
