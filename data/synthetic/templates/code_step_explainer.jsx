(function () {
    app.beginUndoGroup("AEFT Code Step Explainer");
    var comp = app.project.items.addComp("AEFT Code Step Explainer", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.025, 0.03, 0.04];

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

    addRect("Editor Panel", [960, 545], [1120, 620], [0.1, 0.12, 0.16]);
    addRect("Accent Rail Cyan", [412, 545], [36, 620], [0.0, 0.65, 1]);
    addRect("Accent Rail Amber", [1508, 545], [36, 620], [1, 0.58, 0.08]);
    var wash = addRect("Compiler Color Sweep", [-160, 545], [320, 760], [0.95, 0.14, 0.22]);
    wash.property("Transform").property("Rotation").setValue(-12);
    wash.property("Transform").property("Opacity").setValue(38);
    wash.property("Transform").property("Position").setValueAtTime(1.0, [-160, 545]);
    wash.property("Transform").property("Position").setValueAtTime(5.4, [2080, 545]);
    var highlight = addRect("Moving Highlight", [960, 390], [1040, 84], [0.16, 0.28, 0.58]);
    highlight.property("Transform").property("Position").setValueAtTime(0.6, [960, 390]);
    highlight.property("Transform").property("Position").setValueAtTime(2.4, [960, 500]);
    highlight.property("Transform").property("Position").setValueAtTime(4.2, [960, 610]);
    addText("Code Row 1", "var comp = app.project.items.addComp(...);", [520, 405], 34, [0.78, 0.9, 1]);
    addText("Code Row 2", "var layer = comp.layers.addText(title);", [520, 515], 34, [0.78, 1, 0.84]);
    addText("Code Row 3", "layer.property(\"Opacity\").setValueAtTime(...);", [520, 625], 34, [1, 0.86, 0.68]);
    var cursor = addRect("Blinking Cursor", [1220, 625], [14, 48], [0.2, 0.82, 1]);
    cursor.property("Transform").property("Opacity").expression = "Math.floor(time * 4) % 2 ? 20 : 100;";
    addText("Title", "Three steps to a renderable comp", [410, 230], 48, [0.95, 0.98, 1]);
    app.endUndoGroup();
})();
