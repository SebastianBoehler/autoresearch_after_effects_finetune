(function () {
    app.beginUndoGroup("AEFT Real Estate Listing Tour");
    var comp = app.project.items.addComp("AEFT Real Estate Listing Tour", 1080, 1080, 1, 7, 30);
    comp.bgColor = [0.925, 0.92, 0.88];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0], pos[1] + 60]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.4, pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.2, 100);
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

    addText("Listing Title", "RIVERFRONT LOFT", [540, 100], 58, [0.08, 0.1, 0.12], 0.2);
    addRect("Hero Photo", [540, 335], [820, 390], [0.14, 0.38, 0.46], 0.4);
    addRect("Window Glow", [725, 285], [230, 170], [0.95, 0.82, 0.46], 0.8);
    addRect("Price Backplate", [245, 235], [230, 86], [0.88, 0.2, 0.16], 0.72);
    addText("Price Tag", "$820K", [245, 255], 54, [1, 1, 1], 0.8);
    var stats = [["2 BED", 235], ["91 SQM", 440], ["12 MIN", 645], ["TOP FLOOR", 850]];
    for (var i = 0; i < stats.length; i++) {
        addRect("Stat Card " + i, [stats[i][1], 615], [170, 95], [0.98, 0.98, 0.94], 1.2 + i * 0.12);
        addText("Stat Text " + i, stats[i][0], [stats[i][1], 632], 28, [0.08, 0.1, 0.12], 1.3 + i * 0.12);
    }
    addText("Floorplan Label", "SMART FLOOR PLAN", [540, 750], 34, [0.08, 0.1, 0.12], 2.1);
    var rooms = [[360, 860, 250, 150], [610, 860, 210, 150], [535, 985, 360, 90], [790, 955, 130, 150]];
    for (var j = 0; j < rooms.length; j++) {
        addRect("Room Block " + j, [rooms[j][0], rooms[j][1]], [rooms[j][2], rooms[j][3]], [0.78, 0.8, 0.72], 2.4 + j * 0.14);
    }
    var scan = addRect("Floorplan Scan", [260, 820], [70, 330], [0.08, 0.58, 0.82], 3.2);
    scan.property("Transform").property("Opacity").setValueAtTime(3.2, 40);
    scan.property("Transform").property("Opacity").setValueAtTime(5.8, 40);
    scan.property("Transform").property("Position").setValueAtTime(3.2, [260, 920]);
    scan.property("Transform").property("Position").setValueAtTime(5.8, [820, 920]);
    for (var k = 0; k < 4; k++) {
        addRect("Progress Dot " + k, [465 + k * 50, 1030], [28, 28], k === 1 ? [0.08, 0.58, 0.82] : [0.55, 0.58, 0.55], 4.5 + k * 0.08);
    }
    app.endUndoGroup();
})();
