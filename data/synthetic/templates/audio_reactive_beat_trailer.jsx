app.beginUndoGroup("AEFT Audio Reactive Beat Trailer");
(function () {
    if (!app.project) app.newProject();
    var W = 1920, H = 1080, DUR = 12, FPS = 30;
    var comp = app.project.items.addComp("AEFT Audio Reactive Beat Trailer", W, H, 1, DUR, FPS);
    comp.bgColor = [0.018, 0.018, 0.024];
    var paper = [0.9, 0.94, 0.92], cyan = [0.25, 0.86, 0.78], mag = [0.88, 0.2, 0.46], dark = [0.018, 0.018, 0.024];
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
        var f = asset(rel); f.encoding = "UTF-8"; f.open("r");
        var txt = f.read(); f.close(); return parseJsonText(txt);
    }
    function parseJsonText(txt) {
        if (typeof JSON !== "undefined" && JSON.parse) return JSON.parse(txt);
        return (new Function("return " + txt))();
    }
    function ease(p) {
        if (!p || p.numKeys < 2) return;
        var a = [new KeyframeEase(0, 88)];
        for (var i = 1; i <= p.numKeys; i++) try { p.setTemporalEaseAtKey(i, a, a); } catch (e) {}
    }
    function at(p, t, v) { for (var i = 0; i < t.length; i++) p.setValueAtTime(t[i], v[i]); ease(p); }
    function root(l) { return l.property("ADBE Root Vectors Group"); }
    function group(parent, name) { var g = parent.addProperty("ADBE Vector Group"); g.name = name; return g.property("ADBE Vectors Group"); }
    function fill(g, c, o) { var f = g.addProperty("ADBE Vector Graphic - Fill"); f.property("ADBE Vector Fill Color").setValue(c); f.property("ADBE Vector Fill Opacity").setValue(o); }
    function rect(g, size, pos, r) { var q = g.addProperty("ADBE Vector Shape - Rect"); q.property("ADBE Vector Rect Size").setValue(size); q.property("ADBE Vector Rect Position").setValue(pos || [0, 0]); q.property("ADBE Vector Rect Roundness").setValue(r || 0); return q; }
    function ellipse(g, size, pos) { var e = g.addProperty("ADBE Vector Shape - Ellipse"); e.property("ADBE Vector Ellipse Size").setValue(size); e.property("ADBE Vector Ellipse Position").setValue(pos || [0, 0]); return e; }
    function text(s, size, c, pos, tin, tout, box) {
        var l = box ? comp.layers.addBoxText(box) : comp.layers.addText(s);
        var d = l.property("Source Text").value;
        d.text = s; d.fontSize = size; d.fillColor = c; d.applyFill = true; d.tracking = size > 44 ? 50 : 150; d.justification = ParagraphJustification.CENTER_JUSTIFY;
        try { d.font = size > 42 ? "Arial-BoldMT" : "ArialMT"; } catch (e) {}
        l.property("Source Text").setValue(d); l.property("Transform").property("Position").setValue(pos); l.inPoint = tin; l.outPoint = tout;
        at(l.property("Transform").property("Opacity"), [tin, tin + 0.08, tout - 0.12, tout], [0, 100, 100, 0]);
        return l;
    }
    var beats = readJson("beat_markers.json");
    comp.layers.addSolid(dark, "Beat Charcoal", W, H, 1);
    var audioOpts = new ImportOptions(asset("signal_pulse.wav"));
    var audio = app.project.importFile(audioOpts);
    var audioLayer = comp.layers.add(audio);
    audioLayer.name = "Imported Local WAV Pulse";
    audioLayer.startTime = 0;
    audioLayer.outPoint = audio.duration;
    for (var i = 0; i < beats.beats.length; i++) {
        try { comp.markerProperty.setValueAtTime(beats.beats[i], new MarkerValue("beat " + (i + 1))); } catch (e) {}
    }
    var bars = comp.layers.addShape(); bars.name = "Beat Marker Bar Array";
    var br = root(bars);
    for (i = 0; i < 12; i++) {
        var g = group(br, "bar " + i);
        rect(g, [16, 120 + (i % 4) * 70], [-520 + i * 95, 0], 3);
        fill(g, i % 3 === 0 ? mag : cyan, 78);
    }
    bars.property("Transform").property("Position").setValue([960, 640]);
    bars.property("Transform").property("Scale").expression = "s = 94 + Math.sin(time * " + beats.bpm + " / 9.55) * 9; [s, s]";
    at(bars.property("Transform").property("Opacity"), [0.15, 0.38, 10.1, 10.45], [0, 100, 100, 0]);
    for (i = 0; i < 8; i++) {
        var b = beats.beats[i] + 0.05;
        var burst = comp.layers.addShape(); burst.name = "Beat Burst " + i;
        var rg = group(root(burst), "ring");
        ellipse(rg, [160 + i * 14, 160 + i * 14], [0, 0]); fill(rg, i % 2 ? mag : cyan, 10);
        burst.property("Transform").property("Position").setValue([360 + (i % 4) * 400, 315 + Math.floor(i / 4) * 410]);
        at(burst.property("Transform").property("Scale"), [b, b + 0.22], [[20, 20], [118, 118]]);
        at(burst.property("Transform").property("Opacity"), [b, b + 0.05, b + 0.24], [0, 100, 0]);
    }
    var cut = comp.layers.addShape(); cut.name = "Beat Cut Blade";
    var cg = group(root(cut), "blade");
    rect(cg, [20, H + 160], [0, 0], 0); fill(cg, paper, 96);
    at(cut.property("Transform").property("Position"), [3.62, 3.86, 7.38, 7.64], [[-80, 540], [2000, 540], [2000, 540], [-80, 540]]);
    text("AUDIO REACTIVE CUT", 70, paper, [960, 282], 0.22, 3.8, [1040, 94]);
    text("LOCAL WAV + BEAT JSON MARKERS", 26, cyan, [960, 370], 0.5, 4.0, [880, 54]);
    text("MARKER-SYNCED BURSTS", 74, paper, [960, 486], 4.05, 7.65, [1120, 96]);
    text("PULSE LOCK", 84, paper, [960, 500], 7.84, DUR, null);
    text("AUDIO FOOTAGE / JSON TIMING / EXPRESSIONS", 25, cyan, [960, 596], 8.1, DUR, [960, 54]);
})();
app.endUndoGroup();
