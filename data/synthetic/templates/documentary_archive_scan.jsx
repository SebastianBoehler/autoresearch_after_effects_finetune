(function () {
    app.beginUndoGroup("AEFT Documentary Archive Scan");
    var comp = app.project.items.addComp("AEFT Documentary Archive Scan", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.1, 0.095, 0.08];

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
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    for (var i = 0; i < 14; i++) {
        rect("Film Perf Top " + i, [110 + i * 132, 80], [58, 34], [0.02, 0.018, 0.014]);
        rect("Film Perf Bottom " + i, [110 + i * 132, 1000], [58, 34], [0.02, 0.018, 0.014]);
    }
    for (var j = 0; j < 4; j++) {
        var x = 420 + j * 285;
        var photo = rect("Archive Photo " + j, [x, 540 + (j % 2) * 70], [360, 430], [0.78, 0.74, 0.64]);
        photo.property("Transform").property("Rotation").setValue(-5 + j * 4);
        photo.property("Transform").property("Position").setValueAtTime(0.6 + j * 0.25, [x, 740]);
        photo.property("Transform").property("Position").setValueAtTime(1.5 + j * 0.25, [x, 540 + (j % 2) * 70]);
        rect("Archive Image Block " + j, [x, 500 + (j % 2) * 70], [300, 230], [0.24, 0.25, 0.23]);
    }
    for (var k = 0; k < 6; k++) {
        rect("Redaction Strip " + k, [470 + k * 210, 710 + (k % 2) * 70], [170, 24], [0.02, 0.02, 0.018]);
    }
    var midBand = rect("Mid Archive Scan Band", [360, 620], [1120, 9], [0.72, 0.9, 1]);
    midBand.property("Transform").property("Opacity").setValueAtTime(2.7, 0);
    midBand.property("Transform").property("Opacity").setValueAtTime(3.1, 68);
    midBand.property("Transform").property("Opacity").setValueAtTime(4.0, 0);
    midBand.property("Transform").property("Position").setValueAtTime(2.7, [360, 620]);
    midBand.property("Transform").property("Position").setValueAtTime(4.0, [1380, 760]);
    var glass = ellipse("Magnifier Glass", [360, 430], [220, 220], [0.72, 0.9, 1]);
    glass.property("Transform").property("Opacity").setValue(28);
    glass.property("Transform").property("Position").setValueAtTime(1.2, [360, 430]);
    glass.property("Transform").property("Position").setValueAtTime(6.4, [1420, 690]);
    rect("Magnifier Handle", [448, 524], [160, 18], [0.72, 0.9, 1]);
    text("Date Stamp", "FILE 1974-09 / DECLASSIFIED", [150, 204], 34, [0.91, 0.78, 0.52]);
    text("Title", "ARCHIVE SCAN", [150, 895], 70, [0.95, 0.9, 0.78]);
    app.endUndoGroup();
})();
