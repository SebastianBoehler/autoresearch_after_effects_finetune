(function () {
    app.beginUndoGroup("AEFT Split Screen Launch Opener");
    var comp = app.project.items.addComp("AEFT Split Screen Launch Opener", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.03, 0.035, 0.045];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0], pos[1] + 90]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.45, pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.2, 100);
        return layer;
    }

    function addText(name, value, pos, size, color, delay) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.25, 100);
        return layer;
    }

    var panels = [
        ["Hero Panel", 410, 430, 430, 360, [0.06, 0.28, 0.5]],
        ["Feature Panel", 1110, 300, 360, 210, [0.9, 0.28, 0.18]],
        ["Detail Panel", 1450, 690, 360, 300, [0.1, 0.65, 0.46]],
        ["Ticker Panel", 730, 845, 540, 130, [1, 0.76, 0.12]]
    ];
    for (var i = 0; i < panels.length; i++) {
        addRect(panels[i][0], [panels[i][1], panels[i][2]], [panels[i][3], panels[i][4]], panels[i][5], 0.3 + i * 0.22);
        addRect("Media Shine " + i, [panels[i][1] - 80, panels[i][2]], [80, panels[i][4]], [1, 1, 1], 1.0 + i * 0.18).property("Transform").property("Rotation").setValue(-18);
    }
    addText("Launch Title", "NOVA KIT", [960, 190], 104, [0.94, 0.98, 1], 0.6);
    addText("Launch Subtitle", "MULTISCREEN PRODUCT OPENER", [960, 280], 34, [0.56, 0.78, 1], 1.0);
    addRect("Logo Bug", [1700, 170], [82, 82], [1, 0.76, 0.12], 1.2);
    addText("Logo Letter", "N", [1700, 190], 42, [0.04, 0.05, 0.07], 1.28);
    var chips = ["FAST SETUP", "NO PLUGINS", "COLOR CONTROLS", "4K READY"];
    for (var j = 0; j < chips.length; j++) {
        addRect("Feature Chip " + j, [500 + j * 310, 965], [230, 58], [0.08, 0.1, 0.14], 2.0 + j * 0.15);
        addText("Feature Text " + j, chips[j], [500 + j * 310, 983], 24, [0.92, 0.96, 1], 2.08 + j * 0.15);
    }
    for (var k = 0; k < 10; k++) {
        var signal = addRect("Panel Signal Tick " + k, [260 + k * 145, 735 + (k % 2) * 48], [82, 8], [0.56, 0.78, 1], 1.1 + k * 0.04);
        signal.property("Transform").property("Opacity").expression = "36 + Math.sin(time * " + (2.0 + k * 0.1) + " + " + k + ") * 24;";
        signal.property("Transform").property("Scale").expression = "w = 58 + Math.abs(Math.sin(time * " + (1.5 + k * 0.08) + " + " + k + ")) * 42; [w, 100];";
    }
    for (var m = 0; m < 7; m++) {
        var gutter = addRect("Animated Gutter Marker " + m, [360 + m * 205, 560 + (m % 3) * 74], [78, 8], [0.98, 0.95, 0.7], 2.8 + m * 0.06);
        gutter.property("Transform").property("Position").setValueAtTime(2.8 + m * 0.06, [360 + m * 205, 560 + (m % 3) * 74]);
        gutter.property("Transform").property("Position").setValueAtTime(6.6, [420 + m * 172, 520 + (m % 2) * 86]);
        gutter.property("Transform").property("Opacity").expression = "30 + Math.abs(Math.sin(time * " + (2.4 + m * 0.13) + " + " + m + ")) * 42;";
    }
    var wipe = addRect("Final Wipe", [-160, 540], [250, 1280], [0.98, 0.95, 0.7], 4.9);
    wipe.property("Transform").property("Rotation").setValue(-16);
    wipe.property("Transform").property("Position").setValueAtTime(4.9, [-160, 540]);
    wipe.property("Transform").property("Position").setValueAtTime(6.4, [2080, 540]);
    app.endUndoGroup();
})();
