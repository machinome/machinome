## Why

The episode is *Addition*, the Curta film (the Curta Type I 3x project,
`videos/addition/`, five chapters filming the clocked model through its
export). Its finding is wart 31 of the section "Addition (Curta, 1 October
2026)" of `workflow/warts.md`: `speech` generates the missing takes, which
are paid, before it loads the film, so an unrecorded or mismatched export
is refused only after paying. `bin/videomaker.mjs` calls
`generateMovieTakes` for a `.json` source before `loadEpisode`, and
`generateMovieTakes` checks only the document itself (format, schema and
the static rules without the export) before it asks the provider for every
chapter whose take is not cached; everything the load refuses against the
project (the export's manifest and its recorded revision, the take's
identity against the export, the parts and tokens the document names, the
stage modules, the running-program and loop refusals, the evidence files,
the pinned source excerpts, the pictures) is refused afterwards.

The film is stale against its project today: since the project's machinome
0.8 commits, `check` on `videos/addition/_build/movie.json` refuses with
`Source differs from pinned model revision: simulation/event_driven.py`
(campaign plan `workflow/ongoing/catch-up-0-8/plan.md`, item 2). Once its
narration is revised, `speech` on that document as it stands would buy one
take per changed chapter, up to five, and then print the same refusal.

## What the film does with the result

Its author runs `speech` on the film's document against the export as it
is, and a stale or mismatched export, a revision that differs, a take
recorded on another machine or excerpts that no longer match the pinned
revision are refused by the same words `check` prints, before any take is
requested. Only a film whose document and project pass the load pays for
narration.

## What Changes

- **`speech` refuses what the load refuses without a take, before it
  generates one.** On a movie document, `speech` (and `build` without
  `--silent`, which runs the same step) first makes every check of the
  load that needs no take, in the load's own order and with its own words:
  the document, the export's manifest and recorded source, the pinned
  revision, the document's names against the export and the excerpts
  (parts, tokens, a take's identity, inputs and bank), the project
  repository and the stage modules, the export's kind and length against
  the document, the output and the cameras, the evidence files, the pinned
  source excerpts and the pictures. Only then does it generate the missing
  takes, load the film as before and fit, caption, time and mix.
- **Nothing else moves.** The refusals and their words are unchanged;
  `check`, `preview`, `render` and `live` load as before, in the same
  order; a YAML episode is already loaded whole before its takes are
  generated and is unchanged. The refusals made on the resolved film (the
  resolution of anchors against the takes, the checks of resolved times,
  the film's frame count, a take that overflows its chapter) still come
  after generation, since the times they judge come from the takes.
- **Proof** (layer 7 in process, then layer 8 once from the command line):
  the existing provider double of the pipeline tests, which answers with
  the fixture takes and counts requests, sees no request when the speech
  step runs on fixture movies whose export's recorded revision differs,
  whose export is missing, whose excerpt differs from the pinned revision,
  whose export publishes a running program, or whose take was recorded on
  another machine; each is refused with the load's words. Before the
  change it counts one request per chapter before the same refusal. From
  the command line, `speech` and `build` on the changed revision print the
  load's refusal and attempt no purchase.
- **Records**: `docs/movie-document.md` ("Resolution", item 2),
  `CHANGELOG.md`, `workflow/warts.md` (Addition 31). No ADR (design,
  "No ADR").

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `movie-document`: `speech` generates a document's takes only after every
  refusal of the load that needs no take has passed.

## Impact

Code: `src/movie.mjs` (the load's take-free part opened once for both the
load and the speech command's first step; `checkProject` holds the frame
count to a resolved film), `bin/videomaker.mjs` (its comment). Tests:
`test/pipeline/movie-pipeline.test.mjs`. No schema, fixture, stage,
renderer, Python or viewer change; no shot cache key changes, since
`src/movie.mjs` is not hashed into one. `speech` on a valid document makes
the take-free checks twice (before generation and in the load), reading
the excerpts at their revision and probing the pictures once more.

## Non-goals

`check`'s own refusals before its load (the stage bundle and its type
check, the measured layout), which `speech` never made and does not make
now; the refusals on the resolved film, including those that in a given
document judge only literal times; the YAML episode path; a paid request,
which no test makes; the Curta's export and document, which are project
work at the campaign's wave 2.
