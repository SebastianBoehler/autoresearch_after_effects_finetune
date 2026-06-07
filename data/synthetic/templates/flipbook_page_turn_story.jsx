(function () {
    app.beginUndoGroup("AEFT Flipbook Page Turn Story");
    var comp = app.project.items.addComp("AEFT Flipbook Page Turn Story", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.11, 0.085, 0.065];

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

    var table = addRect("Table Surface", [960, 660], [1640, 640], [0.21, 0.15, 0.1]);
    table.property("Transform").property("Opacity").expression = "92 + Math.sin(time * 1.6) * 5;";
    addRect("Book Shadow", [990, 705], [890, 360], [0.04, 0.03, 0.025]).property("Transform").property("Opacity").setValue(42);
    var spine = addRect("Book Spine", [960, 560], [32, 520], [0.2, 0.17, 0.13]);
    spine.threeDLayer = true;
    var left = addRect("Left Page Stack", [735, 560], [430, 520], [0.92, 0.88, 0.78]);
    left.threeDLayer = true;
    var right = addRect("Right Page Stack", [1185, 560], [430, 520], [0.98, 0.94, 0.84]);
    right.threeDLayer = true;
    var title = addText("Book Title", "FIELD NOTES", [960, 175], 56, [0.95, 0.9, 0.78]);
    title.property("Transform").property("Position").expression = "value + [Math.sin(time * 1.1) * 10, 0];";

    for (var i = 0; i < 7; i++) {
        var page = addRect("Turning Page " + i, [1185, 560], [410, 500], [0.96 - i * 0.015, 0.92 - i * 0.012, 0.82]);
        page.threeDLayer = true;
        page.property("Transform").property("Anchor Point").setValue([0, 0, 0]);
        page.property("Transform").property("Position").setValue([980, 310, -i * 2]);
        var start = 0.8 + i * 0.52;
        page.property("Transform").property("Y Rotation").setValueAtTime(start, 0);
        page.property("Transform").property("Y Rotation").setValueAtTime(start + 0.45, -155);
        page.property("Transform").property("Opacity").setValueAtTime(start + 0.5, 100);
        page.property("Transform").property("Opacity").setValueAtTime(start + 0.75, 0);
        addRect("Page Image Block " + i, [1110, 475 + (i % 3) * 28], [210, 120], [0.18 + i * 0.04, 0.38, 0.58]);
        var edge = addRect("Page Turn Edge Highlight " + i, [980, 560], [14, 500], [1, 0.96, 0.74]);
        edge.threeDLayer = true;
        edge.property("Transform").property("Opacity").setValueAtTime(start, 0);
        edge.property("Transform").property("Opacity").setValueAtTime(start + 0.2, 70);
        edge.property("Transform").property("Opacity").setValueAtTime(start + 0.65, 0);
    }
    for (var j = 0; j < 5; j++) {
        addRect("Page Line " + j, [1185, 690 + j * 28], [270 - j * 25, 8], [0.42, 0.36, 0.28]);
    }
    for (var t = 0; t < 8; t++) {
        var tab = addRect("Page Index Tab " + t, [1420, 342 + t * 42], [76, 20], [0.7, 0.5, 0.32]);
        tab.property("Transform").property("Position").expression = "value + [Math.sin(time * 2 + " + t + ") * 8, 0];";
    }
    var cameraSweep = addRect("Table Light Sweep", [-220, 790], [360, 36], [1, 0.9, 0.64]);
    cameraSweep.property("Transform").property("Opacity").setValue(30);
    cameraSweep.property("Transform").property("Position").setValueAtTime(1.0, [-220, 790]);
    cameraSweep.property("Transform").property("Position").setValueAtTime(6.2, [2140, 690]);
    addText("Book Caption", "page-turn controls / camera-ready story system", [960, 930], 32, [0.93, 0.84, 0.68]);
    app.endUndoGroup();
})();
