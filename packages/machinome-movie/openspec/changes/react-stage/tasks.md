## 0. Preconditions

- [x] 0.1 Base: branch `react-stage-runtime` from `react-stage` at `502ef71`.
  Run the base suite cold once before any change and record, in
  `evidence.md`, which tests fail and why (the removed 0.1 schema and
  fixtures).
- [ ] 0.2 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: the document checks and resolution (D1, D2), the YAML
  conversion and its indexed slots (D3), the frame (D4), the runtime and its
  refusals (D5), the shipped sets (D6), the bundle (D7), the renderer (D8),
  the raster discipline (D10).

## 1. Red, innermost first (record each in `evidence.md`)

- [ ] 1.1 Layer 2: both fixture documents load, check and resolve to their
  pins twice identically; every invalid fixture is refused naming its words;
  a 0.1 document is refused naming the format this build reads.
- [ ] 1.2 Layer 3: the timeline over inline resolved fixtures (views, moves
  and continuity, marks, highlight, source typing and emphasis, titles,
  pictures, project actions, transitions and the outgoing frame, no film-wide
  position, determinism); the YAML conversion keeps every YAML rule.
- [ ] 1.3 Layer 4: sets render their slots and chrome; elements draw their
  state; the registry refuses unknown kinds and slot mismatches by name;
  `tsc --noEmit` over `stage/` and over a generated `movie.d.ts`.
- [ ] 1.4 Layer 5: readback, pixel replay A-B-A, no masthead without
  `Chrome`, chrome hidden in picture-only captures, two views two instances,
  an instance kept across a cut, project state reaching its component, the
  proofs.
- [ ] 1.5 Layer 8: `check`, `preview`, `render` and `review` on the 0.2
  fixture movie and on the YAML fixture episode; a second render captures
  nothing; the manifest records the stage hash.
- [ ] 1.6 Layer 9: the manual pages exist; one schema file; `film.js` gone;
  no page source carries a brand or a series label.

## 2. Implementation

- [ ] 2.1 `src/schema.mjs` keywords; `src/movie.mjs` checks, resolution,
  load (D1, D2).
- [ ] 2.2 `src/episode.mjs` conversion (D3).
- [ ] 2.3 `src/timeline.mjs`, `src/words.mjs`, `src/code.mjs`,
  `src/pictures.mjs` (D4).
- [ ] 2.4 `stage/` runtime, shipped sets and elements (D5, D6).
- [ ] 2.5 `src/stage-build.mjs` (D7).
- [ ] 2.6 `src/render.mjs`, `src/review-samples.mjs`, `src/shot-cache.mjs`,
  `bin/videomaker.mjs`, `src/film.html`; `src/film.js` deleted (D8).
- [ ] 2.7 Fixtures: `fixtures/resolved/{minimal,tour}.json` pinned and
  reviewed by hand; the tour's `stage.tsx` and `stage.css`; the fixture
  revision re-pinned and the documents re-evaluated; the Python suite run.
- [ ] 2.8 Tests moved to `test/browser/` and `test/pipeline/`; the slow list.

## 3. Records

- [ ] 3.1 `docs/stage.md`; `docs/movie-document.md` wording; `docs/FORMAT.md`;
  `README.md`.
- [ ] 3.2 ADR-004 and ADR-006, the index, the architecture overview.
- [ ] 3.3 `AGENTS.md` status and testing sentences; `CHANGELOG.md`.
- [ ] 3.4 Findings in `workflow/warts.md` under a dated heading.
- [ ] 3.5 The whole suite cold before the final commit, and warm; counts and
  times in `evidence.md`.
- [ ] 3.6 Sync baseline specs and archive the change with the CLI.

## 4. Human review (not claimed by automation)

- [ ] 4.1 The film: produced in the Leonardo repository by the campaign's film
  step, and inspected by the pilot.
