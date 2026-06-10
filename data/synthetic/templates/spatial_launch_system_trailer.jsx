(function () {
    if (!app.project) {
        app.newProject();
    }
    app.beginUndoGroup("AEFT Spatial Launch System");
    var W = 1920;
    var H = 1080;
    var DUR = 13;
    var comp = app.project.items.addComp("AEFT Spatial Launch System", W, H, 1, DUR, 30);
    comp.bgColor = [0.028, 0.034, 0.046];
    try {
        comp.motionBlur = true;
        comp.shutterAngle = 220;
        comp.shutterPhase = -110;
        comp.motionBlurSamplesPerFrame = 16;
    } catch (err) {}
    var voidColor = [0.028, 0.034, 0.046];
    var plateColor = [0.060, 0.074, 0.095];
    var planeColor = [0.088, 0.108, 0.132];
    var cyan = [0.0, 0.78, 0.96];
    var amber = [1.0, 0.58, 0.13];
    var white = [0.94, 0.96, 0.95];
    function keep(layer, start, end) {
        layer.inPoint = start;
        layer.outPoint = end;
        try {
            layer.motionBlur = true;
        } catch (err) {}
        return layer;
    }
    function T(layer, name) {
        var group = layer.property("ADBE Transform Group") || layer.property("Transform");
        if (!group) {
            return null;
        }
        var map = {
            "Anchor Point": "ADBE Anchor Point",
            "Position": "ADBE Position",
            "Scale": "ADBE Scale",
            "Opacity": "ADBE Opacity",
            "Rotation": "ADBE Rotate Z",
            "X Rotation": "ADBE Rotate X",
            "Y Rotation": "ADBE Rotate Y",
            "Z Rotation": "ADBE Rotate Z"
        };
        return group.property(map[name] || name) || group.property(name);
    }
    function ease(prop, influence) {
        if (!prop) {
            return;
        }
        for (var k = 1; k <= prop.numKeys; k++) {
            var value = prop.keyValue(k);
            var dims = value instanceof Array ? value.length : 1;
            var ins = [];
            var outs = [];
            for (var d = 0; d < dims; d++) {
                ins.push(new KeyframeEase(0, influence || 80));
                outs.push(new KeyframeEase(0, influence || 80));
            }
            try {
                prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
                prop.setTemporalEaseAtKey(k, ins, outs);
            } catch (err) {}
        }
    }
    function key(layer, propName, times, values, influence) {
        var prop = T(layer, propName);
        if (!prop) {
            return layer;
        }
        for (var i = 0; i < times.length; i++) {
            prop.setValueAtTime(times[i], values[i]);
        }
        ease(prop, influence || 80);
        return layer;
    }
    function fade(layer, t0, t1, t2, t3, peak) {
        return key(layer, "Opacity", [t0, t1, t2, t3], [0, peak, peak, 0], 76);
    }
    function fx(layer, matchName) {
        try {
            return layer.property("ADBE Effect Parade").addProperty(matchName);
        } catch (err) {
            return null;
        }
    }
    function make3(layer, pos, xr, yr, zr) {
        layer.threeDLayer = true;
        T(layer, "Position").setValue(pos);
        try {
            T(layer, "X Rotation").setValue(xr || 0);
            T(layer, "Y Rotation").setValue(yr || 0);
            T(layer, "Z Rotation").setValue(zr || 0);
            layer.property("Material Options").property("Accepts Lights").setValue(1);
        } catch (err) {}
        return layer;
    }
    function rect(name, size, color, start, end, opacity, strokeColor, strokeWidth) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        group.property("Contents").addProperty("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size").setValue(size);
        if (color) {
            group.property("Contents").addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(color);
        }
        if (strokeColor) {
            var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
            stroke.property("ADBE Vector Stroke Color").setValue(strokeColor);
            stroke.property("ADBE Vector Stroke Width").setValue(strokeWidth || 3);
        }
        T(layer, "Opacity").setValue(opacity === undefined ? 100 : opacity);
        return keep(layer, start, end);
    }
    function textLayer(name, value, pos, size, color, start, end, tracking) {
        var layer = comp.layers.addText(value);
        layer.name = name;
        var doc = layer.property("Source Text").value;
        doc.fontSize = size;
        doc.fillColor = color;
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        try {
            doc.font = size > 58 ? "Helvetica-Bold" : "ArialMT";
            doc.tracking = tracking === undefined ? 24 : tracking;
        } catch (err) {}
        layer.property("Source Text").setValue(doc);
        T(layer, "Position").setValue(pos);
        try {
            var anim = layer.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
            var amount = anim.property("ADBE Text Animator Properties").addProperty("ADBE Text Tracking Amount");
            amount.setValueAtTime(start, size > 70 ? 74 : 38);
            amount.setValueAtTime(start + 0.34, tracking === undefined ? 24 : tracking);
            ease(amount, 84);
        } catch (err) {}
        return keep(layer, start, end);
    }
    function pathLayer(name, points, color, width, pos, start, end, drawEnd) {
        var layer = comp.layers.addShape();
        layer.name = name;
        layer.threeDLayer = true;
        var group = layer.property("Contents").addProperty("ADBE Vector Group");
        var shape = new Shape();
        shape.vertices = points;
        shape.closed = false;
        shape.inTangents = [];
        shape.outTangents = [];
        for (var i = 0; i < points.length; i++) {
            shape.inTangents.push([0, 0]);
            shape.outTangents.push([0, 0]);
        }
        group.property("Contents").addProperty("ADBE Vector Shape - Group").property("ADBE Vector Shape").setValue(shape);
        var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        stroke.property("ADBE Vector Stroke Color").setValue(color);
        stroke.property("ADBE Vector Stroke Width").setValue(width);
        var trim = group.property("Contents").addProperty("ADBE Vector Filter - Trim");
        trim.property("ADBE Vector Trim End").setValueAtTime(start, 0);
        trim.property("ADBE Vector Trim End").setValueAtTime(drawEnd || start + 0.82, 100);
        trim.property("ADBE Vector Trim Offset").setValueAtTime(start, 0);
        trim.property("ADBE Vector Trim Offset").setValueAtTime(end, 55);
        ease(trim.property("ADBE Vector Trim End"), 84);
        ease(trim.property("ADBE Vector Trim Offset"), 70);
        T(layer, "Position").setValue(pos);
        return keep(layer, start, end);
    }
    function flash(name, time, color, amount) {
        var layer = rect(name, [1920, 1080], color, time - 0.02, time + 0.16, 0);
        T(layer, "Position").setValue([960, 540]);
        fade(layer, time - 0.02, time, time + 0.035, time + 0.16, amount);
    }
    comp.layers.addSolid(voidColor, "Spatial Deep Background", W, H, 1, DUR);
    var rig = comp.layers.addNull();
    rig.name = "Launch Architecture Rig";
    rig.threeDLayer = true;
    T(rig, "Position").setValue([960, 540, 0]);
    try {
        T(rig, "Y Rotation").expression = "Math.sin(time * 0.55) * 5;";
    } catch (err) {}
    keep(rig, 0, DUR);
    var floorSeed = rect("Architectural Floor Ruler", [70, 4], null, 0, 9.05, 32, cyan, 1.4);
    make3(floorSeed, [210, 830, 950], 72, 0, 0);
    try {
        var floorContents = floorSeed.property("Contents").property(1).property("Contents");
        var rep = floorContents.addProperty("ADBE Vector Filter - Repeater");
        rep.property("ADBE Vector Repeater Copies").setValue(22);
        rep.property("ADBE Vector Repeater Transform").property("ADBE Vector Repeater Position").setValue([86, 0]);
    } catch (err) {}
    floorSeed.parent = rig;
    var coreBack = rect("Launch Core Back Plane", [720, 420], plateColor, 0.8, 9.05, 78, cyan, 3);
    make3(coreBack, [960, 540, 260], 0, 0, 0);
    key(coreBack, "Scale", [0.8, 1.25, 8.55, 9.05], [[0, 100, 100], [100, 100, 100], [100, 100, 100], [82, 82, 82]], 86);
    fade(coreBack, 0.8, 1.05, 8.55, 9.05, 78);
    coreBack.parent = rig;
    var coreFace = rect("Launch Core Face", [420, 420], [0.050, 0.060, 0.076], 1.05, 9.05, 88, amber, 6);
    make3(coreFace, [960, 540, -80], 0, 0, 45);
    key(coreFace, "Z Rotation", [1.05, 2.2, 5.9, 7.7, 8.85], [45, 45, 45, 180, 220], 82);
    key(coreFace, "Scale", [1.05, 1.42, 7.2, 8.85], [[0, 0, 0], [100, 100, 100], [106, 106, 106], [78, 78, 78]], 86);
    try {
        T(coreFace, "Opacity").expression = "(time < 1.0 || time > 9.05) ? 0 : 82 + Math.sin(time * 20) * 10;";
    } catch (err) {}
    coreFace.parent = rig;
    var beam = rect("Launch Central Beam", [96, 650], [0.0, 0.40, 0.48], 1.2, 9.0, 22, cyan, 3);
    make3(beam, [960, 540, -150], 0, 0, 0);
    key(beam, "Scale", [1.2, 1.62, 8.55, 9.0], [[100, 0, 100], [100, 100, 100], [100, 106, 100], [100, 70, 100]], 84);
    try {
        T(beam, "Opacity").expression = "(time < 1.2 || time > 9.0) ? 0 : 20 + Math.sin(time * 16) * 6;";
    } catch (err) {}
    beam.parent = rig;
    var wingData = [
        ["Left Gantry Rail", [116, 670, 420], 0, -8, 0, [630, 540, 430]],
        ["Right Gantry Rail", [116, 670, 420], 0, 8, 0, [1290, 540, 430]],
        ["Upper Brace", [850, 86, 360], -8, 0, 0, [960, 275, 520]],
        ["Lower Runway Brace", [850, 86, 360], 10, 0, 0, [960, 805, 620]]
    ];
    for (var w = 0; w < wingData.length; w++) {
        var t = 1.42 + w * 0.14;
        var wing = rect("Architecture " + wingData[w][0], [wingData[w][1][0], wingData[w][1][1]], planeColor, t, 8.85, 58, cyan, 2);
        make3(wing, wingData[w][5], wingData[w][2], wingData[w][3], wingData[w][4]);
        key(wing, "Scale", [t, t + 0.38, 8.35, 8.85], [[0, 100, 100], [100, 100, 100], [100, 100, 100], [70, 70, 70]], 84);
        fade(wing, t, t + 0.16, 8.32, 8.85, 58);
        wing.parent = rig;
    }
    var routeA = pathLayer("Primary Launch Vector", [[-620, 120], [-250, -80], [90, 60], [380, -160], [660, -60]], cyan, 6, [960, 540, -220], 2.65, 6.35, 3.65);
    fx(routeA, "ADBE Glow");
    routeA.parent = rig;
    var routeB = pathLayer("Amber Transfer Vector", [[-520, -180], [-120, -260], [220, -90], [620, -230]], amber, 5, [960, 540, -120], 5.35, 8.65, 6.2);
    routeB.parent = rig;
    var sweep = rect("Controlled Light Sweep", [130, 2200], white, 2.0, 8.8, 13);
    make3(sweep, [-220, 540, -320], 0, 0, 18);
    try {
        sweep.blendingMode = BlendingMode.ADD;
    } catch (err) {}
    key(sweep, "Position", [2.0, 3.15, 6.5, 7.7], [[-220, 540, -320], [2180, 540, -320], [-220, 540, -320], [2180, 540, -320]], 66);
    try {
        var ambient = comp.layers.addLight("Spatial Ambient Fill", [960, 540]);
        ambient.lightType = LightType.AMBIENT;
        ambient.property("Light Options").property("Intensity").setValue(48);
        keep(ambient, 0, DUR);
        var point = comp.layers.addLight("Spatial Cyan Key", [960, 540]);
        point.lightType = LightType.POINT;
        point.threeDLayer = true;
        T(point, "Position").setValue([700, 300, -720]);
        point.property("Light Options").property("Intensity").setValueAtTime(0, 40);
        point.property("Light Options").property("Intensity").setValueAtTime(1.25, 142);
        point.property("Light Options").property("Color").setValue(cyan);
        keep(point, 0, DUR);
    } catch (err) {}
    var cam = comp.layers.addCamera("Spatial Camera", [960, 540]);
    key(cam, "Position", [0, 1.55, 1.62, 3.9, 3.98, 6.25, 6.32, 7.8, 8.9, 9.0, 12.8], [[960, 540, -2600], [960, 540, -2150], [610, 500, -1450], [780, 515, -1280], [1350, 420, -1560], [700, 680, -1500], [960, 540, -1760], [960, 540, -900], [960, 540, -950], [960, 540, -2120], [960, 540, -1900]], 78);
    try {
        cam.autoOrient = AutoOrientType.NO_AUTO_ORIENT;
        var camY = T(cam, "Y Rotation");
        camY.setValueAtTime(1.62, -6);
        camY.setValueAtTime(3.9, -2);
        camY.setValueAtTime(3.98, 6);
        camY.setValueAtTime(6.25, -5);
        camY.setValueAtTime(6.32, 0);
        camY.setValueAtTime(12.8, 0);
        ease(camY, 74);
    } catch (err) {}
    var readPlate = comp.layers.addSolid([0.026, 0.031, 0.042], "Final Readability Plate", W, H, 1, DUR);
    keep(readPlate, 8.82, DUR);
    key(readPlate, "Opacity", [8.82, 9.22, 12.7, DUR], [0, 92, 92, 0], 78);
    var t0 = textLayer("Opening Spatial Title", "SPATIAL LAUNCH", [960, 456], 112, white, 0.24, 2.1, 8);
    var s0 = textLayer("Opening Spatial Sub", "ARCHITECTURAL CAMERA SYSTEM", [960, 576], 32, cyan, 0.72, 2.0, 44);
    fade(t0, 0.24, 0.52, 1.62, 2.1, 100);
    fade(s0, 0.72, 0.92, 1.54, 2.0, 96);
    key(t0, "Scale", [0.24, 0.68, 1.4], [[78, 78], [106, 106], [100, 100]], 86);
    flash("Spatial First Snap", 1.58, white, 24);
    var t1 = textLayer("Architecture Title", "KINETIC ARCHITECTURE", [960, 232], 60, white, 2.12, 4.15, 18);
    var s1 = textLayer("Architecture Sub", "GANTRY RAILS / ONE CORE", [960, 846], 28, cyan, 2.54, 4.05, 38);
    fade(t1, 2.12, 2.38, 3.72, 4.15, 100);
    fade(s1, 2.54, 2.72, 3.62, 4.05, 92);
    flash("Spatial Second Snap", 3.92, cyan, 20);
    var t2 = textLayer("Vector Title", "VECTOR DEPLOYMENT", [960, 255], 66, white, 4.1, 6.55, 14);
    var s2 = textLayer("Vector Sub", "TRIM PATHS / CAMERA PUSH / LIGHT SWEEP", [960, 828], 27, amber, 4.6, 6.42, 34);
    fade(t2, 4.1, 4.36, 6.1, 6.55, 100);
    fade(s2, 4.6, 4.78, 6.02, 6.42, 92);
    flash("Spatial Core Snap", 6.38, amber, 24);
    var t3 = textLayer("Core Title", "SYSTEM ONLINE", [960, 500], 92, white, 6.66, 8.85, 8);
    var s3 = textLayer("Core Sub", "3D NULL RIG / POSITION CAMERA / POINT LIGHT", [960, 618], 28, cyan, 7.1, 8.72, 32);
    fade(t3, 6.66, 6.92, 8.34, 8.85, 100);
    fade(s3, 7.1, 7.28, 8.22, 8.72, 92);
    var finalTitle = textLayer("Final Spatial Title", "SPATIAL LAUNCH SYSTEM", [960, 500], 86, white, 9.08, DUR, 4);
    var finalSub = textLayer("Final Spatial Sub", "GENERATED MOTION GRAPHICS / CAMERA READY", [960, 612], 29, cyan, 9.58, 12.72, 34);
    var finalRule = rect("Final Amber Rule", [900, 8], amber, 9.82, 12.7, 100);
    T(finalRule, "Position").setValue([960, 678]);
    key(finalRule, "Scale", [9.82, 10.18, 12.42], [[0, 100], [100, 100], [108, 100]], 82);
    fade(finalTitle, 9.08, 9.42, 12.52, DUR, 100);
    fade(finalSub, 9.58, 9.82, 12.42, 12.72, 96);
    key(finalTitle, "Scale", [9.08, 9.62, 12.24], [[78, 78], [106, 106], [100, 100]], 86);
    comp.openInViewer();
    app.endUndoGroup();
})();
