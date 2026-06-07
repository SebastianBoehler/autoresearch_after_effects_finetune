(function () {
    app.beginUndoGroup("AEFT Handwriting Watercolor Title");
    var comp = app.project.items.addComp("AEFT Handwriting Watercolor Title", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.98, 0.965, 0.93];

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

    addText("Small Label", "PAINT SCRIPT TITLE", [960, 210], 30, [0.18, 0.2, 0.26]);
    var title = addText("Final Scripted Word", "Bloom", [960, 560], 176, [0.1, 0.1, 0.14]);
    title.property("Transform").property("Opacity").setValueAtTime(0.0, 0);
    title.property("Transform").property("Opacity").setValueAtTime(3.4, 100);

    var brush = [[520, 580, 170, -8], [675, 530, 160, 14], [835, 565, 185, -12], [1020, 515, 155, 18], [1180, 560, 205, -8], [1370, 520, 150, 15]];
    var colors = [[0.18, 0.52, 0.95], [0.96, 0.24, 0.45], [0.98, 0.72, 0.16], [0.22, 0.72, 0.58]];
    for (var i = 0; i < brush.length; i++) {
        var seg = addRect("Animated Brush Stroke " + i, [brush[i][0], brush[i][1]], [brush[i][2], 22], colors[i % colors.length]);
        seg.property("Transform").property("Rotation").setValue(brush[i][3]);
        seg.property("Transform").property("Scale").setValueAtTime(0.35 + i * 0.28, [0, 100]);
        seg.property("Transform").property("Scale").setValueAtTime(0.95 + i * 0.28, [100, 100]);
    }

    for (var j = 0; j < 18; j++) {
        var x = 430 + (j * 81) % 1060;
        var y = 360 + ((j * 53) % 360);
        var blob = addCircle("Watercolor Bloom " + j, [x, y], 24 + (j % 5) * 7, colors[j % colors.length]);
        blob.property("Transform").property("Opacity").setValue(34);
        blob.property("Transform").property("Scale").setValueAtTime(1.0 + j * 0.06, [0, 0]);
        blob.property("Transform").property("Scale").setValueAtTime(1.6 + j * 0.06, [100, 100]);
    }
    var underline = addRect("Paper Underline", [960, 710], [760, 16], [0.08, 0.09, 0.12]);
    underline.property("Transform").property("Opacity").setValue(72);
    underline.property("Transform").property("Scale").setValueAtTime(4.0, [82, 100]);
    underline.property("Transform").property("Scale").setValueAtTime(5.7, [104, 100]);
    var caption = addText("Brush Caption", "generated strokes, blooms, and final lettering", [960, 790], 34, [0.18, 0.2, 0.26]);
    caption.property("Transform").property("Position").setValueAtTime(4.1, [960, 815]);
    caption.property("Transform").property("Position").setValueAtTime(5.8, [960, 790]);
    for (var k = 0; k < 6; k++) {
        var fleck = addCircle("Late Ink Fleck " + k, [680 + k * 112, 675 + (k % 2) * 42], 8 + (k % 3) * 4, colors[k % colors.length]);
        fleck.property("Transform").property("Opacity").expression = "28 + Math.sin(time * " + (2.5 + k * 0.2) + " + " + k + ") * 22;";
    }
    app.endUndoGroup();
})();
