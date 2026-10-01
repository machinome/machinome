## Why

Videomaker films a machinome model by mounting the viewer with
`renderMode: 'on-demand'` (with `animation: 'external'`, `autoplay: false`,
`driverControls: 'none'`, `partControls: 'none'`), posing every frame
explicitly and capturing it: a frame is a pure function of video time and
no frame loop runs. Its next film is the Curta adding 23 + 145 on the
project's clocked machine (`Calculators/Curta-Type-I-3x`, model
`clocked_curta` = `simulation.clocked:ClockedCurta`, a version 8 document).

The curta-video campaign's spike
(`videomaker/WTs/curta-video/workflow/ongoing/curta-video-campaign/spike.md`,
1 October 2026, against this repository's `main` 94cfcc0, API 28) found:

- `mount` refuses that document under on-demand, verbatim
  `on-demand rendering requires a posed document without instructions`
  (`viewer.ts`, `assertCaptureDocument`), and `mount.rst` documents the
  refusal.
- Under `continuous` everything the film needs already works:
  `machine().restore({identity, bank})` accepts a bank whose input lies
  mid-path, poses the tree synchronously and deterministically (A, B, A
  gives byte-identical captures across launches), `move` reproduces the
  framework's requests bit for bit, and a highlight survives `restore`.
- But a 1920x1080 capture costs 12.3 s in continuous mode against 0.43 s
  on-demand for a comparable posed model (the frame loop and the headless
  software GPU contend), so a one-minute film would take about six hours
  to capture once.

What the film needs from the viewer is the mode it already uses for posed
models, admitted for a clocked machine.

## What Changes

- `renderMode: 'on-demand'` accepts a document carrying a `clocked`
  machine (version 8), with or without declared instructions, under the
  same four mount conditions it already requires. A running program
  (`program`) stays refused, now with a message of its own; a posed
  document with instructions stays refused with today's message.
- Under on-demand, `machine().move`, `restore` and `reset` pose the model
  and draw it before they return, as they already do in continuous mode;
  `setView` draws too, and `setView(viewer.view())` redraws without
  changing the view. No new handle entry.
- Under on-demand, `machine().trigger(name)` is refused, naming the mode,
  before any request is made: it draws a transition over the
  instruction's declared seconds, which needs the frame loop. A host poses
  the transition bank by bank with `restore`. `machine().setClockPlaying(true)`
  is refused for the same reason; `setClockPlaying(false)` and a clock
  advanced by `move(clock, {by})` remain.
- An on-demand mount shows no control: no clocked panel, no part control,
  and no full-screen button (already true since `go-fullscreen`; now
  pinned for a clocked document and documented).
- Viewer API 28 -> 29. The document versions stay 1 to 13.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: an on-demand viewer mounts, poses and draws a clocked
  machine, and refuses the two clocked verbs that need a frame loop.

## Impact

`machinome_viewer/widget/src/options.ts` (a pure on-demand document check
and a pure frame-loop refusal), `viewer.ts` (the mount's document check,
`machine().trigger` and `setClockPlaying`), `package.json`
(`machinomeViewerApi` 29), `options.test.ts`, `version.test.ts`; browser
tests in `tests/test_widget_e2e.py`; API pins in `tests/test_bundle.py`,
`tests/test_documentation.py`; `docs/reference/mount.rst`,
`docs/reference/clocked.rst`, `docs/compatibility.rst`,
`docs/embedding.rst`; `CHANGELOG.md` (an `Unreleased` section above
0.7.1); ADR-077. Nothing is pushed or published, and the bundle is built
only in this worktree.
