app.beginUndoGroup("AEFT Product Sequence Launch Trailer");
(function () {
    if (!app.project) app.newProject();
    var W = 1920, H = 1080, DUR = 12, FPS = 30;
    var comp = app.project.items.addComp("AEFT Product Sequence Launch Trailer", W, H, 1, DUR, FPS);
    comp.bgColor = [0.02, 0.025, 0.03];
    var paper = [0.9, 0.94, 0.92], cyan = [0.22, 0.82, 0.78], coral = [0.94, 0.24, 0.18], dark = [0.02, 0.025, 0.03];
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
    function ease(p) {
        if (!p || p.numKeys < 2) return;
        var a = [new KeyframeEase(0, 86)];
        for (var i = 1; i <= p.numKeys; i++) try { p.setTemporalEaseAtKey(i, a, a); } catch (e) {}
    }
    function at(p, t, v) {
        for (var i = 0; i < t.length; i++) p.setValueAtTime(t[i], v[i]);
        ease(p);
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
    function rect(g, size, pos, r) {
        var q = g.addProperty("ADBE Vector Shape - Rect");
        q.property("ADBE Vector Rect Size").setValue(size);
        q.property("ADBE Vector Rect Position").setValue(pos || [0, 0]);
        q.property("ADBE Vector Rect Roundness").setValue(r || 0);
        return q;
    }
    function text(s, size, c, pos, tin, tout, box) {
        var l = box ? comp.layers.addBoxText(box) : comp.layers.addText(s);
        var d = l.property("Source Text").value;
        d.text = s; d.fontSize = size; d.fillColor = c; d.applyFill = true; d.tracking = size > 42 ? 42 : 145;
        d.justification = ParagraphJustification.CENTER_JUSTIFY;
        try { d.font = size > 42 ? "Arial-BoldMT" : "ArialMT"; } catch (e) {}
        l.property("Source Text").setValue(d);
        l.property("Transform").property("Position").setValue(pos);
        l.inPoint = tin; l.outPoint = tout;
        at(l.property("Transform").property("Opacity"), [tin, tin + 0.14, tout - 0.2, tout], [0, 100, 100, 0]);
        return l;
    }
    function still(rel, name, pos, sc, tin, tout) {
        var ftg = app.project.importFile(new ImportOptions(asset(rel)));
        var l = comp.layers.add(ftg);
        l.name = name;
        l.inPoint = tin; l.outPoint = tout;
        l.property("Transform").property("Position").setValue(pos);
        at(l.property("Transform").property("Scale"), [tin, tin + 0.28, tout - 0.2], [[sc * 0.88, sc * 0.88], [sc, sc], [sc, sc]]);
        at(l.property("Transform").property("Opacity"), [tin, tin + 0.16, tout - 0.18, tout], [0, 100, 100, 0]);
        return l;
    }
    comp.layers.addSolid(dark, "Launch Charcoal", W, H, 1);
    var firstFrame = asset("product_sequence/product_0001.png");
    var opts = new ImportOptions(firstFrame);
    opts.sequence = true;
    var sequenceFootage = app.project.importFile(opts);
    sequenceFootage.name = "Synthetic Product PNG Sequence";
    var plate = comp.layers.add(sequenceFootage);
    plate.name = "Imported Product Sequence Plate";
    plate.inPoint = 1.1; plate.outPoint = 8.9;
    plate.property("Transform").property("Position").setValue([960, 536]);
    at(plate.property("Transform").property("Scale"), [1.1, 2.0, 8.6], [[116, 116], [128, 128], [150, 150]]);
    at(plate.property("Transform").property("Opacity"), [1.1, 1.5, 8.35, 8.9], [0, 100, 100, 0]);
    var placeholder = comp.layers.addSolid(cyan, "Replace Source Placeholder", 640, 360, 1);
    placeholder.replaceSource(sequenceFootage, false);
    placeholder.name = "replaceSource Imported Plate";
    placeholder.property("Transform").property("Position").setValue([960, 536]);
    placeholder.inPoint = 8.65; placeholder.outPoint = 10.7;
    at(placeholder.property("Transform").property("Scale"), [8.65, 9.15, 10.55], [[98, 98], [145, 145], [170, 170]]);
    at(placeholder.property("Transform").property("Opacity"), [8.65, 9.05, 10.45, 10.7], [0, 100, 100, 0]);
    var hero = still("product_sequence/product_0004.png", "Hero Imported PNG Frame 0004", [960, 536], 154, 3.85, 8.9);
    hero.moveBefore(placeholder);
    still("product_sequence/product_0001.png", "Reference Frame 0001", [420, 820], 38, 2.45, 8.9);
    still("product_sequence/product_0002.png", "Reference Frame 0002", [780, 820], 38, 2.55, 8.9);
    still("product_sequence/product_0003.png", "Reference Frame 0003", [1140, 820], 38, 2.65, 8.9);
    still("product_sequence/product_0004.png", "Reference Frame 0004", [1500, 820], 38, 2.75, 8.9);
    var matte = comp.layers.addShape(); matte.name = "Imported Plate Reveal Matte";
    var mg = group(root(matte), "aperture");
    var mr = rect(mg, [0, 640], [-480, 0], 0);
    at(mr.property("ADBE Vector Rect Size"), [1.08, 1.85], [[0, 640], [1280, 640]]);
    fill(mg, [1, 1, 1], 100);
    matte.property("Transform").property("Position").setValue([960, 540]);
    matte.moveBefore(plate);
    if (typeof TrackMatteType !== "undefined") plate.trackMatteType = TrackMatteType.ALPHA;
    var frame = comp.layers.addShape(); frame.name = "Swiss Product Frame";
    var fr = group(root(frame), "frame");
    rect(fr, [1260, 700], [0, 0], 0); stroke(fr, paper, 1.6, 45);
    var mark = group(root(frame), "signal mark");
    rect(mark, [160, 5], [-520, -310], 0); fill(mark, coral, 90);
    frame.property("Transform").property("Position").setValue([960, 540]);
    at(frame.property("Transform").property("Opacity"), [0.4, 0.9, 10.4, 10.9], [0, 100, 100, 0]);
    var blade = comp.layers.addShape(); blade.name = "Product Cut Blade";
    var bg = group(root(blade), "blade");
    rect(bg, [24, H + 160], [0, 0], 0); fill(bg, paper, 95);
    at(blade.property("Transform").property("Position"), [0.0, 0.66, 10.65, 11.08], [[-100, 540], [2020, 540], [-80, 540], [2000, 540]]);
    text("SYNTHETIC PRODUCT SEQUENCE", 56, paper, [960, 216], 0.45, 3.2, [1120, 86]);
    text("PNG IMAGE SEQUENCE / IMPORTOPTIONS", 24, cyan, [960, 292], 0.75, 3.4, [920, 50]);
    text("VISIBLE LOCAL PNG FRAMES 0001-0004", 25, cyan, [960, 934], 2.7, 8.8, [920, 52]);
    text("SOURCE REPLACEMENT / LOCAL FOOTAGE", 26, paper, [960, 170], 4.1, 8.7, [900, 54]);
    text("LAUNCH PLATE", 78, paper, [960, 500], 10.75, DUR, null);
    text("ASSET-BACKED AE SCRIPT", 26, cyan, [960, 590], 10.95, DUR, [740, 56]);
})();
app.endUndoGroup();
