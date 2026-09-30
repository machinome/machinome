# Warts — Videomaker findings, in the order they were met

Working record. Nothing here is ratified; an entry is evidence, not a
requirement, and becomes work only through an OpenSpec change in this
repository (or the viewer's, for viewer findings). Entries are grouped by the
episode that produced them and record the pilot's triage in place.

No entry yet. The frictions met by the sawmill rehearsal and the release-film
source study before this file existed are recorded in `docs/first-rehearsal.md`
and in the archived OpenSpec changes.

## Cut and Advance (Leonardo, 30 September 2026): the first film declared in Python

Findings met while producing the declarative-python campaign's validation
film from `videos/cut_and_advance/movie.py`. Triage: none yet; the pilot
decides each.

1. **A hold that ends exactly at a snapped shot end is refused.** The split
   shot ended at `spoken_end(phrase, plus=0.9)` and its emphasis cleared at
   the phrase end plus 0.9 s; the shot end snapped to the frame grid landed
   up to half a frame earlier, so `Emphasis clears after shot coupling ends`.
   The film shortened the hold. A resolver could snap a cue's end to the same
   frame as the shot's when they are written on the same anchor, as it
   already does for a model keyframe's last `at`.
2. **`lines.end()` has no anchor of its own.** The Python side emits it as the
   spoken end of the shortest unique run of the narration's last words
   (`moment`, `stroke`, `progress`, `blade`, `description`). It works and is
   fragile in principle; a `narrationEnd` anchor form would say what is meant.
3. **Source emphasis lights only the excerpt's last line.** Enough for the
   film's three-line excerpt; a film that lights a word on another line has no
   spelling for it (`emphasize` takes no `line=`).
4. **A film is a whole number of frames on its own grid only.** `render --fps
   10` of a 30 fps movie may be refused; the quick silent look at a lower rate
   does not always work for a movie. Render movies at their own rate.
5. **Two fixture projects.** The Node side made a Node-generated fixture
   project and the Python side a seesaw project, so the shared fixtures rest
   on two models. One fixture project both sides read would be simpler.
6. **The speech key is read from the worktree's `.env`**, so a command run from
   a worktree finds no key until the primary checkout's file is sourced or
   linked. A path option or an environment-only lookup would avoid the trap.
7. **The narrator sets the film's length.** With every cut on a phrase and
   the chapter tails as the only slack, a 100-second shot list resolved to
   59 s once Jessica's takes were measured. That is the point of anchors, and
   an author needs to know it before estimating durations.

## The test suite (one-runner cycle, 30 September 2026)

Findings met while moving the Node suite to vitest and memoizing it
(`openspec/changes/archive/2026-09-30-one-runner/evidence.md`). Not an
episode's; recorded here because the suite is the tool's proof. Triage: none
yet; the pilot decides.

1. **A second intermittent pixel test.** The base run under `node --test`
   failed `a movie document is refused before its takes, then checks, speaks,
   previews and renders from them` (`test/movie-pipeline.test.mjs`) with
   `Partial picture replay is not deterministic: wheel #0 at 1.00 s` from
   preview's picture proof; the same file alone passed right after, and the
   three whole-suite vitest runs of the cycle that executed it passed it.
   With the already known `every incremental PNG equals a separately cold
   film across the first reused-shot gap` (seen in the movie-document
   cycle's base run, not in this cycle's runs), the suite has two pixel
   proofs that fail rarely under load. The memo makes this sharper: a flaky
   test that passed once is not run again until its inputs change, so only
   the cold run before integration shows it.
   Worth finding the cause rather than retrying.
