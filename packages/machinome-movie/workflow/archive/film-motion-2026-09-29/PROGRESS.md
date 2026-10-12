# Film motion — execution index

Completed locally on 29 September 2026, branch `film-motion`. Runtime content
is frozen at `8212566`; the campaign archive commit adds evidence only.
The consuming project is Leonardo. Its episodes, media and generated films
stay in that repository, intentionally untracked/ignored for this local demo.

## Cycle records

All paths below are under `openspec/changes/archive/` at repository root.
Planning was begun by Claude; GPT-6 Sol proposal/apply agents resumed it,
with Codex's adversarial review, real-film validation, sync and archival.

| Cycle | Planning commit | Implementation/archive commit | Archive directory |
| --- | --- | --- | --- |
| Keyframes and easing | `37b2e56` | `bc13655` | `2026-09-29-keyframes-and-easing` |
| Shot transitions | `263a3e8` | `2885a45` | `2026-09-29-shot-transitions` |
| Graphic overlays | `4edad8e` | `cef6a61` | `2026-09-29-graphic-overlays` |
| Text animation | `6c22af1` | `9aea9f2` | `2026-09-29-text-animation` |
| Stills and clips | `6c22af1` | `8212566` | `2026-09-29-stills-and-clips` |

The initial campaign plan is `835cf35`; first demo/status records are
`7e4e810` and `6417f97`. Recovery reconciled the delegated workflow and
validation gates in `40d7bda`, added the export-pinned format-0.2 compatibility
consumer in `ff85c4b`, and recorded capability purposes and the combined
demonstration plan in `b11287c`. Those are planning/evidence commits, not
additional product cycles.

Prior API-28 work consumed by the final film: `cad2d4d` (annotations),
`e303629` (highlights), `9802bda` (camera up/field of view). The viewer source
bundle comes from its separate `film-annotations` worktree at `f040f45`.
No new viewer change was made in this campaign.

## Gates and delivery

- Final serial implementation suite: 116 passed, 0 failed.
- Fresh compatibility: 3 format-0.2 and 32 format-0.3 PNGs byte-identical to
  detached `6417f97` under the same viewer/browser/export.
- Strict OpenSpec validation: nine passed (seven baseline capabilities and
  two unrelated pre-existing active changes), none failed.
- Five feature films retained; earlier easing/transitions films re-inspected,
  three remaining films produced and inspected during recovery.
- Combined preview: 402 poses, 147 samples, exact replay and nonvacuous
  feature checks. Finished full-HD film: 46 seconds, narrated, 1,380 frames;
  decoded-frame vision passed. See `report.md` for sampling and limits.
- All five baseline deltas synced and changes archived. Historical pilot-only
  review/adoption/publication checkboxes are not impersonated; test-order
  exceptions are explicitly recorded in the resumed review records.

`plan.md` preserves the evolving commission. `report.md` is the delivery and
reproduction guide. `evidence.json` records actual output/input hashes,
streams, narration, selected preview proofs and decoded review sheets.
The complete project-owned manifests remain beside the videos.

No main-branch integration, push or publication was performed. The temporary
legacy checkout alone was removed; the production worktrees and caches remain.
