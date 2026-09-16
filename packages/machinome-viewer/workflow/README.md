# `workflow/` — the viewer's pre-spec working record

This directory holds working material of solid-node-viewer development that
is real and worth keeping but is not, or is not yet, an OpenSpec record. It
follows the convention the framework established in
`solid-node/workflow/README.md`; read that file for the reasoning. What is
here is the viewer's own, and never the framework's.

Nothing in this directory is ratified, and nothing in it is a public API
promise. When a document here and an OpenSpec spec or an accepted ADR
disagree, the spec or the ADR is right and the document is stale. Say so in
the document rather than quietly editing the record.

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
