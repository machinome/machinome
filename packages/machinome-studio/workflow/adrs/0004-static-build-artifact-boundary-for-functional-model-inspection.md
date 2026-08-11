# ADR 0004: Use published build artifacts as the functional-model boundary

**Status:** Accepted — the artifact boundary stands; the callback refresh
mechanism is superseded by [ADR 0010](./0010-shop-owned-model-watcher.md), and
the source-serving clause is amended by
[ADR 0021](./0021-serve-verified-project-source-as-inert-editable-text.md)

**Date:** 2026-07-20

**Origin:** Sprint 001, STORY-005 — Inspect the functional model

## Context

Shop-floor is long-lived while a project's conventional model is Python code
that changes during machining. Importing that model into floor would cache
module state, make reload behaviour unreliable, and couple the browser service
to project execution.

`solid build <project-local-model-path>` atomically publishes a completed
`_build` directory containing `viewer.json` and the model files it references.
`solid develop <project-local-model-path> --callback URL` sends an empty POST
only after a successful replacement of that complete directory; failed rebuilds
retain the preceding build and send no callback.

## Decision

Floor SHALL treat the completed `_build` directory as its only functional-model
input. It serves the viewer snapshot and referenced model files to the browser
and uses the development callback solely as a signal to reload that static
output.

Floor SHALL NOT import, execute, reload, inspect, or serve project Python
source. Project Python execution belongs only to the `solid build` subprocess
and the framework-owned `solid develop` process.

**Amendment (2026-08-11).** [ADR 0021](./0021-serve-verified-project-source-as-inert-editable-text.md)
permits Floor to list, read, and atomically replace verified project source as
inert text for the Code workspace. Floor still does not import, interpret, or
execute that source, and `_build` remains the only functional-model input.

**Amendment (2026-08-02, Sprint 002).** Floor obtains the framework's static
browser viewer through `solid viewer` during preparation and serves that one
bundle to the browser. It remains separate from project artifacts and does not
weaken this boundary: Floor neither imports nor executes project Python.

The framework viewer renders the served snapshot and model artifacts. The
backend does not interpret the snapshot or execute any model code.

## Consequences

- The visible model is always derived from a complete CLI publication.
- Floor does not need Python-module invalidation or project-runtime lifecycle
  management.
- A failed later build leaves the prior inspectable result available.
- Floor implementation and tests must exercise static `_build` serving and
  callback-driven browser refresh without importing a project model.
