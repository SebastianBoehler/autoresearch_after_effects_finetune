(function () {
    app.beginUndoGroup("AEFT Parallax Cursor Screen Demo");
    var comp = app.project.items.addComp("AEFT Parallax Cursor Screen Demo", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.018, 0.022, 0.03];
    var camera = comp.layers.addCamera("Parallax UI Camera", [960, 540]);
    camera.property("Transform").property("Position").setValueAtTime(0.2, [960, 540, -1120]);
    camera.property("Transform").property("Position").setValueAtTime(7.6, [1040, 500, -760]);

    function addRect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.threeDLayer = true;
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
        layer.threeDLayer = true;
        return layer;
    }

    for (var i = 0; i < 4; i++) {
        var z = i * 95;
        var win = addRect("Parallax App Window " + i, [620 + i * 210, 475 + i * 38, z], [520, 320], [0.055 + i * 0.012, 0.07, 0.095]);
        win.property("Transform").property("Position").setValueAtTime(0.4 + i * 0.2, [540 + i * 210, 500 + i * 38, z]);
        win.property("Transform").property("Position").setValueAtTime(6.8, [700 + i * 210, 430 + i * 30, z]);
        addRect("Window Highlight " + i, [620 + i * 210, 420 + i * 38, z + 8], [410, 32], [0.12, 0.56, 1]);
        addRect("Window Text Row " + i, [620 + i * 210, 510 + i * 38, z + 8], [340, 18], [0.75, 0.86, 0.92]);
        addRect("Window CTA Row " + i, [620 + i * 210, 575 + i * 38, z + 8], [240, 24], [0.18, 0.86, 0.58]);
    }
    var cursor = addRect("Mouse Cursor Pointer", [430, 380, 420], [50, 72], [1, 1, 1]);
    cursor.property("Transform").property("Rotation Z").setValue(-18);
    cursor.property("Transform").property("Position").setValueAtTime(1.0, [430, 380, 420]);
    cursor.property("Transform").property("Position").setValueAtTime(3.2, [910, 500, 420]);
    cursor.property("Transform").property("Position").setValueAtTime(5.4, [1210, 650, 420]);
    cursor.property("Transform").property("Position").setValueAtTime(7.5, [730, 705, 420]);
    for (var c = 0; c < 3; c++) {
        var click = addRect("Click Ring " + c, [910 + c * 150, 500 + c * 75, 410], [90, 90], [0.08, 0.65, 1]);
        click.property("Transform").property("Scale").setValueAtTime(2.0 + c * 1.25, [0, 0]);
        click.property("Transform").property("Scale").setValueAtTime(2.7 + c * 1.25, [130, 130]);
        click.property("Transform").property("Opacity").setValueAtTime(2.0 + c * 1.25, 70);
        click.property("Transform").property("Opacity").setValueAtTime(2.7 + c * 1.25, 0);
    }
    addText("Demo Header", "PARALLAX CURSOR DEMO", [960, 155, 160], 56, [0.92, 0.98, 1]);
    addText("Callout Label", "depth camera / click states / responsive panels", [960, 910, 160], 30, [0.68, 0.82, 1]);
    app.endUndoGroup();
})();
