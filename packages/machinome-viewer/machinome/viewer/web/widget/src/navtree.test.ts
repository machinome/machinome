/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Every decision the navigator makes, made here where it can be tested
// (design D3, `controls.test.ts`'s own pattern): what rows are presented,
// what depth and colour they carry, which is the focused root, hidden vs
// obscured, every keyboard transition and every reconciliation rule. No
// DOM, so this runs in the suite's default `node` environment exactly as
// `controls.test.ts` does.

import { describe, expect, it } from 'vitest';
import { AssemblyNavigationState } from './assembly';
import {
  chipState, keyAction, NavigatorLocal, navigatorRows, reconcileLocal,
} from './navtree';
import { AssemblyNode, assemblyPathKey } from './tree';

// One tree, reused across every test: a root with a coloured child `A`
// that has its own child `B` (inheriting A's colour, resolved already --
// `AssemblyNode.color` is always the EFFECTIVE colour, tree.ts's job,
// never this module's), and a leaf sibling `Leaf`.
const leaf = (): AssemblyNode => ({
  name: 'Leaf', path: ['Leaf'], color: null, model: true, children: [],
});
const nodeB = (): AssemblyNode => ({
  name: 'B', path: ['A', 'B'], color: '#ff0000', model: true, children: [],
});
const nodeA = (): AssemblyNode => ({
  name: 'A', path: ['A'], color: '#ff0000', model: false, children: [nodeB()],
});
const root = (): AssemblyNode => ({
  name: 'Root', path: [], color: null, model: false, children: [nodeA(), leaf()],
});

const rootKey = assemblyPathKey([]);
const keyA = assemblyPathKey(['A']);
const keyB = assemblyPathKey(['A', 'B']);
const keyLeaf = assemblyPathKey(['Leaf']);

const nav = (overrides: Partial<AssemblyNavigationState> = {}): AssemblyNavigationState => ({
  root: null, hidden: [], ...overrides,
});

const local = (overrides: Partial<NavigatorLocal> = {}): NavigatorLocal => ({
  expanded: new Set(), active: null, ...overrides,
});

describe('navigatorRows', () => {
  it('presents the root alone when nothing is expanded', () => {
    const rows = navigatorRows(root(), nav(), local());
    expect(rows.map((row) => row.key)).toEqual([rootKey]);
  });

  it('presents the root and its children once the root is expanded', () => {
    const rows = navigatorRows(root(), nav(), local({ expanded: new Set([rootKey]) }));
    expect(rows.map((row) => row.key)).toEqual([rootKey, keyA, keyLeaf]);
  });

  it('goes deeper only under an expanded parent, depth-first', () => {
    const rows = navigatorRows(
      root(), nav(), local({ expanded: new Set([rootKey, keyA]) }));
    expect(rows.map((row) => row.key)).toEqual([rootKey, keyA, keyB, keyLeaf]);
    expect(rows.map((row) => row.depth)).toEqual([0, 1, 2, 1]);
  });

  it('marks expandable off a node\'s own children', () => {
    const rows = navigatorRows(
      root(), nav(), local({ expanded: new Set([rootKey, keyA]) }));
    const byKey = new Map(rows.map((row) => [row.key, row]));
    expect(byKey.get(rootKey)!.expandable).toBe(true);
    expect(byKey.get(keyA)!.expandable).toBe(true);
    expect(byKey.get(keyB)!.expandable).toBe(false);
    expect(byKey.get(keyLeaf)!.expandable).toBe(false);
  });

  it('keys rows by assemblyPathKey, the key the viewer hides by', () => {
    const rows = navigatorRows(root(), nav(), local({ expanded: new Set([rootKey]) }));
    expect(rows.find((row) => row.node.name === 'A')!.key).toBe(assemblyPathKey(['A']));
  });

  it('marks the depth-0 row as root when navigation.root is null', () => {
    const rows = navigatorRows(root(), nav({ root: null }), local({ expanded: new Set([rootKey]) }));
    expect(rows.find((row) => row.key === rootKey)!.root).toBe(true);
    expect(rows.find((row) => row.key === keyA)!.root).toBe(false);
  });

  it('marks the named row as root when navigation.root is a path', () => {
    const rows = navigatorRows(root(), nav({ root: ['A'] }), local({ expanded: new Set([rootKey]) }));
    expect(rows.find((row) => row.key === keyA)!.root).toBe(true);
    expect(rows.find((row) => row.key === rootKey)!.root).toBe(false);
  });

  it('marks no row as root when the focused path is not currently shown', () => {
    // navigation.root names A/B, but A itself is not expanded, so B's
    // row is not among the presented rows at all.
    const rows = navigatorRows(
      root(), nav({ root: ['A', 'B'] }), local({ expanded: new Set([rootKey]) }));
    expect(rows.some((row) => row.root)).toBe(false);
  });

  it('marks a hidden node hidden and its descendant only obscured', () => {
    const rows = navigatorRows(
      root(), nav({ hidden: [['A']] }), local({ expanded: new Set([rootKey, keyA]) }));
    const byKey = new Map(rows.map((row) => [row.key, row]));
    expect(byKey.get(keyA)!.hidden).toBe(true);
    expect(byKey.get(keyA)!.obscured).toBe(false);
    expect(byKey.get(keyB)!.hidden).toBe(false);
    expect(byKey.get(keyB)!.obscured).toBe(true);
    expect(byKey.get(keyB)!.hidingAncestor).toBe('A');
  });

  it('marks a descendant that is itself hidden as both hidden and obscured', () => {
    const rows = navigatorRows(
      root(), nav({ hidden: [['A'], ['A', 'B']] }),
      local({ expanded: new Set([rootKey, keyA]) }));
    const byKey = new Map(rows.map((row) => [row.key, row]));
    expect(byKey.get(keyB)!.hidden).toBe(true);
    expect(byKey.get(keyB)!.obscured).toBe(true);
  });

  it('leaves the descendant hidden-only once the parent is shown again', () => {
    const rows = navigatorRows(
      root(), nav({ hidden: [['A', 'B']] }), local({ expanded: new Set([rootKey, keyA]) }));
    const byKey = new Map(rows.map((row) => [row.key, row]));
    expect(byKey.get(keyA)!.hidden).toBe(false);
    expect(byKey.get(keyB)!.hidden).toBe(true);
    expect(byKey.get(keyB)!.obscured).toBe(false);
  });

  it('carries the node\'s already-effective colour through unchanged', () => {
    const rows = navigatorRows(root(), nav(), local({ expanded: new Set([rootKey]) }));
    expect(rows.find((row) => row.key === rootKey)!.color).toBeNull();
    expect(rows.find((row) => row.key === keyA)!.color).toBe('#ff0000');
  });

  it('marks the active row from local.active', () => {
    const rows = navigatorRows(root(), nav(), local({ active: rootKey }));
    expect(rows[0].active).toBe(true);
  });
});

