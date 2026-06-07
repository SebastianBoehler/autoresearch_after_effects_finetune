(function () {
    app.beginUndoGroup("AEFT Liquid Logo Bloom");
    var comp = app.project.items.addComp("AEFT Liquid Logo Bloom", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.02, 0.018, 0.03];

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

    var colors = [[0.0, 0.8, 1], [1, 0.18, 0.46], [1, 0.68, 0.12]];
    var cyanWash = addRect("Cyan Liquid Wash", [260, 540], [260, 820], [0.0, 0.62, 1]);
    cyanWash.property("Transform").property("Opacity").setValue(42);
    cyanWash.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.2) * 44, Math.cos(time * 0.9) * 18];";
    var magentaWash = addRect("Magenta Liquid Wash", [1660, 540], [260, 820], [1, 0.12, 0.46]);
    magentaWash.property("Transform").property("Opacity").setValue(42);
    magentaWash.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.1 + 2) * 44, Math.cos(time * 0.8 + 2) * 18];";
    for (var i = 0; i < 9; i++) {
        var angle = i * Math.PI * 2 / 9;
        var blob = addCircle("Liquid Blob " + i, [960, 540], 72 + i * 4, colors[i % 3]);
        blob.property("Transform").property("Opacity").setValue(72);
        blob.property("Transform").property("Position").setValueAtTime(0.4, [960, 540]);
        blob.property("Transform").property("Position").setValueAtTime(2.0, [960 + Math.cos(angle) * 310, 540 + Math.sin(angle) * 190]);
        blob.property("Transform").property("Scale").setValueAtTime(2.0, [100, 100]);
        blob.property("Transform").property("Scale").setValueAtTime(4.8, [20, 20]);
    }
    for (var j = 0; j < 12; j++) {
        var orbit = addCircle("Orbit Droplet " + j, [960, 540], 18 + (j % 3) * 6, colors[j % 3]);
        orbit.property("Transform").property("Opacity").setValue(54);
        orbit.property("Transform").property("Position").expression =
            "a=time*" + (1.2 + j * 0.08) + "+" + j + "; [960+Math.cos(a)*" + (250 + j * 14) + ", 540+Math.sin(a)*" + (120 + j * 8) + "];";
    }
    for (var r = 0; r < 7; r++) {
        var ripple = addCircle("Liquid Ripple Ring " + r, [960, 540], 125 + r * 38, colors[r % 3]);
        ripple.property("Transform").property("Opacity").expression = "18 + Math.sin(time * " + (1.5 + r * 0.11) + " + " + r + ") * 12;";
        ripple.property("Transform").property("Scale").expression = "s = 86 + Math.sin(time * " + (1.1 + r * 0.08) + " + " + r + ") * 16; [s, s];";
    }
    var mark = addRect("Logo Mark", [960, 540], [260, 260], [0.94, 0.98, 1]);
    mark.property("Transform").property("Rotation").setValueAtTime(1.8, -45);
    mark.property("Transform").property("Rotation").setValueAtTime(3.0, 0);
    mark.property("Transform").property("Scale").setValueAtTime(1.8, [20, 20]);
    mark.property("Transform").property("Scale").setValueAtTime(3.0, [100, 100]);
    mark.property("Transform").property("Scale").setValueAtTime(5.5, [108, 108]);
    mark.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.7) * 12, Math.cos(time * 1.3) * 10];";
    var ribbon = addRect("Liquid Reflection Sweep", [-160, 540], [88, 780], [1, 1, 1]);
    ribbon.property("Transform").property("Opacity").setValue(26);
    ribbon.property("Transform").property("Rotation").setValue(-16);
    ribbon.property("Transform").property("Position").setValueAtTime(2.2, [-160, 540]);
    ribbon.property("Transform").property("Position").setValueAtTime(5.6, [2080, 540]);
    for (var p = 0; p < 8; p++) {
        var prism = addRect("Late Liquid Prism " + p, [620 + p * 92, 700 + (p % 3) * 42], [72, 8], colors[p % 3]);
        prism.property("Transform").property("Opacity").expression = "24 + Math.abs(Math.sin(time * " + (2.1 + p * 0.17) + " + " + p + ")) * 54;";
        prism.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.4 + p * 0.09) + ") * 36, Math.cos(time * " + (1.8 + p * 0.08) + ") * 22];";
        prism.property("Transform").property("Rotation").expression = "Math.sin(time * " + (1.6 + p * 0.11) + ") * 24;";
    }
    for (var q = 0; q < 6; q++) {
        var drop = addCircle("Outro Micro Drop " + q, [760 + q * 82, 300 + (q % 2) * 420], 12 + (q % 3) * 5, colors[(q + 1) % 3]);
        drop.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.9 + q * 0.12) + " + " + q + ") * 52, Math.cos(time * " + (1.3 + q * 0.1) + ") * 38];";
        drop.property("Transform").property("Scale").expression = "s = 80 + Math.abs(Math.sin(time * " + (2.4 + q * 0.14) + ")) * 42; [s, s];";
    }
    for (var h = 0; h < 9; h++) {
        var halo = addRect("Outro Halo Sweep " + h, [500 + h * 115, 410 + (h % 3) * 92], [80, 9], colors[h % 3]);
        halo.property("Transform").property("Position").setValueAtTime(4.2 + h * 0.05, [500 + h * 115, 410 + (h % 3) * 92]);
        halo.property("Transform").property("Position").setValueAtTime(5.9, [430 + h * 128, 360 + (h % 2) * 230]);
        halo.property("Transform").property("Opacity").expression = "24 + Math.abs(Math.sin(time * " + (2.6 + h * 0.12) + " + " + h + ")) * 56;";
        halo.property("Transform").property("Rotation").expression = "Math.sin(time * " + (1.9 + h * 0.09) + ") * 28;";
    }
    var brand = addText("Brand Name", "BLOOMLAB", [960, 780], 66, [0.95, 0.98, 1]);
    brand.property("Transform").property("Position").expression = "value + [0, Math.sin(time * 1.2) * 10];";
    var tagline = addText("Brand Tagline", "liquid identity system", [960, 840], 28, [0.28, 0.86, 1]);
    tagline.property("Transform").property("Opacity").expression = "72 + Math.sin(time * 2.2) * 18;";
    var exitGlint = addRect("Final Logo Glint", [-140, 610], [90, 420], [1, 1, 1]);
    exitGlint.property("Transform").property("Rotation").setValue(-18);
    exitGlint.property("Transform").property("Opacity").setValue(24);
    exitGlint.property("Transform").property("Position").setValueAtTime(4.7, [-140, 610]);
    exitGlint.property("Transform").property("Position").setValueAtTime(5.95, [2060, 420]);
    app.endUndoGroup();
})();
