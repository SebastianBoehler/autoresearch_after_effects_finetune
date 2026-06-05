from after_effects_pipeline.static_check import analyze_static_jsx


def test_static_check_accepts_minimal_ae_script():
    code = """
(function () {
  app.beginUndoGroup("Demo");
  var comp = app.project.items.addComp("Demo Comp", 1920, 1080, 1, 5, 30);
  var layer = comp.layers.addText("Hello");
  layer.property("Transform").property("Opacity").setValueAtTime(0, 0);
  app.endUndoGroup();
})();
"""
    result = analyze_static_jsx(code, {"comp_name": "Demo Comp"})
    assert result.syntax_ok
    assert result.ae_contract_ok
    assert result.signals["creates_comp"]


def test_static_check_rejects_forbidden_api():
    result = analyze_static_jsx(
        'app.beginUndoGroup("x"); fetch("https://example.com"); app.endUndoGroup();',
        {},
    )
    assert not result.syntax_ok
    assert any("forbidden API" in issue for issue in result.issues)

