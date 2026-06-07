(function () {
    app.beginUndoGroup("AEFT Sports Scorebug Replay");
    var comp = app.project.items.addComp("AEFT Sports Scorebug Replay", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.015, 0.08, 0.045];

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

    for (var i = 0; i < 8; i++) {
        var yard = addRect("Field Yard Line " + i, [220 + i * 220, 540], [8, 980], [0.42, 0.68, 0.42]);
        yard.property("Transform").property("Opacity").setValue(74);
    }
    addRect("Midfield Stripe", [960, 540], [1920, 10], [0.72, 0.9, 0.64]);
    var replay = addRect("Replay Wipe", [-260, 540], [420, 1080], [1, 0.72, 0.05]);
    replay.property("Transform").property("Rotation").setValue(-18);
    replay.property("Transform").property("Opacity").setValue(38);
    replay.property("Transform").property("Position").setValueAtTime(0.5, [-260, 540]);
    replay.property("Transform").property("Position").setValueAtTime(3.8, [2180, 540]);
    addRect("Scorebug Base", [960, 112], [1320, 118], [0.02, 0.03, 0.06]);
    addRect("Home Team Plate", [615, 112], [340, 86], [0.0, 0.24, 0.72]);
    addRect("Away Team Plate", [1305, 112], [340, 86], [0.8, 0.08, 0.08]);
    addText("Home Team", "NOVA", [540, 128], 46, [1, 1, 1]);
    addText("Away Team", "PULSE", [1230, 128], 46, [1, 1, 1]);
    var homeScore = addText("Home Score", "24", [735, 130], 62, [1, 0.86, 0.18]);
    var awayScore = addText("Away Score", "21", [1425, 130], 62, [1, 0.86, 0.18]);
    homeScore.property("Transform").property("Scale").expression = "p = 100 + Math.sin(time * Math.PI * 3) * 5; [p, p];";
    awayScore.property("Transform").property("Scale").expression = "p = 100 + Math.sin(time * Math.PI * 3 + 1) * 4; [p, p];";
    var ticker = addText("Replay Ticker", "REPLAY  /  THIRD QUARTER  /  01:42", [960, 1010], 36, [0.95, 0.98, 1]);
    ticker.property("Transform").property("Position").setValueAtTime(0.0, [2600, 1010]);
    ticker.property("Transform").property("Position").setValueAtTime(5.8, [-700, 1010]);
    app.endUndoGroup();
})();
