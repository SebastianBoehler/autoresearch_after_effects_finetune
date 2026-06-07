(function () {
    app.beginUndoGroup("AEFT Timeline Milestone Rise");
    var comp = app.project.items.addComp("AEFT Timeline Milestone Rise", 1920, 1080, 1, 9, 30);
    comp.bgColor = [0.98, 0.97, 0.93];

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

    addRect("Header Ink Band", [960, 145], [1660, 116], [0.12, 0.14, 0.13]);
    addText("Title", "Research pipeline milestones", [150, 160], 50, [0.95, 0.97, 0.9]);
    var focus = addRect("Moving Focus Window", [360, 560], [320, 390], [1, 0.68, 0.18]);
    focus.property("Transform").property("Opacity").setValue(30);
    focus.property("Transform").property("Position").setValueAtTime(0.7, [360, 560]);
    focus.property("Transform").property("Position").setValueAtTime(5.8, [1560, 560]);
    var progress = addRect("Progress Line", [960, 560], [1320, 10], [0.12, 0.48, 0.86]);
    progress.property("Transform").property("Scale").setValueAtTime(0.4, [0, 100]);
    progress.property("Transform").property("Scale").setValueAtTime(6.2, [100, 100]);
    var labels = ["Seed", "Verify", "Tune", "Publish"];
    var dates = ["01", "02", "03", "04"];
    for (var i = 0; i < 4; i++) {
        var x = 360 + i * 400;
        var stem = addRect("Stem " + labels[i], [x, 565], [8, 180], [0.16, 0.18, 0.2]);
        stem.property("Transform").property("Scale").setValueAtTime(0.7 + i * 0.7, [100, 0]);
        stem.property("Transform").property("Scale").setValueAtTime(1.2 + i * 0.7, [100, 100]);
        var dot = addRect("Dot " + labels[i], [x, 560], [42, 42], [0.12, 0.48, 0.86]);
        dot.property("Transform").property("Scale").expression = "p = 100 + Math.sin(time * Math.PI * 2 + " + i + ") * 8; [p, p];";
        addText("Date " + labels[i], dates[i], [x - 18, 488], 30, [0.12, 0.48, 0.86]);
        var label = addText("Label " + labels[i], labels[i], [x - 52, 720], 34, [0.11, 0.12, 0.11]);
        label.property("Transform").property("Opacity").setValueAtTime(1.1 + i * 0.7, 0);
        label.property("Transform").property("Opacity").setValueAtTime(1.7 + i * 0.7, 100);
    }
    var topFocus = addRect("Top Focus Sweep", [360, 560], [320, 520], [1, 0.58, 0.12]);
    topFocus.property("Transform").property("Opacity").setValue(46);
    topFocus.property("Transform").property("Position").setValueAtTime(0.85, [360, 560]);
    topFocus.property("Transform").property("Position").setValueAtTime(6.0, [1560, 560]);
    var spark = addRect("Timeline Spark", [360, 560], [92, 92], [0.04, 0.52, 1]);
    spark.property("Transform").property("Rotation").setValue(45);
    spark.property("Transform").property("Position").setValueAtTime(0.95, [360, 560]);
    spark.property("Transform").property("Position").setValueAtTime(6.1, [1560, 560]);
    app.endUndoGroup();
})();
