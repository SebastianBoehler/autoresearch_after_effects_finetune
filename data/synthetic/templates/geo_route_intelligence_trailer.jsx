app.beginUndoGroup("AEFT Geo Route Intelligence Trailer");
(function () {
    if (!app.project) app.newProject();
    var W = 1920, H = 1080, DUR = 13, FPS = 30;
    var comp = app.project.items.addComp("AEFT Geo Route Intelligence Trailer", W, H, 1, DUR, FPS);
    comp.bgColor = [0.024, 0.033, 0.04];
    var paper = [0.88, 0.93, 0.91], mint = [0.24, 0.85, 0.74], coral = [0.95, 0.28, 0.18], ink = [0.024, 0.033, 0.04];
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
    function root(l) { return l.property("ADBE Root Vectors Group"); }
    function group(parent, name) { var g = parent.addProperty("ADBE Vector Group"); g.name = name; return g.property("ADBE Vectors Group"); }
    function fill(g, c, o) { var f = g.addProperty("ADBE Vector Graphic - Fill"); f.property("ADBE Vector Fill Color").setValue(c); f.property("ADBE Vector Fill Opacity").setValue(o); }
    function stroke(g, c, w, o) { var s = g.addProperty("ADBE Vector Graphic - Stroke"); s.property("ADBE Vector Stroke Color").setValue(c); s.property("ADBE Vector Stroke Width").setValue(w); s.property("ADBE Vector Stroke Opacity").setValue(o || 100); }
    function rect(g, size, pos, r) { var q = g.addProperty("ADBE Vector Shape - Rect"); q.property("ADBE Vector Rect Size").setValue(size); q.property("ADBE Vector Rect Position").setValue(pos || [0, 0]); q.property("ADBE Vector Rect Roundness").setValue(r || 0); return q; }
    function ellipse(g, size, pos) { var e = g.addProperty("ADBE Vector Shape - Ellipse"); e.property("ADBE Vector Ellipse Size").setValue(size); e.property("ADBE Vector Ellipse Position").setValue(pos || [0, 0]); return e; }
    function path(g, verts) { var shp = new Shape(); shp.vertices = verts; shp.closed = false; var p = g.addProperty("ADBE Vector Shape - Group"); p.property("ADBE Vector Shape").setValue(shp); return p; }
    function text(s, size, c, pos, tin, tout, box) {
        var l = box ? comp.layers.addBoxText(box) : comp.layers.addText(s);
        var d = l.property("Source Text").value;
        d.text = s; d.fontSize = size; d.fillColor = c; d.applyFill = true; d.tracking = size > 42 ? 45 : 150; d.justification = ParagraphJustification.CENTER_JUSTIFY;
        try { d.font = size > 42 ? "Arial-BoldMT" : "ArialMT"; } catch (e) {}
        l.property("Source Text").setValue(d); l.property("Transform").property("Position").setValue(pos); l.inPoint = tin; l.outPoint = tout;
        at(l.property("Transform").property("Opacity"), [tin, tin + 0.14, tout - 0.2, tout], [0, 100, 100, 0]);
    }
    var geo = readJson("route_points.geojson");
    if (geo.features[0].geometry.type !== "LineString") throw new Error("Expected GeoJSON LineString");
    var coords = geo.features[0].geometry.coordinates;
    var origin = geo.features[0].properties.origin, dest = geo.features[0].properties.destination;
    comp.layers.addSolid(ink, "Map Charcoal", W, H, 1);
    var map = comp.layers.addShape(); map.name = "GeoJSON Route Map";
    var mr = root(map);
    for (var i = 0; i < 9; i++) {
        var grid = group(mr, "grid " + i);
        rect(grid, [1.4, 760], [-640 + i * 160, 0], 0); fill(grid, paper, 10);
    }
    var verts = [];
    for (i = 0; i < coords.length; i++) {
        var lon = coords[i][0], lat = coords[i][1];
        verts.push([(lon - 12.5) * 74, (54 - lat) * 54]);
    }
    var route = group(mr, "cold chain line");
    path(route, verts);
    var trim = route.addProperty("ADBE Vector Filter - Trim");
    at(trim.property("ADBE Vector Trim End"), [1.4, 5.6], [0, 100]);
    stroke(route, mint, 5, 100);
    for (i = 0; i < verts.length; i++) {
        var dot = group(mr, "waypoint " + i);
        ellipse(dot, [24, 24], verts[i]); fill(dot, i === verts.length - 1 ? coral : paper, 100);
    }
    map.property("Transform").property("Position").setValue([960, 540]);
    at(map.property("Transform").property("Scale"), [0.8, 3.5, 8.8], [[108, 108], [122, 122], [130, 130]]);
    at(map.property("Transform").property("Opacity"), [0.6, 1.05, 10.0, 10.45], [0, 100, 100, 0]);
    var pane = comp.layers.addShape(); pane.name = "Route Data Pane";
    var pg = group(root(pane), "pane");
    rect(pg, [520, 650], [0, 0], 0); fill(pg, [0.88, 0.93, 0.9], 94); stroke(pg, mint, 2, 80);
    pane.property("Transform").property("Position").setValue([1460, 540]);
    at(pane.property("Transform").property("Position"), [5.8, 6.35], [[1700, 540], [1460, 540]]);
    text("GEOJSON ROUTE", 60, paper, [700, 210], 0.35, 4.5, [820, 84]);
    text(origin + "  /  " + dest, 30, mint, [700, 292], 0.65, 4.8, [740, 58]);
    text("COLD-CHAIN WINDOW", 26, ink, [1460, 374], 6.12, 9.8, [420, 52]);
    text("6 NODES", 78, ink, [1460, 470], 6.32, 9.8, null);
    text("LIVE ROUTE TRACE", 26, coral, [1460, 570], 6.5, 9.8, [420, 52]);
    text("ROUTE LOCK", 82, paper, [960, 500], 10.45, DUR, null);
    text("LOCAL GEOJSON / TRIM PATH / WAYPOINTS", 26, mint, [960, 596], 10.72, DUR, [920, 58]);
})();
app.endUndoGroup();
