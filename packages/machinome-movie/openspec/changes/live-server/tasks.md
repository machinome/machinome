## 0. Preconditions

- [x] 0.1 Base: branch `live-server` from `player` at `b86f88b` (the
  campaign's plan and contract over `main` at `7fba270`), worktree
  `WTs/live-server`; `node_modules` is the primary's, linked, never
  installed into.
- [ ] 0.2 The orchestrator, as the campaign's ratification gate, reviews
  the planning artifacts and the contract readings of the proposal
  ("Where the contract is refined").
- [ ] 0.3 The viewer bundle for layer 6 is passed by path in the
  environment (`VIDEOMAKER_VIEWER_BUNDLE`), never written into the
  repository.

## 1. The extractions, behaviour unchanged

- [ ] 1.1 `src/check.mjs`: `commandOptions`, `summaryLine`, `checkSource`
  (design D1), the code moved from `bin/videomaker.mjs`; the script's
  `check` calls `checkSource` and exits; the other commands call
  `commandOptions` and `summaryLine`. Run the pipeline tests that pin
  `check`'s lines (`test/pipeline/movie-pipeline.test.mjs`, then the whole
  slow project) before anything else; record.
- [ ] 1.2 `src/film-assets.mjs`: `filmFiles`, `clipUses`, `filmAssets`
  (D2), moved from `src/render.mjs`; `browserSession` uses them; the
  common key gains `assets`. `test/support/reach.mjs` declares what
  `film-assets.mjs` reads. Run the browser and pipeline layers; record.

## 2. Layer 3, pure (red first)

- [ ] 2.1 Red: `test/live.test.mjs`: `frameFor` gives `frameAt` at the
  nearest output instant for the resolved fixture `count` (its excerpt
  attached as a load attaches it), clamps below 0 and past the end to the
  first and last frames, and refuses `NaN`, `Infinity`, `undefined` and a
  string naming `t`; `outline` of the resolved `count` and `tour` gives the
  contract's shape (chapters, shots with their resolved `model`, joins,
  cues in video time, the take or the loop with its sorted marks, speech
  flags, stage hash, viewer API, generation, refusal), and the session's
  geometry at a width. Run with `src/live.mjs` absent; record.
- [ ] 2.2 `frameFor` and `outline` (D5). Green.

## 3. Layer 8, serial (red first)

- [ ] 3.1 Red: `test/pipeline/live.test.mjs` (declared in
  `test/support/reach.mjs` as spawning the command line and reading the
  fixtures):
  - through the module on `count`: the printed lines equal `check`'s
    (`bundled` or `reused` aside); `/film.json`; `/frame` at a time between
    frames, below 0, past the end, and refused without a number;
    `/film.html`, `/config.json`, `/stage.js`, `/stage.css`, `/viewer.js`,
    `/model/manifest.json` byte for byte; `/`, `/player.js` 404 `The player
    is not built`, then served once `_build/player/` holds them;
    `/narration.wav` and `/captions.json` 404, then, after `speech` mixes
    the cached take (no request), served and flagged, by a reload;
    `/events`' first event; files written under `_build/stage/`,
    `_build/preview/` and as `movie-resolved.json` start no reload; the
    document written again gives `generation` 2 and the check lines again;
    the stage module of a copy of `tour` made to import a second module
    reloads, and a change to that second module reloads again (the watched
    set recomputed from the new generation);
    broken, `refused` with generation 2 still served and `/film.json`
    carrying the refusal; restored, `generation` 3; `close()` ends the
    stream and frees the port;
  - through the module on the YAML fixture episode: `production.yaml`
    written again reloads it;
  - through the command line on `tour` with `--port <free port>`, `--poll
    100` and `--open` (an `xdg-open` on the path that records its
    arguments): the check lines (layout, reframe, picture, text) then the
    `Live:` line on that port; the opened address; `/film.json`'s loop and
    joins; `/frame` inside the reframe; `/pictures/stills/plate`; the
    document changed, found by polling, `generation` 2; SIGINT, exit 0,
    the port free;
  - through the command line: a document that is not JSON refused with
    `check`'s message and exit 1; an `xdg-open` that fails does not fail
    the command; `--port` and `--poll` refused by name when malformed;
    `--fps` refused for `live`, `--port` for `check`.
  Run cold before `live` exists (the command refused as unknown, the
  module's `live` absent, the routes absent); record.
- [ ] 3.2 `live` (D3, D4, D6, D7, D9), `assetServer({port})`, the command
  (D8). Green.

## 4. Layer 9 and the records (red first)

- [ ] 4.1 Red: `test/repository.test.mjs`: every option the command line
  declares is documented in `README.md`; the README documents `live`, its
  address line and its routes; the usage line names `live`; the changelog
  bullet `(\`live-server\`, ADR-021)`; the ADR index row; the architecture
  overview names `src/check.mjs`, `src/film-assets.mjs` and `src/live.mjs`.
  Run; record.
- [ ] 4.2 `README.md`, `CHANGELOG.md` (one bullet under `Unreleased`),
  `docs/adrs/PIPELINE/ADR-021-…md` (Proposed) and its index row,
  `docs/architecture-overview.md`, `AGENTS.md`'s status line. Green.

## 5. Proof

- [ ] 5.1 The Node suite cold (`npm test -- --cold`) with the API 29
  bundle selected, and the Python suite; summaries quoted.
- [ ] 5.2 `evidence.md`: every run (command, counts, time, cold or memo),
  the red-first output, the reload times measured on `count` and `tour`,
  findings, what was not done.
- [ ] 5.3 Stop before committing the implementation, for the
  orchestrator's review.

## Not in this cycle

Syncing the baseline spec, archiving the change and promoting ADR-021: the
pilot ordered the campaign to stop before sync until the player has been
validated in a browser. No film is touched; no proof runs on a real film
(finding 16 of `workflow/warts.md`).
