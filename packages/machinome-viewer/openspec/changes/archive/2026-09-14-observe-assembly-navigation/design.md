# Design — observe assembly navigation

## Context

This is cycle 1 of the pilot's 2026-09-14 decision that the assembly
navigator moves into this package. Cycle 2 mounts a plain-DOM navigator
given only a handle; cycle 3 composes it into a shipped layout; the shop
cycle deletes the studio's copy. This cycle adds **nothing a maker can
see**. It publishes the two facts such a navigator needs and cannot get:
the state, and the moment it moved.

What exists:

- `AssemblyNavigation` (`src/assembly.ts:13-62`) holds `focusedPath:
  string[] | null` and `hiddenPaths: Map<key, string[]>`, applies them to
  the tree through `tree.applyVisibility` (`tree.ts:362-375`), and
  reconciles them against a republished tree (`assembly.ts:44-57`),
  returning whether the focused root was reset. It already exposes
  `root()` and `isVisible(path)` — to `viewer.ts`, not to a host.
- `viewer.ts` owns every moment the state can move: `focusOn`
  (`:548-560`, "the ONE place focus moves, whether the host called
  `setRoot` or the maker clicked the breadcrumb"), `setVisible`
  (`:822-828`), `replaceTree` (`:505`, reached by `mount` and `reload`),
  `artifactChanged` (`:786-791`) and `manifestChanged` (`:793-812`).
- `drivers.ts` already carries the listener pattern this change mirrors:
  `onDriverChange` returning an unsubscribe (`:214-217`), a private
  `announce` over a snapshot of the set (`:310-314`), and a `dispose()`
  that clears it (`:286-292`). The viewer subscribes to its own public
  channel rather than reaching into the store (`viewer.ts:709-714`), and
  the comment there says why: "no private path into the store".

The shape of this change is that last idea again. A navigator mounted by
this package will read the handle the way any host reads it, so the
on-screen navigator and a host's own can never disagree.

## 1. What is published

### D1. `navigation()` returns the whole inspection state, as a copy

```ts
export interface AssemblyNavigationState {
  /** The focused subtree, or `null` for the published document root. */
  root: string[] | null;
  /** Explicitly hidden paths, each root-relative. */
  hidden: string[][];
}

navigation(): AssemblyNavigationState;
```

One read, not three (`root()`, `hidden()`, `isVisible(path)`), because a
navigator renders a whole tree from one consistent picture and because a
snapshot can be compared, stored and logged. `assembly()` already answers
"what is there"; `navigation()` answers "how is it being looked at". The
two are separate because the tree changes for one reason (the document)
and the navigation state for another (the maker).

Both fields are **copies**: `AssemblyNavigation` already copies in
`root()` (`assembly.ts:17-19`), and `hidden` is built fresh from the map's
values. A caller holding a snapshot is holding a value, not a window into
the widget.

`navigation()` does not need the tree and therefore does not throw when
`assembly()` would (`viewer.ts:813-818`). After a successful mount the
tree always exists, so the distinction is invisible in practice; the
reason to keep it is that a state read should not have a failure mode.

### D2. The document root is `null`, not `[]`

`setRoot(null)` restores the document root, and the breadcrumb inside the
widget already converts for exactly this reason: "The document root is
`null` to the focus API, not an empty path" (`viewer.ts:1250-1253`).
Reporting `[]` would give the handle two spellings of one state and make
`navigation().root` unusable as an argument to `setRoot`. So:

> `navigation().root` is always a value `setRoot` accepts, and
> `setRoot(navigation().root)` is a no-op in meaning.

The node it names is then `assembly()` itself, whose own `path` is `[]`
(`tree.ts:330-338`) — the one asymmetry, stated in the spec and worth its
cost: a *node's* identity is a path and the empty path is the root node;
a *focus* is either "a subtree" or "none".

*Alternative that lost:* report `[]` and make `setRoot` accept it too.
That is two spellings for one state in an API a host gates on by version,
and it invites a navigator to compare `root` against a node path with
`===` on stringified values and get the root wrong.

### D3. `hidden` lists what was hidden, not what is invisible

The map holds the paths a caller explicitly hid; a descendant of a hidden
node is not in it, and `tree.applyVisibility` derives the rest
(`tree.ts:362-375`). Publishing the explicit set is what lets a navigator
draw a checkbox that is *checked but greyed* under a hidden ancestor —
the studio's semantics today (`main.tsx:346-353` keeps exactly this set)
— and what makes `setVisible(path, true)` on a listed path the exact
inverse of what hid it.

The list contains only paths the current tree still has, because
`reconcile` drops the others (`assembly.ts:50-55`). Its **order is not
part of the contract**: the implementation yields insertion order, and a
consumer keys by path.

## 2. When it fires

### D4. One subscription, one meaning: "what you read may be stale"

```ts
export interface AssemblyChange {
  assembly: AssemblyNode;
  navigation: AssemblyNavigationState;
}
export type AssemblyListener = (change: AssemblyChange) => void;

onAssemblyChange(listener: AssemblyListener): () => void;
```

The listener receives both snapshots, equal to what `assembly()` and
`navigation()` return when it runs, so a navigator never has to call back
into the handle to redraw — and a host that prefers to may, and gets the
same values.

The event is **per accepted operation**, not per observed difference. A
`setVisible(path, true)` on a path already visible notifies; so does
`setRoot` with the currently focused path; so does a `manifestChanged()`
that republishes an identical document. Three reasons:

1. `setRoot` with the current path is not a no-op *in the viewer*:
   `focusOn` re-fits the camera and rebuilds the chrome unconditionally
   (`viewer.ts:552-560`). Calling that "nothing changed" would be false.
2. Suppressing duplicates makes the viewer define equality over paths and
   over a published tree — a deep comparison per operation, for a
   consumer that re-renders idempotently anyway.
3. A rule a host can state in one sentence ("every accepted call tells
   me") is one it can reason about; "sometimes, if something differed"
   is not.

A navigator therefore must be idempotent under a redundant notification,
which a rebuild from a snapshot is. What it must **not** do is write back
into the handle from inside the listener; the spec says the listener
reads, and cycle 2's navigator does.

*Alternative that lost:* carry a `reason` (`'focus' | 'visibility' |
'tree'`) so a consumer can skip work. It invites a taxonomy the viewer
would then owe forever — what is the reason for a republish that also
reset the root? — for a saving a navigator does not need.

*Alternative that lost:* per-node events (`onNodeHidden(path)`). The
state is small and whole-tree; per-node events would have to be emitted
in a defined order on a republish that changed several at once, and a
consumer would still rebuild.

### D5. Exactly one notification per operation, at the end of it

`viewer.ts` decides the moment, as it already decides that there is one
place focus moves. Each of the five operations fires exactly once, after
the viewer has finished — navigation reconciled, tree updated, chrome
rebuilt, frame rendered — and, for the asynchronous ones, **before the
promise settles**:

| operation | fires |
| --- | --- |
| `setRoot(path)` / the breadcrumb | once, at the end of `focusOn` |
| `setVisible(path, visible)` | once, after the render |
| `reload()` | once, at the end of `replaceTree` |
| `artifactChanged(path)` | once, after `reconcile` and the render |
| `manifestChanged()` | once, after `reconcile`, `refreshControls` and the render |

A targeted update that reconciles away a hidden path or resets the
focused root (`assembly.ts:44-57`) is one of those, not an extra one: the
listener is told once and reads the reconciled state.

**Mount never notifies.** `replaceTree` runs inside `mount()` before the
handle exists (`viewer.ts:707`), so no listener can be registered to
receive it. That is a property of the construction, not a flag, and the
spec states it as the guarantee a host relies on: the initial state is
read, not awaited.

**Dispose ends it.** `dispose()` clears the listener set beside
`drivers.dispose()` (`viewer.ts:757-784`), so nothing fires afterwards,
and the unsubscribe function a host still holds stays safe to call.

### D6. Dispatch is defensive where `drivers.ts` is not

`announce` iterates a copy of the set (`drivers.ts:310-314`), so a
listener removed *during* a dispatch is still called. For a navigator
that unsubscribes in its own `dispose()` that is a live handle called
after teardown, so the notifier here checks membership as it goes: a
listener unsubscribed during a notification is not called for that
notification, and one added during it is not called either (it will hear
the next one).

A listener that throws does not stop the others and does not escape into
the caller of `setRoot`: the exception is reported to `console.error` and
the loop continues. A host's bug in a tree renderer must not leave the
viewer half-focused — and the caller of `setVisible` never asked to catch
someone else's listener.

*Not adopted:* changing `drivers.ts` to match. It is a different channel
with a different call rate, its behaviour is specified and tested as it
is, and widening this cycle to touch the driver store buys nothing.

## 3. Where the logic lives so a test can reach it

`viewer.ts`'s mount has no unit test: vitest runs here with no DOM
environment (no jsdom, no happy-dom in `package.json`), which is why
`controls.ts` and `runControls.ts` exist as pure deciders beside it. The
same split applies:

- **`assembly.ts`** gets the state read and a small
  `AssemblyChangeNotifier` (subscribe → unsubscribe, `notify(change)`,
  `dispose()`). Everything decidable without a DOM is decided there and
  pinned in `assembly.test.ts`: the state's shape and copies, the `null`
  root, explicit-hidden-only, reconciliation's effect on the state,
  unsubscribe, unsubscribe-during-dispatch, a throwing listener, and
  silence after dispose.
- **`viewer.ts`** keeps the *when*: five call sites, one each. No
  notification is emitted from inside `AssemblyNavigation`, deliberately —
  `reconcile` runs mid-update (`viewer.ts:804`, before `tree.update` and
  `refreshControls`), and a listener that fired from there would see a
  half-settled widget.
- **`tests/test_widget_e2e.py`** proves the wiring against the real
  bundle in Chromium: that each of the five sources notifies, that a
  targeted update notifies once, that the values read inside the listener
  equal `assembly()`/`navigation()` after it, that an invalid path
  notifies nobody, and that dispose silences it.

## 4. The version

8 → 9. The rule is the spec's own: raised "when a capability a host may
require is added to the handle". A navigator — this package's, in cycle
2, or a host's own — requires it and can check for it before mounting,
which is the whole purpose of the number. `0.2.0` is unreleased, so the
README table's existing `0.2.0` row moves to 9 rather than gaining a row.

## 5. Risks

1. **A listener that drives the viewer.** Nothing stops a host calling
   `setRoot` from inside `onAssemblyChange` and looping forever. The
   viewer cannot prevent it without dropping notifications, which is
   worse. Mitigated by saying plainly, in the spec and the README, that a
   listener observes; and by the fact that cycle 2's navigator calls the
   handle only from a maker's gesture.
2. **Snapshot cost per notification.** `tree.assembly()` walks the whole
   tree (`tree.ts:330-338`). It fires per *operation* — a click, a
   republish — never per frame, so the cost is the cost the studio
   already pays after every update (`main.tsx:190`). If a future
   fine-grained source ever fires per frame, it must not use this
   channel.
3. **A host holding a stale snapshot.** `assembly()` returns a fresh
   object each call and the old one is never updated in place. That is
   already true; publishing a second snapshot makes it twice as easy to
   hold one too long. Stated in the spec: a snapshot is a value.

## 6. Open questions

1. **Should `navigation()` also report the effective visibility of a
   path** (`isVisible`, ancestors included)? A navigator computes it from
   `hidden` in three lines, and publishing it would be a second way to
   ask one question. Left out; cycle 2 will say whether it wanted it.
2. **Should a change carry the previous state?** A diffing consumer could
   use it. No consumer in the campaign needs it, and it doubles what the
   viewer must retain. Left out.
3. **Does the studio's "Show full assembly" button belong to the
   navigator or to the layout?** Cycle 2's question, recorded here because
   the state it reads (`root !== null`) is this cycle's.

## 7. The ADR to extract

- **ADR-049 (EXPORT): The viewer publishes its assembly navigation
  state.** Amends ADR-042. The decision that focus and visibility are
  *published* state with a change subscription, over the same host-safe
  API — serializable paths, no Three.js, no document — so a navigator
  needs only a handle; that the notification is per accepted operation and
  says "what you read may be stale"; that the document root stays `null`
  on the way out as it is on the way in; and that hosts may still build
  their own navigator on exactly the same channel the package's own uses.
  Beside ADR-035's declared API version, which moves to 9.
