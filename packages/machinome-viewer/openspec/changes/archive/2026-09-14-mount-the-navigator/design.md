# Design — mount the navigator

## Context

Cycle 2 of the pilot's 2026-09-14 decision. Cycle 1 published the state
(`navigation()`, `onAssemblyChange()`, ADR-049); this cycle writes the
component that reads it. Cycle 3 composes it into a shipped layout and
the export page; the shop cycle deletes the studio's copy and mounts
this one.

What exists here:

- `ViewerHandle` (`viewer.ts:133-173`) with `assembly()` (the **whole**
  published tree from the document root, `tree.ts:330-338` — focus never
  narrows it), `setRoot(path | null)`, `setVisible(path, visible)`,
  `navigation()` (`:145`) and `onAssemblyChange(listener)` (`:152`).
- `AssemblyNode = { name, path, color, model, children }`
  (`tree.ts:39-45`); `assemblyPathKey` is `JSON.stringify(path)`
  (`tree.ts:47-49`) and is the same key `AssemblyNavigation` hides by
  (`assembly.ts:41`).
- The driver chrome (`viewer.ts:1195-1345`): plain DOM, built into the
  viewer's own container, every element styled by `style.cssText` from a
  module constant. Its breadcrumb is the other thing that moves focus
  (`viewer.ts:584-602`).
- `controls.ts`: the pattern for a testable component here — every
  decision is a pure function over plain data, and `viewer.ts` renders
  exactly what it returns, "because there is no DOM test framework in
  this bench and an untestable decision is a decision nobody checks"
  (`viewer.ts:1173-1179`).
- vitest runs with no DOM (`vitest.config.ts` sets only `define`;
  `package.json` has neither jsdom nor happy-dom). 533 tests, 28 files.

What exists in the studio, and is the behavioural source for this cycle:
`AssemblyPanel` (`floor/frontend/src/main.tsx:295-434`), `.assembly-*`
(`floor/frontend/src/styles.css:166-191`), and the ratified spec
`openspec/specs/assembly-navigation/spec.md` in that repository. Its
*look* — mono 12px rows, 5/8 padding, radius 5, 7px chip, 14-16px
indent, selected row `#1c2128` (`docs/design/README.md`, "MODEL (1b)") —
is the **studio's**, and stays the studio's: this package ships a
neutral default and the variables the studio overrides.

## 1. The public interface

### D1. One function, a target, a handle, four options

```ts
export interface NavigatorOptions {
  /** Accessible name of the tree; default 'Assembly'. */
  label?: string;
  /** Present the "show full assembly" affordance; default true. */
  fullAssembly?: boolean;
  /** Extra class on the navigator root, for a host's own scoping. */
  className?: string;
  /** Inject the stylesheet into the target's document; default 'inject'. */
  styles?: 'inject' | 'none';
}

export interface NavigatorHandle {
  dispose(): void;
}

export function mountNavigator(
  target: HTMLElement | string,
  viewer: ViewerHandle,
  options?: NavigatorOptions,
): NavigatorHandle;
```

Four decisions are packed in here.

**It takes a handle, not state.** Everything a navigator needs is on the
handle, which is what cycle 1 was for. There is no `assembly` prop, no
`hidden` prop, no `onFocus` callback: a host that wants to know what the
maker did subscribes to the same `onAssemblyChange` the navigator does.
Fewer doors, and no way for a host to hand the navigator a state that
disagrees with the viewer.

**It is synchronous.** `mount()` is async because it fetches a document;
a navigator fetches nothing. It reads `assembly()` and `navigation()`,
builds the DOM, appends it, subscribes, and returns — one turn. A host
gets a drawn tree back from the call, and does not have to await
anything or wait for a first notification. (Reading before subscribing
is safe *because* it is one turn: the viewer notifies only from an
operation, and no operation can interleave.)

**`styles` mirrors `driverControls`.** `'inline' | 'none'` is the
existing spelling for "the widget presents this itself, or the host
does" (`viewer.ts:56-58`). `'inject' | 'none'` is the same idea for the
stylesheet, and it is the escape hatch for a page under a
Content-Security-Policy that forbids inline style blocks (D15).

