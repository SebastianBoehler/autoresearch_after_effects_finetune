(function () {
    app.beginUndoGroup("AEFT Loop Badge Boomerang");
    var comp = app.project.items.addComp("AEFT Loop Badge Boomerang", 1080, 1080, 1, 6, 30);
    comp.bgColor = [0.055, 0.045, 0.07];

    function addEllipse(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function addStrokeEllipse(name, pos, size, color, width) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue(size);
        var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        stroke.property("ADBE Vector Stroke Color").setValue(color);
        stroke.property("ADBE Vector Stroke Width").setValue(width);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function addText(name, value, pos, size, color) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    addStrokeEllipse("Outer Halo", [540, 540], [760, 760], [0.34, 0.18, 0.68], 18).property("Transform").property("Rotation").expression = "time * 18;";
    addStrokeEllipse("Middle Ring", [540, 540], [610, 610], [0.06, 0.58, 0.95], 14).property("Transform").property("Opacity").setValue(68);
    var badge = addEllipse("Core Badge", [540, 540], [330, 330], [1, 0.76, 0.08]);
    badge.property("Transform").property("Scale").setValueAtTime(0, [88, 88]);
    badge.property("Transform").property("Scale").setValueAtTime(1.5, [108, 108]);
    badge.property("Transform").property("Scale").setValueAtTime(3, [88, 88]);
    badge.property("Transform").property("Scale").expression = "loopOut('cycle');";
    for (var i = 0; i < 16; i++) {
        var angle = i * Math.PI * 2 / 16;
        var dot = addEllipse("Orbit Dot " + i, [540 + Math.cos(angle) * 340, 540 + Math.sin(angle) * 340], [34, 34], [0.92, 0.96, 1]);
        dot.property("Transform").property("Scale").expression = "v = 70 + Math.sin(time * Math.PI * 2 + " + i + ") * 30; [v, v];";
        dot.property("Transform").property("Opacity").expression = "50 + Math.sin(time * Math.PI * 2 + " + i + ") * 35;";
    }
    addText("Brand Mark", "LOOP", [540, 535], 94, [0.08, 0.06, 0.08]);
    addText("Badge Label", "PING PONG MOTION", [540, 650], 28, [0.1, 0.08, 0.1]);
    var sweep = addStrokeEllipse("Sweep Pulse", [540, 540], [180, 180], [0.35, 0.95, 0.72], 16);
    sweep.property("Transform").property("Scale").setValueAtTime(0, [0, 0]);
    sweep.property("Transform").property("Scale").setValueAtTime(3, [360, 360]);
    sweep.property("Transform").property("Opacity").setValueAtTime(0, 70);
    sweep.property("Transform").property("Opacity").setValueAtTime(3, 0);
    sweep.property("Transform").property("Scale").expression = "loopOut('cycle');";
    sweep.property("Transform").property("Opacity").expression = "loopOut('cycle');";
    app.endUndoGroup();
})();
