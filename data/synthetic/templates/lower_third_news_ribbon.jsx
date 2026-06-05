(function () {
    app.beginUndoGroup("AEFT Lower Third News Ribbon");
    var comp = app.project.items.addComp("AEFT Lower Third News Ribbon", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.03, 0.04, 0.055];

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

    var plate = addRect("Sliding Nameplate", [650, 820], [980, 150], [0.08, 0.16, 0.28]);
    var tag = addRect("Section Tag", [205, 752], [270, 54], [0.95, 0.2, 0.16]);
    var line = addRect("Animated Underline", [650, 910], [980, 8], [0.2, 0.72, 1]);
    plate.property("Transform").property("Position").setValueAtTime(0, [-520, 820]);
    plate.property("Transform").property("Position").setValueAtTime(0.75, [650, 820]);
    tag.property("Transform").property("Position").setValueAtTime(0.1, [-160, 752]);
    tag.property("Transform").property("Position").setValueAtTime(0.85, [205, 752]);
    line.property("Transform").property("Scale").setValueAtTime(0.6, [0, 100]);
    line.property("Transform").property("Scale").setValueAtTime(1.2, [100, 100]);
    addText("Section Text", "UPDATE", [122, 765], 28, [1, 1, 1]);
    addText("Name Text", "After Effects Autoresearch", [210, 824], 50, [0.95, 0.98, 1]);
    addText("Headline Text", "Synthetic scripts with live verification hooks", [210, 875], 29, [0.65, 0.78, 0.92]);
    app.endUndoGroup();
})();