**`fullAssembly` is a boolean, not a slot.** See D7.

*Alternative that lost:* returning the built root element on the handle
(`{ dispose(), element }`). Nothing in the campaign needs it, and
handing a host the element invites exactly the DOM-reaching the styling
contract exists to prevent. A host that needs to find it has
`className`, and `dispose()` empties the target either way.

*Alternative that lost:* `mountNavigator(target, viewer)` returning a
promise for symmetry with `mount()`. Symmetry is not a reason to make a
synchronous thing await-shaped, and a host that has to `await` cannot
draw a navigator in the same layout pass as the rest of its panel.

### D2. Exported from `widget.ts`, not from `viewer.ts`

`SolidNodeWidget.mountNavigator` is the published name (beside `mount`,
`apiVersion`, `API_VERSION` — `widget.ts:14-16`). `navigator.ts` is its
own module and `viewer.ts` does **not** re-export it:

- `navigator.ts` needs `ViewerHandle`, `AssemblyNode`, `AssemblyPath`,
  `AssemblyChange` and `AssemblyNavigationState`, and imports every one
  of them with `import type`. Erased at compile time, so the navigator's
  own test loads no three.js, no `OrbitControls`, no renderer.
- A runtime re-export from `viewer.ts` would make the dependency
  circular (navigator → viewer → navigator) for no gain: `widget.ts`
  already imports both, and it is the published entry point ADR-035
  named.

The cost is one duplicated six-line helper: `resolveContainer`
(`viewer.ts:1162-1171`) is private to `viewer.ts`, and `navigator.ts`
gets its own `resolveTarget` with the same refusal text
(`solid-widget: no element matches "<selector>"`). Exporting the
existing one instead would drag the renderer module into the jsdom test
just to resolve a selector. The duplication is named in both places.

Types exported beside the existing ones: `NavigatorOptions`,
`NavigatorHandle` from `navigator.ts`, re-exported by `widget.ts` the
way `viewer.ts:60-61` re-exports the assembly types.

## 2. What it shows

### D3. The rows are a pure function; the DOM renders them

Following `controls.ts` exactly. `navtree.ts` holds every decision:

```ts
export interface NavigatorRow {
  node: AssemblyNode;
  key: string;          // assemblyPathKey(node.path)
  depth: number;
  expandable: boolean;  // node.children.length > 0
  expanded: boolean;
  active: boolean;      // the roving-tabindex row
  root: boolean;        // the focused viewer root
  hidden: boolean;      // explicitly hidden
  obscured: boolean;    // invisible only because an ancestor is hidden
  color: string | null; // node.color, effective and inherited
}

export function navigatorRows(assembly, navigation, local): NavigatorRow[];
export function keyAction(rows, key, event): NavigatorAction | null;
export function reconcileLocal(assembly, previous): NavigatorLocal;
```

`NavigatorLocal = { expanded: Set<string>, active: string | null }` —
the navigator's own state, and the only state it has.

`navigatorRows` walks the assembly depth-first, emitting a row for the
root and for every node under an expanded parent, and decides `root`,
`hidden` and `obscured` from `navigation` alone:

- `root`: `navigation.root === null ? depth === 0 : keys equal`.
- `hidden`: the node's own key is in the hidden set.
- `obscured`: some **proper ancestor**'s key is in the hidden set. Cheap
  to compute in the same walk (carry "an ancestor is hidden" down).

This is the whole reason cycle 1 published the explicit set rather than
effective visibility (ADR-049 §3): the distinction between the two is
derived here, once, by a function a test can call with a hand-built
tree and no browser.

### D4. The root row is `null` to the focus API

The studio calls `viewer.setRoot(node.path)` for every row including the
root, whose path is `[]` (`main.tsx:341-343`). Under cycle 1's contract that
puts `[]` into `navigation().root` — a second spelling of the document
root that ADR-049 §2 spent a decision eliminating. So:

> The navigator passes `null` when the row is the document root, and the
> path otherwise — the same conversion the breadcrumb already makes
> (`viewer.ts:1302-1303`).

