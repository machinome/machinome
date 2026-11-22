/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// Every decision the navigator makes, made here where it can be tested
// (design D3, `controls.test.ts`'s own pattern): what rows are presented,
// what depth and colour they carry, which is the focused root, hidden vs
// obscured, every keyboard transition and every reconciliation rule. No
// DOM, so this runs in the suite's default `node` environment exactly as
// `controls.test.ts` does.

import * as THREE from 'three';
import { describe, expect, it, vi } from 'vitest';

// The marked document's meshes are never the question here, so the
// loader is stood in for exactly as `tree.test.ts` stands it in.
vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({
  STLLoader: class {
    loadAsync = () => Promise.resolve(new THREE.BoxGeometry());
  },
}));
import { AssemblyNavigationState } from './assembly';
import {
  chipState, keyAction, NavigatorLocal, navigatorRows, reconcileLocal,
} from './navtree';
import { AssemblyNode, assemblyPathKey, WidgetTree } from './tree';
import { ManifestNode } from './types';
import markedManifest from '../../../../../tests/fixtures/marked/manifest.json';

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

// OpenSpec `draw-what-a-part-carries`, design D7: a marking is NO ROW of
// the navigator. `navigatorRows` walks `AssemblyNode.children`, and
// `assembly()` builds those from `WidgetTree` children only, so a
// marking cannot become a row -- excluded by construction. Pinned all
// the same, on the framework's own marked document, because "by
// construction" is a property of today's code.
describe('navigatorRows over a marked document', () => {
  const stripMarkings = (node: ManifestNode): ManifestNode => {
    const { markings, ...rest } = node as ManifestNode & { markings?: unknown };
    void markings;
    return { ...rest, children: node.children?.map(stripMarkings) } as ManifestNode;
  };

  const rowsFor = async (manifestRoot: ManifestNode) => {
    const tree = new WidgetTree(manifestRoot, '/build/');
    await tree.loaded;
    const assembly = tree.assembly();
    const expanded = new Set<string>();
    const collect = (node: AssemblyNode) => {
      expanded.add(assemblyPathKey(node.path));
      node.children.forEach(collect);
    };
    collect(assembly);
    return navigatorRows(assembly, nav(), local({ expanded }));
  };

  it('presents one row per part and none for any marking', async () => {
    const document = markedManifest as unknown as { root: ManifestNode };
    const marked = await rowsFor(document.root);
    const twin = await rowsFor(stripMarkings(document.root));

    expect(marked.map((row) => row.node.name)).toEqual(['Bench', 'dial', 'plate']);
    expect(marked.map((row) => row.key)).toEqual(twin.map((row) => row.key));
    expect(marked.map((row) => [row.node.name, row.depth, row.node.color, row.color]))
      .toEqual(twin.map((row) => [row.node.name, row.depth, row.node.color, row.color]));
    for (const name of ['digits', 'badge', 'band']) {
      expect(marked.some((row) => row.node.name === name)).toBe(false);
    }
  });
});

