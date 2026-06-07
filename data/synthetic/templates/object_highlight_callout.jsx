(function () {
    app.beginUndoGroup("AEFT Object Highlight Callout");
    var comp = app.project.items.addComp("AEFT Object Highlight Callout", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.925, 0.93, 0.92];

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
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    rect("Product Body", [790, 560], [430, 540], [0.1, 0.16, 0.2]);
    rect("Product Screen", [790, 505], [330, 310], [0.02, 0.055, 0.08]);
    rect("Detail Card", [1340, 350], [420, 210], [1, 1, 1]);
    text("Detail Label", "AUTO HIGHLIGHT", [1190, 314], 34, [0.08, 0.11, 0.13]);
    text("Detail Value", "EDGE SENSOR // 92%", [1190, 370], 28, [0.13, 0.42, 0.72]);
    for (var i = 0; i < 4; i++) {
        var ring = ellipse("Target Ring " + i, [735 + i * 52, 466 + i * 20], [100 + i * 24, 100 + i * 24], [0.1, 0.62, 1]);
        ring.property("Transform").property("Opacity").setValue(22);
        ring.property("Transform").property("Scale").expression = "s = 92 + Math.sin(time * 5 + " + i + ") * 8; [s, s];";
        var dot = ellipse("Number Dot " + i, [1030 + i * 92, 678 - i * 58], [42, 42], [0.1, 0.62, 1]);
        dot.property("Transform").property("Scale").setValueAtTime(0.8 + i * 0.18, [0, 0]);
        dot.property("Transform").property("Scale").setValueAtTime(1.4 + i * 0.18, [100, 100]);
        text("Number Label " + i, "0" + (i + 1), [1015 + i * 92, 688 - i * 58], 22, [1, 1, 1]);
    }
    for (var j = 0; j < 5; j++) {
        var line = rect("Connector Line " + j, [1025 + j * 82, 566 - j * 48], [190, 4], [0.12, 0.18, 0.22]);
        line.property("Transform").property("Rotation").setValue(-28);
        line.property("Transform").property("Opacity").setValueAtTime(0.9 + j * 0.12, 0);
        line.property("Transform").property("Opacity").setValueAtTime(1.7 + j * 0.12, 100);
    }
    var sweep = rect("Scanning Sweep", [620, 250], [500, 18], [0.32, 0.86, 1]);
    sweep.property("Transform").property("Opacity").setValue(65);
    sweep.property("Transform").property("Position").setValueAtTime(1.0, [620, 250]);
    sweep.property("Transform").property("Position").setValueAtTime(6.1, [620, 780]);
    text("Footer", "GENERATED CALLOUTS FROM SELECTED LAYERS", [555, 938], 30, [0.22, 0.26, 0.28]);
    app.endUndoGroup();
})();
