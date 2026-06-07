(function () {
    app.beginUndoGroup("AEFT Product Reveal Split");
    var comp = app.project.items.addComp("AEFT Product Reveal Split", 1920, 1080, 1, 5, 30);
    comp.bgColor = [0.035, 0.045, 0.06];

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

    addRect("Deep Stage", [960, 540], [1320, 620], [0.055, 0.075, 0.1]);
    for (var i = 0; i < 7; i++) {
        var stripe = addRect("Diagonal Motion Stripe " + i, [240 + i * 260, 225 + (i % 3) * 130], [260, 22], [0.08, 0.42, 0.62]);
        stripe.property("Transform").property("Rotation").setValue(-18);
        stripe.property("Transform").property("Opacity").setValue(24);
        stripe.property("Transform").property("Position").setValueAtTime(0.15 + i * 0.08, [40 + i * 230, 225 + (i % 3) * 130]);
        stripe.property("Transform").property("Position").setValueAtTime(2.9, [240 + i * 245, 255 + (i % 3) * 122]);
        stripe.property("Transform").property("Position").setValueAtTime(4.7, [420 + i * 250, 300 + (i % 3) * 118]);
    }
    var productCard = addRect("Product Card", [1305, 560], [350, 500], [0.92, 0.96, 0.98]);
    productCard.property("Transform").property("Position").setValueAtTime(0.65, [1510, 620]);
    productCard.property("Transform").property("Position").setValueAtTime(1.35, [1305, 560]);
    productCard.property("Transform").property("Position").setValueAtTime(3.2, [1258, 548]);
    productCard.property("Transform").property("Position").setValueAtTime(4.85, [1338, 522]);
    productCard.property("Transform").property("Scale").setValueAtTime(1.35, [96, 96]);
    productCard.property("Transform").property("Scale").setValueAtTime(4.85, [103, 103]);
    var product = addRect("Product Placeholder", [1285, 530], [245, 335], [1, 1, 1]);
    product.property("Transform").property("Scale").setValueAtTime(0.75, [72, 72]);
    product.property("Transform").property("Scale").setValueAtTime(1.45, [100, 100]);
    product.property("Transform").property("Scale").setValueAtTime(3.35, [94, 94]);
    product.property("Transform").property("Scale").setValueAtTime(4.85, [106, 106]);
    product.property("Transform").property("Rotation").setValueAtTime(1.45, -3);
    product.property("Transform").property("Rotation").setValueAtTime(4.85, 2);
    var scan = addRect("Product Scan Sweep", [1160, 360], [46, 360], [0.16, 0.74, 1]);
    scan.property("Transform").property("Opacity").setValue(38);
    scan.property("Transform").property("Position").setValueAtTime(1.05, [1160, 360]);
    scan.property("Transform").property("Position").setValueAtTime(2.65, [1400, 660]);
    scan.property("Transform").property("Position").setValueAtTime(4.55, [1205, 430]);
    for (var j = 0; j < 5; j++) {
        var dot = addRect("Feature Pulse " + j, [250 + j * 102, 742], [48, 48], [0.18, 0.74, 0.62]);
        dot.property("Transform").property("Scale").expression = "s = 78 + Math.sin(time * 4 + " + j + ") * 18; [s, s];";
        dot.property("Transform").property("Opacity").setValueAtTime(0.85 + j * 0.1, 0);
        dot.property("Transform").property("Opacity").setValueAtTime(1.55 + j * 0.1, 100);
        dot.property("Transform").property("Position").setValueAtTime(2.2 + j * 0.08, [250 + j * 102, 742]);
        dot.property("Transform").property("Position").setValueAtTime(4.65, [292 + j * 92, 705 + (j % 2) * 34]);
    }
    for (var r = 0; r < 9; r++) {
        var rail = addRect("Late Product Rail " + r, [220 + r * 135, 205 + (r % 3) * 58], [88, 8], [0.16, 0.74, 1]);
        rail.property("Transform").property("Opacity").expression = "32 + Math.abs(Math.sin(time * " + (2.4 + r * 0.16) + " + " + r + ")) * 42;";
        rail.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.2 + r * 0.08) + ") * 34, Math.cos(time * " + (1.4 + r * 0.05) + ") * 18];";
    }
    for (var s = 0; s < 4; s++) {
        var swatch = addRect("Orbiting Color Swatch " + s, [1138 + s * 95, 252], [62, 62], [[0.16, 0.74, 1], [0.18, 0.74, 0.62], [1, 0.62, 0.08], [0.95, 0.08, 0.42]][s]);
        swatch.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.5 + s * 0.2) + " + " + s + ") * 42, Math.cos(time * " + (1.1 + s * 0.15) + ") * 30];";
        swatch.property("Transform").property("Rotation").expression = "time * " + (24 + s * 8) + ";";
    }
    var title = addText("Title", "SCRIPTED MOTION", [345, 400], 74, [0.94, 0.98, 1]);
    title.property("Transform").property("Position").setValueAtTime(0.45, [245, 400]);
    title.property("Transform").property("Position").setValueAtTime(1.15, [345, 400]);
    title.property("Transform").property("Position").setValueAtTime(4.75, [382, 382]);
    var subtitle = addText("Subtitle", "A ready comp from generated JSX", [350, 485], 34, [0.58, 0.78, 1]);
    subtitle.property("Transform").property("Opacity").setValueAtTime(0.9, 0);
    subtitle.property("Transform").property("Opacity").setValueAtTime(1.55, 100);
    subtitle.property("Transform").property("Position").setValueAtTime(1.55, [350, 485]);
    subtitle.property("Transform").property("Position").setValueAtTime(4.7, [382, 505]);
    var cta = addRect("CTA Chip", [430, 615], [300, 64], [0.18, 0.74, 0.62]);
    cta.property("Transform").property("Scale").setValueAtTime(1.1, [0, 100]);
    cta.property("Transform").property("Scale").setValueAtTime(1.8, [100, 100]);
    cta.property("Transform").property("Position").setValueAtTime(2.1, [430, 615]);
    cta.property("Transform").property("Position").setValueAtTime(4.7, [470, 635]);
    addText("CTA Text", "RENDER READY", [342, 628], 28, [0.02, 0.06, 0.07]);
    for (var k = 0; k < 4; k++) {
        var stat = addRect("Spec Meter " + k, [1110, 805 + k * 42], [180 + k * 34, 8], [0.16, 0.74, 1]);
        stat.property("Transform").property("Scale").setValueAtTime(1.6 + k * 0.12, [0, 100]);
        stat.property("Transform").property("Scale").setValueAtTime(2.4 + k * 0.12, [100, 100]);
        stat.property("Transform").property("Position").setValueAtTime(4.6, [1165 + k * 28, 805 + k * 42]);
        stat.property("Transform").property("Opacity").expression = "56 + Math.sin(time * " + (2.2 + k * 0.18) + ") * 24;";
    }
    app.endUndoGroup();
})();
