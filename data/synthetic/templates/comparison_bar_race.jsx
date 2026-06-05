(function () {
    app.beginUndoGroup("AEFT Comparison Bar Race");
    var comp = app.project.items.addComp("AEFT Comparison Bar Race", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.99, 0.985, 0.965];

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

    function addText(name, value, pos, size, color) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    addText("Title", "Framework-specific generation score", [190, 150], 50, [0.09, 0.1, 0.11]);
    var labels = ["Static", "Contract", "Live AE", "Review"];
    var widths = [860, 740, 620, 520];
    var colors = [[0.1, 0.45, 0.85], [0.08, 0.62, 0.42], [0.75, 0.32, 0.85], [0.95, 0.5, 0.18]];
    for (var i = 0; i < 4; i++) {
        var y = 330 + i * 145;
        addText("Label " + labels[i], labels[i], [210, y + 12], 34, [0.1, 0.12, 0.14]);
        var bar = addRect("Bar " + labels[i], [760, y], [widths[i], 54], colors[i]);
        bar.property("Transform").property("Scale").setValueAtTime(0.5 + i * 0.3, [0, 100]);
        bar.property("Transform").property("Scale").setValueAtTime(1.4 + i * 0.3, [100, 100]);
        addText("Value " + labels[i], String(Math.round(widths[i] / 10)) + "%", [1230, y + 12], 30, [0.1, 0.12, 0.14]);
    }
    addRect("Baseline Axis", [760, 905], [940, 5], [0.75, 0.78, 0.8]);
    app.endUndoGroup();
})();

