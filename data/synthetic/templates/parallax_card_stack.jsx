(function () {
    app.beginUndoGroup("AEFT Parallax Card Stack");
    var comp = app.project.items.addComp("AEFT Parallax Card Stack", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.055, 0.07, 0.09];

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

    var back = addCard("Back Card", [780, 570], [650, 390], [0.14, 0.28, 0.52], 0.1);
    back.property("Transform").property("Position").expression = "value + [Math.sin(time * 0.9) * 26, Math.cos(time * 0.7) * 14];";
    var middle = addCard("Middle Card", [910, 520], [650, 390], [0.1, 0.42, 0.32], 0.25);
    middle.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.0 + 1) * 18, Math.cos(time * 0.8 + 1) * 12];";
    var front = addCard("Front Card", [1040, 470], [650, 390], [1, 1, 1], 0.4);
    front.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.1 + 2) * 10, Math.cos(time * 0.9 + 2) * 8];";
    for (var i = 0; i < 10; i++) {
        var marker = addCard("Parallax Marker " + i, [250 + i * 150, 850 - (i % 3) * 38], [78, 14], [0.08, 0.58, 0.88], 0.2 + i * 0.05);
        marker.property("Transform").property("Position").expression =
            "value + [Math.sin(time * " + (1.2 + i * 0.08) + ") * 20, Math.cos(time * " + (0.7 + i * 0.04) + ") * 10];";
    }
    var sweep = addCard("Depth Sweep", [220, 540], [90, 720], [1, 0.78, 0.16], 1.5);
    sweep.property("Transform").property("Rotation").setValue(-18);
    sweep.property("Transform").property("Opacity").setValue(48);
    sweep.property("Transform").property("Position").setValueAtTime(1.5, [220, 540]);
    sweep.property("Transform").property("Position").setValueAtTime(5.8, [1720, 540]);
    addText("Title", "Verified JSX Samples", [820, 380], 58, [0.07, 0.1, 0.15], 0.75);
    addText("Line 1", "Static checks", [820, 470], 34, [0.12, 0.18, 0.24], 0.95);
    addText("Line 2", "Live AE harness", [820, 530], 34, [0.12, 0.18, 0.24], 1.15);
    addText("Line 3", "HF-ready rows", [820, 590], 34, [0.12, 0.18, 0.24], 1.35);
    app.endUndoGroup();
})();
