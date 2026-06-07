(function () {
    app.beginUndoGroup("AEFT Music Visualizer Neon");
    var comp = app.project.items.addComp("AEFT Music Visualizer Neon", 1080, 1080, 1, 6, 30);
    comp.bgColor = [0.01, 0.01, 0.02];

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

    var glow = addCircle("Outer Glow Disc", [540, 450], 210, [0.03, 0.18, 0.32]);
    glow.property("Transform").property("Scale").expression = "s = 96 + Math.sin(time * 2.1) * 5; [s, s];";
    var disc = addCircle("Rotating Album Disc", [540, 450], 168, [0.0, 0.82, 1]);
    disc.property("Transform").property("Opacity").setValue(44);
    disc.property("Transform").property("Rotation").expression = "time * 48;";
    var core = addCircle("Album Core", [540, 450], 72, [1, 0.1, 0.42]);
    core.property("Transform").property("Scale").expression = "s = 92 + Math.sin(time * 5.5) * 10; [s, s];";
    for (var i = 0; i < 14; i++) {
        var x = 160 + i * 58;
        var bar = addRect("Spectrum Bar " + i, [x, 860], [30, 230], [0.1 + i * 0.04, 0.82, 1 - i * 0.035]);
        bar.property("Transform").property("Scale").expression =
            "h = 45 + Math.abs(Math.sin(time * " + (2.4 + i * 0.18) + " + " + i + ")) * 90; [100, h];";
    }
    var scan = addRect("Beat Scanline", [540, 700], [920, 5], [1, 0.2, 0.62]);
    scan.property("Transform").property("Position").expression = "[540, 680 + Math.sin(time * 8) * 120];";
    addText("Track Title", "NIGHT DRIVE", [540, 185], 62, [0.95, 0.98, 1]);
    addText("Artist Name", "synthetic waveform study", [540, 248], 26, [0.2, 0.88, 1]);
    app.endUndoGroup();
})();
