(function () {
    app.beginUndoGroup("AEFT Vertical App Promo Reel");
    var comp = app.project.items.addComp("AEFT Vertical App Promo Reel", 1080, 1920, 1, 7, 30);
    comp.bgColor = [0.97, 0.96, 0.92];

    function addRect(name, pos, size, color, delay) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var rect = group.property("Contents").addProperty("ADBE Vector Shape - Rect");
        rect.property("ADBE Vector Rect Size").setValue(size);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValueAtTime(delay, [pos[0], pos[1] + 160]);
        layer.property("Transform").property("Position").setValueAtTime(delay + 0.55, pos);
        return layer;
    }

    function addText(name, value, pos, size, color, delay) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValueAtTime(delay, 0);
        layer.property("Transform").property("Opacity").setValueAtTime(delay + 0.35, 100);
        return layer;
    }

    addText("Hook", "Study faster", [540, 250], 86, [0.08, 0.12, 0.16], 0.2);
    var orbitColors = [[0.1, 0.5, 0.95], [0.16, 0.72, 0.48], [0.95, 0.42, 0.22], [1, 0.86, 0.18]];
    for (var o = 0; o < 8; o++) {
        var orbit = addRect("Background Orbit " + o, [160 + (o % 4) * 250, 430 + Math.floor(o / 4) * 980], [92, 18], orbitColors[o % 4], 0.1 + o * 0.04);
        orbit.property("Transform").property("Rotation").setValue(o % 2 === 0 ? -16 : 14);
        orbit.property("Transform").property("Position").expression =
            "value + [Math.sin(time * " + (1.2 + o * 0.08) + ") * 22, Math.cos(time * " + (1.0 + o * 0.06) + ") * 18];";
    }
    var phone = addRect("Phone Body", [540, 980], [560, 940], [0.06, 0.07, 0.09], 0.35);
    phone.effect.addProperty("ADBE Drop Shadow");
    addRect("Phone Screen", [540, 980], [500, 850], [0.95, 0.98, 1], 0.55);
    var cards = ["Plan", "Quiz", "Review"];
    var colors = [[0.1, 0.5, 0.95], [0.16, 0.72, 0.48], [0.95, 0.42, 0.22]];
    for (var i = 0; i < 3; i++) {
        var y = 730 + i * 190;
        var card = addRect("App Card " + cards[i], [540, y], [420, 120], [1, 1, 1], 0.8 + i * 0.25);
        card.effect.addProperty("ADBE Drop Shadow");
        addRect("App Accent " + cards[i], [370, y], [20, 82], colors[i], 0.95 + i * 0.25);
        var fill = addRect("Progress Fill " + cards[i], [570, y + 42], [250, 12], colors[i], 1.05 + i * 0.22);
        fill.property("Transform").property("Scale").setValueAtTime(1.1 + i * 0.25, [0, 100]);
        fill.property("Transform").property("Scale").setValueAtTime(4.8 + i * 0.18, [100, 100]);
        addText("App Label " + cards[i], cards[i], [540, y + 14], 42, [0.1, 0.13, 0.16], 1.0 + i * 0.25);
    }
    for (var n = 0; n < 4; n++) {
        var note = addRect("Floating Notification " + n, [300 + n * 150, 1260 + (n % 2) * 96], [220, 54], [0.95, 0.98, 1], 1.6 + n * 0.22);
        note.property("Transform").property("Position").setValueAtTime(2.0 + n * 0.12, [300 + n * 150, 1260 + (n % 2) * 96]);
        note.property("Transform").property("Position").setValueAtTime(6.2, [360 + n * 150, 1210 + (n % 2) * 96]);
        note.property("Transform").property("Position").setValueAtTime(6.9, [260 + n * 170, 1130 + (n % 2) * 70]);
    }
    var touch = addRect("Touch Cursor", [720, 725], [58, 58], [0.08, 0.62, 1], 1.2);
    touch.property("Transform").property("Position").setValueAtTime(1.2, [720, 725]);
    touch.property("Transform").property("Position").setValueAtTime(2.5, [715, 920]);
    touch.property("Transform").property("Position").setValueAtTime(3.8, [720, 1110]);
    touch.property("Transform").property("Position").setValueAtTime(6.4, [350, 1510]);
    touch.property("Transform").property("Position").setValueAtTime(6.9, [730, 1510]);
    touch.property("Transform").property("Opacity").expression = "55 + Math.sin(time * Math.PI * 4) * 25;";
    var scan = addRect("Phone Scanline", [540, 610], [460, 10], [0.1, 0.5, 0.95], 1.0);
    scan.property("Transform").property("Position").setValueAtTime(1.0, [540, 610]);
    scan.property("Transform").property("Position").setValueAtTime(5.6, [540, 1360]);
    scan.property("Transform").property("Position").setValueAtTime(6.6, [540, 720]);
    scan.property("Transform").property("Opacity").setValue(42);
    var badge = addRect("Sticker Badge", [790, 520], [260, 86], [1, 0.86, 0.18], 2.1);
    badge.property("Transform").property("Rotation").setValue(-8);
    badge.property("Transform").property("Scale").expression = "s = 100 + Math.sin(time * Math.PI * 3) * 5; [s, s];";
    addText("Sticker Text", "LIVE DEMO", [790, 535], 34, [0.08, 0.08, 0.08], 2.15);
    var sheet = addRect("Late Action Sheet", [540, 2025], [760, 260], [1, 1, 1], 5.15);
    sheet.property("Transform").property("Position").setValueAtTime(5.15, [540, 2025]);
    sheet.property("Transform").property("Position").setValueAtTime(6.5, [540, 1595]);
    var cta = addText("CTA", "Swipe into your next session", [540, 1630], 48, [0.08, 0.12, 0.16], 3.4);
    cta.property("Transform").property("Position").setValueAtTime(5.4, [540, 1630]);
    cta.property("Transform").property("Position").setValueAtTime(6.8, [540, 1545]);
    var underline = addRect("CTA Progress Underline", [540, 1705], [460, 12], [0.08, 0.62, 1], 5.6);
    underline.property("Transform").property("Scale").setValueAtTime(5.6, [0, 100]);
    underline.property("Transform").property("Scale").setValueAtTime(6.9, [100, 100]);
    underline.property("Transform").property("Opacity").expression = "58 + Math.sin(time * 4.2) * 24;";
    for (var r = 0; r < 7; r++) {
        var ripple = addRect("Final Swipe Ripple " + r, [245 + r * 96, 1768], [56, 8], orbitColors[r % 4], 5.45 + r * 0.06);
        ripple.property("Transform").property("Position").setValueAtTime(5.45 + r * 0.06, [245 + r * 96, 1768]);
        ripple.property("Transform").property("Position").setValueAtTime(6.95, [305 + r * 84, 1690 + (r % 2) * 34]);
        ripple.property("Transform").property("Opacity").expression = "42 + Math.abs(Math.sin(time * " + (2.5 + r * 0.12) + " + " + r + ")) * 44;";
    }
    for (var g = 0; g < 6; g++) {
        var graph = addRect("Late Session Graph " + g, [320 + g * 88, 1390], [54, 160 - (g % 3) * 28], orbitColors[g % 4], 4.6 + g * 0.07);
        graph.property("Transform").property("Scale").expression = "h = 45 + Math.abs(Math.sin(time * " + (2.8 + g * 0.18) + " + " + g + ")) * 68; [100, h];";
        graph.property("Transform").property("Opacity").expression = "48 + Math.abs(Math.sin(time * " + (2.1 + g * 0.11) + ")) * 38;";
    }
    for (var m = 0; m < 4; m++) {
        var status = addRect("Late Status Dot " + m, [365 + m * 104, 1512], [34, 34], orbitColors[(m + 1) % 4], 5.25 + m * 0.08);
        status.property("Transform").property("Scale").expression = "s = 72 + Math.abs(Math.sin(time * " + (3.4 + m * 0.2) + ")) * 42; [s, s];";
    }
    var endSweep = addRect("End Card Energy Sweep", [120, 1600], [80, 520], [0.08, 0.62, 1], 5.9);
    endSweep.property("Transform").property("Rotation").setValue(14);
    endSweep.property("Transform").property("Position").setValueAtTime(5.9, [120, 1600]);
    endSweep.property("Transform").property("Position").setValueAtTime(6.95, [960, 1510]);
    endSweep.property("Transform").property("Opacity").setValue(34);
    app.endUndoGroup();
})();