describe('chipState', () => {
  const rowFor = (overrides: {
    hidden?: boolean; obscured?: boolean; color?: string | null;
    hidingAncestor?: string | null; name?: string;
  } = {}) => {
    const rows = navigatorRows(
      root(), nav({ hidden: overrides.hidden ? [['A']] : [] }),
      local({ expanded: new Set([rootKey, keyA]) }));
    const base = rows.find((row) => row.key === keyA)!;
    return {
      ...base,
      color: overrides.color !== undefined ? overrides.color : base.color,
      obscured: overrides.obscured ?? base.obscured,
      hidingAncestor: overrides.hidingAncestor ?? base.hidingAncestor,
      hidden: overrides.hidden ?? base.hidden,
    };
  };

  it('is checked and coloured for a shown, coloured node', () => {
    const chip = chipState(rowFor({ hidden: false, color: '#ff0000' }));
    expect(chip).toEqual({ checked: true, fill: 'color', label: 'Visibility for A' });
  });

  it('is checked and neutral for a shown, colourless node', () => {
    const chip = chipState(rowFor({ hidden: false, color: null }));
    expect(chip).toEqual({ checked: true, fill: 'neutral', label: 'Visibility for A' });
  });

  it('is unchecked and empty for an explicitly hidden node', () => {
    const chip = chipState(rowFor({ hidden: true }));
    expect(chip).toEqual({ checked: false, fill: 'none', label: 'Visibility for A' });
  });

  it('stays checked, and names the ancestor, for an obscured node', () => {
    const chip = chipState(
      rowFor({ hidden: false, color: '#ff0000', obscured: true, hidingAncestor: 'Root' }));
    expect(chip).toEqual({
      checked: true, fill: 'color', label: 'Visibility for A (hidden with Root)',
    });
  });

  it('is unchecked and names the ancestor when hidden in its own right too', () => {
    const chip = chipState(
      rowFor({ hidden: true, obscured: true, hidingAncestor: 'Root' }));
    expect(chip).toEqual({
      checked: false, fill: 'none', label: 'Visibility for A (hidden with Root)',
    });
  });
});

