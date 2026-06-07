(function () {
    app.beginUndoGroup("AEFT Trailer Credits Builder");
    var comp = app.project.items.addComp("AEFT Trailer Credits Builder", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.015, 0.014, 0.013];

    function rect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var box = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        box.property("ADBE Vector Rect Size").setValue(size);
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
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    rect("Letterbox Top", [960, 76], [1920, 152], [0, 0, 0]);
    rect("Letterbox Bottom", [960, 1004], [1920, 152], [0, 0, 0]);
    var title = text("Main Film Title", "LAST SIGNAL", [960, 345], 112, [0.95, 0.92, 0.84]);
    title.property("Transform").property("Opacity").setValueAtTime(0.7, 0);
    title.property("Transform").property("Opacity").setValueAtTime(1.35, 100);
    title.property("Transform").property("Scale").setValueAtTime(1.35, [96, 96]);
    title.property("Transform").property("Scale").setValueAtTime(5.8, [106, 106]);

    var names = ["DIRECTED BY", "STARRING", "EDITED BY", "MUSIC BY", "VFX SUPERVISOR", "COLOR BY"];
    for (var i = 0; i < names.length; i++) {
        var x = 430 + (i % 3) * 260;
        var y = 560 + Math.floor(i / 3) * 92;
        var card = rect("Credit Plate " + i, [x, y], [216, 58], [0.08, 0.08, 0.075]);
        card.property("Transform").property("Position").setValueAtTime(1.6 + i * 0.12, [x - 130, y]);
        card.property("Transform").property("Position").setValueAtTime(2.25 + i * 0.12, [x, y]);
        text("Credit Role " + i, names[i], [x, y - 8], 22, [0.58, 0.12, 0.1]);
        text("Credit Name " + i, "A. VECTOR", [x, y + 24], 25, [0.9, 0.87, 0.76]);
    }

    for (var j = 0; j < 24; j++) {
        var tick = rect("Film Tick " + j, [154 + j * 70, 912], [26, 34], [0.9, 0.78, 0.55]);
        tick.property("Transform").property("Opacity").setValueAtTime(0.3 + j * 0.03, 0);
        tick.property("Transform").property("Opacity").setValueAtTime(1.1 + j * 0.03, 60);
    }
    var midFlash = rect("Mid Trailer Flash", [960, 512], [1920, 18], [0.9, 0.78, 0.55]);
    midFlash.property("Transform").property("Opacity").setValueAtTime(3.0, 0);
    midFlash.property("Transform").property("Opacity").setValueAtTime(3.3, 72);
    midFlash.property("Transform").property("Opacity").setValueAtTime(3.7, 0);
    midFlash.property("Transform").property("Scale").setValueAtTime(3.0, [35, 100]);
    midFlash.property("Transform").property("Scale").setValueAtTime(3.7, [100, 100]);
    var wipe = rect("Red Billing Wipe", [-340, 760], [520, 16], [0.72, 0.04, 0.03]);
    wipe.property("Transform").property("Position").setValueAtTime(2.4, [-340, 760]);
    wipe.property("Transform").property("Position").setValueAtTime(6.4, [2260, 760]);
    text("Billing Block", "IN ASSOCIATION WITH FRAME LABS // WORLD PREMIERE // FALL", [960, 816], 26, [0.72, 0.68, 0.58]);
    app.endUndoGroup();
})();
