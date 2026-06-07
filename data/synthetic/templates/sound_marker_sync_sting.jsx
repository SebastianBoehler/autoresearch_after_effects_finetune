(function () {
    app.beginUndoGroup("AEFT Sound Marker Sync Sting");
    var comp = app.project.items.addComp("AEFT Sound Marker Sync Sting", 1920, 1080, 1, 6, 30);
    comp.bgColor = [0.012, 0.014, 0.018];
    var markerTrack = comp.layers.addNull();
    markerTrack.name = "Beat Marker Track";
    markerTrack.property("Marker").setValueAtTime(0.6, new MarkerValue("tick"));
    markerTrack.property("Marker").setValueAtTime(1.4, new MarkerValue("whoosh"));
    markerTrack.property("Marker").setValueAtTime(2.35, new MarkerValue("hit"));
    markerTrack.property("Marker").setValueAtTime(4.7, new MarkerValue("resolve"));

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

    addText("Sync Title", "SOUND MARKER SYNC", [960, 170], 58, [0.94, 0.98, 1]);
    var logo = addRect("Logo Impact Block", [960, 515], [260, 260], [0.12, 0.5, 1]);
    var beats = [0.6, 1.4, 2.35, 3.2, 4.7];
    for (var i = 0; i < beats.length; i++) {
        var tick = addRect("Timeline Marker Tick " + i, [360 + i * 300, 850], [8, 95], [0.98, 0.76, 0.18]);
        tick.property("Transform").property("Scale").setValueAtTime(beats[i] - 0.12, [100, 35]);
        tick.property("Transform").property("Scale").setValueAtTime(beats[i] + 0.12, [100, 120]);
        var flash = addRect("Impact Flash " + i, [960, 515], [420 + i * 70, 18], [1, 1, 1]);
        flash.property("Transform").property("Opacity").setValueAtTime(beats[i], 92);
        flash.property("Transform").property("Opacity").setValueAtTime(beats[i] + 0.28, 0);
        logo.property("Transform").property("Scale").setValueAtTime(beats[i], [88, 88]);
        logo.property("Transform").property("Scale").setValueAtTime(beats[i] + 0.2, [108, 108]);
    }
    for (var b = 0; b < 18; b++) {
        var bar = addRect("Waveform Trigger Bar " + b, [360 + b * 70, 690], [34, 60], [0.18, 0.88, 0.68]);
        bar.property("Transform").property("Scale").expression = "[100, 45 + Math.sin(time * " + (5 + b % 4) + " + " + b + ") * 55];";
    }
    addText("Cue Labels", "tick   whoosh   hit   riser   resolve", [960, 955], 34, [0.76, 0.88, 1]);
    app.endUndoGroup();
})();
