(function () {
    app.beginUndoGroup("AEFT Ecommerce Story Sale");
    var comp = app.project.items.addComp("AEFT Ecommerce Story Sale", 1080, 1920, 1, 7, 30);
    comp.bgColor = [1, 0.95, 0.86];

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

    var sweep = addRect("Story Color Sweep", [-180, 960], [320, 1780], [1, 0.28, 0.22]);
    sweep.property("Transform").property("Rotation").setValue(12);
    sweep.property("Transform").property("Opacity").setValue(42);
    sweep.property("Transform").property("Position").setValueAtTime(0.5, [-180, 960]);
    sweep.property("Transform").property("Position").setValueAtTime(4.8, [1260, 960]);
    addText("Sale Title", "FLASH SALE", [540, 230], 92, [0.08, 0.08, 0.1]);
    addText("Sale Subtitle", "48 hours only", [540, 315], 38, [0.72, 0.12, 0.1]);
    for (var i = 0; i < 3; i++) {
        var y = 640 + i * 330;
        var card = addRect("Product Card " + i, [540, y], [760, 250], [1, 1, 1]);
        card.property("Transform").property("Position").setValueAtTime(0.4 + i * 0.2, [1180, y]);
        card.property("Transform").property("Position").setValueAtTime(1.0 + i * 0.2, [540, y]);
        addRect("Product Image " + i, [305, y], [190, 190], [0.08, 0.24 + i * 0.12, 0.72]);
        addText("Product Name " + i, ["Aero Pack", "Studio Lamp", "Desk Dock"][i], [610, y - 28], 42, [0.08, 0.08, 0.1]);
        addText("Product Price " + i, ["$49", "$79", "$35"][i], [850, y + 48], 54, [0.9, 0.12, 0.08]);
    }
    var badge = addRect("Discount Badge", [790, 430], [250, 120], [0.08, 0.08, 0.1]);
    badge.property("Transform").property("Rotation").setValue(-7);
    badge.property("Transform").property("Scale").expression = "p = 100 + Math.sin(time * Math.PI * 2) * 4; [p, p];";
    addText("Discount Text", "30% OFF", [790, 450], 44, [1, 0.86, 0.18]);
    addRect("CTA Pill", [540, 1680], [520, 96], [0.08, 0.08, 0.1]);
    addText("CTA Text", "SHOP NOW", [540, 1705], 44, [1, 1, 1]);
    app.endUndoGroup();
})();
