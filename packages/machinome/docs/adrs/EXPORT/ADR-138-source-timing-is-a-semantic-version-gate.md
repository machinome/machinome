# ADR-138: Source timing is a semantic version gate

**Status:** Accepted

**Date:** 2026-09-22

**Amends:** The minimum running document-version and identity-preservation
decisions in ADR-110, ADR-121, ADR-122 and ADR-133; preserves payload syntax,
the independent viewer process boundary and ADR-111 conformance discipline.

**Change:** [preserve-carry-across-graph-expansion](../../../openspec/changes/archive/2026-09-22-preserve-carry-across-graph-expansion/)

## Context and decision

Curta's old viewer can read the corrected producer's existing payload yet
silently execute the wrong carry. API 24 is a consumer capability report, not
a requirement carried by a model document. Therefore every newly exported
running program declares document v11. Its canonical identity includes
`source-timing version=11`, preventing an endpoint-era snapshot from restoring
into corrected arithmetic before any live state changes. No payload key or
expression spelling changes. Posed/looping and clocked versions stay unchanged.

The independent viewer supports v11 and corrected physics for legacy running
documents too. Re-export is the migration; lowering the version manually is
not. Old files cannot retroactively prevent old viewers from running their old
algorithm. New snapshots replay normally; old state must be reconstructed by
replaying intended commands from the model's initial state.

## Alternatives and consequences

Changing API alone does not protect portable exports. Selective versioning
would require an unproved static detector of timing-sensitive graphs. Keeping
the old identity would silently mix semantic generations. Conservatively
gating all running models changes version and identity even for affine models
whose physics is unchanged. Legacy corpus bytes remain committed controls,
with only those two fields normalized when comparing fresh publications.

Producer-owned fixtures carry source hashes and full observed results; the
viewer consumes copies without importing framework or project code. The old
API-23 bundle refuses v11 in Chromium, and API-24 worker/fallback paths pass
the unchanged full constrained Curta carry. No integration or publication is
implied by this accepted worktree decision.
