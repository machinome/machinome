/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// OpenSpec `rebuild-a-flexible-part-for-less`. A flexible part reads its
// parameters by the roots it prepared, and computes a rebuilt part's
// bounds in two passes over its position array. Neither may move one
// result, so most of this file is parity against what the part did
// before: `evalExpr` of each text by itself, and three.js's own
// `computeBoundingBox` and `computeBoundingSphere` on the same array.
//
//   R1-R4  the work, counted: text lookups (`prepare`) and scopes
//          (`withExpressions`) during a warm read, and calls of the
//          position attribute's accessors during a rebuild.
//   P1-P4  parameter values and refusals against `evalExpr`'s.
//   L1-L5  what the part keeps, across a reclamation, a rebind, two
//          documents and pressure at depth 0.
//   B1-B3  the bounds against three.js's own, number for number under
//          `Object.is`, console reports included.
//
// The counts come from pass-through spies on `./expressions`: calls made
// from inside `expressions.ts` are not seen, calls from `evaluator.ts`,
// `flexible.ts`, `tree.ts` and `bindings.ts` are.

import { readFileSync } from 'node:fs';
import * as THREE from 'three';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('molejo', async (importOriginal) => {
  const actual = await importOriginal<typeof import('molejo')>();
  return { ...actual, evaluate: vi.fn(actual.evaluate) };
});

vi.mock('./expressions', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./expressions')>();
  return {
    ...actual,
    prepare: vi.fn(actual.prepare),
    withExpressions: vi.fn(actual.withExpressions),
  };
});

import { evaluate, parameterNames } from 'molejo';
import {
  EXPRESSION_LIMITS, FLAT_PASS, expressionGeneration, expressionMetrics, flatPassMetrics,
  prepare, releaseExpressions, resetExpressionMetrics, retainExpressions, withExpressions,
} from './expressions';
import type { EvalScope } from './expressions';
import { evalExpr } from './evaluator';
import { BindingTable, bindingTable, EMPTY_BINDINGS } from './bindings';
import * as flexible from './flexible';
import { FlexibleShape } from './flexible';
import { WidgetTree } from './tree';
import { Manifest, ManifestNode } from './types';

// Read through the namespace, so that where it does not exist a test
// fails at this name and not at the file's link.
const computeFlexibleBounds = (geometry: THREE.BufferGeometry): void =>
  (flexible as unknown as {
    computeFlexibleBounds: (geometry: THREE.BufferGeometry) => void;
  }).computeFlexibleBounds(geometry);

const molejo = () => vi.mocked(evaluate);
const evaluations = () => molejo().mock.calls.length;
const lastValues = (): Record<string, unknown> =>
  molejo().mock.calls[molejo().mock.calls.length - 1][1] as Record<string, unknown>;
const prepares = () => vi.mocked(prepare).mock.calls.length;
const scopes = () => vi.mocked(withExpressions).mock.calls.length;
const clearCounts = () => {
  molejo().mockClear();
  vi.mocked(prepare).mockClear();
  vi.mocked(withExpressions).mockClear();
};

/** A reclamation of the whole store, with no scope open and nothing
 * mounted: the generation rises by one. */
const reclaim = (): void => {
  const before = expressionGeneration();
  retainExpressions();
  releaseExpressions();
  expect(expressionGeneration()).toBe(before + 1);
};

const limits = { ...EXPRESSION_LIMITS };
const minimumBindings = FLAT_PASS.minimumBindings;

beforeEach(() => {
  retainExpressions();
  releaseExpressions();
  clearCounts();
});

