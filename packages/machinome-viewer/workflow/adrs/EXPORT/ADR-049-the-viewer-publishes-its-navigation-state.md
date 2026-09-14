# ADR-049: The viewer publishes its assembly navigation state

**Status:** Accepted

**Date:** 2026-09-14

**Change:** `observe-assembly-navigation`

**Amends:**
- [ADR-042: Host-controlled viewer assembly navigation](ADR-042-host-controlled-viewer-assembly-navigation.md)

**Extends:**
- [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md)

## Context

ADR-042 gave a host three host-safe operations — read the assembly, focus
a subtree, hide a subtree — and left the navigator itself to the host. At
the time there was one host, SolidNode Studio, and it built one.

Two things have happened since.

**The widget grew its own way to move focus.** The driver chrome's
breadcrumb descends into a subassembly and returns to any ancestor
(ADR-042's assumption that the host is the only mover is no longer true;
`viewer.ts` now says so in a comment: "the ONE place focus moves, whether
the host called `setRoot` or the maker clicked the breadcrumb"). And a
targeted update (ADR-037) can discard a hidden path or reset the focused
root all by itself. Neither reaches a host, so a host-owned navigator can
be silently wrong about what the viewer is showing.

**The pilot decided the navigator belongs here** (2026-09-14). The studio's
Model panel becomes a mount of this package's navigator, and this package
ships a navigator of its own for use outside the studio. A component this
package mounts is given a handle and nothing else — no host state, no
props, no framework. Whatever it needs, the handle must answer.

Meanwhile every host pays the cost ADR-042 left it. The studio keeps its
own `focused` and `hidden` sets beside every call it makes, and rebuilds
them from a fresh `assembly()` after every update, because the viewer will
not say what survived. Two copies of one truth, kept in step by the host
remembering to.

## Decision

**Focus and visibility are published state with a change notification, on
the same host-safe API ADR-042 established.**

1. **The handle reports what it is showing.** A single read returns the
   focused root and the explicitly hidden paths, as root-relative arrays
   of sibling names — the same currency `assembly()`, `setRoot` and
   `setVisible` already speak. No document, no Three.js object, no
   filesystem path: ADR-042's boundary is unchanged, and this is more of
   the same metadata, not a widening.

2. **The document root is reported as `null`**, the value `setRoot` takes
   for it. The reported root is always a value the focus operation
   accepts, so a consumer can round-trip it. A node's own path for the
   root is still `[]`; a *focus* is either a subtree or none, and one
   spelling of that is better than two.

3. **The hidden list is what was hidden, not what is invisible.** A
   descendant made invisible by a hidden ancestor is not in it. That is
   what lets a navigator draw the difference — a part hidden on purpose
   against a part hidden by its parent — and it keeps show/hide exactly
   invertible.

4. **A subscription fires after every change, whatever moved it** — a host
   call, an affordance inside the widget, a rebuild, or a targeted update
   that reconciled the state away. It carries the fresh assembly snapshot
   and the fresh navigation state, equal to what the handle's reads return
   at that moment. It mirrors `onDriverChange`: subscribe, receive an
   unsubscribe function. The widget's own chrome is rebuilt directly by
   the operation that moved focus; the navigator this package mounts
   (the next cycle) listens on the same public channel a host does, so
   a shipped navigator and a host's own can never disagree.

5. **It is per accepted operation, not per observed difference.** The
   notification means *what you last read may be stale*; it never promises
   that something differs. A call that changes nothing still notifies —
   `setRoot` with the current path re-fits the camera and rebuilds the
   chrome, so "nothing changed" would be false — and a call refused for an
   invalid path changes nothing and notifies nobody. The viewer does not
   owe hosts a diff.

6. **Once per operation, at the end of it.** A targeted update notifies
   once, after the viewer has reconciled, updated and rendered, and before
   its promise settles. Mounting notifies nobody, because no listener can
   exist before the handle does. Disposal releases every subscription, and
   a listener cancelled while a notification is being delivered does not
   receive it — a navigator unsubscribing in its own teardown is the
   ordinary case, not an edge one.

7. **A host may still build its own navigator**, on exactly this channel.
   ADR-042 is amended in its ownership claim, not in its boundary: the
   package will ship a navigator (the next cycle) because most hosts want
   one, and a host that wants a different one has strictly more to build
   it with than it had before.

The declared API version rises from 8 to 9: a capability a host may
require has been added to the handle, which is the rule ADR-035 set for
the number.

## Consequences

- A navigator can be a component of this package. Given only a handle it
  renders the tree, shows what is focused and what is hidden, and stays
  correct when something else moves the state — which is the whole reason
  the next cycle can exist.
- A host stops mirroring. The studio's parallel `focused`/`hidden` sets
  and its manual re-derivation after each update become one read and one
  subscription, and then, in the shop cycle, nothing at all.
- The breadcrumb and a navigator agree by construction, because both read
  the same published state rather than two copies of it.
- The viewer owes a notification per operation forever, including for
  calls that change nothing. A consumer must be idempotent under a
  redundant notification; a rebuild from a snapshot is.
- A listener that drives the viewer can loop. The viewer cannot prevent it
  without dropping notifications, so the contract says plainly that a
  listener observes.
- The snapshot walks the whole tree per notification. That is per gesture
  or per republish, never per frame; any future per-frame source must not
  use this channel.

## Alternatives considered

**Leave the navigator with the host (ADR-042 unchanged).** It is the
status quo and it has a real cost: every host reimplements colour
inheritance, path handling, keyboard semantics and reconciliation, and
none of them can see a focus change the widget made. The pilot's decision
settles the direction; this record settles the mechanism.

**Expose the Three.js scene and let a navigator read it.** Rejected for
the same reason ADR-042 rejected it: renderer internals would become a
public compatibility contract, and a consumer could violate lifecycle
safety. The state a navigator needs is small, serializable and already
computed.

**Per-node events** (`onNodeHidden(path)`, `onFocusChanged(path)`). A
republish that reconciles several nodes at once would have to emit them in
some defined order, the viewer would owe that order forever, and a
consumer would rebuild from the whole tree anyway.

**Carry a reason on each change** (`'focus' | 'visibility' | 'tree'`) so a
consumer can skip work. It invites a taxonomy with no honest answer for a
republish that also reset the root, to save a redraw nobody measured.

**Keep state in the host and have it poll.** Polling a tree walk per frame
for a state that changes per gesture is the wrong shape, and it still
cannot tell a host *when* — which is what a navigator needs to stay in
step.

## References

- `solid_node_viewer/widget/src/assembly.ts` — `AssemblyNavigation`, the
  state and the notifier
- `solid_node_viewer/widget/src/viewer.ts` — the handle, `focusOn` and the
  five moments the state can move
- `solid_node_viewer/widget/src/drivers.ts` — `onDriverChange`, the
  listener pattern this mirrors
- `openspec/changes/observe-assembly-navigation/`
- [ADR-037: Targeted in-place viewer updates](../VIEWER-WEB/ADR-037-targeted-in-place-viewer-updates.md)
