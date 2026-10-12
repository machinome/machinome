# Player campaign — report

Closed 4 October 2026, the day it opened. `plan.md` is the architecture the
campaign was cut from, with the contract its cycles built against;
`PROGRESS.md` is the execution index naming every commit, run and finding;
the three archived changes carry their own `evidence.md`:
`openspec/changes/archive/2026-10-04-take-transport/`,
`2026-10-04-live-server/` and `2026-10-04-player-page/`. The findings are in
`workflow/warts.md` under "The player (4 October 2026)".

## What was built

`videomaker live SOURCE` serves a film to a browser while it is edited: the
player at `/`, with a movie surface (the render's own stage page in an
iframe, the renderer's frames from `/frame`, the narration as the clock,
composed joins shown as a cut and said so, a reframe drawn live) and a take
surface (the viewer alone, the take transport seeking a clocked take by the
pose rule the frame uses, free camera), one ruler with scrubbing, keys and
readouts, a reload on every accepted generation and a refusal shown and
kept. Beneath it, the take transport (`transport/`, ADR-020), written to
lift into the viewer package at the migration and pinned to import nothing
but the viewer's handle types and the pose rule; the live session
(`src/live.mjs`, ADR-021) loading as `check` does through `checkSource`,
serving the renderer's files through `film-assets.mjs`, watching each
input's directory without recursion; and the player (`player/`, ADR-022)
with `python -m machinome_movie watch` re-evaluating a project's movie.

## The decisions

- Two transports, nested: a take transport (time to machine pose, marks as
  stops) and a movie transport (video time to frame to each view's take
  time; the narration its clock). A video is a recording of the movie
  transport's output; nothing in the player draws.
- The viewer stays thin (the pilot, 4 October): the take transport lives
  in Videomaker now and is arranged into the monorepo at the migration.
- The pilot's instruction to stop before sync: every change was proposed,
  ratified, applied red-first, tested and committed, and synced and
  archived only after the pilot validated the player in the browser on the
  Curta film *Addition*.

## Evidence

The merged head 5aeb4be, cold with the API 29 viewer bundle: Node 52
files, 501 passed; Python 298 passed. The live session on *Addition* from
that head answered every route. What the episode still owes: the pace of
the Curta on a machine with a GPU and the time from an edit to the frame on
screen, measured by the pilot.

## Process findings

The orchestrator's union of a conflict hunk that split a test function
left `test/repository.test.mjs` unparsed on the campaign branch for one
cycle (fixed in 2c46e84); a cycle's agent ran one `pkill -f` with a
pattern. Both are in `warts.md`.