afterEach(() => {
  Object.assign(EXPRESSION_LIMITS, limits);
  FLAT_PASS.minimumBindings = minimumBindings;
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------
// Parts, scopes and the comparison of numbers.
// ---------------------------------------------------------------------

// A small spring: 24 segments on one helix, an 8-sided wire, so 25 rings
// of 8 plus two cap centres.
const springSpec = (param = 'height'): Record<string, unknown> => ({
  molejo: '0.1',
  profile: { type: 'circle', radius: 2.0 },
  path: [{ type: 'helix', radius: 14.0, turns: 6.5, height: { param } }],
  loop: false,
  tessellation: { path: 24, profile: 8 },
});
const SPRING_VERTICES = 25 * 8 + 2;

const part = (params: Record<string, string>, bindings: BindingTable = EMPTY_BINDINGS,
              spec: Record<string, unknown> = springSpec()) =>
  new FlexibleShape('spring', { tech: 'molejo', spec, params }, null, bindings);

const node = (name: string, params: Record<string, string>,
              spec: Record<string, unknown> = springSpec()): ManifestNode => ({
  name, type: 'LeafNode', color: null, operations: [],
  flexible: { tech: 'molejo', spec, params },
});

const engine = (children: ManifestNode[]): ManifestNode => ({
  name: 'engine', type: 'AssemblyNode', color: null, operations: [], children,
});

const at = (lift: number, on = 0, time = 0,
            bindings?: EvalScope['bindings']): EvalScope => ({
  time, drivers: { v: { lift }, gate: { on } }, ...(bindings ? { bindings } : {}),
});

const lifted = () => ({ time: false, drivers: new Set(['v.lift']) });

const table = (entries: { name: string; expression: string }[]) =>
  bindingTable({ bindings: entries, drivers: { 'v.lift': {}, 'gate.on': {} } } as unknown as Manifest,
               '/m.json');

/** A number as `Object.is` tells it: `-0` and `0` apart, `NaN` itself. */
const key = (value: unknown): string => (typeof value === 'number'
  ? (Object.is(value, -0) ? '-0' : String(value))
  : `${typeof value} ${String(value)}`);

/** What `evalExpr` gives for each text in `scope`, by name. */
const expected = (params: Record<string, string>, scope: EvalScope) =>
  Object.fromEntries(Object.keys(params).sort()
    .map((name) => [name, key(evalExpr(params[name], scope))]));

const received = (values: Record<string, unknown>) =>
  Object.fromEntries(Object.keys(values).sort().map((name) => [name, key(values[name])]));

type Outcome = { ok: true } | { error: string };

const outcome = (action: () => unknown): Outcome => {
  try {
    action();
    return { ok: true };
  } catch (error) {
    return { error: `${(error as Error)?.constructor?.name}: ${(error as Error)?.message}` };
  }
};

/** The first refusal of reading `params` one by one with `evalExpr`, in
 * the order of their names. */
const firstRefusal = (params: Record<string, string>, scope: EvalScope): Outcome =>
  outcome(() => Object.keys(params).sort().map((name) => evalExpr(params[name], scope)));

const positionsOf = (shape: FlexibleShape): THREE.BufferAttribute =>
  shape.mesh.geometry.getAttribute('position') as THREE.BufferAttribute;

/** The ten numbers: the box's two corners, the sphere's centre and radius. */
const tenOf = (geometry: THREE.BufferGeometry): string[] => {
  const box = geometry.boundingBox!;
  const sphere = geometry.boundingSphere!;
  return [box.min.x, box.min.y, box.min.z, box.max.x, box.max.y, box.max.z,
          sphere.center.x, sphere.center.y, sphere.center.z, sphere.radius].map(key);
};

/** three.js's own bounds of a copy of `array`. */
const threeBoundsOf = (array: ArrayLike<number>): string[] => {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(array), 3));
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  return tenOf(geometry);
};

// ---------------------------------------------------------------------
// R. The work, counted on the base.
// ---------------------------------------------------------------------

const FIVE = {
  height: '(40 - v.lift)',
  a: '(v.lift * 2)',
  b: '(v.lift + 1)',
  c: 'min(v.lift, 3)',
  d: '(v.lift > 1)',
};

describe('a warm read of a part does no work it did before', () => {
  it('R1. a warm read looks nothing up', () => {
    const shape = part(FIVE);
    shape.evaluate(at(0));
    clearCounts();

    shape.evaluate(at(1));

    expect(evaluations()).toBe(1);
    expect({ prepare: prepares(), withExpressions: scopes() })
      .toEqual({ prepare: 0, withExpressions: 1 });
  });

  it('R2. a warm judgement looks nothing up', () => {
    const shape = part(FIVE);
    shape.evaluate(at(0));
    clearCounts();

    shape.admit(at(2));

    expect(evaluations()).toBe(1);
    expect({ prepare: prepares(), withExpressions: scopes() })
      .toEqual({ prepare: 0, withExpressions: 1 });
  });

  it('R3. through the tree, shown and judged', async () => {
    const tree = new WidgetTree(engine([node('spring', FIVE)]), '/build/');
    await tree.loaded;
    tree.update(at(0));
    clearCounts();

    tree.update(at(1), lifted());
    const shown = { prepare: prepares(), molejo: evaluations() };
    clearCounts();
    tree.admit(at(2), lifted());
    const judged = { prepare: prepares(), molejo: evaluations() };

    expect({ shown, judged }).toEqual({
      shown: { prepare: 0, molejo: 1 }, judged: { prepare: 0, molejo: 1 },
    });
    tree.dispose();
  });

  it('R4. a rebuild does not read the vertices through the accessors', () => {
    const shape = part({ height: '(40 - v.lift)' });
    shape.evaluate(at(0));
    const attribute = positionsOf(shape);
    expect(attribute.count).toBe(SPRING_VERTICES);
    const prototype = THREE.BufferAttribute.prototype;
    const spies = {
      getX: vi.spyOn(prototype, 'getX'),
      getY: vi.spyOn(prototype, 'getY'),
      getZ: vi.spyOn(prototype, 'getZ'),
    };
    const ofPart = (spy: { mock: { contexts: unknown[] } }) =>
      spy.mock.contexts.filter((receiver) => receiver === attribute).length;

    shape.evaluate(at(3));

    const calls = {
      getX: ofPart(spies.getX), getY: ofPart(spies.getY), getZ: ofPart(spies.getZ),
    };
    Object.values(spies).forEach((spy) => spy.mockRestore());
    expect(evaluations()).toBe(2);
    expect(calls).toEqual({ getX: 0, getY: 0, getZ: 0 });
    expect(tenOf(shape.mesh.geometry)).toEqual(threeBoundsOf(attribute.array));
  });
});

