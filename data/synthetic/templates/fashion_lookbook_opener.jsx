(function () {
    app.beginUndoGroup("AEFT Fashion Lookbook Opener");
    var comp = app.project.items.addComp("AEFT Fashion Lookbook Opener", 1080, 1920, 1, 6, 30);
    comp.bgColor = [0.96, 0.92, 0.86];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0] - 120, pos[1]]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.35, pos);
        return layer;
    }

    function addText(name, value, pos, size, color, delay) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.2, 100);
        return layer;
    }

    addText("Masthead", "STREET EDIT", [540, 160], 76, [0.08, 0.07, 0.06], 0.2);
    var colors = [[0.08, 0.1, 0.13], [0.85, 0.12, 0.12], [0.98, 0.66, 0.12], [0.18, 0.44, 0.78]];
    for (var i = 0; i < 4; i++) {
        var panel = addRect("Look Panel " + i, [260 + (i % 2) * 560, 450 + Math.floor(i / 2) * 540], [410, 470], colors[i], 0.45 + i * 0.16);
        panel.property("Transform").property("Rotation").setValue(i % 2 === 0 ? -4 : 4);
        panel.property("Transform").property("Position").expression =
            "value + [Math.sin(time * " + (1.1 + i * 0.2) + ") * 20, Math.cos(time * " + (0.9 + i * 0.1) + ") * 14];";
        addText("Panel Label " + i, ["DROP 01", "VOLT", "RUNWAY", "NIGHT"][i], [260 + (i % 2) * 560, 640 + Math.floor(i / 2) * 540], 34, [1, 1, 1], 0.7 + i * 0.18);
    }
    for (var s = 0; s < 6; s++) {
        addRect("Color Swatch " + s, [200 + s * 135, 1510], [86, 86], colors[s % 4], 1.6 + s * 0.08);
    }
    for (var b = 0; b < 8; b++) {
        var band = addRect("Editorial Band " + b, [120 + b * 120, 1340 + (b % 2) * 70], [78, 18], colors[(b + 1) % 4], 1.15 + b * 0.06);
        band.property("Transform").property("Rotation").setValue(b % 2 === 0 ? -8 : 8);
        band.property("Transform").property("Position").expression =
            "value + [Math.sin(time * " + (1.4 + b * 0.08) + ") * 16, 0];";
    }
    var wipe = addRect("Magazine Wipe", [-120, 970], [150, 1920], [1, 1, 1], 3.3);
    wipe.property("Transform").property("Rotation").setValue(-12);
    wipe.property("Transform").property("Position").setValueAtTime(3.3, [-120, 970]);
    wipe.property("Transform").property("Position").setValueAtTime(4.2, [1220, 970]);
    addText("CTA", "LOOKBOOK / SPRING SYSTEM", [540, 1710], 38, [0.08, 0.07, 0.06], 2.2);
    app.endUndoGroup();
})();
