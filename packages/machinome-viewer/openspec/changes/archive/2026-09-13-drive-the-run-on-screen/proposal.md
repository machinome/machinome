## Why

`run-in-the-worker` makes the viewer execute a published program, and
leaves a person with no way to ask it for anything. A version 5 document
mounts, poses at its rest bank, and stands there: every request goes
through the handle, so the machine is drivable by a host and not by a
maker. The campaign's whole point is the Pascaline module **in a browser,
on the shop floor, for the pilot to press**.

The controls are not open design work. The pilot ratified them on
2026-09-12 and again in the 2026-09-13 decision, and the shape is
unusually specific:

- an **input** exposes a coordinate as an entry point for movement
  requests and stores no second editable copy of it;
- an **instruction** is a named movement request, and a button for one
  references it rather than repeating its definition;
- a **control** is how a person issues a request: nudge and hold-to-jog
  first, then constrained dragging;
- **there is no two-way binding** between an editable position and the
  mechanism, amount and rate editors configure future commands rather
  than coordinates, and readouts follow committed state and never feed a
  movement back into the run;
- every request reports completed, blocked, refused or cancelled **with
  the travel actually admitted**, and a blocked request accumulates no
  hidden movement;
- release, lost pointer capture and lost window focus end a manual jog;
- **no live-time scrubber**: seeking belongs to recorded history;
- the existing static and looping position controls keep their existing
  meaning and do not become running mechanical controls.

A slider is the one control this document cannot have. A slider *is* a
two-way binding: it writes a position into a coordinate. Under a run,
where a coordinate is the output of an integration with history in it,
writing a position is exactly the re-entry the running mode was built to
remove — ten `Add one` on a slider would leave the tens drum where one
did. So the running chrome is a different chrome, not the old one widened.

The dev server and the capture need one sentence each for the same
reason: `solid develop` republishes while a run is live, and
`solid snapshot --renderer web` will stop being refused for version 5
documents the moment this package declares it reads them.

## What Changes

- **A running document gets its own chrome**, decided as pure data in a
  new `runControls.ts` and rendered by `viewer.ts`, exactly the split
  `controls.ts` already has — so every decision it makes is tested in
  plain node.
- **Per declared input of the focused layer**: a follow-only readout of
  the input's actual committed position in design units with its declared
  unit; a **nudge** pair (− / +) issuing a relative move by a configurable
  amount over a configurable duration; and a **hold-to-jog** pair issuing
  a rate on press and cancelling it on release, on lost pointer capture,
  on lost window focus and when the page stops being displayed. The
  amount and rate editors configure the *request*; neither writes a
  coordinate.
- **Per declared instruction of the focused layer**: one button,
  submitting the run's own `trigger` — `targets` and `by` alike, which is
  what version 5 publishes and what the shipped viewer's instruction
  button cannot read today.
- **A transport bar**: run, pause, step one tick, speed over the existing
  ladder, an elapsed simulation time readout, and reset.
- **Outcomes are surfaced**: the last outcome of each control reads
  completed, blocked with the travel admitted, refused with the run's own
  message, or cancelled. A refused tick pauses the run and shows the
  framework's message — which names the relation as its author wrote it —
  rather than retrying it sixty times a second.
- **No slider and no timeline for a running document.** A version 1 to 4
  document keeps every pixel of the chrome it has today: the same
  sliders, the same click-to-edit readouts, the same instruction buttons,
  the same animation bar.
- **The standalone export page** carries this without a change to its
  HTML: an export of a running model opens, runs and is driven offline
  from one directory.
- **A republish keeps the run only when it is the same machine.**
  `manifestChanged()` keeps the bank, the commands and the tick when the
  new document's program identity and step size are unchanged, and starts
  a fresh run at the new rest bank otherwise, saying which it did. A
  coordinate is not preserved because a string matched.
- **The capture photographs a version 5 document at its rest pose**, with
  the clock at zero and no step taken, and refuses a non-zero `--time` on
  one by name — a running document has no animation fraction for it to
  mean anything in.
- **Constrained dragging of a part is not in this change.** It is the
  next viewer cycle, and it is named as such: the same command interface,
  a pick bound to a declared input, a blocked drag accumulating no hidden
  movement.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: three new requirements — a maker drives a running
  machine with nudge, jog and instruction controls; a maker runs, pauses,
  steps, speeds and resets the run and reads its elapsed time; a request's
  outcome is reported where it was issued — and two modified ones: the
  on-screen driver chrome is scoped to documents that are posed rather
  than run, and the host's presentation choice covers the running chrome
  too.
- `development-server`: the development page keeps a live run across a
  rebuild only when the republished program is the same machine.
- `snapshot-capture`: a document carrying a program is photographed at its
  rest pose, and an animation instant is refused on one.

Capabilities needing no delta:

- `viewer-distribution`: `run-in-the-worker` already published
  `documentVersions`; this change moves no distribution contract.
- `viewer-assembly-navigation`: the running chrome follows the focused
  layer through the navigation that already exists.

## Impact

- `solid_node_viewer/widget/src/runControls.ts` — **new**: the running
  chrome as pure data. `runControls.test.ts` beside it, in plain node.
- `solid_node_viewer/widget/src/viewer.ts` — the running panel's DOM and
  the transport bar; the choice between the posed chrome and the running
  one; the republish rule; the jog's release, capture-loss, blur and
  visibility handlers.
- `solid_node_viewer/widget/src/playback.ts` — an elapsed-seconds
  formatter beside the machine-time one.
- `solid_node_viewer/widget/src/options.ts` — `run: {nudge, jog}` defaults
  beside `run-in-the-worker`'s `{dt, record}`; `driverControls: 'none'`
  suppresses the running chrome exactly as it suppresses the posed one.
- `solid_node_viewer/capture.py`, `solid_node_viewer/cli.py` — the rest
  pose and the `--time` refusal; `tests/test_capture.py`,
  `tests/test_cli.py`.
- `solid_node_viewer/app/` — nothing. The development page mounts the same
  bundle; the republish rule lives in the widget, where the run does.
- `tests/test_running_document.py` — the Pascaline acceptance grows the
  on-screen half: press `Add one` ten times **as a maker**, and read
  65.54 off the tens drum.
- `README.md`, `CHANGELOG.md` (still 0.2.0, unreleased), and
  `docs/adrs/EXPORT/ADR-048-…`.
- **Depends on `run-in-the-worker`**, in this repository, which must be
  ratified and implemented first: this change has no run to drive without
  it.
