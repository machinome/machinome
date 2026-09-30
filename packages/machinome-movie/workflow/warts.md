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
2. **`lines.end()` has no anchor of its own.** The Python side emits it as the
   spoken end of the shortest unique run of the narration's last words
   (`moment`, `stroke`, `progress`, `blade`, `description`). It works and is
   fragile in principle; a `narrationEnd` anchor form would say what is meant.
3. **Source emphasis lights only the excerpt's last line.** Enough for the
   film's three-line excerpt; a film that lights a word on another line has no
   spelling for it (`emphasize` takes no `line=`).
4. **A film is a whole number of frames on its own grid only.** `render --fps
   10` of a 30 fps movie may be refused; the quick silent look at a lower rate
   does not always work for a movie. Render movies at their own rate.
5. **Two fixture projects.** The Node side made a Node-generated fixture
   project and the Python side a seesaw project, so the shared fixtures rest
   on two models. One fixture project both sides read would be simpler.
6. **The speech key is read from the worktree's `.env`**, so a command run from
   a worktree finds no key until the primary checkout's file is sourced or
   linked. A path option or an environment-only lookup would avoid the trap.
7. **The narrator sets the film's length.** With every cut on a phrase and
   the chapter tails as the only slack, a 100-second shot list resolved to
   59 s once Jessica's takes were measured. That is the point of anchors, and
   an author needs to know it before estimating durations.

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
4. **Between the two halves the campaign branch has no reader.** After the
   Python side emits 0.2 and removes the 0.1 schema and fixtures, the Node
   suite fails on them until the Node side's change merges; the two cycles
   of one format change cannot land one at a time without a red suite.
5. **An element's prop types come from use.** With no prop declared on the
   class, the generated types list what the movie's instances give; a prop
   one movie omits and another gives cannot be optional, and two instances
   that disagree are refused. Enough for the film's one card; a reusable
   element library would want declared props.

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
2. **One element per slot per shot.** The YAML paper sets carry indexed slots
   (`top`, `top-2` … `top-8`, and so on) so that several captions of one
   position in one shot stay separate elements; a project template that wants
   a sequence of captions in one place must declare several slots. A slot
   that holds a sequence might be the better shape once a film asks.
3. **Chrome across two templates.** The live chrome is the incoming set's and
   the outgoing picture is captured without chrome, so a masthead that differs
   between two sets cuts at the join while the pictures dissolve or wipe. No
   film joins two templates with different chrome yet.
4. **Every pose repaints the whole page.** Four animation frames per pose (the
   old page did it only for fresh poses, pictures and source-only frames): the
   fixture tour captures 567 frames at 1280×720 in about two minutes with the
   viewer double. A long 1080p film pays it on every frame.
5. **One viewer per view element.** The contract's rule; *Cut and Advance*
   would mount six sawmill viewers in one page. Memory with the real viewer is
   unmeasured (layer 6 has no test).
6. **Three YAML refusals are not applied to movie documents** because the
   Python side emits documents that break them and the contract does not state
   them: an emphasis hold running past its shot's end (it now ends with the
   shot), a join longer than the shot it leaves (the outgoing shot continues),
   and an incoming join overlapping a fade-out (the join is drawn first).
   Whether the contract should refuse them is the orchestrator's; recorded as
   findings of the change.
7. **Emphasis words in a document may light out of spoken order.** The YAML
   rule that words follow the narration is not applied to (spoken, token)
   pairs.
8. **The fixture tour's still is 48 by 32 pixels** with an allowance of 1.5,
   so its template's plate is a 3.9 % stamp in a corner; a larger fixture
   still would let the template put the plate over the stage as the film does.
9. **The storyboard sorted samples by name**, and names had two digits: a
   preview with a hundred samples or more laid its contact sheet out of order.
   Names now have three digits; the Leonardo film will have more than a
   hundred.
10. **Cold memo artefacts leak.** With the cold switch the artefact memo
    writes into `/tmp/videomaker-cold-*` and removes them on the process's
    exit, which vitest's workers never reach; some two hundred directories had
    gathered by the end of this cycle. The global setup's teardown could
    remove them.
11. **A viewer refusal says "episode" for a movie** (`viewerApiRefusal`): the
    wording predates movie documents.
