# Automatic visual-review packs — working plan

Status: proposal candidate, not implementation authority. The campaign record is
`film-production-campaign.md`; the proposed OpenSpec change is
`automatic-visual-review-packs`.

## Origin and narrow need

Leonardo's finished `demo-all-features` film required manual inspection of the
**encoded MP4**, not just browser PNGs: 46 seconds, 1,380 frames at 30 fps,
with 92 half-second samples across four sheets and separate exact onset,
source-emphasis, join, and end samples. The archived
`workflow/archive/film-motion-2026-09-29/report.md` names the sampled indices
and files. Earlier `text-animation` and `stills-and-clips` root reviews also
made encoded-film sheets and before/after pairs by hand. The recurring need is
to prepare the same *evidence for a human* reliably after each local render.

## Candidate contract

- A successful Videomaker render publishes the film and its manifest first,
  then attempts a review pack. A separate `review MANIFEST.json` command
  retries or generates a pack from an already published film. It does not load
  current episode YAML, speech, source, viewer, or the current timeline.
- During render, persist a schema-labelled resolved review plan with the
  manifest. Build its zero-based output-frame event pairs from the very global
  frame requests used to render/cache the film: shot joins and tails; visible
  word-count changes (spoken and even); source-emphasis set changes; film end.
  Compare state by shot and authored cue identity across an active-to-outgoing
  role transfer, while retaining incoming/outgoing as sample context; do not
  invent a new onset just because that role changed. Also record
  midpoint and last-active-frame samples for each resolved transition, so a
  join is not represented by its boundary alone. Deduplicate pairs and retain
  all event labels for a shared frame. This is
  an index plan, not a newly authored YAML declaration. A legacy manifest
  without the plan is explicitly refused for automatic event review; its
  original film remains untouched. Do not reinterpret it with a newer
  `frameAt` or pretend it has a recorded plan.
- Verify the manifest's output SHA-256 against the published MP4 before any
  decoding or pack reuse. Decode from an attested input snapshot and recheck
  manifest/output binding before index publication or successful reuse; if
  either live source changes during the attempt, refuse with no new complete
  index. Decode the **MP4** in display order, associate every
  selected zero-based index with its actual reported PTS, and reject missing,
  non-monotonic, or inconsistent frame metadata/count/dimensions. Never label
  requested `n/fps` as the encoded PTS. Sheet cells identify index and PTS;
  direct decoded-frame extraction is the reference in tests.
- Overview sampling is deterministic and bounded (at most 96 approximately
  evenly spread samples, including first/last); event sheets are paginated,
  at most 24 cells each, without truncating events. The 1,380-frame consumer
  therefore fits in a few overview pages. Distinguish blank sheet padding
  from a decoded black frame. Keep on-cell labels short and bounded; preserve
  full cue text and all shared event labels in the index. Put generated images and a final index in an
  ignored `_build/review-packs/` generation bound to manifest and MP4 hashes.
  Publish the index last, atomically; incomplete generations are not usable,
  retries preserve earlier completed packs, and no existing pack is overwritten.
- A pack failure is a **review-artifact failure after a good film**, visibly
  reported with a retry path. It never rolls back the MP4 or mutates its
  manifest into a false film failure. The index records provenance and sample
  mappings but never says the images were inspected, the aesthetics approved,
  the audio checked, or the film cleared for release.

## Boundaries and proof

The automatic plan concerns Videomaker's own encoded MP4 and its new manifest
schema, not arbitrary videos or a general archive/reproducibility audit. The
render keeps existing frame timing and film publication behavior. Start with
failing tests for stale/tampered output and mid-attempt replacement, old
manifests, fractional shot and word boundaries, distinct same-index cues in
different shots and continuity of one cue through active-to-outgoing transfer,
transition midpoint/last-active sampling, distinct and very long event labels
sharing a pair, decoder PTS versus requested times, page limits,
interrupted/failed pack publication, and the
film-good/pack-failed separation. Then test a real Leonardo render: every
pack image must match the independently decoded MP4 frame at its recorded
index, including joins, word/emphasis edges and last frame. Root performs
actual visual review; pack generation cannot approve itself.
