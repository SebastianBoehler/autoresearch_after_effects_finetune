(function () {
    app.beginUndoGroup("AEFT CRT Datamosh Transition");
    var comp = app.project.items.addComp("AEFT CRT Datamosh Transition", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.01, 0.012, 0.016];

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

    var cyan = addText("RGB Cyan Title", "SIGNAL SHIFT", [952, 505], 116, [0.08, 0.95, 1]);
    var red = addText("RGB Red Title", "SIGNAL SHIFT", [968, 520], 116, [1, 0.08, 0.14]);
    var main = addText("White Title", "SIGNAL SHIFT", [960, 512], 116, [0.94, 0.98, 1]);
    cyan.property("Transform").property("Opacity").setValue(65);
    red.property("Transform").property("Opacity").setValue(58);
    main.property("Transform").property("Position").setValueAtTime(0.8, [960, 512]);
    main.property("Transform").property("Position").setValueAtTime(3.0, [880, 512]);
    main.property("Transform").property("Position").setValueAtTime(3.22, [1000, 512]);
    main.property("Transform").property("Position").setValueAtTime(4.7, [960, 512]);

    var flicker = addRect("CRT Flicker Plate", [960, 540], [1920, 1080], [0.04, 0.08, 0.12]);
    flicker.property("Transform").property("Opacity").expression = "22 + wiggle(18, 18)";

    for (var i = 0; i < 34; i++) {
        var line = addRect("Scanline " + i, [960, 40 + i * 32], [1920, 2], [0.5, 0.9, 1]);
        line.property("Transform").property("Opacity").setValue(18);
    }
    var colors = [[0.0, 0.9, 1], [1, 0.05, 0.18], [0.6, 1, 0.16], [1, 1, 1]];
    for (var j = 0; j < 18; j++) {
        var block = addRect("Datamosh Block " + j, [320 + (j * 137) % 1320, 260 + (j * 71) % 520], [120 + (j % 4) * 48, 36 + (j % 3) * 22], colors[j % colors.length]);
        block.property("Transform").property("Opacity").setValueAtTime(1.6 + j * 0.03, 0);
        block.property("Transform").property("Opacity").setValueAtTime(1.85 + j * 0.03, 68);
        block.property("Transform").property("Opacity").setValueAtTime(3.8 + j * 0.02, 0);
        block.property("Transform").property("Position").setValueAtTime(1.8, block.property("Transform").property("Position").value);
        block.property("Transform").property("Position").setValueAtTime(3.0, [900 + (j % 5) * 36, 540 + (j % 4) * 24]);
    }
    var wipe = addRect("Analog Wipe", [-120, 540], [180, 1080], [0.9, 0.97, 1]);
    wipe.property("Transform").property("Opacity").setValue(55);
    wipe.property("Transform").property("Position").setValueAtTime(0.9, [-120, 540]);
    wipe.property("Transform").property("Position").setValueAtTime(4.9, [2040, 540]);
    addText("Lower Status", "FRAME REBUILD / RGB OFFSET / MOSH BANDS", [960, 840], 34, [0.46, 0.9, 1]);
    app.endUndoGroup();
})();
