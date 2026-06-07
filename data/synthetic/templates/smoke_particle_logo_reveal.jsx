(function () {
    app.beginUndoGroup("AEFT Smoke Particle Logo Reveal");
    var comp = app.project.items.addComp("AEFT Smoke Particle Logo Reveal", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.012, 0.012, 0.016];

    function addCircle(name, pos, radius, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([radius * 2, radius * 2]);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

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
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    var colors = [[0.42, 0.48, 0.56], [0.75, 0.82, 0.92], [0.12, 0.58, 1], [1, 0.34, 0.22]];
    for (var i = 0; i < 46; i++) {
        var angle = i * 0.73;
        var radius = 45 + (i % 9) * 20;
        var p = addCircle("Smoke Particle " + i, [960, 540], 10 + (i % 5) * 6, colors[i % colors.length]);
        p.property("Transform").property("Opacity").setValueAtTime(0.2 + i * 0.015, 0);
        p.property("Transform").property("Opacity").setValueAtTime(1.2 + i * 0.015, 62);
        p.property("Transform").property("Opacity").setValueAtTime(4.8, 0);
        p.property("Transform").property("Position").setValueAtTime(0.5, [960, 540]);
        p.property("Transform").property("Position").setValueAtTime(3.6, [960 + Math.cos(angle) * radius * 2.2, 540 + Math.sin(angle) * radius]);
        p.property("Transform").property("Scale").setValueAtTime(0.5, [40, 40]);
        p.property("Transform").property("Scale").setValueAtTime(3.6, [145, 145]);
    }
    var mark = addRect("Logo Reveal Mark", [960, 540], [220, 220], [0.94, 0.98, 1]);
    mark.property("Transform").property("Rotation").setValueAtTime(1.7, -35);
    mark.property("Transform").property("Rotation").setValueAtTime(2.8, 0);
    mark.property("Transform").property("Scale").setValueAtTime(1.7, [35, 35]);
    mark.property("Transform").property("Scale").setValueAtTime(2.8, [100, 100]);
    addText("Logo Name", "EMBER", [960, 745], 70, [0.94, 0.98, 1]);
    addText("Logo Caption", "particle smoke reveal", [960, 810], 30, [0.56, 0.72, 0.92]);
    app.endUndoGroup();
})();
