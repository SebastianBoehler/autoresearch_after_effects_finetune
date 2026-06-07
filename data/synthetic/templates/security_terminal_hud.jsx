(function () {
    app.beginUndoGroup("AEFT Security Terminal HUD");
    var comp = app.project.items.addComp("AEFT Security Terminal HUD", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.015, 0.018, 0.022];

    function addRect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function addText(name, value, pos, size, color) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    addRect("Top Status Bar", [960, 88], [1640, 74], [0.06, 0.14, 0.18]);
    addRect("Amber Alert Plate", [1510, 88], [300, 74], [0.95, 0.48, 0.08]);
    addRect("Blue Auth Plate", [320, 920], [420, 120], [0.05, 0.28, 0.95]);
    addText("Header", "SECURITY TERMINAL / NODE 07", [180, 105], 34, [0.15, 0.95, 0.7]);
    for (var i = 0; i < 6; i++) {
        var y = 220 + i * 105;
        var row = addRect("Terminal Row " + i, [520, y], [720, 62], [0.06, 0.1, 0.13]);
        row.property("Transform").property("Opacity").expression = "62 + Math.sin(time * 4 + " + i + ") * 18;";
        addText("Row Label " + i, "SCAN_" + (i + 1) + "  OK", [210, y + 12], 28, [0.18, 0.9, 0.64]);
        var metric = addRect("Metric Fill " + i, [650, y], [300 - i * 28, 18], [0.1, 0.7, 1]);
        metric.property("Transform").property("Scale").setValueAtTime(0.6 + i * 0.18, [0, 100]);
        metric.property("Transform").property("Scale").setValueAtTime(1.6 + i * 0.18, [100, 100]);
    }
    addRect("Map Panel", [1350, 535], [520, 600], [0.06, 0.08, 0.1]);
    for (var j = 0; j < 5; j++) {
        var route = addRect("Route Trace " + j, [1240 + j * 55, 400 + j * 54], [320, 8], [1, 0.32, 0.12]);
        route.property("Transform").property("Rotation").setValue(-28 + j * 14);
        route.property("Transform").property("Opacity").setValueAtTime(1.0 + j * 0.22, 0);
        route.property("Transform").property("Opacity").setValueAtTime(2.2 + j * 0.22, 80);
    }
    var sweep = addRect("Terminal Scan Sweep", [960, 180], [1640, 8], [0.15, 0.95, 0.7]);
    sweep.property("Transform").property("Opacity").setValue(52);
    sweep.property("Transform").property("Position").setValueAtTime(0.6, [960, 180]);
    sweep.property("Transform").property("Position").setValueAtTime(7.2, [960, 940]);
    var redSweep = addRect("Threat Sweep", [-180, 760], [260, 220], [1, 0.12, 0.18]);
    redSweep.property("Transform").property("Opacity").setValue(42);
    redSweep.property("Transform").property("Position").setValueAtTime(1.0, [-180, 760]);
    redSweep.property("Transform").property("Position").setValueAtTime(6.8, [2100, 760]);
    addText("Footer", "ENCRYPTED CHANNEL / LIVE", [180, 990], 28, [0.5, 0.72, 0.8]);
    app.endUndoGroup();
})();
