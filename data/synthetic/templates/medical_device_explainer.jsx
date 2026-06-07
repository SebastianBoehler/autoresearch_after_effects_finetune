(function () {
    app.beginUndoGroup("AEFT Medical Device Explainer");
    var comp = app.project.items.addComp("AEFT Medical Device Explainer", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.93, 0.97, 0.98];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0], pos[1] + 60]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.45, pos);
        return layer;
    }

    function addCircle(name, pos, radius, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([radius * 2, radius * 2]);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Scale").setValueAtTime(delay, [0, 0]);
        layer.property("Transform").property("Scale").setValueAtTime(delay + 0.35, [100, 100]);
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

    addText("Header", "CLINICAL DEVICE FLOW", [960, 115], 58, [0.04, 0.16, 0.22], 0.2);
    addRect("Patient Monitor", [500, 520], [620, 520], [0.05, 0.12, 0.16], 0.4);
    for (var i = 0; i < 18; i++) {
        var pulse = addRect("Heartbeat Segment " + i, [230 + i * 32, 520 + (i % 4 === 0 ? -42 : 18)], [46, 8], [0.22, 1, 0.68], 0.8 + i * 0.03);
        pulse.property("Transform").property("Opacity").expression = "55 + Math.sin(time * 5 + " + i + ") * 35;";
    }
    var heartSweep = addRect("Heartbeat Sweep", [205, 520], [70, 320], [0.22, 1, 0.68], 0.8);
    heartSweep.property("Transform").property("Opacity").setValue(34);
    heartSweep.property("Transform").property("Position").setValueAtTime(0.8, [205, 520]);
    heartSweep.property("Transform").property("Position").setValueAtTime(6.8, [780, 520]);
    addRect("Device Body", [1125, 560], [300, 500], [0.86, 0.9, 0.92], 0.7);
    addCircle("Device Dial", [1125, 430], 64, [0.12, 0.58, 0.82], 1.0);
    addCircle("Sensor Patch", [1125, 620], 48, [0.14, 0.82, 0.64], 1.15);
    var scan = addRect("Dose Scan", [1125, 360], [260, 18], [0.12, 0.58, 0.82], 1.6);
    scan.property("Transform").property("Position").setValueAtTime(1.6, [1125, 360]);
    scan.property("Transform").property("Position").setValueAtTime(6.6, [1125, 760]);
    var steps = ["CHECK", "SYNC", "DELIVER", "CONFIRM"];
    for (var j = 0; j < steps.length; j++) {
        addCircle("Step Dot " + j, [1460, 360 + j * 120], 28, [0.12, 0.58, 0.82], 1.2 + j * 0.35);
        addText("Step Label " + j, steps[j], [1600, 374 + j * 120], 30, [0.04, 0.16, 0.22], 1.35 + j * 0.35);
        var stepFill = addRect("Step Fill " + j, [1515, 390 + j * 120], [170, 12], [0.14, 0.82, 0.64], 1.5 + j * 0.3);
        stepFill.property("Transform").property("Scale").setValueAtTime(1.5 + j * 0.3, [0, 100]);
        stepFill.property("Transform").property("Scale").setValueAtTime(4.2 + j * 0.3, [100, 100]);
    }
    for (var b = 0; b < 6; b++) {
        var bubble = addCircle("Clinical Bubble " + b, [740 + b * 112, 245 + (b % 2) * 610], 20, [0.12, 0.58, 0.82], 2.0 + b * 0.1);
        bubble.property("Transform").property("Position").expression =
            "value + [Math.sin(time * " + (1.4 + b * 0.12) + ") * 26, Math.cos(time * " + (1.0 + b * 0.08) + ") * 18];";
    }
    addText("Footer", "LIVE VITALS / SMART DOSING / SAFE LOOP", [960, 965], 34, [0.04, 0.16, 0.22], 2.8);
    app.endUndoGroup();
})();
