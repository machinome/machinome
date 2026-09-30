# Film-production record and guidance cleanup — working plan

Status: reviewed and accepted by root on 29 September 2026 under the
commissioned cleanup scope. This records current-behavior reconciliation, not
new product authority. Root owns baseline sync and archive after the feature
cycles; Sol applies the focused command/docs correction and the separately
scoped workspace skill correction. No runtime behavior, film source, evidence
measurement, new authoring field, or publication is proposed.

## Why this is reconciliation, not a new feature cycle

Two implemented changes remain active in OpenSpec:
`first-narrated-rehearsal` (the original 84-second/2,520-frame Leonardo
rehearsal, adopted **during** implementation) and `narrated-source-scenes`
(later planned and implemented with an explicit **breaking** move to external
SRT). Neither `educational-video-production` nor `narrated-source-scenes` has a
main baseline spec yet. The first delta's on-screen captions and authored
closing credits accurately describe its historical artifact, but conflict
with current `README.md`, `docs/FORMAT.md`, the later source-scene change,
and the pilot's no-credits-in-film policy. A mechanical sync of both deltas
would leave contradictory current norms. Their requirement/evidence text and
adoption chronology must remain intact, not rewritten as if approved first.

This is an archival semantic merge of already accepted behavior. Do **not**
open a new product-feature OpenSpec change just to make external captions or
off-film credits look newly invented. Both baseline capabilities are absent,
so a `MODIFIED educational-video-production` delta would also falsely claim
an existing target baseline. If root determines that an additional formal
cleanup change is required, open it only after the historical capability is
seeded, label it explicitly as record reconciliation, and do no runtime work.

## Purpose text to resolve before first baseline sync

Neither historical delta has `## Purpose`. Before syncing either one, add only
these concise Purpose sections to its existing delta as a **dated
administrative sync-hygiene amendment**, leaving every original requirement,
task and evidence claim unchanged; the commit must not backdate proposal or
ratification:

- `first-narrated-rehearsal/specs/educational-video-production/spec.md`:
  “Support project-authored, inspectable local narrated films of an existing
  posed Machinome simulation, with reproducible presentation and production
  evidence separate from publication.”
- `narrated-source-scenes/specs/narrated-source-scenes/spec.md`:
  “Show export-pinned project Python beside Leonardo's model with deterministic
  typing, reviewable narration, and optional external subtitles, without
  presenting fabricated source or silently changing a mastered film.”

These are Purpose seeds, not claims that either capability was proposed before
implementation. Do not let baseline sync invent a `TBD` Purpose or silently
replace historical evidence. The later source-scenes delta's requirements
otherwise sync unchanged into its own current baseline.

## Exact current educational-video-production baseline resolution

Seed the educational baseline from the original delta, then make the
following *current-baseline-only* substitutions in one reviewed cleanup
transaction, using the later source-scenes supersession and pilot film policy
as authority. Keep all other original requirement blocks (readable screenplay,
input refusal, posed presentation, reusable narration, inspectable evidence)
unless a separate demonstrated conflict is found. Never apply these edits to
the original delta or its 84-second evidence.

1. `Captions and teaching cues follow the lesson`: keep authored explanatory
   labels and measured phase mapping. Replace its video-caption promise with:
   narrated renders provide a same-basename UTF-8 SRT, timed from verified
   speech alignment and preserving written names behind pronunciation aliases;
   the narration transcript is neither burned into frames nor embedded in the
   MP4. Its cut/advance scenario still checks pose/label timing, but checks
   the **external SRT**, not visible transcript pixels.
2. `An author can inspect a local rehearsal`: retain still previews, requested
   size/duration/FPS, local narrated MP4 and reusable caption sidecars. Replace
   the fixed `2,520 frames / 84 seconds / on-screen captions / authored credits`
   scenario with a format-neutral one: the existing global output grid
   requires an integral `count = duration × render fps` and uses frame
   indices `0..count-1` at the requested dimensions (shot boundaries may
   still fall between those global frame instants);
   narration is in the MP4, SRT is
   beside it, and no transcript or credit is burned into the picture. Keep the
   silent preview/no-new-speech scenario. The exact 84-second facts remain in
   `docs/first-rehearsal.md` and the historical change/evidence only.
3. `Credits and publication gaps are explicit`: move normative attribution,
   copyright/license and public-link copy to production-side `credits` and the
   draft/generated upload description, **outside film picture, narration and
   subtitle transcript**. An unresolved public URL stays a marked placeholder
   and blocks `releaseReady`; rendering still does not upload or publish.
   This is an authoring/release-copy policy, not a claim that Videomaker can
   automatically judge a licence or currently rejects every on-film credit.
   Shown picture media's existing credit/rights/committed and description
   placeholder gates remain governed by `stills-and-clips` baseline and must
   not be erased by an obsolete “URLs only” sentence.

