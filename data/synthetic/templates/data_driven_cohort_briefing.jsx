app.beginUndoGroup("AEFT Data Driven Cohort Briefing");
(function () {
    if (!app.project) app.newProject();
    var W = 1920, H = 1080, DUR = 12, FPS = 30;
    var comp = app.project.items.addComp("AEFT Data Driven Cohort Briefing", W, H, 1, DUR, FPS);
    comp.bgColor = [0.025, 0.031, 0.038];
    var ink = [0.025, 0.031, 0.038], paper = [0.88, 0.93, 0.92], mint = [0.25, 0.88, 0.76], coral = [0.96, 0.27, 0.2];
    function asset(rel) {
        var roots = [];
        if ($.global.AEFT_ASSET_ROOT) roots.push($.global.AEFT_ASSET_ROOT);
        var here = new File($.fileName).parent;
        roots.push(here.parent.fsName + "/assets");
        roots.push(here.fsName + "/../assets");
        for (var i = 0; i < roots.length; i++) {
            var f = new File(roots[i] + "/" + rel);
            if (f.exists) return f;
        }
        throw new Error("Missing asset: " + rel);
    }
    function readJson(rel) {
        var f = asset(rel);
        f.encoding = "UTF-8";
        f.open("r");
        var txt = f.read();
        f.close();
        return parseJsonText(txt);
    }
    function parseJsonText(txt) {
        if (typeof JSON !== "undefined" && JSON.parse) return JSON.parse(txt);
        return (new Function("return " + txt))();
    }
    function ease(p, n) {
        if (!p || p.numKeys < 2) return;
        var a = [new KeyframeEase(0, n || 82)];
        for (var k = 1; k <= p.numKeys; k++) try { p.setTemporalEaseAtKey(k, a, a); } catch (e) {}
    }
    function at(p, t, v) {
        for (var i = 0; i < t.length; i++) p.setValueAtTime(t[i], v[i]);
        ease(p, 86);
    }
    function root(l) { return l.property("ADBE Root Vectors Group"); }
    function group(parent, name) {
        var g = parent.addProperty("ADBE Vector Group");
        g.name = name;
        return g.property("ADBE Vectors Group");
    }
    function fill(g, c, o) {
        var f = g.addProperty("ADBE Vector Graphic - Fill");
        f.property("ADBE Vector Fill Color").setValue(c);
        f.property("ADBE Vector Fill Opacity").setValue(o);
    }
    function stroke(g, c, w, o) {
        var s = g.addProperty("ADBE Vector Graphic - Stroke");
        s.property("ADBE Vector Stroke Color").setValue(c);
        s.property("ADBE Vector Stroke Width").setValue(w);
        s.property("ADBE Vector Stroke Opacity").setValue(o || 100);
    }
    function rect(g, size, pos, round) {
        var r = g.addProperty("ADBE Vector Shape - Rect");
        r.property("ADBE Vector Rect Size").setValue(size);
        r.property("ADBE Vector Rect Position").setValue(pos || [0, 0]);
        r.property("ADBE Vector Rect Roundness").setValue(round || 0);
        return r;
    }
    function path(g, verts) {
        var shp = new Shape();
        shp.vertices = verts;
        shp.closed = false;
        var p = g.addProperty("ADBE Vector Shape - Group");
        p.property("ADBE Vector Shape").setValue(shp);
        return p;
    }
    function text(txt, size, c, pos, tin, tout, box) {
        var l = box ? comp.layers.addBoxText(box) : comp.layers.addText(txt);
        var d = l.property("Source Text").value;
        d.text = txt; d.fontSize = size; d.fillColor = c; d.applyFill = true;
        d.tracking = size > 44 ? 35 : 130; d.justification = ParagraphJustification.CENTER_JUSTIFY;
        try { d.font = size > 42 ? "Arial-BoldMT" : "ArialMT"; } catch (e) {}
        l.property("Source Text").setValue(d);
        l.property("Transform").property("Position").setValue(pos);
        l.inPoint = tin; l.outPoint = tout;
        at(l.property("Transform").property("Opacity"), [tin, tin + 0.12, tout - 0.18, tout], [0, 100, 100, 0]);
        return l;
    }
    var data = readJson("cohort_metrics.json");
    var bg = comp.layers.addSolid(ink, "Data Charcoal", W, H, 1);
    bg.outPoint = DUR;
    var grid = comp.layers.addShape(); grid.name = "Fine Data Grid";
    var gr = group(root(grid), "tick");
    rect(gr, [2, 22], [-760, -350], 0); fill(gr, paper, 18);
    var repX = gr.addProperty("ADBE Vector Filter - Repeater");
    repX.property("ADBE Vector Repeater Copies").setValue(39);
    repX.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([40, 0]);
    var repY = gr.addProperty("ADBE Vector Filter - Repeater");
    repY.property("ADBE Vector Repeater Copies").setValue(17);
    repY.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([0, 44]);
    grid.property("Transform").property("Position").setValue([960, 540]);
    grid.property("Transform").property("Opacity").expression = "12 + Math.sin(time * 1.5) * 2";
    text(data.title, 62, paper, [960, 200], 0.15, DUR, [1220, 90]);
    text(data.subtitle.toUpperCase(), 24, mint, [960, 272], 0.38, DUR, [760, 48]);
    var chart = comp.layers.addShape(); chart.name = "JSON Timeline Trace";
    var cr = root(chart);
    var fr = group(cr, "frame");
    rect(fr, [1240, 420], [0, 0], 0); fill(fr, [0.055, 0.073, 0.08], 72); stroke(fr, paper, 1.4, 28);
    var verts = [];
    for (var i = 0; i < data.timeline.length; i++) verts.push([-560 + i * 185, 150 - data.timeline[i] * 285]);
    var pg = group(cr, "metric path");
    path(pg, verts);
    var trim = pg.addProperty("ADBE Vector Filter - Trim");
    at(trim.property("ADBE Vector Trim End"), [1.2, 3.35], [0, 100]);
    stroke(pg, mint, 4, 100);
    chart.property("Transform").property("Position").setValue([960, 540]);
    at(chart.property("Transform").property("Scale"), [0.8, 1.25, DUR], [[96, 96], [100, 100], [101, 101]]);
    for (i = 0; i < data.metrics.length; i++) {
        var m = data.metrics[i];
        var x = 410 + i * 365;
        var card = comp.layers.addShape(); card.name = "Metric " + m.label;
        var cg = group(root(card), "card");
        rect(cg, [295, 170], [0, 0], 8); fill(cg, [0.9, 0.95, 0.93], 94); stroke(cg, i === 2 ? coral : mint, 2, 78);
        card.property("Transform").property("Position").setValue([x, 810]);
        at(card.property("Transform").property("Position"), [3.3 + i * 0.12, 3.72 + i * 0.12], [[x, 910], [x, 810]]);
        text(m.label.toUpperCase(), 18, ink, [x, 772], 3.45 + i * 0.12, DUR, [250, 40]);
        text(String(m.value) + m.unit, 48, i === 2 ? coral : ink, [x, 828], 3.55 + i * 0.12, DUR, [260, 70]);
    }
    var wipe = comp.layers.addShape(); wipe.name = "Data Blade Transition";
    var wg = group(root(wipe), "blade");
    rect(wg, [18, H + 120], [0, 0], 0); fill(wg, paper, 92);
    at(wipe.property("Transform").property("Position"), [9.45, 10.05], [[-80, 540], [1990, 540]]);
    text("DATASET INGEST / VERIFIED LOCAL JSON", 28, mint, [960, 948], 5.4, 10.6, [980, 50]);
    text("COHORT LOCK", 78, paper, [960, 518], 10.15, DUR, null);
    text("LOCAL FILE DRIVEN AEFT SAMPLE", 26, mint, [960, 606], 10.38, DUR, [760, 58]);
})();
app.endUndoGroup();