A deliberate divergence from the studio's current code, and the shop
cycle inherits it by deleting that code.

### D5. The checkbox is the chip, and it says three things

A real `<input type="checkbox">` per row, `appearance: none`, sized by a
custom property, exactly as the studio does (`styles.css:186-187`) —
checkbox semantics, `checked`, and an accessible name come free, and
they are what the ratified scenario "both expose their checked state to
assistive technology" asks for.

| state | checked | fill | class | accessible name |
| --- | --- | --- | --- | --- |
| shown, coloured | yes | the node's colour | — | `Visibility for <name>` |
| shown, colourless | yes | neutral gray | — | `Visibility for <name>` |
| explicitly hidden | no | none, border only | `--hidden` | `Visibility for <name>` |
| obscured by an ancestor | yes | the node's colour, dimmed | `--obscured` | `Visibility for <name> (hidden with <ancestor>)` |
| hidden in its own right, under a hidden ancestor | no | none, border only | `--hidden --obscured` | `Visibility for <name> (hidden with <ancestor>)` |

The fourth row is this cycle's answer to the question cycle 1 left open.
An obscured node's checkbox reports the node's **own** setting, so
`Space` on it stays the exact inverse of what hid it and
`setVisible(path, true)` on a node whose parent is hidden does what the
baseline spec already says it does (it stays invisible until the
ancestor is shown). What differs is the *row*, not the control: the row
carries `solid-nav-row--obscured`, the chip is dimmed by a variable, and
the control's accessible name names the hidden ancestor so the
difference is not carried by colour alone.

*Alternative that lost:* show an obscured node as unchecked. It would
make the checkbox lie about the node's own state, break the inverse, and
make a maker who shows the ancestor see checkboxes flip that nobody
touched.

*Alternative that lost:* an `aria-disabled` obscured checkbox. It is not
disabled — toggling it is meaningful and takes effect the moment the
ancestor is shown.

### D6. Every row carries its label, depth and colour

`name` as text (ellipsised by CSS, never truncated in the DOM, so the
accessible name is whole); depth as the custom property the indent is
computed from; colour as the chip. A `root` badge on the focused row and
a per-row `Focus` button, as the studio has — both are what the ratified
requirement means by "labelled controls to focus the selected subtree"
and "identify the focused viewer root".

### D7. "Show full assembly" belongs to the navigator

Cycle 1's design §6.3 left this open. Decision: **the navigator renders
it**, in a toolbar row above the tree, present only when
`navigation().root !== null`, and suppressible with
`fullAssembly: false`.

Why the navigator and not the layout:

