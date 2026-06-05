(function () {
    app.beginUndoGroup("AEFT Kinetic Type Reveal");
    var comp = app.project.items.addComp("AEFT Kinetic Type Reveal", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.035, 0.043, 0.06];

    function addText(name, value, pos, size, color) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var textDoc = layer.property("Source Text").value;
        textDoc.fontSize = size;
        textDoc.fillColor = color;
        textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(textDoc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function addBar(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        var scale = layer.property("Transform").property("Scale");
        scale.setValueAtTime(delay, [0, 100]);
        scale.setValueAtTime(delay + 0.55, [100, 100]);
        return layer;
    }

    var title = addText("Headline", "MAKE MOTION", [960, 455], 118, [0.94, 0.96, 1]);
    var sub = addText("Subtitle", "Generated from a single JSX script", [960, 575], 38, [0.6, 0.78, 1]);
    addBar("Accent Bar Left", [600, 675], [380, 10], [0.18, 0.56, 1], 0.2);
    addBar("Accent Bar Center", [960, 715], [520, 10], [0.35, 0.9, 0.74], 0.35);
    addBar("Accent Bar Right", [1320, 675], [380, 10], [1, 0.42, 0.35], 0.5);

    title.property("Transform").property("Opacity").setValueAtTime(0, 0);
    title.property("Transform").property("Opacity").setValueAtTime(0.7, 100);
    title.property("Transform").property("Position").setValueAtTime(0, [960, 500]);
    title.property("Transform").property("Position").setValueAtTime(0.7, [960, 455]);
    sub.property("Transform").property("Opacity").setValueAtTime(0.45, 0);
    sub.property("Transform").property("Opacity").setValueAtTime(1.25, 100);
    app.endUndoGroup();
})();

