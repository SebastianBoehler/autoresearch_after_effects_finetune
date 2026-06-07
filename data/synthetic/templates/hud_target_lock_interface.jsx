(function () {
    app.beginUndoGroup("AEFT HUD Target Lock Interface");
    var comp = app.project.items.addComp("AEFT HUD Target Lock Interface", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.005, 0.012, 0.018];

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

    function addRing(name, pos, radius, color, width) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([radius * 2, radius * 2]);
        var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        stroke.property("ADBE Vector Stroke Color").setValue(color);
        stroke.property("ADBE Vector Stroke Width").setValue(width);
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

    addText("Hud Title", "TARGET LOCK", [120, 105], 46, [0.1, 0.9, 1]);
    var alert = addRect("Amber Alert Sweep", [-180, 930], [280, 180], [1, 0.55, 0.08]);
    alert.property("Transform").property("Opacity").setValue(44);
    alert.property("Transform").property("Position").setValueAtTime(0.8, [-180, 930]);
    alert.property("Transform").property("Position").setValueAtTime(5.8, [2100, 930]);
    var magenta = addRect("Magenta Signal Plate", [1700, 845], [330, 180], [0.95, 0.08, 0.42]);
    magenta.property("Transform").property("Opacity").setValue(72);
    var bluePlate = addRect("Blue Signal Plate", [270, 845], [280, 150], [0.08, 0.32, 1]);
    bluePlate.property("Transform").property("Opacity").setValue(58);
    for (var i = 0; i < 4; i++) {
        var ring = addRing("Radar Ring " + i, [960, 540], 150 + i * 72, [0.0, 0.72, 0.86], 3);
        ring.property("Transform").property("Opacity").setValue(30 + i * 8);
        ring.property("Transform").property("Rotation").expression = "time * " + (12 + i * 4) + ";";
    }
    var sweep = addRect("Radar Sweep", [960, 540], [520, 8], [0.2, 1, 0.82]);
    sweep.property("Transform").property("Anchor Point").setValue([0, 0]);
    sweep.property("Transform").property("Opacity").setValue(55);
    sweep.property("Transform").property("Rotation").expression = "time * 95;";
    for (var j = 0; j < 5; j++) {
        var target = addRect("Target Box " + j, [500 + j * 230, 360 + (j % 2) * 250], [110, 76], [1, 0.22, 0.16]);
        target.property("Transform").property("Opacity").expression = "50 + Math.sin(time * 5 + " + j + ") * 25;";
    }
    for (var k = 0; k < 6; k++) {
        addRect("Telemetry Bar " + k, [1510, 245 + k * 80], [260 - k * 20, 18], [0.1, 0.9, 1]);
        addText("Telemetry Label " + k, "SIG " + (k + 1), [1310, 258 + k * 80], 24, [0.55, 0.9, 0.95]);
    }
    var scanline = addRect("Global Scanline", [960, 80], [1920, 5], [0.2, 1, 0.82]);
    scanline.property("Transform").property("Opacity").setValue(35);
    scanline.property("Transform").property("Position").setValueAtTime(0.4, [960, 80]);
    scanline.property("Transform").property("Position").setValueAtTime(6.6, [960, 1000]);
    app.endUndoGroup();
})();
