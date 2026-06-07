from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script(name):
    path = REPO_ROOT / "scripts" / f"{name}.py"
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


export_train_ready_dataset = _load_script("export_train_ready_dataset")


def test_train_ready_export_rebalances_same_split_overlaps():
    splits = {
        "train": [_record("a"), _record("b")],
        "valid": [_record("c")],
        "test": [_record("d")],
    }
    render_analysis = {
        "cases": [
            _render_case("a", 0.05, 0.25),
            _render_case("b", 0.052, 0.26),
            _render_case("c", 0.14, 0.05),
            _render_case("d", 0.01, 0.44),
        ]
    }

    balanced, report = export_train_ready_dataset._rebalance_overlap_splits(
        splits,
        render_analysis,
    )

    assert {name: len(cases) for name, cases in balanced.items()} == {"train": 2, "valid": 1, "test": 1}
    assert report["summary"]["same_split_overlap_count"] == 0
    split_by_case = export_train_ready_dataset._split_by_case(balanced)
    assert split_by_case["a"] != split_by_case["b"]


def _record(case_id):
    return {"case_id": case_id, "expected": {"width": 1920, "height": 1080}}


def _render_case(case_id, motion, foreground):
    return {
        "case_id": case_id,
        "source": {"width": 1920, "height": 1080},
        "analysis": {
            "active_frame_ratio": 0.7,
            "blank_frame_ratio": 0.0,
            "brightness": _stats(0.18),
            "center_foreground_ratio": _stats(0.35),
            "component_count": _stats(12),
            "contrast": _stats(0.24),
            "edge_density": _stats(0.08),
            "foreground_ratio": _stats(foreground),
            "largest_component_ratio": _stats(0.12),
            "motion": _stats(motion / 4),
            "motion_area_ratio": _stats(motion),
            "motion_timeline": {"motion_profile": "steady", "longest_stall_ratio": 0.1},
            "saturation": _stats(0.12),
        },
    }


def _stats(value):
    return {"mean": value, "min": value, "max": value, "p95": value}
