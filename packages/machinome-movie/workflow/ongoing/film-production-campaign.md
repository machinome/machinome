# Film production campaign

Status: commissioned 29 September 2026; scope and execution record, not a
ratified episode-format specification. Starts at Videomaker `e12fcfc` on
branch/worktree `film-production`, using viewer main `f040f45` / API 28.

## Commission

The pilot approved shot-level incremental rendering next, then selected
bounded parallel rendering, faster compositing, the evidenced source/model
layouts, automatic visual-review packs, and documentation/workflow cleanup.
Audio diagnostics, stronger general regression coverage and a reproducibility
audit are explicitly deferred. Live preview belongs to future Studio work
requiring the pilot's attention and is outside this campaign.

The pilot requested the same delegated discipline: GPT-6 Sol proposes,
another Sol applies, Sol produces empirical evidence, and Codex performs
adversarial review and independently verifies results before spec sync and
archive. Root controls planning/implementation commits and closure. Ordinary
within-scope planning refinements are reviewed by root; a consequential
expansion or changed purpose returns to the pilot. Tests prove each new
promise red before implementation. No retrospective red-first claims.

## Order and evidence gates

1. **Shot-level incremental rendering.** Leonardo `demo-all-features` is a
   nine-shot, 46-second film. Its local camera/title/timing corrections caused
   whole-episode frame identities to change. Demonstrate selective reuse on
   a real-model consumer and exact equivalence with a fresh render, including
   incoming/outgoing transitions and global-frame timing. Preserve the
   validated original film and caches.
2. **Bounded parallel rendering investigation.** Benchmark the same
   consumer only after incremental rendering. Previous virtiofs descriptor
   exhaustion is a constraint, not evidence of a speedup. Implement a
   bounded option only if measured benefit and resource behavior justify it;
   otherwise archive the investigation as no change. A controlled parallel
   experiment requires root's explicit browser/resource lease.
3. **Compositing performance.** The `demo-graphic-overlays` record measures
   103.08 seconds between first/last capture for 450 frames. Root enumerated
   the consumer's actual 30 fps timeline: 105 frames have one partial fade,
   25 have two, and 320 have none. Profile current costs and retain exact old
   pixels; correctness proofs are not weakened for speed.
4. **Supported source/model layouts.** Leonardo's dark-source experiments
   left the public format to alternate full-screen source and the model.
   Serve those evidenced layouts, not a general layout engine. Use pinned
   real source and real model pixels; no invented mechanical behavior.
5. **Automatic visual-review packs.** The prior campaign manually decoded
   whole-film contact sheets and exact word/join/end frame pairs. Automate
   those concrete artifacts from the encoded MP4, preserving provenance and
   honest limits; a pack is evidence for review, not automatic aesthetic
   approval.
6. **Documentation/workflow cleanup.** Reconcile known stale guidance,
   correct default test discovery traversing nested worktrees, and close the
   two fully implemented historical changes without rewriting their adoption
   history. Workspace skill edits belong in a separate workspace worktree
   and commit, never in this repository. No new feature sweep is included.

Each product cycle gets a proposal/design/delta/tasks planning commit, then
red-first implementation, real consuming-film evidence, root verification,
baseline sync, archive and an implementation commit. A finding without a
justified product change stays a workflow investigation; it does not receive
invented interface requirements merely to fill the campaign.

## Boundaries and coordination

- Tool code, tests, specs and development evidence belong to Videomaker.
  Episode sources/media and generated films belong to Leonardo. Do not stage
  a consuming project's files here or modify mechanical source/export.
- The initial viewer was main's API-28 bundle, SHA-256
  `a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`.
  After the evidenced prerequisite, use
  `/home/asa/devel/machinome/machinome-viewer/WTs/film-production-order/machinome_viewer/widget/dist/machinome-viewer.js`,
  SHA-256 `5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413`,
  built from viewer branch commit `94cfcc0`. API 28 is source capability,
  not a published-release claim; the correction is not integrated to main.
- One browser/render/testing owner at a time, except a deliberately leased
  parallel-render benchmark. Unit/read-only work can run alongside it.
- Reuse cached narration or silent evidence. No paid generation is presently
  needed or authorized by this production plan. Never expose `.env` or keys.
- Never consult other video/animation frameworks' implementation/API/docs.
  Preserve deterministic frames, format compatibility and production refusals.
- No main-branch integration, push, publication, release licensing decision
  or Studio implementation is implied by the earlier campaign's merges.
- Preserve pre-existing worktrees and untracked files. The new dependency
  symlink is local environment setup and must not be staged.

## Progress

