/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The assembly navigator: a React-free, plain-DOM tree mounted into any
// host element from a ViewerHandle alone (design D1, ADR-050). Everything
// it DECIDES lives in navtree.ts, following controls.ts's own pattern;
// everything here renders exactly what that module returns and calls the
// handle exactly as a maker's gesture decides (design D3, D10). It holds
// no copy of the viewer's focused root or hidden paths -- only its own
// expansion and active row (design D8) -- and it imports viewer.ts, tree.ts
// and assembly.ts for TYPES ONLY, so this module pulls no renderer and its
// own test loads no three.js (design D2).

import type { AssemblyChange, AssemblyListener, AssemblyNavigationState } from './assembly';
import {
  chipState, keyAction, navigatorRows, reconcileLocal,
  type NavigatorAction, type NavigatorLocal, type NavigatorRow,
} from './navtree';
import type { AssemblyNode, AssemblyPath } from './tree';
import type { ViewerHandle } from './viewer';

export interface NavigatorOptions {
  /** Accessible name of the tree; default 'Assembly'. */
  label?: string;
  /** Present the "show full assembly" affordance; default true (design D7). */
  fullAssembly?: boolean;
  /** Extra class on the navigator root, for a host's own scoping. */
  className?: string;
  /** Inject the stylesheet into the target's document; default 'inject'
   * (design D13, D15). */
  styles?: 'inject' | 'none';
}

export interface NavigatorHandle {
  dispose(): void;
}

const STYLE_ID = 'machinome-navigator-style';

// The class contract and the custom-property defaults of design D13.
// Every colour and metric a host may want is a variable declared on
// `.machinome-nav`; everything else in this stylesheet is structure. Per-row
// data that is NOT theme -- depth and the node's own colour -- is written
// straight to the row element with `style.setProperty`, never here.
const NAVIGATOR_STYLESHEET = `
.machinome-nav {
  --machinome-nav-font: 12px ui-monospace, SFMono-Regular, Menlo, monospace;
  --machinome-nav-indent: 15px;
  --machinome-nav-row-padding: 4px 5px;
  --machinome-nav-row-radius: 5px;
  --machinome-nav-row-min-height: 28px;
  --machinome-nav-gap: 6px;
  --machinome-nav-chip-size: 12px;
  --machinome-nav-fg: inherit;
  --machinome-nav-fg-strong: inherit;
  --machinome-nav-muted: rgba(128, 128, 128, 0.95);
  --machinome-nav-bg: transparent;
  --machinome-nav-row-hover-bg: rgba(128, 128, 128, 0.18);
  --machinome-nav-root-bg: rgba(128, 128, 128, 0.22);
  --machinome-nav-root-mark: currentColor;
  --machinome-nav-chip-neutral: #9aa0a8;
  --machinome-nav-chip-border: rgba(128, 128, 128, 0.8);
  --machinome-nav-obscured-opacity: 0.45;
  --machinome-nav-focus-ring: currentColor;
  background: var(--machinome-nav-bg);
  color: var(--machinome-nav-fg);
  font: var(--machinome-nav-font);
}
.machinome-nav-toolbar {
  display: flex;
  justify-content: flex-end;
  padding: 4px 5px;
}
.machinome-nav-full {
  background: transparent;
  border: 0;
  color: var(--machinome-nav-muted);
  cursor: pointer;
  font: inherit;
  padding: 2px 3px;
}
.machinome-nav-full:hover {
  color: var(--machinome-nav-fg-strong);
}
.machinome-nav-row {
  align-items: center;
  border-radius: var(--machinome-nav-row-radius);
  color: var(--machinome-nav-fg);
  cursor: default;
  display: grid;
  gap: var(--machinome-nav-gap);
  grid-template-columns:
    var(--machinome-nav-chip-size) var(--machinome-nav-chip-size) minmax(0, 1fr) auto;
  min-height: var(--machinome-nav-row-min-height);
  padding: var(--machinome-nav-row-padding);
  padding-left: calc(5px + var(--machinome-nav-depth, 0) * var(--machinome-nav-indent));
}
.machinome-nav-row:hover,
.machinome-nav-row--root {
  background: var(--machinome-nav-row-hover-bg);
  color: var(--machinome-nav-fg-strong);
}
.machinome-nav-row--root {
  background: var(--machinome-nav-root-bg);
  box-shadow: inset 2px 0 var(--machinome-nav-root-mark);
}
.machinome-nav-row:focus-visible,
.machinome-nav-visibility:focus-visible,
.machinome-nav-twisty:focus-visible,
.machinome-nav-focus:focus-visible,
.machinome-nav-full:focus-visible {
  outline: 2px solid var(--machinome-nav-focus-ring);
  outline-offset: 1px;
}
.machinome-nav-twisty {
  align-items: center;
  background: transparent;
  border: 0;
  color: inherit;
  cursor: pointer;
  display: flex;
  font: inherit;
  height: var(--machinome-nav-chip-size);
  justify-content: center;
  line-height: 1;
  padding: 0;
  width: var(--machinome-nav-chip-size);
}
.machinome-nav-spacer {
  height: var(--machinome-nav-chip-size);
  width: var(--machinome-nav-chip-size);
}
.machinome-nav-visibility {
  appearance: none;
  background: transparent;
  border: 1px solid var(--machinome-nav-chip-border);
  border-radius: 2px;
  cursor: pointer;
  height: var(--machinome-nav-chip-size);
  margin: 0;
  width: var(--machinome-nav-chip-size);
}
.machinome-nav-visibility:checked {
  background: var(--machinome-nav-node-color, var(--machinome-nav-chip-neutral));
  border-color: var(--machinome-nav-node-color, var(--machinome-nav-chip-neutral));
}
.machinome-nav-row--obscured .machinome-nav-visibility {
  opacity: var(--machinome-nav-obscured-opacity);
}
.machinome-nav-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.machinome-nav-badge {
  color: var(--machinome-nav-fg-strong);
  font-size: 9px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.machinome-nav-focus {
  background: transparent;
  border: 0;
  color: var(--machinome-nav-muted);
  cursor: pointer;
  font: inherit;
  opacity: 0;
  padding: 2px 3px;
  pointer-events: none;
}
.machinome-nav-row:hover .machinome-nav-focus,
.machinome-nav-row:focus-visible > .machinome-nav-focus,
.machinome-nav-focus:focus-visible {
  opacity: 1;
  pointer-events: auto;
}
`;

