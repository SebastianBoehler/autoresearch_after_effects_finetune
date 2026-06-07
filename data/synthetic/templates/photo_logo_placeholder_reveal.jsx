(function () {
    app.beginUndoGroup("AEFT Photo Logo Placeholder Reveal");
    var comp = app.project.items.addComp("AEFT Photo Logo Placeholder Reveal", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.95, 0.94, 0.9];

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

    var colors = [[0.2, 0.32, 0.48], [0.78, 0.28, 0.2], [0.86, 0.62, 0.2], [0.22, 0.55, 0.48]];
    for (var row = 0; row < 3; row++) {
        for (var col = 0; col < 5; col++) {
            var x = 310 + col * 220;
            var y = 230 + row * 185;
            var tile = rect("Photo Placeholder " + row + "-" + col, [x, y], [178, 132], colors[(row + col) % colors.length]);
            tile.property("Transform").property("Opacity").setValueAtTime(0.4 + (row + col) * 0.12, 0);
            tile.property("Transform").property("Opacity").setValueAtTime(1.2 + (row + col) * 0.12, 86);
            tile.property("Transform").property("Scale").setValueAtTime(0.4 + (row + col) * 0.12, [80, 80]);
            tile.property("Transform").property("Scale").setValueAtTime(1.2 + (row + col) * 0.12, [100, 100]);
            text("Replace Label " + row + "-" + col, "PHOTO", [x, y + 8], 24, [1, 1, 1]);
        }
    }
    var flash = rect("Camera Flash", [960, 540], [1920, 1080], [1, 1, 1]);
    flash.property("Transform").property("Opacity").setValueAtTime(2.2, 0);
    flash.property("Transform").property("Opacity").setValueAtTime(2.45, 88);
    flash.property("Transform").property("Opacity").setValueAtTime(2.8, 0);
    ellipse("Aperture Outer", [960, 545], [260, 260], [0.08, 0.1, 0.12]);
    ellipse("Aperture Inner", [960, 545], [128, 128], [0.95, 0.94, 0.9]);
    for (var i = 0; i < 6; i++) {
        var blade = rect("Aperture Blade " + i, [960, 545], [190, 28], [0.08, 0.1, 0.12]);
        blade.property("Transform").property("Rotation").setValue(i * 60);
        blade.property("Transform").property("Scale").setValueAtTime(2.0, [0, 100]);
        blade.property("Transform").property("Scale").setValueAtTime(3.0, [100, 100]);
    }
    var logo = text("Logo Lockup", "FRAME MARK", [960, 760], 64, [0.08, 0.1, 0.12]);
    logo.property("Transform").property("Scale").setValueAtTime(4.2, [92, 92]);
    logo.property("Transform").property("Scale").setValueAtTime(6.4, [106, 106]);
    var footer = text("Footer", "DROP IMAGES INTO PLACEHOLDERS", [960, 842], 28, [0.36, 0.38, 0.4]);
    footer.property("Transform").property("Position").setValueAtTime(4.0, [960, 872]);
    footer.property("Transform").property("Position").setValueAtTime(6.2, [960, 842]);
    var lateSweep = rect("Late Gallery Sweep", [-180, 650], [120, 520], [1, 1, 1]);
    lateSweep.property("Transform").property("Opacity").setValue(22);
    lateSweep.property("Transform").property("Rotation").setValue(-18);
    lateSweep.property("Transform").property("Position").setValueAtTime(4.4, [-180, 650]);
    lateSweep.property("Transform").property("Position").setValueAtTime(6.7, [2100, 360]);
    app.endUndoGroup();
})();
