(function () {
    app.beginUndoGroup("AEFT Orbiting Concept Map");
    var comp = app.project.items.addComp("AEFT Orbiting Concept Map", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.02, 0.025, 0.035];

    function addCircle(name, pos, radius, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([radius * 2, radius * 2]);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function addText(name, value, pos, size) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = [0.92, 0.95, 1];
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    addCircle("Core Topic Circle", [960, 540], 145, [0.08, 0.35, 0.72]);
    addText("Core Topic", "MODEL", [960, 555], 54);
    var names = ["DATA", "EVAL", "ADAPTER", "RENDER"];
    for (var i = 0; i < names.length; i++) {
        var angle = i * Math.PI / 2;
        var x = 960 + Math.cos(angle) * 385;
        var y = 540 + Math.sin(angle) * 240;
        var node = addCircle("Node " + names[i], [x, y], 78, [0.1, 0.72, 0.62]);
        addText("Label " + names[i], names[i], [x, y + 12], 30);
        node.property("Transform").property("Position").expression =
            "origin = [960, 540]; r = length(value - origin); a = Math.atan2(value[1]-origin[1], value[0]-origin[0]) + time * 0.35; origin + [Math.cos(a)*r, Math.sin(a)*r*0.62];";
    }
    var comet = addCircle("Orbit Comet", [575, 390], 96, [1, 0.42, 0.12]);
    comet.property("Transform").property("Opacity").setValue(72);
    comet.property("Transform").property("Position").setValueAtTime(0.6, [575, 390]);
    comet.property("Transform").property("Position").setValueAtTime(2.3, [1345, 390]);
    comet.property("Transform").property("Position").setValueAtTime(4.0, [1345, 690]);
    comet.property("Transform").property("Position").setValueAtTime(5.7, [575, 690]);
    for (var j = 0; j < 4; j++) {
        var connector = comp.layers.addShape();
        connector.name = "Connector " + (j + 1);
        connector.property("Transform").property("Opacity").setValueAtTime(j * 0.2, 0);
        connector.property("Transform").property("Opacity").setValueAtTime(0.8 + j * 0.2, 45);
    }
    app.endUndoGroup();
})();
