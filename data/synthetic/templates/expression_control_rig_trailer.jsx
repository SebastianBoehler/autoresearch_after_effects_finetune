app.beginUndoGroup("AEFT Expression Control Rig Trailer");
(function () {
    if (!app.project) app.newProject();
    var W = 1920, H = 1080, DUR = 12, FPS = 30;
    var comp = app.project.items.addComp("AEFT Expression Control Rig Trailer", W, H, 1, DUR, FPS);
    comp.bgColor = [0.018, 0.023, 0.028];
    var ink = [0.018, 0.023, 0.028], paper = [0.88, 0.93, 0.91], cyan = [0.22, 0.86, 0.76], coral = [0.94, 0.25, 0.18];
    function ease(p) { if (!p || p.numKeys < 2) return; var a = [new KeyframeEase(0, 86)]; for (var i = 1; i <= p.numKeys; i++) try { p.setTemporalEaseAtKey(i, a, a); } catch (e) {} }
    function at(p, t, v) { for (var i = 0; i < t.length; i++) p.setValueAtTime(t[i], v[i]); ease(p); }
    function root(l) { return l.property("ADBE Root Vectors Group"); }
    function group(parent, name) { var g = parent.addProperty("ADBE Vector Group"); g.name = name; return g.property("ADBE Vectors Group"); }
    function fill(g, c, o) { var f = g.addProperty("ADBE Vector Graphic - Fill"); f.property("ADBE Vector Fill Color").setValue(c); f.property("ADBE Vector Fill Opacity").setValue(o); }
    function stroke(g, c, w, o) { var s = g.addProperty("ADBE Vector Graphic - Stroke"); s.property("ADBE Vector Stroke Color").setValue(c); s.property("ADBE Vector Stroke Width").setValue(w); s.property("ADBE Vector Stroke Opacity").setValue(o || 100); }
    function rect(g, size, pos, round) { var r = g.addProperty("ADBE Vector Shape - Rect"); r.property("ADBE Vector Rect Size").setValue(size); r.property("ADBE Vector Rect Position").setValue(pos || [0, 0]); r.property("ADBE Vector Rect Roundness").setValue(round || 0); return r; }
    function ellipse(g, size, pos) { var e = g.addProperty("ADBE Vector Shape - Ellipse"); e.property("ADBE Vector Ellipse Size").setValue(size); e.property("ADBE Vector Ellipse Position").setValue(pos || [0, 0]); return e; }
    function text(s, size, c, pos, tin, tout, box) {
        var l = box ? comp.layers.addBoxText(box) : comp.layers.addText(s);
        var d = l.property("Source Text").value;
        d.text = s; d.fontSize = size; d.fillColor = c; d.applyFill = true; d.tracking = size > 46 ? 52 : 160; d.justification = ParagraphJustification.CENTER_JUSTIFY;
        try { d.font = size > 42 ? "Arial-BoldMT" : "ArialMT"; } catch (e) {}
        l.property("Source Text").setValue(d); l.property("Transform").property("Position").setValue(pos); l.inPoint = tin; l.outPoint = tout;
        at(l.property("Transform").property("Opacity"), [tin, tin + 0.12, tout - 0.18, tout], [0, 100, 100, 0]); return l;
    }
    comp.layers.addSolid(ink, "Control Rig Background", W, H, 1);
    var ctrl = comp.layers.addNull();
    ctrl.name = "AEFT CONTROL RIG";
    ctrl.enabled = false;
    var fx = ctrl.property("Effects");
    var amp = fx.addProperty("ADBE Slider Control"); amp.name = "Pulse Amplitude"; amp.property("Slider").setValue(42);
    var rate = fx.addProperty("ADBE Slider Control"); rate.name = "Pulse Rate"; rate.property("Slider").setValue(5.4);
    var angle = fx.addProperty("ADBE Angle Control"); angle.name = "Scan Angle"; angle.property("Angle").setValue(-8);
    var col = fx.addProperty("ADBE Color Control"); col.name = "Accent Color"; col.property("Color").setValue(cyan);
    var grid = comp.layers.addShape(); grid.name = "Controller Driven Micro Grid";
    var gg = group(root(grid), "tick");
    rect(gg, [2, 28], [-720, -350], 0); fill(gg, paper, 15);
    var rx = gg.addProperty("ADBE Vector Filter - Repeater");
    rx.property("ADBE Vector Repeater Copies").setValue(37);
    rx.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([40, 0]);
    var ry = gg.addProperty("ADBE Vector Filter - Repeater");
    ry.property("ADBE Vector Repeater Copies").setValue(17);
    ry.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([0, 44]);
    grid.property("Transform").property("Position").setValue([960, 540]);
    grid.property("Transform").property("Opacity").expression = "8 + thisComp.layer('AEFT CONTROL RIG').effect('Pulse Amplitude')('Slider') / 10";
    var ring = comp.layers.addShape(); ring.name = "Expression Driven Pulse Ring";
    var rg = group(root(ring), "ring");
    ellipse(rg, [560, 560], [0, 0]); stroke(rg, cyan, 2.2, 90);
    var rt = rg.addProperty("ADBE Vector Filter - Trim");
    at(rt.property("ADBE Vector Trim End"), [0.6, 2.4, 5.8, 7.1], [8, 100, 100, 35]);
    ring.property("Transform").property("Position").setValue([960, 540]);
    ring.property("Transform").property("Scale").expression = "a=thisComp.layer('AEFT CONTROL RIG').effect('Pulse Amplitude')('Slider'); r=thisComp.layer('AEFT CONTROL RIG').effect('Pulse Rate')('Slider'); s=100+Math.sin(time*r)*a/4; [s,s]";
    var blade = comp.layers.addShape(); blade.name = "Angle Control Scan Blade";
    var bg = group(root(blade), "blade");
    rect(bg, [18, H + 160], [0, 0], 0); fill(bg, paper, 92);
    blade.property("Transform").property("Rotation").expression = "thisComp.layer('AEFT CONTROL RIG').effect('Scan Angle')('Angle')";
    at(blade.property("Transform").property("Position"), [2.1, 2.64, 7.2, 7.72], [[-80, 540], [2000, 540], [2000, 540], [-80, 540]]);
    for (var i = 0; i < 5; i++) {
        var cell = comp.layers.addShape(); cell.name = "Rig Readout " + i;
        var cg = group(root(cell), "cell");
        rect(cg, [250, 138], [0, 0], 8); fill(cg, [0.88, 0.94, 0.91], i === 2 ? 92 : 76); stroke(cg, i === 2 ? coral : cyan, 2, 80);
        cell.property("Transform").property("Position").setValue([360 + i * 300, 720]);
        at(cell.property("Transform").property("Position"), [2.7 + i * 0.08, 3.12 + i * 0.08], [[360 + i * 300, 840], [360 + i * 300, 720]]);
        cell.property("Transform").property("Scale").expression = "a=thisComp.layer('AEFT CONTROL RIG').effect('Pulse Amplitude')('Slider'); [100+Math.sin(time*5+" + i + ")*a/20,100+Math.sin(time*5+" + i + ")*a/20]";
    }
    text("EXPRESSION CONTROL RIG", 68, paper, [960, 250], 0.18, 3.1, [1120, 92]);
    text("SLIDERS / ANGLE / COLOR / EXPRESSIONS", 25, cyan, [960, 334], 0.45, 3.3, [940, 54]);
    text("ONE CONTROLLER DRIVES THE SYSTEM", 42, paper, [960, 520], 3.25, 7.7, [1120, 72]);
    text("RIG LOCK", 86, paper, [960, 500], 7.86, DUR, null);
    text("EFFECT CONTROLS AS MOTION API", 26, cyan, [960, 600], 8.1, DUR, [820, 58]);
})();
app.endUndoGroup();
