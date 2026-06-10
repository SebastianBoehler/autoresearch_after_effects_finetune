(function () {
    if (!app.project) {
        app.newProject();
    }
    app.beginUndoGroup("AEFT Executive Strategy Trailer");
    var W = 1920;
    var H = 1080;
    var DUR = 12;
    var comp = app.project.items.addComp("AEFT Executive Strategy Trailer", W, H, 1, DUR, 30);
    comp.bgColor = [0.92, 0.92, 0.89];
    try {
        comp.motionBlur = true;
        comp.shutterAngle = 190;
        comp.shutterPhase = -95;
        comp.motionBlurSamplesPerFrame = 14;
    } catch (err) {}
    var paper = [0.92, 0.92, 0.89];
    var chalk = [0.98, 0.98, 0.95];
    var charcoal = [0.075, 0.085, 0.095];
    var graphite = [0.18, 0.19, 0.205];
    var pale = [0.84, 0.85, 0.82];
    var teal = [0.0, 0.68, 0.64];
    var red = [0.75, 0.15, 0.13];
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
                ins.push(new KeyframeEase(0, influence || 76));
                outs.push(new KeyframeEase(0, influence || 76));
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
        ease(prop, influence || 76);
        return layer;
    }
    function fade(layer, t0, t1, t2, t3, peak) {
        return key(layer, "Opacity", [t0, t1, t2, t3], [0, peak, peak, 0], 72);
    }
    function fx(layer, matchName) {
        try {
            return layer.property("ADBE Effect Parade").addProperty(matchName);
        } catch (err) {
            return null;
        }
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
    function strokeRect(name, pos, size, color, width, start, end, opacity) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        group.property("Contents").addProperty("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size").setValue(size);
        var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        stroke.property("ADBE Vector Stroke Color").setValue(color);
        stroke.property("ADBE Vector Stroke Width").setValue(width);
        tr(layer, "Position").setValue(pos);
        tr(layer, "Opacity").setValue(opacity === undefined ? 100 : opacity);
        return keep(layer, start, end);
    }
    function dot(name, pos, size, color, start, end) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        group.property("Contents").addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([size, size]);
        group.property("Contents").addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(color);
        tr(layer, "Position").setValue(pos);
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
            doc.font = size > 56 ? "Helvetica-Bold" : "ArialMT";
            doc.tracking = tracking === undefined ? 26 : tracking;
        } catch (err) {}
        layer.property("Source Text").setValue(doc);
        tr(layer, "Position").setValue(pos);
        try {
            var anim = layer.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
            var amount = anim.property("ADBE Text Animator Properties").addProperty("ADBE Text Tracking Amount");
            amount.setValueAtTime(start, size > 70 ? 72 : 34);
            amount.setValueAtTime(start + 0.34, tracking === undefined ? 26 : tracking);
            ease(amount, 82);
        } catch (err) {}
        return keep(layer, start, end);
    }
    function linePath(name, points, color, width, pos, start, end, trimEnd) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = new Shape();
        shape.vertices = points;
        shape.closed = false;
        shape.inTangents = [];
        shape.outTangents = [];
        for (var i = 0; i < points.length; i++) {
            shape.inTangents.push([0, 0]);
            shape.outTangents.push([0, 0]);
        }
        group.property("Contents").addProperty("ADBE Vector Shape - Group").property("ADBE Vector Shape").setValue(shape);
        var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        stroke.property("ADBE Vector Stroke Color").setValue(color);
        stroke.property("ADBE Vector Stroke Width").setValue(width);
        var trim = group.property("Contents").addProperty("ADBE Vector Filter - Trim");
        trim.property("ADBE Vector Trim End").setValueAtTime(start, 0);
        trim.property("ADBE Vector Trim End").setValueAtTime(trimEnd || start + 0.78, 100);
        ease(trim.property("ADBE Vector Trim End"), 84);
        tr(layer, "Position").setValue(pos);
        return keep(layer, start, end);
    }
    function flash(name, time, color, amount) {
        var layer = rect(name, [960, 540], [1920, 1080], color, time - 0.02, time + 0.16, 0);
        fade(layer, time - 0.02, time, time + 0.035, time + 0.16, amount);
        return layer;
    }
    function sceneBg(name, color, start, end) {
        return rect(name, [960, 540], [1920, 1080], color, start, end, 100);
    }
    sceneBg("Paper Base", paper, 0, DUR);
    var openField = sceneBg("Opening Charcoal Cover", charcoal, 0, 2.05);
    key(openField, "Position", [0, 0.58, 1.68, 2.02], [[960, 540], [960, 540], [960, 540], [960, -560]], 86);
    var openTitle = textLayer("Opening Title", "EXECUTIVE STRATEGY", [960, 495], 92, chalk, 0.18, 1.88, 4);
    var openSub = textLayer("Opening Subtitle", "MARKET POSITION / CAPITAL PLAN / RISK CONTROL", [960, 595], 28, teal, 0.56, 1.82, 24);
    var openRule = rect("Opening Teal Rule", [960, 660], [860, 7], teal, 0.62, 1.88, 100);
    fade(openTitle, 0.18, 0.42, 1.42, 1.88, 100);
    fade(openSub, 0.56, 0.74, 1.34, 1.82, 96);
    key(openTitle, "Scale", [0.18, 0.62, 1.32], [[82, 82], [104, 104], [100, 100]], 84);
    key(openRule, "Scale", [0.62, 1.02, 1.62], [[0, 100], [100, 100], [106, 100]], 80);
    flash("Opening Clean Cut", 1.76, chalk, 24);
    sceneBg("Pillar Paper Clear", paper, 1.95, 4.15);
    var pillarTitle = textLayer("Pillar Header", "BOARD PRIORITIES", [960, 178], 34, charcoal, 2.06, 3.92, 56);
    fade(pillarTitle, 2.06, 2.34, 3.62, 4.02, 100);
    var pillarNames = ["POSITION", "GROWTH", "CONTROL"];
    var pillarColors = [charcoal, graphite, charcoal];
    for (var p = 0; p < 3; p++) {
        var px = 470 + p * 490;
        var start = 2.14 + p * 0.13;
        var panel = rect("Priority Panel " + p, [px, 550], [390, 510], pillarColors[p], start, 4.0, 100);
        key(panel, "Position", [start, start + 0.36, 3.62, 4.0], [[px, 890], [px, 550], [px, 550], [px, 245]], 86);
        var number = textLayer("Priority Number " + p, "0" + (p + 1), [px, 410], 34, p === 2 ? red : teal, start + 0.18, 3.58, 22);
        var name = textLayer("Priority Name " + p, pillarNames[p], [px, 550], 38, chalk, start + 0.28, 3.58, 0);
        var rule = rect("Priority Rule " + p, [px, 630], [170, 6], p === 2 ? red : teal, start + 0.36, 3.58, 100);
        fade(number, start + 0.18, start + 0.32, 3.24, 3.58, 96);
        fade(name, start + 0.28, start + 0.44, 3.24, 3.58, 100);
        key(rule, "Scale", [start + 0.36, start + 0.72, 3.34], [[0, 100], [100, 100], [100, 100]], 80);
    }
    var dashSeed = rect("Priority Dash Seed", [346, 855], [34, 6], teal, 2.8, 4.02, 92);
    try {
        var rep = dashSeed.property("Contents").addProperty("ADBE Vector Filter - Repeater");
        rep.property("ADBE Vector Repeater Copies").setValue(28);
        rep.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([44, 0]);
    } catch (err) {}
    flash("Priority Cut", 3.86, teal, 18);
    sceneBg("Chart Paper Clear", paper, 4.0, 6.7);
    var chartHeader = textLayer("Chart Header", "REVENUE TRAJECTORY", [960, 225], 56, charcoal, 4.16, 6.55, 18);
    fade(chartHeader, 4.16, 4.38, 6.1, 6.55, 100);
    var axis = rect("Chart Axis", [960, 792], [1260, 4], charcoal, 4.2, 6.62, 92);
    key(axis, "Scale", [4.2, 4.66], [[0, 100], [100, 100]], 82);
    var graph = linePath("Trimmed Revenue Line", [[-600, 170], [-380, 86], [-140, 126], [92, -42], [330, -148], [610, -224]], teal, 10, [960, 590], 4.42, 6.66, 5.62);
    fade(graph, 4.42, 4.58, 6.18, 6.66, 100);
    fx(graph, "ADBE Glow");
    var dotPts = [[360, 760], [580, 676], [820, 716], [1052, 548], [1290, 442], [1570, 366]];
    for (var d = 0; d < dotPts.length; d++) {
        var mark = dot("Chart Marker " + d, dotPts[d], d === dotPts.length - 1 ? 22 : 14, d === dotPts.length - 1 ? red : teal, 4.62 + d * 0.16, 6.48);
        key(mark, "Scale", [4.62 + d * 0.16, 4.84 + d * 0.16, 6.18], [[0, 0], [110, 110], [100, 100]], 82);
        fade(mark, 4.62 + d * 0.16, 4.74 + d * 0.16, 6.12, 6.48, 100);
    }
    var percent = textLayer("Chart Counter", "+24%", [1465, 318], 76, teal, 5.42, 6.54, -8);
    fade(percent, 5.42, 5.62, 6.12, 6.54, 100);
    try {
        percent.property("Source Text").expression = "p=Math.max(0,Math.min(1,(time-5.42)/0.9)); '+' + Math.round(24*p) + '%';";
        tr(percent, "Scale").expression = "s = 100 + Math.sin(time * 7) * 1.4; [s, s];";
    } catch (err) {}
    flash("Chart Cut", 6.42, charcoal, 18);
    sceneBg("KPI Charcoal Clear", charcoal, 6.54, 8.95);
    var kpiHeader = textLayer("KPI Header", "OPERATING SNAPSHOT", [960, 190], 34, teal, 6.66, 8.58, 56);
    fade(kpiHeader, 6.66, 6.88, 8.16, 8.58, 100);
    var labs = ["MARGIN", "PIPELINE", "EXPOSURE"];
    var vals = ["38.2%", "$1.4B", "-3.1%"];
    var cols = [teal, teal, red];
    for (var r = 0; r < 3; r++) {
        var y = 360 + r * 170;
        var t = 6.82 + r * 0.16;
        var row = rect("KPI Row " + r, [960, y], [1280, 118], graphite, t, 8.8, 100);
        key(row, "Position", [t, t + 0.34, 8.42, 8.8], [[430, y], [960, y], [960, y], [1490, y]], 84);
        var lab = textLayer("KPI Label " + r, labs[r], [610, y + 13], 32, chalk, t + 0.18, 8.34, 32);
        var val = textLayer("KPI Value " + r, vals[r], [1190, y + 16], 68, cols[r], t + 0.28, 8.66, -4);
        fade(lab, t + 0.18, t + 0.32, 8.0, 8.34, 92);
        fade(val, t + 0.28, t + 0.44, 8.0, 8.34, 100);
        key(val, "Scale", [t + 0.28, t + 0.6, 8.1], [[78, 78], [106, 106], [100, 100]], 82);
        linePath("KPI Spark " + r, [[-70, 20], [-20, -12], [28, 8], [80, -25]], cols[r], 5, [1480, y + 8], t + 0.36, 8.34, t + 0.88);
    }
    flash("KPI Cut", 8.66, red, 16);
    sceneBg("Risk Paper Clear", paper, 8.78, 10.46);
    for (var cell = 0; cell < 4; cell++) {
        var cx = 455 + (cell % 2) * 215;
        var cy = 416 + Math.floor(cell / 2) * 178;
        var color = cell === 3 ? red : (cell === 1 ? teal : pale);
        var block = rect("Risk Cell " + cell, [cx, cy], [170, 138], color, 8.94 + cell * 0.08, 10.24, 100);
        key(block, "Scale", [8.94 + cell * 0.08, 9.2 + cell * 0.08, 9.92], [[0, 100], [100, 100], [100, 100]], 82);
    }
    var scan = rect("Risk Scan Line", [562, 270], [430, 7], teal, 9.12, 10.24, 100);
    key(scan, "Position", [9.12, 9.84], [[562, 270], [562, 700]], 76);
    var riskTitle = textLayer("Risk Title", "DECISION CONTROL", [1300, 420], 56, charcoal, 8.96, 10.24, 4);
    var riskSub = textLayer("Risk Sub", "CAPITAL ALLOCATION WITH CLEAN ESCALATION PATHS", [1300, 505], 21, graphite, 9.22, 10.18, 0);
    fade(riskTitle, 8.96, 9.18, 9.88, 10.24, 100);
    fade(riskSub, 9.22, 9.38, 9.84, 10.18, 92);
    flash("Final Transition Cut", 10.18, chalk, 30);
    sceneBg("Closing Charcoal Clear", charcoal, 10.2, DUR);
    var frame = strokeRect("Closing Trim Frame", [960, 540], [1500, 660], teal, 5, 10.32, DUR, 100);
    try {
        var frameGroup = frame.property("Contents").property(1);
        var trim = frameGroup.property("Contents").addProperty("ADBE Vector Filter - Trim");
        trim.property("ADBE Vector Trim End").setValueAtTime(10.32, 0);
        trim.property("ADBE Vector Trim End").setValueAtTime(11.04, 100);
        trim.property("ADBE Vector Trim Offset").expression = "time * 18;";
        ease(trim.property("ADBE Vector Trim End"), 84);
    } catch (err) {}
    var closeTitle = textLayer("Closing Title", "LEAD THE MARKET", [960, 510], 102, chalk, 10.44, DUR, 4);
    var closeSub = textLayer("Closing Subtitle", "Q1 LAUNCH / BOARD APPROVED", [960, 618], 32, teal, 10.86, DUR, 28);
    fade(closeTitle, 10.44, 10.78, 11.68, DUR, 100);
    fade(closeSub, 10.86, 11.08, 11.66, DUR, 96);
    key(closeTitle, "Scale", [10.44, 10.86, 11.52], [[78, 78], [106, 106], [100, 100]], 86);
    comp.openInViewer();
    app.endUndoGroup();
})();
