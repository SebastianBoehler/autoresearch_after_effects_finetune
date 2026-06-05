(function () {
    app.beginUndoGroup("AEFT Parallax Card Stack");
    var comp = app.project.items.addComp("AEFT Parallax Card Stack", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.92, 0.95, 0.98];

    function addCard(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0], pos[1] + 120]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.8, pos);
        layer.effect.addProperty("ADBE Drop Shadow");
        return layer;
    }

    function addText(name, value, pos, size, color, delay) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.6, 100);
        return layer;
    }

    addCard("Back Card", [780, 570], [650, 390], [0.75, 0.84, 1], 0.1);
    addCard("Middle Card", [910, 520], [650, 390], [0.84, 0.96, 0.88], 0.25);
    addCard("Front Card", [1040, 470], [650, 390], [1, 1, 1], 0.4);
    addText("Title", "Verified JSX Samples", [820, 380], 58, [0.07, 0.1, 0.15], 0.75);
    addText("Line 1", "Static checks", [820, 470], 34, [0.12, 0.18, 0.24], 0.95);
    addText("Line 2", "Live AE harness", [820, 530], 34, [0.12, 0.18, 0.24], 1.15);
    addText("Line 3", "HF-ready rows", [820, 590], 34, [0.12, 0.18, 0.24], 1.35);
    app.endUndoGroup();
})();

