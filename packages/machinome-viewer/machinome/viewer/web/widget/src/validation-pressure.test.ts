/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */
import { afterEach, beforeEach, expect, it } from 'vitest';
import { assertRenderable } from './viewer';
import {
  EXPRESSION_LIMITS, expressionGeneration, expressionMetrics,
  profileInspectionMetrics, releaseExpressions, retainExpressions,
  resetExpressionMetrics, withExpressions,
  inspectProfileExpression, prepare, validationProfileInspector,
} from './expressions';
import { bindingPreparationMetrics, resetBindingPreparationMetrics } from './bindings';
import { evalExpr } from './evaluator';
import type { Manifest } from './types';

const limit = EXPRESSION_LIMITS.nodes;
const everyOperation = EXPRESSION_LIMITS.everyOperation;
beforeEach(() => {
  retainExpressions(); releaseExpressions();
  resetExpressionMetrics(); resetBindingPreparationMetrics();
});
afterEach(() => {
  EXPRESSION_LIMITS.nodes = limit;
  EXPRESSION_LIMITS.everyOperation = everyOperation;
  retainExpressions(); releaseExpressions();
});

function document(size = 80, readers = 30): Manifest {
  const expressions = Array.from({ length: readers }, (_, i) => `_b${size - 1} + ${i + 1000}`);
  return {
    format: 'machinome-export', version: 4,
    drivers: { x: { default: 2, range: null, unit: 'mm', dtype: null, scale: null } },
    bindings: Array.from({ length: size }, (_, i) => ({ name: `_b${i}`,
      expression: i === 0 ? 'x * 2' : `_b${i - 1} + ${i}` })),
    root: { name: 'root', type: 'assembly', color: null,
      operations: expressions.map(expression => ['t', [expression, '0', '0']]),
      children: [{ name: 'spring', type: 'leaf', color: null, operations: [],
        flexible: { tech: 'molejo', spec: {
          molejo: '0.1', profile: { type: 'circle', radius: 2 },
          path: [{ type: 'helix', radius: 14, turns: 6.5, height: { param: 'height' } }],
          loop: false, tessellation: { path: 24, profile: 8 },
        }, params: { height: `_b${size - 1} + 2000` } } }],
    },
  };
}

it('prepares one coherent validation graph above finite headroom and keeps it for the next operation', () => {
  // The shipping policy (OpenSpec `keep-a-live-model-parsed`, design
  // Decision 5): an ordinary operation after the load reclaims nothing.
  EXPRESSION_LIMITS.nodes = 5;
  const generation = expressionGeneration();
  const { table } = assertRenderable(document(), '/pressure.json');
  expect(bindingPreparationMetrics()).toBe(1);
  expect(expressionMetrics().nodes).toBeGreaterThan(5);
  expect(expressionGeneration()).toBe(generation);
  const result = withExpressions(() => evalExpr('_b79', {
    time: 0, drivers: { x: 2 }, bindings: table.roots(),
  }));
  expect(Object.is(result, 3164)).toBe(true);
  expect(expressionGeneration()).toBe(generation);
  expect(bindingPreparationMetrics()).toBe(1);
});

it('prepares one coherent validation graph above finite headroom and reconstructs afterward', () => {
  // Forced reclamation before every outermost operation (design
  // Decision 5): the operation after the load reclaims and re-prepares.
  EXPRESSION_LIMITS.nodes = 5;
  EXPRESSION_LIMITS.everyOperation = true;
  const generation = expressionGeneration();
  const { table } = assertRenderable(document(), '/pressure.json');
  console.info({ preparations: bindingPreparationMetrics(), generations: expressionGeneration() - generation });
  expect(bindingPreparationMetrics()).toBe(1);
  expect(expressionGeneration()).toBe(generation);
  expect(expressionMetrics().nodes).toBeGreaterThan(5);
  const result = withExpressions(() => evalExpr('_b79', {
    time: 0, drivers: { x: 2 }, bindings: table.roots(),
  }));
  expect(Object.is(result, 3164)).toBe(true);
  expect(expressionGeneration()).toBe(generation + 1);
  expect(bindingPreparationMetrics()).toBe(2);
});

it('inspects a shared negative prefix once across operations and flexible parameters', () => {
  const { table } = assertRenderable(document(), '/shared-prefix.json');
  console.info({ visits: profileInspectionMetrics(), nodes: expressionMetrics().nodes });
  expect(profileInspectionMetrics()).toBeLessThanOrEqual(expressionMetrics().nodes);
  expect(Object.is(withExpressions(() => evalExpr('_b79', {
    time: 0, drivers: { x: -0 }, bindings: table.roots(),
  })), 3160)).toBe(true);
});

