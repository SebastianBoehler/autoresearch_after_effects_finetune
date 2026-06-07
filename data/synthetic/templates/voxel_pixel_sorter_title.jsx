(function () {
    app.beginUndoGroup("AEFT Voxel Pixel Sorter Title");
    var comp = app.project.items.addComp("AEFT Voxel Pixel Sorter Title", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.015, 0.018, 0.024];

    function rect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var box = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        box.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function label(name, text, pos, size, color) {
        var layer = comp.layers.addText(text);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    rect("Deep Scan Plate", [960, 540], [1760, 760], [0.03, 0.04, 0.06]);
    for (var i = 0; i < 28; i++) {
        var h = 90 + (i % 7) * 38;
        var x = 160 + i * 60;
        var y = 610 - (i % 5) * 28;
        var color = i % 3 === 0 ? [0.04, 0.74, 1] : (i % 3 === 1 ? [1, 0.18, 0.44] : [0.35, 1, 0.58]);
        var voxel = rect("Sorted Voxel " + i, [x, y], [42, h], color);
        voxel.property("Transform").property("Opacity").setValue(62);
        voxel.property("Transform").property("Position").setValueAtTime(0.3 + i * 0.015, [x, y + 180]);
        voxel.property("Transform").property("Position").setValueAtTime(1.4 + i * 0.015, [x, y]);
        voxel.property("Transform").property("Scale").expression = "j = Math.sin(time * 13 + " + i + ") * 6; [100 + j, 100];";
    }
    for (var j = 0; j < 10; j++) {
        var band = rect("Pixel Sort Band " + j, [-220, 250 + j * 58], [420, 22], [0.85, 0.95, 1]);
        band.property("Transform").property("Opacity").setValue(35);
        band.property("Transform").property("Position").setValueAtTime(0.6 + j * 0.08, [-220, 250 + j * 58]);
        band.property("Transform").property("Position").setValueAtTime(4.8 + j * 0.08, [2140, 250 + j * 58]);
    }
    label("Tiny ASCII Top", "0101 // SORT DEPTH // RGB MEMORY", [960, 180], 28, [0.38, 0.85, 1]);
    var title = label("Main Title", "VOXEL SIGNAL", [960, 506], 118, [0.94, 0.97, 1]);
    title.property("Transform").property("Opacity").setValueAtTime(0.9, 0);
    title.property("Transform").property("Opacity").setValueAtTime(1.7, 100);
    title.property("Transform").property("Scale").setValueAtTime(1.7, [92, 92]);
    title.property("Transform").property("Scale").setValueAtTime(5.6, [104, 104]);
    label("Footer Code", "REALTIME TITLE GENERATOR", [960, 825], 34, [0.56, 1, 0.72]);
    app.endUndoGroup();
})();
