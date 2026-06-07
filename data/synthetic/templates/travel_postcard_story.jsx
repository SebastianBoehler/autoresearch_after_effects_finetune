(function () {
    app.beginUndoGroup("AEFT Travel Postcard Story");
    var comp = app.project.items.addComp("AEFT Travel Postcard Story", 1080, 1920, 1, 7, 30);
    comp.bgColor = [0.78, 0.88, 0.86];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0] - 80, pos[1] + 60]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.5, pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.2, 100);
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

    addText("Story Header", "48 HOURS IN LISBON", [540, 170], 58, [0.08, 0.16, 0.18], 0.2);
    var cards = [[360, 520, 0.4], [690, 875, 1.0], [410, 1210, 1.6]];
    for (var i = 0; i < cards.length; i++) {
        var card = addRect("Postcard " + i, [cards[i][0], cards[i][1]], [470, 620], [0.98, 0.96, 0.88], cards[i][2]);
        card.property("Transform").property("Rotation").setValue(i === 1 ? 8 : -7);
        card.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (0.8 + i * 0.12) + " + " + i + ") * 10, Math.cos(time * " + (0.7 + i * 0.1) + ") * 8];";
        var photo = addRect("Photo Placeholder " + i, [cards[i][0], cards[i][1] - 70], [390, 370], [[0.08, 0.48, 0.68], [0.9, 0.42, 0.22], [0.18, 0.62, 0.44]][i], cards[i][2] + 0.15);
        photo.property("Transform").property("Scale").expression = "s = 100 + Math.sin(time * " + (0.9 + i * 0.15) + " + " + i + ") * 3; [s, s];";
        addText("Card Label " + i, ["ALFAMA", "TRAM 28", "SUNSET"][i], [cards[i][0], cards[i][1] + 215], 36, [0.12, 0.13, 0.12], cards[i][2] + 0.3);
    }
    for (var s = 0; s < 5; s++) {
        var stamp = addRect("Stamp Stripe " + s, [220 + s * 138, 360 + s * 18], [88, 18], [0.08, 0.16, 0.18], 1.8 + s * 0.12);
        stamp.property("Transform").property("Rotation").setValue(-10);
    }
    for (var j = 0; j < 5; j++) {
        addCircle("Route Dot " + j, [260 + j * 140, 1545 - j * 42], 20, [0.98, 0.22, 0.18], 2.4 + j * 0.22);
    }
    var route = addRect("Dotted Route Sweep", [540, 1460], [660, 10], [0.98, 0.22, 0.18], 2.2);
    route.property("Transform").property("Rotation").setValue(-17);
    route.property("Transform").property("Scale").setValueAtTime(2.2, [0, 100]);
    route.property("Transform").property("Scale").setValueAtTime(4.8, [100, 100]);
    addText("Passport Stamp", "NEXT STOP", [770, 1640], 42, [0.98, 0.22, 0.18], 4.4).property("Transform").property("Rotation").setValue(-12);
    app.endUndoGroup();
})();
