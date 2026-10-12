# Catch-up campaign — report

Status: campaign record, written 6 October 2026 at the close. Historical
once archived; a later fix does not rewrite what is recorded here.

## What was asked

The pilot, from the orchestrator's sorted list of Videomaker's warts:
"Go with 1, 2, 3, 4 and 8, keep the discipline." Later the same day:
"don't spread Apache2 license around, that license is gone. just name the
new license instead, I want the old license as forgotten as possible."

## What was done

| item | kind | result |
|---|---|---|
| 1. the fixture project under machinome 0.8 | narrow adjustment `fixture-under-0-8` | both models on the 0.8 module spelling, one blank line each removed so the excerpts' lines read as before; re-pinned (manifests differ in `source.revision` and `mtime` only, no STL byte moved) |
| 4. `test_cli.py` from a worktree | narrow adjustment `test-cli-in-the-worktree` | the children run the checkout's package; three-state mutation proof |
| (found) stale viewer status claims | narrow adjustment `status-claims` | README, AGENTS and FORMAT say machinome-viewer 0.8.0 declares API 28 and 29; red-first pin |
| (ruled) the former licence named | narrow adjustment `licence-named-as-it-is` | every mention replaced in place by GPL-2.0-or-later OR CERN-OHL-S-2.0-or-later; fixture re-pinned; a grep finds only third-party entries |
| 3. `speech` pays before loading | OpenSpec change `speech-loads-first` | every take-free check of the load runs before any take is requested; `movie-document` requirement modified; no ADR |
| 2. the Curta film | project work, no Videomaker change | export remade at project head 1f3dc22, evaluated, `check` and `preview` green on the API 29 bundle; no render (deferred by the pilot), no speech, no Curta commit |
| 8. the viewer's log | record | the mount-restyles-its-host finding filed on viewer `main` 24d9ad2; the "no release call" finding corrected: the viewer's handle declares `dispose()`, Videomaker's own type omits it |

## Evidence

Each cycle's report or archived change holds its red, green and suite
outputs: `fixture-under-0-8.md` (items 1, 4, status claims),
`openspec/changes/archive/2026-10-06-speech-loads-first/evidence.md`, and
the Curta film's `_build/preview/report.json` in the project. The
integrated head's cold suites are recorded in `PROGRESS.md`.

## Findings kept

`workflow/warts.md`, section "Catch-up (6 October 2026)": entries 1 to 9.
For the pilot: the Curta project's untracked files make every export dirty;
`set-23` and `set-145` still cross their marks under their dissolves
(Addition 23).

## Not done

No render of the Curta film; no push; no release.
