(function () {
    app.beginUndoGroup("AEFT Speed Ramp Timewarp Promo");
    var comp = app.project.items.addComp("AEFT Speed Ramp Timewarp Promo", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.012, 0.012, 0.015];
    var clipComp = app.project.items.addComp("AEFT Nested Action Clip", 960, 540, 1, 3, 30);

    function addRect(target, name, pos, size, color) {
        var layer = target.layers.addShape();
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

    for (var f = 0; f < 7; f++) {
        var runner = addRect(clipComp, "Action Frame Bar " + f, [120 + f * 120, 270], [86, 260 - f * 22], [0.12, 0.45 + f * 0.05, 1]);
        runner.property("Transform").property("Rotation").setValue(-14 + f * 4);
    }
    var clip = comp.layers.add(clipComp);
    clip.name = "Time Remapped Action Clip";
    clip.property("Transform").property("Position").setValue([960, 485]);
    clip.property("Transform").property("Scale").setValue([145, 145]);
    clip.timeRemapEnabled = true;
    var remap = clip.property("ADBE Time Remapping");
    remap.setValueAtTime(0.0, 0.0);
    remap.setValueAtTime(1.25, 0.9);
    remap.setValueAtTime(2.0, 1.05);
    remap.setValueAtTime(3.1, 2.6);
    remap.setValueAtTime(5.8, 2.95);
    for (var i = 0; i < 14; i++) {
        var streak = addRect(comp, "Speed Streak " + i, [220 + i * 118, 790 + (i % 3) * 22], [120, 10], [1, 0.62, 0.12]);
        streak.property("Transform").property("Scale").setValueAtTime(0.5 + i * 0.08, [0, 100]);
        streak.property("Transform").property("Scale").setValueAtTime(4.8 + i * 0.04, [120, 100]);
    }
    for (var b = 0; b < 5; b++) {
        var beat = addRect(comp, "Beat Marker " + b, [410 + b * 270, 930], [8, 120], [0.12, 0.82, 1]);
        beat.property("Transform").property("Scale").setValueAtTime(0.7 + b * 0.7, [100, 40]);
        beat.property("Transform").property("Scale").setValueAtTime(1.0 + b * 0.7, [100, 115]);
    }
    addText("Speed Title", "SPEED RAMP / FREEZE / HIT", [960, 150], 62, [0.95, 0.98, 1]);
    addText("Velocity Graph", "0.25x      HOLD      3.0x      IMPACT", [960, 1010], 32, [0.72, 0.84, 1]);
    app.endUndoGroup();
})();
