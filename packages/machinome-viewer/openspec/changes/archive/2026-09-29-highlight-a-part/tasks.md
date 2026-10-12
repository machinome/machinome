## 1. Red first

- [x] 1.1 Apply on the line that carries `track-a-part-on-screen` (API 28 and
      `nearestVisibleMesh`). Link the primary checkout's widget
      `node_modules`; never install. Record the base counts.
- [x] 1.2 Add `machinome_viewer/widget/src/presentation.test.ts` (red: the
      module does not exist), on plain three.js materials:
      - "tints the highlighted meshes' emissive and restores it exactly";
      - "dims the others' colour and leaves the highlighted ones";
      - "ghosts the others, including a normal material, and restores
        transparent, opacity and depthWrite exactly" (one material already
        transparent at opacity 0.5 before the highlight);
      - "leaves a normal material untinted and undimmed without throwing";
      - "hover, highlight, unhover, restore leaves the base exactly" and the
        three other interleavings of the same four events;
      - "forget writes every base back and a re-applied highlight reaches
        new meshes";
      - "reports ghosted meshes and only those".
      And for the pure request validator `highlightRequest`: "refuses no
      path", "refuses a colour that is not #rgb or #rrggbb", "refuses an
      unknown treatment of the others", "defaults to #ffb000 and keep".
- [x] 1.3 Add to `tests/test_widget_e2e.py` (spinner, on-demand mount) and
      run red against the API-28 bundle without this change:
      - `test_a_highlighted_part_is_visibly_lifted`: screenshot, highlight
        `['Hub']` in `#00ff00`, screenshot: hub pixels move toward green by
        a recorded margin, blade pixels unchanged; restore and screenshot:
        byte-identical to the first.
      - `test_ghosted_others_are_translucent`: from a view where a blade
        covers the centre of the hub's rectangle, ghost the others: blade
        pixels move toward the background, and the pixel at that centre
        now shows the hub's hue; `partOnScreen(['Hub']).point` is that
        centre when ghosted and another point, or `null`, when not.
      - `test_dimmed_others_are_darker`: blade luminance falls, hub's does
        not.
      - `test_highlight_refusals_and_hidden_parts`: a second highlight
        throws and the frame is unchanged; an unknown path, a bad colour and
        a bad mode throw before anything changes; a hidden highlighted
        blade is not drawn and appears highlighted when shown.
      - `test_highlight_survives_an_in_place_update`: rewrite the manifest,
        `manifestChanged()`, and the hub is still tinted; restore clears it.

## 2. Implement

- [x] 2.1 Create `presentation.ts`: `MaterialPresentation` (design D3) and
      `highlightRequest` (D6), with `DIM_FACTOR`, `GHOST_OPACITY` and the
      default colour as named constants.
- [x] 2.2 In `viewer.ts`, route `liftParts` through the owner; confirm the
      hover tests in `partSurface.test.ts` stay green unchanged.
- [x] 2.3 Add `highlight` to `ViewerHandle` and the handle (D1, D4, D6);
      render after applying and after restoring.
- [x] 2.4 At `replaceTree`, `manifestChanged` and `artifactChanged`, call
      `forget()` before replacement and re-apply the standing highlight
      after (D7); drop the owner in `dispose()`.
- [x] 2.5 Make `partOnScreen`'s reach predicate skip ghosted meshes (D5);
      leave `pickAt` unfiltered. Rebuild the bundle with `npm run build`
      only.

## 3. Document

- [x] 3.1 `docs/reference/viewer-handle.rst`: `highlight` under the camera
      and presentation members, with the options, the default colour, the
      one-at-a-time rule, the restore function, "hidden stays hidden",
      survival across updates, the colourless-part limitation, the ghost
      point rule, and "Available since API 28". Strict Sphinx build.

## 4. Validate and close

- [x] 4.1 Widget suite, typecheck, Python suite (one at a time), the five
      browser tests; inspect the highlighted, dimmed and ghosted frames by
      eye and record the constants finally used, counts and images'
      locations in `evidence.md`.
- [x] 4.2 Mark ADR-076 Accepted in the record and the ADR index if the
      pilot ratifies it; sync the delta spec, strict-validate, archive, and commit
      in this repository only. Integration, push and publication stay with
      the pilot.
