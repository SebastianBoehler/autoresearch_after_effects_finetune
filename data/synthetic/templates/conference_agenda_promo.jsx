(function () {
    app.beginUndoGroup("AEFT Conference Agenda Promo");
    var comp = app.project.items.addComp("AEFT Conference Agenda Promo", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.94, 0.95, 0.96];

    function rect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        shape.property("ADBE Vector Rect Size").setValue(size);
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

    rect("Header Bar", [960, 115], [1920, 170], [0.08, 0.11, 0.16]);
    text("Title", "BUILD SYSTEMS SUMMIT", [130, 125], 58, [0.94, 0.98, 1]);
    rect("Countdown Chip", [1600, 116], [300, 70], [0.1, 0.68, 0.58]);
    text("Countdown Text", "STARTS 09:30", [1486, 128], 30, [0.02, 0.08, 0.07]);
    var speakers = ["KEYNOTE", "DESIGN OPS", "AI WORKFLOWS"];
    var times = ["09:30", "11:00", "14:15"];
    for (var i = 0; i < 3; i++) {
        var x = 335 + i * 470;
        var card = rect("Speaker Card " + i, [x, 390], [380, 245], [1, 1, 1]);
        card.property("Transform").property("Position").setValueAtTime(0.5 + i * 0.25, [x, 520]);
        card.property("Transform").property("Position").setValueAtTime(1.2 + i * 0.25, [x, 390]);
        rect("Speaker Avatar " + i, [x - 125, 338], [90, 90], [0.16, 0.38 + i * 0.12, 0.86]);
        text("Speaker Time " + i, times[i], [x - 166, 475], 32, [0.08, 0.11, 0.16]);
        text("Speaker Label " + i, speakers[i], [x - 166, 404], 29, [0.08, 0.11, 0.16]);
    }
    var progress = rect("Agenda Progress", [940, 690], [1280, 14], [0.09, 0.38, 0.92]);
    progress.property("Transform").property("Scale").setValueAtTime(1.0, [0, 100]);
    progress.property("Transform").property("Scale").setValueAtTime(6.8, [100, 100]);
    for (var j = 0; j < 7; j++) {
        rect("Room Map Block " + j, [470 + j * 150, 820 + (j % 2) * 54], [112, 44], [0.18, 0.22, 0.3]);
    }
    var roomPulse = rect("Mid Agenda Pulse", [470, 820], [150, 10], [0.1, 0.68, 0.58]);
    roomPulse.property("Transform").property("Position").setValueAtTime(3.0, [470, 820]);
    roomPulse.property("Transform").property("Position").setValueAtTime(4.4, [1370, 874]);
    roomPulse.property("Transform").property("Opacity").setValueAtTime(3.0, 0);
    roomPulse.property("Transform").property("Opacity").setValueAtTime(3.4, 86);
    roomPulse.property("Transform").property("Opacity").setValueAtTime(4.4, 0);
    var sweep = rect("Room Map Sweep", [330, 820], [64, 170], [1, 0.74, 0.18]);
    sweep.property("Transform").property("Position").setValueAtTime(2.0, [330, 820]);
    sweep.property("Transform").property("Position").setValueAtTime(7.2, [1450, 874]);
    text("Sponsor Footer", "TRACK A // STUDIO 2 // LIVE STREAM READY", [548, 988], 28, [0.28, 0.32, 0.38]);
    app.endUndoGroup();
})();