- Campaign bench opened from merged main. The first Sol proposal has passed
  root's adversarial planning review. Leonardo's 80-frame baseline measured
  31.67 s cold, 1.70 s unchanged, and 32.11 s after one interior title edit;
  the edit recaptured all 80 although only frames 21–42 changed. Root checked
  every frame hash and decoded the edited MP4 for inspection. The approved
  whole-shot target is 40 reused / 40 captured, with exact cold equivalence.
- Shot-level incremental rendering is implemented but **not closed**. Sol's
  serial scoped suite passed 133 tests; root independently reran five critical
  cases plus three experiment tests. The 80-frame real consumer now reuses
  40 frames after its local edit, and root verified all 80 PNGs and the MP4
  exactly match a separately cold render. Sol measured 20.22 s incremental
  versus 31.34 s cold for that variant.
- The second real consumer exposed an existing-capture determinism limit:
  its 70-frame fractional/source film has one differing model pixel in
  frame 10 between independent cold browser mounts. Two additional cold
  trials reproduced both values; repeated poses within one mount were stable.
  The expected 25 reused / 45 captured counts are correct, but exact cold
  equivalence is not proven. Preserve the failure and investigate its cause;
  do not relax equality, select only matching runs, or archive the cycle.
  Parallel/compositing product work has not started. Deferred items remain
  deferred. No new campaign work is integrated to main.
- A controlled two-surface ABBA diagnostic proves the viewer can choose a
  different visible overlapping surface when STL downloads finish in a
  different order. Root independently reproduced all four mounts. A narrow
  viewer prerequisite, `deterministic-asset-load-order`, has its planning
  commit `63a9465` in the independent `film-production-order` worktree from
  `f040f45`, under the same delegated review discipline. It is
  limited to eliminating asynchronous load-order dependence without changing
  geometry, materials, the public API or film format. The actual Leonardo
  all-frame gate must still pass; the diagnostic alone does not close it.
  Root excluded pre-existing aggregate load-failure cleanup from this narrow
  correction. Sol has reproduced five unit failures before runtime edits
  and is adding the viewer-owned exact-image browser regression.
- The viewer prerequisite passed its red/green regressions, root's independent
  ABBA replay, and both fixed-viewer real-film matrices; it is archived and
  committed at `94cfcc0` in its own branch. The held 70-frame gate now passes
  every PNG against three separate cold mounts, including the former frame-10
  difference. Root verified all 290 edited/cold PNG pairs across the two
  consumers, saved MP4/manifest hashes and generation origins, and inspected
  encoded review frames. The first Videomaker cycle is accepted for closure:
  80-frame edit 21.84 s versus 34.68 s cold, with 40 frames reused; 70-frame
  edit 16.95 s versus 25.09 s cold, with 25 reused. These are local observations.
  Earlier failures and the original 46-second film remain untouched. Next is
  the bounded parallel investigation, not an assumed parallel product feature.
- Shot-level incremental rendering is archived and committed at `24234d6`,
  paired with tested viewer content `94cfcc0` and its pinned bundle above.
  Both repositories' baseline specs validate strictly. The parallel experiment
  plan is approved; its one-off Sol harness is under root safety/fidelity
  review before execution. No author-facing parallel option exists yet.
- The bounded parallel investigation is closed with **no product change**.
  Three preserved attempts completed no serial/parallel pair. After fixing
  two narrow measurement-harness defects, the resource monitor still could
  not attest an FD-read denial as safe to skip. Root verified the final raw
  failure and process cleanup; no speed conclusion is drawn and no further
  retry is authorized. Rendering remains serial. Next is the independent
  single-browser compositing profile.
- The compositing profile completed and is closed with **no product
  optimization**. Root independently verified all 450 PNG pairs and both
  decoded MP4 streams; the plain/instrumented runs took 120.060/121.996 s.
  Screenshot awaits dominate (74.301 s); weighted arithmetic accounts for
  only 3.167 s. No small material saving is established that preserves the
  same-instant capture contract. No speculative shortcut was implemented.
  The source-only layout planning is committed at `73e97c0`; Sol is capturing
  compatibility baselines and genuine red tests before runtime edits.
- Source-only layout passed root review and the complete real-film gate.
  The scoped suite passed 158 tests; root independently reran its 22 focused
  tests, rehashed all 13 legacy sampled PNG/request pairs, all 280 new-film
  PNGs and four MP4/manifest bindings, and independently decoded the two
  source-only films. The 70-frame edit reuses 25 frames and captures B+C's
  45, matching a separate cold render exactly (including MP4 bytes):
  10.797 s versus 18.064 s in this run. Root inspected the encoded source,
  both fades and return. The source-only text-edge replay and preview-override
  bugs found by the real viewer were fixed without relaxing tolerances;
  an overwritten first red-image directory is disclosed, not called immutable.
  The feature is synced and archived as `2026-09-29-source-only-shots`; all
  nine main specs validate strictly. Automatic review packs follow, with
  stable authored cue identities and renderer-selected fade sides.
