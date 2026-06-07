(function () {
    app.beginUndoGroup("AEFT Food Recipe Reel");
    var comp = app.project.items.addComp("AEFT Food Recipe Reel", 1080, 1920, 1, 7, 30);
    comp.bgColor = [0.98, 0.92, 0.82];

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

    function addCircle(name, pos, radius, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([radius * 2, radius * 2]);
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

    addText("Title", "15 MIN PASTA", [540, 220], 82, [0.18, 0.09, 0.05]);
    addText("Subtitle", "creamy tomato skillet", [540, 300], 36, [0.58, 0.22, 0.12]);
    var herbSweep = addRect("Herb Sweep", [-150, 960], [260, 1380], [0.08, 0.54, 0.22]);
    herbSweep.property("Transform").property("Rotation").setValue(-10);
    herbSweep.property("Transform").property("Opacity").setValue(32);
    herbSweep.property("Transform").property("Position").setValueAtTime(0.8, [-150, 960]);
    herbSweep.property("Transform").property("Position").setValueAtTime(5.8, [1230, 960]);
    var plate = addCircle("Plate", [540, 740], 250, [1, 0.98, 0.9]);
    plate.property("Transform").property("Scale").setValueAtTime(0.5, [70, 70]);
    plate.property("Transform").property("Scale").setValueAtTime(1.2, [100, 100]);
    plate.property("Transform").property("Position").setValueAtTime(1.0, [500, 730]);
    plate.property("Transform").property("Position").setValueAtTime(5.6, [585, 755]);
    for (var i = 0; i < 8; i++) {
        var noodle = addRect("Noodle " + i, [430 + i * 32, 720 + (i % 3) * 35], [130, 16], [0.96, 0.62, 0.18]);
        noodle.property("Transform").property("Rotation").setValue(-18 + i * 7);
        noodle.property("Transform").property("Position").expression = "value + [Math.sin(time * 4 + " + i + ") * 9, 0];";
    }
    var sauce = addCircle("Sauce Dot", [540, 740], 64, [0.82, 0.12, 0.08]);
    sauce.property("Transform").property("Scale").expression = "p = 100 + Math.sin(time * Math.PI * 2) * 7; [p, p];";
    var cards = [["01", "boil pasta"], ["02", "stir sauce"], ["03", "finish herbs"]];
    for (var j = 0; j < cards.length; j++) {
        var y = 1160 + j * 170;
        var card = addRect("Step Card " + j, [540, y], [760, 118], [1, 1, 1]);
        card.property("Transform").property("Position").setValueAtTime(1.4 + j * 0.25, [1180, y]);
        card.property("Transform").property("Position").setValueAtTime(2.0 + j * 0.25, [540, y]);
        addText("Step Number " + j, cards[j][0], [265, y + 16], 40, [0.84, 0.14, 0.08]);
        addText("Step Text " + j, cards[j][1], [585, y + 16], 38, [0.2, 0.12, 0.08]);
    }
    addRect("Bottom CTA", [540, 1710], [600, 86], [0.18, 0.09, 0.05]);
    addText("CTA", "SAVE RECIPE", [540, 1735], 40, [1, 0.94, 0.82]);
    app.endUndoGroup();
})();
