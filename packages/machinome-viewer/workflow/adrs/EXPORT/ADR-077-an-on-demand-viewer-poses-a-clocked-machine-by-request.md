# ADR-077: An on-demand viewer poses a clocked machine by request

**Status:** Accepted

**Date:** 2026-10-01

**Change:** `on-demand-clocked`

**Extends:** [ADR-062: The viewer executes a clocked machine in thread](ADR-062-the-viewer-executes-a-clocked-machine-in-thread.md) (where a clocked machine may be mounted), [ADR-064: A clocked instruction is one request, drawn over its duration](ADR-064-a-clocked-instruction-is-one-request-drawn-over-its-duration.md) (when that drawing is possible)

**Builds on:** [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md) (API 29)

## Context

`renderMode: 'on-demand'` mounts a viewer with no animation-frame loop:
the host poses and draws each frame itself and captures it. It required
`animation: 'external'`, `autoplay: false`, `driverControls: 'none'` and
`partControls: 'none'`, and accepted only a posed document without
instructions; a running program, a clocked machine and a document with
instructions were all refused with one message.

A host capturing a clocked machine frame by frame (the Curta adding
23 + 145, `ClockedCurta`, a version 8 document) found the refusal, and
found that continuous mode, which it admits, costs 12.3 s per 1920x1080
capture against 0.43 s on demand for a comparable posed model, because
the frame loop and the headless software GPU contend. In continuous mode
every pose it needs already worked: `restore` of a bank with the crank
mid-stroke, `move` bit for bit with the framework, a highlight that
survives a restore.

A clocked request does not need the frame loop. The machine's `pose` hook
updates the tree and renders inside every accepted `move`, `restore` and
`reset` (ADR-062). Two verbs do need it: a played instruction is drawn by
the loop over its declared seconds (ADR-064), and a running clock is
advanced one request per loop frame (ADR-063).

## Decision

**Under on-demand rendering a clocked machine is accepted and posed by
request; the verbs that draw over wall seconds are refused by name; a
running program and a posed document with instructions stay refused.**

1. `options.ts` holds the document gate, `assertOnDemandDocument`, a pure
   function the mount calls at load and on every republish. A `program`
   is refused with its own message; a `clocked` document is accepted with
   or without instructions; any other document with instructions keeps
   the earlier refusal.
2. Every accepted `move`, `restore` and `reset` poses and draws before it
   returns, in either mode, through the existing hook. `setView` draws and
   re-fits the clipping planes to the posed model; `setView(viewer.view())`
   is the redraw that changes nothing else. No handle entry is added.
3. `machine().trigger(name)` and `machine().setClockPlaying(true)` call
   the pure `assertFrameLoop` first and throw under on-demand, naming the
   verb and the mode, before any request is made. Stopping the clock is
   accepted.
4. No control is drawn: the four mount conditions already remove the
   clocked panel and part controls, and the full-screen controller is
   inert under on-demand.
5. The viewer API rises to 29; the document versions do not move.

## Consequences

- A host captures a clocked machine at the on-demand cost, posing a
  transition bank by bank from a request's `origin`, `end` and commit
  `fraction`s, with no wall clock anywhere in the frame.
- A capture after `restore` alone shows the new bank but keeps the near
  and far planes of the last framing; the frame that depends only on the
  bank and the view is the one after `setView`. On the calculator fixture
  the two differ in a few dozen pixels.
- A posed document's instructions remain a continuous-mode feature; making
  them free would need the same refusal on `viewer.trigger`, and no host
  asks for it.
- A running program remains continuous-only: its ticks are the loop's.
