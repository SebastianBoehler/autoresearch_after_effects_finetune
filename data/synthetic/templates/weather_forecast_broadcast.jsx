(function () {
    app.beginUndoGroup("AEFT Weather Forecast Broadcast");
    var comp = app.project.items.addComp("AEFT Weather Forecast Broadcast", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.05, 0.08, 0.13];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0] - 80, pos[1]]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.45, pos);
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
        layer.property("Transform").property("Scale").setValueAtTime(delay + 0.35, [100, 100]);
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
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.25, 100);
        return layer;
    }

    addRect("Map Panel", [650, 520], [860, 650], [0.08, 0.18, 0.28], 0.1);
    addText("Header", "GLOBAL WEATHER UPDATE", [960, 110], 54, [0.92, 0.98, 1], 0.2);
    for (var i = 0; i < 9; i++) {
        var node = addCircle("Map Node " + i, [330 + (i % 3) * 230, 340 + Math.floor(i / 3) * 150], 22, [0.2, 0.68, 1], 0.5 + i * 0.08);
        node.property("Transform").property("Opacity").expression = "58 + Math.sin(time * 5 + " + i + ") * 28;";
    }
    var radar = addCircle("Radar Sweep", [640, 520], 220, [0.14, 0.72, 0.95], 0.4);
    radar.property("Transform").property("Opacity").setValue(24);
    radar.property("Transform").property("Rotation").expression = "time * 58;";
    var front = addRect("Storm Front Sweep", [210, 520], [130, 640], [0.9, 0.96, 1], 0.8);
    front.property("Transform").property("Rotation").setValue(-18);
    front.property("Transform").property("Opacity").setValue(42);
    front.property("Transform").property("Position").setValueAtTime(0.8, [210, 520]);
    front.property("Transform").property("Position").setValueAtTime(5.8, [1040, 520]);
    for (var iso = 0; iso < 6; iso++) {
        var line = addRect("Pressure Isoline " + iso, [625, 295 + iso * 78], [640 - iso * 45, 5], [0.42, 0.82, 1], 0.65 + iso * 0.08);
        line.property("Transform").property("Rotation").setValue(-11 + iso * 4);
        line.property("Transform").property("Opacity").expression = "24 + Math.sin(time * 2 + " + iso + ") * 12;";
    }
    var days = ["MON", "TUE", "WED", "THU", "FRI"];
    for (var j = 0; j < days.length; j++) {
        var x = 1110 + j * 130;
        addRect("Forecast Card " + j, [x, 430], [104, 310], [0.93, 0.96, 1], 0.7 + j * 0.12);
        addText("Day " + j, days[j], [x, 330], 28, [0.06, 0.1, 0.14], 0.8 + j * 0.12);
        addCircle("Weather Icon " + j, [x, 410], 32, j % 2 ? [0.56, 0.66, 0.78] : [1, 0.72, 0.12], 0.9 + j * 0.12);
        var temp = addRect("Temp Bar " + j, [x, 545], [28, 150], [0.92, 0.24, 0.16], 1.0 + j * 0.12);
        temp.property("Transform").property("Scale").setValueAtTime(1.0 + j * 0.12, [100, 20]);
        temp.property("Transform").property("Scale").setValueAtTime(4.9 + j * 0.08, [100, 60 + j * 9]);
        addText("Temp Label " + j, (18 + j * 2) + "C", [x, 655], 24, [0.06, 0.1, 0.14], 1.1 + j * 0.12);
    }
    for (var w = 0; w < 8; w++) {
        var wind = addRect("Wind Streak " + w, [260 + w * 180, 785 + (w % 2) * 46], [130, 10], [0.3, 0.82, 1], 1.0 + w * 0.05);
        wind.property("Transform").property("Position").expression =
            "value + [Math.sin(time * " + (2.2 + w * 0.12) + ") * 44, 0];";
    }
    for (var r = 0; r < 14; r++) {
        var rain = addRect("Rain Vector " + r, [265 + (r * 93) % 590, 285 + (r * 61) % 455], [6, 68], [0.76, 0.92, 1], 1.1 + r * 0.03);
        rain.property("Transform").property("Rotation").setValue(18);
        rain.property("Transform").property("Position").expression = "value + [18, ((time * 90 + " + (r * 17) + ") % 92) - 46];";
    }
    var ticker = addRect("Forecast Ticker", [960, 975], [1640, 72], [0.02, 0.42, 0.7], 1.4);
    ticker.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.4) * 24, 0];";
    addText("Ticker Text", "WIND ALERT  /  WEEKEND SUN  /  NORTHERN RAIN BAND", [960, 998], 30, [1, 1, 1], 1.55);
    app.endUndoGroup();
})();