// ---------------------------------------------------------------------
// P. Values and refusals against `evalExpr`.
// ---------------------------------------------------------------------

describe('a part reads the values evaluating each expression by itself gives', () => {
  it('P1. values, in value and in type, shown and judged', () => {
    const bound = table([{ name: '_b0', expression: '(v.lift + 0.5)' }]);
    const params = {
      height: '(40 - v.lift)',
      compare: '(v.lift > 1)',
      list: '[v.lift]',
      pair: '[1, 2]',
      text: '"7"',
      unknown: 'nobody',
      group: 'v',
      callee: 'sin',
      signed: '(0 * v.lift)',
      nan: '((v.lift / 0) * 0)',
      timed: '(2 * $t)',
      name: '_b0',
      over: '(_b0 * 2)',
    };
    const shape = part(params, bound);
    const judged = part(params, bound);
    const lifts = [-1, 0, 2, 3.5, -2.25];
    lifts.forEach((lift, i) => {
      const scope = at(lift, 0, i / 8, bound.roots());

      molejo().mockClear();
      shape.evaluate(scope);
      expect(evaluations(), `lift ${lift}`).toBe(1);
      expect(received(lastValues()), `lift ${lift}`).toEqual(expected(params, scope));

      molejo().mockClear();
      judged.admit(scope);
      expect(evaluations(), `lift ${lift}`).toBe(1);
      expect(received(lastValues()), `lift ${lift}`).toEqual(expected(params, scope));
    });
    // The forms the values above stand for, as `evalExpr` gives them.
    const scope = at(-1, 0, 0.25, bound.roots());
    expect(Object.fromEntries(Object.entries(params).map(
      ([name, text]) => [name, key(evalExpr(text, scope))]))).toEqual({
      height: '41', compare: '0', list: '-1', pair: 'NaN', text: '7', unknown: 'NaN',
      group: 'NaN', callee: 'NaN', signed: '-0', nan: 'NaN', timed: '0.5',
      name: '-0.5', over: '-1',
    });
  });

  it('P2. one refusal, before anything is written', () => {
    // `b` sorts second and reads a member of the number 1 at `gate.on = 1`.
    const params = { a: '(v.lift + 1)', b: '(1 + gate.on.x)', height: '(40 - v.lift)' };
    const shape = part(params);
    shape.evaluate(at(0, 0));
    const attribute = positionsOf(shape);
    const positions = Array.from(attribute.array);
    const version = attribute.version;
    const refused = firstRefusal(params, at(3, 1));
    expect('error' in refused).toBe(true);
    molejo().mockClear();

    expect(outcome(() => shape.evaluate(at(3, 1)))).toEqual(refused);
    expect(outcome(() => shape.admit(at(3, 1)))).toEqual(refused);

    expect(evaluations()).toBe(0);
    expect(attribute.version).toBe(version);
    expect(Array.from(attribute.array)).toEqual(positions);

    shape.evaluate(at(0, 0));
    shape.admit(at(0, 0));
    expect(evaluations()).toBe(0);
    expect(attribute.version).toBe(version);
  });

  it('P3. the first of two refusals, in the order of the names', () => {
    // A text the store refuses to prepare, beside one that throws when
    // evaluated; each order of their names.
    const unpreparable = '(x = 3)';
    const throwing = '(1 + gate.on.x)';
    for (const params of [
      { a: throwing, b: unpreparable, height: '(40 - v.lift)' },
      { a: unpreparable, b: throwing, height: '(40 - v.lift)' },
    ]) {
      const scope = at(3, 1);
      const refused = firstRefusal(params, scope);
      expect(refused).toEqual({
        error: params.a === throwing
          ? "TypeError: Cannot use 'in' operator to search for 'x' in 1"
          : 'Error: Expected ) at index 3, found =',
      });
      expect(outcome(() => part(params).evaluate(scope)), params.a).toEqual(refused);
      expect(outcome(() => part(params).admit(scope)), params.a).toEqual(refused);
      const twice = part(params);
      expect(outcome(() => twice.evaluate(scope)), params.a).toEqual(refused);
      expect(outcome(() => twice.evaluate(scope)), params.a).toEqual(refused);
    }
    expect(evaluations()).toBe(0);
  });

  it('P4. a parameter the flat pass serves', async () => {
    FLAT_PASS.minimumBindings = 0;
    const bound = table([
      { name: '_b0', expression: '(v.lift * 2)' },
      { name: '_b1', expression: '(30 + _b0)' },
    ]);
    const bare = { height: '_b1' };
    const over = { height: '(_b1 - 5)' };
    const tree = new WidgetTree(engine([node('bare', bare), node('over', over)]),
                                '/build/', null, bound);
    await tree.loaded;
    resetExpressionMetrics();
    const figures: { resolutions: number; entries: number }[] = [];
    [0, 1.5, 4].forEach((lift, i) => {
      const scope = at(lift, 0, 0, bound.roots());
      molejo().mockClear();
      tree.update(scope, i === 0 ? 'all' : lifted());
      figures.push({
        resolutions: expressionMetrics().resolutions, entries: flatPassMetrics().entries,
      });
      expect(evaluations()).toBe(2);
      const calls = molejo().mock.calls;
      expect(received(calls[0][1] as Record<string, unknown>)).toEqual(expected(bare, scope));
      expect(received(calls[1][1] as Record<string, unknown>)).toEqual(expected(over, scope));
    });
    console.log(`P4 figures: ${JSON.stringify(figures)}`);
    expect(flatPassMetrics().runs).toBeGreaterThan(0);
    expect(figures).toEqual(P4_FIGURES);
    tree.dispose();
  });
});

