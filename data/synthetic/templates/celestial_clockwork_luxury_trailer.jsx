(function () {
    app.beginUndoGroup("AEFT Chronos Luxury Clockwork");
    var comp = app.project.items.addComp("AEFT Chronos Luxury Clockwork", 1920, 1080, 1, 12, 30);
    comp.bgColor = [0.004, 0.006, 0.012];
    try {
        comp.motionBlur = true;
        comp.shutterAngle = 220;
        comp.shutterPhase = -110;
        comp.motionBlurSamplesPerFrame = 16;
    } catch (err) {}
    var voidBlue = [0.004, 0.006, 0.012];
    var midnight = [0.012, 0.015, 0.026];
    var gold = [0.86, 0.66, 0.18];
    var amber = [1.0, 0.48, 0.10];
    var ivory = [0.98, 0.94, 0.86];
    var dim = [0.30, 0.32, 0.38];
    function keep(layer, start, end) {
        layer.inPoint = start;
        layer.outPoint = end;
        try {
            layer.motionBlur = true;
        } catch (err) {}
        return layer;
    }
    function ease(prop, influence) {
        if (!prop) {
            return;
        }
        for (var k = 1; k <= prop.numKeys; k++) {
            var value = prop.keyValue(k);
            var dims = value instanceof Array ? value.length : 1;
            var a = [];
            var b = [];
            for (var d = 0; d < dims; d++) {
                a.push(new KeyframeEase(0, influence));
                b.push(new KeyframeEase(0, influence));
            }
            try {
                prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
                prop.setTemporalEaseAtKey(k, a, b);
            } catch (err) {}
        }
    }
    function key(layer, name, t0, a, t1, b, t2, c, influence) {
        var prop = layer.property("Transform").property(name);
        if (!prop) {
            return;
        }
        prop.setValueAtTime(t0, a);
        prop.setValueAtTime(t1, b);
        if (c !== undefined) {
            prop.setValueAtTime(t2, c);
        }
        ease(prop, influence || 84);
    }
    function fade(layer, t0, t1, t2, t3, peak) {
        key(layer, "Opacity", t0, 0, t1, peak, t2, peak, 84);
        layer.property("Transform").property("Opacity").setValueAtTime(t3, 0);
        ease(layer.property("Transform").property("Opacity"), 84);
        return layer;
    }
    function rect(name, pos, size, color, start, end, opacity) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        group.property("Contents").addProperty("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size").setValue(size);
        group.property("Contents").addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValue(opacity === undefined ? 100 : opacity);
        return keep(layer, start, end);
    }
    function disk(name, pos, size, color, start, end, opacity) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        group.property("Contents").addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue(size);
        group.property("Contents").addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(color);
        layer.property("Transform").property("Position").setValue(pos);
        layer.property("Transform").property("Opacity").setValue(opacity === undefined ? 100 : opacity);
        return keep(layer, start, end);
    }
    function ring(name, size, color, width, start, end, z, xRot, yRot, speed, dashed) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        group.property("Contents").addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue(size);
        var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        stroke.property("ADBE Vector Stroke Color").setValue(color);
        stroke.property("ADBE Vector Stroke Width").setValue(width);
        try {
            var trim = group.property("Contents").addProperty("ADBE Vector Filter - Trim").property("ADBE Vector Trim End");
            trim.setValueAtTime(start, 0);
            trim.setValueAtTime(start + 0.72, 100);
            ease(trim, 88);
            if (dashed) {
                var rep = group.property("Contents").addProperty("ADBE Vector Filter - Repeater");
                rep.property("ADBE Vector Repeater Copies").setValue(10);
                rep.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Rotation").setValue(36);
                rep.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([0, 0]);
            }
        } catch (err) {}
        layer.threeDLayer = true;
        layer.property("Transform").property("Position").setValue([960, 540, z]);
        try {
            layer.property("Transform").property("X Rotation").setValue(xRot);
            layer.property("Transform").property("Y Rotation").setValue(yRot);
            layer.property("Transform").property("Z Rotation").expression = "time * " + speed + ";";
            layer.property("Material Options").property("Accepts Lights").setValue(1);
        } catch (err) {}
        return keep(layer, start, end);
    }
    function txt(name, value, pos, size, color, start, end, serif) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        try {
            doc.font = serif ? "Times New Roman" : "Helvetica-Bold";
            doc.tracking = serif ? 140 : 96;
        } catch (err) {}
        layer.property("Source Text").setValue(doc);
        layer.property("Transform").property("Position").setValue(pos);
        try {
            var anim = layer.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
            var track = anim.property("ADBE Text Animator Properties").addProperty("ADBE Text Tracking Amount");
            track.setValueAtTime(start, serif ? -20 : -28);
            track.setValueAtTime(start + 0.42, serif ? 180 : 120);
            track.setValueAtTime(start + 0.76, serif ? 140 : 96);
            ease(track, 88);
        } catch (err) {}
        return keep(layer, start, end);
    }
    function glow(layer, radius, intensity) {
        try {
            var fx = layer.property("Effects").addProperty("ADBE Glow");
            fx.property("Glow Radius").setValue(radius || 42);
            fx.property("Glow Intensity").setValue(intensity || 0.7);
        } catch (err) {}
        return layer;
    }
    function aperture(name, start, color, reverse) {
        for (var i = 0; i < 6; i++) {
            var bar = rect(name + " Blade " + i, [960, 540], [1680, 105], color, start + i * 0.018, start + 0.72, 0);
            bar.property("Transform").property("Rotation").setValue(i * 30 + (reverse ? 12 : -12));
            fade(bar, start + i * 0.018, start + 0.06 + i * 0.018, start + 0.4, start + 0.72, 82);
            key(bar, "Scale", start + i * 0.018, [0, 100], start + 0.26 + i * 0.018, [112, 100], start + 0.55, [70, 100], 86);
        }
    }
    rect("Midnight Void", [960, 540], [1920, 1080], voidBlue, 0, 12, 100);
    glow(disk("Amber Halo", [960, 540], [520, 520], amber, 0, 12, 14), 120, 0.6);
    var core = glow(disk("Polished Core", [960, 540], [96, 96], gold, 0.05, 11.8, 72), 62, 0.9);
    key(core, "Scale", 0.05, [0, 0], 0.78, [122, 122], 1.12, [100, 100], 90);
    var rig = comp.layers.addNull();
    rig.name = "Chronos 3D Rig";
    rig.threeDLayer = true;
    rig.property("Transform").property("Position").setValue([960, 540, 0]);
    try {
        rig.property("Transform").property("Y Rotation").expression = "time * 7;";
    } catch (err) {}
    keep(rig, 0, 12);
    try {
        var ambient = comp.layers.addLight("Luxury Ambient", [960, 540]);
        ambient.lightType = LightType.AMBIENT;
        ambient.property("Light Options").property("Intensity").setValue(34);
        keep(ambient, 0, 12);
        var point = comp.layers.addLight("Gold Point", [960, 540]);
        point.lightType = LightType.POINT;
        point.threeDLayer = true;
        point.property("Transform").property("Position").setValue([960, 540, -240]);
        point.property("Light Options").property("Intensity").setValueAtTime(0, 0);
        point.property("Light Options").property("Intensity").setValueAtTime(1.05, 145);
        point.property("Light Options").property("Color").setValue(amber);
        keep(point, 0, 12);
    } catch (err) {}
    var cam = comp.layers.addCamera("Chronos Camera", [960, 540]);
    key(cam, "Position", 0, [960, 540, -1580], 1.8, [820, 470, -940], 2.1, [1040, 585, -1120], 78);
    key(cam, "Position", 2.1, [1040, 585, -1120], 4.1, [960, 540, -760], 4.32, [910, 500, -1050], 80);
    key(cam, "Position", 4.32, [910, 500, -1050], 7.2, [1040, 560, -880], 7.45, [960, 540, -1260], 80);
    key(cam, "Position", 7.45, [960, 540, -1260], 10.2, [960, 540, -980], 11.6, [960, 540, -1240], 78);
    keep(cam, 0, 12);
    var r0 = glow(ring("Hero Orbit", [770, 770], gold, 4, 0.15, 11.5, 0, 0, 0, 18, false), 24, 0.65);
    var r1 = ring("Oblique Orbit", [1100, 560], ivory, 3, 0.55, 11.4, 120, 64, 18, -13, false);
    var r2 = ring("Dashed Gear Orbit", [1240, 1240], dim, 2, 0.95, 11.1, 280, 78, -24, 10, true);
    var r3 = glow(ring("Inner Amber Gear", [430, 430], amber, 5, 1.45, 10.9, -80, 30, -54, -28, true), 20, 0.8);
    r0.parent = rig;
    r1.parent = rig;
    r2.parent = rig;
    r3.parent = rig;
    aperture("Opening Aperture", 1.72, gold, false);
    var overline = txt("Opening Overline", "PRECISION MECHANISM", [960, 305], 29, gold, 0.58, 2.65, false);
    var titleA = txt("Chronos Title", "CHRONOS", [960, 520], 132, ivory, 2.32, 5.28, true);
    fade(overline, 0.58, 0.92, 2.18, 2.65, 92);
    fade(titleA, 2.32, 2.72, 4.78, 5.28, 100);
    key(titleA, "Position", 2.32, [960, 595], 2.88, [960, 500], 4.28, [960, 520], 90);
    key(titleA, "Scale", 2.32, [72, 72], 2.96, [110, 110], 4.2, [100, 100], 90);
    aperture("Title Aperture", 4.82, ivory, true);
    for (var t = 0; t < 12; t++) {
        var tick = rect("Fast Clock Tick " + t, [960 + Math.cos(t * Math.PI / 6) * 280, 540 + Math.sin(t * Math.PI / 6) * 280], [76, 5], t % 2 ? ivory : gold, 5.08 + t * 0.035, 8.0, 88);
        tick.threeDLayer = true;
        tick.parent = rig;
        try {
            tick.property("Transform").property("Z Rotation").setValue(t * 30);
        } catch (err) {}
        key(tick, "Scale", 5.08 + t * 0.035, [0, 100], 5.44 + t * 0.035, [126, 100], 6.8, [92, 100], 86);
        fade(tick, 5.08 + t * 0.035, 5.18 + t * 0.035, 7.42, 8.0, 88);
    }
    var detail = txt("Detail Montage", "TWELVE JEWELS / ONE ENGINE", [960, 705], 28, gold, 5.55, 8.05, false);
    fade(detail, 5.55, 5.82, 7.5, 8.05, 94);
    aperture("Detail Cut", 7.62, amber, false);
    var plate = rect("Final Midnight Plate", [960, 540], [1250, 430], midnight, 7.9, 12, 88);
    key(plate, "Position", 7.9, [960, 1180], 8.42, [960, 520], 9.0, [960, 540], 90);
    var finalTitle = txt("Final Luxury Title", "CELESTIAL CLOCKWORK", [960, 465], 76, ivory, 8.32, 12, true);
    var finalSub = txt("Final Luxury Sub", "CAMERA / LIGHTS / 3D RINGS / TRIM PATHS", [960, 602], 29, gold, 8.86, 11.7, false);
    var finalSmall = txt("Final Small", "SCRIPTED INSIDE AFTER EFFECTS", [960, 710], 24, dim, 9.28, 11.55, false);
    fade(finalTitle, 8.32, 8.7, 11.42, 12, 100);
    fade(finalSub, 8.86, 9.1, 11.18, 11.7, 94);
    fade(finalSmall, 9.28, 9.45, 11.05, 11.55, 82);
    key(finalTitle, "Scale", 8.32, [74, 74], 8.95, [106, 106], 11.1, [100, 100], 88);
    comp.openInViewer();
    app.endUndoGroup();
})();
