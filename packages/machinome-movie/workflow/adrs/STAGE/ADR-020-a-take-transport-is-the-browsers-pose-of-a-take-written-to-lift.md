# ADR-020: A take transport is the browser's pose of a take, written to lift

Status: Proposed (OpenSpec change `take-transport`, 4 October 2026, the
first change of the player campaign). It stays Proposed until the change is
archived: the pilot ordered the campaign to stop before sync. Builds on
[ADR-012](ADR-012-a-view-on-a-take-is-posed-by-restoring-the-machines-bank.md)
(a view on a take is posed by restoring the machine's bank) and
[ADR-013](../PIPELINE/ADR-013-the-stage-bundle-names-its-files-by-the-tool-and-the-project.md)
(the stage bundle names its files by the tool and the project).

## Context

The player campaign (`workflow/ongoing/player-campaign/plan.md`) answers a
recorded cost: every timing revision of a film meant a preview run, the
Curta's *Addition* renders in an hour, and its take was written blind,
because nothing showed a take before a movie rendered. Two rulings of the
pilot of 4 October 2026 shape it: the player lives in Videomaker before the
studio takes it, and watching a scenario is a feature by itself, of which a
video is a recording. So a take must be posed at a time in a person's
browser in two places: on the viewer alone (the player's take surface) and
through the stage (the movie surface, which draws the frame the renderer
would capture).

The pose was a few lines of `stage/runtime.tsx` (`poseView`, `viewMachine`):
the viewer's machine restored to the frame's bank with the take's identity,
then the camera, and a viewer with no machine or another refused by name.
Only the stage could call them. The natural home of posing a take at a time
is the view layer, the viewer's widget, which already applies the same rule
when it draws a solved request; but the pilot wants the viewer to stay thin
and has arranged the move into the monorepo (one repository, one licence)
for later.

## Decision

1. **A take transport, `transport/`, is the pose of a take in a browser.**
   `attachMachine(viewer, identity)` gives a machine transport whose
   `pose(bank, camera?)` restores the whole bank with the take's identity and
   makes one `setView` (the camera given, with up and field of view from
   Viewer API 28, or the viewer's own view read back); it refuses a viewer
   with no machine or another machine before touching it, in the stage's
   words. `attachTake(viewer, takeDocument)` seeks a clocked take, the
   document being what the pose rule reads (`{model:
   {expectedDurationSeconds}, marks, take}`), by `bankAt` of `src/take.mjs`,
   imported and never copied, so the browser and the frame pose one rule;
   `attachLoop(viewer)` is the trivial take of a posed loop. A timer clock
   and an audio clock drive them. Every call is synchronous.
2. **The stage poses a take through it.** A view on a take is attached once
   per mounted viewer instance and posed per frame through the transport;
   `window.film.transport(key)` reports it. What a frame carries and how the
   renderer holds the viewer to the take (ADR-012) are unchanged.
3. **It is written to lift.** It knows the viewer's public handle, declared
   in it as types (`viewer-handle.ts`), and the pose rule, and nothing of the
   stage, the movie, React or any package; a repository test refuses any
   other import, so moving it with its tests is a move. Where it goes, the
   viewer package or a view component over the widget, is the pilot's
   arrangement at the migration.
4. **The bundle names it by the tool.** ADR-013's names extend to
   `videomaker/transport/<file>` and `videomaker/src/<file>`, and the
   bundle's key reads the transport's sources beside the runtime's.

## Options considered

- **Keep the pose in the stage** and give the player the stage. The take
  surface would load a set, a slot and React to show a machine, and could
  not be moved to the view layer without the stage.
- **Put it in the viewer now.** The pilot wants the viewer thin until the
  migration; a second repository's change for a piece whose shape is not
  yet proved by its first user.
- **Copy the pose rule into the browser.** Two implementations of one rule,
  whose agreement only a test of both could hold; importing the pure module
  needs none.
- **A transport that draws its own UI or depends on React.** The player is
  plain DOM by the contract, and a view component, if the pilot chooses one
  at the migration, would wrap the transport rather than be it.

## Consequences

- The stage runtime changes, so every film's stage bundle changes and its
  shots recapture once.
- The player's take surface attaches to a take document the server serves;
  the movie surface reads the transport through `window.film.transport`.
- The transport's boundary is a repository test, and its declaration of the
  pose rule (`src/take.d.mts`) is held to the module's exports.
- A pose without a camera always ends with a redraw (`setView` of the
  viewer's own view), though on the API 29 bundle `restore` already draws
  before it returns: a picture drawn by the pose alone keeps the last
  framing's clipping planes, and one drawn after `setView` depends only on
  the bank and the view. The stage always passes a camera and draws as
  before.
