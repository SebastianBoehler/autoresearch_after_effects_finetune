(function () {
    app.beginUndoGroup("AEFT Action Teaser Title Stack");
    var comp = app.project.items.addComp("AEFT Action Teaser Title Stack", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.018, 0.018, 0.02];

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

    var words = ["LOCK", "THE", "FRAME"];
    for (var i = 0; i < words.length; i++) {
        var y = 360 + i * 135;
        var slab = addRect("Trailer Slab " + i, [960, y], [980, 112], i % 2 ? [0.82, 0.08, 0.08] : [0.94, 0.9, 0.78]);
        slab.property("Transform").property("Scale").setValueAtTime(0.55 + i * 0.25, [0, 100]);
        slab.property("Transform").property("Scale").setValueAtTime(1.05 + i * 0.25, [100, 100]);
        var txt = addText("Trailer Word " + i, words[i], [960, y + 38], 118, i % 2 ? [0.98, 0.95, 0.88] : [0.04, 0.035, 0.03]);
        txt.property("Transform").property("Opacity").setValueAtTime(0.65 + i * 0.25, 0);
        txt.property("Transform").property("Opacity").setValueAtTime(1.2 + i * 0.25, 100);
    }
    for (var j = 0; j < 18; j++) {
        var streak = addRect("Action Streak " + j, [-180 + j * 120, 210 + (j % 8) * 88], [260, 9], [1, 0.82, 0.16]);
        streak.property("Transform").property("Rotation").setValue(-12 + (j % 4) * 8);
        streak.property("Transform").property("Position").setValueAtTime(1.6 + j * 0.03, [-180 + j * 120, 210 + (j % 8) * 88]);
        streak.property("Transform").property("Position").setValueAtTime(4.9 + j * 0.03, [220 + j * 120, 190 + (j % 8) * 88]);
    }
    for (var k = 0; k < 10; k++) {
        var shard = addRect("Impact Slice " + k, [320 + k * 145, 525 + (k % 3) * 58], [170, 18], k % 2 ? [0.08, 0.08, 0.09] : [0.88, 0.05, 0.05]);
        shard.property("Transform").property("Rotation").setValue(-18 + (k % 5) * 9);
        shard.property("Transform").property("Scale").setValueAtTime(2.8 + k * 0.025, [0, 100]);
        shard.property("Transform").property("Scale").setValueAtTime(3.35 + k * 0.025, [100, 100]);
        shard.property("Transform").property("Opacity").expression = "45 + Math.sin(time * 18 + " + k + ") * 28;";
    }
    for (var t = 0; t < 16; t++) {
        var tick = addRect("Trailer Timing Tick " + t, [310 + t * 86, 132], [42, 6], [0.7, 0.75, 0.82]);
        tick.property("Transform").property("Opacity").setValueAtTime(0.4 + t * 0.06, 0);
        tick.property("Transform").property("Opacity").setValueAtTime(0.85 + t * 0.06, 86);
        tick.property("Transform").property("Position").expression = "value + [Math.sin(time * 7 + " + t + ") * 6, 0];";
    }
    var flash = addRect("Trailer Flash Frame", [960, 540], [1920, 1080], [1, 1, 1]);
    flash.property("Transform").property("Opacity").setValueAtTime(3.8, 0);
    flash.property("Transform").property("Opacity").setValueAtTime(3.9, 72);
    flash.property("Transform").property("Opacity").setValueAtTime(4.1, 0);
    var footer = addText("Trailer Footer", "FAST TEASER / SLAB TITLES / IMPACT FRAMES", [960, 880], 34, [0.8, 0.84, 0.9]);
    footer.property("Transform").property("Opacity").expression = "78 + Math.sin(time * 5.5) * 18;";
    app.endUndoGroup();
})();
