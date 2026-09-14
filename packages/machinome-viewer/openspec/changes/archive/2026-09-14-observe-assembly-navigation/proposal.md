## Why

The pilot decided on 2026-09-14 that the assembly navigator — the tree a
maker reads a machine's parts off, focuses a subassembly from, and hides
obstructing parts in — becomes a component of **this** package. The studio
mounts it; an export page mounts it; anything holding a handle mounts it.
This change is the first of the three viewer cycles that move it, and it
moves no pixels: it publishes the state such a component has to read.

ADR-042 put the navigator in the host. The viewer keeps focus and
visibility internally (`src/assembly.ts:13-62`), reconciles them across a
targeted update (`viewer.ts:505`, `:789`, `:804`) and lets a host *change*
them (`setRoot`, `setVisible`, `viewer.ts:819-828`) — but it publishes
neither the state nor a notification that it moved. Two consequences,
both visible today:

1. **Every host mirrors the viewer's state by hand.** The studio's
   `AssemblyPanel` keeps its own `focused` and `hidden` sets
   (`floor/frontend/src/main.tsx:299-302`), writes them beside every
   `viewer.setRoot` / `viewer.setVisible` call (`:340-353`), and re-derives
   them from a fresh `assembly()` after every update (`:306-326`) because
   the viewer will not say what survived reconciliation. Two copies of one
   truth, kept in step by the host remembering to.

2. **A change the host did not make is invisible to it.** The driver
   chrome's breadcrumb moves focus from inside the widget — "the ONE place
   focus moves, whether the host called `setRoot` or the maker clicked the
   breadcrumb" (`viewer.ts:548-560`) — and a targeted update can discard a
   hidden path or reset the focused root (`assembly.ts:44-57`). Neither
   reaches the host. A mirrored navigator is then simply wrong: it shows a
   root the viewer no longer has.

A navigator that lives in this package cannot be handed the host's
bookkeeping, because there is no host. It is given a handle and nothing
else, so the handle must answer two questions it cannot answer today:
*what is focused and what is hidden*, and *when did that last change*.

This cycle adds exactly those two answers. The navigator itself is the
next cycle.

## What Changes

- **The handle publishes its navigation state.** `navigation()` returns
  `{ root, hidden }`: the focused root as a root-relative path of sibling
  names or `null` for the published document root — the same `null`
  `setRoot` takes and the breadcrumb already uses (`viewer.ts:1250-1253`)
  — and the paths a host or the widget has explicitly hidden, each a path
  of the same shape. The snapshot is serializable and is a copy: a later
  change does not rewrite one a caller is holding.

- **The handle publishes a change subscription.** `onAssemblyChange(listener)`
  returns an unsubscribe function, exactly as `onDriverChange` does
  (`viewer.ts:837-838`, `drivers.ts:214-217`). The listener is called with
  `{ assembly, navigation }` — the same values `assembly()` and
  `navigation()` return at that moment — after every accepted operation
  that publishes a tree or moves focus or visibility, **whatever moved
  it**: a host call, the widget's own breadcrumb, `reload()`,
  `artifactChanged()` or `manifestChanged()`.

- **Once per operation, never before there is a host, never after
  dispose.** A targeted update notifies once, after the viewer has
  reconciled and rendered and before its promise settles. Mounting never
  notifies — no listener can exist before the handle does. `dispose()`
  drops every listener, as `drivers.dispose()` already does
  (`drivers.ts:286-292`).

- **A call that changes nothing still notifies; a refused call does not.**
  The subscription says *the state you last read may be stale*, never *the
  state definitely differs* — see design D4. `setRoot(['missing'])` throws
  from `tree.requirePath` (`tree.ts:349-360`) before any state moves, and
  notifies nobody.

- **The declared API version rises from 8 to 9.** A capability a host may
  require is added to the handle, which is exactly what the version exists
  to say. The studio will gate on `>= 9` in the shop cycle.

- **Nothing renders.** No UI, no layout, no new published file, no change
  to what `solid export` and the Sphinx directive copy, no framework
  change. `assembly()`, `setRoot`, `setVisible` keep their signatures and
  their meaning.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-assembly-navigation`: two new requirements — a host reads the
  viewer's navigation state, and a host is told when the assembly or its
  navigation changes.
- `viewer-package`: one modified requirement — the declared API version
  becomes 9, for the capability added to the handle.

Capabilities needing no delta:

- `viewer-distribution`: no published name, route or file changes. The
  bundle gains no file; the export copies exactly what it copies today.
- `development-server`, `snapshot-capture`: neither reads the handle's
  navigation state, and the reload path already goes through
  `manifestChanged()`.

## Impact

- `solid_node_viewer/widget/src/assembly.ts` — `AssemblyNavigation` gains
  a state read (`hidden()` beside the existing `root()`), and a small
  `AssemblyChangeNotifier` is added beside it: subscribe, notify, dispose.
  Both are pure and both are reachable by `assembly.test.ts`, which is
  where their semantics are pinned.
- `solid_node_viewer/widget/src/viewer.ts` — `navigation()` and
  `onAssemblyChange()` on the handle and on `ViewerHandle`; one `notify`
  call at the end of each of the five operations that can move the state
  (`focusOn`, `setVisible`, `reload`/`replaceTree`, `artifactChanged`,
  `manifestChanged`); the notifier disposed with everything else. Which
  moment fires stays in `viewer.ts`, beside the comment that already says
  there is one place focus moves.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi: 9`.
- `solid_node_viewer/widget/src/version.test.ts`,
  `tests/test_widget_e2e.py`, `tests/test_running_document.py`,
  `tests/test_bundle.py` — the four places that assert the number 8.
- `tests/test_widget_e2e.py` — the end-to-end guarantee against the real
  bundle: `viewer.ts`'s mount has no unit test to live in (vitest runs
  with no DOM here), so the notification's sources, its once-per-operation
  batching and its read-after-fire equality are proved in Playwright.
- `README.md` (the version table's unreleased `0.2.0` row), `CHANGELOG.md`
  (the same unreleased `0.2.0` section), and
  `docs/adrs/EXPORT/ADR-049-…` with its index row.
- **Consumed by** `mount-the-navigator` (viewer cycle 2) and
  `adopt-the-viewer-navigator` (shop cycle 4). Nothing in this repository
  depends on it yet, which is deliberate: it is observation, and it is
  correct or not on its own.
