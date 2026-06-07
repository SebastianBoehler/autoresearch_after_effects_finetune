(function () {
    app.beginUndoGroup("AEFT Fitness Challenge Vertical Reel");
    var comp = app.project.items.addComp("AEFT Fitness Challenge Vertical Reel", 1080, 1920, 1, 7, 30);
    comp.bgColor = [0.03, 0.032, 0.04];

    function rect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        shape.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function ellipse(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        shape.property("ADBE Vector Ellipse Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function text(name, value, pos, size, color) {
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

    rect("Electric Header", [540, 160], [980, 210], [0.9, 0.08, 0.28]);
    text("Header", "7 MIN CHALLENGE", [540, 188], 72, [1, 1, 1]);
    for (var i = 0; i < 22; i++) {
        var y = 430 + i * 47;
        var line = rect("Speed Line " + i, [-170, y], [300 + (i % 5) * 80, 12], [0.08, 0.88, 1]);
        line.property("Transform").property("Opacity").setValue(48);
        line.property("Transform").property("Position").setValueAtTime(0.3 + i * 0.025, [-170, y]);
        line.property("Transform").property("Position").setValueAtTime(4.8 + i * 0.025, [1260, y - 180]);
    }
    for (var j = 0; j < 18; j++) {
        var dot = ellipse("Progress Ring Dot " + j, [540 + Math.cos(j * 0.349) * 255, 805 + Math.sin(j * 0.349) * 255], [28, 28], [0.95, 0.95, 0.1]);
        dot.property("Transform").property("Scale").expression = "s = 82 + Math.sin(time * 7 + " + j + ") * 24; [s, s];";
    }
    var timer = text("Timer Numerals", "00:45", [540, 835], 152, [1, 1, 1]);
    timer.property("Transform").property("Scale").setValueAtTime(0.7, [80, 80]);
    timer.property("Transform").property("Scale").setValueAtTime(1.5, [100, 100]);
    var stats = ["420 KCAL", "18 MOVES", "HIIT MODE"];
    for (var k = 0; k < 3; k++) {
        rect("Stat Tile " + k, [260 + k * 280, 1340], [235, 126], [0.12, 0.14, 0.18]);
        text("Stat " + k, stats[k], [260 + k * 280, 1360], 34, [0.75, 1, 0.36]);
    }
    rect("CTA Pill", [540, 1650], [650, 92], [0.75, 1, 0.24]);
    text("CTA Text", "JOIN TODAY", [540, 1674], 48, [0.03, 0.04, 0.04]);
    app.endUndoGroup();
})();
