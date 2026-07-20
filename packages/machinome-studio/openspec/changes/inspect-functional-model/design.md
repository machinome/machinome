## Context

The FastAPI floor is a long-lived broker, while a project model is Python code
that the machinist changes during a run. Importing the model in the broker
would cache the module and makes the visible model stale. The existing browser
workspace has an artifact pane but no functional-model content.

The installed `solid` CLI currently exposes neither a one-shot build command
nor a development callback option. This shop change therefore supplies the
originating-project requirement for a linked solid-node change; its exact
public command, artifact format, and callback protocol remain unratified.

## Goals / Non-Goals

**Goals:**

- Treat the project-root `__init__.py` as the conventional model entry point.
- Have the floor use a one-shot solid CLI build before reporting the shop open.
- Keep project Python execution outside the floor process.
- Reuse the solid-node frontend widget in the floor artifact area and provide
  the model-serving endpoints that widget consumes.
- Refresh the visible model after the machinist's development process reports
  a successful change to the broker.
- Let the browser recover using a complete current model state when a refresh
  occurs.

**Non-Goals:**

- Define the solid-node CLI syntax, artifact serialization, or callback
  payload; those belong to the linked framework change.
- Implement delta/state-patch delivery; a complete state reload is sufficient.
- Support arbitrary model entry-point paths, project browsing, or design
  process observability.
- Load or execute a project model inside the floor service.

## Decisions

### The floor owns model lifecycle, not model execution

The porter/floor-open path will locate `<project-root>/__init__.py` and invoke
the framework-provided one-shot build command as a subprocess. The framework
command must either produce the serving input for the floor or exit cleanly
with a useful missing-model result. The floor stores and serves only the build
result; it does not import the model.

An in-process import was rejected because Python module caching makes an
updated model unreliable without restarting the broker. A persistent child
interpreter was also rejected: it adds lifecycle and isolation concerns while
still creating a long-lived model runtime.

### A framework-owned adapter is the cross-repository seam

This change requires the solid-node framework to provide two capabilities:

1. a one-shot build of the conventional entry point; and
2. a development invocation that accepts a floor-broker callback location and
   notifies it after an updated build is ready.

The exact command names, arguments, output location/data, delivery method,
authentication, and event schema are intentionally open. Floor code will
isolate those details behind a small adapter rather than spread a provisional
CLI protocol across lifecycle, broker, and frontend code. The future framework
OpenSpec change is the authority for that public contract.

Using existing `solid develop` without a callback was rejected because it
cannot notify the floor deterministically. Polling project files was rejected
because it duplicates framework change detection and cannot establish that a
new model is successfully built.

### The floor hosts the solid-node viewer widget and its model endpoints

The artifact area will embed or otherwise reuse the frontend widget provided
by solid-node. The floor will implement the endpoints the widget needs to
obtain the current model; it remains the local owner of browser-session and
broker lifecycle, rather than redirecting the maker to a separate framework
web server.

Reimplementing the viewer was rejected because it would duplicate the
framework's model inspection surface. Importing or hosting framework server
internals was rejected because the floor needs a stable public integration
boundary; the widget's endpoint contract will therefore be captured alongside
the linked framework CLI/callback contract.

### The broker turns build-ready notifications into SSE refresh events

The broker exposes a local callback endpoint for the framework development
process. Once it accepts a valid build-ready notification, it updates its
model snapshot/reference and publishes a model-changed event on the existing
run SSE stream. The browser responds by fetching the complete current
functional-model state and replacing the artifact view.

Delta payloads are deferred. Full-state reload is robust across an interrupted
browser connection and does not constrain the future framework artifact
representation.

## Risks / Trade-offs

- [Framework API is not yet defined] → Leave CLI and callback shapes as an
  explicit linked dependency; do not begin implementation until its contract
  is ratified.
- [A build fails after a previously usable model] → Preserve the last
  successfully built state and surface the failure through the floor rather
  than presenting a partially updated model.
- [Local callback is invoked by an unintended process] → The eventual
  framework/floor protocol must use a per-run, unguessable local capability or
  equivalent validation; exact mechanism is an open framework-interface
  decision.
- [Full reload is expensive for large models] → Start with it as the correctness
  baseline; introduce deltas only when evidence shows they are needed.

## Migration Plan

1. Ratify this shop proposal as the originating-project requirement.
2. Establish and implement the linked framework CLI/callback contract in its
   own solid-node change.
3. Implement the floor adapter, widget-compatible model endpoints, broker
   endpoint/SSE event, and workspace view against that ratified contract.
4. Verify initial build, missing-model failure, and a machinist-triggered
   refresh in an isolated project fixture.

Rollback removes the floor integration and retains the existing shop workspace;
no project model is imported or persisted by the floor.

## Open Questions

- What stable CLI commands, arguments, exit categories, and build-result
  representation will the solid-node framework publish?
- What callback request schema and local authentication/capability mechanism
  will bind a `solid develop` process to one floor run?
- What public widget integration and model-serving endpoint contract will
  solid-node publish for a host such as floor?
