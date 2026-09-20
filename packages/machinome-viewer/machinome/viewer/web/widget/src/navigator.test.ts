/**
 * @vitest-environment jsdom
 */
/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The component itself, against a STUB handle -- the whole surface the
// navigator uses (`assembly`, `navigation`, `setRoot`, `setVisible`,
// `onAssemblyChange`), never a renderer (design D2, D16). Scoped to jsdom
// by the docblock above, per file, so the other 29+ files keep running in
// `node` exactly as they do today.

import {
  afterEach, beforeEach, describe, expect, it, vi,
} from 'vitest';
import type { AssemblyChange, AssemblyListener, AssemblyNavigationState } from './assembly';
import { mountNavigator, NavigatorHandle } from './navigator';
import type { AssemblyNode } from './tree';
import type { ViewerHandle } from './viewer';

// The same shape as navtree.test.ts's fixture: a coloured branch two
// deep (A -> B, B inheriting A's already-resolved colour) and a leaf
// sibling, so expand/collapse, focus and hide/obscure all have something
// real to act on.
function leaf(): AssemblyNode {
  return { name: 'Leaf', path: ['Leaf'], color: null, model: true, children: [] };
}
function nodeB(): AssemblyNode {
  return { name: 'B', path: ['A', 'B'], color: '#ff0000', model: true, children: [] };
}
function nodeA(): AssemblyNode {
  return { name: 'A', path: ['A'], color: '#ff0000', model: false, children: [nodeB()] };
}
function tree(): AssemblyNode {
  return { name: 'Root', path: [], color: null, model: false, children: [nodeA(), leaf()] };
}

/** A working fake of the surface `navigator.ts` uses (design D16's
 * "stub" is an object literal with these five methods): `setRoot` and
 * `setVisible` mutate the state and notify synchronously, before they
 * return -- exactly as the real handle does (ADR-049 §6, design D10). */
class StubHandle {
  assemblyTree: AssemblyNode = tree();
  hidden = new Set<string>();
  root: string[] | null = null;
  listener: AssemblyListener | null = null;
  calls: { setRoot: Array<string[] | null>; setVisible: Array<[string[], boolean]> } = {
    setRoot: [], setVisible: [],
  };
  throwOnSetRoot = false;
  throwOnSetVisible = false;

  assembly = (): AssemblyNode => this.assemblyTree;

  navigation = (): AssemblyNavigationState => ({
    root: this.root,
    hidden: [...this.hidden].map((key) => JSON.parse(key)),
  });

  setRoot = (path: string[] | null): void => {
    this.calls.setRoot.push(path);
    if (this.throwOnSetRoot) {
      throw new Error('setRoot refused');
    }
    this.root = path;
    this.notify();
  };

  setVisible = (path: string[], visible: boolean): void => {
    this.calls.setVisible.push([path, visible]);
    if (this.throwOnSetVisible) {
      throw new Error('setVisible refused');
    }
    const key = JSON.stringify(path);
    if (visible) {
      this.hidden.delete(key);
    } else {
      this.hidden.add(key);
    }
    this.notify();
  };

  onAssemblyChange = (listener: AssemblyListener): (() => void) => {
    this.listener = listener;
    return () => { this.listener = null; };
  };

  notify(): void {
    this.listener?.({ assembly: this.assemblyTree, navigation: this.navigation() });
  }

  /** Push a change the navigator did not ask for -- a targeted update or
   * another host's call, standing in for `AssemblyChange`. */
  push(change: AssemblyChange): void {
    this.listener?.(change);
  }
}

function asHandle(stub: StubHandle): ViewerHandle {
  return stub as unknown as ViewerHandle;
}

let container: HTMLElement;
const handles: NavigatorHandle[] = [];

beforeEach(() => {
  container = document.createElement('div');
  document.body.append(container);
});

afterEach(() => {
  handles.splice(0).forEach((handle) => handle.dispose());
  document.body.replaceChildren();
  document.getElementById('machinome-navigator-style')?.remove();
  vi.restoreAllMocks();
});

function mount(stub: StubHandle, options?: Parameters<typeof mountNavigator>[2]) {
  const handle = mountNavigator(container, asHandle(stub), options);
  handles.push(handle);
  return handle;
}

