## 0. Preconditions

- [x] 0.1 Base: branch `player-page` from `player` at `e7703df`, which
  carries `take-transport` and `live-server` merged (worktree
  `WTs/player-page`); `node_modules` is the primary's, linked, never
  installed into.
- [x] 0.2 Baseline on the base content: the Node suite cold with the API 29
  bundle selected (`VIDEOMAKER_VIEWER_BUNDLE`, passed by path, never
  written into the repository) and the Python suite; counts quoted in
  `evidence.md`.
- [x] 0.3 The orchestrator, as the campaign's ratification gate, ratified
  the planning artifacts and the readings of "Where the contract is read"
  by message on 4 October 2026, with two instructions folded in before the
  planning commit: the merge defect of the base (`test/repository.test.mjs`
  unparsed since e94ca59) fixed in this branch as its own commit, 2c46e84,
  before this one; and the ruler made a scrubber (pointer down and drag).
- [x] 0.4 2c46e84: the take-transport pin closed; the merged head's fifteen
  repository pins ran on it for the first time and passed.

## 1. Python: `watch` (layers 1 and 9, red first)

- [x] 1.1 Red: `python/tests/test_watch.py` (the loop with an injected
  listing and sleep: one evaluation at start, none over an unchanged
  listing, one per change of size, time or inode, file added or removed;
  one interval slept per step; `_build`, `.git`, `__pycache__` passed
  over), the command line on a copy of the fixture project (the path
  printed twice around a touched module, exit 0 on an interrupt;
  `--interval 0` refused naming it), and the manual pins in
  `test_repository.py` (`watch` in `docs/declaring-a-movie.md` and
  `python/README.md`). Run, record (the module absent; `watch` an unknown
  subcommand).
- [x] 1.2 `python/machinome_movie/watch.py`, the `watch` subcommand in
  `__main__.py` (D10). Green.

## 2. Layer 3: the marks in video time (red first)

- [x] 2.1 Red: `test/live.test.mjs`, `markInstants` of the resolved `count`
  and `tour` and the outline's `marks`. Run, record.
- [x] 2.2 `markInstants` and `outline`'s `marks` in `src/live.mjs` (D3).
  Green.

## 3. Layer 4: the player's pure parts (red first)

- [x] 3.1 Red: `player/model.test.ts` (snapping, the stage request and
  the join-as-cut rule, routing, the ruler's geometry and the time under a
  pointer, the readout, the reload decision), `player/poser.test.ts`; the
  `stage` project of `vitest.config.mjs` runs `player/**/*.test.ts`;
  `tsc --noEmit -p player/tsconfig.json` among the pure tests
  (`test/stage-types.test.mjs`). Run, record (`player/` absent).
- [x] 3.2 `player/model.ts`, `player/poser.ts`, `player/tsconfig.json`
  (D4 to D9). Green.

## 4. Layer 9: the build and the boundary (red first)

- [x] 4.1 Red: `test/player-build.test.mjs` (two places, one set of bytes,
  named by the tool; reuse; a damaged output rebuilt); the player's import
  pin and the transport's refusal of `../player/…` in
  `test/transport-boundary.test.mjs`; `test/support/reach.mjs` declares
  what `src/player-build.mjs` reads. Run, record (the module absent).
- [x] 4.2 `src/player-build.mjs` (D2), `player/index.html`,
  `player/index.ts`, `player/player.css` (D1, D4 to D9). Green.

## 5. Layer 8: `live` serves the built player (red first)

- [x] 5.1 Red: `test/pipeline/live.test.mjs`: `/`, `/player.js`,
  `/player.css` are the built player, a second session reuses it; a
  scratch file under `_build/player/` reloads nothing. Run, record (`/`
  404).
- [x] 5.2 `live` builds the player before serving and reports it (D2).
  Green.
- [x] 5.3 Added from the browser (6.1): `/narration.wav` answers its length
  and byte ranges (D5); red, then green, at layer 8.

## 6. Layer 5: the page in a browser (red first)

- [x] 6.1 Red: `test/browser/player.test.mjs` (the double; the session
  in-process): on `count`, the movie surface's pose equal to the
  renderer's, A-B-A pixels, the keys, the clicks, a drag across the
  boundary of `once` and `nine` posing frames of both and ending on the
  released time, the readout, the caption,
  the narration as the clock, the reload with the same stage hash, the
  reload of a changed stage module, a refusal shown and cleared; the take
  surface's marks with the recorded bank and its reload; on `tour`, the
  join rule, the reframe, the fade in, the loop surface.
  `test/viewer-double.mjs` mounts without a camera. Run, record.
- [x] 6.2 Green, the page corrected where the browser shows it wrong.

## 7. Layer 6: the take surface on the real viewer

- [x] 7.1 `test/viewer/player.test.mjs`: the take surface over the
  counter's export on the API 29 bundle, each mark clicked, the bank equal
  to the record.

## 8. Records (red first at layer 9)

- [x] 8.1 Red: `test/repository.test.mjs` pins (the README's player:
  surfaces, keys, what is not drawn live, `watch`; the changelog bullet
  `(\`player-page\`, ADR-022)`; the ADR index row; the overview names
  `player/` and `src/player-build.mjs` and no longer says the page is not
  built; `AGENTS.md`'s status line and layer 4). Run, record.
- [x] 8.2 ADR-022 (PIPELINE, Proposed) and its index row;
  `README.md`; `docs/declaring-a-movie.md`; `python/README.md`;
  `docs/architecture-overview.md`; `AGENTS.md`; `CHANGELOG.md` (one bullet
  under `Unreleased`). Green.

## 9. Proof

- [x] 9.1 The Node suite cold on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [x] 9.2 `evidence.md`: every run (command, counts, time, cold or memo),
  the red-first output, findings, deviations, what was not done.
- [x] 9.3 Stop before committing the implementation, for the
  orchestrator's review.

## Not in this cycle

Syncing the baseline specs, archiving the change and promoting ADR-022:
the pilot ordered the campaign to stop before sync until the player has
been validated in a browser. No film is touched and no proof runs on a real
film (finding 16 of `workflow/warts.md`); nothing is listened to or
published. The episode (the Curta's take on the take surface, a timing
revision seen live) is the pilot's, in a browser.
