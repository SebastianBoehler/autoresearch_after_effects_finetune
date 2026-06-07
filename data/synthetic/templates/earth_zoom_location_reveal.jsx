(function () {
    app.beginUndoGroup("AEFT Earth Zoom Location Reveal");
    var comp = app.project.items.addComp("AEFT Earth Zoom Location Reveal", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.01, 0.018, 0.035];

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

    var earth = addCircle("Vector Earth", [960, 540], 330, [0.03, 0.22, 0.52]);
    earth.property("Transform").property("Scale").setValueAtTime(0.3, [62, 62]);
    earth.property("Transform").property("Scale").setValueAtTime(2.5, [145, 145]);
    earth.property("Transform").property("Position").setValueAtTime(0.3, [960, 540]);
    earth.property("Transform").property("Position").setValueAtTime(2.8, [770, 610]);
    var land = [[810, 420, 220, 78], [1070, 490, 300, 92], [925, 650, 250, 70], [1130, 720, 190, 54]];
    for (var i = 0; i < land.length; i++) {
        var strip = addRect("Map Land Strip " + i, [land[i][0], land[i][1]], [land[i][2], land[i][3]], [0.12, 0.58, 0.38]);
        strip.property("Transform").property("Rotation").setValue(i % 2 ? -8 : 12);
    }
    for (var r = 0; r < 5; r++) {
        var ring = addCircle("Target Ring " + r, [1175, 430], 42 + r * 34, [0.1, 0.82, 1]);
        ring.property("Transform").property("Opacity").setValue(28 - r * 3);
        ring.property("Transform").property("Scale").setValueAtTime(2.4 + r * 0.08, [30, 30]);
        ring.property("Transform").property("Scale").setValueAtTime(3.7 + r * 0.08, [100, 100]);
    }
    var pin = addCircle("Location Pin Dot", [1175, 430], 24, [1, 0.22, 0.36]);
    pin.property("Transform").property("Scale").expression = "s = 88 + Math.sin(time * 5.4) * 18; [s, s];";
    var dataCard = addRect("Data Card", [1420, 570], [420, 260], [0.04, 0.07, 0.11]);
    dataCard.property("Transform").property("Opacity").setValue(92);
    dataCard.property("Transform").property("Position").setValueAtTime(4.1, [1490, 570]);
    dataCard.property("Transform").property("Position").setValueAtTime(6.4, [1420, 570]);
    addText("Location Label", "NEW SIGNAL", [1420, 525], 46, [0.92, 0.98, 1]);
    addText("Location Detail", "lat 48.52 / lon 9.05", [1420, 585], 28, [0.5, 0.86, 1]);
    var scan = addRect("Late Satellite Scan", [1175, 430], [520, 6], [0.1, 0.82, 1]);
    scan.property("Transform").property("Opacity").setValue(54);
    scan.property("Transform").property("Rotation").setValue(-12);
    scan.property("Transform").property("Position").setValueAtTime(4.0, [920, 480]);
    scan.property("Transform").property("Position").setValueAtTime(6.6, [1450, 380]);
    var footer = addText("Map Footer", "SATELLITE ZOOM / ROUTE LOCK / DATA OVERLAY", [960, 925], 32, [0.78, 0.9, 1]);
    footer.property("Transform").property("Opacity").expression = "74 + Math.sin(time * 3.2) * 18;";
    app.endUndoGroup();
})();
