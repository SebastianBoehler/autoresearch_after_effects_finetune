(function () {
    app.beginUndoGroup("AEFT Luxury Perfume Macro Reveal");
    var comp = app.project.items.addComp("AEFT Luxury Perfume Macro Reveal", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.08, 0.065, 0.055];

    function rect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        shape.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function ellipse(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        shape.property("ADBE Vector Ellipse Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function text(name, value, pos, size, color) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    rect("Warm Product Stage", [960, 810], [1920, 240], [0.34, 0.22, 0.15]);
    var bottle = rect("Glass Bottle Body", [1085, 520], [310, 455], [0.93, 0.88, 0.78]);
    bottle.property("Transform").property("Opacity").setValue(72);
    bottle.property("Transform").property("Scale").setValueAtTime(0.6, [82, 82]);
    bottle.property("Transform").property("Scale").setValueAtTime(1.6, [100, 100]);
    rect("Glass Cyan Edge", [1038, 520], [18, 440], [0.62, 0.92, 1]).property("Transform").property("Opacity").setValue(36);
    rect("Glass Amber Edge", [1134, 520], [14, 438], [1, 0.68, 0.28]).property("Transform").property("Opacity").setValue(42);
    rect("Bottle Cap", [1085, 252], [190, 80], [0.86, 0.68, 0.36]);
    rect("Label Plate", [1085, 526], [230, 150], [0.12, 0.09, 0.075]);
    text("Label Type", "NOIR 07", [1016, 540], 42, [0.95, 0.84, 0.58]);
    for (var i = 0; i < 13; i++) {
        var puff = ellipse("Fragrance Puff " + i, [690 + i * 52, 655 - (i % 4) * 92], [90 + i * 4, 34], [0.96, 0.78, 0.52]);
        puff.property("Transform").property("Opacity").setValueAtTime(0.7 + i * 0.08, 0);
        puff.property("Transform").property("Opacity").setValueAtTime(1.8 + i * 0.08, 34);
        puff.property("Transform").property("Position").setValueAtTime(1.8, [690 + i * 52, 655 - (i % 4) * 92]);
        puff.property("Transform").property("Position").setValueAtTime(6.2, [640 + i * 64, 570 - (i % 5) * 112]);
    }
    for (var r = 0; r < 4; r++) {
        var ring = ellipse("Macro Refraction Ring " + r, [1085, 520], [380 + r * 74, 380 + r * 74], [1, 0.86, 0.52]);
        ring.property("Transform").property("Opacity").expression = "14 + Math.sin(time * 3.2 - " + r + ") * 10;";
        ring.property("Transform").property("Scale").expression = "s = 86 + ((time * 20 + " + (r * 16) + ") % 38); [s, s];";
    }
    for (var s = 0; s < 12; s++) {
        var sparkle = ellipse("Specular Sparkle " + s, [922 + (s * 39) % 330, 285 + (s * 73) % 420], [12 + (s % 4) * 5, 12 + (s % 4) * 5], [1, 0.94, 0.68]);
        sparkle.property("Transform").property("Opacity").expression = "28 + Math.sin(time * 8 + " + s + ") * 24;";
    }
    var sweep = rect("Specular Bottle Sweep", [895, 310], [40, 520], [1, 0.96, 0.74]);
    sweep.property("Transform").property("Opacity").setValue(48);
    sweep.property("Transform").property("Position").setValueAtTime(1.3, [895, 310]);
    sweep.property("Transform").property("Position").setValueAtTime(5.8, [1275, 690]);
    text("Campaign Title", "PRIVATE RESERVE", [210, 390], 70, [0.97, 0.9, 0.76]);
    text("Campaign Subline", "amber / cedar / midnight iris", [215, 468], 30, [0.74, 0.6, 0.44]);
    rect("CTA Rule", [382, 572], [360, 7], [0.9, 0.68, 0.34]);
    text("CTA", "DISCOVER THE DROP", [240, 640], 28, [0.95, 0.8, 0.52]);
    app.endUndoGroup();
})();