function rowFor(name: string): HTMLElement {
  const row = [...container.querySelectorAll<HTMLElement>('.machinome-nav-row')]
    .find((element) => element.querySelector('.machinome-nav-name')?.textContent === name);
  if (!row) throw new Error(`no row for ${name}`);
  return row;
}

/** Dispatches a real keydown on whichever element currently holds DOM
 * focus (`document.activeElement`). A row reached by any route -- Tab
 * onto the tab stop, a key, or a pointer click (which `.focus()` stands
 * in for here) -- is the row the keys act on. */
function press(key: string): KeyboardEvent {
  const event = new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true });
  (document.activeElement as HTMLElement).dispatchEvent(event);
  return event;
}

describe('mounting', () => {
  it('exposes the complete part name as a hover tooltip', () => {
    const stub = new StubHandle();
    const name = 'A very long part name that cannot fit in the model sidebar';
    stub.assemblyTree.children[0].name = name;
    mount(stub);
    expect(rowFor(name).querySelector('.machinome-nav-name')!.getAttribute('title')).toBe(name);
  });

  it('draws the tree before returning, with no change notified', () => {
    const stub = new StubHandle();
    mount(stub);

    const treeEl = container.querySelector('[role="tree"]');
    expect(treeEl).not.toBeNull();
    expect(treeEl!.getAttribute('aria-label')).toBe('Assembly');
    const items = container.querySelectorAll('[role="treeitem"]');
    // First render expands only the document root (design D9): Root, A, Leaf.
    expect(items.length).toBe(3);
  });

  it('expands only rows with children, and reflects their expanded state', () => {
    const stub = new StubHandle();
    mount(stub);
    const rootRow = rowFor('Root');
    const aRow = rowFor('A');
    const leafRow = rowFor('Leaf');
    expect(rootRow.getAttribute('aria-expanded')).toBe('true');
    expect(aRow.getAttribute('aria-expanded')).toBe('false');
    expect(leafRow.hasAttribute('aria-expanded')).toBe(false);
  });

  it('marks the focused viewer root with aria-selected, and no other row', () => {
    const stub = new StubHandle();
    stub.root = ['A'];
    mount(stub);
    expect(rowFor('A').getAttribute('aria-selected')).toBe('true');
    expect(rowFor('Root').getAttribute('aria-selected')).toBe('false');
  });

  it('has exactly one tab stop, and no other focusable element in the tree', () => {
    const stub = new StubHandle();
    mount(stub);
    const rows = [...container.querySelectorAll<HTMLElement>('[role="treeitem"]')];
    const tabbable = rows.filter((row) => row.tabIndex === 0);
    expect(tabbable.length).toBe(1);
    rows.filter((row) => row.tabIndex !== 0).forEach((row) => expect(row.tabIndex).toBe(-1));
    const others = container.querySelectorAll<HTMLElement>(
      '.machinome-nav-twisty, .machinome-nav-visibility, .machinome-nav-focus, .machinome-nav-full');
    others.forEach((element) => expect(element.tabIndex).toBe(-1));
  });

  it('writes each row\'s label, depth and colour', () => {
    const stub = new StubHandle();
    mount(stub);
    const aRow = rowFor('A');
    expect(aRow.querySelector('.machinome-nav-name')!.textContent).toBe('A');
    expect(aRow.style.getPropertyValue('--machinome-nav-depth')).toBe('1');
    expect(aRow.style.getPropertyValue('--machinome-nav-node-color')).toBe('#ff0000');
    expect(rowFor('Root').style.getPropertyValue('--machinome-nav-depth')).toBe('0');
  });

  it('shows the four chip states of design D5', () => {
    const stub = new StubHandle();
    stub.hidden.add(JSON.stringify(['A']));
    mount(stub);

    const aChip = rowFor('A').querySelector<HTMLInputElement>('.machinome-nav-visibility')!;
    expect(aChip.checked).toBe(false);
    expect(aChip.getAttribute('aria-label')).toBe('Visibility for A');
    expect(rowFor('A').className).toContain('machinome-nav-row--hidden');
    expect(rowFor('A').className).not.toContain('machinome-nav-row--obscured');

    const leafChip = rowFor('Leaf').querySelector<HTMLInputElement>('.machinome-nav-visibility')!;
    expect(leafChip.checked).toBe(true);
    expect(leafChip.getAttribute('aria-label')).toBe('Visibility for Leaf');
  });

  it('marks an obscured descendant, keeping its own checked state', () => {
    const stub = new StubHandle();
    stub.hidden.add(JSON.stringify(['A']));
    mount(stub, { fullAssembly: true });
    // Reach A the only way a keyboard maker can -- Tab lands on the one
    // tab stop (Root, active by default), then Down -- and expand it.
    rowFor('Root').focus();
    press('ArrowDown');
    press('ArrowRight');

    const bChip = rowFor('B').querySelector<HTMLInputElement>('.machinome-nav-visibility')!;
    expect(bChip.checked).toBe(true);
    expect(bChip.getAttribute('aria-label')).toBe('Visibility for B (hidden with A)');
    expect(rowFor('B').className).toContain('machinome-nav-row--obscured');
    expect(rowFor('B').className).not.toContain('machinome-nav-row--hidden');
  });
});

