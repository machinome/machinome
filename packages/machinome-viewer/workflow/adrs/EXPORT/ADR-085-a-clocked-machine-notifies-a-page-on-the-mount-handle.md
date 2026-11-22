# ADR-085: A clocked machine notifies a page of a changed bank or drawing, on the mount handle

**Status:** Accepted

**Date:** 2026-11-22

**Change:** [show-a-models-own-app](../../../openspec/changes/archive/2026-11-22-show-a-models-own-app/) (design Decision 6)

**Extends:** [ADR-064: A clocked instruction is one request, drawn over its duration](ADR-064-a-clocked-instruction-is-one-request-drawn-over-its-duration.md)
(the bank commits at the request; the drawing catches up)

**Builds on:** [ADR-049: The viewer publishes its assembly navigation state](ADR-049-the-viewer-publishes-its-navigation-state.md)
(the change notification: what it means, and that it observes)

## Context

A page could not learn when a clocked machine's committed bank changed or
when a drawn transition ended. `machine()` returns a fresh wrapper over the
machine standing at the call, so a subscription on it would be lost to a
republish that rebuilds the machine. An app's keyboard needs both facts,
whoever moved the machine.

## Decision

**`ViewerHandle.onMachineChange(listener)` calls the listener with no
argument, once, after every accepted operation that changes the committed
bank or starts or ends a drawn transition, whoever made it; and
`MachineHandle.drawing()` answers whether a transition is drawn now.**

1. **Once per operation.** Every door that can change the bank or a drawing
   runs inside one nesting operation; the pose hook marks an accepted pose
   that moved an id, and a drawing is marked where it starts, lands or
   reaches its last frame; the outermost operation notifies once at its end,
   after its panel is written. A gesture that lands a drawing and makes a
   request notifies once; a frame notifies at most once; an accepted request
   that moves nothing notifies nobody.
2. **Never for a refusal.** A refused request marks nothing.
3. **On the mount.** The subscription survives a republish that replaces
   the machine. A load or republish notifies when it builds, rebuilds or
   keeps the machine, and, as decided in the implementation, **also when it
   removes the machine**: the page then reads `machine()` as null, which
   is what the notification exists to say. A document that never carried a
   machine never notifies.
4. **The doctrine of ADR-049.** It means "what you last read may be stale";
   it carries no value; a throwing listener does not stop the others; a
   listener must not drive the viewer from inside it; `dispose()` drops
   every listener and notifies nobody.

## Alternatives

- **A listener receiving the bank:** a copy per notification, wanted or not.
- **Per-frame notification of the shown bank during a drawing:** sixty
  renders a second an app does not need.
- **`onChange` on `MachineHandle`:** lost on republish; the mutation that
  does this turns M5 red.

## Consequences

- Viewer API 31. A page with no listener pays a loop over an empty set per
  operation.

## Proof

`src/machine-change.test.ts` (M1 to M8) and the mutations of the change's
`evidence.md` (no notice at the last frame, a notice for a refusal, the
subscription on the machine: each red).
