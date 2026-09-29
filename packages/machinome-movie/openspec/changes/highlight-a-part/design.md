## Context

`film.js` keeps one piece of cross-frame state today: the hidden paths. On each
frame it compares the requested list with the applied one and, only if they
differ, shows the old paths and hides the new ones, then `setTime` and `setView`
(which renders). Because the comparison is against the request, the result does
not depend on the order frames are posed in, which is what the preview's exact
pixel replay proves.

Viewer API 28 contract used here: `viewer.highlight(paths, {color?, others?:
'keep'|'dim'|'ghost'})` returns `restore()`; it lifts the named parts with a
tint, dims or ghosts (translucent, still drawn) the rest, renders synchronously,
and `restore()` puts every material back.

## Goals / Non-Goals

Show a mechanism inside its context and draw the eye to the part the narration
names, as readable YAML, with frames that stay a function of video time. Not
goals: new visual styles, fades, overlapping cues, a second visibility model.

## Decisions

### D1. The field

```yaml
    highlight:
      - from: 0
        to: 5.366
        parts: [[Feed mechanism, Driving pawl], [Feed mechanism, Ratchet and slender winding axle]]
        others: ghost
      - {from: 5.366, to: 10, parts: [[Feed mechanism, Holding pawl]], others: dim, color: "#237c86"}
```

- `from`, `to`: shot-local, half-open, `0 <= from < to <= duration`. Cues in one
  shot must not overlap; gaps show the model plainly.
- `parts`: a non-empty list; a string entry is a production layer name, a list
  entry is one root-relative assembly path. `parts: [saw, feed]` is two layers;
  `parts: [[Saw mechanism, Connecting rod]]` is one path. Writing a bare path
  without the outer list reads as layer names and is refused as unknown layers,
  never misread silently.
- `others`: `keep`, `dim` or `ghost`; default `keep`. Videomaker always passes
  its value explicitly, so the viewer's own default never decides a film.
- `color`: optional quoted `#rrggbb`; default `style.accent`, also passed
  explicitly.

### D2. Application is a function of the requested state

`frameAt` emits `highlight`: the active cue as data (resolved paths, `others`,
`color`) or `null`. The page keeps the applied cue's canonical JSON and its
`restore`. On each frame, after visibility and before `setTime`/`setView`: if the
requested cue differs from the applied one, call the stored `restore()` (if any),
then, if a cue is requested, call `viewer.highlight(...)` and store the new
`restore`. A cut or a cue's `to` therefore restores; two adjacent cues swap
through a restore; seeking in any order reaches the same materials. The final
`setView` renders the frame as today; highlight's own synchronous render is not
captured.

Rejected: re-applying the highlight on every frame (a restore and a render per
frame for no evidence of need) and accumulating cues across shots (the
production contract already says a shot's visual state is complete in itself).

### D3. Interplay with `hiddenLayers`

Hidden parts stay hidden. `others: ghost` does not bring them back as ghosts:
an author who wants the frame seen through moves those layers out of
`hiddenLayers` and ghosts them. `check` refuses a highlighted path equal to or
inside a path the same shot hides ("Highlighted part is hidden in shot pawls").
A highlighted ancestor of a hidden path is allowed; the hidden descendant stays
hidden. The page applies visibility before the highlight, so a change of hidden
set within a shot (impossible today; hiddenLayers is per shot) needs no rule.

### D4. Refusals

At `check`: empty `parts`; unknown layer; a path absent from the export; `others`
outside the three words; a colour that is not `#rrggbb`; times outside the shot
or not increasing; overlapping cues in one shot; a highlighted part hidden by the
same shot; `highlight` in a 0.2 episode. At `preview`/`render`: a viewer below API
28 (shared gate, D5); a viewer that throws for a path is surfaced with the shot id.

### D5. Format 0.3 and the viewer requirement (shared)

As `annotate-a-part` design D5, applied by whichever of the three sibling changes
lands first: format 0.3 accepted beside 0.2 with 0.2 semantics unchanged; new
fields only in 0.3 (today's validator would silently ignore an unknown
`highlight` key, so an older tool must refuse by format instead);
`requiredViewerApi(e)` returns 28 with reason `highlight (shot <id>)`; the page
refuses on mount below it, and `check` reads the bundle's `viewer API <n>` banner.

### D6. Preview checks

For each highlight cue, preview:

1. poses the cue's midpoint and captures it;
2. poses the same instant with the cue removed from the frame object (a
   preview-only comparison frame) and captures it; the two captures must differ,
   proving the highlight reached the pixels;
3. poses an instant with no cue, then the cue's midpoint again, then the
   unhighlighted instant again; both pairs must match exactly, proving the
   highlight re-applies identically and `restore()` is complete.

Whether a ghosted housing reads as translucent, rather than merely changed, is a
judgement on the stills: the viewer's own tests own material translucency, and
the pilot reviews the look.

## Risks / Trade-offs

- If a viewer operation replaced a part's material between frames (for example a
  flexible part re-evaluated by `setTime`), the tint could be lost on that mesh.
  The contract states the highlight persists until `restore()`; check 3 above
  catches a violation on the tested shot, and the fix belongs in the viewer.
- Ghosting everything but the lifted parts can clutter a wide view; the author
  chooses `dim` or a closer camera. Visual review is required.
- Colour is the only emphasis; a tint close to the model's own colours reads
  weakly. The accent default is chosen to contrast with the timber palette;
  the pilot judges it.

## Migration Plan

Additive and opt-in by format 0.3. No existing episode changes. Reverting the
tool commit makes 0.3 episodes refused by format, never rendered unhighlighted.

## Open Questions

- Default `others`: `keep` is proposed as the least surprising; the pilot's wish
  pairs highlighting with dimming or ghosting, so each Leonardo cue will state it.
