(function () {
    app.beginUndoGroup("AEFT Brutalist Constructivism Trailer");
    var comp = app.project.items.addComp("AEFT Brutalist Constructivism Trailer", 1920, 1080, 1, 12, 30);
    comp.bgColor = [0.11, 0.105, 0.095];
    try {
        comp.motionBlur = true;
        comp.shutterAngle = 210;
        comp.shutterPhase = -105;
        comp.motionBlurSamplesPerFrame = 16;
    } catch (err) {}
    var W = 1920;
    var H = 1080;
    var concrete = [0.11, 0.105, 0.095];
    var slab = [0.22, 0.21, 0.19];
    var dark = [0.045, 0.044, 0.04];
    var red = [0.86, 0.10, 0.08];
    var offWhite = [0.92, 0.90, 0.86];
    function keep(layer, start, end) {
        layer.inPoint = start;
        layer.outPoint = end;
        try {
            layer.motionBlur = true;
        } catch (err) {}
        return layer;
    }
    function ease(prop, influence) {
        for (var k = 1; k <= prop.numKeys; k++) {
            var v = prop.keyValue(k);
            var dims = v instanceof Array ? v.length : 1;
            var a = [];
            var b = [];
            for (var d = 0; d < dims; d++) {
                a.push(new KeyframeEase(0, influence));
                b.push(new KeyframeEase(0, influence));
            }
            try {
                prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
                prop.setTemporalEaseAtKey(k, a, b);
            } catch (err) {}
        }
    }
    function rect(name, pos, size, color, start, end, opacity) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var box = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        box.property("ADBE Vector Rect Size").setValue(size);
        group.property("Contents").addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValue(opacity === undefined ? 100 : opacity);
        return keep(layer, start, end);
    }
    function text(name, value, pos, size, color, start, end) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        try {
            doc.font = "Arial Black";
            doc.tracking = size > 90 ? -38 : 36;
        } catch (err) {}
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        return keep(layer, start, end);
    }
    function fade(layer, t0, t1, t2, t3, peak) {
        var p = layer.property("Transform").property("Opacity");
        p.setValueAtTime(t0, 0);
        p.setValueAtTime(t1, peak);
        p.setValueAtTime(t2, peak);
        p.setValueAtTime(t3, 0);
        ease(p, 84);
        return layer;
    }
    function move(layer, t0, a, t1, b, t2, c) {
        var p = layer.property("Transform").property("Position");
        p.setValueAtTime(t0, a);
        p.setValueAtTime(t1, b);
        if (c) {
            p.setValueAtTime(t2, c);
        }
        ease(p, 88);
        return layer;
    }
    function scale(layer, t0, a, t1, b, t2, c) {
        var p = layer.property("Transform").property("Scale");
        p.setValueAtTime(t0, a);
        p.setValueAtTime(t1, b);
        if (c) {
            p.setValueAtTime(t2, c);
        }
        ease(p, 88);
        return layer;
    }
    function slabIn(name, start, pos, size, color, from) {
        var layer = rect(name, pos, size, color, start, 12, 100);
        var offset = from || [0, 0];
        move(layer, start, [pos[0] + offset[0], pos[1] + offset[1]], start + 0.48, pos, start + 1.02, [pos[0] - offset[0] * 0.04, pos[1] - offset[1] * 0.04]);
        return layer;
    }
    function redWipe(name, start, end, reverse) {
        for (var i = 0; i < 4; i++) {
            var y = 185 + i * 210;
            var fromX = reverse ? 2260 : -340;
            var toX = reverse ? -340 : 2260;
            var bar = rect(name + " Slab " + i, [fromX, y], [760, 138], red, start + i * 0.035, end, 100);
            move(bar, start + i * 0.035, [fromX, y], start + 0.34 + i * 0.035, [960, y], end - 0.24, [toX, y]);
            fade(bar, start + i * 0.035, start + 0.08 + i * 0.035, end - 0.16, end, 100);
        }
    }
    rect("Concrete Base", [960, 540], [1920, 1080], concrete, 0, 12, 100);
    rect("Concrete Shadow Left", [270, 540], [540, 1080], dark, 0, 12, 52);
    rect("Concrete Shadow Right", [1650, 540], [540, 1080], slab, 0, 12, 48);
    slabIn("Opening Mass A", 0.05, [925, 430], [920, 460], slab, [0, -760]);
    slabIn("Opening Red Mass", 0.22, [590, 720], [420, 210], red, [-980, 0]);
    slabIn("Opening Mass B", 0.36, [1280, 745], [560, 260], dark, [980, 0]);
    var first = text("Opening Title", "RAW FORM", [960, 500], 148, offWhite, 0.38, 2.18);
    var firstSub = text("Opening Subtitle", "CONCRETE MOTION / SCRIPTED STRUCTURE", [960, 650], 34, offWhite, 0.78, 2.08);
    fade(first, 0.38, 0.66, 1.76, 2.18, 100);
    fade(firstSub, 0.78, 1.0, 1.72, 2.08, 92);
    scale(first, 0.38, [72, 72], 0.88, [110, 110], 1.58, [100, 100]);
    move(first, 0.38, [960, 585], 0.88, [960, 482], 1.58, [960, 500]);
    redWipe("First Red Cut", 1.82, 2.52, false);
    slabIn("Construct Plate A", 2.22, [540, 500], [650, 620], dark, [-900, 0]);
    slabIn("Construct Plate B", 2.34, [1255, 520], [650, 560], slab, [900, 0]);
    var constructA = text("Construct A", "CONSTRUCT", [960, 455], 122, red, 2.52, 4.42);
    var constructB = text("Construct B", "WITHOUT ORNAMENT", [960, 600], 56, offWhite, 2.88, 4.3);
    fade(constructA, 2.52, 2.82, 4.0, 4.42, 100);
    fade(constructB, 2.88, 3.12, 3.92, 4.3, 94);
    scale(constructA, 2.52, [0, 100], 3.0, [104, 104], 3.7, [100, 100]);
    scale(constructB, 2.88, [72, 72], 3.28, [104, 104], 3.76, [100, 100]);
    var rule = rect("Construct Red Rule", [960, 705], [1120, 14], red, 3.05, 4.3, 100);
    scale(rule, 3.05, [0, 100], 3.55, [100, 100]);
    redWipe("Second Red Cut", 4.05, 4.72, true);
    var card = rect("Manifesto Card", [960, 540], [1320, 670], dark, 4.42, 7.38, 100);
    move(card, 4.42, [960, -420], 4.94, [960, 560], 5.58, [960, 540]);
    var form = text("Manifesto Form", "FORM", [960, 420], 138, red, 4.72, 7.18);
    var follows = text("Manifesto Follows", "FOLLOWS", [960, 555], 92, offWhite, 5.04, 7.06);
    var functionText = text("Manifesto Function", "FUNCTION", [960, 655], 92, offWhite, 5.24, 6.98);
    fade(form, 4.72, 4.98, 6.78, 7.18, 100);
    fade(follows, 5.04, 5.25, 6.68, 7.06, 96);
    fade(functionText, 5.24, 5.45, 6.58, 6.98, 96);
    scale(form, 4.72, [44, 44], 5.12, [112, 112], 6.24, [100, 100]);
    for (var b = 0; b < 5; b++) {
        var band = rect("Manifesto Band " + b, [430 + b * 265, 780], [150, 10], red, 5.18 + b * 0.06, 7.05, 100);
        scale(band, 5.18 + b * 0.06, [0, 100], 5.58 + b * 0.06, [118, 100]);
        fade(band, 5.18 + b * 0.06, 5.35 + b * 0.06, 6.62, 7.05, 92);
    }
    redWipe("Third Red Cut", 6.92, 7.52, false);
    var words = ["MASS", "WEIGHT", "IMPACT", "ORDER"];
    for (var w = 0; w < words.length; w++) {
        var word = text("Kinetic Word " + w, words[w], [960, 405 + w * 95], 88, w === 2 ? red : offWhite, 7.28 + w * 0.18, 9.1);
        fade(word, 7.28 + w * 0.18, 7.48 + w * 0.18, 8.62 + w * 0.12, 9.1, 100);
        move(word, 7.28 + w * 0.18, [780, 405 + w * 95], 7.64 + w * 0.18, [985, 405 + w * 95]);
        scale(word, 7.28 + w * 0.18, [54, 54], 7.68 + w * 0.18, [104, 104]);
    }
    redWipe("Final Red Cut", 8.78, 9.32, true);
    slabIn("Final Block Top", 9.05, [960, 305], [1180, 170], slab, [0, -620]);
    slabIn("Final Block Bottom", 9.12, [960, 690], [1180, 310], dark, [0, 620]);
    var finalA = text("Final Main", "BRUTALIST", [960, 470], 142, offWhite, 9.32, 12);
    var finalB = text("Final Sub", "CONSTRUCTIVISM", [960, 610], 58, red, 9.72, 11.82);
    var finalC = text("Final Billing", "MOTION BUILT FROM MASS / TYPE / CUTS", [960, 745], 32, offWhite, 10.08, 11.72);
    fade(finalA, 9.32, 9.58, 11.55, 12, 100);
    fade(finalB, 9.72, 9.92, 11.38, 11.82, 96);
    fade(finalC, 10.08, 10.26, 11.22, 11.72, 86);
    scale(finalA, 9.32, [72, 72], 9.86, [110, 110], 11.18, [102, 102]);
    move(finalA, 9.32, [960, 540], 9.86, [960, 452], 11.18, [960, 470]);
    var finalRule = rect("Final Red Rule", [960, 665], [1040, 12], red, 9.95, 11.82, 100);
    scale(finalRule, 9.95, [0, 100], 10.38, [100, 100]);
    comp.openInViewer();
    app.endUndoGroup();
})();
