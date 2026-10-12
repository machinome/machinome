## Context

The shop's Model context panel is a React tree written against the viewer's
imperative handle. `AssemblyPanel` (`floor/frontend/src/main.tsx:295-440`)
flattens `viewer.assembly()` into rows, keeps four pieces of local state
(`active`, `focused`, `hidden`, `expanded`), reconciles all four against every
republished tree (`:306-326`), implements the roving tab stop and the
Up/Down/Left/Right/Enter/Space contract (`:352-382`), and drives the viewer with
`setRoot` / `setVisible`. It is fed by `FunctionalModel`, which calls
`onAssemblyChange(mounted.assembly())` after every mount and every update
(`:190`, `:219`, `:237`) into the workspace's `assembly` state (`:1710`), and by
`onViewerChange` into `viewerHandle` (`:1709`). `styles.css:166-191` paints it.

The viewer package no longer needs a host to do that. Its `viewer-navigator`
branch ships, at API 10:

- `handle.navigation(): { root: string[] | null, hidden: string[][] }` and
  `handle.onAssemblyChange(listener) => unsubscribe`, firing once per accepted
  operation with the fresh `{ assembly, navigation }` (ADR-049,
  `widget/src/viewer.ts:142-152`, `widget/src/assembly.ts:20-23, 88-93`).
- `SolidNodeWidget.mountNavigator(target, viewer, options?): NavigatorHandle`
  (ADR-050, `widget/src/navigator.ts:212-526`), a plain-DOM navigator that draws
  the whole tree **synchronously before returning**, redraws from every
  notification, holds only its own expansion and active row, and carries the
  entire behaviour the shop's `assembly-navigation` spec describes — including
  its own "Show full assembly" toolbar (`navigator.ts:275-290`).
- One injected stylesheet `#solid-node-navigator-style` with a published class
  contract (`solid-nav`, `solid-nav-row` and its `--root`/`--hidden`/
  `--obscured`/`--leaf` modifiers, `solid-nav-twisty`, `solid-nav-visibility`,
  `solid-nav-name`, `solid-nav-badge`, `solid-nav-focus`, `solid-nav-full`) and
  a published set of CSS custom properties on `.solid-nav`
  (`navigator.ts:48-66`, README "Reading and moving the assembly").

The bundle built in this workspace's viewer worktree is API 11
(`solid_node_viewer/widget/dist/solid-widget.js`, banner
`solid-node-viewer 0.2.0 - viewer API 11`). The viewer package installed in the
workspace venv, editable from the PRIMARY checkout, still reports API 8 — it has
no `mountNavigator` at all. That gap shapes the test strategy below.

## Goals / Non-Goals

**Goals:**

- The Model panel shows the viewer's navigator, and the shop holds no assembly
  state.
- The panel looks exactly as it looks today, which is what the reference design
  "MODEL (1b)" states, achieved only through the viewer's published theming
  surface.
- A viewer too old to mount a navigator refuses the open, with the existing
  message and remedy.
- The behavioural test of the navigator runs against a REAL bundle, and says
  plainly when it cannot.

**Non-Goals:**

- The viewer's inspector layout (`mountInspector`, ADR-051/052). The studio
  keeps its own workspace layout; the sidebar, rail and toggle that layout
  composes are for pages that have no layout of their own.
- Any change to `solid-node-viewer` or to `solid-node`. This is one repository's
  half of a contract the other half already published and specified.
- The hub's model previews and `solid snapshot --renderer web`.
- Changing the reference design. `docs/design/README.md` is untouched.

## Decisions

### D1. A wrapper component with a dedicated host element, and no queue

`AssemblyNavigator` replaces `AssemblyPanel`:

