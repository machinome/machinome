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
   103.08 seconds between first/last capture for 450 frames, with two
   simultaneous partial fades on 130 frames. Profile current costs and retain
   exact old pixels; correctness proofs are not weakened for speed.
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
- Use `/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js`.
  Its SHA-256 is `a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`.
  API 28 is integrated source capability, not a published-release claim.
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

- Campaign bench opened from merged main. Proposal and baseline evidence for
  shot-level incremental rendering are next. Deferred items remain deferred.