function injectStylesheet(doc: Document): void {
  if (doc.getElementById(STYLE_ID)) {
    return;
  }
  const style = doc.createElement('style');
  style.id = STYLE_ID;
  style.textContent = NAVIGATOR_STYLESHEET;
  doc.head.append(style);
}

/** Resolves the mount target, exactly as `viewer.ts`'s `resolveContainer`
 * does (`viewer.ts:1162-1171`) -- duplicated rather than imported,
 * because importing it would drag `viewer.ts`'s renderer into this
 * module's own jsdom test (design D2). */
function resolveTarget(target: HTMLElement | string): HTMLElement {
  if (typeof target !== 'string') {
    return target;
  }
  const element = document.querySelector<HTMLElement>(target);
  if (!element) {
    throw new Error(`machinome-viewer: no element matches "${target}"`);
  }
  return element;
}

/** `[]` is `null` to the focus API (design D4) -- the same conversion the
 * driver chrome's breadcrumb already makes (`viewer.ts:1302-1303`). */
function focusPath(path: AssemblyPath): AssemblyPath | null {
  return path.length === 0 ? null : path;
}

export function mountNavigator(
  target: HTMLElement | string,
  viewer: ViewerHandle,
  options: NavigatorOptions = {},
): NavigatorHandle {
  const container = resolveTarget(target);
  const doc = container.ownerDocument;
  const label = options.label ?? 'Assembly';
  const showFullAssembly = options.fullAssembly ?? true;
  const stylesMode = options.styles ?? 'inject';

  if (stylesMode === 'inject') {
    injectStylesheet(doc);
  }

  const navRoot = doc.createElement('div');
  navRoot.className = options.className ? `machinome-nav ${options.className}` : 'machinome-nav';

  const toolbar = doc.createElement('div');
  toolbar.className = 'machinome-nav-toolbar';

  const treeEl = doc.createElement('div');
  treeEl.className = 'machinome-nav-tree';
  treeEl.setAttribute('role', 'tree');
  treeEl.setAttribute('aria-label', label);

  navRoot.append(toolbar, treeEl);
  container.append(navRoot);

  let disposed = false;
  // The navigator's OWN state (design D8): the viewer never sees it, and
  // it survives independently of `currentAssembly`/`currentNavigation`
  // below, which are always the viewer's last-published values.
  let local: NavigatorLocal | null = null;
  let rows: NavigatorRow[] = [];
  let currentAssembly: AssemblyNode = viewer.assembly();
  let currentNavigation: AssemblyNavigationState | null = null;
  const rowElements = new Map<string, HTMLElement>();
  // The reverse map, for the row an event actually landed on: a pointer
  // focuses whatever row it clicks, so the keyboard acts on the row that
  // HOLDS focus, not on the row the navigator last remembered.
  const rowKeys = new WeakMap<HTMLElement, string>();

  /** Every call into the viewer is wrapped here (design D10): a refused
   * or impossible call (the viewer disposed first, an ambiguous path)
   * reports to `console.error` and changes nothing on screen, mirroring
   * `AssemblyChangeNotifier`'s own defensiveness against a throwing
   * listener (`assembly.ts:113-121`). */
  function safelyCall(action: () => void): void {
    try {
      action();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('machinome-viewer: a navigator gesture into the viewer failed', error);
    }
  }

  function isFocusInsideTree(): boolean {
    const active = doc.activeElement;
    return active !== null && treeEl.contains(active);
  }

  function focusActiveRow(preventScroll = true): void {
    if (!local || local.active === null) {
      return;
    }
    // Restoring focus after a redraw must not move the maker's viewport.
    // Only explicit keyboard traversal should reveal an off-screen row.
    rowElements.get(local.active)?.focus({ preventScroll });
  }

  function buildToolbar(): void {
    toolbar.replaceChildren();
    if (!showFullAssembly || currentNavigation === null || currentNavigation.root === null) {
      return;
    }
    const button = doc.createElement('button');
    button.type = 'button';
    button.className = 'machinome-nav-full';
    button.tabIndex = -1;
    button.textContent = 'Show full assembly';
    button.addEventListener('click', () => {
      handleAction({ type: 'focus', path: null });
    });
    toolbar.append(button);
  }

  function buildRow(row: NavigatorRow): HTMLElement {
    const el = doc.createElement('div');
    const modifiers = [
      row.root ? 'machinome-nav-row--root' : '',
      row.hidden ? 'machinome-nav-row--hidden' : '',
      row.obscured ? 'machinome-nav-row--obscured' : '',
      row.expandable ? '' : 'machinome-nav-row--leaf',
    ].filter((name) => name !== '').join(' ');
    el.className = modifiers ? `machinome-nav-row ${modifiers}` : 'machinome-nav-row';
    el.setAttribute('role', 'treeitem');
    el.setAttribute('aria-selected', String(row.root));
    if (row.expandable) {
      el.setAttribute('aria-expanded', String(row.expanded));
    }
    el.tabIndex = row.active ? 0 : -1;
    el.style.setProperty('--machinome-nav-depth', String(row.depth));
    el.style.setProperty(
      '--machinome-nav-node-color', row.color ?? 'var(--machinome-nav-chip-neutral)');

    if (row.expandable) {
      const twisty = doc.createElement('button');
      twisty.type = 'button';
      twisty.className = 'machinome-nav-twisty';
      twisty.tabIndex = -1;
      twisty.setAttribute(
        'aria-label', `${row.expanded ? 'Collapse' : 'Expand'} ${row.node.name}`);
      twisty.textContent = row.expanded ? '−' : '+';
      twisty.addEventListener('click', (event) => {
        event.stopPropagation();
        handleAction(row.expanded
          ? { type: 'collapse', key: row.key } : { type: 'expand', key: row.key });
      });
      el.append(twisty);
    } else {
      const spacer = doc.createElement('span');
      spacer.className = 'machinome-nav-spacer';
      el.append(spacer);
    }

    const chip = chipState(row);
    const checkbox = doc.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'machinome-nav-visibility';
    checkbox.tabIndex = -1;
    checkbox.checked = chip.checked;
    checkbox.setAttribute('aria-label', chip.label);
    checkbox.addEventListener('click', (event) => event.stopPropagation());
    checkbox.addEventListener('change', () => {
      // Read .checked into the argument HERE, at call time: the redraw
      // this triggers may detach `checkbox` before `handleAction`
      // returns (design D10), so it is never read again afterwards.
      handleAction({ type: 'visibility', path: row.node.path, visible: checkbox.checked });
    });
    el.append(checkbox);

    const name = doc.createElement('span');
    name.className = 'machinome-nav-name';
    name.textContent = row.node.name;
    name.title = row.node.name;
    el.append(name);

    if (row.root) {
      const badge = doc.createElement('span');
      badge.className = 'machinome-nav-badge';
      badge.textContent = 'root';
      el.append(badge);
    } else {
      const focusButton = doc.createElement('button');
      focusButton.type = 'button';
      focusButton.className = 'machinome-nav-focus';
      focusButton.tabIndex = -1;
      focusButton.setAttribute('aria-label', `Focus ${row.node.name}`);
      focusButton.textContent = 'Focus';
      focusButton.addEventListener('click', (event) => {
        event.stopPropagation();
        if (local) {
          local.active = row.key;
        }
        handleAction({ type: 'focus', path: focusPath(row.node.path) });
      });
      el.append(focusButton);
    }

    return el;
  }

  function buildRows(): void {
    rowElements.clear();
    treeEl.replaceChildren();
    rows.forEach((row) => {
      const el = buildRow(row);
      rowElements.set(row.key, el);
      rowKeys.set(el, row.key);
      treeEl.append(el);
    });
  }

  /** A row that receives focus by any route -- Tab onto the tab stop, a
   * key, or a pointer click -- becomes the active row: the roving tab
   * stop moves to it without a rebuild and without moving focus again,
   * so the next key acts on the row the maker is actually on. */
  function activate(key: string): void {
    if (!local || local.active === key) {
      return;
    }
    const previous = local.active === null ? undefined : rowElements.get(local.active);
    if (previous) {
      previous.tabIndex = -1;
    }
    local.active = key;
    const next = rowElements.get(key);
    if (next) {
      next.tabIndex = 0;
    }
  }

  /** The ONE place a local-only change (expansion, the active row)
   * repaints: no viewer call, no notification -- the viewer has no
   * opinion about either (design D8). */
  function rerenderLocal(focusAfter: boolean): void {
    if (!local) {
      return;
    }
    rows = navigatorRows(currentAssembly, currentNavigation ?? { root: null, hidden: [] }, local);
    buildToolbar();
    buildRows();
    if (focusAfter) {
      focusActiveRow();
    }
  }

  /** The ONE place a change FROM the viewer repaints: the initial
   * synchronous draw and every `onAssemblyChange` notification alike
   * (design D1, D9). Reconciles local state against the fresh tree,
   * decides whether keyboard focus was inside the tree BEFORE the old
   * rows are replaced, and restores it to the (possibly different)
   * active row afterwards. */
  function applyChange(assembly: AssemblyNode, navigation: AssemblyNavigationState): void {
    const focusWasInside = isFocusInsideTree();
    const previousRoot = currentNavigation?.root ?? null;
    currentAssembly = assembly;
    currentNavigation = navigation;
    local = reconcileLocal(assembly, navigation, local, previousRoot);
    rows = navigatorRows(assembly, navigation, local);
    buildToolbar();
    buildRows();
    if (focusWasInside) {
      focusActiveRow();
    }
  }

  /** Every gesture's effect, decided by `keyAction` or a pointer handler
   * (design D3): `move`/`expand`/`collapse` are entirely local; `focus`
   * and `visibility` are calls into the viewer, wrapped so a refusal
   * changes nothing on screen (design D10). */
  function handleAction(action: NavigatorAction): void {
    if (!local) {
      return;
    }
    switch (action.type) {
      case 'move':
        activate(action.key);
        focusActiveRow(false);
        break;
      case 'expand':
        activate(action.key);
        local.expanded.add(action.key);
        rerenderLocal(true);
        break;
      case 'collapse':
        activate(action.key);
        local.expanded.delete(action.key);
        rerenderLocal(true);
        break;
      case 'focus':
        safelyCall(() => viewer.setRoot(action.path));
        break;
      case 'visibility':
        safelyCall(() => viewer.setVisible(action.path, action.visible));
        break;
      /* istanbul ignore next -- NavigatorAction is a closed union */
      default:
        break;
    }
  }

  treeEl.addEventListener('focusin', (event) => {
    const row = event.target instanceof HTMLElement
      ? event.target.closest<HTMLElement>('.machinome-nav-row') : null;
    const key = row ? rowKeys.get(row) : undefined;
    if (key !== undefined) {
      activate(key);
    }
  });

  treeEl.addEventListener('keydown', (event) => {
    // Only a ROW answers the keyboard contract. A key on a row's own
    // control -- the checkbox a pointer left focused -- keeps its native
    // meaning, so Space there toggles that checkbox and nothing else.
    const key = event.target instanceof HTMLElement ? rowKeys.get(event.target) : undefined;
    if (!local || key === undefined) {
      return;
    }
    activate(key);
    const action = keyAction(rows, key, event.key);
    if (!action) {
      return;
    }
    event.preventDefault();
    handleAction(action);
  });

  // Synchronous: no notification is needed to draw the first tree
  // (design D1). Reading before subscribing is safe because this is one
  // turn -- the viewer notifies only from an operation, and no operation
  // can interleave with this call.
  applyChange(currentAssembly, viewer.navigation());

  const onChange: AssemblyListener = (change: AssemblyChange) => {
    applyChange(change.assembly, change.navigation);
  };
  const unsubscribe = viewer.onAssemblyChange(onChange);

  return {
    dispose(): void {
      if (disposed) {
        return;
      }
      disposed = true;
      unsubscribe();
      container.replaceChildren();
    },
  };
}
