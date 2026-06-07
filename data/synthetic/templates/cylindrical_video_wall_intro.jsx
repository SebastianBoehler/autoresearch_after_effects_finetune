(function () {
    app.beginUndoGroup("AEFT Cylindrical Video Wall Intro");
    var comp = app.project.items.addComp("AEFT Cylindrical Video Wall Intro", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.018, 0.02, 0.03];

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

    function addText(name, value, pos, size, color, align) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = align || ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    addRect("Back Wall", [960, 520], [1700, 640], [0.03, 0.05, 0.085]);
    addRect("Floor Reflection", [960, 900], [1640, 170], [0.02, 0.03, 0.05]).property("Transform").property("Opacity").setValue(58);
    addText("Wall Title", "LIVE MEDIA WALL", [960, 145], 58, [0.92, 0.98, 1]);
    addText("Wall Subtitle", "one script builds rotating placeholder screens", [960, 205], 28, [0.34, 0.82, 1]);

    var palette = [[0.1, 0.38, 0.92], [0.95, 0.18, 0.48], [0.12, 0.8, 0.68], [1, 0.67, 0.14]];
    for (var i = 0; i < 11; i++) {
        var curve = Math.abs(i - 5);
        var x = 240 + i * 144;
        var y = 540 + curve * 26;
        var w = 132 - curve * 5;
        var h = 410 - curve * 30;
        var delay = 0.12 + i * 0.06;
        var panel = addRect("Arc Media Panel " + i, [x, y + 90], [w, h], palette[i % palette.length]);
        panel.property("Transform").property("Opacity").setValue(82);
        panel.property("Transform").property("Position").setValueAtTime(delay, [x, y + 120]);
        panel.property("Transform").property("Position").setValueAtTime(delay + 0.75, [x, y]);
        panel.property("Transform").property("Scale").setValueAtTime(delay, [28, 100]);
        panel.property("Transform").property("Scale").setValueAtTime(delay + 0.75, [100, 100]);
        addRect("Panel Highlight " + i, [x - w * 0.25, y - h * 0.3], [w * 0.18, h * 0.82], [1, 1, 1]).property("Transform").property("Opacity").setValue(26);
        var label = addText("Panel Label " + i, "CAM " + (i + 1), [x, y + h * 0.33], 18, [0.94, 0.98, 1]);
        label.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        label.property("Transform").property("Opacity").setValueAtTime(delay + 0.55, 100);
    }

    for (var t = 0; t < 8; t++) {
        var tick = addRect("Ticker Block " + t, [420 + t * 150, 815], [104, 18], palette[t % palette.length]);
        tick.property("Transform").property("Position").setValueAtTime(1.4, [420 + t * 150, 815]);
        tick.property("Transform").property("Position").setValueAtTime(6.6, [220 + t * 150, 815]);
    }
    var midPulse = addRect("Mid Wall Pulse", [960, 252], [780, 8], [0.56, 0.92, 1]);
    midPulse.property("Transform").property("Scale").setValueAtTime(3.0, [20, 100]);
    midPulse.property("Transform").property("Scale").setValueAtTime(4.1, [100, 100]);
    midPulse.property("Transform").property("Opacity").setValueAtTime(3.0, 0);
    midPulse.property("Transform").property("Opacity").setValueAtTime(3.4, 78);
    midPulse.property("Transform").property("Opacity").setValueAtTime(4.1, 0);
    var sweep = addRect("Wall Scan Sweep", [120, 520], [36, 610], [0.56, 0.92, 1]);
    sweep.property("Transform").property("Opacity").setValue(42);
    sweep.property("Transform").property("Position").setValueAtTime(0.8, [120, 520]);
    sweep.property("Transform").property("Position").setValueAtTime(6.3, [1800, 520]);
    app.endUndoGroup();
})();
