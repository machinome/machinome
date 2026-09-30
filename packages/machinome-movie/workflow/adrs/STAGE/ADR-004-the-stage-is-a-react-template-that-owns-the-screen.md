# ADR-004: The stage is a React template that owns the screen

Status: Proposed (OpenSpec change `react-stage`, 30 September 2026)

## Context

Every film was drawn on one page, `src/film.html` with `src/film.js`: a
brand, a series label and a progress rule nobody asked for, three layouts
with fixed insets, a fixed inventory of overlays, and a new format field for
every new look. After inspecting the first film declared in Python, the pilot
ruled on 30 September 2026: "the template needs to own the screen ... no
hardcoded stuff in the screen. I want source code shown, that nice way of
highlighting the concepts, side by side, two different containers." The
movie document `machinome-movie/0.2` (ADR-005, `docs/movie-document.md`)
carries sets with slots, elements and cues, and names the project's stage
modules; the validation film *Cut and Advance* (version 2) writes its own
root set, a derived split and an element in its `stage.tsx`. The pilot's
`remove-progress-rule` proposal removed the rule the same morning.

## Decision

1. **A set is a React component that draws the whole screen**: its layout
   with `Slot`s where elements go, and its chrome inside `Chrome`, which the
   stage lifts above transitions, hides in picture-only captures and reports
   for the proofs' mask. The page itself is three empty layers and carries no
   colour, word or layout.
2. **An element is a React component that draws a state** the Node timeline
   resolved for the instant (a view, a source panel, a title, a picture, or a
   project's kind), and reports what it measured. Components are pure in
   video time: no clock, no state between frames, synchronous commits.
3. **The viewer stays outside React**: one instance per view element, kept
   across the shots of its chapter, hosted in the view's box and re-posed
   from the whole state on every frame.
4. **One bundle per movie**: the tool's runtime and the document's stage
   modules bundled by esbuild, typed from the document's stage block and
   checked by `tsc` before speech, rebuilt when the content of its inputs
   changes, hashed into the shot cache and the manifest.
5. **Kinds are registered and checked at mount**: a set or element kind the
   bundle lacks, a set whose slots differ from the document's, a kind
   registered twice and a viewer below the movie's API are refused by name.
6. YAML episodes are drawn by three shipped sets that reproduce the old
   page's layouts and masthead, from props; no set's source carries a brand.

## Options considered

- **Keep the page and add layouts to it.** Every new look stays a format
  change, the finding the direction started from.
- **Render frames in Node (server-side React to images).** Loses the real
  viewer, which draws the model in the browser, and every pixel proof.
- **Let components keep state and animate themselves.** Breaks "a frame is a
  pure function of video time", on which replay, caching and the proofs rest.
- **Mount the viewer inside React.** Reconciliation would remount WebGL
  contexts on layout changes; a host outside React keeps one instance per
  view.

## Consequences

- A project owns its film's look in code it writes; the tool owns only the
  shipped sets and elements.
- Every film's pixels change once; there was no release to preserve.
- Chrome is whatever a set marks, so the proofs' mask follows the template.
- A mismatch between the Python declarations and the components fails
  `check` before speech is bought.
