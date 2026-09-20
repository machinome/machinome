# `workflow/` — viewer development records

This directory holds working material of machinome-viewer development that
is real and worth keeping but is not, or is not yet, an OpenSpec record. It
follows the convention the framework established in
`machinome/workflow/README.md`; read that file for the reasoning. What is
here is the viewer's own, and never the framework's.

Working notes here are not ratified public API promises. When a working note
and an OpenSpec spec or an accepted ADR disagree, the spec or ADR is right and
the note is stale. Say so in the note rather than quietly editing the record.

`adrs/` is the decision log, relocated from `docs/adrs/` without changing the
status or authority of any decision. Accepted decisions remain accepted.
`release-0.2.md` is release preparation, not evidence of a published release.
`documentation.md` explains how maintainers build and publish the manual;
`documentation-review.md` records local review evidence.

The public manual lives in `docs/`. Development plans, audits, decisions and
release checklists do not belong in that user-facing tree. OpenSpec changes
and behavioral specifications remain in `openspec/`.

## `warts.md` — findings, in the order they were met

The running log of viewer friction met while running real machines: a cost a
document pays that nothing in the ratified behaviour asks for, a contract the
viewer cannot express, a promise that failed. Entries say plainly whether they
were filed, deferred, or judged not a viewer fix at all.

An entry is evidence, not a requirement. It becomes a requirement only when it
is taken up as an OpenSpec change in this repository.

A finding met while APPLYING a cycle belongs in that change's own
`evidence.md`, under "Out of scope, found while applying", as it always has.
This file is for findings that belong to no cycle — the ones a project's own
work turns up.
