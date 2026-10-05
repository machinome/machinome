# Parent adversarial review — accepted for owning workflow completion

On 2026-10-05 the parent independently reviewed the validation memo, binding
preparation, geometry admission, tree ownership and reload changes. This is
initially partial review. The final acceptance below supersedes that initial
status for this viewer change only, not for the unfinished Voron project.

## Cancellation result-ownership regression

Source inspection identified a promise-continuation gap: the STL loader could
return live geometry, then its owner could cancel before admission delivered
the value. Admission rejected the promise without disposing that value.
`src/parent-adversarial-geometry.test.ts` resolves the real tree's mocked loader,
yields one microtask, disposes the tree, and checks rejection, no attachment
and exactly one disposal of the returned geometry.

Parent red command, from `machinome_viewer/widget` at 17:13:45 UTC:

```sh
npm test -- src/parent-adversarial-geometry.test.ts
```

Result: one failure, `dispose` expected once but called zero times. The tree
rejected and attached no mesh, so absence of attachment alone missed the leak.
The separate applier corrected abandoned-result disposal and the post-admission
owner check. The parent then ran at 17:16:45 UTC:

```sh
npm test -- src/parent-adversarial-geometry.test.ts src/validation-pressure.test.ts src/expression-lifetime.test.ts src/run/profile-contact.test.ts
```

Result: four test files passed, **41 tests passed and one existing installed
profile-export test skipped**. The measured validation counts remained one
root-map preparation, zero generation changes and 303 visits for 303 nodes.
This result does not replace the full suite or the browser lifecycle tests.

At 17:55:55 UTC the parent extended the same file with artifact-update disposal
at eleven promise-continuation positions. It builds the actual `WidgetTree`,
starts `artifactChanged`, resolves its deferred loader, yields zero through ten
microtasks, disposes the tree and observes subsequent `group.add` calls. The
same focused command reported **three failed, nine passed**: positions three,
four and five attached a replacement after disposal. This independently exposes
a missing commit-boundary disposal check after aggregate preparation; disposing
the geometry alone does not prevent the forbidden late attachment. The separate
applier is correcting it within the reviewed lifecycle scope. Acceptance and a
fresh final candidate are still required.

After the applier added the commit-boundary check and four shared-path
model/marking disposal controls, the parent independently reran at 17:59:06 UTC:

```sh
npm test -- src/parent-adversarial-geometry.test.ts src/geometry-admission.test.ts src/validation-pressure.test.ts
```

All **38 tests passed**. This includes the original abandoned-result race,
all eleven artifact-update timings, queued cancellation/FIFO priority, and the
shared model/marking cases. Counted work remained four active groups for all
18 requested loads, one validation preparation with no generation change, and
303 negative-inspection visits for 303 nodes. The applier's production bundle
for this correction is `02bde914f9d30f4d5866d2eb64cdb76abb73be1aac77a949ca3475ccc7a132b4`;
fresh full-suite and browser results for that bundle remain to be reviewed.

## First actual portable-printer image

The parent inspected the applier's `queued-public-long-rest.png` from
`/tmp/voron-viewer-apply-Yi3m3o/`. It depicts the complete exterior enclosure,
frame corners, door hardware and lower drive components, with default controls
`e=0`, `x=124.9996`, `y=129.0998`, `z=27.0093`. Opaque enclosure panels obscure
the internal gantry; this view alone cannot verify belt shape or moved parts.

The accompanying result records 1,568 HTTP-200 responses including all 1,565
model paths, no failed requests, one canvas and a maximum of four pending
model requests. Chromium was 151.0.7922.34. Exact pins:

- Supplied candidate bundle: `a0b4c48bc2efeed911e8ad38674d3bb523150fc1df0510ee6cb855488adf4db2`.
- Unchanged manifest: `e9fee11746ff36a1f585f24a3db154b472a207bfc83db00e183ebdc96f2cb0c7`.
- Unchanged page: `5a9b57d06fc62ff8acf1d4d3e7c51a7a9b1ee0a01415684a17aecbd3c1fa4605`.
- Screenshot: `3c774d0b038c2dbae5a61a4d528049e7bc557e94e147d1a5fe42d39f7f9bdece`.

The complete probe took 55.604 seconds and exited **1**: graceful browser
closure exceeded its five-second deadline after screenshot and resource checks
succeeded. Cleanup records process group 158908 with no surviving members.
Do not relabel that run as a fully passing process gate. Subsequent lifecycle
corrections also require a newly built candidate and fresh browser evidence.

## Remaining acceptance gates

The final full-suite result, complete host assembly and finite bounds, declared
Home/Center/Present states, independent rigid/flexible geometry comparisons,
return/reload behaviour, simultaneous-viewer and failure isolation, and full
cleanup must still be reviewed. Larger-than-budget draw-order/pixel tests must
remain green. The separate capture-fetch wart and the printer's native-geometry
blockers are not resolved by this review.

## Full-manifest refusal and recovery check

