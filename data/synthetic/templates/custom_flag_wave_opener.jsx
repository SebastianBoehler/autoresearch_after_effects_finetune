(function () {
    app.beginUndoGroup("AEFT Custom Flag Wave Opener");
    var comp = app.project.items.addComp("AEFT Custom Flag Wave Opener", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.02, 0.045, 0.075];

    function rect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var box = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        box.property("ADBE Vector Rect Size").setValue(size);
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

    rect("Flag Pole", [405, 545], [36, 720], [0.78, 0.8, 0.76]);
    rect("Pole Cap", [405, 180], [74, 48], [0.94, 0.78, 0.34]);
    var stripeColors = [[0.93, 0.09, 0.08], [0.98, 0.98, 0.94], [0.08, 0.22, 0.62]];
    for (var row = 0; row < 9; row++) {
        for (var col = 0; col < 11; col++) {
            var seg = rect("Wave Segment " + row + "-" + col, [520 + col * 76, 260 + row * 46], [78, 46], stripeColors[row % 3]);
            seg.property("Transform").property("Position").setValueAtTime(0.4 + col * 0.025, [520 + col * 76, 360 + row * 46]);
            seg.property("Transform").property("Position").setValueAtTime(1.4 + col * 0.025, [520 + col * 76, 260 + row * 46]);
            seg.property("Transform").property("Rotation").expression = "Math.sin(time * 4 + " + (row + col) + ") * 6;";
            seg.property("Transform").property("Position").expression = "value + [0, Math.sin(time * 3 + " + col + ") * 18];";
        }
    }
    for (var i = 0; i < 8; i++) {
        var ribbon = rect("Wind Ribbon " + i, [1340 + i * 62, 230 + i * 54], [180, 6], [0.35, 0.72, 1]);
        ribbon.property("Transform").property("Opacity").setValue(46);
        ribbon.property("Transform").property("Position").setValueAtTime(1.2, [1340 + i * 62, 230 + i * 54]);
        ribbon.property("Transform").property("Position").setValueAtTime(6.4, [1600 + i * 62, 230 + i * 54]);
    }
    text("Country Placeholder", "CUSTOM FLAG", [960, 795], 92, [0.96, 0.98, 1]);
    text("Footer", "REPLACE STRIPES // KEEP WAVE CONTROLS", [960, 890], 31, [0.5, 0.8, 1]);
    app.endUndoGroup();
})();
