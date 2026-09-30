## Context

The contract is `docs/movie-document.md` (`machinome-movie/0.2`, the resolved
document, the frame, the stage's contract with the renderer) with
`schema/machinome-movie-0.2.json`; the campaign plan is
`workflow/ongoing/react-stage-campaign/plan.md` ("What the stage is, in one
paragraph each"). The Python side (`declarative-stage`) evaluates movies to
0.2 and checks them with `check_document` (`python/machinome_movie/document.py`),
whose refusals the shared invalid fixtures pin for both runtimes. The pilot's
`remove-progress-rule` proposal (branch `remove-progress-rule`) removes the
progress rule; its D1 to D5 are carried here. The film this cycle exists for is
Leonardo's `videos/cut_and_advance/spec.md`, version 2.

Where this design reads the contract in a way the contract does not spell,
the reading is recorded under "Contract findings" in `evidence.md` with the
smallest correction; the schema is not forked.

## Goals / Non-Goals

Goals: every film, YAML or document, drawn by a React template that owns the
screen; nothing in the page the document did not ask for; every readback
check, pixel proof, cache and provenance guarantee kept; the film's source
(`movie.py`, `stage.tsx`) producible. Non-goals: the proposal's.

## Decisions

### D1. Loading and checking a document (`src/movie.mjs`, `src/schema.mjs`)

1. **Format first.** `format` other than `machinome-movie/0.2` is refused
   naming it and the format this build reads, before anything else.
2. **Schema.** The subset validator gains `oneOf` (exactly one branch; a
   failure names the field and the branches' titles), `propertyNames`,
   `enum`, `minimum`, `maxItems` and `exclusiveMinimum`; `anyOf` stays; the
   keyword-guard test keeps validator and schema in step.
3. **Static checks, a port of `check_document`.** The same rules, in the same
   order, naming the same subjects and vocabulary (`chapter <id>, shot <id>,
   <field>`; `elements.<key>`; `stage.sets.<kind>`), so every invalid
   fixture's `must_mention` words are named by both runtimes:
   `checkMovie(doc)` (no files) and `checkMovieFiles(doc, {manifest,
   sources})` (parts against the export's assembly, tokens against the
   excerpts' text read through `root`).
4. **The load** (`loadMovie`): read, `checkMovie`; the manifest and every
   excerpt's source text through `root`, `checkMovieFiles`; the stage
   modules exist inside the project repository; the takes of chapters with
   spoken anchors, refused as today when absent; `resolveMovie`; the
   resolved document written to `<root>/_build/movie-resolved.json`; then
   the project checks as before (repository, pinned revision, pinned source
   bytes, pictures, evidence files) and the checks that need them (D2.4).

### D2. Resolution (`resolveMovie(doc, takes)`, pure)

1. Chapters in order, shots in order, from 0; an anchor resolves to chapter
   start + `speechOffset` (default 0.2) + the take's time + `plus`, snapped
   to the output frame grid; literal numbers kept. Marks resolve to model
   seconds.
2. The resolved document is the unresolved one with `resolved: true`,
   `output.durationSeconds`, `speechOffset`, `start` and `end` on every
   chapter, `start` and `end` on every shot, the shot's `until` its numeric
   duration, every cue `at` and `until`, every action `until`, every model
   key `at` and picture view key `at` shot-local and numeric, and every
   model second numeric. Two readings add times the contract implies but
   does not spell (finding): an `emphasize` action gains `until` (its phrase's
   spoken end plus `hold`, unsnapped, as the old emphasis cleared) and each
   of its `words` an `at` (the onset of its spoken words, unsnapped); a
   title `show` with a spoken reveal gains `reveal.onsets` (each word's
   onset). Field order is kept; the output is deterministic.
3. Refused while resolving, naming the chapter, the shot and the field: a
   phrase absent from or repeated in the take; an `until` at or before its
   start; a cue or key outside its shot; a spanning action whose `until` is
   at or before its `at`; a `move` whose `until` is at or before its `at`;
   two moves, two highlights or two shows of one element in one shot
   overlapping in time; an entrance, exit or join shorter than two frames, an
   entrance or exit longer than its span, a join longer than its own shot; an
   outgoing model continued past the export; model keys not following one
   another or running model time back; a spoken reveal word spoken a frame or
   more before its cue or appearing on no frame; a take that does not fit its
   chapter (at `speech`). Three rules of the YAML formats are not applied to a
   document, because the Python side's fixtures break them and the contract
   does not state them (findings): an emphasis hold running past its shot's
   end ends with the shot; a join may be longer than the shot it leaves (the
   outgoing shot continues); an incoming join and a fade-out may overlap (the
   join is drawn until it ends). A YAML episode keeps all three refusals.
4. After the load, with the excerpts and media: a token not yet typed when
   its word is spoken; a clip that does not cover its span and continuation;
   the picture checks of `pictures.mjs` that do not need a slot's box.

### D3. YAML episodes (`src/episode.mjs`)

`validateEpisode` and every YAML rule stay as they are. A validated episode
converts (`episodeFilm`) to the resolved document: one chapter per shot (id,
narration, `speechOffset`), the shot's elements synthesized, placed in the
shipped sets:

| YAML | resolved |
|---|---|
| shot without code | set `paper`, the view in `stage` |
| shot with code | set `paper-split`, the source in `left`, the view in `right` |
| `layout: source-only` | set `source-only`, the source in `source`, no view |
| `camera` keys | the view's `camera` is the first key's preset; each later key a `move` from the previous key's `at` until its own, with its `ease` |
| `hiddenLayers` | the view's `hide` |
| `simulation` | the shot's `model` (`from`/`to`, or `keys`) |
| overlay at `top`, `lower-third`, `center`, `title` | a `title` element (`text`, `subtitle`) shown by one `show` action (`enter`, `leave`, `reveal`) in the slot the position names; the *n*th overlay of a position in a shot in slot `<position>-<n>` (n from 2) |
| `pictures` | a `picture` element per cue, `show` with `enter`, `leave`, `view`; `area: stage` in `plate` (`plate-<n>`), `area: frame` in `full` (`full-<n>`) |
| `annotations` | `ring`, `label`, `arrow` on the view; `place`, `offset` and `padding` converted from the safe area to the view's box |
| `highlight` | `highlight` on the view |
| `code.typing` | `type` actions (`at` = `from`, `over` = `to - from`) |
| `code.emphasis` | `emphasize` at `{spoken: phrase}` with `words` `{spoken: w, token: w}`, `line`, `hold` |
| `transition`, `fadeIn`, `fadeOut` | as written |
| `series`, the brand | the paper sets' props `series` and `brand` (`MACHINOME`) |

Word timing (spoken reveals, emphasis) is filled from the cached takes by the
commands that need it, as before (`prepareWordTimingForCommand`); `speech`
needs none. The masthead's literal words live in the loader, as data the
paper sets draw, never in the page or a set's source.

### D4. The frame (`src/timeline.mjs`)

`frameAt(film, t)` is pure over the resolved document and what the load
attached (the excerpts' pinned text, the pictures' probes). It returns
`{time, chapterId, shotId, set, slots, elements, transition}`; element keys
are `<chapter id>.<element key>`; only placed elements appear, each complete:

- `view`: `time` (model seconds over the export's duration), `view`
  (`camera`, `target`), `up`, `fov`, `hidden` (paths), `highlight`
  (`{paths, others, color}` or `null`), `marks`
  (`[{id: "cues[i].actions[j]", kind, target: {paths} | {point}, text?,
  place? | offset? | padding?, opacity, drawn}]`). The camera starts at the
  element's `camera`, or where its last move in an earlier shot of the
  chapter ended, and follows its moves (position, target and field of view
  eased by the move's curve, default `smooth`; up carried exactly, or mixed
  as unit directions when the two cameras' ups differ).
- `source`: `file`, `firstLine`, `lastLine`, `text` (typed), `html`
  (highlight.js markup of the typed text), `cursor`, `emphasis`
  (`[{token, start, end}]`, offsets in the excerpt's text). Typing continues
  where the chapter's previous typing stopped.
- `title`: `shown`, `text`, `subtitle`?, `opacity`, and with a reveal
  `words` (split words and spaces) and `revealed`.
- `picture`: `shown`, `media` (`still` or `clip`), `name`, `fit`, `opacity`,
  `view` (`{center, zoom}`), and for a clip `frame` and `clipSeconds`
  (finding: the contract's `kind` collides with the element's kind, and its
  `rect` needs the slot's box, which only the stage knows).
- a project kind: `props`, `actions` (`[{action, params, since, until,
  progress}]`).

A spanning action is active from its `at` (inclusive) to its `until`
(exclusive), compared within a nanosecond; past the shot's end, in a
transition's continuation, an action that ran to the end stays, a mark or a
picture with a `leave` has left, a view holds its camera and its model runs on
at its end rate, and a source panel holds its text. `transition` keeps its
earlier shape (`field`, `kind`, `shotId`, `duration`, `ease`, `progress` or
`plate`/`picture`, `direction`, `color`, `outgoingShotId`, `outgoing`). The
frame has no `progress` (remove-progress-rule D2).

### D5. The stage runtime (`stage/`)

- **Page.** `src/film.html` is three empty layers in order, `#stage-root`
  (React), `#transition`, `#chrome`, then `/viewer.js` and `/stage.js`, and
  links `/stage.css`. It carries no colour, word or layout.
- **Authoring API** (`videomaker/stage`, an esbuild alias of
  `stage/index.ts`): `defineSet({kind, slots, component})`,
  `defineElement({kind, component})`, `Slot({name, className?, style?})`,
  `Chrome({children})`, `useMovie()` (`{id, title, series, style}`),
  `useReport(report)`; types for set and element components, augmented per
  movie by the generated `movie.d.ts` (`videomaker/movie`).
- **Sets** receive `{movie, props}` and render their layout with `Slot`s;
  a `Slot` renders the placed element's component in a box
  (`.vm-slot[data-slot]` > `.vm-element[data-element]`), or an empty box.
  `Chrome` is a portal into `#chrome`, above `#transition`, hidden in
  picture-only captures; its children's rectangles are `observed.chrome`.
- **Commits are synchronous** (`flushSync` on a `react-dom/client` root);
  components are pure functions of their state. After the commit the runtime
  poses the views, draws marks, awaits picture decodes, repaints the whole
  page (the discipline of `film.js`, D11) and measures.
- **Views.** One viewer instance per view element key, created on its first
  frame by `MachinomeViewer.mount` in a host outside React, and appended
  into the view element's box after each commit; hosts of views not placed
  are detached and hidden. Each frame re-specifies an instance's whole
  state: visibility, highlight (restored when it differs), time, and view
  (with `up` and `fov` from API 28). Marks are drawn in an SVG layer and
  text boxes over the view's box, positioned by `viewer.partOnScreen` and
  `viewer.project`; `offset`, `place` and `padding` are fractions of the
  view's box.
- **`window.film`**: `{apiVersion, viewer (the first instance), project(key,
  points), setFrame(frame), compose(request), composeMarkBlend(pictures),
  views()}`. `setFrame` returns `observed = {frame: {width, height}, chrome:
  [rects], slots: {slot: rect}, elements: {key: report}}`; a view reports
  `box`, `instance`, `canvas`, `camera`, `target`, `up`, `fov`,
  `navigation`, `marks` (anchor, rect, ring, text, tail, inside, outside);
  a source `box`, `text`, `fits`, `emphasis` (`[{token, text}]`), `cursor`;
  a title `box`, `text` (its text box), `revealed`; a picture `box`,
  `drawn`, `natural`, `frame`; a project element `box` and what it reported.
- **Refusals at mount**, into `window.filmError`, by name: a set kind of the
  document the bundle does not register; one whose registered slots differ
  from the document's; an element kind a chapter uses that is not
  registered; a kind registered twice; a viewer whose API is below what the
  movie needs.

### D6. Shipped sets and elements

- `frame` (`stage`: the whole picture) and `split` (`left`, `right`: two
  halves inside the safe inset) draw no chrome.
- `paper`, `paper-split` and `source-only` reproduce the film page's
  geometry: the model stage at `[5%, 16%, 90%, 63%]` (split: `[56%, 20%,
  42%, 65%]`, the source at left), the overlay positions and their
  typography, the masthead of `props.brand` and `props.series` in `Chrome`,
  and no rule. Their slots: `paper`: `stage`, `plate`…, `full`…, `title`…,
  `top`…, `lower-third`…, `center`…; `paper-split`: `left`, `right`, and the
  same others; `source-only`: `source` and the text positions. "…" is the
  position and its `-2` to `-8`.
- `view`, `source`, `title`, `picture` draw what D4 says. The source, title
  and picture take their type, size and colours from CSS custom properties a
  set may set on its slots (`--vm-source-size`, `--vm-title-size`, …) with
  defaults relative to the frame. A picture's geometry is CSS arithmetic over
  its box (container units), not a measurement.

### D7. One bundle per movie (`src/stage-build.mjs`)

`buildStage(film)` writes under `<root>/_build/stage/`: `entry.tsx`
(imports the shipped runtime, then each module, then boots), `stage.js`
(esbuild, IIFE, `NODE_ENV=production`, no source maps, React resolved from
the tool's `node_modules`, `videomaker/stage` aliased), `stage.css`,
`movie.d.ts` (the stage block as types: a set's slots as a string union and
its props; an element's props and each action's params; exported and merged
into `videomaker/stage`'s registry types), `tsconfig.json`, and
`inputs.json`. When any module is TypeScript, `tsc --noEmit` checks the
modules with the generated types; a `.jsx` module gets only the runtime's
checks. The key is the SHA-256 of the runtime's sources, each module and every
file the previous build read, the stage block, and the versions of esbuild,
TypeScript and React; an equal key reuses the bundle, never an mtime. A YAML
episode bundles the runtime alone. `check` builds and reports it.

### D8. The renderer on the stage (`src/render.mjs`)

The page serves `/`, `/stage.js`, `/stage.css`, `/viewer.js`, the model, the
pictures and `/config.json` (`movie`, `stage`, media sizes, the required
viewer API). Every check of a posed frame reads `observed.elements`: camera,
target, up and fov per view; the canvas filling each view's box; the displayed
source text, its fit and its lit tokens; a title's revealed count and text
inside the frame; each mark's target on its view and its text inside the
frame, a ring wholly on its view and inside the frame; a picture's drawn
rectangle against the one its fit and view give for the reported box, its
natural size against the probe, its clip frame, and its enlargement against
the allowance. Every proof of `preview` is kept, iterating the resolved
actions: highlight change/restore/re-apply, samples, mark entrances and exits
(same-instant blends), reveals, title fades, emphasis, pictures (replay,
partial replay, fades), transitions, lens changes, pixel replay A-B-A, the
invalid camera request. Every pixel proof masks the chrome rectangles.
Review samples come from title and source states. The shot cache's frame
records drop `progress`; the stage bundle's hashes are common inputs through
the page's served files; the manifest records `stageSha256`. Duration stays
in the common key (remove-progress-rule D4); the cache schema is unchanged.

### D9. Tests

Layers 2 (fixtures), 3 (timeline, inline fixtures), 4 (`stage/**/*.test.tsx`,
jsdom; `tsc --noEmit` over `stage/` and a generated `movie.d.ts`), 5
(`test/browser/`, the viewer double), 8 (`test/pipeline/`), 9 (pins). The
slow list names `test/browser/**` and `test/pipeline/**`. Every slow test is a
`slowTest`; the verdict key reads `stage/` and the fixture project too.

### D10. Raster discipline (`film.js` comments)

Kept: a whole-page repaint after every pose (now always, not only after fresh
poses, pictures and source-only frames), the live views hidden while a
transition or a blend is composed from same-instant captures, faded marks and
pictures blended from captures of the plain mark (not CSS opacity), titles
faded by opacity. Dropped: the class toggles between three layouts (a set is
mounted instead), the conditional repaint (always repainting is simpler and
removes the only order dependence it guarded), and chrome's place in the
blend (blends are composed from picture-only captures and the chrome stays
live above them; every proof masks it).

### D11. Records

ADR-004 (`STAGE`): the stage is a React template that owns the screen.
ADR-006 (`SOURCE`), amending ADR-001: YAML episodes and movie documents load
into one resolved movie document. `docs/stage.md` is the authoring contract.

## Risks / Trade-offs

- Every film re-renders cold with new pixels; there is no release to keep.
- Several viewer instances in one page cost memory; one per view element,
  created lazily, is the contract's.
- Always repainting costs a few animation frames per pose.
- The YAML paper sets carry indexed slots (`top-2` …) so that several
  overlays of one position in one shot stay separate elements; more than
  eight is refused naming the shot.

## Open Questions

None blocking; the contract findings in `evidence.md` are for the
orchestrator.
