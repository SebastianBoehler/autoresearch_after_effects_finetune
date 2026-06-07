(function () {
    app.beginUndoGroup("AEFT Lyric Waveform Poster");
    var comp = app.project.items.addComp("AEFT Lyric Waveform Poster", 1080, 1080, 1, 7, 30);
    comp.bgColor = [0.98, 0.96, 0.9];

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

    addRect("Poster Panel", [540, 540], [500, 560], [0.08, 0.08, 0.12]);
    addRect("Poster Cutout Top", [540, 255], [340, 18], [0.98, 0.96, 0.9]);
    addRect("Poster Cutout Bottom", [540, 825], [340, 18], [0.98, 0.96, 0.9]);
    addText("Lyric Line 1", "EVERY FRAME", [540, 325], 50, [1, 0.94, 0.8]);
    addText("Lyric Line 2", "HAS A PULSE", [540, 386], 50, [1, 0.94, 0.8]);
    var colors = [[1, 0.22, 0.28], [0.08, 0.72, 1], [1, 0.72, 0.12]];
    for (var i = 0; i < 18; i++) {
        var x = 315 + i * 25;
        var top = addRect("Upper Wave " + i, [x, 555], [11, 124], colors[i % 3]);
        top.property("Transform").property("Scale").expression =
            "h = 26 + Math.abs(Math.sin(time * " + (2.2 + i * 0.1) + " + " + i + ")) * 64; [100, h];";
        top.property("Transform").property("Opacity").expression = "78 + Math.sin(time * " + (1.4 + i * 0.05) + ") * 18;";
        var lower = addRect("Lower Wave " + i, [x, 690], [11, 104], colors[(i + 1) % 3]);
        lower.property("Transform").property("Scale").expression =
            "h = 28 + Math.abs(Math.sin(time * " + (2.5 + i * 0.09) + " + " + (i + 2) + ")) * 56; [100, h];";
        lower.property("Transform").property("Opacity").expression = "76 + Math.sin(time * " + (1.6 + i * 0.04) + " + 1) * 18;";
    }
    for (var b = 0; b < 12; b++) {
        var side = addRect("Outer Beat Pin " + b, [104 + (b % 2) * 872, 170 + Math.floor(b / 2) * 118], [44, 9], colors[b % 3]);
        side.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.6 + b * 0.08) + " + " + b + ") * 24, Math.cos(time * " + (1.9 + b * 0.06) + ") * 16];";
        side.property("Transform").property("Opacity").expression = "30 + Math.abs(Math.sin(time * " + (2.4 + b * 0.11) + ")) * 50;";
    }
    for (var p = 0; p < 10; p++) {
        var spark = addRect("Poster Edge Spark " + p, [132 + (p % 2) * 816, 250 + Math.floor(p / 2) * 124], [56, 8], colors[p % 3]);
        spark.property("Transform").property("Opacity").expression = "28 + Math.abs(Math.sin(time * " + (2.0 + p * 0.12) + " + " + p + ")) * 46;";
        spark.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.4 + p * 0.08) + ") * 32, Math.cos(time * " + (1.8 + p * 0.05) + ") * 18];";
    }
    var cursor = addRect("Lyric Cursor", [220, 455], [70, 10], [1, 0.72, 0.12]);
    cursor.property("Transform").property("Position").setValueAtTime(0.8, [220, 455]);
    cursor.property("Transform").property("Position").setValueAtTime(5.8, [860, 455]);
    var outroSweep = addRect("Poster Outro Stereo Sweep", [120, 930], [70, 12], [0.08, 0.72, 1]);
    outroSweep.property("Transform").property("Position").setValueAtTime(5.3, [120, 930]);
    outroSweep.property("Transform").property("Position").setValueAtTime(6.8, [960, 930]);
    addText("Track Label", "MOODBOARD  /  120 BPM", [540, 900], 26, [0.55, 0.7, 0.82]);
    app.endUndoGroup();
})();
