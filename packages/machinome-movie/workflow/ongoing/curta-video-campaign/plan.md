# Curta video campaign — plan

Status: working plan, 1 October 2026, opened on branch `curta-video`
(worktree `WTs/curta-video`) from `fix-warts` at 430d3af, the head of the
fix-warts campaign, which was not yet integrated into `main` when the
campaign opened; the film needs that stage. Both branches were integrated
into `main` on 1 October 2026 (see the status below). The pilot's goal is `workflow/ongoing/curta-video.md`, quoted
here in full:

> Make a Curta video and build videomaker full declarative python api
> around it. Curta is our most complex and reliable project, the one that
> made the framework reach the complexity it has. I want the same done for
> videos. You'll create a video demonstrating the curta calculator. It's not
> a full demo, addition is enough. This video must contain: one full
> scenario that will be demonstrated, 23 + 145; a detailed explanation on
> how this works, highlighting components on narration; an explanation how
> machinome works, showing pieces of code and highlighting words synced with
> narration to illustrate how expressive machinome is; the transition to
> the code will be: curta will be full screen; in the same scenario, its
> container will shrink to right half of the screen; code will fade in a
> second container; a narration will show some code and curta will animate.
> It's important that the transition in the previous item happens with
> continuity of the camera on the curta model.

Nothing here is ratified; each cycle ratifies its own change under
`AGENTS.md`, the orchestrator's adversarial review being the gate the pilot
delegated ("make sure you follow the subagent orchestration discipline").
Integration of `curta-video` into `main` is the pilot's.

Done, 1 October 2026 (small hours): the spike, `declare-a-take`
(ADR-011), `pose-a-take` (ADR-012) and `reframe-join` (ADR-010) are merged
on `curta-video`; the viewer cycle `on-demand-clocked` (its ADR-077, API 29)
was fast-forwarded into the viewer's `main` (94cfcc0 → fcd870a) on
1 October; *Addition* is rendered in the Curta project
(`videos/addition/_build/rehearsal.mp4`, 3 787 frames, 126.23 s, every
proof green, the take replayed on the viewer). `PROGRESS.md` has every
commit and run; the findings are in `warts.md` under "Addition". `curta-video`
was fast-forwarded into `main` (e30b05f → 42c4294) on 1 October, on the
pilot's ruling that a finished campaign is integrated, not forked from.
What waits for the pilot: the film's licence statement in
`description.md`, the release addresses, and watching the film.

## What the film needs that the tool lacks

1. **A clocked machine on screen.** The commands refuse anything but a
   posed normalized loop (`Only posed normalized-loop models are
   supported`). The Curta that adds is `ClockedCurta`
   (`simulation/clocked.py` of the project): drivers `digit_1`…`digit_8`,
   `crank_rotation`, `crank_elevation`, `carriage_rotation`,
   `carriage_elevation`, `clearing_rotation`; the instruction `Turn crank`
   (`crank_rotation` by 360, duration 6); states for the result and turns
   registers. This is step 6 of the direction note
   (`workflow/ongoing/declarative-python-api.md`): machine takes, with the
   viewer parity requirement, born from the first episode that needs them.
2. **The shrink.** A join in which the view's container moves from the
   whole frame to the right half while the code fades into the left, the
   camera held and the take running through it. No transition does this:
   dissolve, fade, wipe and slide compose two pictures.
3. Everything else exists on `fix-warts`: source beside the model with
   spoken words lighting tokens, highlights and marks on narration, a
   project template that owns the screen, titles, pictures, the chrome
   through fades, `check` before speech.

## The pieces, by repository

- **Framework.** Nothing new is asked for this step. A clocked `Sim`
  publishes what a take needs: `move(input, by=|to=)` and `trigger(name)`
  return a `Request` with `origin`, `end`, `admitted`, `commits` (each with
  `fraction`, `value`, `targets`, `relations`) and `stops`; `snapshot()`
  gives the bank; the export (document version 8) carries the machine's
  identity, its drivers, states and instructions. The orchestrator's cut:
  the take is recorded by the movie's evaluation through that public API,
  and a framework command that records takes is a later step if a second
  project asks for one. Not the pilot's choice; stated here so it is not
  mistaken for one.
- **Viewer.** Expected: nothing new. `viewer.machine()` gives
  `restore({identity, bank})`, which puts the committed bank in place, and
  `move`, which solves a request the same way the framework does (the
  curta-speed campaign made the two bit-exact over one corpus). The spike
  confirms that a restored bank, including one with an input mid-path,
  poses synchronously and deterministically. If it does not, a viewer cycle
  (`pose-a-bank`) is cut in the viewer repository, two changes in two
  repositories.
- **Videomaker.** Three changes: `declare-a-take` (Python), `pose-a-take`
  (Node and the stage, layer 6 parity), `reframe-join` (Python, Node and the
  stage). A tiny clocked fixture, the framework tutorial's counter
  (`docs/tutorial/counter/c09_clocked.py` of the framework), joins the
  fixture project with a real export.