The parent independently bundled the current `assertRenderable` implementation
for a bounded Node diagnostic and loaded the unchanged real 232,347-binding
manifest identified above. This is validation evidence, not browser evidence.
One process, fenced by `timeout --signal=TERM --kill-after=5s 90s`, performed:

1. Validate the original manifest: accepted in 4022 ms, one map preparation,
   610,546 structural visits and 610,546 expression nodes.
2. Append the unreferenced final binding `{name: '_parent_unreferenced_bad',
   expression: 'parent_missing_driver + 1'}`: refused in 3913 ms with the
   undeclared-driver name. The original four drivers remained e/x/y/z.
3. Remove that binding and append root operation
   `['t', ['profileOverlap(0, 0, 0, 0, 0, 0, 0, 0)', '0', '0']]`:
   refused in 2292 ms as outside a numeric Bound.
4. Remove the operation and validate the restored original in the same process:
   accepted in 3639 ms, again one preparation and 610,546 visits/nodes.

Every phase reset only the source-level work counters, not document validators
or production cache thresholds. The manifest SHA256 was independently verified
before and after. Neither the export nor any model/cache file was written.
The process exited zero. The temporary entry/build scripts are at
`/tmp/voron-parent-validation-rd3WYo/`; the four steps above specify their full
mutations and acceptance conditions for reproduction with the evidence annex's
source-bundling procedure. Durations describe this diagnostic run, not a
cross-platform performance guarantee.

## New project geometry finding remains distinct

The parent also inspected `host-rest.png` and `host-Present-interior.png`.
The latter uses the existing enclosure-visibility control after the full
assembly mounted: the raised gantry/toolhead is visible above the bed. It is
supplemental inspection, not a pruned-document mount or belt contact proof.

The full host diagnostic's independent document-language oracle must use
truncated remainder (`math.fmod`), as specified by the framework export spec
and its existing expression evaluator. The project's Python `operator.mod`
helper instead masks a separate physical publication defect: signed CoreXY
wraps differ by a full turn between ordinary Python construction and the
published expression graph. The parent confirmed the route source and the
framework's already-recorded pose-versus-graph limitation. Correcting the
document oracle establishes browser/document parity only; it does not resolve
the approximately 16.06 mm intended-belt discrepancy. A separate project-owned
proposal, `publish-voron-corexy-signed-wraps`, is investigating that correction.
Viewer numeric semantics must remain unchanged.

## Final viewer-scope acceptance

The parent accepts task 4.3 on 2026-10-05 for production bundle
`02bde914f9d30f4d5866d2eb64cdb76abb73be1aac77a949ca3475ccc7a132b4`.
All identified in-scope lifecycle failures have retained failing controls and
passing corrections. The parent reviewed the final source changes, controlled
counts/refusals, test-observer qualification, complete evidence record and raw
portable/host results; independently verified the final bundle/result hashes
and every one of the 1,568 original input file hashes; and inspected the final
rest/default-controls and Present-interior images. Viewer main remained clean.

Final current-source validation is 1,715 widget tests passed with two retained
missing-Curta-input skips, and 81 relevant Python/browser tests passed without
skips. The original portable page obtains 1,568 HTTP-200 responses, zero failed
requests/page errors, one canvas and peak four pending models. The complete host
has all 1,636 nodes/1,565 models, the declared defaults and instruction targets,
finite bounds, exact three-belt vertex/index agreement with the independent
**published-document** oracle, and maximum representative matrix error
2.842170943040401e-14. Reload rechecks full counts/defaults/bounds. The parent's
independent 38-test rerun and full-manifest refusal/restoration checks are above.

The portable probe's five-second graceful browser-close deadline still expires;
this is explicitly retained, not described as graceful teardown success. Its
owned supervisor terminates the process group within the bounded cleanup fence
and verifies no survivors. All final test/browser/lifecycle supervisors report
exit zero and no surviving members. This acceptance establishes bounded cleanup
for the measured environment, not a cross-browser or memory/performance guarantee.

Final portable result SHA256:
`96fca8c188aace48cdf25c0bcba5fa04334c771cb166a7c7dc0fd9e779c98a94`.
Final host result SHA256:
`c124c714bcf7a3561be57482620c5ba478e6252aac535bad3454b6928a946a9b`.
These raw results and the source-only diagnostic/reproduction scripts remain in
`acceptance/`; no input export or project geometry was modified for acceptance.

Proceed with the planned ADR clarifications and geometry-admission decision,
parent review of those records, portable-export-only wart disposition, then
supported spec synchronization, strict validation and archival. The pilot's
existing local-integration authority applies afterward; no push or publication.
The separate capture-fetch wart and the project's intended CoreXY signed-wrap,
native screw/T-nut, containment and broader whole-printer gates remain separate.

### Completion record

The parent reviewed and accepted the complete ADR-043/044 dated amendments
and ADR-078, then synchronized the two viewer-package requirements. Both
resulting requirement blocks equal their reviewed deltas; all other baseline
content is byte-for-byte unchanged. Strict change and baseline validation
precede archival under `2026-10-05-mount-voron-export`. The enclosing focused
implementation commit completes the cycle. Local main integration remains
authorized separately; neither release nor publication is implied.
