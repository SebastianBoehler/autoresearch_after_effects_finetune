(function () {
    app.beginUndoGroup("AEFT Broadcast Live Stream Pack");
    var comp = app.project.items.addComp("AEFT Broadcast Live Stream Pack", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.035, 0.04, 0.055];

    function rect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var box = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        box.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function text(name, value, pos, size, color) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    rect("Main Feed Frame", [630, 420], [820, 460], [0.08, 0.1, 0.13]);
    rect("Main Feed Plate", [630, 420], [760, 390], [0.13, 0.18, 0.23]);
    rect("Guest Feed Frame", [1380, 350], [500, 320], [0.08, 0.1, 0.13]);
    rect("Guest Feed Plate", [1380, 350], [448, 260], [0.16, 0.2, 0.24]);
    for (var scan = 0; scan < 8; scan++) {
        var line = rect("Feed Scanline " + scan, [630, 255 + scan * 48], [760, 3], [0.18, 0.7, 1]);
        line.property("Transform").property("Opacity").expression = "18 + Math.sin(time * 5 + " + scan + ") * 14;";
        line.property("Transform").property("Position").expression = "value + [0, ((time * 45 + " + (scan * 11) + ") % 34) - 17];";
    }
    rect("Lower Third", [710, 758], [1020, 108], [0.95, 0.98, 1]);
    rect("Lower Accent", [230, 758], [94, 108], [0.88, 0.04, 0.07]);
    text("Lower Third Name", "LIVE WITH MAYA CHEN", [284, 747], 38, [0.04, 0.06, 0.08]);
    text("Lower Third Topic", "MARKET OPEN // PRODUCT ROADMAP", [284, 794], 25, [0.2, 0.24, 0.28]);
    rect("Breaking Strap", [960, 105], [1920, 78], [0.88, 0.04, 0.07]);
    text("Breaking Text", "BREAKING STREAM PACK // MULTI-FEED READY", [360, 116], 31, [1, 1, 1]);
    var liveDot = rect("Live Pulse Dot", [106, 105], [34, 34], [1, 1, 1]);
    liveDot.property("Transform").property("Opacity").expression = "35 + Math.sin(time * 8) * 35;";
    rect("Sponsor Bug", [1660, 118], [240, 72], [0.08, 0.1, 0.13]);
    text("Sponsor Text", "SPONSOR", [1588, 131], 25, [0.95, 0.98, 1]);
    for (var i = 0; i < 7; i++) {
        var meter = rect("Status Meter " + i, [1320 + i * 58, 560], [34, 120], [0.1, 0.6, 0.95]);
        meter.property("Transform").property("Scale").setValueAtTime(0.9 + i * 0.05, [100, 20]);
        meter.property("Transform").property("Scale").setValueAtTime(2.1 + i * 0.05, [100, 68 + i * 6]);
        meter.property("Transform").property("Opacity").expression = "55 + Math.sin(time * 7 + " + i + ") * 26;";
    }
    for (var j = 0; j < 5; j++) {
        var chat = rect("Chat Bubble " + j, [1390, 690 + j * 52], [430, 34], [0.12, 0.15, 0.19]);
        chat.property("Transform").property("Position").setValueAtTime(1.2 + j * 0.2, [1580, 690 + j * 52]);
        chat.property("Transform").property("Position").setValueAtTime(2.0 + j * 0.2, [1390, 690 + j * 52]);
        text("Chat Text " + j, "viewer_" + j + " signal looks clean", [1195, 700 + j * 52], 21, [0.74, 0.82, 0.88]);
    }
    var ticker = rect("Ticker Rail", [-480, 970], [780, 36], [0.1, 0.58, 0.9]);
    ticker.property("Transform").property("Position").setValueAtTime(1.0, [-480, 970]);
    ticker.property("Transform").property("Position").setValueAtTime(7.3, [2400, 970]);
    var tickerText = text("Ticker Text", "CHAT OPEN // QUESTIONS READY // SEGMENT TWO IN 05:00", [440, 980], 24, [0.88, 0.95, 1]);
    tickerText.property("Transform").property("Position").setValueAtTime(1.0, [440, 980]);
    tickerText.property("Transform").property("Position").setValueAtTime(7.3, [2160, 980]);
    app.endUndoGroup();
})();