// Printed by P4 on the base (cb0a5958) and written here: the reader makes
// `evalExpr`'s `valueOf` calls, so neither count moves.
const P4_FIGURES: { resolutions: number; entries: number }[] = [
  { resolutions: 3, entries: 2 },
  { resolutions: 6, entries: 4 },
  { resolutions: 9, entries: 6 },
];

// ---------------------------------------------------------------------
// L. What a part keeps, and for how long.
// ---------------------------------------------------------------------

describe('a part never reads anything prepared before a reclamation', () => {
  it('L1. a reclamation between two reads', () => {
    const params = { p: '(2 * v.lift)', q: '(3 + v.lift)' };
    const shape = part(params, EMPTY_BINDINGS, springSpec('p'));
    shape.evaluate(at(1));
    expect(received(lastValues())).toEqual(expected(params, at(1)));
    const before = [prepare(params.p), prepare(params.q)];

    reclaim();
    // Prepared in the other order, the two texts trade their ids.
    evalExpr(params.q, at(5));
    evalExpr(params.p, at(5));
    expect([prepare(params.p), prepare(params.q)]).toEqual([before[1], before[0]]);
    clearCounts();

    shape.evaluate(at(5));
    const prepared = prepares();
    expect(received(lastValues())).toEqual(expected(params, at(5)));
    expect(received(lastValues())).toEqual({ p: '10', q: '8' });
    expect(prepared).toBe(2);

    clearCounts();
    shape.evaluate(at(6));
    expect(received(lastValues())).toEqual(expected(params, at(6)));
  });

  // The rest of L1, apart because it is a count the base cannot meet: the
  // base prepares every text on every read.
  it('L1b. the read after the one that prepared again prepares nothing', () => {
    const params = { p: '(2 * v.lift)', q: '(3 + v.lift)' };
    const shape = part(params, EMPTY_BINDINGS, springSpec('p'));
    shape.evaluate(at(1));
    reclaim();
    evalExpr(params.q, at(5));
    evalExpr(params.p, at(5));
    shape.evaluate(at(5));
    clearCounts();

    shape.evaluate(at(6));

    expect(prepares()).toBe(0);
    expect(received(lastValues())).toEqual(expected(params, at(6)));
  });

  it('L2. a rebind', () => {
    const shape = part({ height: '(40 - v.lift)', a: '(v.lift * 2)' });
    shape.evaluate(at(1));
    shape.evaluate(at(2));
    const next = { height: '(41 - v.lift)', a: '(v.lift * 3)' };
    shape.rebind({ tech: 'molejo', spec: springSpec(), params: next });
    clearCounts();

    shape.evaluate(at(2));

    expect(prepares()).toBe(2);
    expect(evaluations()).toBe(1);
    expect(received(lastValues())).toEqual(expected(next, at(2)));
    expect(received(lastValues())).toEqual({ height: '39', a: '6' });
  });

  it('L3. two documents, posed alternately across a reclamation', async () => {
    const doubled = table([{ name: '_b0', expression: '(v.lift * 2)' }]);
    const shifted = table([{ name: '_b0', expression: '(v.lift + 7)' }]);
    const params = { height: '(30 + _b0)' };
    const first = new WidgetTree(engine([node('first', params)]), '/build/', null, doubled);
    const second = new WidgetTree(engine([node('second', params)]), '/build/', null, shifted);
    await Promise.all([first.loaded, second.loaded]);
    const poses: [WidgetTree, BindingTable, number][] = [
      [first, doubled, 0], [second, shifted, 0], [first, doubled, 1], [second, shifted, 2],
      [first, doubled, 3], [second, shifted, 3],
    ];
    poses.forEach(([tree, bound, lift], i) => {
      if (i === 3) reclaim();
      const scope = at(lift, 0, 0, bound.roots());
      molejo().mockClear();
      tree.update(scope, i < 2 ? 'all' : lifted());
      expect(evaluations(), `pose ${i}`).toBe(1);
      expect(received(lastValues()), `pose ${i}`).toEqual(expected(params, scope));
      expect(received(lastValues()), `pose ${i}`).toEqual({
        height: key(30 + (bound === doubled ? lift * 2 : lift + 7)),
      });
    });
    first.dispose();
    second.dispose();
  });

  it('L4. pressure at depth 0', () => {
    EXPRESSION_LIMITS.nodes = 1;
    EXPRESSION_LIMITS.everyOperation = true;
    const params = { height: '(40 - v.lift)', a: '(v.lift * 2)', b: 'min(v.lift, 3)' };
    const shape = part(params);
    evalExpr('1', at(0));
    for (const lift of [1, 2, 3.25]) {
      const generation = expressionGeneration();
      molejo().mockClear();
      shape.evaluate(at(lift));
      expect(expressionGeneration(), `lift ${lift}`).toBeGreaterThan(generation);
      expect(evaluations(), `lift ${lift}`).toBe(1);
      expect(received(lastValues()), `lift ${lift}`).toEqual(expected(params, at(lift)));
    }
  });

  // Added in review: the generation must be read inside the reading
  // scope. Here the roots are of the present generation when the read
  // begins, and the scope's own start empties the store; a reader that
  // had read the generation before opening its scope would reuse them.
  it('L4b. pressure switched on over a warm part', () => {
    const params = { height: '(40 - v.lift)', a: '(v.lift * 2)', b: 'min(v.lift, 3)' };
    const shape = part(params);
    shape.evaluate(at(1));
    EXPRESSION_LIMITS.nodes = 1;
    EXPRESSION_LIMITS.everyOperation = true;
    const generation = expressionGeneration();
    molejo().mockClear();

    shape.evaluate(at(2));

    expect(expressionGeneration()).toBeGreaterThan(generation);
    expect(evaluations()).toBe(1);
    expect(received(lastValues())).toEqual(expected(params, at(2)));
  });

  it('L5. a judgement after a reclamation refuses what an evaluation refuses', () => {
    const params = { height: 'sqrt((10 - v.lift))', z: '(1 + gate.on.x)' };
    const judged = part(params);
    const shown = part(params);
    judged.evaluate(at(0, 0));
    shown.evaluate(at(0, 0));
    reclaim();
    const cases: [number, number][] = [[3, 0], [12, 0], [3, 1], [4, 0], [4, 1], [11, 0], [1, 0]];
    const outcomes = cases.map(([lift, on], i) => {
      if (i === 4) reclaim();
      const scope = at(lift, on);
      molejo().mockClear();
      const judgement = outcome(() => judged.admit(scope));
      const judgedValues = evaluations() > 0 ? received(lastValues()) : null;
      molejo().mockClear();
      const evaluation = outcome(() => shown.evaluate(scope));
      const shownValues = evaluations() > 0 ? received(lastValues()) : null;
      expect(judgement, `lift ${lift}, on ${on}`).toEqual(evaluation);
      expect(judgedValues, `lift ${lift}, on ${on}`).toEqual(shownValues);
      return 'error' in evaluation ? evaluation.error.split(':')[0] : 'accepted';
    });
    // The cases cover acceptance and both kinds of refusal.
    expect(outcomes).toEqual([
      'accepted', 'EvaluationError', 'TypeError', 'accepted', 'TypeError',
      'EvaluationError', 'accepted',
    ]);
  });
});

