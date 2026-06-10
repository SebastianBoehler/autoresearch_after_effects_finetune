app.beginUndoGroup("AEFT Procedural Material Lab");
(function () {
    if (!app.project) app.newProject();
    var W = 1920, H = 1080, DUR = 12, FPS = 30;
    var comp = app.project.items.addComp("AEFT Procedural Material Lab", W, H, 1, DUR, FPS);
    comp.bgColor = [0.025, 0.026, 0.03];
    var paper = [0.88, 0.92, 0.9], ink = [0.025, 0.026, 0.03], cyan = [0.22, 0.84, 0.76];
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
    function readJson(rel) { var f = asset(rel); f.encoding = "UTF-8"; f.open("r"); var s = f.read(); f.close(); return parseJsonText(s); }
    function parseJsonText(txt) { if (typeof JSON !== "undefined" && JSON.parse) return JSON.parse(txt); return (new Function("return " + txt))(); }
    function ease(p) { if (!p || p.numKeys < 2) return; var a = [new KeyframeEase(0, 84)]; for (var i = 1; i <= p.numKeys; i++) try { p.setTemporalEaseAtKey(i, a, a); } catch (e) {} }
    function at(p, t, v) { for (var i = 0; i < t.length; i++) p.setValueAtTime(t[i], v[i]); ease(p); }
    function text(s, size, c, pos, tin, tout, box) {
        var l = box ? comp.layers.addBoxText(box) : comp.layers.addText(s);
        var d = l.property("Source Text").value;
        d.text = s; d.fontSize = size; d.fillColor = c; d.applyFill = true; d.tracking = size > 42 ? 45 : 150; d.justification = ParagraphJustification.CENTER_JUSTIFY;
        try { d.font = size > 42 ? "Arial-BoldMT" : "ArialMT"; } catch (e) {}
        l.property("Source Text").setValue(d); l.property("Transform").property("Position").setValue(pos); l.inPoint = tin; l.outPoint = tout;
        at(l.property("Transform").property("Opacity"), [tin, tin + 0.15, tout - 0.2, tout], [0, 100, 100, 0]);
        return l;
    }
    var data = readJson("material_palette.json");
    comp.layers.addSolid(ink, "Material Lab Base", W, H, 1);
    var pre = app.project.items.addComp("AEFT Material Shader Plates", 900, 520, 1, DUR, FPS);
    for (var i = 0; i < data.swatches.length; i++) {
        var sw = data.swatches[i];
        var solid = pre.layers.addSolid(sw.rgb, "shader " + sw.name, 360, 220, 1);
        solid.property("Transform").property("Position").setValue([250 + (i % 2) * 400, 170 + Math.floor(i / 2) * 240]);
        try {
            var noise = solid.property("Effects").addProperty("ADBE Fractal Noise");
            noise.property("Contrast").setValue(58 + sw.roughness * 55);
            noise.property("Brightness").setValue(-8);
        } catch (nErr) {}
        try {
            var glow = solid.property("Effects").addProperty("ADBE Glow");
            glow.property("Glow Threshold").setValue(70);
            glow.property("Glow Radius").setValue(18 + sw.roughness * 24);
        } catch (gErr) {}
    }
    var plate = comp.layers.add(pre);
    plate.name = "Nested Procedural Material Plates";
    plate.property("Transform").property("Position").setValue([960, 540]);
    at(plate.property("Transform").property("Scale"), [0.8, 1.6, 9.2], [[82, 82], [100, 100], [110, 110]]);
    at(plate.property("Transform").property("Opacity"), [0.5, 1.0, 9.7, 10.1], [0, 100, 100, 0]);
    var scan = comp.layers.addShape(); scan.name = "Material Scanline";
    var root = scan.property("ADBE Root Vectors Group");
    var g = root.addProperty("ADBE Vector Group").property("ADBE Vectors Group");
    var r = g.addProperty("ADBE Vector Shape - Rect");
    r.property("ADBE Vector Rect Size").setValue([1040, 5]);
    var f = g.addProperty("ADBE Vector Graphic - Fill");
    f.property("ADBE Vector Fill Color").setValue(cyan);
    f.property("ADBE Vector Fill Opacity").setValue(90);
    scan.property("Transform").property("Position").setValue([960, 275]);
    at(scan.property("Transform").property("Position"), [1.1, 5.8], [[960, 280], [960, 800]]);
    scan.property("Transform").property("Opacity").expression = "65 + Math.sin(time * 14) * 25";
    text(data.title, 66, paper, [960, 196], 0.24, 4.2, [1120, 88]);
    text("LOCAL JSON PALETTE / BUILT-IN EFFECT MATERIALS", 25, cyan, [960, 280], 0.55, 4.4, [1000, 54]);
    for (i = 0; i < data.swatches.length; i++) {
        text(data.swatches[i].name.toUpperCase(), 22, paper, [600 + (i % 2) * 720, 760 + Math.floor(i / 2) * 72], 4.8 + i * 0.12, 9.8, [420, 46]);
    }
    text("PROCEDURAL MATERIAL LOCK", 70, paper, [960, 500], 10.05, DUR, [1120, 90]);
    text("FRACTAL NOISE / GLOW / NESTED COMP", 26, cyan, [960, 594], 10.3, DUR, [940, 58]);
})();
app.endUndoGroup();