it.each([
  ['profileOverlap', /must be called directly/],
  ['(profileOverlap)(0, 0)', /exactly eight arguments/],
  ['profileOverlap(0, 0, 0)', /exactly eight arguments/],
  ['profileOverlap(-1, 0, 0, 0, 0, 0, 0, 0)', /literal nonnegative integers/],
  ['profileOverlap(x, 0, 0, 0, 0, 0, 0, 0)', /literal nonnegative integers/],
  ['profileOverlap(0, 0, 0, 0, 0, 0, 0, 0)', /outside a numeric Bound/],
] as const)('refuses %s after a shared clear prefix, including a dead branch and flexible parameter', (bad, error) => {
  for (const flexible of [false, true]) {
    const doc = document();
    doc.bindings!.push({ name: '_bad', expression: bad });
    const expression = 'false ? _bad : _b79';
    if (flexible) doc.root.children![0].flexible!.params.height = expression;
    else doc.root.operations.push(['t', [expression, '0', '0']]);
    expect(() => assertRenderable(doc, '/reserved.json')).toThrow(error);
  }
});

it('checks reserved direct-callee context before visited shortcuts, and never publishes positive or failed walks', () => {
  withExpressions(() => {
    const inspect = validationProfileInspector();
    const direct = 'profileOverlap(0, 0, 0, 0, 0, 0, 0, 0)';
    const mixed = prepare(`[${direct}, profileOverlap]`);
    for (let attempt = 0; attempt < 2; attempt++) {
      expect(() => inspect(mixed)).toThrow(/must be called directly/);
      expect(inspect(prepare(direct))).toBe(true);
      expect(() => inspect(prepare('profileOverlap'))).toThrow(/must be called directly/);
    }
    const alias = new Map([['_fn', prepare('profileOverlap')]]);
    expect(() => validationProfileInspector(alias)(prepare('_fn(0, 0, 0, 0, 0, 0, 0, 0)')))
      .toThrow(/must be called directly/);
    expect(() => inspectProfileExpression(prepare(direct), undefined, 0))
      .toThrow(/outside the table/);
  });
});

it('discards negative facts between document meanings and operations, even when node IDs are reused', () => {
  const a = document();
  assertRenderable(a, '/a.json');
  const b = document();
  b.bindings![0].expression = 'profileOverlap(0, 0, 0, 0, 0, 0, 0, 0)';
  expect(() => assertRenderable(b, '/b.json')).toThrow(/outside a numeric Bound/);
  EXPRESSION_LIMITS.nodes = 1;
  const generation = expressionGeneration();
  assertRenderable(a, '/a-again.json');
  expect(expressionGeneration()).toBeGreaterThan(generation);
  // Loads reclaim under both modes (design Decision 5): the refused load
  // empties a's graph at its start and its own partial graph at its end,
  // so each of the three validations reuses node ids from zero.
  const beforeB = expressionGeneration();
  expect(() => assertRenderable(b, '/b-again.json')).toThrow(/outside a numeric Bound/);
  expect(expressionGeneration()).toBeGreaterThanOrEqual(beforeB + 2);
  const { table } = assertRenderable(a, '/last-good.json');
  expect(withExpressions(() => evalExpr('_b79', { time: 0, drivers: { x: 2 }, bindings: table.roots() })))
    .toBe(3164);
  retainExpressions(); releaseExpressions();
  expect(expressionMetrics().nodes).toBe(0);
});

it('refuses an invalid unreferenced late entry in an oversized table and releases its scope', () => {
  EXPRESSION_LIMITS.nodes = 5;
  for (const expression of ['missing + 1', '_bad + 1', '(x => x + 1)']) {
    const bad = document();
    bad.bindings!.push({ name: '_bad', expression });
    // The refused partial graph is reclaimed at the refused load's own
    // end, which can only run once its scope has closed (design
    // Decision 5).
    const generation = expressionGeneration();
    expect(() => assertRenderable(bad, '/late.json')).toThrow(/missing|names itself|Func/);
    expect(expressionGeneration()).toBeGreaterThan(generation);
    const { table } = assertRenderable(document(), '/recovery.json');
    expect(withExpressions(() => evalExpr('_b79', {
      time: 0, drivers: { x: 2 }, bindings: table.roots(),
    }))).toBe(3164);
  }
});
