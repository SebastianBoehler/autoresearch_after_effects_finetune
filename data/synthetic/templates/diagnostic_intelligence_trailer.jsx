app.beginUndoGroup("AEFT Diagnostic Intelligence Trailer");
(function () {
    var W = 1920;
    var H = 1080;
    var FPS = 30;
    var DUR = 13;
    if (!app.project) app.newProject();
    var comp = app.project.items.addComp("AEFT Diagnostic Intelligence Trailer", W, H, 1, DUR, FPS);
    comp.bgColor = [0.025, 0.035, 0.045];
    var ink = [0.025, 0.035, 0.045];
    var veil = [0.055, 0.075, 0.085];
    var mint = [0.24, 0.88, 0.78];
    var coral = [0.95, 0.27, 0.22];
    var paper = [0.86, 0.93, 0.92];
    var slate = [0.13, 0.22, 0.25];
    function ease(prop, influence) {
        if (!prop || prop.numKeys < 2) return;
        var dims = 1;
        try {
            if (prop.propertyValueType === PropertyValueType.TwoD || prop.propertyValueType === PropertyValueType.TwoD_SPATIAL) dims = 2;
            if (prop.propertyValueType === PropertyValueType.ThreeD || prop.propertyValueType === PropertyValueType.ThreeD_SPATIAL) dims = 3;
        } catch (dimErr) {}
        var i;
        var d;
        for (i = 1; i <= prop.numKeys; i++) {
            var ei = [];
            var eo = [];
            for (d = 0; d < dims; d++) {
                ei.push(new KeyframeEase(0, influence));
                eo.push(new KeyframeEase(0, influence));
            }
            try {
                prop.setTemporalEaseAtKey(i, ei, eo);
            } catch (e) {}
        }
    }
    function at(prop, times, values, influence) {
        var i;
        for (i = 0; i < times.length; i++) prop.setValueAtTime(times[i], values[i]);
        ease(prop, influence || 82);
    }
    function root(layer) { return layer.property("ADBE Root Vectors Group"); }
    function group(parent, name) {
        var g = parent.addProperty("ADBE Vector Group");
        g.name = name;
        return g.property("ADBE Vectors Group");
    }
    function fill(g, color, opacity) {
        var f = g.addProperty("ADBE Vector Graphic - Fill");
        f.property("ADBE Vector Fill Color").setValue(color);
        f.property("ADBE Vector Fill Opacity").setValue(opacity);
    }
    function stroke(g, color, width, opacity) {
        var s = g.addProperty("ADBE Vector Graphic - Stroke");
        s.property("ADBE Vector Stroke Color").setValue(color);
        s.property("ADBE Vector Stroke Width").setValue(width);
        s.property("ADBE Vector Stroke Opacity").setValue(opacity || 100);
    }
    function rect(g, size, pos, round) {
        var r = g.addProperty("ADBE Vector Shape - Rect");
        r.property("ADBE Vector Rect Size").setValue(size);
        r.property("ADBE Vector Rect Position").setValue(pos || [0, 0]);
        r.property("ADBE Vector Rect Roundness").setValue(round || 0);
        return r;
    }
    function ellipse(g, size, pos) {
        var e = g.addProperty("ADBE Vector Shape - Ellipse");
        e.property("ADBE Vector Ellipse Size").setValue(size);
        e.property("ADBE Vector Ellipse Position").setValue(pos || [0, 0]);
        return e;
    }
    function path(g, verts) {
        var shp = new Shape();
        shp.vertices = verts;
        shp.closed = false;
        var p = g.addProperty("ADBE Vector Shape - Group");
        p.property("ADBE Vector Shape").setValue(shp);
        return p;
    }
    function layer(name, tin, tout) {
        var l = comp.layers.addShape();
        l.name = name;
        l.inPoint = tin;
        l.outPoint = tout;
        return l;
    }
    function text(txt, size, color, pos, tin, tout, box, align) {
        var l;
        try {
            l = box ? comp.layers.addBoxText(box) : comp.layers.addText(txt);
        } catch (e) {
            l = comp.layers.addText(txt);
        }
        var d = l.property("Source Text").value;
        d.text = txt;
        d.fontSize = size;
        d.fillColor = color;
        d.applyFill = true;
        d.tracking = size > 46 ? 62 : 180;
        d.justification = align || ParagraphJustification.CENTER_JUSTIFY;
        try { d.font = size > 42 ? "Arial-BoldMT" : "ArialMT"; } catch (fontErr) {}
        l.property("Source Text").setValue(d);
        l.property("Transform").property("Position").setValue(pos);
        l.inPoint = tin;
        l.outPoint = tout;
        at(l.property("Transform").property("Opacity"), [tin, tin + 0.12, tout - 0.18, tout], [0, 100, 100, 0], 88);
        return l;
    }
    function mark(t, label) {
        try { comp.markerProperty.setValueAtTime(t, new MarkerValue(label)); } catch (e) {}
    }
    mark(0, "calibration hairline");
    mark(2.4, "masked tissue atlas");
    mark(5.25, "signal extraction");
    mark(7.3, "cohort lanes");
    mark(9.75, "sequencing lock");
    mark(11.15, "final title");
    comp.layers.addSolid(ink, "Deep Instrument Background", W, H, 1);
    var dots = layer("Subtle Repeater Dot Matrix", 0, DUR);
    var dg = group(root(dots), "dot");
    ellipse(dg, [3, 3], [-820, -420]);
    fill(dg, paper, 13);
    var dr1 = dg.addProperty("ADBE Vector Filter - Repeater");
    dr1.property("ADBE Vector Repeater Copies").setValue(42);
    dr1.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([40, 0]);
    var dr2 = dg.addProperty("ADBE Vector Filter - Repeater");
    dr2.property("ADBE Vector Repeater Copies").setValue(20);
    dr2.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([0, 44]);
    dots.property("Transform").property("Position").setValue([960, 540]);
    dots.property("Transform").property("Opacity").expression = "7 + Math.sin(time * 1.2) * 2";
    var vignette = comp.layers.addSolid([0, 0, 0], "Soft Masked Lens Falloff", W, H, 1);
    var mask = vignette.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
    var maskShape = new Shape();
    maskShape.vertices = [[120, 90], [1800, 90], [1800, 990], [120, 990]];
    maskShape.closed = true;
    mask.inverted = true;
    mask.property("ADBE Mask Shape").setValue(maskShape);
    mask.property("ADBE Mask Feather").setValue([260, 260]);
    vignette.property("Transform").property("Opacity").setValue(52);
    var atlas = app.project.items.addComp("AEFT Diagnostic Tissue Atlas", W, H, 1, DUR, FPS);
    atlas.bgColor = ink;
    atlas.layers.addSolid([0.035, 0.05, 0.055], "Atlas Plate", W, H, 1);
    var tissue = atlas.layers.addShape();
    tissue.name = "Tissue Contour Field";
    var tr = root(tissue);
    var i;
    for (i = 0; i < 18; i++) {
        var x = -790 + (i % 6) * 315 + ((i * 37) % 42);
        var y = -315 + Math.floor(i / 6) * 285 + ((i * 53) % 42);
        var r = 46 + ((i * 29) % 38);
        var cg = group(tr, "contour " + i);
        ellipse(cg, [r * 2.2, r * 1.55], [x, y]);
        stroke(cg, mint, 1.4, 45);
        fill(cg, [0.07, 0.2, 0.2], 16);
        var ng = group(tr, "index " + i);
        rect(ng, [22, 2], [x + r * 0.35, y - 2], 0);
        fill(ng, paper, 40);
    }
    at(tissue.property("Transform").property("Scale"), [0, DUR], [[102, 102], [110, 110]], 56);
    var atlasLayer = comp.layers.add(atlas);
    atlasLayer.name = "Nested Tissue Atlas Matte Plate";
    atlasLayer.inPoint = 2.15;
    atlasLayer.outPoint = 5.55;
    at(atlasLayer.property("Transform").property("Opacity"), [2.15, 2.45, 5.1, 5.55], [0, 92, 92, 0], 88);
    var matte = layer("Precision Scan Alpha Matte", 2.12, 3.8);
    var mg = group(root(matte), "moving aperture");
    var mr = rect(mg, [0, 760], [-500, 0], 0);
    at(mr.property("ADBE Vector Rect Size"), [2.18, 3.55], [[0, 760], [1500, 760]], 90);
    at(mr.property("ADBE Vector Rect Position"), [2.18, 3.55], [[-720, 0], [0, 0]], 90);
    fill(mg, [1, 1, 1], 100);
    matte.property("Transform").property("Position").setValue([960, 540]);
    matte.moveBefore(atlasLayer);
    if (typeof TrackMatteType !== "undefined") atlasLayer.trackMatteType = TrackMatteType.ALPHA;
    var cal = layer("Calibration Trim Hairline", 0, 2.6);
    var cl = group(root(cal), "draw");
    path(cl, [[-680, 0], [680, 0]]);
    var trim = cl.addProperty("ADBE Vector Filter - Trim");
    at(trim.property("ADBE Vector Trim End"), [0.12, 0.86], [0, 100], 92);
    stroke(cl, mint, 2, 95);
    cal.property("Transform").property("Position").setValue([960, 540]);
    var ruler = layer("Calibration Ruler Ticks", 0.55, 2.65);
    var rg = group(root(ruler), "tick");
    rect(rg, [2, 46], [-640, 0], 0);
    fill(rg, paper, 62);
    var rr = rg.addProperty("ADBE Vector Filter - Repeater");
    rr.property("ADBE Vector Repeater Copies").setValue(33);
    rr.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([40, 0]);
    ruler.property("Transform").property("Position").setValue([960, 540]);
    at(ruler.property("Transform").property("Opacity"), [0.55, 0.74, 2.24, 2.65], [0, 100, 100, 0], 82);
    var blade = layer("Instrument Wipe Blade", 1.94, 2.55);
    var bg = group(root(blade), "blade");
    rect(bg, [18, H + 220], [0, 0], 0);
    fill(bg, paper, 94);
    at(blade.property("Transform").property("Position"), [1.94, 2.42], [[-70, 540], [1990, 540]], 94);
    blade.property("Transform").property("Rotation").setValue(-7);
    text("DXI / PRECISION DIAGNOSTICS", 34, paper, [960, 468], 0.18, 2.05, [980, 70], ParagraphJustification.CENTER_JUSTIFY);
    text("SYSTEM CALIBRATING", 20, mint, [960, 600], 0.72, 2.1, [720, 46], ParagraphJustification.CENTER_JUSTIFY);
    text("TISSUE ATLAS 0042", 28, paper, [960, 172], 2.46, 5.15, [620, 52], ParagraphJustification.CENTER_JUSTIFY);
    text("MASKED MORPHOLOGY / LIVE CONTRAST NORMALIZATION", 24, mint, [960, 914], 2.68, 5.2, [980, 52], ParagraphJustification.CENTER_JUSTIFY);
    var scanner = layer("Thin Scanline Sweep", 2.38, 5.28);
    var sg = group(root(scanner), "scan");
    rect(sg, [1460, 4], [0, 0], 0);
    fill(sg, mint, 90);
    scanner.property("Transform").property("Position").setValue([960, 250]);
    at(scanner.property("Transform").property("Position"), [2.42, 4.96], [[960, 210], [960, 870]], 78);
    scanner.property("Transform").property("Opacity").expression = "72 + Math.sin(time * 18) * 18";
    var signal = layer("Signal Extraction Stage", 5.05, 7.65);
    var sr = root(signal);
    var frame = group(sr, "hairline frame");
    rect(frame, [1280, 390], [0, 0], 0);
    stroke(frame, paper, 1.4, 28);
    fill(frame, veil, 66);
    for (i = 0; i < 6; i++) {
        var gg = group(sr, "ruler " + i);
        rect(gg, [1, 330], [-520 + i * 208, 0], 0);
        fill(gg, paper, 12);
    }
    var wave = group(sr, "biometric path");
    path(wave, [[-560, 74], [-420, 74], [-350, 18], [-292, 126], [-232, -92], [-172, 74], [-42, 74], [48, 18], [108, 102], [184, -44], [278, 58], [560, 58]]);
    var wt = wave.addProperty("ADBE Vector Filter - Trim");
    at(wt.property("ADBE Vector Trim End"), [5.28, 6.48], [0, 100], 92);
    stroke(wave, mint, 3.2, 100);
    signal.property("Transform").property("Position").setValue([960, 542]);
    at(signal.property("Transform").property("Opacity"), [5.05, 5.28, 7.25, 7.65], [0, 100, 100, 0], 84);
    text("SIGNAL EXTRACTION", 38, paper, [960, 266], 5.24, 7.35, [760, 64], ParagraphJustification.CENTER_JUSTIFY);
    var score = text("CONFIDENCE  00.0", 26, mint, [960, 806], 5.54, 7.35, [620, 52], ParagraphJustification.CENTER_JUSTIFY);
    score.property("Source Text").expression = "\"CONFIDENCE  \" + (Math.min(98.7, Math.floor((time - 5.5) * 60) / 10 + 91.2)).toFixed(1)";
    var cohort = layer("Cohort Lane System", 7.2, 9.92);
    var cr = root(cohort);
    for (i = 0; i < 4; i++) {
        var lane = group(cr, "lane " + i);
        rect(lane, [260, 470], [-450 + i * 300, 0], 0);
        stroke(lane, i === 2 ? coral : paper, 1.4, i === 2 ? 90 : 32);
        fill(lane, [0.8, 0.92, 0.88], i === 2 ? 14 : 7);
        var cap = group(cr, "cap " + i);
        rect(cap, [180, 4], [-450 + i * 300, -166], 0);
        fill(cap, i === 2 ? coral : mint, 80);
    }
    cohort.property("Transform").property("Position").setValue([960, 540]);
    at(cohort.property("Transform").property("Scale"), [7.2, 7.68, 9.72], [[98, 98], [100, 100], [102, 102]], 76);
    at(cohort.property("Transform").property("Opacity"), [7.2, 7.48, 9.54, 9.92], [0, 100, 100, 0], 84);
    text("COHORT RESPONSE", 34, paper, [960, 274], 7.44, 9.55, [720, 64], ParagraphJustification.CENTER_JUSTIFY);
    text("98.7", 82, mint, [510, 534], 7.62, 9.48, null, ParagraphJustification.CENTER_JUSTIFY);
    text("96.2", 82, paper, [810, 534], 7.72, 9.48, null, ParagraphJustification.CENTER_JUSTIFY);
    text("03:18", 72, coral, [1110, 536], 7.82, 9.48, null, ParagraphJustification.CENTER_JUSTIFY);
    text("24K", 82, paper, [1410, 534], 7.92, 9.48, null, ParagraphJustification.CENTER_JUSTIFY);
    var rings = layer("Sequencing Calibration Rings", 9.55, 11.45);
    var rrRoot = root(rings);
    for (i = 0; i < 4; i++) {
        var ring = group(rrRoot, "ring " + i);
        ellipse(ring, [260 + i * 112, 260 + i * 112], [0, 0]);
        var ringTrim = ring.addProperty("ADBE Vector Filter - Trim");
        ringTrim.property("ADBE Vector Trim Start").setValue(10 + i * 8);
        at(ringTrim.property("ADBE Vector Trim End"), [9.72 + i * 0.08, 10.72 + i * 0.08], [12, 94], 88);
        stroke(ring, i === 1 ? coral : mint, 1.8, 84 - i * 12);
    }
    var bars = group(rrRoot, "barcode tick");
    rect(bars, [8, 82], [-430, 0], 0);
    fill(bars, paper, 70);
    var br = bars.addProperty("ADBE Vector Filter - Repeater");
    br.property("ADBE Vector Repeater Copies").setValue(34);
    br.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([26, 0]);
    rings.property("Transform").property("Position").setValue([960, 540]);
    rings.property("Transform").property("Rotation").expression = "time * 8";
    at(rings.property("Transform").property("Opacity"), [9.55, 9.85, 11.1, 11.45], [0, 100, 100, 0], 82);
    text("GENOMIC LOCK", 36, paper, [960, 270], 9.86, 11.18, [620, 64], ParagraphJustification.CENTER_JUSTIFY);
    var lock = layer("Final Hairline Lockup", 10.92, DUR);
    var lr = root(lock);
    var top = group(lr, "top line");
    path(top, [[-520, -110], [520, -110]]);
    var bottom = group(lr, "bottom line");
    path(bottom, [[-380, 118], [380, 118]]);
    var lt = top.addProperty("ADBE Vector Filter - Trim");
    var lb = bottom.addProperty("ADBE Vector Filter - Trim");
    at(lt.property("ADBE Vector Trim End"), [10.98, 11.42], [0, 100], 94);
    at(lb.property("ADBE Vector Trim End"), [11.14, 11.62], [0, 100], 90);
    stroke(top, mint, 2, 100);
    stroke(bottom, paper, 1.6, 62);
    lock.property("Transform").property("Position").setValue([960, 540]);
    text("CLINICAL SIGNAL", 82, paper, [960, 504], 11.18, DUR, null, ParagraphJustification.CENTER_JUSTIFY);
    text("DIAGNOSTIC INTELLIGENCE SYSTEM", 28, mint, [960, 592], 11.38, DUR, [820, 60], ParagraphJustification.CENTER_JUSTIFY);
})();
app.endUndoGroup();
