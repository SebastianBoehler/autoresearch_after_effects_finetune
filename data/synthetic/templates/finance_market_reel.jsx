(function () {
    app.beginUndoGroup("AEFT Finance Market Reel");
    var comp = app.project.items.addComp("AEFT Finance Market Reel", 1080, 1920, 1, 7, 30);
    comp.bgColor = [0.025, 0.035, 0.045];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0], pos[1] + 90]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.35, pos);
        return layer;
    }

    function addCircle(name, pos, radius, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([radius * 2, radius * 2]);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Scale").setValueAtTime(delay, [0, 0]);
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
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.2, 100);
        return layer;
    }

    addText("Title", "MARKET OPEN", [540, 185], 72, [0.9, 1, 0.94], 0.2);
    addRect("Chart Backplate", [540, 760], [840, 720], [0.06, 0.09, 0.12], 0.35);
    for (var g = 0; g < 8; g++) {
        addRect("Chart Grid Row " + g, [540, 450 + g * 82], [800, 2], [0.12, 0.2, 0.24], 0.35).property("Transform").property("Opacity").setValue(36);
    }
    for (var i = 0; i < 16; i++) {
        var x = 160 + i * 50;
        var up = i % 3 !== 1;
        var candle = addRect("Candle " + i, [x, 780 - (i % 5) * 34], [24, 150 + (i % 4) * 28], up ? [0.12, 0.85, 0.52] : [1, 0.25, 0.25], 0.65 + i * 0.06);
        candle.property("Transform").property("Scale").setValueAtTime(0.7 + i * 0.05, [100, 12]);
        candle.property("Transform").property("Scale").setValueAtTime(3.2 + i * 0.04, [100, 100]);
        addRect("Wick " + i, [x, 780 - (i % 5) * 34], [5, 210 + (i % 3) * 36], [0.7, 0.8, 0.86], 0.55 + i * 0.04);
    }
    for (var v = 0; v < 12; v++) {
        var bar = addRect("Volume Bar " + v, [220 + v * 58, 1130], [28, 160], [0.18, 0.46, 0.92], 1.1 + v * 0.04);
        bar.property("Transform").property("Scale").expression = "h = 35 + Math.abs(Math.sin(time * " + (2.4 + v * 0.11) + " + " + v + ")) * 80; [100, h];";
    }
    var marketSweep = addRect("Market Sweep", [140, 780], [90, 720], [0.82, 0.95, 1], 1.2);
    marketSweep.property("Transform").property("Opacity").setValue(34);
    marketSweep.property("Transform").property("Position").setValueAtTime(1.2, [140, 780]);
    marketSweep.property("Transform").property("Position").setValueAtTime(5.5, [940, 780]);
    for (var t = 0; t < 7; t++) {
        var tag = addRect("Signal Tag " + t, [170 + t * 125, 520 + (t % 2) * 170], [84, 28], t % 2 ? [1, 0.24, 0.24] : [0.12, 0.85, 0.52], 1.4 + t * 0.1);
        tag.property("Transform").property("Position").expression =
            "value + [0, Math.sin(time * " + (2.0 + t * 0.12) + ") * 24];";
    }
    for (var l = 0; l < 11; l++) {
        var point = addCircle("Price Line Point " + l, [190 + l * 74, 900 - (l % 4) * 62], 11, [0.9, 1, 0.64], 1.0 + l * 0.05);
        point.property("Transform").property("Position").expression = "value + [0, Math.sin(time * 3 + " + l + ") * 18];";
        if (l > 0) {
            var seg = addRect("Price Line Segment " + l, [154 + l * 74, 870 - (l % 4) * 52], [86, 6], [0.9, 1, 0.64], 1.05 + l * 0.04);
            seg.property("Transform").property("Rotation").setValue(-24 + (l % 3) * 18);
            seg.property("Transform").property("Opacity").expression = "54 + Math.sin(time * 4 + " + l + ") * 20;";
        }
    }
    addRect("Portfolio Card", [540, 1390], [760, 220], [0.92, 0.97, 0.92], 2.2);
    addText("Portfolio Value", "+18.4% PORTFOLIO", [540, 1360], 46, [0.04, 0.12, 0.08], 2.35);
    addText("Ticker", "AURA +4.2  /  NOVA -1.1  /  QNT +7.6", [540, 1535], 30, [0.38, 1, 0.68], 2.6);
    for (var c = 0; c < 6; c++) {
        addCircle("Coin Marker " + c, [185 + c * 140, 1660], 34, [1, 0.76, 0.12], 2.0 + c * 0.18).property("Transform").property("Rotation").expression = "time * 120;";
    }
    var tickerRail = addRect("Bottom Price Rail", [540, 1810], [880, 42], [0.06, 0.12, 0.16], 2.6);
    tickerRail.property("Transform").property("Opacity").setValue(82);
    var movingTape = addText("Moving Tape", "FUTURES +0.8  VIX -2.1  AI INDEX +5.4", [540, 1822], 26, [0.82, 1, 0.9], 2.75);
    movingTape.property("Transform").property("Position").setValueAtTime(2.75, [960, 1822]);
    movingTape.property("Transform").property("Position").setValueAtTime(6.8, [120, 1822]);
    app.endUndoGroup();
})();
