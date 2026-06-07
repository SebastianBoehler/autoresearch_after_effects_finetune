(function () {
    app.beginUndoGroup("AEFT Documentary Photo Collage");
    var comp = app.project.items.addComp("AEFT Documentary Photo Collage", 1920, 1080, 1, 9, 30);
    comp.bgColor = [0.12, 0.105, 0.085];

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

    var grain = addRect("Archive Grain Wash", [960, 540], [1920, 1080], [0.19, 0.16, 0.12]);
    grain.property("Transform").property("Opacity").expression = "18 + Math.sin(time * 18) * 6;";
    var photos = [
        ["Photo North", 500, 440, -7, 0.2],
        ["Photo East", 980, 505, 4, 0.45],
        ["Photo South", 1390, 610, 9, 0.7]
    ];
    for (var i = 0; i < photos.length; i++) {
        var frame = addRect(photos[i][0] + " Frame", [photos[i][1], photos[i][2]], [440, 300], [0.94, 0.9, 0.78]);
        frame.property("Transform").property("Rotation").setValue(photos[i][3]);
        frame.property("Transform").property("Position").setValueAtTime(photos[i][4], [photos[i][1] - 80, photos[i][2] + 40]);
        frame.property("Transform").property("Position").setValueAtTime(photos[i][4] + 1.1, [photos[i][1], photos[i][2]]);
        frame.property("Transform").property("Position").expression =
            "value + [Math.sin((time + " + i + ") * 0.9) * 18, Math.cos((time + " + i + ") * 0.7) * 12];";
        var image = addRect(photos[i][0] + " Image", [photos[i][1], photos[i][2] - 10], [390, 230], [0.18 + i * 0.12, 0.24, 0.28 + i * 0.1]);
        image.property("Transform").property("Rotation").setValue(photos[i][3]);
        image.property("Transform").property("Scale").setValueAtTime(photos[i][4], [96, 96]);
        image.property("Transform").property("Scale").setValueAtTime(7.4, [110, 110]);
        image.property("Transform").property("Position").expression =
            "value + [Math.sin((time + " + i + ") * 1.1) * 12, Math.cos((time + " + i + ") * 0.8) * 8];";
    }
    for (var t = 0; t < 5; t++) {
        var tape = addRect("Archive Tape Strip " + t, [330 + t * 310, 110 + (t % 2) * 790], [210, 18], [0.92, 0.76, 0.38]);
        tape.property("Transform").property("Rotation").setValue(t % 2 === 0 ? -5 : 7);
        tape.property("Transform").property("Opacity").expression = "35 + Math.sin(time * 2 + " + t + ") * 14;";
    }
    var line = addRect("Evidence Timeline", [960, 880], [1180, 8], [0.86, 0.68, 0.36]);
    line.property("Transform").property("Scale").setValueAtTime(1.0, [0, 100]);
    line.property("Transform").property("Scale").setValueAtTime(6.8, [100, 100]);
    for (var j = 0; j < 4; j++) {
        addRect("Timeline Tick " + j, [450 + j * 340, 880], [16, 64], [0.86, 0.68, 0.36]);
    }
    var stamp = addRect("Archive Stamp", [1500, 250], [300, 94], [0.68, 0.08, 0.06]);
    stamp.property("Transform").property("Rotation").setValue(-8);
    stamp.property("Transform").property("Opacity").setValueAtTime(2.8, 0);
    stamp.property("Transform").property("Opacity").setValueAtTime(3.2, 82);
    stamp.property("Transform").property("Scale").setValueAtTime(2.8, [130, 130]);
    stamp.property("Transform").property("Scale").setValueAtTime(3.2, [100, 100]);
    addText("Stamp Text", "VERIFIED", [1422, 265], 42, [1, 0.9, 0.72]);
    var scan = addRect("Magnifier Sweep", [260, 360], [88, 360], [0.86, 0.68, 0.36]);
    scan.property("Transform").property("Rotation").setValue(-7);
    scan.property("Transform").property("Opacity").setValue(34);
    scan.property("Transform").property("Position").setValueAtTime(2.0, [260, 360]);
    scan.property("Transform").property("Position").setValueAtTime(6.6, [1500, 620]);
    addText("Title", "Archive of a launch", [170, 180], 62, [0.96, 0.88, 0.68]);
    addText("Subtitle", "field notes / prototypes / signal traces", [174, 240], 30, [0.76, 0.66, 0.52]);
    app.endUndoGroup();
})();