1. It is the inverse of a gesture the navigator already owns. Every row
   can focus; exactly one affordance un-focuses. Splitting the pair
   across two components means a host that mounts only the navigator
   (the studio's Model panel is one element, and that is cycle 4) has a
   tree that can enter a subassembly and not leave it.
2. Its condition is state the navigator already reads and re-renders on
   (`root !== null`). A layout owning it would have to subscribe
   separately to draw one button.
3. The keyboard already reaches the root row, and `Enter` on it focuses
   the document root — so the behaviour exists regardless; the button is
   its pointer affordance, and leaving it out would make the pointer
   strictly weaker than the keyboard.

Why suppressible: cycle 3's layout may put the same affordance in a
header beside the breadcrumb, and two of them in one sidebar is noise.
One boolean is cheaper than a slot API, and a host that wants it
elsewhere calls `setRoot(null)` itself — one line, on a handle it has.

## 3. What it does not own

### D8. Root and hidden come only from the handle; expansion and the active row are local

The studio keeps `focused` and `hidden` in React state and writes them
beside every viewer call (`main.tsx:299-301`, `:340-353`). This
navigator does not. Each render is a pure function of

- `change.assembly` (or `viewer.assembly()` at mount),
- `change.navigation` (or `viewer.navigation()` at mount),
- `local = { expanded, active }`.

A gesture calls the handle and **returns**. The redraw happens when the
notification arrives — which it always does, once per accepted
operation (ADR-049 §5), including for a call that changed nothing. So
there is one code path from state to pixels, and the state it renders is
always the viewer's, never a prediction of it.

Expansion and the active row are local because the viewer has no opinion
about either: two navigators on one handle may show different parts of
the same tree expanded, and they must, or a second mount in cycle 3's
layout would fight the first.

### D9. Reconciliation: retain what survives, drop the rest, expand the root once

`reconcileLocal(assembly, previous)` on every render from a change:

- `expanded`: keep every key the new tree still contains; drop the rest.
  On the **first** render, expand the root (the studio's
  `initializeExpansion`, `main.tsx:315-320`) and nothing else.
- `active`: keep it if the new tree still contains it, otherwise fall
  back to the root's key — never to `null`, so the tree always has
  exactly one tab stop.
- If the DOM focus was inside the tree when the change arrived, the row
  that becomes active receives `focus()` after the redraw; if it was
  not, nothing steals focus. (Rebuilding rows destroys the focused
  element; a maker holding the keyboard in a tree that republished must
  not be dropped to the top of the page.)

**And one thing the studio does not do:** when the focused root moves to
a path that is not currently revealed, the navigator expands that path's
ancestors. The breadcrumb can now focus a subassembly the maker has
collapsed (that is what cycle 1 exists for), and a navigator that marks
a row nobody can see is lying about what it shows. Guarded by comparing
the new root against the last root the navigator rendered, so a maker
who collapses the focused row's parent is not fought by the next
redundant notification.

### D10. Gestures call the handle; the listener never does

ADR-049 §5 says a listener observes. This navigator's listener does
exactly one thing: recompute rows and repaint. Every call into the
viewer (`setRoot`, `setVisible`) is in a pointer or key handler.

Two calls can still throw, and neither may escape into the page:

1. The viewer was disposed first. Disposal notifies nobody (ADR-049 §6),
   so the navigator **cannot** know; a click afterwards reaches a
   handle whose `tree` is gone and throws `Viewer assembly is
   unavailable` (`viewer.ts:590`, `:861`, `:873`).
2. An ambiguous path. `requirePath` refuses a path whose name matches
   two siblings (`tree.ts:349-360`); such a tree renders two rows with
   the same path, and either one's gesture is refused. A limit inherited
   from the path currency ADR-042 chose, not introduced here.

**The redraw happens inside the gesture's own event.** ADR-049 §6 has
the viewer notify before `setVisible`/`setRoot` return, so the listener
rebuilds the rows while the `change` event of the clicked checkbox (or
the `click` of a button, or the `keydown` of a row) is still being
dispatched on an element the rebuild has just detached. That is
permitted by the DOM and by every browser; what the navigator must
ensure is that the handler does nothing with the old element after the
call (no reading `checked` back, no `focus()` on it), and that D9's
focus restoration treats focus on a row's *control* — the checkbox the
maker clicked, which takes focus in most browsers — as "inside the
tree", restoring it to the active row. The jsdom test pushes a change
from inside a stub's `setVisible` to pin exactly this.

So every gesture wraps its handle call, reports a failure to
`console.error` and changes nothing on screen — the same defensiveness
`AssemblyChangeNotifier` already applies to a throwing listener
(`assembly.ts:113-121`). No notification follows a refused call, so
"changes nothing" is automatic.

### D11. Two navigators on one handle agree by construction

Both subscribe; both are notified for every accepted operation; both
render root and hidden from the payload. There is no ordering question
because neither writes anything the other reads. Their expansion and
active rows differ, which is what a maker asked for by opening two.

### D12. Disposal, in either order

`dispose()`: cancel the subscription, empty the target
(`target.replaceChildren()`, as the viewer's own dispose does,
`viewer.ts:821`), mark disposed, and be a no-op the second time.

- **Navigator first:** the viewer loses one listener and is otherwise
  untouched.
- **Viewer first:** cycle 1 guarantees the viewer releases every
  subscription and that the cancel function stays safe to call
  afterwards. The navigator receives nothing more and sits inert,
  showing its last render; a gesture on it is the D10 case; its own
  `dispose()` still empties the target.

## 4. How it is styled

### D13. One injected stylesheet, a class contract, custom properties

```
<style id="solid-node-navigator-style">   ← once per document
.solid-nav { … }
```

Injected into `target.ownerDocument.head` (so a navigator mounted inside
an iframe styles that iframe's document), guarded by
`getElementById(STYLE_ID)`, so N mounts inject one element. Never
removed on dispose: another navigator may still be mounted, and an
unused stylesheet costs a document nothing.

**Class contract** — every element gets a stable class, and this list is
the published contract a host may select on:

| class | element |
| --- | --- |
| `solid-nav` | the navigator root (`<div>`) |
| `solid-nav-toolbar` | the row above the tree |
| `solid-nav-full` | the "show full assembly" button |
| `solid-nav-tree` | `role="tree"` container |
| `solid-nav-row` | `role="treeitem"`; modifiers `--active`, `--root`, `--hidden`, `--obscured`, `--leaf` |
| `solid-nav-twisty` | the expand/collapse button |
| `solid-nav-spacer` | the twisty's width on a leaf |
| `solid-nav-visibility` | the checkbox chip |
| `solid-nav-name` | the node's label |
| `solid-nav-badge` | the `root` marker on the focused row |
| `solid-nav-focus` | the per-row focus button |

**Custom properties** — declared on `.solid-nav`, so a host overrides
them on `.solid-nav`, on an ancestor, or on `:root`:

| property | default | what it sets |
| --- | --- | --- |
| `--solid-nav-font` | `12px ui-monospace, SFMono-Regular, Menlo, monospace` | row type |
| `--solid-nav-indent` | `15px` | indent per level |
| `--solid-nav-row-padding` | `4px 5px` | row padding |
| `--solid-nav-row-radius` | `5px` | row corner |
| `--solid-nav-row-min-height` | `28px` | row height |
| `--solid-nav-gap` | `6px` | gap between a row's parts |
| `--solid-nav-chip-size` | `12px` | the visibility chip |
| `--solid-nav-fg` | `inherit` | row text |
| `--solid-nav-fg-strong` | `inherit` | hovered / focused-root text |
| `--solid-nav-muted` | `rgba(128,128,128,0.95)` | buttons, badges |
| `--solid-nav-bg` | `transparent` | the navigator's ground |
| `--solid-nav-row-hover-bg` | `rgba(128,128,128,0.18)` | hover |
| `--solid-nav-root-bg` | `rgba(128,128,128,0.22)` | the focused-root row |
| `--solid-nav-root-mark` | `currentColor` | its inset rule |
| `--solid-nav-chip-neutral` | `#9aa0a8` | a colourless visible node |
| `--solid-nav-chip-border` | `rgba(128,128,128,0.8)` | a hidden node's outline |
| `--solid-nav-obscured-opacity` | `0.45` | an obscured node's chip |
| `--solid-nav-focus-ring` | `currentColor` | `:focus-visible` outline |

The default theme is **neutral on purpose**: text and focus ring inherit
the host page's colour, and every ground is a translucent gray, which
darkens a light page and lightens a dark one. The studio's `#1c2128`
selected row, `#4fb6b8` root mark and `#e0a350` accent are the studio's,
set in the shop cycle by overriding these variables — the design
reference `docs/design/README.md` "MODEL (1b)" describes the studio's
look, not this package's default.

Per-row data that is **not** theme — the depth and the node's colour —
is written to the row element with `style.setProperty`
(`--solid-nav-depth`, `--solid-nav-node-color`), the way the studio
writes `--assembly-depth` and `--node-color` (`main.tsx:395`). A value,
not a rule.

### D14. Why not the driver chrome's way, and why not shadow DOM

**Not `style.cssText` per element** (`viewer.ts:1195-1345`). It works for
a panel of a dozen fixed elements and fails for a tree: there is no
`:hover`, no `:focus-visible`, no `:checked`, no media query, and no way
for a host to change a colour without rewriting every element's inline
style — which is precisely what "the studio restyles it" has to mean.
The chrome is not being converted in this cycle; it is simply not the
model to copy.

**Not shadow DOM.** It would give perfect encapsulation and take the
theming with it: a host's stylesheet cannot reach in, so every visual
difference would need an explicit `::part` or a custom property we
thought of in advance. It also complicates exactly the two things this
component is tested on — `document.activeElement` across a shadow
boundary, and keyboard/focus assertions in Playwright and jsdom. The
prefix is the encapsulation; a collision on `solid-nav-*` in a host page
is a host's own doing.

**Not a separate `.css` file.** `viewer-distribution` says the export
carries exactly `index.html` + `solid-widget.js` and the framework
copies those two (`solid_node/sphinx.py` `WIDGET_FILES`). A second file
would be a framework change in another repository for a stylesheet.

### D15. The Content-Security-Policy question

Nothing in this repository sets a CSP: the export page
(`widget/index.html`), the capture page (`capture.py:153-162`) and the
e2e harness (`tests/test_widget_e2e.py:92-106`) each carry their own
inline `<style>` block, and the served pages set only `Cache-Control`
(`tests/support.py:102-110`). So an injected `<style>` element is
**exactly as strict a requirement as the export page already is**: both
need `style-src 'unsafe-inline'`, as does every `style.cssText` the
driver chrome already writes.

For a host page that forbids inline styles, `styles: 'none'` skips the
injection entirely and the host serves the same rules from its own
stylesheet — the class contract above is what makes that possible. A
constructed stylesheet adopted through `adoptedStyleSheets` would escape
`style-src` altogether; it is not built here because no consumer in the
campaign needs it, and the escape hatch costs one option.

## 5. Where the logic lives so a test can reach it

Three layers, three test surfaces:

1. **`navtree.ts` — pure, node environment.** `navigatorRows`,
   `keyAction`, `reconcileLocal`, and the chip state. `navtree.test.ts`
   builds `AssemblyNode` literals by hand and asserts rows, ordering,
   depth, `root`/`hidden`/`obscured`, every keyboard transition
   (including the ends of the list and a leaf's Right), reconciliation
   after a pruned tree, first-render root expansion, and the
   expand-to-reveal rule. No DOM, so it runs in the suite exactly as
   `controls.test.ts` does.

2. **`navigator.test.ts` — jsdom, per file.** The component: mount into
   a detached element with a **stub handle** (an object literal with
   `assembly`, `navigation`, `setRoot`, `setVisible`, `onAssemblyChange`
   — the whole surface the navigator uses, which is five methods), then
   assert roles and ARIA attributes, the single tab stop, `focus()`
   moving with Arrow keys, `checked` and the accessible name of each
   chip state, that a gesture called the handle with the expected
   arguments (and `null` for the root row, D4), that a notification
   pushed through the stub redraws, that the stylesheet is injected once
   across two mounts, that `styles: 'none'` injects none, that
   `dispose()` unsubscribes and empties the target and is safe twice,
   and that a throwing handle does not throw out of a click.

   The stub is the point: this layer is tested against the **contract**
   cycle 1 wrote, not against a renderer. Whether the real handle keeps
   that contract is increment 3's Playwright job.

3. **`tests/test_widget_e2e.py` — Chromium, the real bundle.** Mount a
   viewer in `#host` and a navigator in a sibling element from
   `SolidNodeWidget.mountNavigator`, then: the rows match the fixture's
   assembly; the keyboard scenarios end in the *viewer's* state
   (`Enter` → `navigation().root`, `Space` → `navigation().hidden`);
   clicking the driver chrome's `.driver-descend` button moves the
   navigator's marked root with no host code (the breadcrumb agreement,
   on the `nested-driven.json` fixture cycle 1 added for exactly this);
   a targeted update through `manifestChanged()` drops the removed rows
   and keeps expansion for the surviving ones; two navigators on one
   handle agree; `dispose()` empties its element while the viewer keeps
   working.

### D16. jsdom, not happy-dom

Both would run the component. jsdom because:

- **Focus is the thing under test.** The roving tabindex, `row.focus()`
  on an Arrow key, `document.activeElement` after a rebuild, and
  `tabindex="-1"` on the row's children are half this component's
  contract. jsdom implements the focusing steps and the focusability
  rules of the HTML standard as its stated goal; happy-dom's speed comes
  from a lighter model, and its focus/`activeElement` behaviour is the
  part most often reported as divergent. A DOM that disagrees with a
  browser about focus is worse than no DOM here, because the test would
  pass while the maker's keyboard did not.
- **It is the environment vitest documents first** (`environment:
  'node' | 'jsdom' | 'happy-dom' | …`) and the one with the larger
  installed base, so a failure is searchable.
- Speed is not the constraint: **one** test file uses it.

Scoped per file with the documented docblock, so nothing else changes:

```ts
/**
 * @vitest-environment jsdom
 */
```

No `vitest.config.ts` change — the config's `define` block is about the
API version and must stay the only thing there. `jsdom` joins
`devDependencies`; it is a dev dependency of the **widget workspace**
and ships in no distribution (`dist/solid-widget.js` is the only
published artifact of it).

*Alternative that lost:* set `environment: 'jsdom'` globally. It would
put all 533 existing tests in a DOM they do not want, cost startup on
every run, and hide a future accidental DOM dependency in a module that
should be pure.

*Alternative that lost:* skip the DOM test and prove the component only
in Playwright. The e2e suite takes ~20s and needs Chromium; a component
with this many states (four chip states × hidden/obscured, six keys ×
three row shapes) needs a fast surface, and the Python suite already
skips itself where Chromium is absent (`support.py:66-71`) — which would
leave the navigator untested in that environment.

## 6. Risks

1. **A rebuild on every notification.** The navigator rebuilds its rows
   from scratch per accepted operation — a click or a republish, never
   per frame (ADR-049's consequence). A large assembly with everything
   expanded is the worst case, and it is the same walk `assembly()`
   already does for the payload. If it ever matters, the fix is keying
   rows and patching, behind the same pure `navigatorRows`.
2. **Focus is lost on rebuild unless it is restored.** D9 restores it
   deliberately; the jsdom test asserts it, because a keyboard maker
   losing focus on every visibility toggle would be a regression against
   the studio's React reconciliation, which keeps the element.
3. **Duplicate sibling names.** Two rows, one path, both refused by the
   viewer (D10). Pre-existing (ADR-042's path currency), now visible.
   Named in the design so the reviewer sees it was considered and not
   silently handled.
4. **The bundle grows for hosts that never mount a navigator.** One
   module plus a stylesheet string in a 644 kB bundle. Splitting it into
   a second published file would cost a framework change (D14); not
   worth it.
5. **The class contract is now a compatibility surface.** Renaming
   `solid-nav-row` later breaks a host's theme silently. It is listed in
   the README for that reason, and the API version is how a host asks
   which one it got.

## 7. Open questions

1. **Does the navigator need a scroll container of its own?** It fills
   its target and the host scrolls. Left to the host, and to cycle 3's
   sidebar, which is where a height constraint actually exists.
2. **Should the tree offer `Home`/`End`/typeahead** (the full ARIA tree
   pattern)? The studio's ratified contract has six keys; this cycle
   carries exactly those six so the two agree at the moment the studio
   adopts it. Adding more is a later, cheap change.
3. **Should a row be clickable to focus** (rather than only its `Focus`
   button and `Enter`)? The studio's row click does nothing today. Left
   as it is, so the shop cycle is a swap and not a behaviour change.

## 8. The ADR to extract

- **ADR-050 (EXPORT): The navigator is a component of the viewer
  package.** Extends ADR-049 and ADR-035, and completes the amendment
  ADR-042 began. The decision that the assembly navigator ships inside
  the bundle as plain DOM over the published navigation state; that it
  is mounted into any host element from a handle alone; that it holds no
  copy of the viewer's state and owns only expansion and the active row;
  that it is themed through CSS custom properties behind a stable class
  contract rather than encapsulated or inlined; and that the declared
  API version rises to 10 because a host may require it. Alternatives:
  ship a React component (ADR-035's own reason for rejecting it —
  hosts span React 18, 19 and none), shadow DOM, per-element inline
  styles, and leaving the navigator in the host.
