(function () {
    app.beginUndoGroup("AEFT Kinetic Type Reveal");
    var comp = app.project.items.addComp("AEFT Kinetic Type Reveal", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.035, 0.043, 0.06];

    function addText(name, value, pos, size, color) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var textDoc = layer.property("Source Text").value;
        textDoc.fontSize = size;
        textDoc.fillColor = color;
        textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(textDoc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function addBar(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        var scale = layer.property("Transform").property("Scale");
        scale.setValueAtTime(delay, [0, 100]);
        scale.setValueAtTime(delay + 0.55, [100, 100]);
        return layer;
    }

    addBar("Magenta Color Wash", [260, 540], [220, 820], [0.95, 0.08, 0.42], 0.1);
    addBar("Amber Color Wash", [1660, 540], [220, 820], [1, 0.62, 0.08], 0.25);
    var title = addText("Headline", "MAKE MOTION", [960, 455], 118, [0.94, 0.96, 1]);
    var sub = addText("Subtitle", "Generated from a single JSX script", [960, 575], 38, [0.6, 0.78, 1]);
    addBar("Accent Bar Left", [600, 675], [380, 10], [0.18, 0.56, 1], 0.2);
    addBar("Accent Bar Center", [960, 715], [520, 10], [0.35, 0.9, 0.74], 0.35);
    addBar("Accent Bar Right", [1320, 675], [380, 10], [1, 0.42, 0.35], 0.5);
    var sweep = addBar("Kinetic Scan Sweep", [-160, 520], [90, 820], [0.82, 0.96, 1], 0.2);
    sweep.property("Transform").property("Opacity").setValue(34);
    sweep.property("Transform").property("Rotation").setValue(-14);
    sweep.property("Transform").property("Position").setValueAtTime(0.8, [-160, 520]);
    sweep.property("Transform").property("Position").setValueAtTime(5.6, [2080, 520]);
    for (var i = 0; i < 10; i++) {
        var tick = addBar("Kinetic Tick " + i, [340 + i * 138, 825 + (i % 2) * 38], [74, 9], [0.42, 0.84, 1], 0.45 + i * 0.05);
        tick.property("Transform").property("Position").setValueAtTime(1.0, [340 + i * 138, 825 + (i % 2) * 38]);
        tick.property("Transform").property("Position").setValueAtTime(5.2, [420 + i * 138, 785 + (i % 2) * 38]);
    }
    for (var j = 0; j < 14; j++) {
        var shard = addBar("Looping Type Shard " + j, [270 + j * 105, 300 + (j % 4) * 42], [52 + (j % 3) * 18, 7], [0.22, 0.66, 1], 0.25 + j * 0.04);
        shard.property("Transform").property("Opacity").expression = "44 + Math.sin(time * " + (2.4 + j * 0.13) + " + " + j + ") * 28;";
        shard.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.1 + j * 0.05) + " + " + j + ") * 42, Math.cos(time * " + (1.3 + j * 0.04) + ") * 24];";
        shard.property("Transform").property("Rotation").expression = "Math.sin(time * " + (1.8 + j * 0.08) + " + " + j + ") * 8;";
    }
    for (var r = 0; r < 5; r++) {
        var ring = addBar("Late Echo Ring " + r, [620 + r * 170, 505 + (r % 2) * 92], [130 + r * 28, 6], [0.35, 0.9, 0.74], 2.2 + r * 0.12);
        ring.property("Transform").property("Opacity").expression = "28 + Math.abs(Math.sin(time * " + (2.5 + r * 0.2) + ")) * 46;";
        ring.property("Transform").property("Scale").expression = "w = 70 + Math.sin(time * " + (1.7 + r * 0.13) + " + " + r + ") * 28; [w, 100];";
        ring.property("Transform").property("Rotation").expression = "Math.sin(time * " + (1.2 + r * 0.1) + ") * 16;";
    }
    for (var m = 0; m < 8; m++) {
        var marker = addBar("Outro Rhythm Marker " + m, [450 + m * 130, 900], [70, 12], [1, 0.62, 0.08], 3.2 + m * 0.08);
        marker.property("Transform").property("Position").setValueAtTime(3.2 + m * 0.08, [450 + m * 130, 900]);
        marker.property("Transform").property("Position").setValueAtTime(5.85, [500 + m * 120, 845 + (m % 2) * 44]);
    }

    title.property("Transform").property("Opacity").setValueAtTime(0, 0);
    title.property("Transform").property("Opacity").setValueAtTime(0.7, 100);
    title.property("Transform").property("Position").setValueAtTime(0, [960, 500]);
    title.property("Transform").property("Position").setValueAtTime(0.7, [960, 455]);
    title.property("Transform").property("Scale").setValueAtTime(0.7, [96, 96]);
    title.property("Transform").property("Scale").setValueAtTime(5.6, [103, 103]);
    sub.property("Transform").property("Opacity").setValueAtTime(0.45, 0);
    sub.property("Transform").property("Opacity").setValueAtTime(1.25, 100);
    sub.property("Transform").property("Position").setValueAtTime(1.25, [960, 575]);
    sub.property("Transform").property("Position").setValueAtTime(5.5, [960, 610]);
    sub.property("Transform").property("Scale").expression = "s = 100 + Math.sin(time * 1.6) * 2.5; [s, s];";
    app.endUndoGroup();
})();
