(function () {
    app.beginUndoGroup("AEFT Radial Countdown Timer");
    var comp = app.project.items.addComp("AEFT Radial Countdown Timer", 1080, 1080, 1, 5, 30);
    comp.bgColor = [0.015, 0.018, 0.026];

    function addRing(name, radius, color, width) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([radius * 2, radius * 2]);
        var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        stroke.property("ADBE Vector Stroke Color").setValue(color);
        stroke.property("ADBE Vector Stroke Width").setValue(width);
        layer.property("Transform").property("Position").setValue([540, 540]);
        return group;
    }

    addRing("Background Ring", 310, [0.12, 0.16, 0.22], 22);
    var progress = addRing("Progress Ring", 310, [0.18, 0.78, 1], 28);
    var trim = progress.property("Contents").addProperty("ADBE Vector Filter - Trim");
    trim.property("ADBE Vector Trim End").setValueAtTime(0, 100);
    trim.property("ADBE Vector Trim End").setValueAtTime(5, 0);
    var number = comp.layers.addText("05");
    number.name = "Countdown Number";
    var doc = number.property("Source Text").value;
    doc.fontSize = 180;
    doc.fillColor = [0.95, 0.98, 1];
    doc.justification = ParagraphJustification.CENTER_JUSTIFY;
    number.property("Source Text").setValue(doc);
    number.property("Transform").property("Position").setValue([540, 585]);
    number.property("Transform").property("Scale").expression = "p = 100 + Math.sin(time * Math.PI * 2) * 3; [p, p];";
    var label = comp.layers.addText("SECONDS");
    label.name = "Countdown Label";
    label.property("Transform").property("Position").setValue([540, 700]);
    app.endUndoGroup();
})();

