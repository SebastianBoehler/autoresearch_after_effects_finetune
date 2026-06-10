(function () {
    app.beginUndoGroup("AEFT Festival Signal Trailer");
    var W = 1920;
    var H = 1080;
    var DUR = 13;
    var comp = app.project.items.addComp("AEFT Festival Signal Trailer", W, H, 1, DUR, 30);
    comp.bgColor = [0.018, 0.006, 0.035];
    try {
        comp.motionBlur = true;
        comp.shutterAngle = 230;
        comp.shutterPhase = -115;
        comp.motionBlurSamplesPerFrame = 18;
    } catch (err) {}
    var black = [0.018, 0.006, 0.035];
    var violet = [0.12, 0.035, 0.23];
    var acid = [0.58, 1.0, 0.10];
    var magenta = [1.0, 0.06, 0.58];
    var white = [1.0, 0.96, 0.86];
    var dim = [0.20, 0.16, 0.28];
    function keep(layer, start, end) {
        layer.inPoint = start;
        layer.outPoint = end;
        try {
            layer.motionBlur = true;
        } catch (err) {}
        return layer;
    }
    function tr(layer, name) {
        return layer.property("Transform").property(name);
    }
    function ease(prop, influence) {
        if (!prop) {
            return;
        }
        for (var k = 1; k <= prop.numKeys; k++) {
            var value = prop.keyValue(k);
            var dims = value instanceof Array ? value.length : 1;
            var ins = [];
            var outs = [];
            for (var d = 0; d < dims; d++) {
                ins.push(new KeyframeEase(0, influence || 82));
                outs.push(new KeyframeEase(0, influence || 82));
            }
            try {
                prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
                prop.setTemporalEaseAtKey(k, ins, outs);
            } catch (err) {}
        }
    }
    function key(layer, name, times, values, influence) {
        var prop = tr(layer, name);
        for (var i = 0; i < times.length; i++) {
            prop.setValueAtTime(times[i], values[i]);
        }
        ease(prop, influence || 82);
        return layer;
    }
    function fade(layer, t0, t1, t2, t3, peak) {
        return key(layer, "Opacity", [t0, t1, t2, t3], [0, peak, peak, 0], 80);
    }
    function fx(layer, matchName) {
        try {
            return layer.property("ADBE Effect Parade").addProperty(matchName);
        } catch (err) {
            return null;
        }
    }
    function addMode(layer) {
        try {
            layer.blendingMode = BlendingMode.ADD;
        } catch (err) {}
        return layer;
    }
    function rect(name, pos, size, color, start, end, opacity) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        group.property("Contents").addProperty("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size").setValue(size);
        group.property("Contents").addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(color);
        tr(layer, "Position").setValue(pos);
        tr(layer, "Opacity").setValue(opacity === undefined ? 100 : opacity);
        return keep(layer, start, end);
    }
    function ellipse(name, pos, size, color, start, end, opacity, strokeWidth) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        group.property("Contents").addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue(size);
        if (strokeWidth) {
            var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
            stroke.property("ADBE Vector Stroke Color").setValue(color);
            stroke.property("ADBE Vector Stroke Width").setValue(strokeWidth);
        } else {
            group.property("Contents").addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(color);
        }
        tr(layer, "Position").setValue(pos);
        tr(layer, "Opacity").setValue(opacity === undefined ? 100 : opacity);
        return keep(layer, start, end);
    }
    function pathLayer(name, points, color, start, end, opacity) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = new Shape();
        shape.vertices = points;
        shape.closed = true;
        shape.inTangents = [];
        shape.outTangents = [];
        for (var i = 0; i < points.length; i++) {
            shape.inTangents.push([0, 0]);
            shape.outTangents.push([0, 0]);
        }
        group.property("Contents").addProperty("ADBE Vector Shape - Group").property("ADBE Vector Shape").setValue(shape);
        group.property("Contents").addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(color);
        tr(layer, "Opacity").setValue(opacity === undefined ? 100 : opacity);
        return keep(layer, start, end);
    }
    function textLayer(name, value, pos, size, color, start, end, tracking) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        try {
            doc.font = size > 120 ? "Helvetica-Bold" : "Arial-BoldMT";
            doc.tracking = tracking === undefined ? 48 : tracking;
        } catch (err) {}
        layer.property("Source Text").setValue(doc);
        tr(layer, "Position").setValue(pos);
        try {
            var anim = layer.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
            var amount = anim.property("ADBE Text Animator Properties").addProperty("ADBE Text Tracking Amount");
            amount.setValueAtTime(start, size > 100 ? 420 : 260);
            amount.setValueAtTime(start + 0.34, tracking === undefined ? 48 : tracking);
            amount.setValueAtTime(start + 0.72, tracking === undefined ? 48 : tracking);
            ease(amount, 88);
        } catch (err) {}
        return keep(layer, start, end);
    }
    function flash(name, time, color, amount) {
        var layer = rect(name, [960, 540], [1920, 1080], color, time - 0.02, time + 0.22, 0);
        fade(layer, time - 0.02, time, time + 0.05, time + 0.22, amount);
        return addMode(layer);
    }
    function tear(name, start, color, reverse) {
        var pts = [[-960, -540], [960, -540], [960, -210], [840, -162], [955, -108], [760, -48], [900, 20], [730, 82], [940, 145], [760, 210], [960, 278], [960, 540], [-960, 540], [-960, 250], [-810, 192], [-960, 125], [-780, 66], [-930, 0], [-760, -72], [-940, -132], [-800, -205], [-960, -270]];
        var layer = pathLayer(name, pts, color, start, start + 0.7, 100);
        var fromX = reverse ? 2220 : -300;
        var toX = reverse ? -300 : 2220;
        key(layer, "Position", [start, start + 0.26, start + 0.56], [[fromX, 540], [960, 540], [toX, 540]], 88);
        key(layer, "Scale", [start, start + 0.26, start + 0.56], [[76, 100], [112, 100], [84, 100]], 88);
        fade(layer, start, start + 0.05, start + 0.43, start + 0.68, 100);
        return layer;
    }
    function beam(name, x, color, start, end, phase) {
        var layer = rect(name, [x, 260], [92, 1740], color, start, end, 22);
        tr(layer, "Anchor Point").setValue([0, -820]);
        tr(layer, "Rotation").setValue(-22 + phase);
        try {
            tr(layer, "Rotation").expression = "value + Math.sin(time * 3.1 + " + phase + ") * 34;";
        } catch (err) {}
        fx(layer, "ADBE Fast Box Blur");
        addMode(layer);
        return layer;
    }
    function eqBars(start, end) {
        for (var i = 0; i < 22; i++) {
            var x = 260 + i * 66;
            var h = 120 + (i % 6) * 42;
            var bar = rect("Festival EQ Bar " + i, [x, 820], [36, h], i % 3 === 0 ? acid : (i % 3 === 1 ? magenta : white), start + i * 0.018, end, 0);
            tr(bar, "Anchor Point").setValue([0, h / 2]);
            fade(bar, start + i * 0.018, start + 0.12 + i * 0.018, end - 0.34, end, 92);
            try {
                tr(bar, "Scale").expression = "amp = 28 + Math.abs(Math.sin(time * " + (7.4 + i * 0.13) + " + " + i + ")) * 96; [100, amp];";
            } catch (err) {}
        }
    }
    rect("Festival Void", [960, 540], [1920, 1080], black, 0, DUR, 100);
    var haze = rect("Violet Stage Haze", [960, 540], [1920, 1080], violet, 0, DUR, 38);
    fx(haze, "ADBE Turbulent Displace");
    addMode(ellipse("Magenta Bass Halo", [960, 610], [900, 900], magenta, 0, DUR, 13));
    addMode(ellipse("Acid Bass Halo", [960, 610], [520, 520], acid, 0, DUR, 14));
    beam("Left Magenta Follow Spot", 430, magenta, 0.0, 6.4, 0);
    beam("Center Acid Follow Spot", 960, acid, 0.2, 6.4, 2);
    beam("Right White Follow Spot", 1490, white, 0.35, 6.4, 4);
    flash("Cold Open Strobe", 0.08, white, 88);
    var coldSignal = textLayer("Cold Flash Signal", "SIGNAL", [960, 585], 250, black, 0.02, 0.42, -10);
    fade(coldSignal, 0.02, 0.08, 0.2, 0.42, 100);
    var title = textLayer("Main Signal Title", "SIGNAL", [960, 505], 255, acid, 0.46, 2.92, -18);
    key(title, "Scale", [0.46, 0.78, 1.38, 2.75], [[138, 138], [92, 92], [106, 106], [100, 100]], 90);
    fade(title, 0.46, 0.62, 2.48, 2.92, 100);
    addMode(title);
    var sub = textLayer("Transmission Subtitle", "LIVE TRANSMISSION / THREE NIGHTS", [960, 696], 43, white, 0.98, 2.78, 62);
    fade(sub, 0.98, 1.2, 2.38, 2.78, 96);
    var rail = ellipse("Signal Vinyl Ring", [960, 540], [760, 760], magenta, 0.7, 3.0, 64, 7);
    try {
        var group = rail.property("Contents").property(1);
        var trim = group.property("Contents").addProperty("ADBE Vector Filter - Trim");
        trim.property("ADBE Vector Trim End").setValueAtTime(0.72, 0);
        trim.property("ADBE Vector Trim End").setValueAtTime(1.42, 100);
        trim.property("ADBE Vector Trim Offset").expression = "time * 120;";
        ease(trim.property("ADBE Vector Trim End"), 90);
    } catch (err) {}
    key(rail, "Scale", [0.7, 1.25, 2.6], [[0, 0], [105, 105], [116, 116]], 88);
    tear("First Ticket Tear", 2.58, magenta, false);
    eqBars(3.05, 5.98);
    var freq = textLayer("Frequency Headline", "FEEL THE FREQUENCY", [960, 264], 74, magenta, 3.22, 5.92, 82);
    fade(freq, 3.22, 3.45, 5.55, 5.92, 100);
    key(freq, "Position", [3.22, 3.62, 5.5], [[960, 326], [960, 250], [960, 264]], 88);
    flash("EQ Beat Hit", 4.48, acid, 36);
    var record = ellipse("Vinyl Iris Fill", [960, 540], [850, 850], black, 5.66, 7.15, 100);
    ellipse("Vinyl Acid Groove", [960, 540], [850, 850], acid, 5.66, 7.15, 96, 10).parent = record;
    ellipse("Vinyl Magenta Label", [960, 540], [240, 240], magenta, 5.66, 7.15, 92).parent = record;
    key(record, "Scale", [5.66, 6.05, 6.52, 7.12], [[0, 0], [106, 106], [118, 118], [300, 300]], 86);
    key(record, "Rotation", [5.66, 7.12], [0, 720], 78);
    flash("Vinyl White Cut", 6.62, white, 42);
    var names = ["NOVA PULSE", "GHOST CIRCUIT", "ACID BLOOM", "MIDNIGHT VOLT", "JUNE 21 / 23"];
    var colors = [acid, white, magenta, acid, white];
    for (var n = 0; n < names.length; n++) {
        var t = 6.92 + n * 0.72;
        var card = rect("Lineup Back Plate " + n, [960, 540], [1280, 210], n % 2 ? dim : black, t, t + 0.74, 88);
        key(card, "Scale", [t, t + 0.28, t + 0.68], [[0, 100], [108, 100], [92, 100]], 88);
        var line = textLayer("Lineup Name " + n, names[n], [960, 568], n === 4 ? 112 : 148, colors[n], t + 0.05, t + 0.74, n === 4 ? 40 : -10);
        fade(line, t + 0.05, t + 0.16, t + 0.58, t + 0.74, 100);
        key(line, "Scale", [t + 0.05, t + 0.28, t + 0.64], [[138, 138], [98, 98], [104, 104]], 88);
        flash("Lineup Strobe " + n, t + 0.08, colors[n], 20);
    }
    tear("Second Ticket Tear", 10.42, acid, true);
    var finalPlate = rect("Final Stage Plate", [960, 540], [1430, 470], black, 10.68, 13, 88);
    key(finalPlate, "Position", [10.68, 11.12, 12.6], [[960, 910], [960, 520], [960, 540]], 88);
    var finalTitle = textLayer("Final Festival Title", "SIGNAL FEST", [960, 482], 214, white, 10.9, 13, -24);
    var finalSub = textLayer("Final Festival Subtitle", "ONE WEEKEND / ONE SIGNAL", [960, 664], 46, acid, 11.38, 12.82, 88);
    fade(finalTitle, 10.9, 11.18, 12.62, 13, 100);
    fade(finalSub, 11.38, 11.62, 12.52, 12.82, 98);
    key(finalTitle, "Scale", [10.9, 11.35, 12.48], [[62, 62], [108, 108], [100, 100]], 90);
    var finalRule = rect("Final Magenta Rule", [960, 746], [980, 10], magenta, 11.56, 12.82, 100);
    key(finalRule, "Scale", [11.56, 11.96, 12.7], [[0, 100], [100, 100], [112, 100]], 86);
    flash("Final Camera Flash", 11.0, white, 64);
    comp.openInViewer();
    app.endUndoGroup();
})();
