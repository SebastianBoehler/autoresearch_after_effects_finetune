(function () {
    app.beginUndoGroup("AEFT ASCII Signal Glitch Title");
    var comp = app.project.items.addComp("AEFT ASCII Signal Glitch Title", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.006, 0.008, 0.012];

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
        doc.justification = ParagraphJustification.LEFT_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    addRect("Terminal Plate", [960, 540], [1550, 760], [0.02, 0.028, 0.04]);
    addRect("Decoder Header", [960, 170], [1450, 84], [0.045, 0.07, 0.09]);
    addText("Header Copy", "ASCII DECODER // SIGNAL TRACE", [265, 182], 34, [0.58, 1, 0.78]);
    addText("Clock Readout", "UTC 22:14:09 / NODE 7C11", [1190, 182], 26, [0.42, 0.68, 0.76]);

    var rows = [
        "RX // 7C11 packet accepted",
        "KEY // handshake seed A9F3",
        "CHK // frame window 000-090",
        "BUS // carrier drift -02.4db",
        "TMP // buffer parity restored",
        "OPR // route alpha selected",
        "LOG // null byte scrub pass",
        "SIG // trace quality rising",
        "ACK // operator confirm pending"
    ];
    for (var i = 0; i < rows.length; i++) {
        var y = 275 + i * 54;
        var row = addRect("Log Row BG " + i, [760, y], [990, 34], [0.025, 0.045, 0.052]);
        row.property("Transform").property("Opacity").setValueAtTime(0.25 + i * 0.16, 0);
        row.property("Transform").property("Opacity").setValueAtTime(0.65 + i * 0.16, 78);
        var copy = addText("Decoder Log Row " + i, rows[i], [290, y + 8], 25, [0.14, 0.94, 0.58]);
        copy.property("Transform").property("Opacity").expression = "time < " + (0.45 + i * 0.16) + " ? 0 : 72 + Math.sin(time * 8 + " + i + ") * 16;";
        var chip = addRect("Checksum Block " + i, [1260 + (i % 3) * 88, y], [52, 24], i % 2 === 0 ? [0.1, 0.7, 0.95] : [0.42, 1, 0.55]);
        chip.property("Transform").property("Scale").setValueAtTime(0.45 + i * 0.16, [0, 100]);
        chip.property("Transform").property("Scale").setValueAtTime(0.9 + i * 0.16, [100, 100]);
        chip.property("Transform").property("Opacity").expression = "50 + Math.sin(time * " + (5 + i % 4) + " + " + i + ") * 28;";
    }

    var cardNames = ["CARRIER", "DECODE", "PARITY", "OPERATOR"];
    var cardValues = ["82%", "RUN", "OK", "WAIT"];
    for (var c = 0; c < cardNames.length; c++) {
        var cx = 1110 + (c % 2) * 250;
        var cy = 575 + Math.floor(c / 2) * 135;
        var card = addRect("Status Card " + c, [cx, cy], [205, 92], [0.035, 0.065, 0.078]);
        card.property("Transform").property("Scale").setValueAtTime(1.15 + c * 0.22, [88, 88]);
        card.property("Transform").property("Scale").setValueAtTime(1.65 + c * 0.22, [100, 100]);
        card.property("Transform").property("Opacity").setValueAtTime(1.15 + c * 0.22, 0);
        card.property("Transform").property("Opacity").setValueAtTime(1.65 + c * 0.22, 92);
        addText("Status Label " + c, cardNames[c] + "  " + cardValues[c], [cx - 82, cy + 10], 23, [0.78, 0.96, 0.86]);
    }

    var traceBase = addRect("Signal Trace Base", [760, 825], [980, 8], [0.08, 0.13, 0.16]);
    traceBase.property("Transform").property("Opacity").setValue(80);
    var trace = addRect("Signal Trace Active", [270, 825], [980, 8], [0.34, 1, 0.72]);
    trace.property("Transform").property("Anchor Point").setValue([-490, 0]);
    trace.property("Transform").property("Scale").setValueAtTime(2.8, [0, 100]);
    trace.property("Transform").property("Scale").setValueAtTime(5.35, [100, 100]);
    var cursor = addRect("Decoder Cursor", [270, 800], [18, 54], [0.78, 1, 0.88]);
    cursor.property("Transform").property("Position").setValueAtTime(2.8, [270, 800]);
    cursor.property("Transform").property("Position").setValueAtTime(5.35, [1250, 800]);
    cursor.property("Transform").property("Opacity").expression = "time % 0.32 < 0.16 ? 100 : 25;";

    var badge = addRect("Verified Badge", [1350, 825], [260, 58], [0.1, 0.56, 0.42]);
    badge.property("Transform").property("Scale").setValueAtTime(4.65, [0, 0]);
    badge.property("Transform").property("Scale").setValueAtTime(5.2, [100, 100]);
    var badgeCopy = addText("Verified Copy", "PACKET VERIFIED", [1238, 835], 25, [0.94, 1, 0.92]);
    badgeCopy.property("Transform").property("Opacity").setValueAtTime(4.65, 0);
    badgeCopy.property("Transform").property("Opacity").setValueAtTime(5.2, 100);
    app.endUndoGroup();
})();
