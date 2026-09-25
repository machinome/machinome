/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { bindingTable } from './bindings';
import {
  EXPRESSION_LIMITS, expressionGeneration, expressionMetrics, prepare,
  releaseExpressions, retainExpressions, valueOf, withExpressions,
} from './expressions';
import { evaluateExpression, kinkLevel, loadProgram } from './run/program';
import { evalExpr } from './evaluator';
import { poseScope } from './run/pose';
import { LevelPaths } from './run/jumps';
import type { ProgramJump, ProgramPlan } from './run/program';
import type { RunDocument } from './run/program';
import type { Manifest } from './types';
import { Run } from './run/run';
import { loadClocked } from './clocked/document';
import { clockedMachine } from './clocked/machine';
import type { ClockedSnapshot } from './clocked/machine';
import { WidgetTree } from './tree';

const limit = EXPRESSION_LIMITS.nodes;
beforeEach(() => { retainExpressions(); releaseExpressions(); });
afterEach(() => {
  EXPRESSION_LIMITS.nodes = limit;
  retainExpressions(); releaseExpressions();
});

function document(): RunDocument {
  return {
    format: 'machinome-export', version: 5,
    drivers: { crank: { default: 0, range: null, unit: 'deg', dtype: null, scale: null } },
    bindings: [
      { name: '_b0', expression: 'crank - 3' },
      { name: '_b1', expression: 'max(0, _b0)' },
      ...Array.from({ length: 12 }, (_, i) => ({ name: `_pad${i}`, expression: `${i + 10} + crank` })),
    ],
    program: {
      identity: 'lifetime-fixture', clock: 'time',
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        wheel: { kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational' },
      },
      intermediates: [],
      edges: [{ kind: 'law', needs: ['crank'], gives: ['wheel'],
        description: 'crank drives wheel', stated_by: 'CacheBench',
        expressions: ['_b1'], affine: [false], plans: [null] }],
      spans: {}, sources: { crank: ['crank'], wheel: ['crank'] },
      limits: { crossing_tolerance: 1e-12, subdivisions: 64,
        bisection_rounds: 64, max_crossings: 1000, agreement: 1e-9 },
    },
  } as RunDocument;
}