// OpenSpec `colour-a-node-by-what-it-holds` (design Decision 8, N1 to
// N11 and N13): a row without children shows its node's effective
// colour, as before; a row with children shows the one colour every part
// beneath it shows, when they all show one, and otherwise what it showed
// before. A part is every node without children beneath the row, and the
// node itself when it has a model of its own. Every tree is written by
// hand, every row is expanded unless the test says otherwise, and every
// assertion reads the rows `navigatorRows` returns.
describe('the colour a row shows', () => {
  type Rows = ReturnType<typeof navigatorRows>;

  const part = (path: string[], color: string | null, model = true): AssemblyNode => ({
    name: path[path.length - 1], path, color, model, children: [],
  });
  const group = (
    path: string[], color: string | null, children: AssemblyNode[], model = false,
  ): AssemblyNode => ({
    name: path.length === 0 ? 'Root' : path[path.length - 1], path, color, model, children,
  });
  const everyKey = (node: AssemblyNode, keys = new Set<string>()): Set<string> => {
    keys.add(assemblyPathKey(node.path));
    node.children.forEach((child) => everyKey(child, keys));
    return keys;
  };
  const rowsOf = (
    tree: AssemblyNode, navigation = nav(), expanded = everyKey(tree),
  ): Rows => navigatorRows(tree, navigation, local({ expanded }));
  const rowAt = (rows: Rows, path: string[]) => {
    const row = rows.find((candidate) => candidate.key === assemblyPathKey(path));
    if (!row) throw new Error(`no row at ${assemblyPathKey(path)}`);
    return row;
  };
  const colourAt = (rows: Rows, path: string[]) => rowAt(rows, path).color;

  // N1: Root -> G -> [p, q]; G has no colour, p and q are both grey.
  const uniform = () => group([], null, [
    group(['G'], null, [part(['G', 'p'], '#a0a0a0'), part(['G', 'q'], '#a0a0a0')]),
  ]);
  // N2: the same shape, its parts of two colours.
  const mixed = () => group([], null, [
    group(['G'], null, [part(['G', 'p'], '#a0a0a0'), part(['G', 'q'], '#191919')]),
  ]);
  const mixedUnderColour = () => group([], null, [
    group(['G'], '#336699', [part(['G', 'p'], '#a0a0a0'), part(['G', 'q'], '#336699')]),
  ]);
  // N3: a part with no colour beside a coloured one.
  const colourless = () => group([], null, [
    group(['G'], null, [part(['G', 'p'], '#a0a0a0'), part(['G', 'q'], null)]),
  ]);
  // N4: inner uniform, outer mixed.
  const nested = () => group([], null, [
    group(['Outer'], null, [
      group(['Outer', 'Inner'], null, [
        part(['Outer', 'Inner', 'a'], '#a0a0a0'), part(['Outer', 'Inner', 'b'], '#a0a0a0'),
      ]),
      part(['Outer', 'c'], '#191919'),
    ]),
  ]);
  // N5: the inner group's declared colour matches the outer group's
  // other part, but its own parts are of two other colours.
  const standIn = () => group([], null, [
    group(['Outer'], null, [
      group(['Outer', 'Inner'], '#ff0000', [
        part(['Outer', 'Inner', 'a'], '#0000ff'), part(['Outer', 'Inner', 'b'], '#00ff00'),
      ]),
      part(['Outer', 'c'], '#ff0000'),
    ]),
  ]);
  // N6: a declared colour every part overrides with one other.
  const overridden = () => group([], null, [
    group(['G'], '#ff0000', [part(['G', 'p'], '#0000ff'), part(['G', 'q'], '#0000ff')]),
  ]);
  // N7: the group's own model is one of its parts.
  const ownModelColourless = () => group([], null, [
    group(['G'], null, [part(['G', 'p'], '#a0a0a0')], true),
  ]);
  const ownModelColoured = () => group([], null, [
    group(['G'], '#a0a0a0', [part(['G', 'p'], '#a0a0a0')], true),
  ]);
  // N8: a flexible part has no model and no children, and still counts.
  const flexibleAlike = () => group([], null, [
    group(['G'], null, [part(['G', 'rigid'], '#a0a0a0'), part(['G', 'flexible'], '#a0a0a0', false)]),
  ]);
  const flexibleOther = () => group([], null, [
    group(['G'], null, [part(['G', 'rigid'], '#a0a0a0'), part(['G', 'flexible'], '#ff0000', false)]),
  ]);

  it('shows the one colour a group\'s parts all show (N1)', () => {
    expect(colourAt(rowsOf(uniform()), ['G'])).toBe('#a0a0a0');
  });

  it('shows the group\'s own effective colour, or none, when its parts differ (N2)', () => {
    expect(colourAt(rowsOf(mixed()), ['G'])).toBeNull();
    expect(colourAt(rowsOf(mixedUnderColour()), ['G'])).toBe('#336699');
  });

  it('shares no colour with a part that has none (N3)', () => {
    expect(colourAt(rowsOf(colourless()), ['G'])).toBeNull();
  });

  it('shows an inner group\'s shared colour where its outer group shares none (N4)', () => {
    const rows = rowsOf(nested());
    expect(colourAt(rows, ['Outer', 'Inner'])).toBe('#a0a0a0');
    expect(colourAt(rows, ['Outer'])).toBeNull();
  });

  it('never lets a group\'s own colour stand in for its parts (N5)', () => {
    const rows = rowsOf(standIn());
    expect(colourAt(rows, ['Outer', 'Inner'])).toBe('#ff0000');
    expect(colourAt(rows, ['Outer'])).toBeNull();
  });

  it('shows the colour its parts all override a declared one with (N6)', () => {
    const row = rowAt(rowsOf(overridden()), ['G']);
    expect(row.color).toBe('#0000ff');
    expect(row.node.color).toBe('#ff0000');
  });

  it('counts the group\'s own model among its parts (N7)', () => {
    expect(colourAt(rowsOf(ownModelColourless()), ['G'])).toBeNull();
    expect(colourAt(rowsOf(ownModelColoured()), ['G'])).toBe('#a0a0a0');
  });

  it('counts a flexible part of the same colour (N8, first case)', () => {
    expect(colourAt(rowsOf(flexibleAlike()), ['G'])).toBe('#a0a0a0');
  });

  it('counts a flexible part of another colour (N8, second case)', () => {
    expect(colourAt(rowsOf(flexibleOther()), ['G'])).toBeNull();
  });

  it('does not follow what is expanded, focused or hidden (N9)', () => {
    const tree = uniform();
    const rootOnly = new Set([assemblyPathKey([])]);
    expect(colourAt(rowsOf(tree, nav(), rootOnly), ['G'])).toBe('#a0a0a0');
    expect(colourAt(rowsOf(tree, nav({ hidden: [['G', 'p']] })), ['G'])).toBe('#a0a0a0');
    expect(colourAt(rowsOf(tree, nav({ hidden: [['G']] })), ['G'])).toBe('#a0a0a0');
    expect(colourAt(rowsOf(tree, nav({ root: ['G'] })), ['G'])).toBe('#a0a0a0');
    expect(colourAt(rowsOf(tree, nav({ root: ['G', 'p'] })), ['G'])).toBe('#a0a0a0');
  });

  it('leaves every row without children at its node\'s colour (N10)', () => {
    const trees = [
      uniform, mixed, mixedUnderColour, colourless, nested, standIn, overridden,
      ownModelColourless, ownModelColoured, flexibleAlike, flexibleOther,
    ].map((make) => make());
    const navigations = [
      nav(), nav({ hidden: [['G', 'p']] }), nav({ hidden: [['G']] }),
      nav({ root: ['G'] }), nav({ root: ['G', 'p'] }),
    ];
    let leaves = 0;
    for (const tree of trees) {
      for (const navigation of navigations) {
        for (const row of rowsOf(tree, navigation)) {
          if (row.node.children.length === 0) {
            leaves += 1;
            expect(row.color).toBe(row.node.color);
          }
        }
      }
    }
    expect(leaves).toBeGreaterThan(0);
  });

  it('fills a uniform group\'s chip with its colour, its checked state and name as any group\'s (N11)', () => {
    const shown = chipState(rowAt(rowsOf(uniform()), ['G']));
    const hidden = chipState(rowAt(rowsOf(uniform(), nav({ hidden: [['G']] })), ['G']));
    expect(shown).toEqual({ checked: true, fill: 'color', label: 'Visibility for G' });
    expect(hidden).toEqual({ checked: false, fill: 'none', label: 'Visibility for G' });

    const mixedShown = chipState(rowAt(rowsOf(mixed()), ['G']));
    const mixedHidden = chipState(rowAt(rowsOf(mixed(), nav({ hidden: [['G']] })), ['G']));
    expect([shown.checked, shown.label]).toEqual([mixedShown.checked, mixedShown.label]);
    expect([hidden.checked, hidden.label]).toEqual([mixedHidden.checked, mixedHidden.label]);
  });

  describe('reads each node a constant number of times (N13)', () => {
    // Replaces every node's `children` with a getter counting its reads.
    const counted = (tree: AssemblyNode): Map<AssemblyNode, number> => {
      const reads = new Map<AssemblyNode, number>();
      const install = (node: AssemblyNode): void => {
        const children = node.children;
        children.forEach(install);
        reads.set(node, 0);
        Object.defineProperty(node, 'children', {
          get: () => {
            reads.set(node, reads.get(node)! + 1);
            return children;
          },
          enumerable: true,
          configurable: true,
        });
      };
      install(tree);
      return reads;
    };

    // 200 nested groups, each holding one part and the next group.
    const chain = (count: number): AssemblyNode => {
      const build = (index: number, above: string[]): AssemblyNode => {
        const here = [...above, `g${index}`];
        const children = [part([...here, 'p'], '#a0a0a0')];
        if (index < count) {
          children.push(build(index + 1, here));
        }
        return group(here, null, children);
      };
      return group([], null, [build(1, [])]);
    };
    // One group of 2,000 parts.
    const flat = (count: number): AssemblyNode => group([], null, [
      group(['G'], null, Array.from(
        { length: count }, (_, index) => part(['G', `p${index}`], '#a0a0a0'))),
    ]);

    it.each([
      ['a chain of 200 nested groups', () => chain(200), 401],
      ['a flat group of 2,000 parts', () => flat(2000), 2002],
    ] as const)('over %s', (_name, make, size) => {
      const tree = make();
      const expanded = everyKey(tree);
      const reads = counted(tree);
      const rows = navigatorRows(tree, nav(), local({ expanded }));
      expect(rows.length).toBe(size);
      expect(Math.max(...reads.values())).toBeLessThanOrEqual(4);
    });
  });
});