describe('keyboard', () => {
  it('moves keyboard focus with Down and Up, suppressing the default', () => {
    const stub = new StubHandle();
    mount(stub);
    rowFor('Root').focus();
    const down = press('ArrowDown');
    expect(document.activeElement).toBe(rowFor('A'));
    expect(down.defaultPrevented).toBe(true);

    const up = press('ArrowUp');
    expect(document.activeElement).toBe(rowFor('Root'));
    expect(up.defaultPrevented).toBe(true);
  });

  it('expands with Right and collapses with Left', () => {
    const stub = new StubHandle();
    mount(stub);
    rowFor('Root').focus();
    press('ArrowDown'); // Root -> A
    press('ArrowRight'); // expands A, stays on A
    expect(rowFor('A').getAttribute('aria-expanded')).toBe('true');
    expect(() => rowFor('B')).not.toThrow();

    press('ArrowLeft'); // collapses A, stays on A
    expect(rowFor('A').getAttribute('aria-expanded')).toBe('false');
  });

  it('focuses the viewer with Enter, passing null for the root row', () => {
    const stub = new StubHandle();
    mount(stub);
    rowFor('Root').focus();
    press('Enter');
    expect(stub.calls.setRoot).toEqual([null]);

    press('ArrowDown'); // Root -> A
    press('Enter');
    expect(stub.calls.setRoot).toEqual([null, ['A']]);
  });

  it('toggles visibility with Space, carrying the inverse of the row\'s own hidden', () => {
    const stub = new StubHandle();
    mount(stub);
    rowFor('Root').focus();
    press('ArrowDown'); // Root -> A
    press(' ');
    expect(stub.calls.setVisible).toEqual([[['A'], false]]);

    press(' ');
    expect(stub.calls.setVisible).toEqual([[['A'], false], [['A'], true]]);
  });
});

describe('keyboard on a row reached by pointer', () => {
  it('acts on the row that holds focus, not the row last remembered', () => {
    const stub = new StubHandle();
    mount(stub);
    rowFor('A').focus(); // a pointer click on A's blank area lands here
    expect(rowFor('A').tabIndex).toBe(0);
    expect(rowFor('Root').tabIndex).toBe(-1);
    press('ArrowUp');
    expect(document.activeElement).toBe(rowFor('Root'));
  });

  it('leaves a row\'s own control its native keys', () => {
    const stub = new StubHandle();
    mount(stub);
    const checkbox = rowFor('A').querySelector<HTMLInputElement>('.machinome-nav-visibility')!;
    checkbox.focus();
    const space = press(' ');
    expect(space.defaultPrevented).toBe(false);
    expect(stub.calls.setVisible).toEqual([]);
  });
});

describe('show full assembly', () => {
  it('appears only when a subtree is focused, and restores the document root', () => {
    const stub = new StubHandle();
    stub.root = ['A'];
    mount(stub);
    const button = container.querySelector<HTMLButtonElement>('.machinome-nav-full');
    expect(button).not.toBeNull();
    button!.click();
    expect(stub.calls.setRoot).toEqual([null]);
  });

  it('is absent when the document root is already focused', () => {
    const stub = new StubHandle();
    mount(stub);
    expect(container.querySelector('.machinome-nav-full')).toBeNull();
  });

  it('is suppressed entirely under fullAssembly: false', () => {
    const stub = new StubHandle();
    stub.root = ['A'];
    mount(stub, { fullAssembly: false });
    expect(container.querySelector('.machinome-nav-full')).toBeNull();
  });
});

