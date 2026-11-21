/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// OpenSpec `evaluate-a-pose-in-one-flat-pass`, design "Tests": the work a
// pose performs (W1-W4), the exactness edges (E1-E16), the scopes the
// flat pass serves, in full or in part, or leaves to the walk (S1-S15)
// and its lifetime
// (L1-L6). Every value is compared, by `Object.is`, with the value the
// recursive walk gives for the same node under an equal scope in a pass
// the flat pass does not serve: the walk is the reference.

import * as THREE from 'three';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const { loadAsync } = vi.hoisted(() => ({
  loadAsync: vi.fn(() => Promise.resolve(new THREE.BoxGeometry())),
}));

vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({
  STLLoader: class { loadAsync = loadAsync; },
}));

import {
  EXPRESSION_LIMITS, FLAT_PASS, expressionGeneration, expressionMetrics,
  flatPassMetrics, flatPassServes, flatPassServing, prepare, prepareFlatPass,
  releaseExpressions, resetExpressionMetrics, retainExpressions, valueOf,
  withExpressions,
} from './expressions';
import type { EvalScope, NodeId } from './expressions';
import { evalExpr } from './evaluator';
import { bindingTable } from './bindings';
import { WidgetTree } from './tree';
import { Manifest, ManifestNode } from './types';

const DEFAULT_MINIMUM = 1_000;

// The base has no `FLAT_PASS`: tolerate its absence so every test reaches
// its first call of a new name, which is where it fails there.
const setMinimum = (value: number): void => {
  if (FLAT_PASS !== undefined) FLAT_PASS.minimumBindings = value;
};

const leaf = (overrides: Partial<ManifestNode> = {}): ManifestNode => ({
  name: 'leaf', type: 'part', color: '#cc4444', operations: [],
  model: 'leaf.stl', mtime: 1, ...overrides,
});

const root = (children: ManifestNode[]): ManifestNode => ({
  name: 'root', type: 'assembly', color: null, operations: [], children,
});

const table = (
  entries: { name: string; expression: string }[],
  drivers: Record<string, unknown> = {},
) => bindingTable({ bindings: entries, drivers } as unknown as Manifest, '/m.json');

/** A hand-built table: every entry's root AND its own name node are
 * interned before any pose, so a served name is visible to the probe. */
interface Doc {
  readonly map: ReadonlyMap<string, NodeId>;
  /** The name node of an entry. */
  name(entry: string): NodeId;
  /** The root node of an entry. */
  root(entry: string): NodeId;
}

function doc(entries: [string, string][]): Doc {
  const map = new Map<string, NodeId>();
  for (const [name, expression] of entries) map.set(name, prepare(expression));
  const names = new Map<string, NodeId>();
  for (const [name] of entries) names.set(name, prepare(name));
  return {
    map,
    name: (entry) => names.get(entry)!,
    root: (entry) => map.get(entry)!,
  };
}

let moves = 0;
/** Moves the evaluation pass to a scope nothing else uses, so the next
 * scope starts a fresh pass the flat pass has not served. */
function movePass(): void {
  moves += 1;
  valueOf(prepare('0'), { time: -1e9 - moves });
}

/** The walk's values for `ids` under a copy of `scope`, in a pass the flat
 * pass does not serve; the pass is moved on again afterwards, so a pose of
 * an equal scope is a new pass and cannot read this one's memo. */
function reference(ids: readonly NodeId[], scope: EvalScope): unknown[] {
  movePass();
  const copy = { ...scope };
  const values = ids.map((id) => valueOf(id, copy));
  movePass();
  return values;
}

/** The error a call throws, or a failure when it does not throw. */
function thrown(action: () => unknown): Error {
  try {
    action();
  } catch (error) {
    return error as Error;
  }
  throw new Error('expected a throw');
}

/** The walk's error for `id` under a copy of `scope`, in an unserved pass. */
function referenceError(id: NodeId, scope: EvalScope): Error {
  movePass();
  const copy = { ...scope };
  const error = thrown(() => valueOf(id, copy));
  movePass();
  return error;
}

const same = (actual: unknown, expected: unknown): void => {
  expect(Object.is(actual, expected),
    `${String(actual)} (${typeof actual}) is not ${String(expected)} (${typeof expected})`)
    .toBe(true);
};

const scopeOf = (drivers: Record<string, unknown>, map: ReadonlyMap<string, NodeId>,
                 time = 0): EvalScope =>
  ({ time, drivers: drivers as EvalScope['drivers'], bindings: map });

afterEach(() => {
  setMinimum(DEFAULT_MINIMUM);
  if (FLAT_PASS !== undefined) FLAT_PASS.verify = false;
});

// ---------------------------------------------------------------------
// W1: the default minimum, through the tree.
// ---------------------------------------------------------------------

