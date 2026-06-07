(function () {
    app.beginUndoGroup("AEFT Podcast Quote Audiogram");
    var comp = app.project.items.addComp("AEFT Podcast Quote Audiogram", 1080, 1080, 1, 6, 30);
    comp.bgColor = [0.04, 0.045, 0.06];

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

    function addCircle(name, pos, radius, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([radius * 2, radius * 2]);
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

    addText("Show Name", "SIGNAL NOTES", [540, 130], 48, [0.9, 0.96, 1]);
    addCircle("Avatar Glow", [540, 310], 120, [0.08, 0.42, 0.9]);
    var avatar = addCircle("Speaker Avatar", [540, 310], 82, [1, 0.72, 0.12]);
    avatar.property("Transform").property("Scale").expression = "p = 100 + Math.sin(time * Math.PI * 2) * 4; [p, p];";
    addText("Quote", "\"The best scripts\\nmake motion testable.\"", [540, 555], 58, [1, 1, 1]);
    addText("Speaker", "EP. 12  /  MOTION SYSTEMS", [540, 715], 26, [0.45, 0.8, 1]);
    for (var i = 0; i < 18; i++) {
        var x = 150 + i * 46;
        var bar = addRect("Audiogram Bar " + i, [x, 875], [24, 220], [0.08 + i * 0.035, 0.72, 1 - i * 0.025]);
        bar.property("Transform").property("Scale").expression =
            "h = 32 + Math.abs(Math.sin(time * " + (2.8 + i * 0.13) + " + " + i + ")) * 95; [100, h];";
    }
    var progress = addRect("Progress Line", [540, 1000], [760, 8], [0.16, 0.22, 0.32]);
    progress.property("Transform").property("Scale").setValueAtTime(0.2, [0, 100]);
    progress.property("Transform").property("Scale").setValueAtTime(5.8, [100, 100]);
    addText("Timecode", "00:18 / 01:00", [540, 1030], 24, [0.65, 0.76, 0.86]);
    app.endUndoGroup();
})();
