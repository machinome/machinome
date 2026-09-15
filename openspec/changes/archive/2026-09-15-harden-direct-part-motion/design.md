## Context

Review of implementation `53bd983` reproduced failures for an inherited
`coordinate=own_joint` control when a subclass or declaration site replaces
that joint. The control currently compares the old declaration's identity
with the effective joint table, although the relation already addresses the
effective coordinate by name. A second probe removed one pivot translation
from a three-operation selected revolute placement: `_published_span` still
returned a two-operation span instead of refusing the incomplete placement.

The user initially requested review and fixes in the existing worktree,
then Curta implementation using it. After merging that work into main, the
user explicitly directed the corrections to branch from main instead.
This corrective cycle preserves the
ratified public design and both of the other agent's commits. The stale CLI
context concerning a framework-local web app does not apply: the viewer is
an independent repository and consumes only exported documents.

## Goals / Non-Goals

Goals: make effective joint selection and complete-placement refusal conform
to existing declaration and export contracts, with red-first adversarial tests.

Non-goals: new gestures, new public arguments or document fields, run/solver
changes, acceptance of foreign references or multi-coordinate joints, main
integration, or changing the Curta's operation design.

## Decisions

1. Resolve validated coordinate references to the effective named joint on
   the realized node. Keep class-definition ownership checks and instance
   ancestry checks. Recheck effective coordinate count and domain after an
   override so a single-coordinate selection cannot unpack a Free joint or
   silently change a slide into a turn. Check raw declarations only to reject
   a non-joint reference; their old identity is not an effective placement.
   Requiring every reusable body to redeclare its controls was rejected
   because supported joint overrides already preserve named relation ends.
2. Extend existing private placement ownership marks with each operation's
   index and the placement block's total length at the insertion seam. A
   selected span must contain the complete ordered sequence as well as one
   contiguous slot. Do not trust a stale side list, resynthesize geometry or
   parse expressions. These marks are not serialized and change no program.
3. Preserve the previous implementation record and add this correction as a
   new planning/completion pair based on merged main `1aac0ff`, in the
   `harden-direct-part-motion` branch/worktree, as the pilot now directs.
   Keep the former worktree and review state intact. The original paired browser evidence
   remains outstanding until the independent viewer and Curta are exercised.

## Risks / Trade-offs

- Name resolution could accidentally admit a foreign declaration → retain
  the existing declaration checks and add same-name foreign-reference tests.
- Joint replacement can change shape/domain → test revolute/prismatic and
  Free replacements and read the effective geometry, not the old declaration.
- Placement marks must survive lifecycle operations → exercise rebind,
  snapshot/replay and checkpoint restoration alongside truncation/reordering.

## Migration Plan

Validate and commit the focused planning state, implement after regression
tests fail, run the affected suites and full framework regression, regenerate
consumer fixtures, and preserve legacy documents and corpus bytes. Record the
confirmed fix, sync and archive this corrective cycle, then commit its complete
state. Use the reviewed worktree for the independent viewer and Curta work;
do not integrate into framework main without separate authority.
