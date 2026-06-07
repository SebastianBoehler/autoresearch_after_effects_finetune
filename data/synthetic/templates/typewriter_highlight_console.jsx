(function () {
    app.beginUndoGroup("AEFT Typewriter Highlight Console");
    var comp = app.project.items.addComp("AEFT Typewriter Highlight Console", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.012, 0.014, 0.018];

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

    function addText(name, value, pos, size, color, delay) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.font = "Courier";
        doc.justification = ParagraphJustification.LEFT_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.28, 100);
        return layer;
    }

    addRect("Console Window", [960, 540], [1320, 720], [0.025, 0.032, 0.045]);
    addRect("Console Header", [960, 205], [1320, 58], [0.07, 0.09, 0.12]);
    addText("Console Title", "TYPE PANEL / MONO HIGHLIGHT / CURSOR", [360, 222], 24, [0.72, 0.84, 1], 0.1);
    var lines = ["init text layer", "split words into spans", "apply underline preset", "track cursor to sourceRect", "export clean mogrt"];
    for (var i = 0; i < lines.length; i++) {
        var y = 320 + i * 86;
        var highlight = addRect("Typing Highlight " + i, [720, y - 9], [0, 46], [0.15, 0.42, 0.95]);
        highlight.property("Transform").property("Scale").setValueAtTime(0.55 + i * 0.48, [0, 100]);
        highlight.property("Transform").property("Scale").setValueAtTime(1.2 + i * 0.48, [100, 100]);
        addText("Typed Line " + i, "> " + lines[i], [370, y], 34, [0.86, 0.94, 0.88], 0.45 + i * 0.48);
        var underline = addRect("Underline " + i, [680, y + 22], [470, 4], [0.28, 0.9, 0.68]);
        underline.property("Transform").property("Scale").setValueAtTime(1.0 + i * 0.48, [0, 100]);
        underline.property("Transform").property("Scale").setValueAtTime(1.7 + i * 0.48, [100, 100]);
    }
    var cursor = addRect("Blinking Cursor", [1240, 660], [16, 58], [0.9, 1, 0.72]);
    cursor.property("Transform").property("Opacity").expression = "Math.floor(time * 4) % 2 ? 100 : 15;";
    cursor.property("Transform").property("Position").setValueAtTime(0.8, [430, 320]);
    cursor.property("Transform").property("Position").setValueAtTime(3.2, [935, 664]);
    cursor.property("Transform").property("Position").setValueAtTime(6.6, [1265, 728]);
    var status = addRect("Late Status Panel", [1310, 815], [460, 130], [0.045, 0.08, 0.08]);
    status.property("Transform").property("Scale").setValueAtTime(4.8, [0, 100]);
    status.property("Transform").property("Scale").setValueAtTime(5.5, [100, 100]);
    addText("Late Status Copy", "5 text boxes synced\\n0 overflow warnings", [1120, 790], 28, [0.62, 1, 0.82], 5.0);
    app.endUndoGroup();
})();
