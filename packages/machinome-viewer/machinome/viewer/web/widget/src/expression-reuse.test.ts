/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// OpenSpec `keep-a-live-model-parsed` (design Decisions 1 to 3): a loaded
// document's prepared graph is reused from one operation to the next
// whatever its size, and obsolete expression state is reclaimed where it
// is created -- a load's start, a refused load, a replacement's
// settlement and a viewer's disposal -- never between ordinary
// operations. Every document here is synthetic and built in the test.

import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { assertRenderable } from './viewer';
import {
  EXPRESSION_LIMITS, expressionGeneration, expressionMetrics, prepare,
  releaseExpressions, resetExpressionMetrics, retainExpressions, valueOf, withExpressions,
} from './expressions';
import {
  bindingPreparationMetrics, bindingTable, resetBindingPreparationMetrics,
} from './bindings';
import type { BindingTable } from './bindings';
import { evalExpr } from './evaluator';
import { WidgetTree } from './tree';
import type { Manifest } from './types';
import { loadClocked } from './clocked/document';
import { clockedMachine } from './clocked/machine';
import type { ClockedSnapshot } from './clocked/machine';
import { Engine } from './run/engine';
import type { RunDocument } from './run/program';
import runningCorpus from './running-corpus.json';

const limit = { ...EXPRESSION_LIMITS };
beforeEach(() => {
  retainExpressions(); releaseExpressions();
  resetExpressionMetrics(); resetBindingPreparationMetrics();
});
afterEach(() => {
  Object.assign(EXPRESSION_LIMITS, limit);
  retainExpressions(); releaseExpressions();
});

/** A wide binding table: `_b0 = x * scale + offset`, `_bi = _b0 + (i +
 * shift)`. Two nodes per entry and no deep chain, so 66,000 entries cross
 * the default headroom without approaching the evaluator's recursion; a
 * `shift` gives every entry an expression no unshifted table shares. The
 * root reads the last entry and the third, so both are document text. */
function wide(size: number, scale = 2, offset = 0, shift = 0): Manifest {
  const first = offset === 0 ? `x * ${scale}` : `x * ${scale} + ${offset}`;
  return {
    format: 'machinome-export', version: 4,
    drivers: { x: { default: 2, range: null, unit: 'mm', dtype: null, scale: null } },
    bindings: Array.from({ length: size }, (_, i) => ({ name: `_b${i}`,
      expression: i === 0 ? first : `_b0 + ${i + shift}` })),
    root: { name: 'root', type: 'assembly', color: null,
      operations: [['t', [`_b${size - 1}`, '_b2', '0']]] },
  };
}

/** One outermost operation reading `name` through the table's roots. */
function read(table: BindingTable, name: string, x = 2): unknown {
  return withExpressions(() => evalExpr(name, {
    time: 0, drivers: { x }, bindings: table.roots(),
  }));
}

/** The table preparations `action` causes (the counter is page-wide). */
function preparing(action: () => void): number {
  const before = bindingPreparationMetrics();
  action();
  return bindingPreparationMetrics() - before;
}

/** A wide table refused by its last entry, which names itself. */
function refused(size: number, scale: number, offset = 0): Manifest {
  const document = wide(size, scale, offset);
  document.bindings!.push({ name: '_bad', expression: '_bad + 1' });
  return document;
}

/** One heap reading after a forced collection, only when the run exposes
 * the collector (`NODE_OPTIONS=--expose-gc`): evidence, never asserted. */
function heap(test: string, state: string): void {
  const collect = (globalThis as { gc?: () => void }).gc;
  if (collect === undefined) return;
  collect();
  console.info({ test, state, heapUsedMB: +(process.memoryUsage().heapUsed / 2 ** 20).toFixed(1),
    nodes: expressionMetrics().nodes });
}

const LARGE = 66_000;

