## 1. Red-first precision and compatibility proof

- [ ] 1.1 Add direct Frame.resolve and realized-node resolved_frames regressions for Curta's exact supplied triad, independently computing unsnapped normalization, projection and cross product. Prove tiny nonzero components are lost on base before implementation.
- [ ] 1.2 Add explicit literal, parameter/formula and callable direction tests, checking per-instance resolution once and the same cached readout object, plus unit/orthogonality and unchanged degeneracy refusals.
- [ ] 1.3 Pin both-explicit positional/keyword equivalence, explicit default z versus omitted z, x=None and omitted x, all six principal inferred defaults and near-principal/nonprincipal refusal behavior. Pin public Frame/constructor signatures, Frame.z default, declaration repr and accepted arity; no presence sentinel or generic capture signature leaks.
- [ ] 1.4 Add actual public mate composition using precise explicit directions with nonidentity endpoints/origins, independently comparing matrices/basis points. Prove readout matches the actual composed cached basis, not a display-only change, accounting for unchanged final mate snap.
- [ ] 1.5 Pin final mate angle/axis snap unchanged and fresh-generated joint axis normalization/snap independent of Frame precision; reused joints retain their original axes. Preserve existing exact principal and symmetric half-turn fixtures.

## 2. Narrow precision implementation

- [ ] 2.1 Internally record explicit z presence without new public arguments or changed public/default signatures; select precise resolution only with non-None explicit x AND explicit z. Preserve literal default attributes and existing construction/refusal semantics.
- [ ] 2.2 Normalize z, project/normalize x and cross y without component snapping on that path only; leave omitted-direction path, inference and thresholds unchanged. Keep direct resolution, cached resolved_frames and mate composition on the same basis and make red tests green.

## 3. Public documentation and separate companion

- [ ] 3.1 Read write-the-manual before reader-facing edits; add red-first documentation contract tests and update Frame/ResolvedFrame docstrings and docs/concepts/joints.rst universal-snap wording to the both-explicit exception. Keep public signatures/examples accurate; record the numeric behavior change under docs/project/changelog.rst Unreleased only, leaving released records/substitutions untouched.
- [ ] 3.2 Run focused documentation/API structure tests and a strict Sphinx HTML build (warnings as errors); inspect changed built passages as a reader. Reuse existing navigation and examples, add no project/workspace provenance or new links requiring sibling changes.
- [ ] 3.3 Coordinate separately owned Studio companion API correction with root in machinome-studio/WTs/explicit-frame-precision-api: its Frame and resolved-frame paragraphs state both explicit directions retain normalized precision, defaults retain snap, the read is the same mate basis, and final mate/joint snap remains unchanged. No Studio files are edited/staged in this framework tree.

## 4. Verification and reviewed completion

- [ ] 4.1 Run focused and complete frame/mate tests and relevant expression/joint/operation regressions against this worktree, recording red/green commands/results and honest baseline failures.
- [ ] 4.2 Coordinate unchanged Curta zero-mate caller red/green comparisons and 6/6 geometric evidence with root; record tested framework/caller content and original strict tolerances, without caller edits or physical-fit claims. Root's fresh base witness is two tests in 0.730s with structural pass and pose failure at places 8.
- [ ] 4.3 Present implementation, public/default compatibility, documentation and companion evidence to root for adversarial review BEFORE sync/archive. Bring any interface broadening or omitted-z precision proposal to the pilot first.
- [ ] 4.4 Only after verified implementation, record accepted ADR disposition and proportional architecture/decision updates; update wart resolution and archive the intent note. Then supported sync/archive/strict validation under root direction preserves the two-commit cycle. No proposer commit/apply/integration/cleanup or push is authorized.
