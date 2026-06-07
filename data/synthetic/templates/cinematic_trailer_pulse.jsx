(function () {
    app.beginUndoGroup("AEFT Cinematic Trailer Pulse");
    var comp = app.project.items.addComp("AEFT Cinematic Trailer Pulse", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.005, 0.006, 0.011];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0] - 80, pos[1]]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.6, pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.25, 100);
        return layer;
    }

    function addText(name, value, pos, size, delay) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = [0.96, 0.9, 0.72];
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.35, 100);
        layer.property("Transform").property("Scale").setValueAtTime(delay, [92, 92]);
        layer.property("Transform").property("Scale").setValueAtTime(delay + 1.4, [108, 108]);
        return layer;
    }

    addRect("Top Letterbox", [960, 70], [1920, 140], [0, 0, 0], 0);
    addRect("Bottom Letterbox", [960, 1010], [1920, 140], [0, 0, 0], 0);
    for (var i = 0; i < 7; i++) {
        var flare = addRect("Light Sweep " + i, [180 + i * 260, 540], [80, 1080], [0.18, 0.28, 0.42], i * 0.18);
        flare.property("Transform").property("Rotation").setValue(-18);
        flare.property("Transform").property("Opacity").setValueAtTime(1.2 + i * 0.16, 0);
        flare.property("Transform").property("Opacity").setValueAtTime(1.5 + i * 0.16, 42);
        flare.property("Transform").property("Opacity").setValueAtTime(2.0 + i * 0.16, 0);
    }
    var ember = addRect("Amber Side Wash", [260, 540], [260, 860], [1, 0.34, 0.08], 1.1);
    ember.property("Transform").property("Opacity").setValueAtTime(1.35, 34);
    ember.property("Transform").property("Opacity").setValueAtTime(7.6, 34);
    var blue = addRect("Blue Counter Wash", [1660, 540], [260, 860], [0.05, 0.42, 1], 2.0);
    blue.property("Transform").property("Opacity").setValueAtTime(2.25, 30);
    blue.property("Transform").property("Opacity").setValueAtTime(7.6, 30);
    blue.property("Transform").property("Position").setValueAtTime(5.2, [1660, 540]);
    blue.property("Transform").property("Position").setValueAtTime(7.7, [1510, 540]);
    addText("Act One", "SIGNAL LOST", [960, 430], 116, 0.4);
    addText("Act Two", "ONE SYSTEM REMAINS", [960, 550], 54, 2.2);
    var actThree = addText("Act Three", "AUTORESEARCH", [960, 705], 86, 4.7);
    actThree.property("Transform").property("Position").setValueAtTime(5.1, [960, 705]);
    actThree.property("Transform").property("Position").setValueAtTime(7.6, [960, 650]);
    actThree.property("Transform").property("Scale").setValueAtTime(5.1, [100, 100]);
    actThree.property("Transform").property("Scale").setValueAtTime(7.6, [118, 118]);
    var flash = addRect("Impact Flash", [960, 540], [1920, 1080], [1, 0.88, 0.55], 4.45);
    flash.property("Transform").property("Opacity").setValueAtTime(4.45, 0);
    flash.property("Transform").property("Opacity").setValueAtTime(4.52, 58);
    flash.property("Transform").property("Opacity").setValueAtTime(4.7, 0);
    for (var c = 0; c < 5; c++) {
        var credit = addText("Late Credit Line " + c, "SYSTEM NODE 0" + (c + 1), [960, 760 + c * 42], 24, 5.25 + c * 0.16);
        credit.property("Transform").property("Position").setValueAtTime(5.25 + c * 0.16, [900, 760 + c * 42]);
        credit.property("Transform").property("Position").setValueAtTime(7.4 + c * 0.06, [1020, 730 + c * 34]);
        credit.property("Transform").property("Opacity").setValueAtTime(7.7, 50);
    }
    for (var g = 0; g < 8; g++) {
        var tick = addRect("Late Radar Tick " + g, [420 + g * 155, 895], [84, 8], [0.96, 0.9, 0.72], 5.4 + g * 0.05);
        tick.property("Transform").property("Scale").setValueAtTime(5.4 + g * 0.05, [0, 100]);
        tick.property("Transform").property("Scale").setValueAtTime(7.5 + g * 0.02, [120, 100]);
    }
    for (var r = 0; r < 6; r++) {
        var shard = addRect("Final Signal Shard " + r, [540 + r * 165, 315 + (r % 2) * 92], [120, 10], [0.96, 0.9, 0.72], 5.9 + r * 0.08);
        shard.property("Transform").property("Opacity").expression = "30 + Math.abs(Math.sin(time * " + (2.4 + r * 0.14) + " + " + r + ")) * 48;";
        shard.property("Transform").property("Position").setValueAtTime(5.9 + r * 0.08, [540 + r * 165, 315 + (r % 2) * 92]);
        shard.property("Transform").property("Position").setValueAtTime(7.85, [610 + r * 138, 355 + (r % 3) * 72]);
        shard.property("Transform").property("Rotation").expression = "Math.sin(time * " + (1.8 + r * 0.12) + ") * 18;";
    }
    var finalPulse = addRect("Final Trailer Pulse", [960, 650], [720, 8], [1, 0.34, 0.08], 6.2);
    finalPulse.property("Transform").property("Scale").setValueAtTime(6.2, [10, 100]);
    finalPulse.property("Transform").property("Scale").setValueAtTime(7.8, [115, 100]);
    finalPulse.property("Transform").property("Opacity").expression = "40 + Math.sin(time * 3.8) * 28;";
    app.endUndoGroup();
})();