describe('a loaded graph is reused across operations at the default headroom', () => {
  it('A: keeps one large document prepared across adjacent operations', async () => {
    const document = wide(LARGE);
    const { table } = assertRenderable(document, '/large.json');
    const generation = expressionGeneration();
    const loaded = expressionMetrics().nodes;
    console.info({ test: 'A', loaded, peakNodes: expressionMetrics().peakNodes });
    heap('A', 'loaded');
    expect(loaded).toBeGreaterThan(EXPRESSION_LIMITS.nodes);
    expect(bindingPreparationMetrics()).toBe(1);

    const tree = new WidgetTree(document.root, '/', null, table);
    await tree.loaded;
    expect(expressionGeneration()).toBe(generation);
    for (let operation = 0; operation < 3; operation += 1) {
      expect(read(table, `_b${LARGE - 1}`, operation)).toBe(2 * operation + LARGE - 1);
      expect(expressionGeneration()).toBe(generation);
      expect(bindingPreparationMetrics()).toBe(1);
    }
    tree.update({ time: 0, drivers: { x: 3 }, get bindings() { return table.roots(); } });
    expect(tree.group.matrix.elements[12]).toBe(6 + LARGE - 1);
    expect(tree.group.matrix.elements[13]).toBe(8);
    expect(expressionGeneration()).toBe(generation);
    expect(bindingPreparationMetrics()).toBe(1);
    console.info({ test: 'A', after: expressionMetrics().nodes,
      peakNodes: expressionMetrics().peakNodes });
    heap('A', 'after the operations');
    tree.dispose();
    retainExpressions(); releaseExpressions(); // the final disposal
    expect(expressionMetrics().nodes).toBe(0);
    heap('A', 'after final disposal');
  }, 120_000);

  it('B: operates a large and a small document alternately without reclaiming', () => {
    const largeDocument = wide(LARGE);
    const smallDocument = wide(3, 3, -1);
    let largePreparations = 0;
    let large!: BindingTable;
    largePreparations += preparing(() => {
      large = assertRenderable(largeDocument, '/large.json').table;
    });
    const { table: small } = assertRenderable(smallDocument, '/small.json');
    // One operation each: the small document's load may have emptied the
    // large graph once (its start, design Decision 1, point 1).
    largePreparations += preparing(() => {
      expect(read(large, '_b2')).toBe(6);
    });
    expect(read(small, '_b2')).toBe(7);
    const generation = expressionGeneration();
    console.info({ test: 'B', settled: expressionMetrics().nodes,
      peakNodes: expressionMetrics().peakNodes });
    for (let round = 0; round < 3; round += 1) {
      largePreparations += preparing(() => {
        expect(read(large, `_b${LARGE - 1}`, round)).toBe(2 * round + LARGE - 1);
      });
      expect(expressionGeneration()).toBe(generation);
      expect(read(small, '_b2', round)).toBe(3 * round + 1);
      expect(read(small, '_b1', round)).toBe(3 * round);
      expect(expressionGeneration()).toBe(generation);
    }
    expect(largePreparations).toBe(2);
    console.info({ test: 'B', after: expressionMetrics().nodes,
      peakNodes: expressionMetrics().peakNodes });
  }, 120_000);
});