describe('keyAction', () => {
  // Root and A expanded: root(0) -> A(1) -> B(2) -> Leaf(1).
  const rows = () => navigatorRows(
    root(), nav(), local({ expanded: new Set([rootKey, keyA]) }));
  // Only root expanded: root(0) -> A(1, collapsed) -> Leaf(1).
  const collapsedRows = () => navigatorRows(
    root(), nav(), local({ expanded: new Set([rootKey]) }));

  it('moves down between rows', () => {
    expect(keyAction(rows(), rootKey, 'ArrowDown')).toEqual({ type: 'move', key: keyA });
  });

  it('stays at the last row on Down', () => {
    expect(keyAction(rows(), keyLeaf, 'ArrowDown')).toBeNull();
  });

  it('stays at the first row on Up', () => {
    expect(keyAction(rows(), rootKey, 'ArrowUp')).toBeNull();
  });

  it('moves up between rows', () => {
    expect(keyAction(rows(), keyA, 'ArrowUp')).toEqual({ type: 'move', key: rootKey });
  });

  it('expands a collapsed parent on Right, without moving', () => {
    expect(keyAction(collapsedRows(), keyA, 'ArrowRight')).toEqual({ type: 'expand', key: keyA });
  });

  it('moves into the first child on Right of an already-expanded parent', () => {
    expect(keyAction(rows(), keyA, 'ArrowRight')).toEqual({ type: 'move', key: keyB });
  });

  it('does nothing on Right of a leaf', () => {
    expect(keyAction(rows(), keyLeaf, 'ArrowRight')).toBeNull();
    expect(keyAction(rows(), keyB, 'ArrowRight')).toBeNull();
  });

  it('collapses an expanded parent on Left', () => {
    expect(keyAction(rows(), keyA, 'ArrowLeft')).toEqual({ type: 'collapse', key: keyA });
  });

  it('moves to the parent row on Left of a collapsed parent or a leaf', () => {
    expect(keyAction(rows(), keyB, 'ArrowLeft')).toEqual({ type: 'move', key: keyA });
    expect(keyAction(rows(), keyLeaf, 'ArrowLeft')).toEqual({ type: 'move', key: rootKey });
    expect(keyAction(collapsedRows(), keyA, 'ArrowLeft')).toEqual({ type: 'move', key: rootKey });
  });

  it('does nothing on Left of a collapsed root row', () => {
    const nothingExpanded = navigatorRows(root(), nav(), local());
    expect(keyAction(nothingExpanded, rootKey, 'ArrowLeft')).toBeNull();
  });

  it('yields a focus action carrying null for the root row', () => {
    expect(keyAction(rows(), rootKey, 'Enter')).toEqual({ type: 'focus', path: null });
  });

  it('yields a focus action carrying the path for any other row', () => {
    expect(keyAction(rows(), keyA, 'Enter')).toEqual({ type: 'focus', path: ['A'] });
  });

  it('yields a visibility action carrying the row\'s own hidden on Space', () => {
    const hiddenRows = navigatorRows(
      root(), nav({ hidden: [['A']] }), local({ expanded: new Set([rootKey, keyA]) }));
    expect(keyAction(hiddenRows, keyA, ' ')).toEqual({ type: 'visibility', path: ['A'], visible: true });
    expect(keyAction(hiddenRows, keyLeaf, ' ')).toEqual({ type: 'visibility', path: ['Leaf'], visible: false });
  });

  it('yields nothing for a key the contract does not bind', () => {
    expect(keyAction(rows(), rootKey, 'Tab')).toBeNull();
    expect(keyAction(rows(), rootKey, 'a')).toBeNull();
  });

  it('yields nothing when the active key names no presented row', () => {
    expect(keyAction(rows(), 'missing', 'ArrowDown')).toBeNull();
  });
});

describe('reconcileLocal', () => {
  it('expands only the document root on the first reconcile', () => {
    const result = reconcileLocal(root(), nav(), null, null);
    expect(result.expanded).toEqual(new Set([rootKey]));
    expect(result.active).toBe(rootKey);
  });

  it('keeps expanded keys the new tree still has and drops the rest', () => {
    const previous: NavigatorLocal = { expanded: new Set([rootKey, keyA]), active: keyA };
    // A no longer has Leaf's sibling relationship changed; simulate a
    // pruned tree missing A entirely.
    const pruned: AssemblyNode = { ...root(), children: [leaf()] };
    const result = reconcileLocal(pruned, nav(), previous, null);
    expect(result.expanded).toEqual(new Set([rootKey]));
  });

  it('keeps the active row when it survives', () => {
    const previous: NavigatorLocal = { expanded: new Set([rootKey]), active: keyA };
    const result = reconcileLocal(root(), nav(), previous, null);
    expect(result.active).toBe(keyA);
  });

  it('falls back to the root key when the active row no longer exists, never to null', () => {
    const previous: NavigatorLocal = { expanded: new Set([rootKey]), active: keyB };
    const pruned: AssemblyNode = { ...root(), children: [leaf()] };
    const result = reconcileLocal(pruned, nav(), previous, null);
    expect(result.active).toBe(rootKey);
  });

  it('reveals the ancestors of a root that has just moved', () => {
    const previous: NavigatorLocal = { expanded: new Set([rootKey]), active: rootKey };
    const result = reconcileLocal(root(), nav({ root: ['A', 'B'] }), previous, null);
    expect(result.expanded.has(rootKey)).toBe(true);
    expect(result.expanded.has(keyA)).toBe(true);
  });

  it('does not re-expand a collapsed ancestor when the root did not move', () => {
    // The root already sits at ['A', 'B'] on both the previous and the
    // current render -- the maker has since collapsed A by hand.
    const previous: NavigatorLocal = { expanded: new Set([rootKey]), active: rootKey };
    const result = reconcileLocal(root(), nav({ root: ['A', 'B'] }), previous, ['A', 'B']);
    expect(result.expanded.has(keyA)).toBe(false);
  });
});
