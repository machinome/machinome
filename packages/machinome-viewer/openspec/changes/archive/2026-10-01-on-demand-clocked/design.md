## Context

`resolveOptions` (`options.ts`) admits `renderMode: 'on-demand'` only with
`animation: 'external'`, `autoplay: false`, `driverControls: 'none'` and
`partControls: 'none'`; it never sees the document. The document is
checked inside `mount` by `assertCaptureDocument` (`viewer.ts`), at the
initial load (`replaceTree`) and on `manifestChanged`: under on-demand it
refuses any document with `program`, with `clocked`, or with a non-empty
`instructions` table, all with one message.

A clocked machine is built by `startMachine` with a `pose` hook. Every
accepted `move`, `restore` and `reset` of `clocked/machine.ts` calls that
hook with the bank it is about to commit, and the hook updates the tree
and calls `renderer.render(scene, camera)`. So a clocked request already
poses and draws synchronously, without any frame; the spike saw
`partOnScreen` report the crank's new place with no frame between
`restore` and the read. Nothing of that depends on the frame loop.

Two clocked verbs do depend on it. `machine().trigger(name)` (`clockedPlay`)
makes its one request and then starts a drawing (`startDrawing`), advanced
by `drawingFrame` from the animation loop over the instruction's declared
seconds; without the loop the drawing's frame 0 (the transition's origin)
would stand on screen forever while the bank stands at its end.
`setClockPlaying(true)` sets a flag that `clockFrame` reads in the same
loop; without it, nothing would ever advance.

The animation loop is installed only when `renderMode === 'continuous'`.
The full-screen controller is inert under on-demand (`fullscreenAvailable`,
OpenSpec `go-fullscreen`, design D5). The clocked panel is built only when
`showsRunControls(driverControls, true)`, false for `'none'`, and part
controls follow `partControls: 'none'`.

## Goals / Non-Goals

**Goals:**

- A film host mounts a clocked document on-demand, poses each frame by
  `restore` (or `move`, `reset`) and captures it; the capture shows the
  bank it restored.
- A verb that cannot work without the frame loop says so instead of
  standing still.

**Non-Goals:**

- No drawing of a transition under on-demand: a host computes each frame's
  bank (the stroke's commit fractions are in the `ClockedRequest`) and
  restores it.
- No on-demand execution of a running program: its motion advances in
  ticks the loop drives (`runtime.frame`), and no film asks for it.
- No change to a posed document with instructions under on-demand (D2).
- No change to continuous mode.
- No new handle entry for redrawing (D3).

## Decisions

### D1. The document gate accepts a clocked machine

The check moves out of `mount` into `options.ts` as the pure
`assertOnDemandDocument(renderMode, document)`, so it is testable in node;
`mount` calls it where it called `assertCaptureDocument`. Under
`continuous` it accepts everything. Under `on-demand`:

1. a document carrying `program` is refused:
   `on-demand rendering cannot run a program: a running machine advances
   in ticks the frame loop drives; mount it with renderMode 'continuous'`;
2. a document carrying `clocked` is accepted, whether or not it declares
   instructions;
3. any other document with a non-empty `instructions` table is refused
   with today's message, `on-demand rendering requires a posed document
   without instructions`;
4. anything else is accepted, as today.

The program case is checked first, so a malformed document carrying both
is refused as a program.

### D2. A posed document with instructions stays refused

Its instructions are driver ramps (`viewer.trigger(name)`), advanced by
`drivers.tick()` inside the same loop. Admitting it would need the same
frame-loop refusal on `viewer.trigger`, and a host can already pose it by
`setDriver`. No film asks for it, so it stays as it is. A clocked
document's `viewer.trigger` already refuses for every mode (OpenSpec
`play-the-instruction`, design 11), so admitting clocked documents opens
no ramp path.

### D3. A request draws itself; `setView` redraws

No change to the pose hook: an accepted `move`, `restore` or `reset`
already poses and draws before it returns, in either mode. A capture taken
right after it shows the new bank. `setView` draws as before. A host that
wants to redraw without changing the view calls `setView(viewer.view())`:
`view()` returns the whole view (camera, target, up, field of view) and
`setView` adopts it unchanged and draws. That is documented rather than
adding an entry, since an accepted request never leaves the screen stale.

A refused `restore` or `move` throws before the hook runs, so neither the
bank nor the drawn pose moves.

### D4. The verbs that need frames are refused by name

`options.ts` gains the pure `assertFrameLoop(renderMode, verb)`: under
on-demand it throws
`<verb> needs the frame loop, which a renderMode 'on-demand' viewer does
not run. <advice>`. The machine handle calls it:

- `trigger(name)`, first, before the instruction is looked up or any
  request made, so the bank and the pose stand. Advice: pose the
  transition bank by bank with `machine().restore()`, or mount with
  renderMode `'continuous'`.
- `setClockPlaying(true)`, after the existing refusal of a machine with no
  clock (that message stays the truth for such a machine). Advice: advance
  the clock with `machine().move(clock, {by: seconds})`.
  `setClockPlaying(false)` is accepted: the clock is already stopped.

The ruling named `trigger`; `setClockPlaying(true)` is the same case (a
flag the loop reads, a page that silently never moves) and is refused here
for the same reason rather than left as a dead control.

### D5. No control, by the existing gates

No new gate is needed: the four mount conditions remove the clocked panel
and the part controls, and the full-screen controller is inert under
on-demand. A browser test pins it for a clocked document (no `button`,
`input`, `select`, `.clocked-controls`, `.machinome-fullscreen` in the
host), and `mount.rst` says the on-demand mount draws no full-screen
control.

### D6. API 29

What a host may now ask of the viewer changes (an on-demand mount of a
clocked document, and two refusals), so `machinomeViewerApi` rises from 28
to 29. No document field is read anew, so the document versions stay 1 to
13. The 0.7.1 release record stays API 27.

## Risks / Trade-offs

- [A request draws twice per film frame] -> a film frame is `restore` then
  `setView`, two renders. The spike measured `restore` at about 23 ms and
  `setView` at about 4 ms on the Curta; the capture dominates. Suppressing
  the hook's render under on-demand would make "an accepted request is on
  screen" mode-dependent, so it is kept.
- [A host that called `trigger` on an on-demand mount gets an exception]
  -> no such host exists: the mount refused clocked documents until now.
- [The refusal of a program changes its message] -> a host matching the
  old single message for a running document would no longer match; the
  old message stays for the posed-with-instructions case, the only one the
  manual's wording "posed document without instructions" described.

## Migration Plan

Additive: every mount that succeeded before succeeds the same way. A
clocked document that was refused under on-demand now mounts.

## Open Questions

None.