describe('W1: a pose moving one input computes only what it feeds', () => {
  it('W1 performs at most four resolutions plus entries where the walk performs thousands', async () => {
    // A balanced tree of sums over `a`, about ten levels deep, and one
    // entry over `b`: 1,204 entries, above the default minimum.
    const entries: { name: string; expression: string }[] = [];
    let level: string[] = [];
    for (let i = 0; i < 600; i += 1) {
      entries.push({ name: `_l0_${i}`, expression: `(a + ${i})` });
      level.push(`_l0_${i}`);
    }
    let depth = 0;
    while (level.length > 1) {
      depth += 1;
      const next: string[] = [];
      for (let i = 0; i + 1 < level.length; i += 2) {
        const name = `_l${depth}_${i / 2}`;
        entries.push({ name, expression: `(${level[i]} + ${level[i + 1]})` });
        next.push(name);
      }
      if (level.length % 2 === 1) next.push(level[level.length - 1]);
      level = next;
    }
    const top = level[0];
    entries.push({ name: '_b', expression: '(b + 1)' });
    expect(entries.length).toBeGreaterThan(DEFAULT_MINIMUM);
    const bound = table(entries, { a: {}, b: {} });
    const tree = new WidgetTree(root([
      leaf({ name: 'sum', operations: [['t', [`(${top} + _b)`, '0', '0']]] }),
    ]), '/build/', null, bound);
    await tree.loaded;
    const scope = (a: number, b: number): EvalScope =>
      ({ time: 0, drivers: { a, b }, get bindings() { return bound.roots(); } });
    tree.update(scope(1, 1));
    resetExpressionMetrics();

    tree.update(scope(1, 2), { time: false, drivers: new Set(['b']) });

    const { resolutions } = expressionMetrics();
    console.log(`W1: ${entries.length} entries; the pose moving b: ${resolutions} resolutions,`
      + ` ${flatPassMetrics?.()?.entries} flat entries`);
    // The operation's sum, its literal, and `(b + 1)`.
    expect(resolutions).toBeLessThanOrEqual(4);
    expect(resolutions + flatPassMetrics().entries).toBeLessThanOrEqual(4);
    // sum over i < 600 of (1 + i), plus (2 + 1).
    expect(tree.children[0].group.matrix.elements[12]).toBe(180_300 + 3);
    tree.dispose();
  });
});

// ---------------------------------------------------------------------
// Everything else lowers the minimum to 0.
// ---------------------------------------------------------------------

