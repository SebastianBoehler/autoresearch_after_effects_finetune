(function () {
    app.beginUndoGroup("AEFT Shape Morph Social Transition");
    var comp = app.project.items.addComp("AEFT Shape Morph Social Transition", 1080, 1920, 1, 6, 30);
    comp.bgColor = [0.96, 0.98, 1];

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

    var blob = addCircle("Opening Circle Matte", [500, 640], 138, [0.12, 0.34, 0.95]);
    blob.property("Transform").property("Scale").setValueAtTime(0.35, [22, 22]);
    blob.property("Transform").property("Scale").setValueAtTime(1.35, [94, 94]);
    blob.property("Transform").property("Scale").setValueAtTime(4.9, [72, 72]);
    blob.property("Transform").property("Position").setValueAtTime(0.35, [220, 430]);
    blob.property("Transform").property("Position").setValueAtTime(1.8, [470, 635]);
    blob.property("Transform").property("Position").setValueAtTime(4.8, [760, 620]);
    blob.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.2) * 18, Math.cos(time * 1.4) * 14];";
    var sideBlob = addCircle("Secondary Morph Dot", [790, 420], 54, [0.08, 0.7, 0.86]);
    sideBlob.property("Transform").property("Scale").setValueAtTime(1.6, [0, 0]);
    sideBlob.property("Transform").property("Scale").setValueAtTime(2.4, [120, 120]);
    sideBlob.property("Transform").property("Position").setValueAtTime(2.4, [790, 420]);
    sideBlob.property("Transform").property("Position").setValueAtTime(5.5, [255, 1180]);
    var card = addRect("Message Card", [540, 990], [540, 300], [1, 1, 1]);
    card.property("Transform").property("Scale").setValueAtTime(1.0, [0, 100]);
    card.property("Transform").property("Scale").setValueAtTime(1.75, [100, 100]);
    card.property("Transform").property("Position").setValueAtTime(3.2, [540, 990]);
    card.property("Transform").property("Position").setValueAtTime(5.8, [540, 875]);
    addText("Hook", "Shape to story", [540, 890], 66, [0.08, 0.09, 0.12]);
    addText("Copy", "Mask-style motion\\nfor social explainers", [540, 1015], 42, [0.18, 0.24, 0.32]);
    var wipe = addRect("Color Block Wipe", [540, 2110], [880, 360], [1, 0.32, 0.18]);
    wipe.property("Transform").property("Position").setValueAtTime(3.4, [540, 2110]);
    wipe.property("Transform").property("Position").setValueAtTime(4.5, [540, 1480]);
    wipe.property("Transform").property("Position").setValueAtTime(5.7, [540, 1565]);
    for (var i = 0; i < 5; i++) {
        var dot = addCircle("Reaction Dot " + i, [300 + i * 120, 1390], 32, [0.1 + i * 0.12, 0.72, 0.95 - i * 0.08]);
        dot.property("Transform").property("Scale").expression = "p = 100 + Math.sin(time * 5 + " + i + ") * 12; [p, p];";
    }
    for (var j = 0; j < 9; j++) {
        var trail = addRect("Morph Trail " + j, [170 + (j % 3) * 370, 430 + Math.floor(j / 3) * 310], [96, 8], [0.12, 0.34, 0.95]);
        trail.property("Transform").property("Opacity").expression = "24 + Math.sin(time * " + (1.8 + j * 0.12) + " + " + j + ") * 18;";
        trail.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.1 + j * 0.06) + " + " + j + ") * 38, Math.cos(time * " + (1.4 + j * 0.05) + ") * 24];";
    }
    for (var k = 0; k < 4; k++) {
        var chip = addRect("Story Step Chip " + k, [225 + k * 210, 1215], [145, 44], [0.08, 0.16 + k * 0.08, 0.26 + k * 0.08]);
        chip.property("Transform").property("Scale").setValueAtTime(2.4 + k * 0.18, [0, 100]);
        chip.property("Transform").property("Scale").setValueAtTime(3.1 + k * 0.18, [100, 100]);
    }
    for (var m = 0; m < 6; m++) {
        var gap = addRect("Negative Space Slice " + m, [165 + m * 150, 1505 + (m % 2) * 76], [86, 14], [0.96, 0.98, 1]);
        gap.property("Transform").property("Position").setValueAtTime(3.8 + m * 0.08, [165 + m * 150, 1505 + (m % 2) * 76]);
        gap.property("Transform").property("Position").setValueAtTime(5.8, [245 + m * 124, 1445 + (m % 3) * 58]);
    }
    addText("CTA", "SWIPE FOR MORE", [540, 1580], 44, [1, 1, 1]);
    app.endUndoGroup();
})();
