(function () {
    app.beginUndoGroup("AEFT Science Molecule Explainer");
    var comp = app.project.items.addComp("AEFT Science Molecule Explainer", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.94, 0.97, 0.98];

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

    addRect("Lab Header", [960, 112], [1660, 104], [0.04, 0.16, 0.22]);
    addText("Title", "Molecule binding sequence", [180, 130], 50, [0.94, 0.98, 1]);
    var scan = addRect("Microscope Scan", [360, 560], [430, 720], [0.04, 0.72, 0.86]);
    scan.property("Transform").property("Opacity").setValue(34);
    scan.property("Transform").property("Position").setValueAtTime(0.7, [360, 560]);
    scan.property("Transform").property("Position").setValueAtTime(6.6, [1480, 560]);
    var catalyst = addRect("Catalyst Energy Sweep", [300, 870], [320, 76], [1, 0.54, 0.1]);
    catalyst.property("Transform").property("Opacity").setValue(42);
    catalyst.property("Transform").property("Position").setValueAtTime(1.2, [300, 870]);
    catalyst.property("Transform").property("Position").setValueAtTime(6.4, [1520, 870]);
    var atoms = [["A", 720, 520, 70], ["B", 960, 380, 58], ["C", 1180, 555, 66], ["D", 940, 720, 50]];
    for (var i = 0; i < atoms.length; i++) {
        var atom = addCircle("Atom " + atoms[i][0], [atoms[i][1], atoms[i][2]], atoms[i][3], [0.05, 0.44 + i * 0.1, 0.9 - i * 0.08]);
        atom.property("Transform").property("Scale").expression = "p = 100 + Math.sin(time * Math.PI * 2 + " + i + ") * 5; [p, p];";
        addText("Atom Label " + atoms[i][0], atoms[i][0], [atoms[i][1] - 12, atoms[i][2] + 14], 36, [1, 1, 1]);
    }
    var bond1 = addRect("Bond A B", [840, 450], [280, 12], [0.13, 0.22, 0.28]);
    bond1.property("Transform").property("Rotation").setValue(-30);
    var bond2 = addRect("Bond B C", [1070, 470], [280, 12], [0.13, 0.22, 0.28]);
    bond2.property("Transform").property("Rotation").setValue(38);
    var bond3 = addRect("Bond C D", [1065, 640], [260, 12], [0.13, 0.22, 0.28]);
    bond3.property("Transform").property("Rotation").setValue(-34);
    addRect("Annotation Card", [1540, 610], [390, 250], [1, 1, 1]);
    addText("Step Label", "STEP 03", [1390, 540], 32, [0.02, 0.46, 0.7]);
    addText("Step Copy", "Active site aligns\\nwith catalyst orbit.", [1390, 610], 34, [0.08, 0.12, 0.16]);
    app.endUndoGroup();
})();