describe('following the viewer', () => {
  it('redraws from a pushed change it never asked for, calling nothing back', () => {
    const stub = new StubHandle();
    mount(stub);
    const before = stub.calls.setRoot.length + stub.calls.setVisible.length;

    stub.push({
      assembly: tree(),
      navigation: { root: ['A'], hidden: [] },
    });

    expect(rowFor('A').getAttribute('aria-selected')).toBe('true');
    expect(stub.calls.setRoot.length + stub.calls.setVisible.length).toBe(before);
  });

  it('reconciles a pruned tree: drops removed rows, keeps surviving expansion, restores focus', () => {
    const stub = new StubHandle();
    mount(stub);
    rowFor('Root').focus();
    press('ArrowDown'); // Root -> A
    press('ArrowRight'); // expands A
    press('ArrowDown'); // A -> B
    expect(document.activeElement).toBe(rowFor('B'));

    const pruned: AssemblyNode = { ...tree(), children: [leaf()] };
    stub.push({ assembly: pruned, navigation: { root: null, hidden: [] } });

    expect(() => rowFor('A')).toThrow();
    expect(() => rowFor('B')).toThrow();
    // The active row fell back to the document root, and focus moved
    // with it because it was inside the tree at the time of the change.
    expect(document.activeElement).toBe(rowFor('Root'));
  });
});

describe('the stylesheet', () => {
  it('injects exactly one identifiable stylesheet across two mounts', () => {
    const stub = new StubHandle();
    mount(stub);
    const second = document.createElement('div');
    document.body.append(second);
    handles.push(mountNavigator(second, asHandle(new StubHandle())));

    expect(document.querySelectorAll('#machinome-navigator-style').length).toBe(1);
  });

  it('injects nothing under styles: none', () => {
    const stub = new StubHandle();
    mount(stub, { styles: 'none' });
    expect(document.getElementById('machinome-navigator-style')).toBeNull();
    // The class contract is still there for a host's own stylesheet.
    expect(container.querySelector('.machinome-nav')).not.toBeNull();
  });

  it('puts a host\'s className on the navigator root', () => {
    const stub = new StubHandle();
    mount(stub, { className: 'studio-panel' });
    const root = container.querySelector('.machinome-nav')!;
    expect(root.className.split(' ')).toContain('studio-panel');
  });
});

describe('synchronous redraw inside a gesture (design D10)', () => {
  it('rebuilds the tree inside the click, and restores focus to the active row', () => {
    const stub = new StubHandle();
    mount(stub);
    const rootRow = rowFor('Root');
    rootRow.focus();
    expect(document.activeElement).toBe(rootRow);

    const before = rowFor('A').querySelector<HTMLInputElement>('.machinome-nav-visibility')!;
    before.focus();
    expect(() => before.click()).not.toThrow();

    const after = rowFor('A').querySelector<HTMLInputElement>('.machinome-nav-visibility')!;
    expect(after).not.toBe(before);
    expect(after.checked).toBe(false);
    // Operating A's checkbox makes A active; returning to the previously
    // active Root was the cause of Studio's hide/show scroll jump.
    expect(document.activeElement).toBe(rowFor('A'));
  });
});

describe('disposal', () => {
  it('unsubscribes and empties the target, and is safe to call twice', () => {
    const stub = new StubHandle();
    const handle = mountNavigator(container, asHandle(stub));
    expect(container.children.length).toBeGreaterThan(0);
    expect(stub.listener).not.toBeNull();

    handle.dispose();
    expect(container.children.length).toBe(0);
    expect(stub.listener).toBeNull();

    expect(() => handle.dispose()).not.toThrow();
  });

  it('does not throw out of a click when the viewer refuses the call', () => {
    const stub = new StubHandle();
    stub.throwOnSetRoot = true;
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    mount(stub);

    expect(() => {
      rowFor('Root').focus();
      press('Enter');
    }).not.toThrow();
    // eslint-disable-next-line no-console
    expect(console.error).toHaveBeenCalled();
  });
});

describe('refusal', () => {
  it('refuses a selector matching no element, naming it', () => {
    const stub = new StubHandle();
    expect(() => mountNavigator('#does-not-exist', asHandle(stub)))
      .toThrow('machinome-viewer: no element matches "#does-not-exist"');
  });
});
