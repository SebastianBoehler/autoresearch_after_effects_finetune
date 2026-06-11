app.beginUndoGroup("AEFT Type Animator System Trailer");
(function () {
    if (!app.project) app.newProject();
    var W = 1920, H = 1080, DUR = 12, FPS = 30;
    var comp = app.project.items.addComp("AEFT Type Animator System Trailer", W, H, 1, DUR, FPS);
    comp.bgColor = [0.025, 0.028, 0.032];
    var paper = [0.9, 0.94, 0.92], mint = [0.23, 0.86, 0.76], coral = [0.94, 0.25, 0.18], ink = [0.025, 0.028, 0.032];
    function ease(p) { if (!p || p.numKeys < 2) return; var a = [new KeyframeEase(0, 88)]; for (var i = 1; i <= p.numKeys; i++) try { p.setTemporalEaseAtKey(i, a, a); } catch (e) {} }
    function at(p, t, v) { for (var i = 0; i < t.length; i++) p.setValueAtTime(t[i], v[i]); ease(p); }
    function root(l) { return l.property("ADBE Root Vectors Group"); }
    function group(parent, name) { var g = parent.addProperty("ADBE Vector Group"); g.name = name; return g.property("ADBE Vectors Group"); }
    function fill(g, c, o) { var f = g.addProperty("ADBE Vector Graphic - Fill"); f.property("ADBE Vector Fill Color").setValue(c); f.property("ADBE Vector Fill Opacity").setValue(o); }
    function stroke(g, c, w, o) { var s = g.addProperty("ADBE Vector Graphic - Stroke"); s.property("ADBE Vector Stroke Color").setValue(c); s.property("ADBE Vector Stroke Width").setValue(w); s.property("ADBE Vector Stroke Opacity").setValue(o || 100); }
    function rect(g, size, pos, r) { var q = g.addProperty("ADBE Vector Shape - Rect"); q.property("ADBE Vector Rect Size").setValue(size); q.property("ADBE Vector Rect Position").setValue(pos || [0, 0]); q.property("ADBE Vector Rect Roundness").setValue(r || 0); return q; }
    function text(s, size, c, pos, tin, tout, box) {
        var l = box ? comp.layers.addBoxText(box) : comp.layers.addText(s);
        var d = l.property("Source Text").value;
        d.text = s; d.fontSize = size; d.fillColor = c; d.applyFill = true; d.tracking = size > 54 ? 8 : 120; d.justification = ParagraphJustification.CENTER_JUSTIFY;
        try { d.font = size > 42 ? "Arial-BoldMT" : "ArialMT"; } catch (e) {}
        l.property("Source Text").setValue(d); l.property("Transform").property("Position").setValue(pos); l.inPoint = tin; l.outPoint = tout;
        at(l.property("Transform").property("Opacity"), [tin, tin + 0.12, tout - 0.18, tout], [0, 100, 100, 0]); return l;
    }
    comp.layers.addSolid(ink, "Type System Background", W, H, 1);
    var title = text("KINETIC LANGUAGE", 92, paper, [960, 420], 0.2, 5.15, null);
    var animators = title.property("ADBE Text Properties").property("ADBE Text Animators");
    var anim = animators.addProperty("ADBE Text Animator");
    anim.name = "Range Push Reveal";
    var props = anim.property("ADBE Text Animator Properties");
    props.addProperty("ADBE Text Position 3D").setValue([0, 74, 0]);
    props.addProperty("ADBE Text Opacity").setValue(0);
    var sel = anim.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
    at(sel.property("ADBE Text Percent Start"), [0.35, 1.08, 3.6, 4.25], [0, 100, 100, 0]);
    try { sel.property("ADBE Text Range Advanced").property("ADBE Text Selector Smoothness").setValue(68); } catch (e) {}
    var skewAnim = animators.addProperty("ADBE Text Animator");
    skewAnim.name = "Accent Skew";
    var skewProps = skewAnim.property("ADBE Text Animator Properties");
    skewProps.addProperty("ADBE Text Skew").setValue(-12);
    var skewSel = skewAnim.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
    at(skewSel.property("ADBE Text Percent End"), [1.25, 2.2], [0, 100]);
    var subtitle = text("NATIVE TEXT ANIMATORS / RANGE SELECTORS", 26, mint, [960, 520], 0.78, 5.2, [920, 54]);
    var subAnim = subtitle.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
    subAnim.name = "Subtitle Tracking Fade";
    subAnim.property("ADBE Text Animator Properties").addProperty("ADBE Text Tracking Amount").setValue(26);
    subAnim.property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity").setValue(0);
    var subSel = subAnim.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
    at(subSel.property("ADBE Text Percent Start"), [0.9, 1.8], [0, 100]);
    var rules = comp.layers.addShape(); rules.name = "Editorial Type Rules";
    var rr = root(rules);
    for (var i = 0; i < 5; i++) {
        var g = group(rr, "rule " + i);
        rect(g, [620 - i * 72, 3], [0, -210 + i * 105], 0);
        fill(g, i === 2 ? coral : mint, i === 2 ? 95 : 58);
    }
    rules.property("Transform").property("Position").setValue([960, 540]);
    at(rules.property("Transform").property("Opacity"), [1.3, 1.62, 5.0, 5.4], [0, 100, 100, 0]);
    var blade = comp.layers.addShape(); blade.name = "Type Shutter Transition";
    var bg = group(root(blade), "blade");
    rect(bg, [24, H + 160], [0, 0], 0); fill(bg, paper, 94);
    at(blade.property("Transform").property("Position"), [4.85, 5.28, 8.15, 8.56], [[-80, 540], [2000, 540], [2000, 540], [-80, 540]]);
    var lines = ["RANGE SELECTOR", "POSITION OFFSET", "OPACITY CASCADE", "TRACKING SYSTEM"];
    for (i = 0; i < lines.length; i++) {
        var l = text(lines[i], 42, i === 1 ? coral : paper, [960, 340 + i * 94], 5.35 + i * 0.1, 8.35, [920, 62]);
        var la = l.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
        la.name = "Line Reveal " + i;
        la.property("ADBE Text Animator Properties").addProperty("ADBE Text Position 3D").setValue([-80, 0, 0]);
        la.property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity").setValue(0);
        var ls = la.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
        at(ls.property("ADBE Text Percent Start"), [5.5 + i * 0.16, 6.25 + i * 0.16], [0, 100]);
    }
    text("TYPE LOCK", 88, paper, [960, 500], 8.7, DUR, null);
    text("TEXT ANIMATOR API COVERAGE", 26, mint, [960, 600], 8.95, DUR, [820, 58]);
})();
app.endUndoGroup();