describe('expression lifetime under cache pressure', () => {
  it('retains a current large graph across adjacent operations within finite capacity', () => {
    const before = expressionGeneration();
    withExpressions(() => {
      prepare('source + 1');
      let serial = 10;
      while (expressionMetrics().nodes < 102_700) {
        prepare(`${serial} + source`);
        serial += 1;
      }
    });
    expect(expressionMetrics().nodes).toBeGreaterThanOrEqual(102_700);
    expect(expressionMetrics().nodes).toBeLessThan(125_000);
    for (let tick = 0; tick < 3; tick += 1) {
      const result = withExpressions(() => valueOf(prepare('source + 1'), {
        time: 0, drivers: { source: 2 },
      }));
      expect(result).toBe(3);
      expect(expressionGeneration()).toBe(before);
    }
  }, 30_000);

  it('reconciles document-local binding changes and poses the new tree under pressure', async () => {
    EXPRESSION_LIMITS.nodes = 5;
    const a = document() as Manifest;
    const b = document() as Manifest;
    b.bindings![0].expression = '$t - 2';
    const root: Manifest['root'] = { name: 'root', type: 'assembly', color: null,
      operations: [['t', ['_b1', '0', '0']]] };
    const tableA = bindingTable(a, '/a.json'), tableB = bindingTable(b, '/b.json');
    const tree = new WidgetTree(root, '/', null, tableA);
    await tree.loaded;
    tree.update(poseScope({ crank: 7 }, 'time', 0, tableA));
    expect(tree.group.matrix.elements[12]).toBe(4);
    await tree.reconcile(root, '/', null, tableB);
    tree.update({ time: 5, get bindings() { return tableB.roots(); } },
      { time: true, drivers: new Set() });
    expect(tree.group.matrix.elements[12]).toBe(3);
    tree.dispose();
  });

  it('defers reclamation in nested scopes and releases scopes after exceptions', () => {
    EXPRESSION_LIMITS.nodes = 1;
    withExpressions(() => {
      const first = prepare('2 + 3');
      const generation = expressionGeneration();
      withExpressions(() => prepare('200 + 300'));
      expect(expressionGeneration()).toBe(generation);
      expect(valueOf(first, { time: 0 })).toBe(5);
    });
    const generation = expressionGeneration();
    expect(() => withExpressions(() => {
      prepare('20 + 30');
      throw Error('refused replacement');
    })).toThrow('refused replacement');
    expect(expressionGeneration()).toBe(generation + 1);
    withExpressions(() => prepare('40 + 50'));
    expect(expressionGeneration()).toBe(generation + 2);
    retainExpressions();
    withExpressions(() => {
      const root = prepare('60 + 70');
      releaseExpressions();
      expect(valueOf(root, { time: 0 })).toBe(130);
    });
    expect(expressionMetrics().nodes).toBe(0);
  });

  it('keeps live documents separate and bounds successful/failed replacement history', () => {
    EXPRESSION_LIMITS.nodes = 5;
    const a = loadProgram(document(), '/a.json');
    const other = document();
    other.bindings![0].expression = 'crank - 2';
    const b = loadProgram(other, '/b.json');
    let high = 0;
    for (let version = 0; version < 60; version += 1) {
      const next = document();
      next.bindings![0].expression = `crank - ${version + 100}`;
      loadProgram(next, '/replacement.json');
      const bad = document();
      bad.bindings!.push({ name: '_bad', expression: '_bad + 1' });
      expect(() => loadProgram(bad, '/bad.json')).toThrow(/names itself/);
      expect(evaluateExpression(a, '_b1', { crank: 7 })).toBe(4);
      expect(evaluateExpression(b, '_b1', { crank: 7 })).toBe(5);
      high = Math.max(high, expressionMetrics().nodes);
    }
    expect(high).toBeLessThanOrEqual(50);
    console.info(`60 replacements plus refusals: at most ${high} retained nodes (threshold 5)`);
    retainExpressions(); releaseExpressions();
    expect(expressionMetrics().nodes).toBe(0);
  });

  it('keeps a running bank stable while traversing a kink across generations', () => {
    const execute = (threshold: number) => {
      EXPRESSION_LIMITS.nodes = threshold;
      const run = new Run(loadProgram(document(), '/running.json'), 0.1);
      run.move('crank', { to: 8, duration: 1 });
      for (let tick = 0; tick < 12; tick += 1) {
        prepare(`${tick + 1000} + unrelated`);
        run.advance();
      }
      expect(run.state()).toEqual({ crank: 8, wheel: 5 });
      return run.snapshot();
    };
    expect(execute(5)).toEqual(execute(limit));
  });

  it('replays all clocked corpus operations unchanged under pressure', () => {
    const corpus = JSON.parse(readFileSync(new URL('./clocked-corpus.json', import.meta.url), 'utf8'));
    const execute = (entry: typeof corpus.machines[number], threshold: number) => {
      EXPRESSION_LIMITS.nodes = threshold;
      const doc = entry.document as Manifest;
      const machine = clockedMachine(loadClocked(doc, entry.name, bindingTable(doc, entry.name)));
      const saved = new Map<string, ClockedSnapshot>();
      return entry.script.map((step: { move?: { input: string; by?: number; to?: number };
        trigger?: string; snapshot?: string; restore?: string; reset?: boolean }) => {
        prepare('98765 + unrelated');
        let outcome: unknown;
        try {
          if (step.move) {
            const { input, ...request } = step.move;
            outcome = machine.move(input, request);
          }
          if (step.trigger) outcome = machine.trigger(step.trigger);
          if (step.snapshot) saved.set(step.snapshot, machine.snapshot());
          if (step.restore) machine.restore(saved.get(step.restore)!);
          if (step.reset) machine.reset();
        } catch (error) {
          outcome = { message: (error as Error).message, kind: (error as { kind?: string }).kind };
        }
        return { outcome, bank: machine.state() };
      });
    };
    for (const entry of corpus.machines) {
      expect(execute(entry, 5), entry.name).toEqual(execute(entry, limit));
    }
  });

  it('reconstructs a pose scope acquired before reclamation', () => {
    const table = bindingTable(document() as Manifest, '/pose.json');
    const scope = poseScope({ crank: 7 }, 'time', 0, table);
    EXPRESSION_LIMITS.nodes = 1;
    prepare('400 + 500');
    expect(evalExpr('_b1', scope)).toBe(4);
  });

  it('reconstructs a held path with its original standing values', () => {
    const program = loadProgram(document(), '/path.json');
    const jump: ProgramJump = { name: 'j0', primitive: 'floor',
      level: '_b0 + fixed', affine: true, shape: 'affine', kinks: null };
    const plan: ProgramPlan = { skeleton: 'j0', jumps: [jump], shape: 'constant', kinks: null };
    const paths = new LevelPaths(program, new Set(['crank']));
    const piece = paths.newPiece();
    expect(paths.value(plan, jump, piece, { crank: 1, fixed: 20 }, 'path', 'wheel')).toBe(18);
    EXPRESSION_LIMITS.nodes = 1;
    prepare('[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]');
    expect(paths.value(plan, jump, piece, { crank: 7, fixed: 999 }, 'path', 'wheel')).toBe(24);
  });

  it('prepares a multi-entry binding map larger than the threshold coherently', () => {
    EXPRESSION_LIMITS.nodes = 5;
    const table = bindingTable(document() as Manifest, '/pressure.json');
    const roots = table.roots()!;
    const scope = { time: 0, drivers: { crank: 1 }, bindings: roots };
    expect(valueOf(roots.get('_pad0')!, scope)).toBe(11);
    expect(valueOf(roots.get('_pad11')!, scope)).toBe(22);
    expect(valueOf(roots.get('_b1')!, scope)).toBe(0);
    expect(expressionMetrics().nodes).toBeGreaterThan(EXPRESSION_LIMITS.nodes);
  });

  it('classifies root plus bindings above the threshold, cold or warm', () => {
    EXPRESSION_LIMITS.nodes = 5;
    for (let warm = 0; warm < 3; warm += 1) {
      prepare(`${900 + warm} + unrelated`);
      const program = loadProgram(document(), '/pressure.json');
      expect(program.edges[0].shapes).toEqual(['kinked']);
      expect(evaluateExpression(program, '_b1', { crank: 7 })).toBe(4);
    }
  });

  it('reconstructs retained kink operands when old IDs name DIFFERENT nodes', () => {
    const program = loadProgram(document(), '/pressure.json');
    const kink = program.edges[0].kinks[0]![0];
    expect(kinkLevel(program, kink, { crank: 1 })).toBe(2);
    const old = kink.a;
    const generation = expressionGeneration();
    EXPRESSION_LIMITS.nodes = 1;
    prepare('[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]');
    expect(expressionGeneration()).toBeGreaterThan(generation);
    expect(valueOf(old, { time: 0 })).not.toBe(0);
    expect(kinkLevel(program, kink, { crank: 1 })).toBe(2);
    expect(evaluateExpression(program, '_b1', { crank: 7 })).toBe(4);
  });
});