describe('the flat pass', () => {
  beforeEach(() => setMinimum(0));

  describe('work', () => {
    it('W2 a new scope object with equal values computes nothing', () => {
      const d = doc([['_wx', '(a * 2)'], ['_wy', '(_wx + b)']]);
      const first = scopeOf({ a: 1, b: 2 }, d.map);
      prepareFlatPass(first);
      same(valueOf(d.name('_wy'), first), 4);
      resetExpressionMetrics();

      const second = scopeOf({ a: 1, b: 2 }, d.map);
      prepareFlatPass(second);

      same(valueOf(d.name('_wy'), second), 4);
      same(valueOf(d.name('_wx'), second), 2);
      expect(flatPassServes(d.name('_wy'))).toBe(true);
      expect(flatPassMetrics().runs).toBe(0);
      expect(flatPassMetrics().entries).toBe(0);
      expect(expressionMetrics().resolutions).toBe(0);
    });

    it('W3 the first pose after a compile computes every entry once, and the class with no input never again', () => {
      const d = doc([['_k3', '(2 + 3)'], ['_x3', '(a * 2)'], ['_y3', 'max(_k3, _x3)']]);
      resetExpressionMetrics();
      prepareFlatPass(scopeOf({ a: 1 }, d.map));
      const first = flatPassMetrics();
      expect(first.compiles).toBe(1);
      expect(first.programEntries).toBe(3);
      expect(first.entries).toBe(3);

      for (const a of [2, 7, -4]) {
        resetExpressionMetrics();
        const scope = scopeOf({ a }, d.map);
        prepareFlatPass(scope);
        expect(flatPassMetrics().entries).toBe(2);
        same(valueOf(d.name('_k3'), scope), 5);
        same(valueOf(d.name('_y3'), scope), Math.max(5, a * 2));
      }
    });

    it('W4 two independent inputs, each moved alone, compute only their own segments', () => {
      const d = doc([
        ['_x4', '(a * 2)'], ['_x5', '(_x4 + 1)'],
        ['_y4', '(b * 3)'], ['_y5', '(_y4 / 2)'],
        ['_w4', '(_x5 + _y5)'],
      ]);
      prepareFlatPass(scopeOf({ a: 1, b: 1 }, d.map));

      resetExpressionMetrics();
      const movedA = scopeOf({ a: 5, b: 1 }, d.map);
      prepareFlatPass(movedA);
      expect(flatPassMetrics().entries).toBe(3);
      same(valueOf(d.name('_w4'), movedA), 11 + 1.5);

      resetExpressionMetrics();
      const movedB = scopeOf({ a: 5, b: 4 }, d.map);
      prepareFlatPass(movedB);
      expect(flatPassMetrics().entries).toBe(3);
      same(valueOf(d.name('_w4'), movedB), 11 + 6);
    });
  });

  describe('exactness', () => {
    it('E1 a comparison read by a walked `=== true` gives the walk\'s boolean', () => {
      const d = doc([['_c1', '(a > 1)'], ['_e1', '(_c1 === true)']]);
      const scope = scopeOf({ a: 2 }, d.map);
      const ids = [d.name('_c1'), d.root('_e1'), d.name('_e1')];
      const expected = reference(ids, scope);
      prepareFlatPass(scope);
      expect(flatPassServes(d.name('_c1'))).toBe(true);
      expect(flatPassServes(d.root('_e1'))).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
      same(valueOf(d.root('_e1'), scope), true);
    });

    it('E2 a comparison read by a walked `!== false` gives the walk\'s boolean', () => {
      const d = doc([['_c2', '(a > 1)'], ['_e2', '(_c2 !== false)']]);
      const scope = scopeOf({ a: 0 }, d.map);
      const ids = [d.name('_c2'), d.root('_e2')];
      const expected = reference(ids, scope);
      prepareFlatPass(scope);
      expect(flatPassServes(d.name('_c2'))).toBe(true);
      expect(flatPassServes(d.root('_e2'))).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
      same(valueOf(d.root('_e2'), scope), false);
    });

    it('E3 a comparison added to itself, compared with 1 and passed to max', () => {
      const d = doc([
        ['_c3', '(a > 1)'], ['_s3', '(_c3 + _c3)'], ['_q3', '(_c3 == 1)'], ['_m3', 'max(_c3, 0)'],
      ]);
      for (const a of [2, 0]) {
        const scope = scopeOf({ a }, d.map);
        const ids = ['_c3', '_s3', '_q3', '_m3'].map((name) => d.name(name));
        const expected = reference(ids, scope);
        prepareFlatPass(scope);
        ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
        ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
        expect(typeof valueOf(d.name('_q3'), scope)).toBe('boolean');
        expect(typeof valueOf(d.name('_s3'), scope)).toBe('number');
      }
    });

    it('E4 negative zero through unary minus of a zero input, sign(-0) and 1 / -0', () => {
      const d = doc([
        ['_z4', '-a'], ['_s4', 'sign(_z4)'], ['_d4', '(1 / _z4)'], ['_n4', '-0'],
      ]);
      const scope = scopeOf({ a: 0 }, d.map);
      const ids = ['_z4', '_s4', '_d4', '_n4'].map((name) => d.name(name));
      const expected = reference(ids, scope);
      expect(expected.map(String)).toEqual(['0', '0', '-Infinity', '0']);
      same(expected[0], -0);
      same(expected[1], 0);
      same(expected[3], -0);
      prepareFlatPass(scope);
      ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
    });

    it('E5 not-a-number through sqrt(-1), compared, and an input that stays NaN across passes', () => {
      const d = doc([
        ['_n5', 'sqrt(-1)'], ['_q5', '(_n5 == _n5)'], ['_r5', '(_n5 != _n5)'],
        ['_a5', '(a + 1)'], ['_b5', '(b * 2)'],
      ]);
      const ids = ['_n5', '_q5', '_r5', '_a5', '_b5'].map((name) => d.name(name));
      for (const b of [1, 2, 3]) {
        const scope = scopeOf({ a: NaN, b }, d.map);
        const expected = reference(ids, scope);
        prepareFlatPass(scope);
        ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
        ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
        same(valueOf(d.name('_a5'), scope), NaN);
      }
    });

    it('E6 `&&` and `||` stay with the walk: lazy on their right side', () => {
      const d = doc([
        ['_x6', '(b * 2)'],
        ['_g6', '(a && b)'], ['_h6', '(a || b)'],
        ['_p6', '(b > 5)'], ['_pa6', '(_p6 && b)'],
        ['_t6', 'f(1)'], ['_and6', '(a && _t6)'], ['_or6', '(a || _t6)'],
      ]);
      const scope = scopeOf({ a: 0, b: 1, f: 3 }, d.map);
      const ids = ['_x6', '_g6', '_h6', '_pa6', '_and6'].map((name) => d.name(name));
      const expected = reference(ids, scope);
      const error = referenceError(d.name('_or6'), scope);
      expect(error).toBeInstanceOf(TypeError);
      prepareFlatPass(scope);
      expect(flatPassServes(d.name('_x6'))).toBe(true);
      for (const name of ['_g6', '_h6', '_pa6', '_t6', '_and6', '_or6']) {
        expect(flatPassServes(d.root(name)), name).toBe(false);
      }
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
      same(valueOf(d.name('_pa6'), scope), false);
      expect(() => valueOf(d.name('_or6'), scope)).toThrow(error.message);
    });

    it('E7 a ternary whose untaken branch would throw', () => {
      const d = doc([['_x7', '(a * 2)'], ['_t7', '((a > 0) ? 1 : f(2))']]);
      const taken = scopeOf({ a: 1, f: 3 }, d.map);
      const expected = reference([d.name('_t7')], taken);
      prepareFlatPass(taken);
      expect(flatPassServes(d.name('_x7'))).toBe(true);
      expect(flatPassServes(d.root('_t7'))).toBe(false);
      same(valueOf(d.name('_t7'), taken), expected[0]);

      const other = scopeOf({ a: 0, f: 3 }, d.map);
      const error = referenceError(d.name('_t7'), other);
      prepareFlatPass(other);
      expect(() => valueOf(d.name('_t7'), other)).toThrow(error.message);
    });

    it('E8 a generic member and an index stay with the walk', () => {
      const d = doc([['_x8', '(a * 2)'], ['_m8', '(o).k'], ['_i8', 'a[0]']]);
      const scope = scopeOf({ a: 5, o: { k: 4 } }, d.map);
      const ids = ['_x8', '_m8', '_i8'].map((name) => d.name(name));
      const expected = reference(ids, scope);
      prepareFlatPass(scope);
      expect(flatPassServes(d.name('_x8'))).toBe(true);
      expect(flatPassServes(d.root('_m8'))).toBe(false);
      expect(flatPassServes(d.root('_i8'))).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
    });

    it('E9 a name nothing resolves is absent: the pass is served in part, the entry over it walked', () => {
      const d = doc([['_x9', '(a * 2)'], ['_u9', '(zz + 1)']]);
      const scope = scopeOf({ a: 5 }, d.map);
      const ids = ['_x9', '_u9'].map((name) => d.name(name));
      const expected = reference(ids, scope);
      resetExpressionMetrics();
      prepareFlatPass(scope);
      expect(flatPassMetrics().declined).toBe(0);
      expect(flatPassMetrics().partial).toBe(1);
      expect(flatPassServes(d.name('_x9'))).toBe(true);
      expect(flatPassServes(d.name('_u9'))).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
    });

    it('E10 an owner map used as a value is absent: the pass is served in part, the entry over it walked', () => {
      const d = doc([['_x10', '(a * 2)'], ['_o10', '(o + 1)']]);
      const scope = scopeOf({ a: 5, o: { k: 4 } }, d.map);
      const ids = ['_x10', '_o10'].map((name) => d.name(name));
      const expected = reference(ids, scope);
      resetExpressionMetrics();
      prepareFlatPass(scope);
      expect(flatPassMetrics().declined).toBe(0);
      expect(flatPassMetrics().partial).toBe(1);
      expect(flatPassServes(d.name('_x10'))).toBe(true);
      expect(flatPassServes(d.name('_o10'))).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
    });

    it('E11 a context function used as a value stays with the walk', () => {
      const d = doc([['_x11', '(a * 2)'], ['_f11', '(max + 1)']]);
      const scope = scopeOf({ a: 5 }, d.map);
      const ids = ['_x11', '_f11'].map((name) => d.name(name));
      const expected = reference(ids, scope);
      prepareFlatPass(scope);
      expect(flatPassServes(d.name('_x11'))).toBe(true);
      expect(flatPassServes(d.root('_f11'))).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
    });

    it('E12 profileOverlap in an entry, with profiles in the scope, stays with the walk', () => {
      const square = {
        points: [[0, 0], [1, 0], [1, 1], [0, 1]] as const,
        polygons: [[0, 1, 2, 3]],
      };
      const d = doc([['_x12', '(a * 2)'], ['_p12', 'profileOverlap(0, 0, 0, 0, 0, 0, a, 0)']]);
      const scope: EvalScope = { ...scopeOf({ a: 0.5 }, d.map), profiles: [square] };
      const ids = ['_x12', '_p12'].map((name) => d.name(name));
      const expected = reference(ids, scope);
      prepareFlatPass(scope);
      expect(flatPassServes(d.name('_x12'))).toBe(true);
      expect(flatPassServes(d.root('_p12'))).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
    });

    it('E13 random() in an entry stays with the walk: a new value each pass', () => {
      const d = doc([['_x13', '(a * 2)'], ['_r13', 'random()']]);
      const seen = new Set<unknown>();
      for (const a of [1, 2, 3, 4]) {
        const scope = scopeOf({ a }, d.map);
        prepareFlatPass(scope);
        expect(flatPassServes(d.name('_x13'))).toBe(true);
        expect(flatPassServes(d.root('_r13'))).toBe(false);
        seen.add(valueOf(d.name('_r13'), scope));
      }
      expect(seen.size).toBe(4);
    });

    it('E14 a call of an unlisted function stays with the walk', () => {
      const d = doc([['_x14', '(a * 2)'], ['_h14', 'hypot(3, a)']]);
      const scope = scopeOf({ a: 4 }, d.map);
      const ids = ['_x14', '_h14'].map((name) => d.name(name));
      const expected = reference(ids, scope);
      prepareFlatPass(scope);
      expect(flatPassServes(d.name('_x14'))).toBe(true);
      expect(flatPassServes(d.root('_h14'))).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
      same(expected[1], 5);
    });

    it('E15 a string, a boolean and a null literal stay with the walk', () => {
      const d = doc([
        ['_x15', '(a * 2)'], ['_s15', '("ab" + 1)'], ['_b15', '(true + 1)'], ['_n15', '(null + 1)'],
      ]);
      const scope = scopeOf({ a: 4 }, d.map);
      const ids = ['_x15', '_s15', '_b15', '_n15'].map((name) => d.name(name));
      const expected = reference(ids, scope);
      expect(expected).toEqual([8, 'ab1', 2, 1]);
      prepareFlatPass(scope);
      expect(flatPassServes(d.name('_x15'))).toBe(true);
      for (const name of ['_s15', '_b15', '_n15']) {
        expect(flatPassServes(d.root(name)), name).toBe(false);
      }
      ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
    });

    it('E16 a pose refused for a non-finite transform refuses with the base\'s message', async () => {
      const runs = flatPassMetrics().runs;
      const refusal = async (minimum: number): Promise<Error> => {
        setMinimum(minimum);
        const bound = table([{ name: '_x16', expression: '(1 / a)' }], { a: {} });
        const tree = new WidgetTree(root([
          leaf({ name: 'moved', operations: [['t', ['_x16', '0', '0']]] }),
        ]), '/build/', null, bound);
        await tree.loaded;
        const scope = (a: number): EvalScope =>
          ({ time: 0, drivers: { a }, get bindings() { return bound.roots(); } });
        tree.update(scope(1));
        const before = [...tree.children[0].group.matrix.elements];
        const error = thrown(() => tree.update(scope(0), { time: false, drivers: new Set(['a']) }));
        expect([...tree.children[0].group.matrix.elements]).toEqual(before);
        tree.dispose();
        return error;
      };
      const walked = await refusal(Infinity);
      expect(flatPassMetrics().runs).toBe(runs);
      const served = await refusal(0);
      expect(flatPassMetrics().runs).toBe(runs + 2);
      expect(served.message).toBe(walked.message);
      expect(served.message).toMatch(/operation 0/);
    });
  });

  describe('scopes', () => {
    it('S1 an input missing takes only its cone off the pass, and a complete scope is served in full', () => {
      const d = doc([['_xs1', '(a * 2)'], ['_ys1', '(b + 1)']]);
      const ids = ['_xs1', '_ys1'].map((name) => d.name(name));
      const missing = scopeOf({ a: 1 }, d.map);
      const expected = reference(ids, missing);
      resetExpressionMetrics();
      prepareFlatPass(missing);
      expect(flatPassMetrics().declined).toBe(0);
      expect(flatPassMetrics().runs).toBe(1);
      expect(flatPassMetrics().partial).toBe(1);
      expect(flatPassMetrics().absentInputs).toBe(1);
      expect(flatPassServing()).toBe('part');
      expect(flatPassServes(ids[0])).toBe(true);
      expect(flatPassServes(ids[1])).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, missing), expected[i]));

      const complete = scopeOf({ a: 3, b: 4 }, d.map);
      prepareFlatPass(complete);
      expect(flatPassServing()).toBe('full');
      expect(flatPassMetrics().partial).toBe(1);
      ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
      same(valueOf(ids[0], complete), 6);
      same(valueOf(ids[1], complete), 5);
    });

    it('S2 an input that is a string, a boolean or an owner map takes only its cone off the pass', () => {
      const d = doc([['_xs2', '(a * 2)'], ['_ys2', '(b + 1)']]);
      const ids = ['_xs2', '_ys2'].map((name) => d.name(name));
      for (const b of ['7', true, { k: 1 }]) {
        const scope = scopeOf({ a: 1, b }, d.map);
        const expected = reference(ids, scope);
        resetExpressionMetrics();
        prepareFlatPass(scope);
        expect(flatPassMetrics().declined).toBe(0);
        expect(flatPassMetrics().partial).toBe(1);
        expect(flatPassServes(ids[0])).toBe(true);
        expect(flatPassServes(ids[1])).toBe(false);
        ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
      }
    });

    it('S3 a dotted input over a truthy number is absent: no throw from the pass, the walk\'s TypeError where the cone is read', () => {
      const d = doc([['_xs3', '(a * 2)'], ['_ds3', '(x.y + 1)']]);
      const scope = scopeOf({ a: 1, x: 5 }, d.map);
      const error = referenceError(d.name('_ds3'), scope);
      expect(error).toBeInstanceOf(TypeError);
      resetExpressionMetrics();
      prepareFlatPass(scope);
      expect(flatPassMetrics().declined).toBe(0);
      expect(flatPassMetrics().partial).toBe(1);
      expect(flatPassMetrics().failures).toBe(0);
      expect(flatPassServes(d.name('_xs3'))).toBe(true);
      expect(flatPassServes(d.name('_ds3'))).toBe(false);
      same(valueOf(d.name('_xs3'), scope), 2);
      const posed = thrown(() => valueOf(d.name('_ds3'), scope));
      expect(posed).toBeInstanceOf(TypeError);
      expect(posed.message).toBe(error.message);
    });

    it('S4 a nested driver map is read through its owners', () => {
      const d = doc([['_ns4', '(x_axis.motor * 2)'], ['_ms4', '(p.q.r + 1)']]);
      const ids = ['_ns4', '_ms4'].map((name) => d.name(name));
      for (const motor of [3, 4]) {
        const scope = scopeOf({ x_axis: { motor }, p: { q: { r: 4 } } }, d.map);
        const expected = reference(ids, scope);
        prepareFlatPass(scope);
        ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
        ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
      }
    });

    it('S5 $t is read from the scope\'s time', () => {
      const d = doc([['_ts5', '($t * 2)'], ['_ks5', '(a + 1)']]);
      const ids = ['_ts5', '_ks5'].map((name) => d.name(name));
      for (const time of [0.25, 0.5]) {
        const scope = scopeOf({ a: 1 }, d.map, time);
        const expected = reference(ids, scope);
        resetExpressionMetrics();
        prepareFlatPass(scope);
        ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
        ids.forEach((id, i) => same(valueOf(id, scope), expected[i]));
        same(valueOf(ids[0], scope), time * 2);
      }
      expect(flatPassMetrics().entries).toBe(1);
    });

    it('S6 a driver named max beside max(a, 1) declines, and the walk throws its TypeError', () => {
      const d = doc([['_ms6', 'max(a, 1)']]);
      const shadowed = scopeOf({ a: 2, max: 5 }, d.map);
      const error = referenceError(d.name('_ms6'), shadowed);
      expect(error).toBeInstanceOf(TypeError);
      resetExpressionMetrics();
      prepareFlatPass(shadowed);
      expect(flatPassMetrics().declined).toBe(1);
      expect(flatPassServes(d.name('_ms6'))).toBe(false);
      expect(() => valueOf(d.name('_ms6'), shadowed)).toThrow(error.message);

      const plain = scopeOf({ a: 2 }, d.map);
      prepareFlatPass(plain);
      expect(flatPassServes(d.name('_ms6'))).toBe(true);
      same(valueOf(d.name('_ms6'), plain), 2);
    });

    it('S7 seventy inputs: moving the sixty-fifth computes only its cone', () => {
      const entries: [string, string][] = [];
      for (let i = 0; i < 70; i += 1) entries.push([`_es7_${i}`, `(x${i} * 2)`]);
      const d = doc(entries);
      const drivers = (moved: number): Record<string, number> => {
        const values: Record<string, number> = {};
        for (let i = 0; i < 70; i += 1) values[`x${i}`] = i === 64 ? moved : i;
        return values;
      };
      prepareFlatPass(scopeOf(drivers(64), d.map));
      expect(flatPassMetrics().inputs).toBe(70);
      resetExpressionMetrics();
      const moved = scopeOf(drivers(1000), d.map);
      prepareFlatPass(moved);
      expect(flatPassMetrics().entries).toBe(1);
      same(valueOf(d.name('_es7_64'), moved), 2000);
      same(valueOf(d.name('_es7_63'), moved), 126);
      same(valueOf(d.name('_es7_69'), moved), 138);
    });

    it('S8 a pass served in part between two served ones, the other input moving in it, leaves nothing stale', () => {
      const d = doc([['_as8', '(a * 2)'], ['_bs8', '(b + 1)'], ['_ss8', '(_as8 + _bs8)']]);
      const ids = ['_as8', '_bs8', '_ss8'].map((name) => d.name(name));
      const first = scopeOf({ a: 1, b: 1 }, d.map);
      prepareFlatPass(first);
      same(valueOf(ids[2], first), 4);

      const part = scopeOf({ a: 2, b: 'x' }, d.map);
      const partExpected = reference(ids, part);
      resetExpressionMetrics();
      prepareFlatPass(part);
      expect(flatPassMetrics().declined).toBe(0);
      expect(flatPassMetrics().partial).toBe(1);
      expect(flatPassServes(ids[0])).toBe(true);
      expect(flatPassServes(ids[1])).toBe(false);
      expect(flatPassServes(ids[2])).toBe(false);
      ids.forEach((id, i) => same(valueOf(id, part), partExpected[i]));
      same(valueOf(ids[0], part), 4);

      const third = scopeOf({ a: 2, b: 1 }, d.map);
      const expected = reference(ids, third);
      prepareFlatPass(third);
      ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
      ids.forEach((id, i) => same(valueOf(id, third), expected[i]));
      same(valueOf(ids[0], third), 4);
      same(valueOf(ids[2], third), 6);
    });

    it('S9 an extra driver nothing reads leaves nothing absent', () => {
      const d = doc([['_xs9', '(a * 2)']]);
      const scope = scopeOf({ a: 1, extra: 'text', other: { deep: true } }, d.map);
      resetExpressionMetrics();
      prepareFlatPass(scope);
      expect(flatPassMetrics().declined).toBe(0);
      expect(flatPassMetrics().partial).toBe(0);
      expect(flatPassServes(d.name('_xs9'))).toBe(true);
      same(valueOf(d.name('_xs9'), scope), 2);
    });

    it('S10 an input supplied again counts as changed, whatever its value, and nothing of its cone is computed while it is absent', () => {
      const d = doc([['_xs10', '(a * 2)'], ['_rs10', '(b + 1)']]);
      const ids = ['_xs10', '_rs10'].map((name) => d.name(name));
      // `b` absent from the first pose: its slot is never written.
      resetExpressionMetrics();
      prepareFlatPass(scopeOf({ a: 1 }, d.map));
      expect(flatPassMetrics().entries).toBe(1);

      // Supplied as 0, the never-written slot's own value.
      resetExpressionMetrics();
      const zero = scopeOf({ a: 1, b: 0 }, d.map);
      prepareFlatPass(zero);
      expect(flatPassMetrics().entries).toBe(1);
      expect(flatPassServing()).toBe('full');
      ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
      same(valueOf(ids[1], zero), 1);

      // Absent again, then supplied at the value it had before.
      resetExpressionMetrics();
      prepareFlatPass(scopeOf({ a: 1, b: 'x' }, d.map));
      expect(flatPassMetrics().partial).toBe(1);
      expect(flatPassMetrics().entries).toBe(0);
      resetExpressionMetrics();
      const back = scopeOf({ a: 1, b: 0 }, d.map);
      const expected = reference(ids, back);
      prepareFlatPass(back);
      expect(flatPassMetrics().entries).toBe(1);
      ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
      ids.forEach((id, i) => same(valueOf(id, back), expected[i]));
    });

    it('S11 a node over an absent input and an input that moved while it was absent is recomputed before it is served again', () => {
      const d = doc([['_as11', '(a * 2)'], ['_ss11', '(_as11 + b)'], ['_ts11', '(_ss11 * a)']]);
      const ids = ['_as11', '_ss11', '_ts11'].map((name) => d.name(name));
      const first = scopeOf({ a: 1, b: 10 }, d.map);
      prepareFlatPass(first);
      same(valueOf(ids[2], first), 12);

      for (const a of [2, 3]) {
        const absent = scopeOf({ a }, d.map);
        const expected = reference(ids, absent);
        prepareFlatPass(absent);
        expect(flatPassServes(ids[0])).toBe(true);
        expect(flatPassServes(ids[1])).toBe(false);
        expect(flatPassServes(ids[2])).toBe(false);
        ids.forEach((id, i) => same(valueOf(id, absent), expected[i]));
        same(valueOf(ids[0], absent), a * 2);
      }

      const back = scopeOf({ a: 3, b: 10 }, d.map);
      const expected = reference(ids, back);
      prepareFlatPass(back);
      ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
      ids.forEach((id, i) => same(valueOf(id, back), expected[i]));
      same(valueOf(ids[2], back), (6 + 10) * 3);
    });

    it('S12 a pose served in part refuses with the walk\'s own error, and only where it reads the cone', async () => {
      const pose = async (minimum: number, reads: string): Promise<{
        error?: Error; x: number; partial: number; declined: number;
      }> => {
        setMinimum(minimum);
        const bound = table([
          { name: '_ok12', expression: '(a * 2)' }, { name: '_bad12', expression: '(x.y + 1)' },
        ]);
        const tree = new WidgetTree(root([
          leaf({ name: 'moved', operations: [['t', [reads, '0', '0']]] }),
        ]), '/build/', null, bound);
        await tree.loaded;
        const scope: EvalScope =
          { time: 0, drivers: { a: 3, x: 5 }, get bindings() { return bound.roots(); } };
        // Equal scopes over hash-consed tables are one pass: start a new one.
        movePass();
        const before = flatPassMetrics();
        let error: Error | undefined;
        try {
          tree.update(scope);
        } catch (thrownError) {
          error = thrownError as Error;
        }
        const after = flatPassMetrics();
        const x = tree.children[0].group.matrix.elements[12];
        tree.dispose();
        return {
          error, x,
          partial: (after.partial ?? 0) - (before.partial ?? 0),
          declined: after.declined - before.declined,
        };
      };
      const unread = await pose(0, '_ok12');
      expect(unread.error).toBeUndefined();
      expect(unread.partial).toBe(1);
      expect(unread.declined).toBe(0);
      expect(unread.x).toBe(6);

      const walked = await pose(Infinity, '_bad12');
      expect(walked.error).toBeInstanceOf(Error);
      const served = await pose(0, '_bad12');
      expect(served.partial).toBe(1);
      expect(served.declined).toBe(0);
      expect(served.error).toBeInstanceOf(Error);
      expect(served.error!.message).toBe(walked.error!.message);
    });

    it('S13 a steady absent set builds one view, and each later pose computes only what moved', () => {
      const entries: [string, string][] = [['_os13', '(_own / 6)'], ['_as13', '(a * 2)']];
      for (let i = 0; i < 50; i += 1) entries.push([`_bs13_${i}`, `(b + ${i})`]);
      const d = doc(entries);
      resetExpressionMetrics();
      prepareFlatPass(scopeOf({ a: 1, b: 1 }, d.map));
      expect(flatPassMetrics().views).toBe(1);
      expect(flatPassMetrics().entries).toBe(51);
      for (const a of [2, 3, 4, 5]) {
        resetExpressionMetrics();
        const scope = scopeOf({ a, b: 1 }, d.map);
        prepareFlatPass(scope);
        const metrics = flatPassMetrics();
        expect(metrics.partial).toBe(1);
        expect(metrics.absentInputs).toBe(1);
        expect(metrics.views).toBe(0);
        expect(metrics.entries).toBe(1);
        expect(flatPassServing()).toBe('part');
        same(valueOf(d.name('_as13'), scope), a * 2);
        same(valueOf(d.name('_bs13_49'), scope), 50);
        expect(expressionMetrics().resolutions).toBe(0);
        expect(flatPassServes(d.name('_os13'))).toBe(false);
        same(valueOf(d.name('_os13'), scope), NaN);
      }
    });

    it('S14 a pass declined whole between two served ones, its input moving in it, leaves nothing stale', () => {
      const d = doc([['_ms14', 'max(a, 1)'], ['_xs14', '(a * 2)']]);
      const ids = ['_ms14', '_xs14'].map((name) => d.name(name));
      const first = scopeOf({ a: 1 }, d.map);
      prepareFlatPass(first);
      same(valueOf(ids[0], first), 1);

      resetExpressionMetrics();
      prepareFlatPass(scopeOf({ a: 2, max: 5 }, d.map));
      expect(flatPassMetrics().declined).toBe(1);
      expect(flatPassMetrics().runs).toBe(0);
      expect(flatPassServing()).toBe('none');

      const third = scopeOf({ a: 2 }, d.map);
      const expected = reference(ids, third);
      prepareFlatPass(third);
      ids.forEach((id) => expect(flatPassServes(id)).toBe(true));
      ids.forEach((id, i) => same(valueOf(id, third), expected[i]));
      same(valueOf(ids[0], third), 2);
      same(valueOf(ids[1], third), 4);
    });

    it('S15 a drivers value that is not an object declines whole, and the walk throws where it resolves a name', () => {
      const d = doc([['_ts15', '($t * 2)'], ['_xs15', '(a * 2)']]);
      const scope: EvalScope = { time: 0.5, drivers: null as unknown as EvalScope['drivers'], bindings: d.map };
      const error = referenceError(d.name('_xs15'), scope);
      expect(error).toBeInstanceOf(TypeError);
      const expected = reference([d.name('_ts15')], scope);
      resetExpressionMetrics();
      prepareFlatPass(scope);
      expect(flatPassMetrics().declined).toBe(1);
      expect(flatPassMetrics().failures).toBe(0);
      expect(flatPassServes(d.name('_ts15'))).toBe(false);
      same(valueOf(d.name('_ts15'), scope), expected[0]);
      expect(() => valueOf(d.name('_xs15'), scope)).toThrow(error.message);
    });
  });

  describe('lifetime', () => {
    /** Empties the store: a retain released at no open scope is the last. */
    const resetTheStore = (): void => {
      retainExpressions();
      releaseExpressions();
    };

    it('L1 a reset between poses recompiles, with node ids reused for different nodes', () => {
      resetTheStore();
      const generation = expressionGeneration();
      const before = prepare('(a + 1)');
      const name = prepare('_xl1');
      const map = new Map([['_xl1', before]]);
      resetExpressionMetrics();
      const scope = scopeOf({ a: 1 }, map);
      prepareFlatPass(scope);
      same(valueOf(name, scope), 2);
      expect(flatPassMetrics().compiles).toBe(1);

      resetTheStore();
      expect(expressionGeneration()).toBe(generation + 1);
      const after = prepare('(a * 10)');
      expect(after).toBe(before);
      expect(prepare('_xl1')).toBe(name);
      // The same map object, whose id now names a different node.
      const again = scopeOf({ a: 1 }, map);
      prepareFlatPass(again);
      expect(flatPassMetrics().compiles).toBe(2);
      expect(flatPassServes(name)).toBe(true);
      same(valueOf(name, again), 10);
      same(valueOf(after, again), 10);
    });

    it('L2 two tables binding one name to different roots, posed alternately: two compiles', () => {
      const first = doc([['_xl2', '(a + 1)']]);
      const second = doc([['_xl2', '(a * 3)']]);
      const name = first.name('_xl2');
      expect(second.name('_xl2')).toBe(name);
      resetExpressionMetrics();
      for (let i = 0; i < 6; i += 1) {
        const a = i + 1;
        const bound = i % 2 === 0 ? first : second;
        const scope = scopeOf({ a }, bound.map);
        prepareFlatPass(scope);
        expect(flatPassServes(name)).toBe(true);
        same(valueOf(name, scope), i % 2 === 0 ? a + 1 : a * 3);
      }
      expect(flatPassMetrics().compiles).toBe(2);
      expect(flatPassMetrics().runs).toBe(6);
    });

    it('L3 a node interned after the compile reads covered values', () => {
      const d = doc([['_xl3', '(a + 1)']]);
      const scope = scopeOf({ a: 1 }, d.map);
      prepareFlatPass(scope);
      const later = prepare('(_xl3 * 10)');
      resetExpressionMetrics();
      same(valueOf(later, scope), 20);
      expect(flatPassServes(later)).toBe(false);
      expect(flatPassServes(d.name('_xl3'))).toBe(true);
      // The new product and its new literal: `_xl3` is read from the pass.
      expect(expressionMetrics().resolutions).toBe(2);
    });

    it('L4 the last release drops the program', () => {
      retainExpressions();
      const bound = table([{ name: '_xl4', expression: '(a + 1)' }]);
      const scope = (a: number): EvalScope =>
        ({ time: 0, drivers: { a }, get bindings() { return bound.roots(); } });
      resetExpressionMetrics();
      const generation = expressionGeneration();
      const posed = scope(1);
      prepareFlatPass(posed);
      const name = prepare('_xl4');
      const root = bound.roots().get('_xl4')!;
      expect(flatPassServes(root)).toBe(true);
      same(valueOf(name, posed), 2);
      expect(flatPassMetrics().compiles).toBe(1);

      releaseExpressions();

      expect(expressionGeneration()).toBe(generation + 1);
      expect(flatPassServes(root)).toBe(false);
      const again = scope(1);
      prepareFlatPass(again);
      expect(flatPassMetrics().compiles).toBe(2);
      same(valueOf(prepare('_xl4'), again), 2);
    });

    it('L5 everyOperation compiles at every pose, with the values unchanged and the generation risen', () => {
      const limits = { ...EXPRESSION_LIMITS };
      EXPRESSION_LIMITS.everyOperation = true;
      EXPRESSION_LIMITS.nodes = 1;
      try {
        const bound = table([
          { name: '_xl5', expression: '(a + 1)' }, { name: '_yl5', expression: '(_xl5 * 2)' },
        ]);
        const generation = expressionGeneration();
        resetExpressionMetrics();
        const values: number[] = [];
        for (let i = 0; i < 3; i += 1) {
          values.push(withExpressions(() => {
            const scope: EvalScope =
              { time: 0, drivers: { a: 2 }, get bindings() { return bound.roots(); } };
            prepareFlatPass(scope);
            expect(flatPassServes(bound.roots().get('_yl5')!)).toBe(true);
            return evalExpr('_yl5', scope);
          }));
        }
        expect(values).toEqual([6, 6, 6]);
        expect(flatPassMetrics().compiles).toBe(3);
        expect(expressionGeneration()).toBeGreaterThanOrEqual(generation + 3);
      } finally {
        Object.assign(EXPRESSION_LIMITS, limits);
      }
    });

    it('L6 a table below the minimum, and a scope with no table, compile nothing', () => {
      const d = doc([['_xl6', '(a + 1)'], ['_yl6', '(a + 2)']]);
      resetExpressionMetrics();
      setMinimum(5);
      const small = scopeOf({ a: 1 }, d.map);
      prepareFlatPass(small);
      expect(flatPassServes(d.name('_xl6'))).toBe(false);
      same(valueOf(d.name('_xl6'), small), 2);
      setMinimum(0);
      const none: EvalScope = { time: 0, drivers: { a: 1 } };
      prepareFlatPass(none);
      same(valueOf(prepare('(a + 1)'), none), 2);
      expect(flatPassMetrics().compiles).toBe(0);
      expect(flatPassMetrics().runs).toBe(0);
      expect(flatPassMetrics().declined).toBe(0);
    });
  });
});