describe('repeated operation adds no expression state', () => {
  it('C: a second pass of every corpus script, tick and pose prepares nothing new', async () => {
    const generation = expressionGeneration();
    let machines = 0;
    const clocked = JSON.parse(readFileSync(new URL('./clocked-corpus.json', import.meta.url), 'utf8'));
    for (const entry of clocked.machines) {
      const doc = entry.document as Manifest;
      const machine = clockedMachine(loadClocked(doc, entry.name, bindingTable(doc, entry.name)));
      const pass = () => {
        const saved = new Map<string, ClockedSnapshot>();
        for (const step of entry.script as { move?: { input: string; by?: number; to?: number };
          trigger?: string; snapshot?: string; restore?: string; reset?: boolean }[]) {
          try {
            if (step.move) {
              const { input, ...request } = step.move;
              machine.move(input, request);
            }
            if (step.trigger) machine.trigger(step.trigger);
            if (step.snapshot) saved.set(step.snapshot, machine.snapshot());
            if (step.restore) machine.restore(saved.get(step.restore)!);
            if (step.reset) machine.reset();
          } catch {
            // A refused request is an outcome, not a failure of this test.
          }
        }
        machine.reset();
      };
      pass();
      const first = expressionMetrics().nodes;
      pass();
      expect(expressionMetrics().nodes, `clocked ${entry.name}`).toBe(first);
      machines += 1;
    }

    for (const entry of (runningCorpus as unknown as { machines: { name: string; dt: number;
      steps: number; document: unknown; script: { tick: number; handle?: string;
        move?: { input: string; by?: number; to?: number; duration?: number };
        rate?: { input: string; rate: number }; trigger?: string; snapshot?: string;
        restore?: string }[] }[] }).machines) {
      const engine = Engine.load(entry.document as RunDocument, {
        dt: entry.dt, record: entry.steps + 1, sourceUrl: `running-corpus.json#${entry.name}`,
      });
      const start = engine.snapshot();
      const pass = () => {
        engine.restore(start);
        const saved = new Map<string, unknown>();
        for (let tick = 1; tick <= entry.steps; tick += 1) {
          for (const action of entry.script.filter(one => one.tick === tick)) {
            if (action.move !== undefined) {
              const { input, ...request } = action.move;
              engine.move(input, request);
            } else if (action.rate !== undefined) {
              engine.rate(action.rate.input, action.rate.rate);
            } else if (action.trigger !== undefined) {
              engine.trigger(action.trigger);
            } else if (action.snapshot !== undefined) {
              saved.set(action.snapshot, engine.snapshot());
            } else if (action.restore !== undefined) {
              engine.restore(saved.get(action.restore) as never);
            }
          }
          engine.advance(1);
        }
      };
      pass();
      const first = expressionMetrics().nodes;
      pass();
      expect(expressionMetrics().nodes, `running ${entry.name}`).toBe(first);
      machines += 1;
    }

    const document = wide(20);
    const { table } = assertRenderable(document, '/posed.json');
    const tree = new WidgetTree(document.root, '/', null, table);
    await tree.loaded;
    const pose = () => {
      for (const x of [2, 3, -1]) {
        tree.update({ time: 0, drivers: { x }, get bindings() { return table.roots(); } });
      }
    };
    pose();
    const first = expressionMetrics().nodes;
    pose();
    expect(expressionMetrics().nodes).toBe(first);
    expect(tree.group.matrix.elements[12]).toBe(-2 + 19);
    tree.dispose();
    console.info({ test: 'C', machines, nodes: expressionMetrics().nodes,
      peakNodes: expressionMetrics().peakNodes, generations: expressionGeneration() - generation });
  }, 120_000);
});

