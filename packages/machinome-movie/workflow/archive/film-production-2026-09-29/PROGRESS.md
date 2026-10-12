# Film production — execution index

Completed locally on 29 September 2026. Product changes, investigations and
record cleanup are separate below. Leonardo's episode sources, generated
media and ignored raw evidence remain in its own repository.

## Product cycles

All archive directories below are under `openspec/changes/archive/` in
Videomaker. The commits are on the local `film-production` branch.

| Cycle | Planning commit | Implementation commit | Archive directory |
| --- | --- | --- | --- |
| Shot-level incremental rendering | `3ae9e03` | `24234d6` | `2026-09-29-shot-level-incremental-rendering` |
| Source-only shots | `73e97c0` | `2cc54e5` | `2026-09-29-source-only-shots` |
| Automatic visual-review packs | `e1dac36`, refined `d0087c4` | `7acd2c4` | `2026-09-29-automatic-visual-review-packs` |

The incremental cycle depended on a viewer-owned deterministic asset-load
order correction: viewer planning commit `63a9465`, verified archive/content
commit `94cfcc0`, on the separate `film-production-order` branch. Its tested
Viewer API 28 bundle SHA-256 is
`5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413`.
This viewer correction is not integrated to viewer main.

## No-change investigations and record cleanup

- Bounded parallel rendering: planned at `2bf5775`, final no-change decision
  at `edb6904`; no paired comparison or product option.
- Compositing: plan `b3d83d4`, measured profile `9eea574`, no-change
  decision `c845b87`; one exact-pixel 450-frame pair, no optimization.
- Scoped test discovery and historical cleanup: plan `e952b32`, test script
  and verification `9dbdded`, two historical baseline/archive records
  committed at `f84b139`. Their archive directories are
  `2026-09-29-first-narrated-rehearsal` and
  `2026-09-29-narrated-source-scenes`. The original historical requirements
  are preserved; the educational main baseline has exactly three reviewed
  current-only replacements.
- Workspace guidance correction: `ba0a39c` on the separate workspace
  `videomaker-film-guidance` branch. It is not a Videomaker repository commit.

The source-only scoped suite passed 158/158. The review-pack full scoped suite
passed 188/188 before the later alias-path correction; final focused pack
tests passed 31/31. Root reran 12/12 pure planner tests at the committed
product. Twelve current baseline specs passed strict validation, with no
active changes. `report.md` gives the bounded real-film results and limits;
`evidence.json` locates raw reports. No main merge, push or publication is
included in these commits.
