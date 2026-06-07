(function () {
    app.beginUndoGroup("AEFT Fluid Noise Map Loop");
    var comp = app.project.items.addComp("AEFT Fluid Noise Map Loop", 1080, 1080, 1, 6, 30);
    comp.bgColor = [0.025, 0.028, 0.038];

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

    addText("Map Title", "FLUID MAP", [540, 145], 58, [0.92, 0.98, 1]);
    addText("Map Subtitle", "looped directional flow field", [540, 205], 28, [0.42, 0.84, 1]);
    var colors = [[0.04, 0.64, 1], [0.16, 0.92, 0.62], [0.98, 0.28, 0.58], [1, 0.76, 0.18]];
    for (var i = 0; i < 18; i++) {
        var y = 315 + i * 30;
        var band = addRect("Flow Band " + i, [540, y], [760, 18], colors[i % colors.length]);
        band.property("Transform").property("Opacity").setValue(48 + (i % 4) * 8);
        band.property("Transform").property("Position").expression =
            "amp=" + (16 + i % 5 * 5) + "; [value[0] + Math.sin(time * 2 + " + i + ") * amp, value[1]];";
        band.property("Transform").property("Scale").expression =
            "s=82 + Math.sin(time * 3 + " + (i * 0.7) + ") * 18; [s, 100];";
    }
    for (var j = 0; j < 12; j++) {
        var dot = addCircle("Sharp Flow Cell " + j, [230 + (j % 4) * 210, 340 + Math.floor(j / 4) * 145], 32 + (j % 3) * 10, colors[(j + 1) % colors.length]);
        dot.property("Transform").property("Opacity").setValue(64);
        dot.property("Transform").property("Rotation").expression = "time * " + (24 + j * 3) + ";";
        dot.property("Transform").property("Scale").expression = "p = 92 + Math.sin(time * 4 + " + j + ") * 18; [p, p];";
    }
    for (var c = 0; c < 10; c++) {
        var cell = addRect("Voronoi Flow Cell " + c, [180 + (c * 113) % 760, 280 + (c * 151) % 520], [80 + (c % 3) * 38, 42 + (c % 4) * 24], colors[(c + 2) % colors.length]);
        cell.property("Transform").property("Rotation").expression = "time * " + (8 + c * 2) + " + " + (c * 19) + ";";
        cell.property("Transform").property("Opacity").expression = "22 + Math.sin(time * 3.1 + " + c + ") * 14;";
    }
    var scan = addRect("Loop Seam Scanner", [120, 890], [120, 16], [1, 1, 1]);
    scan.property("Transform").property("Opacity").setValue(66);
    scan.property("Transform").property("Position").setValueAtTime(0, [120, 890]);
    scan.property("Transform").property("Position").setValueAtTime(3, [960, 890]);
    scan.property("Transform").property("Position").setValueAtTime(6, [120, 890]);
    for (var knob = 0; knob < 4; knob++) {
        var dial = addCircle("Loop Control Dial " + knob, [300 + knob * 160, 820], 32, colors[knob], 0);
        dial.property("Transform").property("Rotation").expression = "time * " + (45 + knob * 15) + ";";
        addRect("Dial Needle " + knob, [300 + knob * 160, 820], [50, 5], [1, 1, 1]);
    }
    addText("Map Footer", "OFFSET / SCALE / TURBULENCE", [540, 950], 30, [0.8, 0.88, 0.96]);
    app.endUndoGroup();
})();