describe('reclamation where obsolete state is created', () => {
  it('D: bounds history by the loaded documents under the shipping policy', () => {
    const H = 5;
    EXPRESSION_LIMITS.nodes = H;
    EXPRESSION_LIMITS.everyOperation = false;
    // b and its replacements share no entry expression with a.
    const first = wide(20, 2);
    const second = wide(20, 3, 0, 1000);
    const replacement = (version: number) => wide(20, 3, version + 100, 1000);
    const bad = refused(20, 3, 7);
    // g: the high-water of loading each document alone into an emptied store.
    const alone = (document: Manifest): number => {
      retainExpressions(); releaseExpressions();
      resetExpressionMetrics();
      try { assertRenderable(document, '/alone.json'); } catch { /* the refused one */ }
      return expressionMetrics().peakNodes;
    };
    const g = Math.max(alone(first), alone(second), alone(bad),
      ...Array.from({ length: 60 }, (_, version) => alone(replacement(version))));
    retainExpressions(); releaseExpressions();
    resetExpressionMetrics();

    const a = assertRenderable(first, '/a.json');
    a.settlement.installed();
    let b = assertRenderable(second, '/b.json');
    b.settlement.installed();
    const operate = (expectedB: number) => {
      const generation = expressionGeneration();
      expect(read(a.table, '_b19')).toBe(4 + 19);
      expect(read(b.table, '_b19')).toBe(expectedB);
      expect(read(a.table, '_b2')).toBe(4 + 2);
      expect(expressionGeneration()).toBe(generation);
    };
    operate(6 + 19 + 1000);
    const before = expressionGeneration();
    for (let version = 0; version < 60; version += 1) {
      let generation = expressionGeneration();
      b = assertRenderable(replacement(version), '/replacement.json');
      expect(expressionGeneration()).toBeGreaterThan(generation);
      b.settlement.installed();
      operate(6 + version + 100 + 19 + 1000);
      generation = expressionGeneration();
      expect(() => assertRenderable(bad, '/bad.json')).toThrow(/names itself/);
      expect(expressionGeneration()).toBeGreaterThan(generation);
      operate(6 + version + 100 + 19 + 1000);
    }
    const peak = expressionMetrics().peakNodes;
    const bound = (H - 1) + 2 * g;
    console.info({ test: 'D', g, bound, peakNodes: peak, nodes: expressionMetrics().nodes,
      generations: expressionGeneration() - before });
    expect(peak).toBeLessThanOrEqual(bound);
  });

  it('E: reclaims a disposed viewer\'s graph while another stays mounted', () => {
    const H = 50;
    EXPRESSION_LIMITS.nodes = H;
    EXPRESSION_LIMITS.everyOperation = false;
    let holds = 0;
    const retain = () => { retainExpressions(); holds += 1; };
    const release = () => { releaseExpressions(); holds -= 1; };
    const large = (name: string) => withExpressions(() => {
      for (let i = 0; i < 30; i += 1) prepare(`${i} + ${name}`);
    });
    const survivor = '(7100001 + 1)';
    try {
      retain(); retain();
      large('disposed');
      withExpressions(() => prepare(survivor));
      const generation = expressionGeneration();
      const held = expressionMetrics().nodes;
      expect(held).toBeGreaterThanOrEqual(H);
      release();
      expect(withExpressions(() => valueOf(prepare(survivor), { time: 0 }))).toBe(7100002);
      console.info({ test: 'E', held, nodes: expressionMetrics().nodes,
        peakNodes: expressionMetrics().peakNodes });
      expect(expressionMetrics().nodes).toBeLessThan(H + 3);
      expect(expressionGeneration()).toBe(generation + 1);

      // Released inside an open scope: honoured when the scope ends.
      retain();
      large('disposedAgain');
      const inner = expressionGeneration();
      withExpressions(() => {
        release();
        expect(expressionGeneration()).toBe(inner);
        expect(valueOf(prepare(survivor), { time: 0 })).toBe(7100002);
      });
      expect(expressionGeneration()).toBe(inner + 1);
      expect(expressionMetrics().nodes).toBe(0);
    } finally {
      while (holds > 0) release();
    }
  });

  it('F: reclaims a refused load beside a small good document', () => {
    const H = 50;
    EXPRESSION_LIMITS.nodes = H;
    EXPRESSION_LIMITS.everyOperation = false;
    const good = assertRenderable(wide(3), '/good.json');
    good.settlement.installed();
    const graph = expressionMetrics().nodes;
    const generation = expressionGeneration();
    expect(() => assertRenderable(refused(60, 5), '/refused.json')).toThrow(/names itself/);
    const refusal = expressionMetrics().peakNodes;
    expect(read(good.table, '_b2')).toBe(6);
    console.info({ test: 'F', graph, peakNodes: refusal, nodes: expressionMetrics().nodes });
    expect(refusal).toBeGreaterThanOrEqual(H + graph);
    expect(expressionMetrics().nodes).toBeLessThan(H + graph);
    expect(expressionGeneration()).toBe(generation + 1);
  });

  it('G: reclaims a validated document abandoned after its validation', () => {
    const H = 50;
    EXPRESSION_LIMITS.nodes = H;
    EXPRESSION_LIMITS.everyOperation = false;
    const good = assertRenderable(wide(3), '/good.json');
    good.settlement.installed();
    const graph = expressionMetrics().nodes;
    const generation = expressionGeneration();
    const incoming = assertRenderable(wide(60, 5), '/incoming.json');
    const validated = expressionMetrics().nodes;
    expect(validated).toBeGreaterThanOrEqual(H + graph);
    incoming.settlement.abandoned();
    expect(read(good.table, '_b2')).toBe(6);
    console.info({ test: 'G', graph, validated, nodes: expressionMetrics().nodes,
      peakNodes: expressionMetrics().peakNodes });
    expect(expressionMetrics().nodes).toBeLessThan(H + graph);
    expect(expressionGeneration()).toBe(generation + 1);

    // The first call won: a later installation on the same handle does
    // nothing, even with the store above the headroom again.
    withExpressions(() => { for (let i = 0; i < 30; i += 1) prepare(`${i} + unrelated`); });
    expect(expressionMetrics().nodes).toBeGreaterThanOrEqual(H);
    const nodes = expressionMetrics().nodes;
    incoming.settlement.installed();
    expect(expressionGeneration()).toBe(generation + 1);
    expect(expressionMetrics().nodes).toBe(nodes);
  });

  it('H: reclaims at installation the standing graph rebuilt while the successor loaded', () => {
    const H = 50;
    EXPRESSION_LIMITS.nodes = H;
    EXPRESSION_LIMITS.everyOperation = false;
    const standing = assertRenderable(wide(60, 2), '/standing.json');
    standing.settlement.installed();
    expect(read(standing.table, '_b59')).toBe(4 + 59);
    const generation = expressionGeneration();
    const successor = assertRenderable(wide(60, 7, 3, 1000), '/successor.json');
    expect(expressionGeneration()).toBe(generation + 1); // its start
    const validated = expressionMetrics().nodes;
    // The standing model keeps operating while the successor's assets load.
    expect(read(standing.table, '_b59')).toBe(4 + 59);
    expect(expressionGeneration()).toBe(generation + 1);
    const window = expressionMetrics().nodes;
    expect(window - validated).toBeGreaterThanOrEqual(H);
    successor.settlement.installed();
    expect(expressionGeneration()).toBe(generation + 2);
    expect(read(successor.table, '_b59')).toBe(17 + 1059);
    console.info({ test: 'H', validated, window, nodes: expressionMetrics().nodes,
      peakNodes: expressionMetrics().peakNodes });
  });

  it('I: keeps an installed large document\'s graph for its first operations', () => {
    const H = 50;
    EXPRESSION_LIMITS.nodes = H;
    EXPRESSION_LIMITS.everyOperation = false;
    const standing = assertRenderable(wide(60, 2), '/standing.json');
    standing.settlement.installed();
    expect(read(standing.table, '_b59')).toBe(4 + 59);
    const generation = expressionGeneration();
    const successor = assertRenderable(wide(60, 7, 3, 1000), '/successor.json');
    expect(expressionGeneration()).toBe(generation + 1); // its start
    expect(expressionMetrics().nodes).toBeGreaterThanOrEqual(H);
    successor.settlement.installed();
    let preparations = 0;
    for (let operation = 0; operation < 3; operation += 1) {
      preparations += preparing(() => {
        expect(read(successor.table, '_b59', operation)).toBe(7 * operation + 3 + 1059);
      });
      expect(expressionGeneration()).toBe(generation + 1);
    }
    expect(preparations).toBe(0);
  });
});
