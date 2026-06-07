(function () {
    app.beginUndoGroup("AEFT Geo Terrain Route Flyover");
    var comp = app.project.items.addComp("AEFT Geo Terrain Route Flyover", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.008, 0.018, 0.028];
    var camera = comp.layers.addCamera("Terrain Flyover Camera", [960, 540]);
    camera.property("Transform").property("Position").setValueAtTime(0.2, [960, 540, -1250]);
    camera.property("Transform").property("Position").setValueAtTime(7.6, [1120, 450, -680]);

    function addRect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.threeDLayer = true;
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
        layer.threeDLayer = true;
        return layer;
    }

    for (var i = 0; i < 11; i++) {
        var strip = addRect("Terrain Contour Strip " + i, [960, 260 + i * 58, i * 22], [1250 - i * 58, 12], [0.08, 0.36 + i * 0.035, 0.28]);
        strip.property("Transform").property("Rotation Z").setValue((i % 2 ? -1 : 1) * (6 + i));
        strip.property("Transform").property("Scale").setValueAtTime(0.3 + i * 0.06, [30, 100]);
        strip.property("Transform").property("Scale").setValueAtTime(2.8 + i * 0.08, [100, 100]);
    }
    var route = [];
    for (var r = 0; r < 7; r++) {
        var seg = addRect("Route Trace Segment " + r, [430 + r * 175, 740 - r * 58, 90], [150, 14], [0.92, 0.7, 0.18]);
        seg.property("Transform").property("Rotation Z").setValue(-18);
        seg.property("Transform").property("Scale").setValueAtTime(2.6 + r * 0.32, [0, 100]);
        seg.property("Transform").property("Scale").setValueAtTime(3.15 + r * 0.32, [100, 100]);
        route.push(seg);
    }
    for (var p = 0; p < 4; p++) {
        var pin = addRect("Altitude Pin " + p, [520 + p * 350, 690 - p * 88, 120], [34, 95], [0.1, 0.75, 1]);
        pin.property("Transform").property("Scale").setValueAtTime(3.4 + p * 0.5, [100, 0]);
        pin.property("Transform").property("Scale").setValueAtTime(4.1 + p * 0.5, [100, 100]);
        addText("Altitude Label " + p, "ALT " + (1800 + p * 420), [520 + p * 350, 620 - p * 88, 120], 24, [0.82, 0.95, 1]);
    }
    var card = addRect("Satellite Data Card", [1430, 230, 80], [420, 170], [0.035, 0.06, 0.085]);
    card.property("Transform").property("Position").setValueAtTime(5.2, [1540, 230, 80]);
    card.property("Transform").property("Position").setValueAtTime(7.4, [1430, 230, 80]);
    addText("Geo Header", "GEO TERRAIN ROUTE", [960, 130, 0], 58, [0.92, 0.98, 1]);
    addText("Geo Footer", "camera push / contour depth / route trace", [960, 955, 0], 30, [0.7, 0.84, 1]);
    app.endUndoGroup();
})();
