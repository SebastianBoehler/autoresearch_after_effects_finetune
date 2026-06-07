(function () {
    app.beginUndoGroup("AEFT Lower Third News Ribbon");
    var comp = app.project.items.addComp("AEFT Lower Third News Ribbon", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.03, 0.04, 0.055];

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
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    var sweep = addRect("Broadcast Color Sweep", [-260, 820], [420, 330], [0.22, 0.72, 1]);
    sweep.property("Transform").property("Opacity").setValue(42);
    sweep.property("Transform").property("Position").setValueAtTime(0.2, [-260, 820]);
    sweep.property("Transform").property("Position").setValueAtTime(3.8, [2180, 820]);
    var crawl = addRect("Ticker Crawl Bar", [960, 990], [1920, 72], [0.96, 0.62, 0.12]);
    crawl.property("Transform").property("Position").setValueAtTime(0.0, [-960, 990]);
    crawl.property("Transform").property("Position").setValueAtTime(2.2, [960, 990]);
    crawl.property("Transform").property("Opacity").expression = "82 + Math.sin(time * 5) * 12;";
    var plate = addRect("Sliding Nameplate", [650, 820], [980, 150], [0.06, 0.14, 0.28]);
    var tag = addRect("Section Tag", [205, 752], [270, 54], [0.95, 0.2, 0.16]);
    var line = addRect("Animated Underline", [650, 910], [980, 8], [0.2, 0.72, 1]);
    plate.property("Transform").property("Position").setValueAtTime(0, [-520, 820]);
    plate.property("Transform").property("Position").setValueAtTime(0.75, [650, 820]);
    tag.property("Transform").property("Position").setValueAtTime(0.1, [-160, 752]);
    tag.property("Transform").property("Position").setValueAtTime(0.85, [205, 752]);
    line.property("Transform").property("Scale").setValueAtTime(0.6, [0, 100]);
    line.property("Transform").property("Scale").setValueAtTime(1.2, [100, 100]);
    line.property("Transform").property("Opacity").expression = "62 + Math.sin(time * 4.2) * 28;";
    plate.property("Transform").property("Position").setValueAtTime(3.6, [650, 820]);
    plate.property("Transform").property("Position").setValueAtTime(5.85, [700, 792]);
    addText("Section Text", "UPDATE", [122, 765], 28, [1, 1, 1]);
    addText("Name Text", "After Effects Autoresearch", [210, 824], 50, [0.95, 0.98, 1]);
    addText("Headline Text", "Synthetic scripts with live verification hooks", [210, 875], 29, [0.65, 0.78, 0.92]);
    for (var i = 0; i < 8; i++) {
        var slug = addRect("Ticker Slug " + i, [260 + i * 230, 990], [120, 16], [0.06, 0.14, 0.28]);
        slug.property("Transform").property("Position").setValueAtTime(1.2, [260 + i * 230, 990]);
        slug.property("Transform").property("Position").setValueAtTime(5.8, [-160 + i * 230, 990]);
    }
    for (var j = 0; j < 10; j++) {
        var scan = addRect("Signal Scanline " + j, [180 + j * 170, 720 + (j % 3) * 42], [96, 6], [0.22, 0.72, 1]);
        scan.property("Transform").property("Opacity").expression = "28 + Math.sin(time * " + (2.1 + j * 0.14) + " + " + j + ") * 24;";
        scan.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.4 + j * 0.07) + " + " + j + ") * 54, 0];";
    }
    for (var k = 0; k < 7; k++) {
        var equalizer = addRect("Broadcast Equalizer " + k, [1520 + k * 38, 895], [20, 70 + (k % 3) * 34], [0.95, 0.2, 0.16]);
        equalizer.property("Transform").property("Scale").expression = "h = 55 + Math.sin(time * " + (3.4 + k * 0.22) + " + " + k + ") * 45; [100, h];";
    }
    for (var m = 0; m < 6; m++) {
        var tail = addRect("Late Ticker Tail " + m, [1180 + m * 95, 1018], [62, 10], [0.06, 0.14, 0.28]);
        tail.property("Transform").property("Position").setValueAtTime(3.4 + m * 0.08, [1180 + m * 95, 1018]);
        tail.property("Transform").property("Position").setValueAtTime(5.85, [720 + m * 124, 1018]);
        tail.property("Transform").property("Opacity").expression = "45 + Math.abs(Math.sin(time * " + (2.8 + m * 0.16) + ")) * 45;";
    }
    var flash = addRect("Final Data Flash", [1760, 746], [180, 8], [0.22, 0.72, 1]);
    flash.property("Transform").property("Position").setValueAtTime(3.9, [1760, 746]);
    flash.property("Transform").property("Position").setValueAtTime(5.75, [1460, 746]);
    flash.property("Transform").property("Scale").expression = "w = 48 + Math.abs(Math.sin(time * 3.3)) * 62; [w, 100];";
    var liveDot = addRect("Live Pulse Dot", [1780, 820], [52, 52], [0.95, 0.2, 0.16]);
    liveDot.property("Transform").property("Scale").expression = "s = 84 + Math.sin(time * 6) * 18; [s, s];";
    app.endUndoGroup();
})();
