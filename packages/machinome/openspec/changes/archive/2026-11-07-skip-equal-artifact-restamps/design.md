## Context

This standalone core maintenance cycle starts at clean framework primary `main`
`b0829b39809e64e889e56eb9bececa57cd3430ad`. Workspace
`scripts/dev-env skip-equal-artifact-restamps setup` created the exact
same-named branch at
`/home/asa/devel/machinome/machinome/WTs/skip-equal-artifact-restamps`, slot 15.
The integration target is that primary `main`, only if still clean and at this
base. The pending `illuminate-model-lamps` worktree remains unchanged.

The origin is Enigma's ordinary declared model, not a new extracted feature.
Plain builds retained under project `sources/derived/standard-model-publication-`
`v4/`, `v5/` and `v6/` failed pinned-artifact validation. Full trace v3 on
project `a3bd96a7e2da90e8a04c38fd3861163a0d514e90` succeeded in 204.737 s after
two caught refusals on Ratchet III/V; source/framework pins and the existing
viewer document SHA-256
`f6ffa7958cf787d2d5b06f246a11d380ef4b3851f8585756a653650629ddbf6a`
were unchanged. On its two watched artifacts it found eight exact-equal mtime
restamps, all with matching worker syscall/audit/inotify events, and six other
ctime-only stat jumps without such events in its stated 250 ms classification
window. Bytes were unchanged; no watched writable open/mmap/write or writable
guest `/proc` handle was captured. This is a bounded observation, not proof of
the unknown writer or shared-filesystem mechanism. Idle/copy/facts controls were
negative. Never describe this correction as the delayed-ctime cure without new
caller evidence.

Current source and contracts read for this plan:

- `docs/architecture.md`, source-generation/currency and strong-identity sections;
- `openspec/specs/build-pipeline/spec.md`, exact timestamp/content fallback,
  source fingerprint, coarse-filesystem, source generation and redundant-write
  requirements; `printed-pieces`/`model-consumption` strong artifact identity;
- accepted ADR-006/033/060/071/081/084/186, especially ADR-060's best-effort
  restamp and ADR-081's mandatory per-contributor fingerprint fallback;
- `machinome/node/base.py::_up_to_date/_content_verified`,
  `machinome/currency.py::restamp/record/publish_text`, `_artifact.py`, and
  `core/pieces.py` publication ownership;
- existing content-verified currency, coarse-filesystem, generation-dedup,
  piece-facts/replacement and producer-recipe tests.

`_up_to_date` first refuses a mismatched producer recipe, then requires both
artifact mtime and source-set fingerprint for its settled hit. A miss enters
`_content_verified`, which proves retained source content/current or compatible
legacy digest before calling `currency.restamp`; it then records current digest,
fingerprint and recipe. `restamp` presently always calls `os.utime`, setting
atime to now even when mtime already equals the desired integer. `publish_text`
already skips its restamp call for exact-equal mtime. The artifact's atime/ctime
refresh is not an accepted currency requirement.

The package owner is unambiguous: core source/tests/specs are under
`packages/machinome/`. Current accepted monorepo architecture is authoritative;
the OpenSpec CLI's context still contains older source/frontend layout and
commit shorthand. This cycle does not adopt or edit that stale context. The
workspace skill owns the managed bench and two-commit discipline. No
framework-local prompt/AGENTS file was read as authority.

## Goals / Non-Goals

**Goals:** avoid an unnecessary artifact timestamp syscall when exact desired
mtime already holds; preserve content/source/recipe verification and required
record migration; prove an earlier pin survives that refresh; exercise ordinary
Enigma delivery with the owning WT runtime and locally integrated runtime.

**Non-Goals:** identify or mask every shared-filesystem writer; promise reliable
plain delivery before measuring it; remove ctime/inode/device checks; add a
tolerance, content shortcut, snapshot repinning or another retry; change public
API/format/dependencies; modify the mechanical model, geometry, document, cache
layout, viewer/Studio or the pending lamp appearance proposal.

## Decisions

### 1. Put exact desired-state suppression at the existing mutation helper

In `currency.restamp`, stat the artifact inside its existing best-effort
`try`/`except OSError` boundary. If `st_mtime_ns` exactly equals requested
`mtime_ns`, return without `os.utime`; otherwise retain the existing integer-ns
utime operation. No rounding, tolerance, coercion or new input format is added.
Stat/utime errors remain best effort and logged; no error manufactures a new
content proof or artifact. The helper does not read artifact bytes.

This centralizes the no-op rule for all existing callers. An alternative
caller-only condition in `_content_verified` duplicates timestamp-write
decisions and leaves other helper callers able to make the redundant mutation.
Changing the snapshot guard would discard a valuable refusal and is rejected.
Adding retries or suppressing fingerprint checks is also rejected. Doing
nothing avoids a patch but retains an empirically demonstrated needless write.

### 2. Keep proof and record refresh independent of the timestamp write

Do not move the equality shortcut into `_up_to_date`'s source proof or return
from `_content_verified` before `currency.record`. Even if an artifact's mtime
already matches, a missing/different fingerprint or compatible legacy record
still needs the existing retained-source proof and current record. A changed
recipe, changed retained source, unknown/malformed/missing digest or unreadable
source must retain its present refusal. Current/previous-rule migration rules,
publication ordering, per-generation checks and artifact replacement detection
are unchanged.

The exact comparison is desired timestamp state, not artifact validity. Another
writer can still invalidate an artifact and must still be rejected by the
unchanged `ArtifactSnapshot`/inventory validation. The stat-to-action interval
does not gain a new atomicity claim. Where differing timestamps cannot be made
equal on a coarse filesystem, attempt restamping once as today and retain
digest-proven currency for the current check without looping.

### 3. Use a real source-owned red proof rather than Enigma geometry