```tsx
function AssemblyNavigator({ viewer }: { viewer: ViewerHandle | null }) {
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const target = host.current;
    if (target === null || viewer === null) return;
    const widget = window.SolidNodeWidget;
    if (!widget || typeof widget.mountNavigator !== "function") return;
    const mounted = widget.mountNavigator(target, viewer, {
      label: "Assembly", fullAssembly: true,
    });
    return () => mounted.dispose();
  }, [viewer]);

  return <section className="assembly-panel" aria-labelledby="assembly-heading">
    <h2 id="assembly-heading">MODEL</h2>
    {viewer === null ? <p className="empty">No model assembly is available.</p> : null}
    <div className="assembly-navigator-host" ref={host} />
  </section>;
}
```

Rendered at `main.tsx:1958` as `<AssemblyNavigator viewer={viewerHandle} />`.

Three things make this simpler than `FunctionalModel`'s machinery, and each is
a property of the viewer's contract rather than a hope:

- **StrictMode needs no queue.** `FunctionalModel` serialises its work on a
  promise chain because `mount()` is async, so StrictMode's synchronous
  unmount/remount can interleave two mounts. `mountNavigator` is synchronous and
  draws before returning (`navigator.ts:212`, README: "synchronous, draws before
  returning"), so React runs cleanup-then-effect in order: dispose, then mount.
  A flag or a queue would add a failure mode, not remove one.
- **The host element is the navigator's to empty.** `NavigatorHandle.dispose()`
  ends with `container.replaceChildren()` (`navigator.ts:519`). The wrapper
  therefore gives it a `<div>` that React never puts children into; React's own
  reconciliation never sees the navigator's DOM, and the navigator never removes
  a React-owned node. This is why the heading and the empty-state paragraph are
  siblings of the host, not inside it.
- **Disposal order is safe in both directions.** When a session ends,
  `FunctionalModel`'s cleanup disposes the viewer and then calls
  `onViewerChange(null)`, so this effect's cleanup runs after the viewer is
  already disposed. `dispose()` there only calls the unsubscribe closure, which
  deletes from a `Set` (`assembly.ts:105-108`) — safe on a disposed viewer,
  which has in any case already released every subscription (ADR-049).

`viewer` is the effect's only dependency, and it is the handle identity: one
mount per viewer, so the navigator survives every area change (the Model panel
stays mounted behind `area-hidden`), every artifact update, and every
reconnect — the same one-mount property `test_model_panel_...` asserts today
with `__solidNodeWidgetHistory.mounts == 1`.

**Alternative rejected:** passing `assembly` down and re-rendering the wrapper on
every change. That is the plumbing this change exists to delete; the navigator
subscribes to the handle itself and needs no host notification (README: "a
navigator given ONLY the handle").

### D2. The look is CSS custom properties, plus exactly two class rules

`styles.css`'s `.assembly-*` block collapses to the panel shell plus one
override block. Every value below is today's rendered value, read off
`styles.css:166-191`:

```css
.assembly-panel { border-bottom: 1px solid #262b33; margin-bottom: 18px; padding-bottom: 18px; }
.assembly-panel h2 { /* unchanged: mono 10px uppercase #e6e8ec, letter-spacing .08em */ }
.assembly-navigator-host { margin-top: 10px; }

.assembly-panel .solid-nav {
  --solid-nav-font: 12px ui-monospace, SFMono-Regular, Menlo, monospace;
  --solid-nav-indent: 15px;
  --solid-nav-row-padding: 4px 5px;
  --solid-nav-row-radius: 5px;
  --solid-nav-row-min-height: 28px;
  --solid-nav-gap: 6px;
  --solid-nav-chip-size: 12px;
  --solid-nav-fg: #c3c8d1;
  --solid-nav-fg-strong: #e6e8ec;
  --solid-nav-muted: #8b929e;
  --solid-nav-bg: transparent;
  --solid-nav-row-hover-bg: #1c2128;
  --solid-nav-root-bg: #1c2128;
  --solid-nav-root-mark: #4fb6b8;
  --solid-nav-chip-neutral: #6b7280;
  --solid-nav-chip-border: #6b7280;
  --solid-nav-obscured-opacity: 0.45;
  --solid-nav-focus-ring: #e0a350;
}
/* The two accents the variables do not reach, through the navigator's own
   published class contract (README "The class contract"): */
.assembly-panel .solid-nav-badge { color: #4fb6b8; }
.assembly-panel .solid-nav-focus { color: #e0a350; }
```

The two class rules exist because `--solid-nav-muted` is one variable shared by
the `Show full assembly` button (today `#8b929e`) and the per-row `Focus` button
(today `#e0a350`), and because `.solid-nav-badge` takes `--solid-nav-fg-strong`
(`#e6e8ec`) where the studio's `root` marker is `#4fb6b8`. Both classes are in
the contract the viewer publishes for hosts to select on, which is exactly the
seam this change is allowed to use; nothing here selects an element the viewer
did not name, and nothing changes in the viewer.

Two one-pixel differences are accepted rather than fought:

- The twisty column becomes `--solid-nav-chip-size` (12px) where today's grid
  gives it 13px (`grid-template-columns: 13px 13px …`), because the navigator
  sizes the twisty and the chip from the same variable.
- `Show full assembly` moves from the panel header, beside `MODEL`, to the
  navigator's own right-aligned toolbar directly above the tree
  (`navigator.ts:69-73`). This is the pilot's preference recorded in the
  campaign: one affordance, the viewer's.

**Alternative rejected:** `styles: 'none'` and serving the whole class contract
from `styles.css`. It would let the studio dictate every pixel, and it would
make the shop own a copy of the navigator's structural CSS — the same
duplication in a new place, silently stale after any viewer change.

### D3. The gate rises to 10, and the browser checks too

`REQUIRED_VIEWER_API` (`floor/preparation.py:28`) becomes 10 — the API that
introduced `mountNavigator`, not 11 (the bundle that happens to be built here).
The floor requires a capability, not the newest build.

`solid-node-widget.d.ts` is re-vendored from the viewer worktree at API 11 and
declares `SOLID_NODE_VIEWER_API_VERSION: 10`; `test_required_viewer_api_matches_the_declared_widget_interface`
(`tests/test_project_preparation.py:538-540`) already binds that literal to
`REQUIRED_VIEWER_API`, so the two cannot drift. The file records in a comment
which viewer version and commit it was vendored from. It declares the
`ViewerHandle` surface the studio actually uses — `apiVersion`,
`artifactChanged`, `manifestChanged`, `reload`, `view`, `dispose`, plus
`assembly`, `setRoot`, `setVisible`, `navigation`, `onAssemblyChange` as the
contract the navigator consumes — and adds `AssemblyNavigationState`,
`AssemblyChange`, `AssemblyListener`, `NavigatorOptions`, `NavigatorHandle`, and
`mountNavigator` on `window.SolidNodeWidget`. The driving, playback and run
surfaces stay out: the studio uses none of them, and a typing it does not use is
a typing that rots.

`loadViewer` (`main.tsx:598`) additionally rejects after the script loads when
`window.SolidNodeWidget` is absent or `apiVersion < SOLID_NODE_VIEWER_API_VERSION`,
which lands on the existing `viewerReady === false` state. Both gates, because
they fail differently: preparation refuses to OPEN the project, which is the
honest outcome; the browser check means a bundle that somehow reaches the page
anyway cannot call a function that is not there. The wrapper's own
`typeof widget.mountNavigator !== "function"` guard is the third, and the only
one that runs when a page is served a bundle whose `apiVersion` lies.

### D4. The behavioural test runs on a real bundle, or says why it did not

The fake widget in `tests/fixtures/fake_solid.py:147` is a hand-written
`SolidNodeWidget`. Teaching it a navigator would mean writing a second tree and
then asserting against it — a test of the fixture. So the Model-panel
behavioural test runs against a real bundle, resolved in this order:

1. `SHOP_E2E_VIEWER_BUNDLE`, if set. A value naming no file is an error, not a
   skip: the pilot asked for that bundle. Its API version is read from the
   bundle's own banner (`/\bviewer API (\d+)/` over the first 512 bytes —
   `build.mjs:17-31` writes it there for every build).
2. Otherwise the installed `solid_node_viewer` package:
   `bundle.bundle_path()` and `bundle.api_version()`, used when the file exists
   and the version is at least `REQUIRED_VIEWER_API`.
3. Otherwise `self.skipTest(...)`, naming `SHOP_E2E_VIEWER_BUNDLE` and the
   version that was found, so a skip reads as a missing bundle rather than as a
   pass.

Today step 2 declines (the installed package is API 8), so the test skips unless
the pilot exports the worktree's bundle; once the viewer branch reaches the
workspace's installed viewer, step 2 starts answering on its own. **A skipped run
is not evidence:** the implementer must run this test with
`SHOP_E2E_VIEWER_BUNDLE` pointing at
`solid-node-viewer/WTs/viewer-navigator/solid_node_viewer/widget/dist/solid-widget.js`
and record that it went red first.

Two fixture facts make that bundle actually run under the fake framework:

- The fake's `viewer` command already honours `FAKE_SOLID_BUNDLE` to substitute
  a real bundle file (`fake_solid.py:148-149`), but it reports
  `state.get("viewer_api_version", …)` read from the project's state file — and
  the shop runs `solid viewer` from its own launch directory, where no project
  state exists. So the `viewer` branch also honours an env var
  `FAKE_SOLID_VIEWER_API` (the name the inline preparation fake already uses,
  `test_project_preparation.py:728`), and the e2e sets it to the discovered
  bundle's version, so preparation's report and the served bytes agree.
- The real viewer refuses a document it cannot walk:
  `assertRenderable` iterates `node.operations` unguarded
  (`viewer.ts:1056-1060`) and `RENDERED_VERSIONS` is `[1..5]`
  (`viewer.ts:959`). The fixture document must therefore give every node
  `operations: []` and `children: []` — the shape
  `test_model_panel_controls_the_supplied_framework_viewer` already writes
  (`test_shop_lifecycle_e2e.py:672-690`).

**No STL is needed, and none should be written.** `WidgetTree` fetches geometry
only for a node carrying `model` (`tree.ts:113-115`), so a fixture document
whose nodes name no model loads with no artifact request at all. This is worth
saying because the fake's default publication *does* name `part.stl` with the
contents `solid part` (`fake_solid.py:106-107`), which is neither a valid ASCII
STL nor long enough for three.js's `STLLoader.isBinary` to read its face count
without a `RangeError` — any future test that points the real bundle at the
fake's DEFAULT document would need the fake to publish a real 84-byte-header
binary STL. The Model-panel test avoids the question by declaring an assembly of
pure structure, which is also all a navigator test needs.

### D5. The fake widget keeps every other test running

The fake `SolidNodeWidget` reports `apiVersion: 10` and gains the smallest
`mountNavigator` that satisfies the wrapper and the page, and nothing more:

```js
mountNavigator(target, viewer, options){
  const history = window.__solidNodeWidgetHistory ??= {mounts:0,fetches:[],updates:[],navigators:[]};
  const record = {label: (options && options.label) || 'Assembly', disposed: false};
  history.navigators.push(record);
  const tree = document.createElement('div');
  tree.className = 'solid-nav';
  const inner = document.createElement('div');
  inner.className = 'solid-nav-tree';
  inner.setAttribute('role','tree');
  inner.setAttribute('aria-label', record.label);
  tree.append(inner);
  target.append(tree);
  return {dispose(){record.disposed = true; target.replaceChildren();}};
}
```

No rows, no keyboard, no `onAssemblyChange`: an empty labelled tree and a
record. That is enough for every e2e test that only needs the Model panel to
exist and for one test of the shop's OWN behaviour — that the wrapper mounts
exactly one navigator, gives it the label `Assembly`, does not remount it when
the maker moves between areas, and disposes it when the project closes. Anything
richer would be a second implementation and would start lying the moment the
viewer's does something new.

`tests/test_project_preparation.py`'s inline fake (`:727-728`) gets the same
`apiVersion: 10` bump and default, because every preparation test in that file
opens through it.

### D6. Which tests go, and what replaces them

- `test_model_panel_navigates_the_viewer_assembly`
  (`test_shop_lifecycle_e2e.py:561-668`) and
  `test_model_panel_controls_the_supplied_framework_viewer` (`:670-704`) both
  assert the deleted DOM (`.assembly-row`, `focused-root`, the studio's
  `Expand housing` button). They are replaced by ONE real-bundle test,
  `test_model_panel_presents_the_viewer_navigator`, written against the
  navigator's published contract: `solid-nav-row--root` and `aria-selected` on
  the focused row, `Expand <name>` twisties, `Visibility for <name>` checkboxes,
  the `Show full assembly` toolbar button, keyboard Up/Down/Right/Enter/Space,
  and — the part that is the shop's own — the computed values the overrides
  produce: root row `rgb(28, 33, 40)`, coloured chip `rgb(204, 68, 68)`,
  colourless chip `rgb(107, 114, 128)`, hidden chip `rgba(0, 0, 0, 0)`, the
  focused row's `box-shadow` carrying `rgb(79, 182, 184)`, and
  `getPropertyValue('--solid-nav-focus-ring')` equal to `#e0a350`.
- `test_model_panel_mounts_and_disposes_the_viewer_navigator` is the new
  fake-widget test of D5, and is the one that keeps running everywhere.
- `test_project_open.py:128` and `test_project_preparation.py:380` assert the
  reported API version and become 10;
  `test_project_preparation.py:523`'s expected message becomes
  `viewer API 10 is required but installed viewer API is 3`. The refusal stays
  meaningful: 3 is still below 10.

### D7. The record

No shop ADR recorded the host-built navigator — the decision that put it in the
host was the viewer's ADR-042, and the decision that took it back is the
viewer's ADR-050. What this repository owes is the boundary it now keeps: a new
shop ADR 0030, "The Model panel is the viewer's navigator", stating that the
shop mounts and themes the navigator and specifies none of its behaviour, and
that the viewer's inspector layout is deliberately not used. `docs/adrs/README.md`
gains its row, and `docs/architecture-overview.md`'s Model-panel passage
(`:459-464`, and the Model/Code/Agents/Build paragraph at `:466-480`) is
rewritten rather than annotated, per AGENTS.md.

## Risks / Trade-offs

- [The real-bundle test silently skips and nobody notices the navigator broke] →
  The skip message names `SHOP_E2E_VIEWER_BUNDLE` and the version it found; the
  fake-widget mount/dispose test always runs; the tasks require a red-then-green
  run with the bundle exported, recorded in evidence.
- [The workspace's installed viewer is API 8, so an ordinary `scripts/test-e2e`
  run after this change cannot exercise the real navigator] → Accepted and
  stated. It resolves itself when the viewer's `viewer-navigator` branch reaches
  the installed package; until then the bundle is one env var away.
- [A future viewer changes a default and the panel drifts] → Every value the
  panel depends on is written explicitly in `styles.css`, including ones that
  happen to equal today's navigator default (font, indent, radius, row height,
  gap). A default change cannot move the studio's look.
- [The two class-name rules couple the shop to the navigator's internals] →
  They use only `solid-nav-badge` and `solid-nav-focus`, both published in the
  viewer's README class table as a host-selectable contract and specified by its
  `viewer-assembly-navigation` capability. If either disappears, the panel loses
  an accent colour, not a function.
- [Raising the gate to 10 refuses a shop whose installed viewer is older] →
  That is the intended behaviour and already specified: preparation fails with
  the required and installed versions named, and no floor opens with a Model
  panel that cannot navigate.
- [`mountNavigator` throws for a viewer disposed between the render and the
  effect] → The navigator reads `assembly()` and `navigation()` synchronously at
  mount; `viewer` is the effect's dependency, so the handle it mounts on is the
  one state currently holds, and the guard returns early when it is `null`.

## Open Questions

None. The two judgment calls the campaign left open are decided above: the
navigator's own toolbar carries `Show full assembly` (D2), and both the
preparation gate and a browser-side API check are kept (D3).
