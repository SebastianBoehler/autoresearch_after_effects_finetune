(function () {
    app.beginUndoGroup("AEFT AI Network Node Explainer");
    var comp = app.project.items.addComp("AEFT AI Network Node Explainer", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.02, 0.025, 0.035];

    function rect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        shape.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function ellipse(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        shape.property("ADBE Vector Ellipse Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function text(name, value, pos, size, color) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    text("Header", "AGENT ROUTING GRAPH", [120, 145], 52, [0.86, 0.96, 1]);
    for (var g = 0; g < 12; g++) {
        var guideX = rect("Routing Guide X " + g, [260 + g * 125, 542], [1.5, 720], [0.06, 0.12, 0.18]);
        guideX.property("Transform").property("Opacity").expression = "18 + Math.sin(time * 2 + " + g + ") * 9;";
    }
    for (var h = 0; h < 7; h++) {
        var guideY = rect("Routing Guide Y " + h, [960, 250 + h * 95], [1360, 1.5], [0.06, 0.12, 0.18]);
        guideY.property("Transform").property("Opacity").expression = "16 + Math.cos(time * 1.7 + " + h + ") * 8;";
    }
    var xs = [410, 690, 960, 1230, 1510, 560, 1130, 1370];
    var ys = [300, 510, 320, 600, 380, 740, 785, 235];
    for (var i = 0; i < xs.length; i++) {
        var node = ellipse("Network Node " + i, [xs[i], ys[i]], [72, 72], [0.1, 0.76, 0.64]);
        node.property("Transform").property("Scale").expression = "s = 94 + Math.sin(time * 3.4 + " + i + ") * 12; [s, s];";
        text("Node Label " + i, "N" + i, [xs[i] - 18, ys[i] + 8], 22, [0.03, 0.06, 0.07]);
    }
    for (var j = 0; j < 10; j++) {
        var bar = rect("Connection Segment " + j, [520 + j * 96, 425 + (j % 3) * 92], [180, 6], [0.16, 0.42, 0.92]);
        bar.property("Transform").property("Rotation").setValue(-24 + (j % 4) * 18);
        bar.property("Transform").property("Opacity").setValueAtTime(0.5 + j * 0.1, 0);
        bar.property("Transform").property("Opacity").setValueAtTime(1.4 + j * 0.1, 70);
    }
    var pulse = ellipse("Routing Pulse", [410, 300], [46, 46], [1, 0.74, 0.18]);
    pulse.property("Transform").property("Position").setValueAtTime(1.1, [410, 300]);
    pulse.property("Transform").property("Position").setValueAtTime(3.2, [960, 320]);
    pulse.property("Transform").property("Position").setValueAtTime(5.4, [1230, 600]);
    pulse.property("Transform").property("Position").setValueAtTime(7.2, [1510, 380]);
    for (var p = 0; p < 7; p++) {
        var packet = ellipse("Packet Trail " + p, [410, 300], [22, 22], p % 2 ? [0.18, 0.9, 1] : [1, 0.74, 0.18]);
        packet.property("Transform").property("Position").setValueAtTime(1.0 + p * 0.18, [410, 300]);
        packet.property("Transform").property("Position").setValueAtTime(3.0 + p * 0.18, [960, 320]);
        packet.property("Transform").property("Position").setValueAtTime(5.2 + p * 0.18, [1230, 600]);
        packet.property("Transform").property("Opacity").setValueAtTime(0.8 + p * 0.18, 0);
        packet.property("Transform").property("Opacity").setValueAtTime(1.2 + p * 0.18, 82);
        packet.property("Transform").property("Opacity").setValueAtTime(6.2 + p * 0.18, 0);
    }
    for (var r = 0; r < 3; r++) {
        var focus = ellipse("Focus Ring " + r, [960, 320], [145 + r * 48, 145 + r * 48], [0.1, 0.62, 1]);
        focus.property("Transform").property("Opacity").expression = "22 + Math.sin(time * 4 - " + r + ") * 18;";
        focus.property("Transform").property("Scale").expression = "s = 82 + ((time * 24 + " + (r * 18) + ") % 54); [s, s];";
    }
    rect("Model State Card", [300, 850], [410, 160], [0.07, 0.1, 0.16]);
    text("Model State", "STATE: TOOL READY", [132, 842], 30, [0.8, 1, 0.9]);
    rect("Latency Meter", [1450, 850], [360, 36], [0.12, 0.18, 0.28]);
    var fill = rect("Latency Fill", [1325, 850], [96, 36], [0.2, 0.84, 1]);
    fill.property("Transform").property("Scale").setValueAtTime(1.0, [0, 100]);
    fill.property("Transform").property("Scale").setValueAtTime(7.0, [300, 100]);
    text("Latency Label", "LATENCY 42MS", [1312, 920], 28, [0.56, 0.8, 1]);
    app.endUndoGroup();
})();
