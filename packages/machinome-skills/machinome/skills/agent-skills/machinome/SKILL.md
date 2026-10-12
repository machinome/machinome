---
name: machinome
description: Build, modify, and verify mechanical parts and assemblies with machinome. Use for parametric CAD nodes, assembly placement, mechanical motion, geometry contracts, and visual verification in a machinome project. For reconstructing an existing external design, start with machinome-simulate.
license: GPL-2.0-or-later OR CERN-OHL-S-2.0+
---

# Build and verify a machine

Work in the user's mechanical project and its selected environment. Read its
design record, existing model and tests before changing them. Follow its own
planning and commit conventions; this skill does not require Studio, a team of
agents, or OpenSpec. A request for explanation or review stays read-only.

## Establish the supported interface

Use official machinome documentation as the API authority. This skill supplies
mechanical working practices, not an API catalogue.

1. Identify the installed machinome version in the project's Python environment
   and any recorded source revision. Do not upgrade it merely to match an example.
2. If Context7 is available, resolve `machinome` and query the relevant concept.
   Check the returned source and version; an old package name or documentation
   from a different release is not proof that the installed API supports it.
3. If Context7 is absent, incomplete, or stale, read the official documentation
   linked by the package or the [upstream repository](https://github.com/machinome/machinome), or the version-matched
   documentation shipped with the project. Use the installed CLI's help to
   confirm command options. Do not install an MCP server as a side effect.
4. Look up the CAD backend's official documentation when its API is needed.
   Cite the relevant source when an interface choice matters to the work.

If a needed interface cannot be verified, name the gap and continue independent
work. Never invent an import or depend on a private implementation to fill it.
Treat a documentation defect as a finding; recording it does not submit an issue.

## Shape the model around the mechanical relationships

- Let the node tree represent parts and assemblies with physical meaning. Features
  that form one manufactured piece belong to one connected solid; pieces that
  move independently remain separate. A successful boolean union can still be
  a compound of disconnected bodies.
- Declare each design input where it is owned and propagate it to its dependants.
  Derive mating dimensions from shared inputs: a bore follows a shaft and its
  clearance. Keep placement constants distinct from configurable dimensions.
- Preserve the project's CAD technology and layout unless the task needs a
  change. Import existing geometry instead of redrawing it for convenience.
- Keep rest placement separate from motion. State the origin, axes, units and
  positive direction before writing transforms. Use the installed version's
  documented joint and coupling facilities where they express the mechanism.
- A geometry parameter changes what is built; an operating input changes its
  state or pose. Expose controls in the user's mechanical terms. Use symbolic
  motion operations supported by the documentation so browser and Python motion
  agree; ordinary numeric code may not accept symbolic inputs.
- Choose posed, history-dependent, or event-driven simulation from what the
  machine needs and the installed version supports. Do not introduce retained
  state merely to animate something expressible as a pose.

## Prove the change

For geometry work, read [mechanical contracts](references/mechanical-contracts.md)
before selecting the assertions and measurements. It covers connectivity,
engagement, independent expectations, sampling, and useful mutation checks.

1. Express the intended failure in a contract and run it before implementing the
   change. Distinguish the expected mechanical failure from an environment or
   import failure. Then implement until the contract passes.
2. Check dimensions, placement and operation as applicable. A gear pair needs
   evidence of engagement as well as clearance and its transmission ratio.
   Assert rendered geometry, not a boolean attribute claiming the part is right.
3. Include the project root in regression: local success can hide an assembly
   collision or a disconnected piece elsewhere. For parameter relationships,
   exercise a second meaningful configuration and any affected validity limits.
4. Use a fast geometric approximation during iteration if available. Finish with
   the documented exact checks where the geometry supports them; distinguish
   exact solids from mesh-only imports and report which checks actually ran.
   Investigate disagreements rather than increasing an unexplained tolerance.
5. For a new or materially changed mechanical contract, perturb the relevant
   implementation in isolation and verify that the intended test catches it.
   Restore the change and confirm green. Do not disturb unrelated edits.

## Build, inspect, and hand off

Integrate the component into the model the user actually opens. Run a finite
build in the project's environment and check that the affected parts, placements,
and controls are published. Investigate a stale build through the documented
dependency rules; deleting generated artifacts alone does not fix missed inputs.

Inspect rendered images of the changed assembly from an overall view and a view
that exposes the relevant alignment. For motion, inspect a meaningful changed
pose or operation as well as rest. Pixels demonstrate assembly and presentation;
contracts establish fits and engagement too small to judge from an image.
A still image cannot establish the outcome of a history-dependent operation.

Use the installed viewer and snapshot facilities as appropriate. Reuse a known
project watcher when present; start a live viewer when the task calls for one.
No shop process is assumed. A failed build's leftover artifacts are not evidence
for the latest edit. If image inspection or execution is unavailable, say which
evidence is missing and do not present it as verified.

Report what changed, the configurations and motion checked, test results,
inspected images, and remaining assumptions. Keep generated artifacts separate
from source according to project convention. Record consequential findings in
the project. Commit and close planning records under the user's authorization
and the project's workflow; publication and upstream contact require direction.
