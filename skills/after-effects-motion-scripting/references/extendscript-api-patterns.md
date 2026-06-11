# ExtendScript API Patterns

## Safe Language Subset

After Effects JSX is ExtendScript, not modern browser JavaScript.

- Use `var`, functions, arrays, and plain objects.
- Avoid `let`, `const`, classes, arrow functions, template strings, destructuring, `forEach`, and `map`.
- Avoid reserved words as identifiers.
- Wrap fragile API calls in targeted `try/catch`, but do not hide whole-script failures unless writing a harness.

## Project Skeleton

```jsx
app.beginUndoGroup("AEFT Sample Name");
(function () {
    if (!app.project) app.newProject();
    var comp = app.project.items.addComp("AEFT Sample Name", 1920, 1080, 1, 12, 30);
    comp.bgColor = [0.02, 0.03, 0.04];
    // create layers
})();
app.endUndoGroup();
```

## Easing Helper

Use a dimension-aware helper and tolerate AE rejecting temporal easing on some properties.

```jsx
function ease(prop, influence) {
    if (!prop || prop.numKeys < 2) return;
    var dims = 1;
    try {
        if (prop.propertyValueType === PropertyValueType.TwoD || prop.propertyValueType === PropertyValueType.TwoD_SPATIAL) dims = 2;
        if (prop.propertyValueType === PropertyValueType.ThreeD || prop.propertyValueType === PropertyValueType.ThreeD_SPATIAL) dims = 3;
    } catch (e) {}
    for (var k = 1; k <= prop.numKeys; k++) {
        var ei = [], eo = [];
        for (var d = 0; d < dims; d++) {
            ei.push(new KeyframeEase(0, influence));
            eo.push(new KeyframeEase(0, influence));
        }
        try { prop.setTemporalEaseAtKey(k, ei, eo); } catch (ignore) {}
    }
}
```

## Shape Operator Order

AE can invalidate object handles after adding operators to a shape group. Prefer:

1. Create group.
2. Add shape/path.
3. Add Trim Paths or Repeater and animate those properties.
4. Add Stroke/Fill.

If AE reports “object is invalid,” reacquire the property or move the operator creation earlier.

## Local Asset Resolver

Use local fixtures and support both direct script runs and repo harnesses.

```jsx
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
```

## JSON Fallback

Some AE runtimes lack global `JSON`.

```jsx
function parseJsonText(txt) {
    if (typeof JSON !== "undefined" && JSON.parse) return JSON.parse(txt);
    return (new Function("return " + txt))();
}
```

Only use the fallback for trusted local fixtures committed with the sample.

## Import Patterns

- Single file: `app.project.importFile(new ImportOptions(asset("image.png")))`.
- Image sequence: create `ImportOptions` from the first numbered frame and set `opts.sequence = true`.
- Audio: import WAV/AIFF, add as layer, then drive markers/visuals from separate local beat JSON.
- Replacement: create a placeholder layer and call `replaceSource(footageItem, false)`.
