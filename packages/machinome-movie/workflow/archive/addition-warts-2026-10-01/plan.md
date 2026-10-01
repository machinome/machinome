# Addition-warts campaign — plan

Status: done, 1 October 2026. Nine cycles and one investigation merged on
`addition-warts`, its closing cold suite green (Node 408, Python 291), the
branch fast-forwarded into `main` the same day and this directory moved to
`workflow/archive/`; what the table below calls wave 3 is done too, except
the film's re-render, recorded in PROGRESS. Written as a working plan,
1 October 2026, on branch `addition-warts` (worktree `WTs/addition-warts`)
from `main` at 54d64d8, which holds the
curta-video campaign (ADR-010 to ADR-012, the Curta film *Addition*) and
the fix-warts campaign before it, both integrated that morning. Nothing
here is ratified: each cycle ratifies its own change under `AGENTS.md`,
the orchestrator's adversarial review being the gate the pilot delegated.
The branch fast-forwards into `main` when every cycle is merged and both
suites are green on its head, by the pilot's ruling of 1 October 2026 that
a finished campaign is integrated, not forked from.

## The findings and their triage

`workflow/warts.md`, section "Addition (Curta, 1 October 2026)": fourteen
findings met while producing the Curta film and the cycles it needed.
Triage of 1 October 2026, the pilot's rulings where marked and otherwise
the orchestrator's cuts, which the pilot may overturn:

| finding | triage |
|---|---|
| 1. `preview` and `render` serve every `.stl` or image string in the manifest and fail with a bare `ENOENT` | cycle `serve-what-the-viewer-reads` |
| 2. the highlight proof cannot tell the right part from the wrong one | cycle `proofs-report-the-look`; cut: no proof can know the intended part, so the review pack carries the lit frame, the unlit frame and their difference for every highlight, named by the part it lights |
| 3. a continuation through a join crosses a mark silently | cycle `check-the-continuation`; cut: a `check` report line naming the shot, the mark and the step, not a refusal |
| 4. no line says when a title wraps or code is too small | cycle `proofs-report-the-look`; cut: `check` reports measured code sizes and headline line counts, no threshold, no refusal |
| 5. render provenance records `projectHead` for a dirty tree | cycle `honest-provenance` |
| 6. `check`'s `Stage:` line hashes only `stage.js` | cycle `honest-provenance` |
| 7. mark times drift when `over` durations are summed in floats | cycle `exact-take-times` |
| 8. two contract corrections | written into "The take" at the merge of pose-a-take; no cycle |
| 9. the take's identity cannot be read from `Sim` | the framework's bench `curta-findings`, cycle `sim-identity`; Videomaker consumes it in a later cycle once that change is in the framework's `main`, since this suite runs on the workspace venv's framework |
| 10. marks on a take with the viewer double stay put | cycle `double-poses-a-bank` |
| 11. a reframe through a slot sized by what it holds is refused | no film needs it; recorded, no cycle |
| 12. a reframe frame costs one canvas wait more | a measurement; no cycle |
| 13. the on-demand viewer blanks its canvas on a resize | the viewer's, recorded in its log by its cycle; no cycle |
| 14. the film is 126 s for 278 words; the render cost 63 min at a second a frame | pilot, 1 October: the pace is the screenplay's and the wart is about performance only. Investigation `render-cost` first: where the second goes. A fix follows if the cost is capture, encoding, waiting or Node-side work; the wart is **deferred** if only a GPU would remove it, because the GPU is on the virtual machine's host, not in it, and that is the pilot's separate decision |

The pilot's other ruling of the day: the framework's export records its
source revision inside `manifest.json` (additive, no version bump). That
is the bench's cycle `export-records-its-revision`, and it decides cycle 8
below.

## Cycles

| # | change | findings | ADR reserved | wave |
|---|---|---|---|---|
| 1 | `serve-what-the-viewer-reads` | 1 | none used; ADR-013 reassigned to cycle 10 | 1 |
| 2 | `honest-provenance` | 5, 6 | ADR-015 (PIPELINE) | 1 |
| 3 | `exact-take-times` | 7 | ADR-016 (SOURCE) | 1 |
| 4 | `render-cost`: investigation, one commit, no product change; done 1 Oct: 88 % of a frame is the software raster, wart 14 **deferred** | 14 | none | 1 |
| 5 | `check-the-continuation` | 3 | ADR-014 (TIMELINE) | 2 |
| 6 | `proofs-report-the-look` | 2, 4 | ADR-017 (PIPELINE) | 2 |
| 7 | `double-poses-a-bank` | 10 | ADR-018 (PIPELINE), or a dated section of ADR-008 | 2 |
| 8 | `read-the-exports-source`: `model.sourceRevision` pinned from the manifest's `source` instead of `source-revision.txt`, the dirty marker read into provenance; the Curta's hand-typed file deleted and Leonardo's gallery script relieved of writing it (project work, direct) | 9 and the ruling above | to assign | 3, after the framework bench is in its `main` |
| 9 | struck 1 Oct: `render-cost` proposes no fix; only a GPU removes the second | 14 | — | — |
| 10 | `stable-stage-bundle`: a stage bundle built from the same sources is the same bytes from any checkout (finding 15) | 15 | ADR-013 (PIPELINE) | 2 |

An ADR number is reserved per cycle and used only for an architectural
decision; a number not used is released, and the orchestrator renumbers
at the merge so the sequence stays dense.

Each cycle is a complete two-commit OpenSpec cycle on an opus agent in its
own worktree `WTs/<change>` cut from the `addition-warts` head, reviewed
by the orchestrator before its merge. The briefs name the finding, where
it lives, the proof and the film evidence; the agents never edit
`warts.md`. Wave 1 runs beside the framework bench's first two cycles.

## After the campaign

The Curta film's workaround (the symlink `export/clocked_curta/STLs` in
its untracked export) is removed when cycle 1 lands, and `check` and
`preview` of the film are run again on the campaign head; the film itself
is not re-rendered unless a cycle changes a picture input, which none is
meant to.

## Evidence to keep

`PROGRESS.md` beside this plan records worktrees, commits, test runs and
merges. The campaign archives to `workflow/archive/addition-warts-<date>/`
once the branch is in `main`.
