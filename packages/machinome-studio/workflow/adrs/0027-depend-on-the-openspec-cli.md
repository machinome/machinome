# ADR 0027: Depend on the OpenSpec CLI and refuse to start without it

**Status:** Proposed

**Date:** 2026-08-22

**Origin:** `builder-openspec-discipline`

## Context

`scoped-agent-tools` ratified runtime location independence: the shop loads its
resources from the running package or source worktree, invokes the solid-node
CLI from its own Python environment, and requires no Git checkout and no
ambient `PATH` executable to start. That requirement exists so an installed
shop can run against an arbitrary project catalogue on a machine that carries
no development workspace, and so a stray executable earlier on `PATH` cannot
change what the shop runs.

Giving Builder a durable design record means giving it OpenSpec, and OpenSpec
is distributed as a Node program. Nothing in the shop's Python environment can
supply it. Three routes were available: reimplement the grammar and lifecycle
in Python, vendor the CLI into the shop's distribution, or depend on it.

Reimplementation was rejected outright — the value is the existing grammar,
lifecycle, and its evolving toolchain, not a private dialect of it. Vendoring
is a packaging question the shop is not ready to answer: browser delivery is
under active exploration in three prototype repositories and no delivery
architecture has been chosen, so freezing a Node bundling strategy now would
likely be discarded.

The remaining question was what a missing CLI should do. A degraded mode —
open the shop, disable spec tooling — keeps a maker working when Node is
broken. It also means a Builder session silently loses the discipline, and the
Maker has no reason to notice: the parts still get built, only the record
stops accumulating.

## Decision

The shop depends on the `openspec` CLI resolved from the ambient `PATH`, and
verifies it is present and runnable before binding a listener or opening any
project. When it is absent, the shop refuses to start, naming the missing
prerequisite. There is no reduced mode.

The relaxation of runtime location independence is bounded to this one named
executable. Every other shop and backend behavior still resolves from the
running package or the shop's own Python environment, and no further ambient
dependency may be introduced without superseding this decision.

Node and `@fission-ai/openspec` become documented installation prerequisites
alongside the Python environment.

## Consequences

- A machine that can run the shop today but has no Node will stop starting
  until it installs one. That is a breaking change for such an installation,
  and it is stated rather than discovered mid-session.
- The failure is loud and early. A maker sees a named prerequisite at startup
  instead of an opaque tool error several turns into a design change.
- The shop's tests exercise the real CLI. No stand-in is maintained, so a
  behavioral change in OpenSpec surfaces as a failing shop test rather than as
  a fiction that keeps passing.
- The prerequisite applies to every profile, including makers who never do
  design work, because startup is one gate for the whole shop.
- Browser delivery inherits an open question: whichever architecture is chosen
  must supply OpenSpec or supersede this ADR. Recording it now means that
  choice is argued rather than assumed.
