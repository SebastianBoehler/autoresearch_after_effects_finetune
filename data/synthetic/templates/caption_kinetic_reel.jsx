(function () {
    app.beginUndoGroup("AEFT Caption Kinetic Reel");
    var comp = app.project.items.addComp("AEFT Caption Kinetic Reel", 1080, 1920, 1, 6, 30);
    comp.bgColor = [0.035, 0.04, 0.052];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Scale").setValueAtTime(delay, [0, 100]);
        layer.property("Transform").property("Scale").setValueAtTime(delay + 0.25, [100, 100]);
        return layer;
    }

    function addText(name, value, pos, size, color, delay) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.18, 100);
        layer.property("Transform").property("Scale").setValueAtTime(delay, [82, 82]);
        layer.property("Transform").property("Scale").setValueAtTime(delay + 0.28, [108, 108]);
        layer.property("Transform").property("Scale").setValueAtTime(delay + 0.5, [100, 100]);
        return layer;
    }

    addRect("Top Safe Frame", [540, 210], [820, 6], [0.18, 0.28, 0.42], 0.1);
    addText("Hook", "MAKE IT MOVE", [540, 245], 64, [0.95, 1, 0.98], 0.2);
    var accents = [
        [175, 500, 90, 26, [0.02, 0.58, 0.9]],
        [910, 610, 110, 26, [1, 0.28, 0.22]],
        [160, 840, 78, 78, [0.28, 0.92, 0.5]],
        [920, 1030, 86, 86, [1, 0.72, 0.08]],
        [180, 1280, 120, 24, [1, 0.24, 0.42]],
        [900, 1440, 96, 24, [0.06, 0.62, 1]]
    ];
    for (var a = 0; a < accents.length; a++) {
        addRect("Color Accent " + a, [accents[a][0], accents[a][1]], [accents[a][2], accents[a][3]], accents[a][4], 0.25 + a * 0.12);
    }
    for (var m = 0; m < 12; m++) {
        var meter = addRect("Side Audio Meter " + m, [82, 520 + m * 78], [42, 42 + (m % 4) * 28], [0.06, 0.62, 1], 0.25 + m * 0.04);
        meter.property("Transform").property("Scale").expression = "h = 62 + Math.abs(Math.sin(time * 4 + " + m + ")) * 58; [100, h];";
        var meterR = addRect("Right Audio Meter " + m, [998, 560 + m * 78], [42, 52 + (m % 3) * 24], [1, 0.24, 0.42], 0.3 + m * 0.04);
        meterR.property("Transform").property("Scale").expression = "h = 60 + Math.abs(Math.cos(time * 4 + " + m + ")) * 56; [100, h];";
    }
    var rows = [
        ["REAL", "AE", "TEXT", 700, 0.7],
        ["TIMED", "TO", "SPEECH", 910, 1.7],
        ["EDIT", "EVERY", "WORD", 1120, 2.7],
        ["EXPORT", "WITH", "STYLE", 1330, 3.7]
    ];
    for (var r = 0; r < rows.length; r++) {
        addRect("Caption Card " + r, [540, rows[r][3]], [850, 150], [0.94, 0.96, 0.88], rows[r][4]);
        for (var c = 0; c < 3; c++) {
            var x = 275 + c * 260;
            addRect("Word Highlight " + r + "-" + c, [x, rows[r][3] + 34], [200, 18], [[1, 0.72, 0.08], [0.06, 0.62, 1], [1, 0.24, 0.42]][c], rows[r][4] + c * 0.16);
            addText("Caption Word " + r + "-" + c, rows[r][c], [x, rows[r][3] - 10], 54, [0.05, 0.06, 0.08], rows[r][4] + c * 0.16);
        }
    }
    var reaction = addRect("Reaction Backplate", [540, 1544], [510, 88], [0.26, 0.9, 0.62], 4.25);
    reaction.property("Transform").property("Position").setValueAtTime(4.25, [540, 1544]);
    reaction.property("Transform").property("Position").setValueAtTime(5.85, [590, 1512]);
    reaction.property("Transform").property("Scale").expression = "s = 100 + Math.sin(time * 3.6) * 4; [s, s];";
    addText("Reaction Chip", "98% RETENTION", [540, 1560], 38, [0.05, 0.06, 0.08], 4.35);
    var cursor = addRect("Karaoke Cursor", [160, 1430], [34, 220], [0.06, 0.62, 1], 0.55);
    cursor.property("Transform").property("Position").setValueAtTime(0.55, [160, 690]);
    cursor.property("Transform").property("Position").setValueAtTime(4.6, [910, 1320]);
    var scan = addRect("Caption Timing Sweep", [540, 590], [920, 14], [0.24, 0.9, 0.62], 0.4);
    scan.property("Transform").property("Position").setValueAtTime(0.8, [540, 590]);
    scan.property("Transform").property("Position").setValueAtTime(4.8, [540, 1438]);
    for (var s = 0; s < 10; s++) {
        var syllable = addRect("Syllable Spark " + s, [210 + (s % 5) * 165, 430 + Math.floor(s / 5) * 1010], [86, 10], [0.24, 0.9, 0.62], 0.5 + s * 0.05);
        syllable.property("Transform").property("Opacity").expression = "36 + Math.sin(time * " + (2.8 + s * 0.14) + " + " + s + ") * 28;";
        syllable.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.6 + s * 0.07) + " + " + s + ") * 55, Math.cos(time * " + (1.2 + s * 0.05) + ") * 18];";
    }
    for (var k = 0; k < 4; k++) {
        var lane = addRect("Moving Caption Lane " + k, [540, 650 + k * 210], [760, 5], [0.95, 0.96, 0.88], 0.7 + k * 0.18);
        lane.property("Transform").property("Scale").expression = "w = 68 + Math.sin(time * " + (1.8 + k * 0.2) + ") * 32; [w, 100];";
    }
    var scrub = addRect("Outro Caption Scrubber", [540, 1715], [820, 10], [0.95, 0.96, 0.88], 4.2);
    scrub.property("Transform").property("Scale").setValueAtTime(4.2, [18, 100]);
    scrub.property("Transform").property("Scale").setValueAtTime(5.85, [100, 100]);
    var playhead = addRect("Caption Playhead", [160, 1715], [34, 60], [1, 0.72, 0.08], 4.25);
    playhead.property("Transform").property("Position").setValueAtTime(4.25, [160, 1715]);
    playhead.property("Transform").property("Position").setValueAtTime(5.85, [920, 1715]);
    for (var o = 0; o < 7; o++) {
        var chip = addRect("Late Reaction Blip " + o, [250 + o * 95, 1650 + (o % 2) * 46], [54, 18], [[1, 0.72, 0.08], [0.06, 0.62, 1], [1, 0.24, 0.42]][o % 3], 4.4 + o * 0.06);
        chip.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (2.0 + o * 0.13) + " + " + o + ") * 28, Math.cos(time * " + (1.7 + o * 0.09) + ") * 18];";
        chip.property("Transform").property("Opacity").expression = "45 + Math.abs(Math.sin(time * " + (2.8 + o * 0.12) + ")) * 45;";
    }
    for (var d = 0; d < 8; d++) {
        var trace = addRect("Always-On Caption Trace " + d, [230 + (d % 4) * 210, 360 + Math.floor(d / 4) * 1260], [128, 8], [[1, 0.72, 0.08], [0.06, 0.62, 1], [1, 0.24, 0.42]][d % 3], 0.3 + d * 0.04);
        trace.property("Transform").property("Scale").expression = "w = 48 + Math.abs(Math.sin(time * " + (2.6 + d * 0.18) + " + " + d + ")) * 70; [w, 100];";
        trace.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.5 + d * 0.1) + " + " + d + ") * 42, Math.cos(time * " + (1.8 + d * 0.08) + ") * 24];";
        trace.property("Transform").property("Opacity").expression = "34 + Math.abs(Math.sin(time * " + (2.2 + d * 0.12) + ")) * 48;";
    }
    var finalSweep = addRect("Final Subtitle Sweep", [90, 1810], [80, 14], [0.24, 0.9, 0.62], 5.0);
    finalSweep.property("Transform").property("Position").setValueAtTime(5.0, [90, 1810]);
    finalSweep.property("Transform").property("Position").setValueAtTime(5.95, [990, 1810]);
    finalSweep.property("Transform").property("Opacity").setValue(72);
    app.endUndoGroup();
})();
