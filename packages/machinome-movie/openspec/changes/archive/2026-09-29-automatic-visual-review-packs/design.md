## Context

Leonardo's archived `demo-all-features` review sampled the **finished**
46-second, 1,380-frame MP4: 92 half-second frames in four sheets, then exact
spoken-word, source-emphasis, join, and end frames. The archived text and
picture cycles made similar sheets manually. Those reviews did not inspect
only the browser's pre-encode PNGs. Current render publication verifies frame
count and dimensions, writes `outputSha256` into a manifest, then replaces the
MP4 and manifest. Render also enumerates every `frameAt(e,n/fps,captions)`
request on the global output grid for its shot cache. The manifest keeps the
resolved episode and word timing, but **not** a versioned event/sample plan;
future code could reinterpret those fields differently.

## Goals / Non-Goals

**Goals:** Produce bounded, indexed visual evidence from the published MP4;
preserve exact event mapping without later timeline reinterpretation; make a
failed pack distinguishable from a failed film; keep old packs and complete
indexes trustworthy.

**Non-Goals:** Watch or approve a film automatically, assess audio or rights,
replace human review, process arbitrary external movies, audit all legacy
render provenance, add episode syntax, or change encoding and shot cache
semantics.

## Decisions

### D1. Record the resolved sample plan at render time

The render's existing global frame-request enumeration is the authority for
event indices, including fractional shot/cue starts and outgoing transitions.
During that enumeration, record a `review-samples-v1` plan containing output
frame count/rate and ordered, labelled zero-based pairs. An event is the
adjacent **output** frames immediately before and at a resolved change: first
frame assigned to the incoming shot (join); an active word reveal count
increase, whether even or measured spoken; a source-emphasis set change,
including clearing; and the final two frames of each shot and film. If
several events resolve to the same pair, retain all labels on one pair.
Frame zero has no invented predecessor; a one-frame film/shot gets a
single-frame end sample. Preserve the relevant shot/cue/word label and
resolved state in the plan, but no extra YAML declaration. Compare cue state
using its **shot ID and authored cue identity**, not its array position alone;
the same cue retains identity when its shot moves from active to outgoing at a
join, so the role transfer alone creates no word/emphasis onset. Record the
incoming/outgoing **side as context** on each sample and distinguish different
shots whose cues both have list index zero. Capture the actual request context;
do not infer joins only from nominal `shot.start*fps` or discard outgoing
transition state. For each resolved transition run, additionally record its
actual midpoint output request (nearest available frame to the run midpoint)
and last active output request. These are individually labelled samples, not
invented before/after edges; an empty or one-frame run cannot create a
nonexistent midpoint or last frame. This makes a join inspectable inside the
transition as well as at its boundary.

Keep authored identities in a **render-only sidecar**, keyed to each already
enumerated global request, not in `frameAt`'s JSON or the shot-cache
fingerprint. The active overlay selection used by `shotFrame` can share a
small internal helper that yields `{authoredIndex, cue}`; pair those indices
with the resolved request's `overlays` in order and verify the observed
`shown` values. Do not key by cue text or the current filtered-array position:
two simultaneous, identical even-reveal descriptions are valid distinct
authored cues. For source emphasis, the resolved `wordTiming[shotId].emphasis`
entries already retain their authored `index`; pair their active word ordinals
with `codeAt`'s flattened `{word,line,start,end}` descriptors and refuse a
sidecar/request mismatch. This preserves old request shape and pixels while
giving review events stable `(shotId, authoredCueIndex[, wordOrdinal])`
identity across active-to-outgoing transfer.

Event candidates follow the renderer's **picture-side** selection. A
fade-through-colour join captures only `transition.picture` (`outgoing` in
its first half, `incoming` in its second); a cue state change on the other,
uncaptured side is not labelled as a visible onset. At the side switch a
newly selected cue may carry its then-resolved count/emphasis set as a
picture-entry state, not a newly timed word onset. Dissolve, wipe and slide
capture both sides, so both can contribute resolved event candidates.
Even there, a wipe edge, picture opacity or full colour plate can conceal
the cue in encoded pixels. Pack labels therefore state **resolved request /
candidate picture state**, not a guarantee of perceptual visibility; the
decoded frame is supplied for human judgement. No browser geometry detector
or additional author field is implied.

Put the plan in the render manifest that binds the published MP4. The plan
must be produced on cache hits as well as fresh captures. A later standalone
review consumes only this stored plan and the MP4, never the current episode,
source, speech, viewer, or `frameAt`. Re-evaluating an old episode was rejected
because newer timeline code could silently move an onset. An old manifest
without `review-samples-v1`, or with an invalid/incompatible plan, is refused
with a rerender instruction; its MP4 is not changed.

### D2. Decode and attest the published film

