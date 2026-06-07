(function () {
    app.beginUndoGroup("AEFT Command Palette Toolkit HUD");
    var comp = app.project.items.addComp("AEFT Command Palette Toolkit HUD", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.012, 0.016, 0.024];

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

    function addText(name, value, pos, size, color, justify) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = justify || ParagraphJustification.LEFT_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    addRect("Workspace Grid", [960, 540], [1680, 820], [0.025, 0.035, 0.052]);
    var palette = addRect("Command Palette", [960, 385], [900, 450], [0.055, 0.07, 0.105]);
    palette.property("Transform").property("Scale").setValueAtTime(0.2, [86, 86]);
    palette.property("Transform").property("Scale").setValueAtTime(0.75, [100, 100]);
    addText("Search Prompt", "command frame: add easing preset", [590, 225], 36, [0.92, 0.98, 1]);

    var commands = ["Animate selected layers", "Align anchors to center", "Apply icon grid", "Chain presets", "Export Lottie preview"];
    for (var i = 0; i < commands.length; i++) {
        var y = 300 + i * 64;
        var row = addRect("Command Row " + i, [960, y], [800, 48], i === 1 ? [0.1, 0.34, 0.9] : [0.075, 0.09, 0.13]);
        row.property("Transform").property("Opacity").setValueAtTime(0.55 + i * 0.11, 0);
        row.property("Transform").property("Opacity").setValueAtTime(0.95 + i * 0.11, 100);
        addText("Command Text " + i, commands[i], [600, y + 11], 24, [0.88, 0.94, 1]);
        addText("Command Shortcut " + i, "cmd+" + (i + 1), [1285, y + 11], 20, [0.48, 0.78, 1]);
    }

    addRect("Icon Browser", [1410, 720], [360, 250], [0.045, 0.055, 0.08]);
    for (var j = 0; j < 12; j++) {
        var x = 1280 + (j % 4) * 86;
        var yy = 645 + Math.floor(j / 4) * 62;
        var icon = addRect("Imported Icon Tile " + j, [x, yy], [42, 42], [0.12, 0.22 + (j % 3) * 0.12, 0.95]);
        icon.property("Transform").property("Rotation").setValueAtTime(1.2 + j * 0.04, -12);
        icon.property("Transform").property("Rotation").setValueAtTime(2.0 + j * 0.04, 0);
    }
    addRect("Execution Progress", [960, 890], [0, 12], [0.24, 0.9, 0.72]).property("Transform").property("Scale").setValueAtTime(0.5, [0, 100]);
    var progress = addRect("Execution Progress Fill", [960, 890], [720, 12], [0.24, 0.9, 0.72]);
    progress.property("Transform").property("Scale").setValueAtTime(2.0, [0, 100]);
    progress.property("Transform").property("Scale").setValueAtTime(5.2, [100, 100]);
    addText("Status Text", "12 layers tagged / 5 tools chained / preview ready", [600, 950], 28, [0.7, 0.84, 1]);
    app.endUndoGroup();
})();