// ---------------------------------------------------------------------
// B. The bounds against three.js's own.
// ---------------------------------------------------------------------

type Make = () => THREE.BufferGeometry;

const fromArray = (values: ArrayLike<number>): Make => () => {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(values), 3));
  return geometry;
};

/** One geometry bounded by three.js's two functions, one by
 * `computeFlexibleBounds`: the ten numbers and the console's calls
 * compared. Returns how many calls three.js made. */
function compareBounds(make: Make, label: string): number {
  const errors = vi.spyOn(console, 'error').mockImplementation(() => undefined);
  try {
    const theirs = make();
    theirs.computeBoundingBox();
    theirs.computeBoundingSphere();
    const theirCalls = errors.mock.calls.map((call) => [...call]);
    errors.mockClear();
    const ours = make();
    computeFlexibleBounds(ours);
    const ourCalls = errors.mock.calls.map((call) => [...call]);

    expect(tenOf(ours), label).toEqual(tenOf(theirs));
    expect(ourCalls.map((call) => [call.length, call[0]]), label)
      .toEqual(theirCalls.map((call) => [call.length, call[0]]));
    ourCalls.forEach((call) => expect(call[1], label).toBe(ours));
    theirCalls.forEach((call) => expect(call[1], label).toBe(theirs));
    return theirCalls.length;
  } finally {
    errors.mockRestore();
  }
}

