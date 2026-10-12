# ADR 0020: Use a canonical project-root model screenshot

**Status:** Accepted

**Date:** 2026-08-10

**Deciders:** Pilot

**Origin:** OpenSpec change `add-project-model-screenshots`

## Context

Project cards need a cheap, durable model preview that works for closed
repositories without making the hub mount a full functional-model viewer.
Builds and commits remain more important than preview generation.

## Decision

The shop owns one canonical preview at `<project>/screenshot.png`. It renders a
fixed 640x360 autocentred, view-all image through the selected
solid-node CLI's web renderer, which supplies a transparent background. The
shop writes the complete renderer output outside the project and atomically
replaces only a regular non-symlink target when bytes change. Successful
observed builds and floor-mediated commits request a best-effort refresh; the
commit tool then attempts to stage that exact path without delaying the commit.

Inventory carries a content revision, and the hub serves only the verified
project root's exact regular image through a dedicated route. A changed revision
is a hub-scoped metadata update; it is never conversation or broker history.

## Alternatives considered

### Serve miniature live viewers

Rejected because it would make every card expensive and could not cheaply show
closed projects.

### Store the image under `_build`

Rejected because `_build` remains the framework-owned functional-model
publication boundary.

### Gate builds or commits on preview success

Rejected because a model build and an important commit are more valuable than a
thumbnail.

## Consequences

### Positive

- Hub cards obtain a durable, cache-correct preview for open and closed projects.
- A completed image is never observed half-written.
- Agents need not remember to stage the shop-managed artifact.

### Negative and trade-offs

- A preview may be stale or absent when rendering fails.
- Commit-time refresh adds bounded rendering work.

### Neutral

- Engineering snapshots remain agent scratch and are not committed.
- Existing projects are unchanged until a successful observed build or commit.
