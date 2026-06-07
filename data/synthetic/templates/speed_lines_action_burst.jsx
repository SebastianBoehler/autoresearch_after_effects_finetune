(function () {
    app.beginUndoGroup("AEFT Speed Lines Action Burst");
    var comp = app.project.items.addComp("AEFT Speed Lines Action Burst", 1920, 1080, 1, 5, 30);
    comp.bgColor = [0.025, 0.028, 0.04];

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

    for (var i = 0; i < 28; i++) {
        var y = 90 + i * 34;
        var line = addRect("Speed Line " + i, [120 + (i % 4) * 85, y], [420 + (i % 5) * 90, 8], [0.13, 0.72, 1]);
        line.property("Transform").property("Opacity").setValue(38 + (i % 4) * 12);
        line.property("Transform").property("Position").expression =
            "x = value[0] + (time * " + (620 + i * 16) + ") % 2100; [x, value[1]];";
    }
    for (var g = 0; g < 6; g++) {
        var ghost = addRect("Trail Ghost " + g, [830 - g * 90, 540], [300, 178], [1, 0.28, 0.16]);
        ghost.property("Transform").property("Opacity").setValue(42 - g * 5);
        ghost.property("Transform").property("Position").setValueAtTime(1.2 + g * 0.04, [760 - g * 82, 540]);
        ghost.property("Transform").property("Position").setValueAtTime(3.5 + g * 0.04, [1220 + g * 70, 540]);
    }
    var core = addRect("Action Core", [960, 540], [360, 220], [1, 0.64, 0.05]);
    core.property("Transform").property("Scale").setValueAtTime(0.7, [40, 40]);
    core.property("Transform").property("Scale").setValueAtTime(1.1, [112, 112]);
    core.property("Transform").property("Scale").setValueAtTime(1.45, [100, 100]);
    addText("Impact Word", "BOOST", [960, 565], 132, [0.04, 0.04, 0.05]);
    var slash = addRect("Energy Slash", [-180, 540], [180, 1250], [0.98, 0.98, 1]);
    slash.property("Transform").property("Rotation").setValue(-22);
    slash.property("Transform").property("Position").setValueAtTime(2.6, [-180, 540]);
    slash.property("Transform").property("Position").setValueAtTime(3.4, [2100, 540]);
    app.endUndoGroup();
})();
