## Why

Leonardo's `demo-all-features` required manual contact sheets and exact
before/after frames decoded from its finished 46-second MP4 to inspect joins,
word and source-emphasis onsets, and the end. Earlier `text-animation` and
`stills-and-clips` rehearsals needed the same hand-made evidence. Videomaker
should prepare bounded, trustworthy visual-review material with each local
film without presenting that material as an aesthetic or release decision.

## What Changes

- Record a resolved, versioned review-sample plan from the actual global
  output-frame requests during render, including stable cue identity across
  incoming/outgoing role changes and transition interior samples, alongside the published film
  manifest.
- After successful film publication, automatically attempt a paginated pack
  of overview and event-pair images decoded from the encoded MP4. Provide one
  standalone command to generate/retry a pack from a compatible manifest
  without reopening the episode or recalculating events under newer code.
- Bind the pack to a stable manifest/MP4 input across decoding and reuse,
  label exact zero-based decoded display-frame indices and actual PTS, and
  publish an immutable pack index atomically. Preserve prior packs and report
  pack failure separately from successful film publication.
- Explicitly refuse automatic event review for legacy manifests without a
  recorded plan. No author-facing episode field, new visual style, automatic
  approval, audio judgement, or publishing behavior is introduced.

## Capabilities

### New Capabilities

- `visual-review-packs`: Resolved sample-plan provenance and bounded,
  encoded-film visual review artifacts with safe publication and retry.

### Modified Capabilities

None. Existing rendering and shot-cache requirements are retained.

## Impact

The renderer records a plan with its output manifest and attempts pack
generation only after the film is published. A small decoder/sheet/index
module and one `review MANIFEST.json` CLI route consume that manifest and its
MP4; the project-owned ignored `_build/review-packs/` holds artifacts. Tests
cover exact decoded-frame provenance and the Leonardo consumer. No viewer,
framework, project source, speech service, or release workflow changes.

## Planning review

Root accepted the bounded design on 29 September 2026 under the commissioned
campaign, after adding transition-interior samples, active-to-outgoing cue
continuity, stable attested inputs with live-hash checks, and bounded printed
labels retaining full index descriptions. A post-publication pack failure
keeps film-success exit status and prints a distinct retry warning; standalone
review fails nonzero. Legacy manifests explicitly refuse event review rather
than being reinterpreted. Implementation follows source-only closure; no
browser overlap, new episode field or approval claim is authorized here.
