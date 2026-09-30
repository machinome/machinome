# Fix-warts campaign — plan

Status: working plan, 30 September 2026, opened on branch `fix-warts`
(worktree `WTs/fix-warts`) from `main` at e30b05f, the head the pilot had
the react-stage campaign merged to the same afternoon. Closed the same
evening at the pilot's word ("this is taking too long … leave the agent
running and validate the other cycles") on seven of the eight cycles;
`flaky-pixel-proofs` runs on in `WTs/flaky-pixel-proofs` and is integrated
later if it brings anything. `PROGRESS.md` has every commit and run. The pilot's words:
"merge to main. then make a list of warts in videomaker that you can work on
autonomously. orchestrate cycles on all those." Nothing here is ratified;
each cycle ratifies its own change under `AGENTS.md`, the orchestrator's
adversarial review being the ratification gate the pilot delegated.
Integration of `fix-warts` into `main` is the pilot's.

## The list

Every entry of `workflow/warts.md` was read and sorted into three piles. The
first pile is this campaign: findings a real film produced, whose fix is
within the tool's settled design, needs no product choice the pilot has not
made, no spending and no episode that does not yet exist. The second pile is
settled without a cycle, its triage written into `warts.md` by the
orchestrator. The third waits for the pilot or for an episode.

### Cycles (the orchestrator's autonomous pile)

| # | change | warts | what it does |
|---|---|---|---|
| 1 | `narration-end-anchor` | Cut and Advance 2, 7 | An anchor for the end of a chapter's narration, `{"narrationEnd": true}` with `plus`, emitted by `Narration.end()` instead of the shortest unique tail; the commands print each chapter's take beside its resolved length, and the manual says the narrator sets the film's length |
| 2 | `speech-key-lookup` | Cut and Advance 6 | The speech command finds its key in the environment, then in the checkout's `.env`, then in the primary checkout's `.env` through Git's common directory, and its refusal names where it looked; tests keep reading no key |
| 3 | `pose-repaints` | React stage 4, Cut and Advance v2 5 | A pose waits only for what can change the picture; measured on the fixture tour and proved by the pixel proofs run cold repeatedly; the real-viewer evidence is the film re-rendered after the merge |
| 4 | `viewer-instances` | React stage 5, Cut and Advance v2 4 | Viewer instances are pooled by model and leased to view elements, so a film mounts no more than the largest number of views one frame shows; the A-B-A proof covers a re-leased instance |
| 5 | `flaky-pixel-proofs` | The test suite 1 | The two intermittent pixel proofs reproduced under load, their cause found and fixed red first, or the non-reproduction recorded with its runs |
| 6 | `fixture-hygiene` | Declarative stage 3, React stage 8 | A larger fixture still so the tour's plate covers the stage as the film's does; a re-pin helper for the fixture project's revision so a template edit is one command |
| 7 | `viewer-integration-layer` | Cut and Advance v2 1, React stage 5 | Layer 6: tests over a real viewer bundle selected by path, skipped by name when none is given, never assumed: the view element over a real posed export, the late canvas cases the film met, the A-B-A proof with the real viewer, memory per instance measured and recorded |
| 8 | `check-measures-the-stage` | React stage 1, Cut and Advance v2 6 | `check` measures each set's slot geometry once in the browser after bundling, so a picture's enlargement beyond its allowance and a view that leaves the picture are refused before speech for a project's set as they are for the shipped ones |

Waves, chosen so that cycles touching the same files do not run at once:

- Wave 1: 1, 2, 3 in parallel (Python and resolution; the speech command;
  the stage runtime).
- Wave 2: 4, 5, 6 (the runtime again, after 3; the suite; the fixtures,
  after 1 has re-pinned them).
- Wave 3: 7, 8 (layer 6 over the runtime 3 and 4 settled; `check` and the
  runtime's measurement).

Each is a complete two-commit OpenSpec cycle on an opus agent in its own
worktree `WTs/<change>` cut from the `fix-warts` head, unless the agent
classifies it as a narrow adjustment under `AGENTS.md` and says so in its
record. The orchestrator reviews every cycle adversarially, merges it into
`fix-warts`, records its triage in `warts.md` and a row in `PROGRESS.md`.
Agents never edit `warts.md`; their findings go to their change's
`evidence.md`. After the last merge the whole Node suite runs cold once on
the campaign head, the Python suite runs, and *Cut and Advance* is
re-rendered on the real viewer as the film evidence for cycles 3, 4 and 8.

### Settled without a cycle (triage recorded in `warts.md`)

- Cut and Advance 1: resolved by the react-stage change, which ends an
  emphasis with its shot instead of refusing the hold.
- Cut and Advance 3: resolved by `declarative-stage` (`line=` on an
  emphasis).
- Cut and Advance 5: resolved by `declarative-stage` (one fixture project).
- Declarative stage 1 and 2: ruled before the merge (a dot bounds a token).
- Declarative stage 4: a campaign-process finding, closed by the merge.
- React stage 6: the orchestrator's ruling at the react-stage review stands;
  the relaxed rules are accepted because anchors make durations unknowable
  when authoring.
- React stage 7: not a defect; a (spoken, token) pair carries its own
  instant, so no order is owed between pairs.
- React stage 9, 10, 11: fixed by `react-stage` and `test-memo-sharing`.
- Cut and Advance v2 2 and 3: by design; an author retunes a mark's offset
  and a camera's lens when the container changes.

### Waiting for the pilot or for an episode

- Cut and Advance 4: whether a lower-rate look may drop a partial frame is a
  product choice.
- Declarative stage 5: declared props wait for a reusable element library.
- React stage 2: a slot that holds a sequence waits for a film that asks.
- React stage 3: chrome across two templates waits for a film that joins
  them.

## Evidence to keep

`PROGRESS.md` beside this plan records worktrees, commits, test runs and the
render. The campaign archives to `workflow/archive/fix-warts-<date>/` with
its report once the pilot has inspected the result.