`review MANIFEST.json` is the only new command. Render invokes the same pack
generator automatically **after** the film and manifest are published. First
hash the manifest and verify its declared `outputSha256` against the actual
published MP4; no pack generation or old-pack reuse on mismatch. Copy both
inputs into an isolated attempt snapshot, hash those bytes against the
initially verified inputs, and decode only that MP4 snapshot. Re-hash the
live manifest and output before publishing an index or reporting a verified
old-pack reuse. If either differs from its initial/snapshot hash, refuse the
attempt without publishing a complete index. The later pack remains bound to
the snapshot's verified hashes; every future reuse checks the then-current
live inputs again. This is narrow protection of pack provenance during its
own attempt, not a universal render/archive corruption audit. Validate the
recorded plan's count, contiguous index range, and event references against
the film's decoded display-order frame count/dimensions. Extract only selected
frames while decoding/checking the whole MP4. Record each selected frame's
zero-based decoded/display index and decoder-reported presentation timestamp
as integer ticks plus its rational time base. Label sheets with index and
actual PTS; `n/fps` is an output-request time, not a substitute for encoded
PTS. Reject missing/nonmonotonic PTS and metadata disagreement rather than
guessing. The pack image pixels come solely from the decoded MP4, not the
shot-cache PNGs, thumbnail, preview, or an episode re-render.

### D3. Bound and group the evidence

The overview uses global indices at approximately half-second spacing with
`stride=max(1,round(fps/2),ceil((count-1)/95))`, then includes the last frame.
It contains at most 96 unique indices, including first and last, and is
paginated at 24 cells per sheet. Event pairs are deduplicated by frame-index
pair and shown adjacent, at most 12 pairs/24 cells per sheet; one shared pair
carries all event labels. Transition midpoint/last-active samples are placed
on bounded event pages as labelled single cells, without evicting pairs or
splitting them across pages. A single-frame end sample uses one cell. Each
cell's visible text is fixed-format and length-bounded (event kind, index,
PTS and a short identifier); the complete, potentially long cue text and
all co-occurring labels live in the index. Decode a
frame once even if it appears in overview and several event contexts. Padding
cells are clearly marked as padding, never presented as decoded black frames.
No event is silently dropped to meet a page limit. For Leonardo's 1,380
frames at 30 fps, the overview is 93 frames across four sheets (the historical
92 half-second indices plus frame 1379); event sheets are paginated separately.

### D4. Publish immutable generations and separate failure status

Generate in a new ignored `_build/review-packs/` generation, bound by the
manifest SHA-256 and MP4 SHA-256. Its schema-labelled `index.json` records
source paths/hashes, frame count/dimensions/rate, decoder identity, selected
index-to-PTS mappings, event labels, page entries and artifact hashes, and an
explicit `generated, not reviewed` status. Write and verify images first;
atomically publish the complete index **last**. No index means an incomplete
generation, not a pack. Do not overwrite or delete earlier complete
generations. A retry may reuse a complete, hash-verified generation for that
same manifest/MP4 or publish a new one; a corrupt/incomplete generation never
passes as success.

The film transaction ends before pack generation. If the automatic attempt
fails, preserve the good MP4 and manifest, print a distinct `review pack
failed; film published` warning with a standalone retry command, and keep
render's film-success exit status. The standalone `review` command itself
fails nonzero on pack failure. Do not rewrite a good film manifest to express
a later pack failure or claim a pack was human-reviewed. This deliberately
separates machine evidence preparation from root/pilot visual judgement.

## Risks / Trade-offs

- **More decode time after each render** → Stream the whole film once for
  count/PTS validation while retaining only selected frames; bounded sheets
  cap image layout size, and film publication is already complete.
- **A rendering-code change could reinterpret old events** → Standalone
  review uses the stored versioned plan only; old manifests without it refuse.
- **A decoder or interrupted write could leave plausible stale sheets** →
  verify and snapshot both inputs, recheck the live hashes before completion,
  store exact PTS/artifact hashes, publish the index last, and reject
  incomplete generations.
- **Long narration or many events could overrun a cell** → Keep printed labels
  fixed and bounded while preserving complete descriptions in the index;
  paginate all samples instead of truncating evidence.
- **Contact sheets may miss an aesthetic flaw between samples** → Index
  states the sampling scope and no approval; a person retains responsibility
  to inspect more film when needed.

## Migration Plan

New renders include a review plan and automatically attempt a pack. Existing
MP4s/manifests remain usable as films, but `review` refuses automatic event
packs for manifests without the plan and asks for a new render. No episode
format migration, cache purge, deletion of old review images, or publication
step is implied.

## Open Questions

None before root's adversarial review. The generated-pack exit/status policy
and the 96/24-cell bounds above are explicit proposals to ratify, not claims
about current behavior.
