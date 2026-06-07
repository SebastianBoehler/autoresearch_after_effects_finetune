(function () {
    app.beginUndoGroup("AEFT Photo Grid Slideshow");
    var comp = app.project.items.addComp("AEFT Photo Grid Slideshow", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.94, 0.92, 0.86];

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

    addText("Title", "Weekend field notes", [120, 150], 60, [0.08, 0.08, 0.1]);
    addText("Subtitle", "grid slideshow / six placeholders", [124, 205], 28, [0.46, 0.38, 0.28]);
    var colors = [[0.08, 0.28, 0.54], [0.85, 0.32, 0.16], [0.08, 0.48, 0.36], [0.64, 0.18, 0.48], [0.94, 0.66, 0.12], [0.15, 0.18, 0.25]];
    for (var i = 0; i < 6; i++) {
        var col = i % 3;
        var row = Math.floor(i / 3);
        var x = 420 + col * 520;
        var y = 420 + row * 310;
        var frame = addRect("Photo Frame " + i, [x, y], [410, 245], [1, 1, 1]);
        frame.property("Transform").property("Position").setValueAtTime(0.3 + i * 0.16, [x, y + 90]);
        frame.property("Transform").property("Position").setValueAtTime(0.95 + i * 0.16, [x, y]);
        var image = addRect("Photo Placeholder " + i, [x, y - 10], [370, 195], colors[i]);
        image.property("Transform").property("Scale").setValueAtTime(1.0 + i * 0.16, [100, 100]);
        image.property("Transform").property("Scale").setValueAtTime(7.5, [116, 116]);
    }
    var focus = addRect("Focus Outline", [420, 420], [520, 340], [0.02, 0.12, 0.2]);
    focus.property("Transform").property("Opacity").setValue(34);
    focus.property("Transform").property("Position").setValueAtTime(2.0, [420, 420]);
    focus.property("Transform").property("Position").setValueAtTime(4.0, [940, 420]);
    focus.property("Transform").property("Position").setValueAtTime(6.0, [1460, 730]);
    var ribbon = addRect("Slideshow Ribbon Sweep", [-200, 860], [360, 150], [0.88, 0.24, 0.16]);
    ribbon.property("Transform").property("Opacity").setValue(42);
    ribbon.property("Transform").property("Position").setValueAtTime(2.2, [-200, 860]);
    ribbon.property("Transform").property("Position").setValueAtTime(6.8, [2120, 860]);
    app.endUndoGroup();
})();
