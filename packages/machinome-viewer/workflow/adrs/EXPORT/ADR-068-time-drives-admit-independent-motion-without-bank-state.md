# ADR-068: Time drives admit independent motion without bank state

**Status:** Accepted

**Date:** 2026-09-20

**Change:** [execute-running-time-drives](../../../openspec/changes/execute-running-time-drives/)

**Authority:** The pilot's instruction to implement viewer support next,
consuming the accepted producer contract; no new authoring interface.

**Extends:**
- [ADR-045: The run executes in a worker](ADR-045-the-run-executes-in-a-worker.md)
- [ADR-047: The corpus makes the two runtimes one algorithm](ADR-047-the-corpus-makes-the-two-runtimes-one-algorithm.md)

**Preserves:**
- [ADR-067: A play edge retains contact history](ADR-067-a-play-edge-retains-contact-history-in-the-running-bank.md)

**Consumes:** machinome ADR-133: Running time drives — retained motion with independent admissions.

## Context

Astrarium's diagnostic mechanism now runs, stops, winds and restarts with the
framework's explicit time drive. Its version-10 export cannot mount in the
version-9 viewer. A synthetic browser rate command would replace the machine's
declared behavior rather than execute it. A shared time admission would couple
independent trains at their stops.

## Decision

Validate the ordered `program.time_drives` mappings against the original edge
list before block contraction, attaching each admission ID to its mapped law.
Time stays a source-only clock named `time`; neither clock nor admission IDs
are physical state, inputs or computed coordinates.

Each advancing tick admits `dt` separately per mapped relation. Evaluation
substitutes that relation's admitted local clock path into its laws and jump
plans. A stopped relation holds its admitted endpoint for the rest of the tick;
the next tick retries from current global time without a backlog. Operator
commands and other time drives remain independent. Instant operator moves
admit zero time. No additional state is saved or restored.

Locate time-driven downstream stops by replaying original source admissions,
not by interpolating a nonlinear follower's endpoint delta. Use the existing
subdivision, bisection and agreement limits. Stop records keep real inputs in
`inputs` and include sorted `time_drives` only when nonempty. Existing no-time
programs retain their execution paths and record shape. Play remains restricted
to its existing driver-rooted linear chains.

Worker and fallback share the engine. Astrarium's browser test also exposed a
pre-existing transport defect: an instantaneous move retired without reporting
the committed bank to a paused host. Send its existing frame notification before
the outcome, with no new message or public method.

The producer's seven-machine, 54-step corpus is copied unchanged and replayed
under its own numeric contract. A separate committed Astrarium export exercises
both browser transports and rendered motion without importing the framework.

Viewer API becomes 23; supported documents become 1–10. Package 0.2.0 remains
unreleased. The manual describes this architecture and its kinematic limits.

## Consequences

Astrarium's capability fixture is browser-operable without a startup command;
its historical reconstruction is still separate, unfinished project work.
Independent trains can stop and retry correctly, nonlinear time laws use global
elapsed time rather than a hidden resumable phase, and saved state retains its
existing shape. This adds no physics, inferred energy or expanded Play topology.
