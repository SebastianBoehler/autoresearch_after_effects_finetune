(function () {
    app.beginUndoGroup("AEFT Map Route Reveal");
    var comp = app.project.items.addComp("AEFT Map Route Reveal", 1920, 1080, 1, 7, 30);
    comp.bgColor = [0.7, 0.84, 0.78];

    function addRect(name, pos, size, color) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        return layer;
    }

    function addCircle(name, pos, radius, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("ADBE Vector Ellipse Size").setValue([radius * 2, radius * 2]);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Scale").setValueAtTime(delay, [0, 0]);
        layer.property("Transform").property("Scale").setValueAtTime(delay + 0.35, [100, 100]);
        return layer;
    }

    function addText(name, value, pos, size, color, delay) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.35, 100);
        return layer;
    }

    for (var i = 0; i < 9; i++) {
        addRect("Map Road H " + i, [960, 180 + i * 95], [1540, 8], [0.34, 0.48, 0.42]);
        addRect("Map Road V " + i, [210 + i * 190, 540], [8, 760], [0.34, 0.48, 0.42]);
    }
    var radar = addRect("Map Radar Sweep", [-120, 540], [140, 880], [0.9, 1, 0.78]);
    radar.property("Transform").property("Opacity").setValue(26);
    radar.property("Transform").property("Rotation").setValue(-8);
    radar.property("Transform").property("Position").setValueAtTime(0.4, [-120, 540]);
    radar.property("Transform").property("Position").setValueAtTime(6.5, [2040, 540]);
    addRect("Map Header Band", [960, 112], [1660, 112], [0.05, 0.13, 0.12]);
    var route = addRect("Animated Route", [960, 540], [1160, 24], [0.08, 0.42, 0.9]);
    route.property("Transform").property("Scale").setValueAtTime(0.5, [0, 100]);
    route.property("Transform").property("Scale").setValueAtTime(4.3, [100, 100]);
    route.property("Transform").property("Rotation").setValue(-12);
    var cities = [["BER", 430, 660], ["PRG", 820, 580], ["VIE", 1210, 500], ["BUD", 1510, 430]];
    for (var j = 0; j < cities.length; j++) {
        addCircle("Pin " + cities[j][0], [cities[j][1], cities[j][2]], 32, [0.96, 0.2, 0.18], 0.8 + j * 0.65);
        addText("City " + cities[j][0], cities[j][0], [cities[j][1] - 28, cities[j][2] - 54], 30, [0.08, 0.12, 0.12], 1.0 + j * 0.65);
    }
    var pulse = addCircle("Route Pulse", [430, 660], 54, [1, 0.86, 0.16], 1.0);
    pulse.property("Transform").property("Opacity").setValue(70);
    pulse.property("Transform").property("Position").setValueAtTime(1.0, [430, 660]);
    pulse.property("Transform").property("Position").setValueAtTime(2.2, [820, 580]);
    pulse.property("Transform").property("Position").setValueAtTime(3.6, [1210, 500]);
    pulse.property("Transform").property("Position").setValueAtTime(4.8, [1510, 430]);
    var plane = addText("Route Plane", ">", [420, 620], 72, [0.08, 0.42, 0.9], 1.0);
    plane.property("Transform").property("Position").setValueAtTime(1.0, [420, 620]);
    plane.property("Transform").property("Position").setValueAtTime(4.8, [1510, 430]);
    plane.property("Transform").property("Rotation").setValue(-12);
    for (var b = 0; b < 5; b++) {
        var blip = addCircle("Traffic Blip " + b, [430, 660], 18, [0.08, 0.42, 0.9], 1.2 + b * 0.2);
        blip.property("Transform").property("Position").setValueAtTime(1.2 + b * 0.3, [430, 660]);
        blip.property("Transform").property("Position").setValueAtTime(3.0 + b * 0.2, [920, 560]);
        blip.property("Transform").property("Position").setValueAtTime(5.4 + b * 0.1, [1510, 430]);
        blip.property("Transform").property("Opacity").expression = "55 + Math.sin(time * 5 + " + b + ") * 28;";
    }
    addText("Title", "Four cities in one sprint", [140, 130], 56, [0.94, 0.98, 0.92], 0.3);
    var routeGlow = addRect("Route Glow Sweep", [420, 620], [140, 520], [1, 0.8, 0.12]);
    routeGlow.property("Transform").property("Rotation").setValue(-12);
    routeGlow.property("Transform").property("Opacity").setValue(34);
    routeGlow.property("Transform").property("Position").setValueAtTime(1.0, [420, 620]);
    routeGlow.property("Transform").property("Position").setValueAtTime(4.8, [1510, 430]);
    app.endUndoGroup();
})();
