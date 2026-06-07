(function () {
    app.beginUndoGroup("AEFT Glitch Logo Sting");
    var comp = app.project.items.addComp("AEFT Glitch Logo Sting", 1920, 1080, 1, 5, 30);
    comp.bgColor = [0.01, 0.012, 0.018];

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
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    for (var i = 0; i < 12; i++) {
        var scan = addRect("Signal Slice " + i, [960, 210 + i * 58], [1680, 3], [0.03, 0.18, 0.22]);
        scan.property("Transform").property("Opacity").expression = "18 + Math.sin(time * 8 + " + i + ") * 14;";
    }
    var cyanPanel = addRect("Cyan Shock Panel", [250, 540], [240, 760], [0.0, 0.62, 1]);
    cyanPanel.property("Transform").property("Opacity").setValue(28);
    cyanPanel.property("Transform").property("Position").expression = "value + [Math.sin(time * 18) * 28, 0];";
    var redPanel = addRect("Red Shock Panel", [1670, 540], [240, 760], [1, 0.08, 0.2]);
    redPanel.property("Transform").property("Opacity").setValue(28);
    redPanel.property("Transform").property("Position").expression = "value + [Math.sin(time * 16 + 1.2) * -28, 0];";
    var cyan = addRect("Logo Cyan Offset", [930, 520], [300, 300], [0.0, 0.95, 1]);
    var red = addRect("Logo Red Offset", [990, 520], [300, 300], [1, 0.08, 0.18]);
    var core = addRect("Logo Core", [960, 520], [250, 250], [0.94, 0.96, 1]);
    cyan.property("Transform").property("Opacity").setValue(55);
    red.property("Transform").property("Opacity").setValue(55);
    core.property("Transform").property("Rotation").setValueAtTime(0.2, -18);
    core.property("Transform").property("Rotation").setValueAtTime(1.4, 0);
    core.property("Transform").property("Scale").setValueAtTime(0.2, [35, 35]);
    core.property("Transform").property("Scale").setValueAtTime(1.1, [118, 118]);
    core.property("Transform").property("Scale").setValueAtTime(1.5, [100, 100]);
    for (var j = 0; j < 6; j++) {
        var bar = addRect("Glitch Bar " + j, [960, 440 + j * 32], [520 - j * 38, 16], [0.95, 0.98, 1]);
        bar.property("Transform").property("Position").expression = "value + [Math.sin(time * 30 + " + j + ") * 34, 0];";
        bar.property("Transform").property("Opacity").setValueAtTime(0.35 + j * 0.05, 0);
        bar.property("Transform").property("Opacity").setValueAtTime(0.48 + j * 0.05, 100);
        bar.property("Transform").property("Opacity").setValueAtTime(1.1 + j * 0.04, 0);
    }
    addText("Logo Name", "SIGNALFORGE", [960, 765], 62, [0.92, 0.96, 1]);
    addText("Logo Tagline", "procedural motion systems", [960, 835], 28, [0.2, 0.9, 1]);
    app.endUndoGroup();
})();
