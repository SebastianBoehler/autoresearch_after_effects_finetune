(function () {
    app.beginUndoGroup("AEFT Event Promo Countdown");
    var comp = app.project.items.addComp("AEFT Event Promo Countdown", 1920, 1080, 1, 8, 30);
    comp.bgColor = [0.04, 0.02, 0.06];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0] - 180, pos[1]]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.5, pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.25, 100);
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

    for (var i = 0; i < 5; i++) {
        var stripe = addRect("Diagonal Energy " + i, [240 + i * 360, 540], [110, 1300], [0.22, 0.08, 0.42], i * 0.08);
        stripe.property("Transform").property("Rotation").setValue(22);
        stripe.property("Transform").property("Opacity").expression = "30 + Math.sin(time * 2 + " + i + ") * 16;";
    }
    var beam = addRect("Stage Light Sweep", [-200, 540], [160, 1080], [0.55, 0.22, 1], 0.25);
    beam.property("Transform").property("Opacity").setValue(42);
    beam.property("Transform").property("Rotation").setValue(-18);
    beam.property("Transform").property("Position").setValueAtTime(0.7, [-200, 540]);
    beam.property("Transform").property("Position").setValueAtTime(7.5, [2120, 540]);
    addText("Kicker", "LIVE ONLINE WORKSHOP", [180, 180], 34, [1, 0.82, 0.2], 0.25);
    addText("Title", "MOTION SYSTEMS", [170, 340], 96, [1, 0.96, 0.9], 0.45);
    addText("Subtitle", "Build verified After Effects scripts", [176, 420], 38, [0.78, 0.68, 0.95], 0.75);
    var dateBlock = addRect("Date Block", [1440, 300], [360, 220], [1, 0.82, 0.2], 1.0);
    dateBlock.property("Transform").property("Scale").setValueAtTime(1.0, [70, 70]);
    dateBlock.property("Transform").property("Scale").setValueAtTime(1.7, [100, 100]);
    addText("Date Day", "24", [1340, 315], 112, [0.08, 0.04, 0.08], 1.1);
    addText("Date Month", "JUN", [1500, 310], 52, [0.08, 0.04, 0.08], 1.25);
    var names = ["Prompt", "Script", "Render"];
    for (var j = 0; j < 3; j++) {
        var speakerCard = addRect("Speaker Card " + j, [380 + j * 420, 760], [330, 130], [0.12, 0.08, 0.2], 1.7 + j * 0.25);
        speakerCard.property("Transform").property("Position").setValueAtTime(4.2 + j * 0.15, [380 + j * 420, 760]);
        speakerCard.property("Transform").property("Position").setValueAtTime(7.55, [430 + j * 390, 718 + (j % 2) * 38]);
        addText("Speaker " + j, names[j], [280 + j * 420, 777], 38, [0.95, 0.9, 1], 1.85 + j * 0.25);
    }
    var progress = addRect("Countdown Progress", [960, 940], [1480, 12], [1, 0.82, 0.2], 1.1);
    progress.property("Transform").property("Scale").setValueAtTime(1.2, [0, 100]);
    progress.property("Transform").property("Scale").setValueAtTime(7.4, [100, 100]);
    for (var p = 0; p < 8; p++) {
        var dot = addRect("Beat Marker " + p, [360 + p * 170, 965], [42, 42], [0.94, 0.18, 0.42], 1.4 + p * 0.12);
        dot.property("Transform").property("Scale").expression = "b = 84 + Math.sin(time * 5 + " + p + ") * 16; [b, b];";
    }
    for (var k = 0; k < 12; k++) {
        var meter = addRect("Audio Meter " + k, [310 + k * 105, 610], [32, 120 + (k % 4) * 32], [0.95, 0.22 + (k % 3) * 0.16, 0.52], 0.9 + k * 0.04);
        meter.property("Transform").property("Scale").expression = "h = 58 + Math.sin(time * " + (3.2 + k * 0.17) + " + " + k + ") * 42; [100, h];";
        meter.property("Transform").property("Opacity").expression = "52 + Math.sin(time * " + (2.2 + k * 0.11) + ") * 26;";
    }
    for (var n = 0; n < 6; n++) {
        var flare = addRect("Orbiting Stage Flare " + n, [1360 + n * 70, 520 + (n % 2) * 72], [86, 12], [1, 0.82, 0.2], 1.2 + n * 0.08);
        flare.property("Transform").property("Position").expression = "value + [Math.sin(time * " + (1.4 + n * 0.12) + " + " + n + ") * 58, Math.cos(time * " + (1.7 + n * 0.1) + ") * 36];";
        flare.property("Transform").property("Rotation").expression = "time * " + (28 + n * 5) + ";";
    }
    for (var r = 0; r < 10; r++) {
        var ring = addRect("Countdown Orbit Tick " + r, [1338 + Math.cos(r) * 180, 760 + Math.sin(r) * 100], [70, 10], [1, 0.82, 0.2], 2.4 + r * 0.04);
        ring.property("Transform").property("Opacity").expression = "38 + Math.abs(Math.sin(time * " + (2.3 + r * 0.08) + " + " + r + ")) * 50;";
        ring.property("Transform").property("Rotation").expression = "time * " + (38 + r * 3) + ";";
    }
    for (var s = 0; s < 7; s++) {
        var sweep = addRect("Late RSVP Sweep " + s, [260 + s * 220, 220 + (s % 2) * 80], [120, 14], [0.94, 0.18, 0.42], 3.8 + s * 0.08);
        sweep.property("Transform").property("Position").setValueAtTime(3.8 + s * 0.08, [260 + s * 220, 220 + (s % 2) * 80]);
        sweep.property("Transform").property("Position").setValueAtTime(7.6, [360 + s * 190, 270 + (s % 3) * 66]);
    }
    for (var q = 0; q < 9; q++) {
        var pulse = addRect("Outro Seat Pulse " + q, [430 + (q % 3) * 210, 510 + Math.floor(q / 3) * 70], [140, 12], [0.55, 0.22, 1], 4.7 + q * 0.05);
        pulse.property("Transform").property("Scale").expression = "w = 42 + Math.abs(Math.sin(time * " + (3.0 + q * 0.13) + " + " + q + ")) * 78; [w, 100];";
        pulse.property("Transform").property("Opacity").expression = "32 + Math.abs(Math.sin(time * " + (2.4 + q * 0.09) + ")) * 54;";
    }
    for (var z = 0; z < 4; z++) {
        var finalFlash = addRect("Final Countdown Flash " + z, [1310 + z * 82, 850], [52, 52], [1, 0.82, 0.2], 5.2 + z * 0.12);
        finalFlash.property("Transform").property("Position").setValueAtTime(5.2 + z * 0.12, [1310 + z * 82, 850]);
        finalFlash.property("Transform").property("Position").setValueAtTime(7.75, [1270 + z * 104, 650 + (z % 2) * 60]);
        finalFlash.property("Transform").property("Scale").expression = "s = 72 + Math.abs(Math.sin(time * " + (3.6 + z * 0.22) + ")) * 54; [s, s];";
    }
    addText("Countdown", "03 DAYS", [1370, 760], 58, [1, 0.82, 0.2], 2.6);
    app.endUndoGroup();
})();