Extend the existing small `test_content_verified_currency.py` source fixtures.
Hold an actual `ArtifactSnapshot` open across a real `_up_to_date` fallback,
with the artifact mtime already equal to the node's maximum source mtime.
Exercise two actual triggers: a matching legacy digest-only record upgraded to
the current fingerprint, and an equal-content contributor metadata change below
an unchanged maximum. Assert the currency answer/updated record and validate
the original pin afterward. The current tree must fail at pin validation from
its unnecessary ctime mutation; record that red before editing production.

For the fingerprint scenario, the existing future-maximum fixture pattern can
keep the aggregate mtime fixed while rewriting a contributor with identical
bytes. Do not fake a successful digest/fingerprint proof or replace the real
snapshot check. Use the framework's authored tiny fixtures, not Enigma STLs.
The tests can reuse current tiny native fixtures where required, with no long
full-model CAD operation.

Retain genuine changed-mtime STL/BREP restamp, settled source-content-free hit,
coarse-resolution, missing/unreadable/stale source, incompatible recipe,
legacy/current digest migration, generation checks, same-size restored-mtime
replacement and fact-cache invalidation tests. Add a bounded helper/error case
only where needed to cover a newly introduced stat-error branch; do not add an
unrelated filesystem abstraction or benchmark.

### 4. Caller acceptance uses the actual ordinary path twice

After root review releases the hold, create the worktree's own uv environment
from its lock (`uv sync --python 3.12`) before running tests. All framework tests and project WT checks
must consume its source-owned core, with actual distribution/source identities
recorded. Do not mutate the shared installed environment during isolated work.

After focused framework proof is green, under the existing secondary native lock and in coordination with root's model
jobs, run one ordinary `machinome build` from canonical
`/mnt/data/machinome-projects/enigma-i` using the WT-owned executable. Pin the
current declared model inputs/reference, compare document and STL byte hashes,
keep all original guards, and retain elapsed time, code, stderr/error state and
any caught/final refusal. No custom model/build directory, cache purge, manual
document edits or STL rewrites are validation aids. Ordinary required currency
record refresh remains allowed through its production writer.

After reviewed authority covers local completion, sync/archive and produce the
two-commit cycle. Coordinate integration with root; reverify primary clean `main`
still at `b0829b39`, fast-forward only, then refresh the workspace's editable core
through its normal install mechanism. Core is Python: no viewer bundle rebuild
belongs to this change. Record installed module path/source SHA and framework
commit, then run one **plain uninstrumented** canonical ordinary build and check
normal document/error state, input/artifact bytes and public Studio availability.
Report traced success separately from plain delivery. Any remaining refusal is
retained and reported; do not silently weaken guards or repeat builds until one
passes. Root review of these outcomes determines whether acceptance is met.
The post-integration receipt belongs in the originating project's retained
evidence and final handoff, so the framework keeps its two-commit shape. The
archived implementation record must identify that delivery check as pending
until its actual result exists; archival alone is not accepted Studio delivery.

## Risks / Trade-offs

- [Unknown delayed ctime cause] → Claim only the proved no-op correction. The
  prior controls were negative; origin acceptance must be measured and failures
  remain visible rather than erased by success from an instrumented run.
- [An extra stat on fallback mutations] → Keep it inside the existing helper;
  settled metadata hits remain unchanged and no artifact content is read.
- [Record upgrade accidentally skipped] → Both pin-survival tests must also
  assert the correct current digest/fingerprint/recipe record.
- [A differing timestamp or coarse filesystem stops being supported] → Preserve
  the one actual utime attempt and its existing best-effort tests/semantics.
- [Concurrency is overstated] → Exact equality is not validity or locking; all
  source-generation and strong artifact observations/refusals remain intact.
- [Primary moved] → Report base/new head and stop; do not rebase/merge/cherry-pick
  around the standalone identity gate.

## Migration Plan

No data migration, API/version gate, dependency or new feature declaration is
needed. Existing cache/source records retain their exact readers/writers and
formats. At most the existing helper/docstring and implementation evidence need
updating. This is not a new architectural choice, so an ADR/architecture edit is
not expected; confirm that disposition after implementation, not before tests.

Authority comes from workspace `goal.md`'s instruction to deliver the declared
model/ordinary build and correct limitations in the owning package, delegated by
root to this standalone maintenance cycle. **Review recorded 2026-11-07:** root
approved proposal/design/spec/tasks as maintenance under that active goal and
released the apply hold for planning commit 1, red-first implementation, focused
checks, canonical Enigma WT-runtime caller acceptance and sync/archive/completion
commit 2. Local integration is authorized after root reviews green caller
evidence and the exact two-commit handoff. Root's review is delegated agent
review under pilot goal authority; it is not represented as human review of the
finished artifacts. Do not invent a second pilot gate for stages already covered
by that authority. Recheck root's secondary native slot/model freeze before the
caller build. Shared workspace core is already editable at primary: inspect
module resolution after integration before deciding that reinstall is needed.
Push, publication, tagging and contact remain outside this local cycle.
The lamp API proposal is separately unratified and never enters either commit.

## Open Questions

No interface decision is open. Root has approved the plan and released apply;
the green caller/two-commit integration review remains the explicit hold. The source
of the additional delayed ctime jumps is unresolved and is not settled by this
plan. The implementation/caller evidence must establish the exact maintenance
benefit and honestly delimit any ordinary-build limitation that remains.

Planning validation receipt, 2026-11-07: supported OpenSpec status reports all
four artifacts complete, and `openspec validate skip-equal-artifact-restamps
--strict` passes. This receipt covers planning only. No runtime test, dependency
sync, source edit, commit, installation or integration has occurred in this
cycle at that receipt. The subsequent root review above now authorizes apply.