- **Curta project.** The clocked export (a build product, untracked, as the
  Leonardo export is), then `videos/addition/`: the spec, the take, the
  movie, the template.

## The take: the orchestrator's contract

Written into `docs/movie-document.md` and the schema before cycle 1 runs;
the sketch here is what the contract says in prose.

```python
class Addition(Take):                       # a clocked take, beside the model
    model = ClockedCurta
    export = "../export/clocked_curta"
    readiness = "The clocked Curta: digits, strokes and carries are exact; …"
    steps = [Move("digit_1", to=3, over=0.4), Move("digit_2", to=2, over=0.4),
             Mark("set_23"), Trigger("Turn crank"), Mark("added_23"),
             Move("digit_1", to=5, over=0.4), …, Trigger("Turn crank"), Mark("added_145")]
    face = Camera(…)
    slides = Layer(ClockedCurta.input_selectors)
```

- A `Take` is the second kind of take beside `Loop`; the posed loop stays
  the trivial take. Its `steps` are `Move(input, to=|by=, over=seconds)`,
  `Trigger(instruction)` (its duration is the instruction's declared one)
  and `Mark(name)`. Take time is the sum of the durations; a mark is the
  instant after the step before it.
- Evaluation records the take once through the framework's `Sim` over the
  declared model: for each step the `Request` as the framework returns it,
  the bank before the first step, and the bank at every mark; and the
  machine's identity from the export. The document carries it under
  `takes.<name>` with `kind: "clocked"`; `model.timeMode` is `"take"` for
  a view on it.
- A step's pose at a fraction `f` of its duration is the bank before the
  step with the moving input at `origin + f·(end − origin)` and the targets
  of every commit whose `fraction ≤ f` written, which is the rule the
  viewer draws an instruction by (its ADR-064). The resolved frame carries
  the view's bank; the stage restores it and sets the camera. A frame is a
  pure function of take time.
- Parity is proved, not assumed: at every mark the viewer's bank after
  `restore` equals the take's; and the viewer's own `move` from a step's
  origin bank reproduces the recorded request (`origin`, `end`, the commits'
  fractions and targets). Both checks run at layer 6 over the fixture
  counter and at preview over the film.
- A posed loop's `from`/`to`/`keys` stay as they are; a clocked view's
  model time runs with take time from the mark the shot starts at.

## Cycles

| # | change | repository | depends on |
|---|---|---|---|
| 0 | spike: the clocked Curta export; parity of the viewer's requests with the framework's on 23 + 145; a restored mid-path bank poses; the cost of a pose; a highlight on the clocked export; the canvas after a resize | Curta project (export) and a videomaker worktree (evidence only, no product change) | nothing |
| 1 | `declare-a-take` | videomaker, Python side; the fixture counter and its real export | the contract |
| 2 | `pose-a-take` | videomaker, Node and the stage; the viewer double gains a machine; layer 6 parity | 0 and 1 |
| 3 | `reframe-join` | videomaker, Python, Node and the stage | nothing |
| 4 | the film: `videos/addition/` | Curta project, direct project work | 1, 2 and 3 merged |

Waves: 0 and 3 in parallel; then 1; then 2; then 4. Each of 1 to 3 is a
complete two-commit OpenSpec cycle on an opus agent in its own worktree
`WTs/<change>` cut from the `curta-video` head, reviewed by the
orchestrator before its merge; 0 is an evidence note committed to this
directory; 4 is project work in the Curta repository by an opus agent, with
the orchestrator inspecting storyboard, stills and the film.

## The film

From the pilot's note, in chapters; the screenplay is cycle 4's to write
and the orchestrator's to review before any speech is bought.

1. The question: the Curta full frame, at rest; the problem, 23 + 145, as a
   title or a card the template draws.
2. Setting and adding 23: the setting slides move to 3 and 2 as the
   narration names them (highlights on the slides), the crank turns (the
   step drum, the result dials highlighted as the narration explains the
   stroke), the result reads 23.
3. The second operand: 145, the stroke, 168; the carry explained with a
   highlight on the carry lever.
4. How machinome says it: the reframe, the Curta's container shrinking to
   the right half with the camera held, the code fading in on the left (the
   `ClockedCurta` declarations: `crank_rotation`, `commits`, `at=stroke`,
   `law=advance`), tokens lit as the narration speaks them while the crank
   turns again.
5. Closing.

Speech: the narration is bought once, when the screenplay is final, under
the pilot's request for a narrated video; nothing is bought before, and the
cycles work with fixtures and doubles.

## Evidence to keep

`PROGRESS.md` beside this plan records worktrees, commits, test runs, the
spike's numbers and the render. The campaign archives to
`workflow/archive/curta-video-<date>/` once the pilot has inspected the film.
