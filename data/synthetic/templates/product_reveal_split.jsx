(function () {
    app.beginUndoGroup("AEFT Product Reveal Split");
    var comp = app.project.items.addComp("AEFT Product Reveal Split", 1920, 1080, 1, 5, 30);
    comp.bgColor = [0.08, 0.08, 0.08];

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

    var left = addRect("Left Color Panel", [480, 540], [960, 1080], [0.06, 0.14, 0.24]);
    var right = addRect("Right Color Panel", [1440, 540], [960, 1080], [0.9, 0.94, 0.98]);
    left.property("Transform").property("Position").setValueAtTime(0, [-520, 540]);
    left.property("Transform").property("Position").setValueAtTime(0.8, [480, 540]);
    right.property("Transform").property("Position").setValueAtTime(0, [2440, 540]);
    right.property("Transform").property("Position").setValueAtTime(0.8, [1440, 540]);
    var product = addRect("Product Placeholder", [1320, 545], [420, 520], [1, 1, 1]);
    product.property("Transform").property("Scale").setValueAtTime(0.7, [70, 70]);
    product.property("Transform").property("Scale").setValueAtTime(1.4, [100, 100]);
    addText("Title", "SCRIPTED MOTION", [300, 445], 74, [0.94, 0.98, 1]);
    addText("Subtitle", "A ready comp from generated JSX", [305, 525], 34, [0.58, 0.78, 1]);
    addRect("CTA Chip", [395, 635], [280, 64], [0.18, 0.74, 0.62]);
    addText("CTA Text", "RENDER READY", [310, 648], 28, [0.02, 0.06, 0.07]);
    app.endUndoGroup();
})();

