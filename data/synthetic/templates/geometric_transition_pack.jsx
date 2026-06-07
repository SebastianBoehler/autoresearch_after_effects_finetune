(function () {
    app.beginUndoGroup("AEFT Geometric Transition Pack");
    var comp = app.project.items.addComp("AEFT Geometric Transition Pack", 1920, 1080, 1, 5, 30);
    comp.bgColor = [0.03, 0.035, 0.05];

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

    var panelA = addRect("Scene A Panel", [440, 540], [640, 560], [0.05, 0.18, 0.45]);
    var panelB = addRect("Scene B Panel", [1490, 540], [640, 560], [0.7, 0.08, 0.16]);
    panelA.property("Transform").property("Position").setValueAtTime(0.2, [440, 540]);
    panelA.property("Transform").property("Position").setValueAtTime(3.2, [310, 540]);
    panelB.property("Transform").property("Position").setValueAtTime(0.2, [1490, 540]);
    panelB.property("Transform").property("Position").setValueAtTime(3.2, [1600, 540]);
    addText("Scene A Label", "SOURCE", [440, 540], 54, [1, 1, 1]);
    addText("Scene B Label", "TARGET", [1490, 540], 54, [1, 1, 1]);
    var colors = [[1, 0.72, 0.08], [0.0, 0.72, 1], [0.98, 0.98, 1]];
    for (var i = 0; i < 5; i++) {
        var wipe = addRect("Diagonal Wipe " + i, [-360 + i * 250, 540], [118, 920], colors[i % 3]);
        wipe.property("Transform").property("Rotation").setValue(-24);
        wipe.property("Transform").property("Position").setValueAtTime(0.45 + i * 0.11, [-360 + i * 250, 520]);
        wipe.property("Transform").property("Position").setValueAtTime(2.25 + i * 0.11, [620 + i * 180, 560]);
        wipe.property("Transform").property("Position").setValueAtTime(4.2 + i * 0.08, [1180 + i * 130, 490]);
        wipe.property("Transform").property("Opacity").setValueAtTime(0.45 + i * 0.11, 82);
        wipe.property("Transform").property("Opacity").setValueAtTime(4.7 + i * 0.08, 18);
    }
    for (var j = 0; j < 8; j++) {
        var tile = addRect("Transition Tile " + j, [500 + (j % 4) * 210, 735 + Math.floor(j / 4) * 118], [88, 88], colors[(j + 1) % 3]);
        tile.property("Transform").property("Scale").setValueAtTime(2.0 + j * 0.12, [0, 0]);
        tile.property("Transform").property("Scale").setValueAtTime(2.55 + j * 0.12, [100, 100]);
        tile.property("Transform").property("Scale").setValueAtTime(4.7 + j * 0.04, [72, 72]);
        tile.property("Transform").property("Rotation").expression = "time * " + (90 + j * 18) + ";";
    }
    for (var k = 0; k < 8; k++) {
        var marker = addRect("Transition Guide Marker " + k, [380 + k * 165, 920], [88, 8], colors[k % 3]);
        marker.property("Transform").property("Scale").expression = "w = 45 + Math.abs(Math.sin(time * " + (2.2 + k * 0.13) + " + " + k + ")) * 55; [w, 100];";
    }
    var targetCard = addRect("Late Target Card", [960, 520], [420, 210], [0.03, 0.04, 0.07]);
    targetCard.property("Transform").property("Scale").setValueAtTime(3.35, [0, 100]);
    targetCard.property("Transform").property("Scale").setValueAtTime(4.15, [100, 100]);
    targetCard.property("Transform").property("Position").setValueAtTime(3.35, [900, 520]);
    targetCard.property("Transform").property("Position").setValueAtTime(4.9, [1018, 500]);
    targetCard.property("Transform").property("Opacity").expression = "72 + Math.sin(time * 5) * 18;";
    for (var m = 0; m < 10; m++) {
        var lateTile = addRect("Outro Tile Sweep " + m, [280 + m * 150, 210 + (m % 3) * 86], [74, 74], colors[(m + 2) % 3]);
        lateTile.property("Transform").property("Scale").setValueAtTime(3.15 + m * 0.04, [0, 0]);
        lateTile.property("Transform").property("Scale").setValueAtTime(4.85, [86 + (m % 3) * 12, 86 + (m % 3) * 12]);
        lateTile.property("Transform").property("Position").setValueAtTime(3.15 + m * 0.04, [280 + m * 150, 210 + (m % 3) * 86]);
        lateTile.property("Transform").property("Position").setValueAtTime(4.9, [360 + m * 118, 250 + (m % 2) * 116]);
        lateTile.property("Transform").property("Rotation").expression = "time * " + (70 + m * 9) + ";";
    }
    for (var n = 0; n < 6; n++) {
        var slit = addRect("Final Slit Scan " + n, [480 + n * 180, 835], [118, 10], colors[n % 3]);
        slit.property("Transform").property("Scale").expression = "w = 36 + Math.abs(Math.sin(time * " + (2.6 + n * 0.15) + " + " + n + ")) * 86; [w, 100];";
        slit.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.5 + n * 0.1) + ") * 48, 0];";
    }
    addText("Late Target Label", "CUT ACCEPTED", [960, 500], 42, [0.92, 0.98, 1]);
    addText("Late Target Mode", "iris / slab / tile / grid", [960, 565], 26, [0.45, 0.84, 1]);
    addText("Pack Label", "MATCH CUT / WIPE / TILE", [960, 150], 44, [0.9, 0.96, 1]);
    app.endUndoGroup();
})();
