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

## Addition (Curta, 1 October 2026): the first film on a clocked take



Findings met while producing the curta-video campaign's film

(`projects/Calculators/Curta-Type-I-3x/videos/addition/`: `takes.py`,

`movie.py`, `stage.tsx`, `stage.css`) and while building the cycles it

needed (`declare-a-take`, `pose-a-take`, `reframe-join`, the viewer's

`on-demand-clocked`). Triage: none yet unless stated; the pilot decides each.



1. **`preview` and `render` serve every `.stl` or image string in the

   manifest as an export asset and fail with a bare `ENOENT`.** `stage()` in

   `src/render.mjs` walks the whole manifest; the framework's `pieces[].sources`

   paths are provenance relative to the project, not files in the export.

   The refusal names neither the field nor the cause; the film worked around

   it with a symlink in the untracked export. The smallest fix collects

   assets from the model fields only, or tolerates source files the viewer

   never reads.
    Triage, 1 October 2026 (orchestrator): fixed by `serve-what-the-viewer-reads` (archived 2026-10-01, merged the same day): the renderer serves exactly the `model` files the manifest's `root` tree and its markings name, and refuses a lost or escaping one before Chromium launches, naming field, node and path; no ADR. The film's symlink workaround is removed when the campaign lands.

2. **The highlight proof cannot tell the right part from the wrong one.** A

   highlight on the bevel tips at the top of the shafts passed changed,

   restored and reapplied exactly as the one on the input pinions beside the

   drum does; the wrong part was caught by looking.
    Triage, 1 October 2026 (orchestrator): fixed by `proofs-report-the-look` (archived 2026-10-01, merged the same day, ADR-017): `preview` keeps every highlight's lit, unlit and difference images at the cue's midpoint under `preview/highlights/`, named by shot, cue and parts, indexed by part in `report.json` with the changed pixels and their box, and prints a `Highlight …` line; for a highlight that dims or ghosts the rest the difference is taken against a review-only pose with the rest kept, so the red marks the named parts alone (the agent's D4a, overturnable; the film is drawn as before).

3. **A shot's continuation through a join is refused only when it leaves the

   take.** `read_23` ran into the next step (a slide moving) during its

   dissolve and nothing said so; a `check` line when a continuation crosses

   a mark would have.
    Triage, 1 October 2026 (orchestrator): fixed by `check-the-continuation` (archived 2026-10-01, merged the same day, ADR-014): resolution follows a shot through its outgoing join on the output frames and, when its take time crosses a mark, the shot's `model.crossing` names join, mark and step, and `check` prints the sentence after its take line; a report, never a refusal.

4. **No proof or check line says when a title wraps or code is too small.**

   `check` reports a headline "sized by what it holds" and the fit proof

   passed at 0.82 vw; both were found by looking.
    Triage, 1 October 2026 (orchestrator): fixed by `proofs-report-the-look`: `check`'s layout probe measures each shot's source panels (`fontSize`, in px and vw) and titles (`lines`, `subtitleLines`) and prints `Shot <id>: …` lines; no threshold, no refusal; a movie the probe does not measure (no picture, no reframe) gets a `Text not measured:` line and still opens no browser.

5. **Render provenance records `projectHead` for a dirty tree.** The film's

   source was uncommitted at render time and the manifest names the last

   commit as if it were the content rendered.
    Triage, 1 October 2026 (orchestrator): fixed by `honest-provenance` (archived 2026-10-01, merged the same day, ADR-015): `projectDirty` and `workflowDirty` beside the heads, `Project tree:` and `Videomaker tree:` lines, `releaseIssues` in words; a dirty tree is not release-ready and is never refused.

6. **`check`'s `Stage:` line hashes only `stage.js`**; a stylesheet change

   leaves it identical, though the manifest carries `cssSha256`.
    Triage, 1 October 2026 (orchestrator): fixed by `honest-provenance`: the `Stage:` line carries the stylesheet's hash beside the script's.

7. **Mark times drift when `over` durations are summed in floats** (moves of

   1.2 s gave marks like 12.599999999999998); the film chose binary-exact

   1.25 s. Evaluation could sum on the frame grid or in exact arithmetic.
    Triage, 1 October 2026 (orchestrator): fixed by `exact-take-times` (archived 2026-10-01, merged the same day, ADR-016): take time is the exact sum of the written decimals in both runtimes; a document summed in floats is refused by field; a mark is posed on its recorded bank exactly.

8. **A step owns `at < t ≤ at + duration`, and the input at `f = 1` is `end`

   itself**: two corrections the pose-a-take change made to the contract

   (written into "The take" at the merge). Triaged 1 October 2026

   (orchestrator): fixed; no cycle.

9. **The take's identity cannot be read from `Sim`**, so evaluation compares

   the bank's ids with the export and leaves the identity to the viewer's

   `restore`; filed as a framework finding (its `workflow/warts.md`,

   1 October 2026), with `Sim` failing through a symlinked project path and

   `machinome export` writing no `source-revision.txt`.
    Triage, 1 October 2026 (orchestrator): the framework side fixed (`sim-identity`, a read-only `Sim.identity`, in the framework's `main` 096217f with `export-records-its-revision`, ADR-158); the revision half consumed by `read-the-exports-source` (archived 2026-10-01, merged the same day, ADR-019): both runtimes take `model.sourceRevision` from the manifest's `source.revision`, refuse an export without one by name, and carry the export's dirt as provenance (`Export:` line, `exportRevision`/`exportDirty`, a `releaseIssues` entry); nothing reads `source-revision.txt`. The identity half fixed by `take-identity` (archived 2026-10-01, merged the same day; ADR-011 amended in place): evaluation reads `sim.identity` and refuses, before any step, a take whose model is not the machine the export publishes, naming the take, the model as `module:Class`, the export and both identities; the bank-ids rule stays for what the identity cannot catch, an `initial` bank missing or exceeding the machine's drivers and states (new invalid fixture `take-initial-incomplete`). Wart 9 closed.

10. **Marks on a take with the viewer double stay put**: the double's part

    rectangles move with a loop's time, not a bank, so a mark on a clocked

    take is proved only at layer 6.
    Triage, 1 October 2026 (orchestrator): fixed by `double-poses-a-bank` (archived 2026-10-01, merged the same day): the double's part rectangles follow the input its machine names (`follows: {input, range}`), refused by name when it names none or one the bank lacks; one shared assertion (`test/support/mark-on-a-take.mjs`) proves a ring on the units drum moves between the take's start and the mark `one` and returns exactly, at layer 5 on the double and at layer 6 on the bundle; no ADR (ADR-018 released).

11. **A reframe through a slot sized by what it holds is refused**, since the

    slot has no box until its content is drawn; the tour's headline is such

    a slot. A film that wants to reframe into one needs a fixed box.
    Triage, 1 October 2026 (orchestrator): no cycle: no film needs it.

12. **A reframe frame costs one canvas wait more** (about 33 ms at 640 px),

    since a moving host is a resize every frame.
    Triage, 1 October 2026 (orchestrator): no cycle: a measurement.

13. **The on-demand viewer blanks its canvas on a resize until the next

    explicit render**; the stage's `setView` after the canvas wait is what

    redraws it. Older than this campaign; recorded by the viewer cycle.
    Triage, 1 October 2026 (orchestrator): no cycle: the viewer's, recorded in its log by its cycle.

14. **The film is 126 s** for 278 words: the take's steps were drawn at the

    narration's pace, and the render cost 63 min at about a second a frame

    on the real viewer (3 787 frames). The pose itself is 14 ms; the

    screenshot is the cost.
    Triage, 1 October 2026 (orchestrator): the pace is the screenplay's (pilot). The render cost was investigated (`render-cost`, merged 2026-10-01, report under `workflow/ongoing/addition-warts-campaign/render-cost.md`): 88 % of a Curta frame is SwiftShader rasterizing the viewer's WebGL draw in Chromium's GPU process, capture proper is 90 ms, the pose 35 ms, Node 2 ms, and no capture alternative moved the frame. **Deferred** by the pilot's ruling: only a GPU removes it, and the GPU is on the virtual machine's host. Data kept for that decision: the viewer's multisampled context is about 70 % of the raster; two concurrent sessions give 1.4× throughput with identical bytes.

### Findings met by the campaign's cycles (1 October 2026)

Recorded at the merges; triage by the orchestrator unless stated.

15. **The stage bundle's hash depends on the checkout that built it.** esbuild writes a path comment per module and the paths embed the checkout (`WTs/<name>/…`); the Curta film has three `stageSha256` values (`e5c7bccec003`, `c82a3718550a`, `6298cd57909a`) for bundles byte-identical once the prefix is masked, and `/stage.js` is in the shot cache's common key, so a render from another checkout recaptures every shot. The stage build's own key hashes absolute runtime paths too, so another checkout rebuilds rather than reuses. Found by `serve-what-the-viewer-reads` and `honest-provenance`. Triage: fixed by `stable-stage-bundle` (archived 2026-10-01, merged the same day, ADR-013): the bundle names every file it read by the tool or the project repository, never by where either lies on the machine, and its build key is content and names, so two checkouts give one `stage.js` and the second reuses the first's bundle.
16. **The film's `_build/` is shared by concurrent agents**: while one cycle previewed the Curta film another rebuilt its `_build/stage/` and a third rewrote `movie-resolved.json`. Process, not tool: a campaign's proofs on a real film run one at a time, or on copies. No cycle.
17. **The Curta project leaves `export/`, `CREDITS`, `curta-2x-files/`, a reference video and a screenshot untracked and not ignored**, so every render of the film is reported dirty until the project ignores or commits them. Project work; `export/` is a build product the orchestrator ignores at the campaign's close, the rest is the pilot's.
18. **A `{mark, plus}` model time is still a float sum on the Node side**, range-checked with the remaining 1e-9 tolerance; no declaration writes one and no film has one. Found by `exact-take-times`. Recorded; the same exact sum in the resolver if a film ever needs it.
19. **The old `markAt` tolerance could only match instants the pose rule does not put on the mark's bank**, which would have been refused as "Viewer bank differs from the take at mark". Latent since pose-a-take; fixed by `exact-take-times` making the match exact.
20. **Playwright's default launch flags and `--disable-gpu` give different bytes from the stage's flags** (1 958 pixels a frame by at most 2 levels) with no speed change; the flags reach the shot cache's key through `render.mjs`. Found by `render-cost`. Recorded.
21. **Each capture session pays 10 to 15 s of warm-up on its first Curta frame**, and the stage's repaint costs 45 to 60 ms on frames whose page content changed. Found by `render-cost`. Recorded.
22. **The viewer's multisampled WebGL context is about 70 % of the software raster** (a Curta frame 1.18 s against 0.36 s without it; every picture changes). The viewer's; filed in its log at the campaign's close.
23. **The film as rendered crosses two marks it never meant to:** `set-23` runs 0.35 s (about 21°) into the first crank stroke and `set-145` 0.23 s (about 14°) into the second, under their dissolves; `read-23`'s crossing was the one caught by eye. Found by `check-the-continuation` on the film's own resolved document. Film work for its author, not the tool's.
24. **The take block does not record a trigger's instruction name**, so a trigger's step is reported as "moves crank_rotation by 360" rather than "Turn crank". The smallest correction is an optional `instruction` on a trigger's step in the contract. Found by `check-the-continuation`. Recorded; no cycle until a film wants the name on screen.
25. **Neither runtime refuses `from > to` on a take's shot**, and a backward continuation would not be reported. Found by `check-the-continuation`. Recorded; no film runs a take backwards.
26. **A stage module that imports a file from outside both the tool and the project repository** still gets a bundle name that depends on the machine; no film does it; documented, not refused. Found by `stable-stage-bundle`.
27. **The bundle's names are rewritten in esbuild's output** (the `//` module line, the module wrapper's string, the `/* */` stylesheet line), so the rewrite depends on esbuild's output shape; the lockfile pins esbuild and the two-checkout test pins the bytes. Orchestrator's note at the merge: a plugin that names modules at resolve time was rejected in the change's design; if esbuild's output changes, the two-checkout test says so first.
28. **The Curta project moved under the campaign:** its `main` advanced to f2ad951 ("Rename Curta models to posed, mechanistic and event-driven") at 09:04 while the campaign's cycles ran their film proofs, so the film's evaluated document (`_build/movie.json`, 03:15) is stale against its sources and `check` refuses from every checkout (`the token 'Driver' is absent from line 52 of the excerpt drivers`). Found by `stable-stage-bundle`. Project work at the campaign's close: evaluate, export and prove the film again on the renamed project.
29. **The real viewer's rectangle for a turned drum changes size more than place** (its centre moves about 2 px between units 0 and 1): a ring shows the change, a label barely would. The viewer's; recorded. Found by `double-poses-a-bank`.
30. **The fixture counter's marks are whole crank turns**, so the real viewer draws the handle alike at every mark, and only the take's start and the mark `one` share a box; a fixture that wants a mark-to-mark proof needs a mark mid-turn. Found by `double-poses-a-bank`. Recorded.
31. **`speech` generates missing takes, which are paid, before it loads the film**, so an unrecorded or mismatched export is refused only after paying. Pre-existing. Found by `read-the-exports-source`. Recorded; the smallest fix loads and refuses first.
32. **A fixture export's revision cannot be Videomaker's HEAD**: the fixture movies' source panels run `git show <revision>:…` in the recipe's own repository, and Videomaker's tree is dirty while a change is made; `scripts/pin-fixture-project.mjs --machinome` therefore exports inside the recipe commit (10b189d1516c…, clean). Found by `read-the-exports-source`; the brief had assumed otherwise. Settled.
33. **Exporting two models from one checkout records the second dirty unless `_build/` is ignored**, since the first build is left untracked; the pin recipe ignores it in `.git/info/exclude`. The Curta ignores neither `_build/` nor `export/` (finding 17). Found by `read-the-exports-source`.
34. **The schema allowed `"sourceRevision": null`**, which nothing produced or accepted; the orchestrator tightened it to a string at the merge of `read-the-exports-source`. `docs/FORMAT.md`'s "A null revision marks unpinned source" was corrected by the cycle.
35. **Text is measured only when the layout probe runs** (a picture or a reframe in the movie); measuring every film would amend "no picture, no browser" in the contract and its scenario. Found by `proofs-report-the-look`. Recorded; the contract stands.
36. **With the rest kept, a highlighted part partly hidden by parts in front shows only its visible pixels in the difference.** Found by `proofs-report-the-look`. Recorded.
37. **The probe measures a shot's text without the shot's other elements**; a template whose title width depends on a sibling would be mis-measured; no fixture or film does that. Found by `proofs-report-the-look`. Recorded.
38. **The film's README names `export/event_driven_curta` while its document reads `export/clocked_curta`**, after the project's rename (finding 28). Project work at the close. Found by `proofs-report-the-look`.
39. **A machine's identity depends on the module its model is imported from**: the same `counter.py` gives the export's identity as `models.counter` and another under another module name, so a take evaluated through a different `PYTHONPATH` spelling is refused as another machine. The framework's definition; the refusal names `module:Class` for it. Found by `take-identity`. Recorded here and worth the framework's log.
40. **A document evaluated before `take-identity` from a changed model still passes `check`**, carrying the export's identity; only evaluating it again, or the viewer's `restore` at preview, catches it. Found by `take-identity`. Recorded.

