(function () {
    app.beginUndoGroup("AEFT Multicolor Tapered Path Reveal");
    var comp = app.project.items.addComp("AEFT Multicolor Tapered Path Reveal", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.025, 0.026, 0.036];

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

    function addSegment(name, a, b, thick, color, delay) {
        var dx = b[0] - a[0];
        var dy = b[1] - a[1];
        var len = Math.sqrt(dx * dx + dy * dy);
        var layer = addRect(name, [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], [len, thick], color);
        layer.property("Transform").property("Rotation").setValue(Math.atan2(dy, dx) * 180 / Math.PI);
        layer.property("Transform").property("Scale").setValueAtTime(delay, [0, 100]);
        layer.property("Transform").property("Scale").setValueAtTime(delay + 0.45, [100, 100]);
        return layer;
    }

    addText("Path Title", "SNAKE PATH SYSTEM", [960, 170], 58, [0.92, 0.96, 1]);
    addText("Path Subtitle", "multicolor segments, tapered caps, and staggered path growth", [960, 230], 28, [0.46, 0.88, 1]);
    var pts = [[240, 690], [430, 470], [650, 640], [845, 405], [1080, 570], [1290, 390], [1510, 640], [1690, 475]];
    var colors = [[0.1, 0.7, 1], [1, 0.24, 0.54], [1, 0.72, 0.12], [0.16, 0.9, 0.55]];
    for (var i = 0; i < pts.length - 1; i++) {
        addSegment("Tapered Color Segment " + i, pts[i], pts[i + 1], 34 - (i % 3) * 7, colors[i % colors.length], 0.4 + i * 0.32);
        var cap = addCircle("Taper Cap " + i, pts[i], 23 - (i % 4) * 3, colors[i % colors.length]);
        cap.property("Transform").property("Scale").setValueAtTime(0.25 + i * 0.32, [0, 0]);
        cap.property("Transform").property("Scale").setValueAtTime(0.75 + i * 0.32, [100, 100]);
    }
    var finalCap = addCircle("Final Path Cap", pts[pts.length - 1], 18, colors[3]);
    finalCap.property("Transform").property("Scale").setValueAtTime(4.6, [86, 86]);
    finalCap.property("Transform").property("Scale").setValueAtTime(6.4, [118, 118]);
    finalCap.property("Transform").property("Opacity").expression = "70 + Math.sin(time * 4.2) * 24;";

    for (var j = 0; j < 9; j++) {
        var guide = addRect("Alignment Guide " + j, [300 + j * 165, 780], [96, 4], [0.5, 0.55, 0.65]);
        guide.property("Transform").property("Opacity").setValue(32);
        guide.property("Transform").property("Scale").setValueAtTime(2.0 + j * 0.08, [0, 100]);
        guide.property("Transform").property("Scale").setValueAtTime(2.6 + j * 0.08, [100, 100]);
    }
    addText("Tool Labels", "COLOR MAP  /  TAPER WIDTH  /  PATH FOLLOW", [960, 875], 34, [0.82, 0.88, 0.96]);
    var tracer = addRect("Late Path Tracer", [240, 690], [78, 12], [0.98, 0.98, 1]);
    tracer.property("Transform").property("Position").setValueAtTime(3.8, [240, 690]);
    tracer.property("Transform").property("Position").setValueAtTime(6.6, [1690, 475]);
    app.endUndoGroup();
})();
