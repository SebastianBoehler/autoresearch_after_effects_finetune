(function () {
    app.beginUndoGroup("AEFT Animated Grunge Brush Title");
    var comp = app.project.items.addComp("AEFT Animated Grunge Brush Title", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.08, 0.075, 0.065];

    function shape(name, pos, kind, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var item = group.property("Contents").addProperty(kind);
        if (kind === "ADBE Vector Shape - Rect") {
            item.property("ADBE Vector Rect Size").setValue(size);
        } else {
            item.property("ADBE Vector Ellipse Size").setValue(size);
        }
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function rect(name, pos, size, color) {
        return shape(name, pos, "ADBE Vector Shape - Rect", size, color);
    }

    function ellipse(name, pos, size, color) {
        return shape(name, pos, "ADBE Vector Shape - Ellipse", size, color);
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

    for (var i = 0; i < 16; i++) {
        var y = 350 + (i % 6) * 58;
        var x = 210 + i * 110;
        var brush = rect("Rough Brush Swipe " + i, [x, y], [250 + (i % 4) * 70, 34 + (i % 3) * 16], [0.92, 0.18, 0.08]);
        brush.property("Transform").property("Rotation").setValue(-7 + (i % 5) * 4);
        brush.property("Transform").property("Scale").setValueAtTime(0.25 + i * 0.035, [0, 100]);
        brush.property("Transform").property("Scale").setValueAtTime(1.2 + i * 0.035, [100, 100]);
    }
    for (var j = 0; j < 28; j++) {
        var dot = ellipse("Ink Splatter " + j, [240 + (j * 57) % 1460, 250 + (j * 91) % 510], [18 + (j % 5) * 9, 18 + (j % 5) * 9], [0.94, 0.86, 0.72]);
        dot.property("Transform").property("Opacity").setValueAtTime(0.6 + j * 0.018, 0);
        dot.property("Transform").property("Opacity").setValueAtTime(1.4 + j * 0.018, 78);
        dot.property("Transform").property("Scale").setValueAtTime(0.6 + j * 0.018, [35, 35]);
        dot.property("Transform").property("Scale").setValueAtTime(1.8 + j * 0.018, [100, 100]);
    }
    for (var c = 0; c < 18; c++) {
        var chip = rect("Torn Paint Chip " + c, [260 + (c * 83) % 1410, 205 + (c * 127) % 640], [36 + (c % 4) * 16, 10 + (c % 3) * 7], [0.05, 0.045, 0.04]);
        chip.property("Transform").property("Rotation").setValue(-24 + (c % 7) * 9);
        chip.property("Transform").property("Opacity").setValueAtTime(0.45 + c * 0.025, 0);
        chip.property("Transform").property("Opacity").setValueAtTime(1.25 + c * 0.025, 72);
        chip.property("Transform").property("Position").expression = "value + [Math.sin(time * 5 + " + c + ") * 9, Math.cos(time * 4 + " + c + ") * 5];";
    }
    var title = text("Distressed Main Title", "RAW CUT", [960, 505], 150, [0.98, 0.92, 0.78]);
    title.property("Transform").property("Opacity").setValueAtTime(0.95, 0);
    title.property("Transform").property("Opacity").setValueAtTime(1.55, 100);
    title.property("Transform").property("Position").setValueAtTime(1.55, [960, 535]);
    title.property("Transform").property("Position").setValueAtTime(5.6, [960, 500]);
    var titleShadow = text("Distressed Offset Shadow", "RAW CUT", [972, 520], 150, [0.08, 0.07, 0.06]);
    titleShadow.property("Transform").property("Opacity").expression = "42 + Math.sin(time * 10) * 16;";
    titleShadow.property("Transform").property("Position").expression = "value + [Math.sin(time * 14) * 7, Math.cos(time * 11) * 4];";
    var wipe = rect("Fast Reveal Wipe", [-260, 710], [430, 28], [0.98, 0.92, 0.78]);
    wipe.property("Transform").property("Position").setValueAtTime(1.2, [-260, 710]);
    wipe.property("Transform").property("Position").setValueAtTime(4.9, [2160, 710]);
    text("Footer", "GRUNGE BRUSH TITLE SYSTEM", [960, 836], 30, [0.8, 0.73, 0.6]);
    app.endUndoGroup();
})();
