from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_builder_injects_easing_normalizer_before_end_undo():
    script = _load_script()
    completion = """(function () {
    app.beginUndoGroup("Demo");
    var comp = app.project.items.addComp("Demo", 10, 10, 1, 1, 24);
    layer.property("Transform").property("Opacity").setValueAtTime(0, 0);
    layer.property("Transform").property("Opacity").setValueAtTime(1, 100);
    app.endUndoGroup();
})();"""

    result = script._with_easing_normalizer(completion)

    assert "new KeyframeEase" in result
    assert "setTemporalEaseAtKey" in result
    assert result.index("aeFtEaseComp(comp, 72);") < result.index("app.endUndoGroup();")


def _load_script():
    path = REPO_ROOT / "scripts/build_synthetic_dataset.py"
    spec = spec_from_file_location("build_synthetic_dataset", path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module
