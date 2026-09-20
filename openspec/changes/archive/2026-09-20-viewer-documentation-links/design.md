## Context

Standalone maintainer documentation work, not sprint work. Base is framework
primary `main` at `4d747191f8a94cb72fa3a4bef23a9742b91f0acf`. The shop opened
`machinome/WTs/viewer-documentation-links` with `scripts/dev-env`; its branch is
`viewer-documentation-links`. Integration target is framework `main`, requiring
separate pilot authority. The viewer owns its API/manual under its independent
`user-documentation` change. ADR-068's process/licensing boundary is unchanged.

## Goals / Non-Goals

**Goals:** Make the viewer manual discoverable from the framework and correct
the clocked move/trigger distinction beside the new reference link.

**Non-Goals:** Remove the existing framework embedding surface, change behavior
or dependencies, introduce an architectural decision, integrate or publish.

## Decisions

- Add direct HTTPS links to the intended Read the Docs project, including
  specific operating/embedding/reference pages. Do not copy the independent
  manual into the framework or add a build-time dependency on its hosted site.
- Keep framework-facing explanations and examples intact, and explain that
  direct clocked moves land immediately but instruction triggers draw a
  transition. This is correction against the viewer source, not new behavior.
- Verify links against the local viewer HTML build and build the framework
  manual strictly. Reuse existing generated example exports read-only for
  unrelated framework examples; no CAD rebuild is required for a link change.

## Risks / Trade-offs

- [RTD slug not yet configured] → Record one-time hosting setup separately;
  local build/link checks are not a claim that a remote deployment exists.
- [Other standalone changes share the same base] → Do not integrate, rebase or
  combine them without pilot authority. Mechanics links are already archived
  on their separate branch; this branch does not absorb those changes.

No ADR is needed: neither architecture nor a public runtime interface changes.
