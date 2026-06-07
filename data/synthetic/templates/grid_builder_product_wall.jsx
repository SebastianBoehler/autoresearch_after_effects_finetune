(function () {
    app.beginUndoGroup("AEFT Grid Builder Product Wall");
    var comp = app.project.items.addComp("AEFT Grid Builder Product Wall", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.02, 0.021, 0.026];
    var rig = comp.layers.addNull();
    rig.name = "Grid Builder Control Null";
    rig.property("Transform").property("Position").setValue([960, 540]);

    function addRect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.parent = rig;
        return layer;
    }

    function addText(name, value, pos, size, color) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.LEFT_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    addText("Builder Header", "GRID BUILDER / PRODUCT WALL", [200, 130], 54, [0.93, 0.96, 1]);
    var colors = [[0.1, 0.48, 0.92], [0.92, 0.24, 0.44], [0.95, 0.68, 0.16], [0.12, 0.72, 0.5]];
    for (var row = 0; row < 3; row++) {
        for (var col = 0; col < 5; col++) {
            var i = row * 5 + col;
            var x = 350 + col * 300;
            var y = 300 + row * 210;
            var card = addRect("Placeholder Card " + i, [x, y], [230, 150], [0.055, 0.065, 0.085]);
            card.property("Transform").property("Scale").setValueAtTime(0.25 + i * 0.07, [58, 58]);
            card.property("Transform").property("Scale").setValueAtTime(1.15 + i * 0.07, [100, 100]);
            addRect("Media Color Bar " + i, [x, y - 42], [180, 16], colors[i % colors.length]);
            addRect("Image Placeholder " + i, [x, y + 10], [160, 68], [0.11, 0.12, 0.15]);
        }
    }
    for (var g = 0; g < 6; g++) {
        var v = addRect("Column Guide " + g, [200 + g * 300, 520], [4, 650], [0.22, 0.38, 0.58]);
        v.property("Transform").property("Opacity").setValue(28);
        var h = addRect("Row Guide " + g, [960, 200 + g * 105], [1540, 3], [0.22, 0.38, 0.58]);
        h.property("Transform").property("Opacity").setValue(20);
    }
    var select = addRect("Selected Cell Highlight", [950, 510], [260, 180], [0.18, 0.72, 1]);
    select.property("Transform").property("Opacity").setValueAtTime(2.8, 20);
    select.property("Transform").property("Opacity").setValueAtTime(6.6, 58);
    select.property("Transform").property("Position").setValueAtTime(2.8, [350, 300]);
    select.property("Transform").property("Position").setValueAtTime(6.6, [1550, 720]);
    addText("Layout Status", "15 placeholders / 5 columns / responsive spacing locked", [200, 930], 32, [0.72, 0.84, 1]);
    rig.property("Transform").property("Scale").setValueAtTime(4.2, [100, 100]);
    rig.property("Transform").property("Scale").setValueAtTime(6.9, [94, 94]);
    app.endUndoGroup();
})();
