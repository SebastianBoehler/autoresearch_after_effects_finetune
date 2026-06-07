(function () {
    app.beginUndoGroup("AEFT Neon Sign Kit Intro");
    var comp = app.project.items.addComp("AEFT Neon Sign Kit Intro", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.018, 0.014, 0.028];

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

    for (var g = 0; g < 13; g++) {
        addRect("Brick Line " + g, [960, 185 + g * 58], [1550, 3], [0.12, 0.08, 0.13]).property("Transform").property("Opacity").setValue(62);
    }
    var cyan = addText("Neon Cyan Word", "NIGHT", [805, 485], 150, [0.0, 0.92, 1]);
    var pink = addText("Neon Pink Word", "SHIFT", [1110, 620], 150, [1, 0.13, 0.62]);
    cyan.property("Transform").property("Opacity").expression = "70 + Math.sin(time * 22) * 18";
    pink.property("Transform").property("Opacity").expression = "72 + Math.sin(time * 19 + 1) * 16";
    for (var i = 0; i < 6; i++) {
        var tube = addRect("Neon Tube " + i, [520 + i * 176, 750], [112, 10], i % 2 ? [1, 0.14, 0.62] : [0.0, 0.86, 1]);
        tube.property("Transform").property("Opacity").setValueAtTime(0.4 + i * 0.18, 0);
        tube.property("Transform").property("Opacity").setValueAtTime(0.9 + i * 0.18, 100);
    }
    var sweep = addRect("Electric Sweep", [-140, 545], [80, 650], [0.9, 0.98, 1]);
    sweep.property("Transform").property("Opacity").setValue(46);
    sweep.property("Transform").property("Position").setValueAtTime(1.0, [-140, 545]);
    sweep.property("Transform").property("Position").setValueAtTime(4.8, [2060, 545]);
    addText("Neon Footer", "modular sign kit / light flicker controls", [960, 875], 32, [0.76, 0.84, 0.96]);
    app.endUndoGroup();
})();
