/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import { describe, expect, it } from 'vitest';
import { expressionMetrics, prepare, resetExpressionMetrics, withExpressions } from '../expressions';
import type { KinkLevel } from '../expressions';
import { expressionKinkBreaks, kinkBreaks } from './jumps';
import { kinkLevel } from './program';
import type { PathHost } from './program';

const program = { nodeOf: prepare, bindings: { roots: () => new Map() },
  limits: { crossingTolerance: 1e-12 } } as unknown as PathHost;

function ordinary(host: PathHost, kinks: readonly KinkLevel[],
                  start: number, delta: number, left = 0, right = 1): number[] {
  return kinkBreaks(kinks, (kink, t) => kinkLevel(host, kink,
    { x: start + delta * t }), left, right, 1e-12);
}

function cached(host: PathHost, kinks: readonly KinkLevel[],
                start: number, delta: number, left = 0, right = 1): number[] {
  return expressionKinkBreaks(host, kinks, { x: start }, { x: delta }, {},
    left, right, 1e-12);
}

describe('expression-backed kink probe reuse', () => {
  it('returns identical cuts with fewer pure expression resolutions', () => withExpressions(() => {
    const kinks = [{ a: prepare('x - 0.25'), b: null },
      { a: prepare('x - 0.75'), b: null }];
    resetExpressionMetrics();
    const before = ordinary(program, kinks, 0, 1);
    const baseline = expressionMetrics().resolutions;
    resetExpressionMetrics();
    const after = cached(program, kinks, 0, 1);
    expect(after).toEqual(before);
    expect(after).toEqual([0.25, 0.75]);
    const repeated = [{ a: prepare('x + 1'), b: null }];
    resetExpressionMetrics();
    ordinary(program, [repeated[0], repeated[0], repeated[0]], 0, 1);
    const repeatedBaseline = expressionMetrics().resolutions;
    resetExpressionMetrics();
    cached(program, [repeated[0], repeated[0], repeated[0]], 0, 1);
    expect(expressionMetrics().resolutions).toBeLessThan(repeatedBaseline);
    expect(baseline).toBeGreaterThan(0);
  }));

  it('leaves generic stateful callbacks eager', () => withExpressions(() => {
    const one = { a: prepare('x'), b: null };
    let calls = 0;
    kinkBreaks([one, one], () => ++calls, 0, 1, 1e-12);
    expect(calls).toBe(4);
  }));

  it('rejects random calls and random or coercing bindings', () => withExpressions(() => {
    for (const [root, bindings] of [
      [prepare('random(1) + x'), new Map()],
      [prepare('alias + x'), new Map([['alias', prepare('random(1)')]])],
      [prepare('alias + x'), new Map([['alias', prepare('[1]')]])],
    ] as const) {
      const host = { ...program, bindings: { roots: () => bindings } } as PathHost;
      const kinks = [{ a: root, b: null }, { a: root, b: null }, { a: root, b: null }];
      resetExpressionMetrics();
      ordinary(host, kinks, 0, 1);
      const baseline = expressionMetrics().resolutions;
      resetExpressionMetrics();
      cached(host, kinks, 0, 1);
      expect(expressionMetrics().resolutions).toBe(baseline);
    }
  }));

  it('keeps distinct kinks, signed zero and nonfinite levels separate', () => withExpressions(() => {
    const a = { a: prepare('x - 0.25'), b: null };
    const b = { a: prepare('x - 0.75'), b: null };
    expect(cached(program, [a, b], 0, 1)).toEqual([0.25, 0.75]);
    for (const zero of [0, -0]) {
      expect(cached(program, [a, a], zero, 1, zero)).toEqual(
        ordinary(program, [a, a], zero, 1, zero));
    }
    const singular = { a: prepare('1 / (x - 1)'), b: null };
    let roots = 0;
    const counted = { ...program, bindings: { roots: () => {
      roots += 1;
      return new Map();
    } } } as PathHost;
    expect(cached(counted, [singular, singular], 0, 1)).toEqual(
      ordinary(program, [singular, singular], 0, 1));
    expect(roots).toBe(4); // proof, finite-low once, infinite-high twice
    expect(cached(program, [singular], 0, 1, -Infinity)).toEqual(
      ordinary(program, [singular], 0, 1, -Infinity));
  }));

  it('preserves first errors, fallback and fresh retry', () => withExpressions(() => {
    const good = { a: prepare('x - 0.25'), b: null };
    const bad = { a: prepare('x.y'), b: null };
    const first = () => ordinary(program, [good, good, bad], 1, 0);
    const next = () => cached(program, [good, good, bad], 1, 0);
    let original: unknown;
    try { first(); } catch (error) { original = error; }
    expect(original).toBeInstanceOf(TypeError);
    expect(next).toThrow((original as Error).message);
    expect(next).toThrow((original as Error).message);
  }));

  it('does not surface a preflight error before the scheduled callback error', () => withExpressions(() => {
    let roots = 0;
    const host = { ...program, bindings: { roots: () => {
      roots += 1;
      if (roots === 1) throw new Error('preflight only');
      return new Map();
    } } } as PathHost;
    const bad = { a: prepare('x.y'), b: null };
    expect(() => cached(host, [bad, bad, bad], 1, 0)).toThrow(TypeError);
  }));

  it('caps retention without eviction and starts each search afresh', () => withExpressions(() => {
    const root = prepare('x + 1');
    const kinks = Array.from({ length: 1025 }, () => ({ a: root, b: null }));
    kinks.push(kinks[1024]);
    let rootReads = 0;
    const host = { ...program, bindings: { roots: () => {
      rootReads += 1;
      return new Map();
    } } } as PathHost;
    ordinary(host, kinks, 1, 0);
    expect(rootReads).toBe(2052);
    rootReads = 0;
    cached(host, kinks, 1, 0);
    expect(rootReads).toBe(2053); // one proof + no eviction of saturated keys
    cached(host, [kinks[0], kinks[0], kinks[0]], 1, 0);
    expect(rootReads).toBe(2056); // next search: proof and two cached probes
  }));

  it('resolves a retained descriptor anew on a later search', () => withExpressions(() => {
    const first = { a: prepare('x'), b: null };
    const second = { a: prepare('x + 1'), b: null };
    let active = first;
    const retained = { ...first, current: () => active };
    expect(cached(program, [retained, retained, retained], 0, 1)).toEqual([]);
    active = second;
    expect(cached(program, [retained, retained, retained], 0, 1)).toEqual([]);
  }));
});
