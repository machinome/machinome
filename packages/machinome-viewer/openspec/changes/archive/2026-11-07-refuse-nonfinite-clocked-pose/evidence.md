# Rendered clocked pose refusal — implementation evidence

Pilot authorization on 2026-11-07: **Authorize implementation and local integration**,
following review of the concrete proposal and its evaluator-cache recovery
addition. The approved target is the monorepo viewer. No push/publication is
authorized. The parent repository agent coordinates the eventual primary
fast-forward and installed bundle refresh after its normal Enigma snapshot.

Base: `c8e5e124f84a015f8da322c4ced0fd3ce52ef4f3` on clean `main`.
Planning-only commit: `da27c6727311db623071e678eb27028db6c88dfa`, verified clean
and exactly one commit above that base before implementation. The managed
worktree is `machinome/WTs/refuse-nonfinite-clocked-pose`, slot 14.

## Correction and scope

`WidgetTree.update` now prepares the selected local matrices and validates their
composed world placements before copying any of them into the scene. It refuses
non-finite evaluated operands and matrices, or a throwing operation, with the
assembly path and operation index/type/expression preview. Unchanged descendants
inherit a changed ancestor's composition checks. Unrelated branches retain the
existing expression dependency rules; composed matrices are built lazily only
on affected paths. Transform refusal happens before flexible buffers are
refilled. Valid flexible updates retain their existing buffer ownership/reuse.

The clocked machine's existing pose-before-bank hook required no change.
Neither evaluator caches, driver/State range semantics, event location,
public handles, document format nor API version changed. The source-owned
fixture's independent driver advertises range -1 to 1 but admits a finite move
to 4, pinning the metadata distinction. An unused undefined binding is retained
without evaluation in the tree regressions.

Candidate memo values may remain in the evaluator after refusal. Scope maps are
fresh and `ensurePass` compares the complete bank scope, so a standing-bank or
independent-driver recovery cannot reuse invalid candidate values. Real
cached-NaN and throwing-evaluation regressions exercise original-bank retry,
an independent-driver move without reset/remount, and later valid recovery.
No cache rollback or global clearing was introduced.

No new ADR: this is enforcement of final-pose atomicity already accepted in core
ADR-125 and viewer ADR-062/064. The architecture synthesis remains accurate;
the viewer baseline receives the explicit final-rendered-transform requirement.

## Red and green

- `evidence/tree-red.log`: original `tree.ts` gives eight failing new tree cases
  while its existing 61 cases pass. Covers NaN, both infinities, real thrown
  member evaluation, sibling rollback, bindings and finite-local/world overflow.
  The original source was restored temporarily for the final corrected test
  spelling, then the implementation restored in a `finally`; no commit or
  browser bundle was changed by this isolated source mutation check.
- `evidence/browser-red.log`: before production editing, the actual baseline
  built bundle and unedited standard document accept the first invalid final
  pose. This is an assertion failure, not a missing-browser skip.
- `evidence/widget.log`: complete final widget suite **1,724 passed, 2 skipped**;
  the existing skipped cases require optional external Curta data. The focused
  tree/flexible suite also passes **87 tests**, including an earlier flexible
  shape whose buffers/version/evaluation count stay unchanged when a later
  transform is refused.
- `evidence/typecheck.log`: normal widget TypeScript check passes.
- `evidence/browser.log`: **3 passed**, including source/receipt integrity,
  mounted move/restore and cache recovery, and continuous instruction refusal.
  No required browser acceptance skipped. Screens and bank stay standing,
  screenshot bytes before/after invalid requests are identical, and a later
  valid press fires exactly its one expected event. The independent-driver
  recovery occurs before the separate clean-reset geometry comparison.
- `evidence/native-clocked.log`: native clocked simulation, exact-endpoint,
  conformance-corpus and document checks **170 passed, 206 subtests passed**.
- `evidence/viewer-python.log`: complete final viewer Python suite **255 passed,
  2 skipped, 191 subtests passed** in 291.17 seconds. The two skips require
  external Curta build directories and are unrelated to this correction.
  The source-owned browser acceptance ran and passed in this full suite.
- `evidence/style.log`: black check and flake8 (89-column repository limit)
  pass on all three added Python source/test files.

Commands (repository root unless a working directory is specified):

```sh
uv sync --frozen --python 3.12
npm ci --ignore-scripts
npm run typecheck --workspace @machinome/viewer
npm run build --workspace @machinome/viewer
npm test --workspace @machinome/viewer
# packages/machinome-viewer:
../../.venv/bin/python -m pytest tests -q
../../.venv/bin/python -m pytest tests/test_clocked_pose_admission.py -q
# packages/machinome:
../../.venv/bin/python -m pytest tests/test_clocked_sim.py tests/test_clocked_endpoint.py tests/test_clocked_corpus.py tests/test_clocked_document.py -q
```

The fixture generator is development-only and uses public `machinome export`
and `Sim`. Its source, authored four-triangle STL, unedited version-8 document,
exported four-triangle mesh, native oracle and source hashes are retained under
`tests/fixtures/pose-admission/`. The ordinary viewer test only consumes that
packet and the built official bundle, importing no native model code.

## Originating Enigma replay and handoff

The actual project/source STL was not copied into framework fixtures. The
project's retained version-8 packet remains unchanged, including standard
document SHA-256 `3bc17a362ce89e2c12c61fbbda76f02d541e3b318fa1deea5b94eebc2b9fbadd`.
The public bundle/source hashes and raw replay report are retained in
`evidence/receipt.json` and `evidence/enigma/`. This makes the evidence survive
worktree cleanup after integration; the originating project can copy that
subdirectory into its own `sources/derived/viewer-pose-refusal-correction-v1/`.
No canonical project manifest or build was changed.

Run the retained public checker from the isolated rotor project with the desired
runtime's interpreter (it locates that interpreter's public `machinome viewer`
report), writing a fresh output directory:

```sh
# cwd: /mnt/data/machinome-projects/enigma-i-worktrees/rotor
<framework-worktree>/.venv/bin/python -m simulation.tools.check_flank_expression_viewer --report sources/derived/ordinary-flank-visible-v1/visible-inputs.json --output <fresh-output>/viewer-check.json
```

The checker requires the isolated diagnostic worktree and refuses canonical
main. It intercepts public document/bundle/model requests with Playwright;
there is no custom delivered interface or diagnostic-root rebuild. Retained
inputs are pinned by `sources/ordinary-flank-expression-validation-v1.json`
at project evidence commit `c7f125b`.

Result: **33 valid poses, 3 invalid requests refused**, complete snapshots
unchanged, no non-finite public screen coordinates and no uncaught page errors.
The inspected actual source pawl stays visible at its standing placement after
refusal. `visible-valid.png` and `visible-outside.png` are byte-identical, both
SHA-256 `f814f9a166d3976c1fdc66f99455c55b60d2aa81fcb22bc679a019ddd3fb1a13`.
The three named failures identify `pawl operation 0`, rather than silently
moving the bank or propagating NaN. This establishes browser conformance; it
does not admit the partial first-flank law as a complete Enigma operating law.

After authorized integration, the parent repository agent will coordinate a
normal primary viewer build and repeat this public check with the shared
installed interpreter, recording the final framework commit and actual installed
bundle SHA-256 in the originating project's durable evidence. Fast-forwarding
source alone is not evidence that an ignored previously generated bundle was
refreshed.

OpenSpec: the delta was synchronized into viewer `viewer-package` and both the
change and target baseline passed supported strict validation. The archive
retains the complete planning state and raw evidence. Local integration and
installed/canonical-model checks follow the parent coordination hold point.
