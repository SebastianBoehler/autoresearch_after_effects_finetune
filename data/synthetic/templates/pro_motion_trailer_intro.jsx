(function () {
    app.beginUndoGroup("AEFT Editorial Motion Trailer");
    var comp = app.project.items.addComp("AEFT Editorial Motion Trailer", 1920, 1080, 1, 12, 30);
    comp.bgColor = [0.006, 0.007, 0.01];
    try {
        comp.motionBlur = true;
        comp.shutterAngle = 220;
        comp.shutterPhase = -110;
        comp.motionBlurSamplesPerFrame = 16;
    } catch (err) {}
    var W = 1920;
    var H = 1080;
    var ink = [0.006, 0.007, 0.01];
    var panelInk = [0.022, 0.025, 0.032];
    var paper = [0.91, 0.94, 0.98];
    var muted = [0.62, 0.68, 0.76];
    var amber = [1.0, 0.52, 0.12];
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
            var value = prop.keyValue(k);
            var dims = value instanceof Array ? value.length : 1;
            var inEase = [];
            var outEase = [];
            for (var d = 0; d < dims; d++) {
                inEase.push(new KeyframeEase(0, influence));
                outEase.push(new KeyframeEase(0, influence));
            }
            try {
                prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
                prop.setTemporalEaseAtKey(k, inEase, outEase);
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
    function textLayer(name, value, pos, size, color, start, end, align) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = align || ParagraphJustification.CENTER_JUSTIFY;
        try {
            doc.font = "Helvetica-Bold";
            doc.tracking = size > 70 ? -24 : 54;
        } catch (err) {}
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        try {
            var anim = layer.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
            var track = anim.property("ADBE Text Animator Properties").addProperty("ADBE Text Tracking Amount");
            track.setValueAtTime(start, size > 70 ? -70 : -8);
            track.setValueAtTime(start + 0.38, size > 70 ? 18 : 72);
            track.setValueAtTime(start + 0.72, size > 70 ? 0 : 54);
            ease(track, 88);
        } catch (err) {}
        return keep(layer, start, end);
    }
    function opacity(layer, t0, t1, t2, t3, peak) {
        var p = layer.property("Transform").property("Opacity");
        p.setValueAtTime(t0, 0);
        p.setValueAtTime(t1, peak);
        p.setValueAtTime(t2, peak);
        p.setValueAtTime(t3, 0);
        ease(p, 82);
        return layer;
    }
    function pos(layer, t0, a, t1, b, t2, c) {
        var p = layer.property("Transform").property("Position");
        p.setValueAtTime(t0, a);
        p.setValueAtTime(t1, b);
        if (c) {
            p.setValueAtTime(t2, c);
        }
        ease(p, 86);
        return layer;
    }
    function scl(layer, t0, a, t1, b, t2, c) {
        var p = layer.property("Transform").property("Scale");
        p.setValueAtTime(t0, a);
        p.setValueAtTime(t1, b);
        if (c) {
            p.setValueAtTime(t2, c);
        }
        ease(p, 86);
        return layer;
    }
    function add(layer) {
        try {
            layer.blendingMode = BlendingMode.ADD;
        } catch (err) {}
        return layer;
    }
    function flash(name, t, color, amount) {
        return add(opacity(rect(name, [960, 540], [1920, 1080], color, t - 0.03, t + 0.22, 0), t - 0.03, t, t + 0.04, t + 0.22, amount));
    }
    function shutter(name, start, end, color, reverse) {
        for (var i = 0; i < 12; i++) {
            var y = 64 + i * 88;
            var fromX = reverse ? 2240 : -320;
            var toX = reverse ? -320 : 2240;
            var bar = rect(name + " Bar " + i, [fromX, y], [520, 56], color, start + i * 0.018, end, 100);
            pos(bar, start + i * 0.018, [fromX, y], start + 0.32 + i * 0.018, [960, y], end - 0.34, [toX, y]);
            opacity(bar, start + i * 0.018, start + 0.08 + i * 0.018, end - 0.22, end, 96);
        }
        flash(name + " Impact", start + 0.28, color, 34);
    }
    function grid(start, end) {
        for (var v = 0; v < 7; v++) {
            var x = 240 + v * 240;
            var vl = rect("Editorial Grid V " + v, [x, 540], [2, 820], muted, start, end, 22);
            scl(vl, start, [100, 0], start + 0.5 + v * 0.035, [100, 100]);
        }
        for (var h = 0; h < 5; h++) {
            var y = 210 + h * 160;
            var hl = rect("Editorial Grid H " + h, [960, y], [1380, 2], muted, start, end, 16);
            scl(hl, start + 0.1, [0, 100], start + 0.62 + h * 0.04, [100, 100]);
        }
    }
    rect("Ink Base", [960, 540], [1920, 1080], ink, 0, 12, 100);
    grid(0, 12);
    rect("Top Letterbox", [960, 58], [1920, 116], [0, 0, 0], 0, 12, 100);
    rect("Bottom Letterbox", [960, 1022], [1920, 116], [0, 0, 0], 0, 12, 100);
    var s0 = textLayer("Cold Eyebrow", "A SCRIPTED MOTION SYSTEM", [960, 330], 30, amber, 0.1, 1.95);
    var title = textLayer("Cold Main Title", "AFTER / EFFECTS", [960, 508], 142, paper, 0.18, 2.08);
    var sub = textLayer("Cold Subtitle", "TWELVE SECONDS OF GENERATED EDITORIAL FILM", [960, 640], 30, muted, 0.55, 1.9);
    opacity(s0, 0.1, 0.35, 1.62, 1.95, 92);
    opacity(title, 0.18, 0.42, 1.68, 2.08, 100);
    opacity(sub, 0.55, 0.78, 1.5, 1.9, 92);
    pos(title, 0.18, [960, 570], 0.7, [960, 490], 1.7, [960, 508]);
    scl(title, 0.18, [82, 82], 0.72, [108, 108], 1.75, [100, 100]);
    var coldRule = rect("Cold Amber Rule", [960, 718], [1500, 8], amber, 0.5, 1.95, 100);
    scl(coldRule, 0.5, [0, 100], 1.18, [100, 100]);
    flash("Cold Cut Flash", 1.48, paper, 28);
    shutter("First Shutter", 1.72, 2.45, amber, false);
    var plateA = rect("Act Two Plate A", [542, 540], [624, 520], panelInk, 2.05, 4.15, 92);
    var plateB = rect("Act Two Plate B", [1260, 540], [624, 520], panelInk, 2.18, 4.15, 92);
    pos(plateA, 2.05, [420, 540], 2.55, [560, 540], 3.85, [542, 540]);
    pos(plateB, 2.18, [1400, 540], 2.65, [1240, 540], 3.85, [1260, 540]);
    opacity(plateA, 2.05, 2.26, 3.75, 4.15, 88);
    opacity(plateB, 2.18, 2.36, 3.75, 4.15, 88);
    var noFootage = textLayer("No Footage", "NO FOOTAGE", [542, 500], 88, paper, 2.2, 4.0);
    var noPlugins = textLayer("No Plugins", "NO PLUGINS", [1260, 500], 88, paper, 2.34, 4.0);
    var codeOnly = textLayer("Code Only", "ONLY KEYFRAMES, TYPE, SHAPES", [960, 705], 31, amber, 2.76, 4.0);
    opacity(noFootage, 2.2, 2.48, 3.64, 4.0, 100);
    opacity(noPlugins, 2.34, 2.6, 3.64, 4.0, 100);
    opacity(codeOnly, 2.76, 3.0, 3.62, 4.0, 92);
    scl(noFootage, 2.2, [76, 76], 2.72, [103, 103], 3.5, [100, 100]);
    scl(noPlugins, 2.34, [76, 76], 2.84, [103, 103], 3.5, [100, 100]);
    flash("Act Two Hit", 3.52, amber, 26);
    shutter("Second Shutter", 3.88, 4.56, paper, true);
    var centerMass = rect("Scripted Motion Mass", [960, 540], [1060, 420], panelInk, 4.22, 6.7, 86);
    opacity(centerMass, 4.22, 4.48, 6.18, 6.7, 84);
    scl(centerMass, 4.22, [78, 78], 4.76, [104, 104], 6.2, [100, 100]);
    var scripted = textLayer("Scripted Motion Title", "SCRIPTED MOTION", [960, 470], 116, paper, 4.35, 6.52);
    var production = textLayer("Production Logic", "EASED CURVES / EDITORIAL CUTS / CONTROLLED TYPOGRAPHY", [960, 605], 30, muted, 4.92, 6.35);
    opacity(scripted, 4.35, 4.66, 6.08, 6.52, 100);
    opacity(production, 4.92, 5.16, 6.02, 6.35, 94);
    pos(scripted, 4.35, [960, 525], 4.82, [960, 455], 5.55, [960, 470]);
    for (var a = 0; a < 5; a++) {
        var rule = rect("Act Three Rule " + a, [470 + a * 245, 730], [120, 7], amber, 4.62 + a * 0.06, 6.42, 100);
        scl(rule, 4.62 + a * 0.06, [0, 100], 5.05 + a * 0.06, [118, 100]);
        opacity(rule, 4.62 + a * 0.06, 4.8 + a * 0.06, 6.0, 6.42, 90);
    }
    flash("Scripted Impact", 5.58, paper, 22);
    shutter("Third Shutter", 6.35, 7.0, amber, false);
    var beats = ["01 DESIGN SYSTEM", "02 KEYFRAME RHYTHM", "03 RENDER READY"];
    for (var b = 0; b < beats.length; b++) {
        var beat = textLayer("Beat Card " + b, beats[b], [960, 370 + b * 118], 56, b === 1 ? amber : paper, 6.72 + b * 0.12, 8.0);
        opacity(beat, 6.72 + b * 0.12, 6.95 + b * 0.12, 7.62, 8.0, 96);
        pos(beat, 6.72 + b * 0.12, [860, 370 + b * 118], 7.05 + b * 0.12, [980, 370 + b * 118]);
    }
    flash("Beat Stack Flash", 7.64, amber, 32);
    shutter("Final Shutter", 7.74, 8.28, paper, true);
    var finalFrame = rect("Final Editorial Frame", [960, 540], [1220, 470], panelInk, 8.05, 12, 84);
    opacity(finalFrame, 8.05, 8.3, 11.55, 12, 84);
    var finalTitle = textLayer("Final Title", "GENERATIVE TRAILERS", [960, 470], 108, paper, 8.14, 12);
    var finalSub = textLayer("Final Subtitle", "AFTER EFFECTS FROM CODE", [960, 592], 36, amber, 8.6, 11.86);
    var billing = textLayer("Final Billing", "SCRIPT // DESIGN SYSTEM // KEYFRAMES // RENDER", [960, 735], 28, muted, 8.96, 11.82);
    opacity(finalTitle, 8.14, 8.44, 11.55, 12, 100);
    opacity(finalSub, 8.6, 8.84, 11.42, 11.86, 96);
    opacity(billing, 8.96, 9.15, 11.32, 11.82, 88);
    pos(finalTitle, 8.14, [960, 535], 8.68, [960, 452], 9.5, [960, 470]);
    scl(finalTitle, 8.14, [78, 78], 8.74, [110, 110], 11.2, [104, 104]);
    var finalRule = rect("Final Amber Rule", [960, 662], [1160, 9], amber, 8.78, 11.86, 100);
    scl(finalRule, 8.78, [0, 100], 9.28, [100, 100]);
    flash("Final White Hit", 9.55, paper, 18);
    comp.openInViewer();
    app.endUndoGroup();
})();
