(function () {
    app.beginUndoGroup("AEFT Spiral Grid Logo System");
    var comp = app.project.items.addComp("AEFT Spiral Grid Logo System", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.012, 0.016, 0.026];
    var camera = comp.layers.addCamera("Spiral Layout Camera", [960, 540]);
    camera.property("Transform").property("Position").setValueAtTime(0.2, [960, 540, -1280]);
    camera.property("Transform").property("Position").setValueAtTime(6.8, [1080, 475, -760]);

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

    for (var r = 0; r < 4; r++) {
        var ring = addRect("Guide Ring Slice " + r, [960, 540, 70 + r * 30], [740 + r * 180, 5], [0.16, 0.32, 0.54]);
        ring.property("Transform").property("Rotation Z").expression = "time * " + (8 + r * 3) + ";";
        ring.property("Transform").property("Opacity").setValue(34 - r * 4);
    }
    var colors = [[0.14, 0.55, 1], [0.96, 0.36, 0.52], [0.98, 0.78, 0.22], [0.18, 0.86, 0.58]];
    for (var i = 0; i < 28; i++) {
        var angle = i * 0.62;
        var radius = 70 + i * 22;
        var x = 960 + Math.cos(angle) * radius;
        var y = 540 + Math.sin(angle) * radius * 0.62;
        var tile = addRect("Spiral Placeholder Tile " + i, [x, y, i * 12], [74, 54], colors[i % colors.length]);
        tile.property("Transform").property("Scale").setValueAtTime(0.25 + i * 0.045, [0, 0]);
        tile.property("Transform").property("Scale").setValueAtTime(1.25 + i * 0.045, [100, 100]);
        tile.property("Transform").property("Rotation Z").setValue(angle * 180 / Math.PI);
    }
    var logo = addRect("Selected Logo Tile", [960, 540, 380], [230, 160], [0.98, 0.98, 1]);
    logo.property("Transform").property("Scale").setValueAtTime(3.7, [84, 84]);
    logo.property("Transform").property("Scale").setValueAtTime(6.6, [118, 118]);
    addText("Logo Mark", "GRID", [960, 558, 410], 48, [0.04, 0.06, 0.09]);
    addText("Mode Label", "rectangular / 3D / circular / spiral", [960, 900, 120], 32, [0.72, 0.86, 1]);
    app.endUndoGroup();
})();