The current `narrated-source-scenes` baseline retains its five implemented
requirements, especially `Subtitles are optional player assets`; the
educational baseline above agrees with that explicit supersession. Compare
both resulting main specs against current tests, `README.md` and
`docs/FORMAT.md` before any archive move. Record that the educational main
spec intentionally differs from the old delta for exactly the three blocks
above; do not force an idempotent re-sync of that superseded historical delta.

## Safe sync, archive and links — later apply only

After root ratifies the Purpose additions and exact merge, use the
repository-owned sync/archive procedure in one reviewed cleanup cycle: seed
the two absent main specs from their historical deltas with Purpose, reconcile
the educational main spec to the current policy above, verify no `TBD`, then
archive both changes **without re-syncing** the old educational delta over the
current baseline. The archive summaries must explicitly state that its three
historical promises were superseded, not unimplemented or silently erased.
Preserve both complete delta/design/task/evidence directories and their
original commit chronology. The source-scene delta can be recorded as already
synced before archive; no historical text is rewritten except the dated
Purpose addenda. Stop if the archive/sync tool would overwrite the reviewed
baseline or if any delta/main comparison is unexplained.

Only after paths exist, update the `README.md` link to the inaugural proposal
to its actual dated archive path. In `docs/first-rehearsal.md`, replace the
present-tense “baseline promotion and archive await” status with a dated
archive/current-baseline pointer, while preserving the 84-second hash, frame
count, old closing-credit observation, and adoption-during-implementation
disclosure. Do not imply the pilot later approved that old master for release.

## Explicit test command and verification

The current `package.json` script is `node --test`, which relies on discovery.
Make it explicitly enumerate the supported suites:

`node --test --test-concurrency=1 test/*.test.mjs experiments/dark-source/emphasis.test.mjs`

The experiment's existing test is intentional coverage, not permission to
promote its dark CSS as product styling. Concurrency one matches the current
single-browser safety discipline, preventing two browser-using test files
from competing for the viewer/process lease. Compare the intended explicit
file roster with the already recorded **scoped-suite** baseline, then run the
new `npm test` and verify an ordinary `test/` case and the dark-source
emphasis test appear, with no test discovered under nested `WTs/`. Compare
suite totals to that scoped baseline, accounting for the explicitly added
experiment file. Do **not** run the old unscoped `node --test` as a comparison:
it can traverse nested worktrees. This is a test-runner correction, not a
change in assertion thresholds or film behavior.

The command correction has been applied and verified: source-only's completed
serial `npm test` passed 158/158 (133 prior scoped tests, three retained
dark-source tests and 22 source-only tests), with no nested-worktree discovery.
Sol's pre-edit static command assertion failed; the corrected command and
explicit roster passed. Root reviewed the command and roster and independently
reran the 22 source-only tests. These are the completed source-only suite
results, not a claim that subsequently added review-pack red tests pass before
their implementation.

## Separate workspace skill correction, proposed edit list only

The workspace-owned `skills/videomaker/SKILL.md` is **not** edited in this
Videomaker worktree. Root has opened dedicated
`WTs/videomaker-film-guidance` from workspace main for Sol apply after review;
that actual skill edit must follow `skill-creator`. Keep it to these existing
mainline facts, with no source-only, incremental-cache or review-pack guidance:

1. Replace “keep camera up/FOV constant for the current adapter” with the
   existing format distinction: 0.2 keeps a fixed within-shot lens/up;
   supported 0.3/0.4 shots may key up/FOV when a Viewer API 28 bundle is
   selected and the tool's geometry/refusal checks pass. Still direct the
   operator to current `docs/FORMAT.md` for exact limits.
2. Clarify the generic “Viewer API 21+” setup sentence: 21 suffices for plain
   supported films; annotations/highlights and changed up/FOV need API 28,
   checked against the selected bundle. Do not claim API 28 is published in an
   older viewer distribution merely because source checkout supports it.
3. In inspection guidance, separate visual MP4 inspection from timing and
   readability of the **external SRT enabled in a player**; no transcript is
   expected to be burned into the film.
4. Replace “`releaseReady` reports the URLs, nothing more” with the existing
   URL **and shown-picture media** gates (credit/rights/committed file and
   `{{pictureCredits}}` description placeholder). State clearly that this
   flag does not verify rights, links, human approval or publication permission.

No skill metadata/frontmatter UI edit, no new campaign feature advice, and no
workspace primary-checkout write. Root reviews this precise list before the
separate apply agent edits the dedicated workspace worktree.

## Workspace correction completed on its branch

Sol applied exactly the four reviewed guidance corrections in workspace
`WTs/videomaker-film-guidance`. Sol empirical independently compared the diff
to the existing camera, subtitle and picture-release code; ten pure Node
camera/annotation/highlight tests passed without a browser. Root reviewed the
diff and source, independently checked static/cut API selection, ran the
skill-creator validator and `git diff --check`, and committed only the skill
at workspace `ba0a39c`. Metadata, no-credit policy and narration-cache wording
are unchanged. Skill-creator guidance kept this a focused existing-skill
correction, without new metadata or campaign features. The branch is clean;
workspace main remains untouched and no merge/push is implied.
