## Why

The pilot requested adversarial review and correction of `direct-part-motion`
before using the corrected framework for the Curta. Review reproduced two conformance
gaps: a legitimate joint override breaks an inherited selected control, and
the placement-span check accepts a contiguous but incomplete pivot block.

## What Changes

- Resolve a validated selection to the effective joint on the realized body,
  retaining foreign-reference, domain, reachability and multi-coordinate refusals.
- Verify that a published span contains the complete ordered joint placement,
  not merely some contiguous operations carrying its slot.
- Add adversarial regression tests and record the paired viewer/Curta handoff.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: clarify selected controls under supported joint overrides.
- `export`: clarify refusal of truncated or reordered selected placement blocks.

## Impact

Internal control resolution and placement ownership metadata, tests and evidence.
The public declaration and document shapes, program identity and run semantics
do not change. This is corrective work under the pilot's explicit review-and-fix
request, not another interaction design or permission to integrate into main.

The pilot subsequently merged the prerequisite into main and explicitly directed
the fixes to branch from main. Corrective-cycle base is now
`1aac0ffa8c430b68e97dc1acec04a2d0cd21b140`, clean primary branch `main`.
Use branch and worktree `harden-direct-part-motion` under `solid-node/WTs/`;
its integration target is main, subject to separate pilot authority. Preserve
the original `direct-part-motion` worktree and its review work in place.
The planning/implementation pair begins at this new base without rewriting
the other agent's history.
No push, publication, primary-checkout mutation or worktree cleanup is authorized.
