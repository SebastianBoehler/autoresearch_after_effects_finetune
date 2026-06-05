(function () {
    app.beginUndoGroup("AEFT Metric Dashboard Pulse");
    var comp = app.project.items.addComp("AEFT Metric Dashboard Pulse", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.96, 0.97, 0.96];

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

    addText("Title", "Weekly Learning Metrics", [150, 150], 54, [0.08, 0.11, 0.13]);
    var labels = ["Focus", "Recall", "Pace", "Mastery"];
    var values = ["82%", "71%", "1.4x", "64%"];
    var colors = [[0.05, 0.45, 0.42], [0.16, 0.5, 0.9], [0.58, 0.32, 0.88], [0.94, 0.46, 0.24]];
    for (var i = 0; i < 4; i++) {
        var x = 300 + i * 420;
        addRect("Card " + labels[i], [x, 470], [320, 260], [1, 1, 1]);
        addText("Label " + labels[i], labels[i], [x - 105, 410], 30, [0.38, 0.43, 0.48]);
        addText("Value " + labels[i], values[i], [x - 105, 485], 62, [0.08, 0.11, 0.13]);
        var bar = addRect("Progress " + labels[i], [x - 45, 570], [210, 16], colors[i]);
        var scale = bar.property("Transform").property("Scale");
        scale.setValueAtTime(0.35 + i * 0.18, [0, 100]);
        scale.setValueAtTime(1.2 + i * 0.18, [100, 100]);
    }
    var dot = addRect("Live Status Dot", [1560, 150], [32, 32], [0.05, 0.7, 0.42]);
    dot.property("Transform").property("Scale").expression = "s = 100 + Math.sin(time * Math.PI * 2) * 18; [s, s];";
    addText("Live Label", "LIVE", [1605, 160], 28, [0.05, 0.45, 0.25]);
    app.endUndoGroup();
})();

