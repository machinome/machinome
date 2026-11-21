# ADR-079: Model colors follow the admitted presentation scope

**Status:** Accepted

**Date:** 2026-11-08

**Change:** [read-model-color-choice](../../../openspec/changes/archive/2026-11-08-read-model-color-choice/)

**Amends:** [ADR-076](ADR-076-a-parts-presented-look-has-one-owner.md)

**Amended by:** ADR-076's shared-materials amendment of 21 November 2026:
in point 4, a colour change preserves the mesh, its geometry and its place
in the order of drawing, and points the mesh at the material of its new
colour, where the sentence says "and colored material"

**Builds on:** [ADR-044](ADR-044-a-binding-name-resolves-into-the-shared-dag.md),
[ADR-046](ADR-046-a-committed-bank-is-a-name-in-the-same-scope.md),
[ADR-078](ADR-078-geometry-admission-is-shared-and-resources-keep-their-owner.md)

## Context

Enigma needs its 26 existing glass bodies to show the electrical observation
selected by the same model state its ordinary controls operate. A fixed color
cannot express that observation. Extra bodies, host code and markings would
give a separate owner the model's presentation decision.

ADR-076 already gives hover and highlight one material-presentation owner.
Writing a new color beside that owner would let removing an overlay restore
an obsolete lamp state. Updating materials before validating every candidate
condition would also violate clocked admission: an earlier glass could become
lit even though a later condition refused the request.

## Decision

The node's optional `{when, on, off}` color declaration is evaluated from the
same admitted scope as placement. It adds no presentation state or bank.

1. API 30 reads versions 1–14. The new form requires version 14, exactly
   three fields, a string scalar condition and two fixed six-digit hex
   colors. Both palette entries and the existing expression/binding scope
   are validated before attaching a document. Finite zero selects off;
   finite nonzero selects on. Older readers refuse version 14.
2. A tree retains its nearest inherited color declaration separately from
   its selected string/null. A child's own declaration overrides it. The
   condition's closed input dependencies govern updates, including `$t`.
   Assembly snapshots expose the selected color; markings keep their own
   fixed colors. Rigid and flexible meshes use the same selection rule.
3. Candidate colors and transforms are prepared before either becomes live.
   A clocked request's existing pose-before-bank hook therefore preserves
   bank, events, transforms and materials when a condition fails. A fresh
   candidate scope uses the existing evaluator pass semantics; no global
   cache clearing or new mechanical admission law is introduced.
4. `MaterialPresentation.setBaseColor` rebases the declared material color
   and recomputes active hover/highlight/dim/ghost overlays from it. A color
   change preserves the existing mesh, geometry and colored material.
   The established null/colored material transition remains a replacement
   operation. No material or three.js object crosses the public handle.
5. Initial defaults are resolved before scene attachment. In-place document
   updates prepare geometry, then admit the incoming presentation before
   clearing old overlays or replacing live resources. The admitted colors
   and transforms become live synchronously, before any runtime startup
   await. For version 14, an incoming clocked identity keeps its standing
   bank only when it matches; a changed identity uses its authored initial
   bank. A posed-to-clocked update installs the incoming machine. Existing
   version-1–13 publication behavior is retained.
6. Version 14 describes color choices across execution kinds: `clocked`
   selects a clocked machine, `program` selects a running program, neither
   selects a posed document, and both refuse. Running profile, Follow and
   time-drive payloads retain their existing meaning at version 14.

Running physical-bank ownership is unchanged. A presentation failure does
not roll back committed physical ticks or turn a color condition into a
constraint, stop, integration law or additional interior evaluation.

## Alternatives and consequences

A separate host callback or duplicate geometry would split model truth and
require project-specific client code. Direct material writes would corrupt
overlay restore. Inferring execution from a version floor would misclassify
a posed color document as a missing program. None serves the originating
requirement.

The producer and reader must upgrade together when choices are emitted. This
is an unreleased source capability; published release facts remain API 29
and versions 1–13. It adds no brightness, emission, texture or optical model.

Red-first unit and official-bundle browser evidence covers binding closure,
inheritance, fixed markings, flexible geometry, invalid/non-finite candidate
conditions, cache recovery, overlay interleavings, standard-produced posed,
clocked and running documents, initial powered defaults, state-selected
colors, identity-preserving and identity-changing publication, and unchanged
asset requests. The same original STL is used throughout. Pixel evidence
and the predecessor's explicit version refusal are retained in the change's
acceptance record; real-project acceptance remains separately accountable
to Enigma's electrical oracle.
