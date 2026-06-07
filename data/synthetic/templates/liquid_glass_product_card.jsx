(function () {
    app.beginUndoGroup("AEFT Liquid Glass Product Card");
    var comp = app.project.items.addComp("AEFT Liquid Glass Product Card", 1080, 1920, 1, 7, 30);
    comp.bgColor = [0.02, 0.024, 0.034];

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

    var cyan = addCircle("Cyan Refraction Blob", [250, 370], 210, [0.05, 0.78, 1]);
    cyan.property("Transform").property("Opacity").setValue(55);
    cyan.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.4) * 44, Math.cos(time * 1.2) * 28];";
    var rose = addCircle("Rose Refraction Blob", [860, 1150], 260, [1, 0.18, 0.48]);
    rose.property("Transform").property("Opacity").setValue(46);
    rose.property("Transform").property("Position").expression = "value + [Math.cos(time * 1.1) * 38, Math.sin(time * 1.6) * 52];";
    var lime = addCircle("Lime Refraction Blob", [340, 1540], 190, [0.46, 1, 0.44]);
    lime.property("Transform").property("Opacity").setValue(34);
    lime.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.8) * 32, Math.cos(time * 1.5) * 36];";

    var glass = addRect("Main Glass Card", [540, 950], [760, 980], [0.86, 0.94, 1]);
    glass.property("Transform").property("Opacity").setValue(24);
    glass.property("Transform").property("Position").setValueAtTime(0.4, [540, 1060]);
    glass.property("Transform").property("Position").setValueAtTime(1.3, [540, 950]);
    addRect("Glass Cyan Edge", [532, 950], [780, 1000], [0.0, 0.82, 1]).property("Transform").property("Opacity").setValue(18);
    addRect("Glass Rose Edge", [548, 960], [780, 1000], [1, 0.18, 0.5]).property("Transform").property("Opacity").setValue(14);
    addRect("Product Placeholder", [540, 820], [420, 520], [0.07, 0.085, 0.12]).property("Transform").property("Opacity").setValue(88);
    addRect("Specular Sweep", [220, 820], [80, 780], [1, 1, 1]).property("Transform").property("Opacity").setValue(28);

    var sweep = addRect("Moving Glass Highlight", [220, 820], [82, 780], [1, 1, 1]);
    sweep.property("Transform").property("Opacity").setValue(30);
    sweep.property("Transform").property("Position").setValueAtTime(1.0, [200, 820]);
    sweep.property("Transform").property("Position").setValueAtTime(4.8, [880, 820]);
    sweep.property("Transform").property("Rotation").setValue(12);
    for (var r = 0; r < 4; r++) {
        var ring = addCircle("Glass Ripple Ring " + r, [540, 840], 235 + r * 42, r % 2 ? [1, 0.24, 0.5] : [0.12, 0.82, 1]);
        ring.property("Transform").property("Opacity").expression = "18 + Math.sin(time * 3 - " + r + ") * 12;";
        ring.property("Transform").property("Scale").expression = "s = 88 + ((time * 18 + " + (r * 18) + ") % 42); [s, s];";
    }

    addText("Product Name", "AURA DEVICE", [540, 1210], 74, [0.94, 0.98, 1]);
    addText("Product Claim", "liquid glass social launch", [540, 1285], 34, [0.55, 0.88, 1]);
    for (var i = 0; i < 5; i++) {
        var chip = addRect("Glass Chip " + i, [260 + i * 130, 1410], [92, 48], i % 2 ? [1, 0.26, 0.52] : [0.1, 0.72, 1]);
        chip.property("Transform").property("Opacity").setValue(72);
        chip.property("Transform").property("Scale").setValueAtTime(1.8 + i * 0.12, [0, 0]);
        chip.property("Transform").property("Scale").setValueAtTime(2.5 + i * 0.12, [100, 100]);
        chip.property("Transform").property("Position").expression = "value + [0, Math.sin(time * 3 + " + i + ") * 10];";
    }
    var cta = addText("Lower CTA", "PREORDER / 06.26", [540, 1575], 42, [0.92, 0.98, 1]);
    cta.property("Transform").property("Opacity").expression = "72 + Math.sin(time * 4.5) * 22;";
    app.endUndoGroup();
})();
