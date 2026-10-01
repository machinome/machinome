# Warts — Videomaker findings, in the order they were met

Working record. Nothing here is ratified; an entry is evidence, not a
requirement, and becomes work only through an OpenSpec change in this
repository (or the viewer's, for viewer findings). Entries are grouped by the
episode that produced them and record the pilot's triage in place.

No entry yet. The frictions met by the sawmill rehearsal and the release-film
source study before this file existed are recorded in `docs/first-rehearsal.md`
and in the archived OpenSpec changes.

## Cut and Advance (Leonardo, 30 September 2026): the first film declared in Python

Findings met while producing the declarative-python campaign's validation
film from `videos/cut_and_advance/movie.py`. Triage: none yet; the pilot
decides each.

1. **A hold that ends exactly at a snapped shot end is refused.** The split
   shot ended at `spoken_end(phrase, plus=0.9)` and its emphasis cleared at
   the phrase end plus 0.9 s; the shot end snapped to the frame grid landed
   up to half a frame earlier, so `Emphasis clears after shot coupling ends`.
   The film shortened the hold. A resolver could snap a cue's end to the same
   frame as the shot's when they are written on the same anchor, as it
   already does for a model keyframe's last `at`.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): resolved by
   `react-stage`, which ends an emphasis with its shot instead of refusing
   the hold; no cycle.
2. **`lines.end()` has no anchor of its own.** The Python side emits it as the
   spoken end of the shortest unique run of the narration's last words
   (`moment`, `stroke`, `progress`, `blade`, `description`). It works and is
   fragile in principle; a `narrationEnd` anchor form would say what is meant.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `narration-end-anchor`; fixed the same day (7e0aa12): `{"narrationEnd":
   true}` is the end of the take's last letter or digit, and `lines.end()`
   emits it; every existing cut keeps its frame.
3. **Source emphasis lights only the excerpt's last line.** Enough for the
   film's three-line excerpt; a film that lights a word on another line has no
   spelling for it (`emphasize` takes no `line=`).
   Triaged 30 September 2026 (orchestrator): resolved by `declarative-stage`
   (`line=` on an emphasis); no cycle.
4. **A film is a whole number of frames on its own grid only.** `render --fps
   10` of a 30 fps movie may be refused; the quick silent look at a lower rate
   does not always work for a movie. Render movies at their own rate.
   Triaged 30 September 2026 (orchestrator): left to the pilot; whether a
   lower-rate look may drop a partial frame is a product choice.
5. **Two fixture projects.** The Node side made a Node-generated fixture
   project and the Python side a seesaw project, so the shared fixtures rest
   on two models. One fixture project both sides read would be simpler.
   Triaged 30 September 2026 (orchestrator): resolved by `declarative-stage`;
   both suites read `python/tests/fixtures/project`; no cycle.
6. **The speech key is read from the worktree's `.env`**, so a command run from
   a worktree finds no key until the primary checkout's file is sourced or
   linked. A path option or an environment-only lookup would avoid the trap.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `speech-key-lookup`; fixed the same day (5b5cd77): environment first,
   then the checkout's `.env`, then the primary work tree's, and the
   refusal names where it looked.
7. **The narrator sets the film's length.** With every cut on a phrase and
   the chapter tails as the only slack, a 100-second shot list resolved to
   59 s once Jessica's takes were measured. That is the point of anchors, and
   an author needs to know it before estimating durations.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `narration-end-anchor` (the manual says it; the commands print each
   chapter's take beside its resolved length); done the same day (7e0aa12):
   `check` prints `take … chapter … tail …` per chapter, and
   `docs/declaring-a-movie.md` says the narrator sets the film's length.

## The test suite (one-runner cycle, 30 September 2026)

Findings met while moving the Node suite to vitest and memoizing it
(`openspec/changes/archive/2026-09-30-one-runner/evidence.md`). Not an
episode's; recorded here because the suite is the tool's proof. Triage: none
yet; the pilot decides.

1. **A second intermittent pixel test.** The base run under `node --test`
   failed `a movie document is refused before its takes, then checks, speaks,
   previews and renders from them` (`test/movie-pipeline.test.mjs`) with
   `Partial picture replay is not deterministic: wheel #0 at 1.00 s` from
   preview's picture proof; the same file alone passed right after, and the
   three whole-suite vitest runs of the cycle that executed it passed it.
   With the already known `every incremental PNG equals a separately cold
   film across the first reused-shot gap` (seen in the movie-document
   cycle's base run, not in this cycle's runs), the suite has two pixel
   proofs that fail rarely under load. The memo makes this sharper: a flaky
   test that passed once is not run again until its inputs change, so only
   the cold run before integration shows it.
   Worth finding the cause rather than retrying.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `flaky-pixel-proofs`.

## Declarative stage (react-stage campaign, 30 September 2026): the Python side of the stage

Findings met while making the `machinome_movie` package evaluate to
`machinome-movie/0.2` (`declarative-stage`) and checking the *Cut and
Advance* version 2 source against it. Triage: none yet; the pilot decides
each.

1. **A spoken concept cannot light a segment of a dotted path.** *Triage
   (orchestrator, 30 September 2026): ruled the other way before the merge; a
   dot is a boundary, so `waterwheel` is a token inside
   `water_drive.waterwheel.spin`, and an emphasis may name its `line` when a
   token repeats in the excerpt. The film keeps its words.* The token
   rule counts whole identifiers, dots included, so in the film's coupling
   excerpt (`water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)`)
   neither `waterwheel`, `drives` nor `crankshaft` is a token; the source was
   respelled to light the whole calls. A film that wants the one word lit
   inside a path needs a sub-token spelling, which no episode has asked for
   beyond this one.
2. **The contract's token example cannot hold.** *Triage (orchestrator,
   30 September 2026): resolved with wart 1; the contract now states the
   boundary rule in words and its example is `feed.pawl.turn`.* It says *the driving pawl*
   may light `feed.pawl`; under the rule stated in the same sentence,
   `feed.pawl` never occurs where the source says `feed.pawl.turn`. Recorded
   as a contract finding in the change's evidence.
3. **The fixture project's stage module is under its revision hash.** The
   tour's placeholder `videos/tour/stage.tsx` is a file of the fixture
   project, so writing its real components changes
   `export/seesaw/source-revision.txt` and every Python fixture document
   with it. Whoever writes the components re-pins and re-evaluates in the
   same change; the two sides share one fixture project (wart 5 of the
   previous entry) and now one file in it.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `fixture-hygiene` (a re-pin helper; the revision keeps covering the whole
   project, as a real project's commit does); done the same day (7058acf):
   `node scripts/pin-fixture-project.mjs` re-pins the project and its
   documents in one command.
4. **Between the two halves the campaign branch has no reader.** After the
   Python side emits 0.2 and removes the 0.1 schema and fixtures, the Node
   suite fails on them until the Node side's change merges; the two cycles
   of one format change cannot land one at a time without a red suite.
   Triaged 30 September 2026 (orchestrator): a finding about the campaign's
   process, closed by the merge; no cycle.
5. **An element's prop types come from use.** With no prop declared on the
   class, the generated types list what the movie's instances give; a prop
   one movie omits and another gives cannot be optional, and two instances
   that disagree are refused. Enough for the film's one card; a reusable
   element library would want declared props.
   Triaged 30 September 2026 (orchestrator): waits for the episode that
   needs a reusable element; no cycle.

## The React stage (react-stage campaign, 30 September 2026)

Findings met while building the `react-stage` change (the Node side of
`machinome-movie/0.2` and the stage). Triage: none yet; the pilot decides each.

1. **A picture's geometry is only known in the browser.** A slot's box is
   the set's layout, so `check` cannot refuse a picture's enlargement beyond
   its allowance, or a view that leaves the picture, for a project's set;
   preview and render refuse them against the box the stage reports. YAML
   episodes still refuse them at `check` (the paper sets' boxes are known).
   A layout measured once per set when `check` bundles the stage would move
   the refusal before speech.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `check-measures-the-stage`; done the same day (8b0beae, ADR-009): `check`
   measures each set's slots in a headless page and refuses the enlargement
   before any take is read; a slot sized by what it holds is still preview's.
2. **One element per slot per shot.** The YAML paper sets carry indexed slots
   (`top`, `top-2` … `top-8`, and so on) so that several captions of one
   position in one shot stay separate elements; a project template that wants
   a sequence of captions in one place must declare several slots. A slot
   that holds a sequence might be the better shape once a film asks.
   Triaged 30 September 2026 (orchestrator): waits for a film that asks; no
   cycle.
3. **Chrome across two templates.** The live chrome is the incoming set's and
   the outgoing picture is captured without chrome, so a masthead that differs
   between two sets cuts at the join while the pictures dissolve or wipe. No
   film joins two templates with different chrome yet.
   Triaged 30 September 2026 (orchestrator): waits for a film that joins two
   templates; no cycle.
4. **Every pose repaints the whole page.** Four animation frames per pose (the
   old page did it only for fresh poses, pictures and source-only frames): the
   fixture tour captures 567 frames at 1280×720 in about two minutes with the
   viewer double. A long 1080p film pays it on every frame.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `pose-repaints`; done the same day (77f3a98): a pose repaints only for a
   proof pose, a mounted, replaced or resized view, or content that differs
   from the last repaint's (ADR-004 amended); the tour captures at 5.3–5.4
   frames a second from 4.8–4.9; the film's number is measured after the
   campaign.
5. **One viewer per view element.** The contract's rule; *Cut and Advance*
   would mount six sawmill viewers in one page. Memory with the real viewer is
   unmeasured (layer 6 has no test).
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycles
   `viewer-instances` (the count) and `viewer-integration-layer` (the
   measurement). The count landed the same day (2f24b66, ADR-007): view
   elements lease instances frame by frame, so a film mounts no more than
   the most views one frame places; *Cut and Advance* mounts one. The
   measurement landed with layer 6 (eab6b4f): on the fixture seesaw an
   instance costs 5 to 6 MB of resident memory; the sawmill's is measured
   on the re-render that closes the campaign.
6. **Three YAML refusals are not applied to movie documents** because the
   Python side emits documents that break them and the contract does not state
   them: an emphasis hold running past its shot's end (it now ends with the
   shot), a join longer than the shot it leaves (the outgoing shot continues),
   and an incoming join overlapping a fade-out (the join is drawn first).
   Whether the contract should refuse them is the orchestrator's; recorded as
   findings of the change.
   Triaged 30 September 2026 (orchestrator): the ruling at the react-stage
   review stands; the relaxed rules are accepted because anchors make
   durations unknowable when authoring; no cycle.
7. **Emphasis words in a document may light out of spoken order.** The YAML
   rule that words follow the narration is not applied to (spoken, token)
   pairs.
   Triaged 30 September 2026 (orchestrator): not a defect; each pair carries
   its own instant, so no order is owed between pairs; no cycle.
8. **The fixture tour's still is 48 by 32 pixels** with an allowance of 1.5,
   so its template's plate is a 3.9 % stamp in a corner; a larger fixture
   still would let the template put the plate over the stage as the film does.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `fixture-hygiene`; done the same day (7058acf): the still is drawn at
   864 by 576 and the tour's plate covers the stage.
9. **The storyboard sorted samples by name**, and names had two digits: a
   preview with a hundred samples or more laid its contact sheet out of order.
   Names now have three digits; the Leonardo film will have more than a
   hundred.
   Triaged 30 September 2026 (orchestrator): fixed within `react-stage`; no
   cycle.
10. **Cold memo artefacts leak.** With the cold switch the artefact memo
    writes into `/tmp/videomaker-cold-*` and removes them on the process's
    exit, which vitest's workers never reach; some two hundred directories had
    gathered by the end of this cycle. The global setup's teardown could
    remove them.
    Triaged 30 September 2026: fixed by `test-memo-sharing`; a cold run's
    products live in one run directory the global teardown removes, and the
    next run removes a killed run's. The old code's leftovers are the pilot's
    to delete.
11. **A viewer refusal says "episode" for a movie** (`viewerApiRefusal`): the
    wording predates movie documents.
    Triaged 30 September 2026: fixed by `test-memo-sharing`; the refusal says
    "This movie needs" for a movie document and "This episode needs", as
    before, for a YAML episode.

## Cut and Advance, version 2 (Leonardo, 30 September 2026): the first film on a project template

Findings met while producing the film on the React stage
(`projects/Leonardo/videos/cut_and_advance/`, `movie.py`, `stage.tsx`,
`stage.css`). Triage: none yet; the pilot decides each.

1. **The real viewer sizes its canvas on its own animation frame, and shrinks
   it to nothing while its host is detached.** The stage waited for the
   canvas only after a resize, so the film's first frame was refused (`Viewer
   canvas does not fill its view`), and once that was fixed the preview's
   samples were refused when a view came back after shots without it: the
   viewer had observed the detached host at no size and set its canvas to
   0×0. Fixed on the campaign branch (the stage waits, bounded, on a fresh
   mount, a change of set and a re-attached host, and poses after the wait);
   the viewer double gained `lateCanvas` so a browser test pins it. Layer 6,
   the real viewer, still has no test; this is what it would have caught.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `viewer-integration-layer`; done the same day (eab6b4f, ADR-008): layer 6
   exists, gated on `VIDEOMAKER_VIEWER_BUNDLE`, and its canvas test fails
   with the wait removed, as this finding would have.
2. **A mark's offset is a fraction of the view's box, so a split container
   changes where a label lands.** The holding-pawl label written for the
   full-width view left the frame in the split's 43 % container; the offset
   moved to the part's left. An author retunes offsets when the template
   changes, which is what the rule means.
   Triaged 30 September 2026 (orchestrator): by design; no cycle.
3. **A camera framed for the whole frame is too tight for a container.** The
   `pawls` camera at 37° cut the ratchet off in the split; 46° frames it. A
   camera belongs to a take and a view to a slot, so a shot in a narrower
   container wants its own camera or a wider lens.
   Triaged 30 September 2026 (orchestrator): by design; no cycle.
4. **Six viewer instances of the sawmill cost about 1.5 GB in Chromium** and
   rendered without trouble; the instances are never disposed. A longer film
   with more chapters mounts one per view element.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `viewer-instances`; done the same day (2f24b66): the film's six view
   elements share one leased instance; the memory is measured on the
   re-render that closes the campaign.
5. **The render took 638 s for 1769 frames at 1080p** (about 2.8 frames a
   second), the whole film recaptured because the template's bundle is a
   common key. Every pose repaints (wart 4 of "The React stage"); the render
   itself is where a film's time goes now.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `pose-repaints`; the bundle stays a common key, since a template change
   may change every frame. The cycle landed the same day (77f3a98); the
   film's re-render with the real viewer is the campaign's closing
   evidence.
6. **The picture's enlargement is checked only in the browser** (wart 1 of
   "The React stage"): the still over a full-frame plate slot passed at
   preview and render; `check` could not say so before speech.
   Triaged 30 September 2026 (orchestrator, fix-warts campaign): cycle
   `check-measures-the-stage`; done the same day (8b0beae): `check` prints
   the film's peak and allowance from the measured plate box, before speech.

## Fix-warts campaign (30 September 2026): findings met while fixing warts

Findings the seven cycles of the fix-warts campaign recorded in their
`evidence.md` (or, for a narrow adjustment, in their report), gathered here
by the orchestrator. Triage: none yet unless stated; the pilot decides each.

1. **The renderer accepts a canvas larger than its box.** Its check asks
   only that the canvas cover 98 % of the box; with the canvas wait removed,
   preview passed a 435×288 canvas in a 282×245 box, and only the viewer
   layer's own assertion caught it. The smallest fix is to refuse a canvas
   more than a pixel larger than its box (`viewer-integration-layer`).
2. **`lines.end()` with no `plus` on a chapter's last cut is refused by
   `speech`:** the take's file runs past its last letter (0.16 s in the
   doubles) and `speech` wants 0.1 s of slack after the file ends. The
   per-chapter tail line `check` now prints shows it before `speech`
   refuses; the behaviour is unchanged (`narration-end-anchor`).
3. **The two runtimes name a malformed `narrationEnd` differently.** For
   `{"narrationEnd": true, "phrase": "it"}` Python names the field and
   Node names `phrase` too; no shared fixture carries this form
   (`narration-end-anchor`).
4. **No fixture pixel proof sees Chromium's glyph-edge effect.** Never
   repainting a pose is caught only by preview's picture replay, and
   repainting only fresh and resized poses passes every browser proof; the
   repaint rule is pinned by counting animation frames. The repaint itself,
   about 55 ms, is now the remaining cost of a pose (`pose-repaints`).
5. **Below Viewer API 28 an instance is leased only to a view with the lens
   it mounted with**, since `setView` cannot change up or field of view
   there; the count bound is exact from API 28 and per lens below it. Only
   layer 4 tests it: no fixture below 28 has two lenses
   (`viewer-instances`).
6. **The picture refusal wording is written twice**, in `src/pictures.mjs`
   and `src/layout.mjs`, because `pictures.mjs` is hashed into every film's
   shot-cache common key and sharing the two functions would have recaptured
   every film (`check-measures-the-stage`).
7. **A view that leaves its picture is refused before preview, not before
   `speech`**, because its view keys may be spoken anchors; the enlargement
   needs no times and is refused before `speech` (`check-measures-the-stage`).
8. **The layout probe's content test is a probe, not a proof:** a slot that
   changes only for content of another shape than the large block would be
   trusted wrongly; preview and render still refuse against the live box
   (`check-measures-the-stage`).
9. **`docs/stage.md` quotes the fixture tour's `stage.css` word for word
   and nothing pins it**, so the manual can fall behind the fixture; a pure
   test comparing the fenced block with the file would pin it
   (`fixture-hygiene`).
10. **Render's `pictures.cues[].peak` is measured at the render's width**,
    not the film's output width: at `--width 640` it reports half of what
    preview checks at 1280, as the code comment says; a manifest reader could
    misread it (`fixture-hygiene`).
11. **The invalid fixtures carry stale revisions** and drift further with
    every re-pin; no refusal depends on the revision. Triaged 30 September
    2026 (orchestrator): harmless; no cycle (`fixture-hygiene`).
12. **The real viewer tints and dims only parts that declare a colour**; the
    fixture's blocks gained one so a highlight reaches the pixels. Its
    cameras frame the seesaw small; whether to change them is the pilot's
    (`viewer-integration-layer`).
13. **The old `.env` loading copied the key into the process environment**,
    so Chromium and FFmpeg inherited it; fixed in passing by
    `speech-key-lookup`, which parses the file instead. Triaged 30 September
    2026 (orchestrator): fixed; no cycle.
14. **The set's chrome vanished during every picture or mark fade.** A frame
    with a fading picture or mark is blended from picture-only captures, and
    the stage left the page's picture-only state set after the blend, so the
    masthead was missing from 47 of the fixture tour's 567 frames and from
    the still's fade-in of *Cut and Advance* (frame at 51.72 s, inspected);
    no proof saw it, since the fade proofs only ask that the blended frame
    differ from its references. Found by the `flaky-pixel-proofs`
    investigation reading the kept tour frames. Triaged 1 October 2026
    (orchestrator): fixed the same night as a narrow adjustment
    (`chrome-through-blends`, 53a788c; the blend request now says whether the
    frame is picture-only, and a browser test proves a blended frame differs
    from its picture-only capture in the chrome and nowhere else).
15. **The two intermittent pixel proofs: one cause found, on the old page
    only.** Twenty cold runs on the stage under load passed; twenty on the
    old film page reproduced `Partial picture replay is not deterministic`
    twice, word for word, and the failing pairs are byte-identical across
    runs: 453 pixels one level apart inside the still's detail, two discrete
    renderings. The old page sized a picture only after decoding it, and
    Chromium 151's GPU rasterization draws an image shown at about half its
    size or less one of two ways, chosen per page; the stage sizes its
    pictures in CSS before they load and drew one way in every page tried.
    The incremental frame-1 failure did not reproduce in forty runs and stays
    unexplained. Report, run tables, the failing pair, the difference map and
    a reproduction script: `workflow/ongoing/fix-warts-campaign/flaky-pixel-proofs.md`
    and the directory beside it. Triaged 1 October 2026 (orchestrator): no
    fix, since the stage does not meet the cause; the wart under "The test
    suite" is closed for the picture replay and stays open for the
    incremental frame, which a future failure must keep as the report says.