// A seeded sweep: the same arrays on every run.
function seeded(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const FLOAT_MAX = 3.4028234663852886e38;

describe('a rebuilt part\'s bounds are three.js\'s, number for number', () => {
  it('B1. edge arrays', () => {
    const arrays: [string, number[]][] = [
      ['empty', []],
      ['one vertex', [1.5, -2, 3.25]],
    ];
    for (let axis = 0; axis < 3; axis += 1) {
      const vertex = (value: number, others = [4, -5, 6]) => {
        const out = [...others];
        out[axis] = value;
        return out;
      };
      arrays.push([`axis ${axis}: -0 alone`, vertex(-0)]);
      arrays.push([`axis ${axis}: 0 alone`, vertex(0)]);
      arrays.push([`axis ${axis}: -0 then 0`, [...vertex(-0), ...vertex(0)]]);
      arrays.push([`axis ${axis}: 0 then -0`, [...vertex(0), ...vertex(-0)]]);
      arrays.push([`axis ${axis}: -0 twice`, [...vertex(-0), ...vertex(-0, [1, 2, 3])]]);
      arrays.push([`axis ${axis}: NaN first`, [...vertex(NaN), ...vertex(1, [1, 2, 3])]]);
      arrays.push([`axis ${axis}: NaN last`, [...vertex(1, [1, 2, 3]), ...vertex(NaN)]]);
      arrays.push([`axis ${axis}: NaN alone`, vertex(NaN)]);
      arrays.push([`axis ${axis}: +Infinity`, [...vertex(Infinity), ...vertex(1, [1, 2, 3])]]);
      arrays.push([`axis ${axis}: -Infinity`, [...vertex(-Infinity), ...vertex(1, [1, 2, 3])]]);
      arrays.push([`axis ${axis}: both infinities`,
                   [...vertex(Infinity), ...vertex(-Infinity, [1, 2, 3])]]);
      arrays.push([`axis ${axis}: +Infinity alone`, vertex(Infinity)]);
    }
    arrays.push(['the single-precision limit',
                 [FLOAT_MAX, -FLOAT_MAX, 1.17549435e-38, -FLOAT_MAX, FLOAT_MAX, 1.4e-45,
                  FLOAT_MAX, FLOAT_MAX, -1.4e-45]]);
    arrays.push(['beyond it', [3.5e38, -3.5e38, 0, 1, 2, 3]]);
    const random = seeded(20261121);
    for (let n = 0; n < 200; n += 1) {
      const vertices = 1 + Math.floor(random() * 50);
      const scale = 10 ** Math.floor(random() * 12 - 6);
      arrays.push([`random ${n}`, Array.from({ length: vertices * 3 },
                                             () => (random() - 0.5) * scale)]);
    }

    const reports = new Map<string, number>();
    for (const [label, values] of arrays) {
      reports.set(label, compareBounds(fromArray(values), label));
    }
    // The cases reach both of three.js's reports and its silence.
    expect(reports.get('empty')).toBe(0);
    expect(reports.get('axis 1: NaN first')).toBe(2);
    expect(reports.get('axis 2: +Infinity')).toBe(1);
    expect(reports.get('axis 0: both infinities')).toBe(1);

    // Like three.js, it writes into the box and sphere a geometry has,
    // and allocates them when it has none.
    const held = fromArray([1, 2, 3, 4, 5, 6])();
    const box = new THREE.Box3();
    const sphere = new THREE.Sphere();
    held.boundingBox = box;
    held.boundingSphere = sphere;
    computeFlexibleBounds(held);
    expect(held.boundingBox).toBe(box);
    expect(held.boundingSphere).toBe(sphere);
    expect(tenOf(held)).toEqual(threeBoundsOf([1, 2, 3, 4, 5, 6]));
    const fresh = fromArray([1, 2, 3])();
    expect(fresh.boundingBox).toBeNull();
    expect(fresh.boundingSphere).toBeNull();
    computeFlexibleBounds(fresh);
    expect(fresh.boundingBox).toBeInstanceOf(THREE.Box3);
    expect(fresh.boundingSphere).toBeInstanceOf(THREE.Sphere);
  });

  it('B2. arrays molejo produces', () => {
    const read = (path: string): any => JSON.parse(
      readFileSync(new URL(path, import.meta.url)).toString('utf8'));
    const cases: [string, Record<string, unknown>, Record<string, number>][] = [];

    const parity = read('./parity-fixture.json').flexible;
    for (const one of parity.cases) cases.push([`parity ${one.name}`, parity.spec, one.params]);

    const grid = [-4, -1.5, 0, 0.75, 3, 12, 17.9];
    for (const name of ['lock', 'touched', 'pascaline']) {
      const document = read(`../../../../../tests/fixtures/${name}/viewer.json`);
      const specs = new Map<string, Record<string, unknown>>();
      const walk = (one: ManifestNode): void => {
        if (one.flexible) specs.set(JSON.stringify(one.flexible.spec), one.flexible.spec);
        (one.children ?? []).forEach(walk);
      };
      walk(document.root);
      expect(specs.size, name).toBeGreaterThan(0);
      for (const spec of specs.values()) {
        const names = [...parameterNames(spec)];
        for (const value of grid) {
          cases.push([`${name} at ${value}`, spec,
                      Object.fromEntries(names.map((one) => [one, value]))]);
        }
      }
    }

    const circle = { type: 'circle', radius: 1.25 };
    const square = { type: 'polygon', points: [[-1, -0.5], [1, -0.5], [1, 0.5], [-1, 0.5]] };
    const open = (profile: Record<string, unknown>, path: unknown[], count: number) => ({
      molejo: '0.1', profile, path, loop: false,
      tessellation: { path: count, profile: profile === square ? 4 : 7 },
    });
    const written: [string, Record<string, unknown>][] = [
      ['line', open(circle, [{ type: 'line', to: [{ param: 'h' }, 2, 30] }], 5)],
      ['arc', open(square, [{ type: 'arc', center: [{ param: 'h' }, 0, 0], axis: [0, 1, 0],
                              angle: 1.2 }], 12)],
      ['helix', open(square, [{ type: 'helix', radius: 6, turns: 2.5, height: { param: 'h' } }],
                     40)],
      ['spline', open(circle, [{ type: 'spline', points: [[{ param: 'h' }, 0, 10], [0, 3, 20]],
                                 start_tangent: [0, 0, 1] }], 16)],
      ['line, arc and helix', open(circle, [
        { type: 'line', to: [0, 0, 8] },
        { type: 'arc', center: [-5, 0, 8], axis: [0, 1, 0], angle: { param: 'h' } },
        { type: 'helix', radius: 3, turns: 1, height: 6 },
      ], 30)],
      ['wrap', {
        molejo: '0.1', profile: square, loop: true,
        path: [{ type: 'wrap', around: [
          { center: [0, 0], radius: { param: 'h' } }, { center: [30, 0], radius: 3 },
        ] }],
        tessellation: { path: 48, profile: 4 },
      }],
    ];
    for (const [label, spec] of written) {
      for (const h of [0.5, 2, 9.5, 25]) cases.push([`${label} at ${h}`, spec, { h }]);
    }
    for (const height of [1e39, 1e308]) {
      cases.push([`the test spring at ${height}`, springSpec(), { height }]);
    }

    let compared = 0;
    let infinite = 0;
    const refused: string[] = [];
    for (const [label, spec, values] of cases) {
      let positions: Float32Array;
      try {
        positions = evaluate(spec, values).positions;
      } catch (error) {
        refused.push(`${label}: ${(error as Error).message}`);
        continue;
      }
      if (!positions.every(Number.isFinite)) infinite += 1;
      compareBounds(fromArray(positions), label);
      compared += 1;
    }
    console.log(`B2: ${compared} arrays compared, ${infinite} with positions not finite; `
      + `refused by molejo: ${refused.length ? refused.join('; ') : 'none'}`);
    expect(refused).toEqual([]);
    expect(compared).toBe(cases.length);
    expect(infinite).toBe(2);
  });

  it('B3. the guard sends what it was not proved for to three.js', () => {
    const vertices = evaluate(springSpec(), { height: 30 }).positions;
    const count = vertices.length / 3;
    const plain = fromArray(vertices);

    const morph = (relative: boolean): Make => () => {
      const geometry = plain();
      const offsets = new Float32Array(vertices.length);
      for (let i = 0; i < offsets.length; i += 3) offsets[i] = 100 + i / 3;
      geometry.morphAttributes.position = [new THREE.BufferAttribute(offsets, 3)];
      geometry.morphTargetsRelative = relative;
      return geometry;
    };
    const interleaved: Make = () => {
      const data = new Float32Array(count * 4);
      for (let i = 0; i < count; i += 1) {
        data.set(vertices.subarray(i * 3, i * 3 + 3), i * 4);
        data[i * 4 + 3] = 1000;
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.InterleavedBufferAttribute(
        new THREE.InterleavedBuffer(data, 4), 3, 0) as unknown as THREE.BufferAttribute);
      return geometry;
    };
    const half: Make = () => {
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.Float16BufferAttribute(
        Array.from(vertices, (value) => THREE.DataUtils.toHalfFloat(value)), 3));
      return geometry;
    };
    const four: Make = () => {
      const data = new Float32Array(count * 4);
      for (let i = 0; i < count; i += 1) {
        data.set(vertices.subarray(i * 3, i * 3 + 3), i * 4);
        data[i * 4 + 3] = -1000;
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.BufferAttribute(data, 4));
      return geometry;
    };
    const gl: Make = () => {
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.GLBufferAttribute(
        {} as WebGLBuffer, 5126, 3, 4, count) as unknown as THREE.BufferAttribute);
      return geometry;
    };
    const none: Make = () => new THREE.BufferGeometry();
    const own: Make = () => {
      const geometry = plain();
      const attribute = geometry.getAttribute('position') as THREE.BufferAttribute;
      attribute.getX = function getX(this: THREE.BufferAttribute, index: number) {
        return 2 * this.array[index * 3];
      };
      return geometry;
    };

    expect(compareBounds(morph(true), 'relative morph')).toBe(0);
    expect(compareBounds(morph(false), 'absolute morph')).toBe(0);
    expect(compareBounds(interleaved, 'interleaved')).toBe(0);
    expect(compareBounds(half, 'half float')).toBe(0);
    expect(compareBounds(four, 'item size 4')).toBe(0);
    expect(compareBounds(gl, 'GL attribute')).toBe(2);
    expect(compareBounds(none, 'no position')).toBe(0);
    expect(compareBounds(own, 'own accessor')).toBe(0);
    // Added in review: the array test of the guard, alone. A normalized
    // integer array keeps `BufferAttribute`'s accessors and item size 3,
    // and only those accessors denormalize what it holds.
    const shorts: Make = () => {
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.BufferAttribute(
        new Int16Array([32767, -32767, 0, 1200, -5, 16000, -20000, 77, 3]), 3, true));
      return geometry;
    };
    expect(compareBounds(shorts, 'normalized shorts')).toBe(0);

    // A normalized `Float32Array` reads as itself: the fast path runs, and
    // reads no accessor.
    const normalized: Make = () => {
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position',
                            new THREE.BufferAttribute(new Float32Array(vertices), 3, true));
      return geometry;
    };
    expect(compareBounds(normalized, 'normalized')).toBe(0);
    const geometry = normalized();
    const getX = vi.spyOn(THREE.BufferAttribute.prototype, 'getX');
    computeFlexibleBounds(geometry);
    const reads = getX.mock.contexts
      .filter((receiver) => receiver === geometry.getAttribute('position')).length;
    getX.mockRestore();
    expect(reads).toBe(0);
  });
});
