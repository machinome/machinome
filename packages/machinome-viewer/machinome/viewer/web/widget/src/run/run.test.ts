/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The tick (`simulation/run.py`'s `class Run`, reproduced): admissions,
// one propagation over the edges in program order, stops located inside
// the tick with the group of inputs that push them, segments, and the
// atomicity that makes a refused tick commit nothing at all.

import { describe, expect, it, vi } from 'vitest';
import { movingConstraintReads, Run } from './run';
import type { StopRecord } from './run';
import {
  LandingInvariantError, loadProgram, refusalKind, StopInvariantError,
} from './program';
import type { LoadedProgram, RunDocument } from './program';
import { nextAfter } from './jumps';
import { Motion, propagations } from './motion';
import corpus from '../running-corpus.json';
import wrappedV12 from './follow-wrapped-v12.json';
import wrappedCommandsV12 from './follow-wrapped-commands-v12.json';
import producerLawV11 from '../../../../tests/fixtures/nonfinite-running-law-v11.json';
import {
  ExpressionPath, expressionGeneration, expressionMetrics,
  releaseExpressions, retainExpressions, UnsupportedPathNode,
} from '../expressions';

/** The next representable float below `value`. */
const nextDown = (value: number): number => nextAfter(value, -Infinity);

const LIMITS = {
  crossing_tolerance: 1e-12, subdivisions: 64, bisection_rounds: 64,
  max_crossings: 1000, agreement: 1e-9,
};

const input = (initial: number) => ({ kind: 'input', initial, domain: null });
const coordinate = (initial: number) =>
  ({ kind: 'coordinate', initial, unit: null, domain: null });

function bench(spec: {
  coordinates: Record<string, unknown>;
  edges: unknown[];
  spans?: Record<string, unknown>;
  intermediates?: string[];
  sources?: Record<string, string[]>;
  instructions?: Record<string, unknown>;
  version?: number;
  bindings?: { name: string; expression: string }[];
}): LoadedProgram {
  const ids = Object.keys(spec.coordinates);
  const inputs = ids.filter(
    (id) => (spec.coordinates[id] as { kind: string }).kind === 'input');
  return loadProgram({
    format: 'machinome-export',
    version: spec.version ?? 5,
    bindings: spec.bindings,
    drivers: Object.fromEntries(inputs.map((id) => [id, {
      default: 0, range: null, unit: null, dtype: null, scale: null,
    }])),
    instructions: spec.instructions ?? {},
    program: {
      identity: 'bench', clock: 'time',
      coordinates: spec.coordinates,
      intermediates: spec.intermediates ?? [],
      edges: spec.edges,
      spans: spec.spans ?? {},
      sources: spec.sources ?? Object.fromEntries(
        [...ids, ...(spec.intermediates ?? [])].map(
          (id) => [id, inputs.includes(id) ? [id] : inputs])),
      limits: { ...LIMITS },
    },
  } as unknown as RunDocument, 'bench://run');
}

const law = (needs: string[], gives: string[], expression: string,
             description: string, affine = true) => ({
  kind: 'law', needs, gives, description, stated_by: 'Bench',
  expressions: [expression], affine: [affine], plans: [null],
});

const play = (source: string, retained: string, low: number, high: number) => ({
  kind: 'play', needs: [source, retained], gives: [retained],
  description: `${source} plays ${retained}`, stated_by: 'Bench', low, high,
});

const follow = (lower = 'low', upper = 'high', lowerPlan: unknown = null) => ({
  kind: 'follow', needs: ['low', 'high', 'ball'], gives: ['ball'],
  description: 'two surfaces follow ball', stated_by: 'Bench',
  lower, upper, lower_plan: lowerPlan, upper_plan: null,
});

describe('non-finite running law refusal', () => {
  const sqrtBench = (feed: number, slide: number) => bench({
    coordinates: { feed: input(feed), slide: coordinate(slide) },
    edges: [law(['feed'], ['slide'], 'sqrt(0.1 - feed)',
      'square-root carriage', false)],
  });

  it('loads the producer-exported v11 document and refuses its domain-invalid move', () => {
    // Captured from framework 34b3de127165ec7c2ff9429e24fc01ab39416e5f:
    // document(bound(SquareRootMachine())) in tests/test_running_nonfinite_law.py.
    const program = loadProgram(producerLawV11 as RunDocument,
      'producer://nonfinite-running-law-v11.json');
    const run = new Run(program, 0.1, 8);
    const before = run.snapshot();
    let error: unknown;
    try { run.move('feed', { to: 0.2 }); } catch (caught) { error = caught; }
    expect(refusalKind(error)).toBe('law');
    expect(String(error)).toContain('SquareRootMachine');
    expect(String(error)).toContain('shaft.turn');
    expect(run.snapshot()).toEqual(before);
    expect(run.commands()).toEqual([]);
    expect(run.trajectory()).toEqual([]);

    const finite = new Run(loadProgram(producerLawV11 as RunDocument,
      'producer://nonfinite-running-law-v11.json'), 0.1, 8);
    expect(finite.move('feed', { to: 0.1 }).status).toBe('completed');
    expect(finite.state()).toEqual({ feed: 0.1, 'shaft.turn': 0 });
  });

  it('refuses an immediate valid-start request whose law endpoint is NaN', () => {
    const run = new Run(sqrtBench(0, Math.sqrt(0.1)), 1, 8);
    const before = run.snapshot();
    let error: unknown;
    try { run.move('feed', { to: 0.2 }); } catch (caught) { error = caught; }
    expect(refusalKind(error)).toBe('law');
    expect(String(error)).toContain('square-root carriage');
    expect(String(error)).toContain('Bench');
    expect(String(error)).toContain('slide');
    expect(run.snapshot()).toEqual(before);
    expect(run.state()).toEqual({ feed: 0, slide: Math.sqrt(0.1) });
    expect(run.tick()).toBe(0);
    expect(run.commands()).toEqual([]);
    expect(run.trajectory()).toEqual([]);
    expect(run.crossings()).toEqual([]);
    expect(run.stops()).toEqual([]);
  });

  it('refuses an accepted non-finite authored start before a finite endpoint', () => {
    const run = new Run(sqrtBench(0.2, 0), 1, 8);
    const before = run.snapshot();
    let error: unknown;
    try { run.move('feed', { to: 0.1 }); } catch (caught) { error = caught; }
    expect(refusalKind(error)).toBe('law');
    expect(run.snapshot()).toEqual(before);
    expect(run.state()).toEqual({ feed: 0.2, slide: 0 });
    expect(run.commands()).toEqual([]);
    expect(run.trajectory()).toEqual([]);
  });

  it.each([1, -1])('refuses an evaluated %i infinity', sign => {
    const expression = sign === 1 ? '1 / (feed - 0.1)' : '-1 / (feed - 0.1)';
    const run = new Run(bench({
      coordinates: { feed: input(0), slide: coordinate(-10 * sign) },
      edges: [law(['feed'], ['slide'], expression, 'reciprocal carriage', false)],
    }), 1, 8);
    const before = run.snapshot();
    let error: unknown;
    try { run.move('feed', { to: 0.1 }); } catch (caught) { error = caught; }
    expect(refusalKind(error)).toBe('law');
    expect(String(error)).toContain('reciprocal carriage');
    expect(run.snapshot()).toEqual(before);
    expect(run.commands()).toEqual([]);
  });

  it('retains the first successful tick and admitted travel when the second fails', () => {
    const run = new Run(sqrtBench(0, Math.sqrt(0.1)), 0.1, 8);
    const command = run.move('feed', { to: 0.2, duration: 0.2 });
    run.advance();
    const before = run.snapshot();
    expect(before.tick).toBe(1);
    expect(before.bank.feed).toBe(0.1);
    expect(command.admitted).toBe(0.1);
    let error: unknown;
    try { run.advance(); } catch (caught) { error = caught; }
    expect(refusalKind(error)).toBe('law');
    expect(command.status).toBe('refused');
    expect(command.admitted).toBe(0.1);
    expect(run.tick()).toBe(1);
    expect(run.state()).toEqual({ feed: 0.1, slide: 0 });
    expect(run.trajectory()).toEqual([{ tick: 1, bank: { feed: 0.1, slide: 0 } }]);
    expect(run.crossings()).toEqual([]);
    expect(run.stops()).toEqual([]);
  });

  it('refuses a law result at an existing interior bound-path sample', () => {
    const expression = 'sqrt(((feed - 0.1) * (feed - 0.1)) - 0.0025)';
    const run = new Run(bench({
      coordinates: { feed: input(0), slide: coordinate(Math.sqrt(0.0075)) },
      edges: [law(['feed'], ['slide'], expression, 'arched carriage', false)],
      spans: { feed: { low: null, high: { expression: '(slide + 1)' } } },
    }), 1, 8);
    const before = run.snapshot();
    let error: unknown;
    try { run.move('feed', { to: 0.3 }); } catch (caught) { error = caught; }
    expect(refusalKind(error)).toBe('law');
    expect(String(error)).toContain('arched carriage');
    expect(run.snapshot()).toEqual(before);
  });

  it('admits the finite square-root boundary from a representable exact landing', () => {
    const run = new Run(sqrtBench(0, Math.sqrt(0.1)), 1, 8);
    const command = run.move('feed', { to: 0.1 });
    expect(command.status).toBe('completed');
    expect(command.admitted).toBe(0.1);
    expect(run.state()).toEqual({ feed: 0.1, slide: 0 });
  });

  it('admits the finite square-root boundary after endpoint integration', () => {
    const run = new Run(sqrtBench(-0.2, Math.sqrt(0.1 - (-0.2))), 1, 8);
    const command = run.move('feed', { to: 0.1 });
    expect(command.status).toBe('completed');
    expect(command.admitted).toBeCloseTo(0.3, 12);
    expect(run.state()).toEqual({ feed: 0.1, slide: 0 });
  });

  it('refuses an exact terminal target just outside the law domain', () => {
    const start = -0.234;
    const target = 0.10000000000000002;
    expect(start + (target - start)).toBe(0.1);
    const run = new Run(sqrtBench(start, Math.sqrt(0.1 - start)), 1, 8);
    const before = run.snapshot();
    let error: unknown;
    try { run.move('feed', { to: target }); } catch (caught) { error = caught; }
    expect(refusalKind(error)).toBe('law');
    expect(run.snapshot()).toEqual(before);
    expect(run.commands()).toEqual([]);
  });
});

function followBench(low = 0, high = 3, expression = 'low',
                     plan: unknown = null, bindings: { name: string; expression: string }[] = []): LoadedProgram {
  return bench({ version: 12, bindings,
    coordinates: { low: input(low), high: input(high), ball: coordinate(0) },
    edges: [follow(expression, 'high', plan)],
    spans: { ball: { low: { expression }, high: { expression: 'high' } } },
  });
}

describe('version-12 two-envelope Follow', () => {
  it('shares successful same-fraction prefix work across paired Bounds, not their levels', () => {
    const run = new Run(followBench(), 1, null);
    const probe = run as unknown as {
      constraintLevel: (...args: unknown[]) => number;
      deltasOf: (...args: unknown[]) => Record<string, number>;
    };
    const levels = vi.spyOn(probe, 'constraintLevel');
    const derivations = vi.spyOn(probe, 'deltasOf');
    run.move('low', { to: 2, duration: 1 });
    run.advance();
    expect(run.state()).toEqual({ low: 2, high: 3, ball: 2 });
    expect(levels.mock.calls.length).toBeGreaterThan(100);
    // One initial stretch derivation is outside constraintLevel. The old
    // executor derives each duplicated Follow prefix afresh.
    expect(derivations.mock.calls.length).toBeLessThan(levels.mock.calls.length);
  });

  it('does not reuse a Follow prefix containing a constant-shaped random call', () => {
    const program = bench({ version: 12,
      coordinates: { low: input(0), high: input(3), source: coordinate(0), ball: coordinate(0) },
      edges: [law(['low'], ['source'], '(low + random(1))', 'random source'),
        { kind: 'follow', needs: ['source', 'high', 'ball'], gives: ['ball'],
          description: 'random source follower', stated_by: 'Bench',
          lower: 'source', upper: 'high', lower_plan: null, upper_plan: null }],
      spans: { ball: { low: { expression: 'source' }, high: { expression: 'high' } } },
    });
    const run = new Run(program, 1, null);
    const probe = run as unknown as {
      constraintLevel: (...args: unknown[]) => number;
      deltasOf: (...args: unknown[]) => Record<string, number>;
    };
    const levels = vi.spyOn(probe, 'constraintLevel');
    const derivations = vi.spyOn(probe, 'deltasOf');
    run.move('low', { to: 1, duration: 1 });
    run.advance();
    expect(levels.mock.calls.length).toBeGreaterThan(100);
    expect(derivations.mock.calls.length).toBeGreaterThanOrEqual(levels.mock.calls.length);
  });

  it('keeps distinct Follow prefixes separate and starts fresh after restore', () => {
    const other = { kind: 'follow', needs: ['low2', 'high2', 'ball2'], gives: ['ball2'],
      description: 'other two surfaces', stated_by: 'Bench',
      lower: 'low2', upper: 'high2', lower_plan: null, upper_plan: null };
    const program = bench({ version: 12,
      coordinates: { low: input(0), high: input(3), ball: coordinate(0),
        low2: input(0), high2: input(3), ball2: coordinate(0) },
      edges: [follow(), other],
      spans: {
        ball: { low: { expression: 'low' }, high: { expression: 'high' } },
        ball2: { low: { expression: 'low2' }, high: { expression: 'high2' } },
      },
    });
    const run = new Run(program, 1, null);
    const before = run.snapshot();
    const probe = run as unknown as {
      constraintLevel: (...args: unknown[]) => number;
      deltasOf: (...args: unknown[]) => Record<string, number>;
    };
    const levels = vi.spyOn(probe, 'constraintLevel');
    const derivations = vi.spyOn(probe, 'deltasOf');
    const issue = () => {
      run.move('low', { to: 2, duration: 1 });
      run.move('low2', { to: 2, duration: 1 });
      run.advance();
    };
    issue();
    const first = run.snapshot();
    // Each pair shares its own prefix, but the two different edge
    // sequences cannot share one propagated result at the same fraction.
    expect(levels.mock.calls.length).toBeGreaterThan(250);
    expect(derivations.mock.calls.length).toBeGreaterThan(120);
    expect(derivations.mock.calls.length).toBeLessThan(levels.mock.calls.length);
    const firstDerivations = derivations.mock.calls.length;
    run.restore(before);
    issue();
    expect(run.snapshot()).toEqual(first);
    expect(derivations.mock.calls.length).toBe(firstDerivations * 2);
  });

  it('does not publish a failed prefix or commit its partial tick', () => {
    const run = new Run(followBench(), 1, null);
    const probe = run as unknown as { deltasOf: (...args: unknown[]) => Record<string, number> };
    const original = probe.deltasOf.bind(run);
    let calls = 0;
    const injected = vi.spyOn(probe, 'deltasOf').mockImplementation((...args) => {
      calls += 1;
      if (calls === 3) throw new Error('injected prefix failure');
      return original(...args);
    });
    run.move('low', { to: 2, duration: 1 });
    const before = run.snapshot();
    expect(() => run.advance()).toThrow('injected prefix failure');
    expect(run.snapshot()).toEqual(before);
    injected.mockRestore();
    run.restore(before);
    run.advance();
    expect(run.state()).toEqual({ low: 2, high: 3, ball: 2 });
  });

  it('matches the frozen producer command corpus in order, status and full bank', () => {
    const program = loadProgram(wrappedV12 as unknown as RunDocument, 'producer://follow_wrapped_v12.json');
    const run = new Run(program, wrappedCommandsV12.dt, null);
    expect(run.state()).toEqual(wrappedCommandsV12.initial);
    for (const step of wrappedCommandsV12.steps) {
      const command = run.move(step.move.input, { to: step.move.to });
      expect(command.status).toBe(step.status);
      expect(run.state()).toEqual(step.bank);
    }
  });

  it('executes the exact producer-serialized v12 wrapped fragment', () => {
    const program = loadProgram(wrappedV12 as unknown as RunDocument, 'producer://follow_wrapped_v12.json');
    const run = new Run(program, 1, null);
    run.move('low', { to: 3, duration: 1 });
    run.advance();
    expect(run.state()['ball.slide']).toBe(2);
  });

  it('pushes, retains on retreat, and accepts an inward upper push', () => {
    const run = new Run(followBench(), 1, null);
    run.move('low', { to: 2, duration: 1 });
    run.advance();
    expect(run.state().ball).toBe(2);
    run.move('low', { to: 0, duration: 1 });
    run.advance();
    expect(run.state().ball).toBe(2);
    run.move('high', { to: 1, duration: 1 });
    run.advance();
    expect(run.state().ball).toBe(1);
  });

  it('carries an absolute terminal input to a retained Follow without curving its source', () => {
    const run = new Run(followBench(0, 10), 1, 8);
    expect(run.move('low', { to: -4.9425 }).status).toBe('completed');
    expect(run.state().ball).toBe(0);
    expect(run.move('low', { to: 3.9075 }).status).toBe('completed');
    expect(run.state().low).toBe(3.9075);
    expect(run.state().ball).toBe(3.9075);
  });

  it('retains the producer modulo left-closure excursion', () => {
    const program = followBench(0, 3, '_b3', {
      skeleton: '(low - (2 * _j0))',
      jumps: [{ name: '_j0', primitive: 'floor', level: '_b0', affine: true }],
    }, [
      { name: '_b0', expression: '(low / 2)' },
      { name: '_b1', expression: 'floor(_b0)' },
      { name: '_b2', expression: '(2 * _b1)' },
      { name: '_b3', expression: '(low - _b2)' },
    ]);
    const run = new Run(program, 1, null);
    run.move('low', { to: 3, duration: 1 });
    run.advance();
    expect(run.state().low).toBe(3);
    expect(run.state().ball).toBe(2);
  });

  it('stops opposing surfaces at their first compatible contact and replays', () => {
    const run = new Run(followBench(), 1, null);
    const before = run.snapshot();
    const firstLow = run.move('low', { to: 2, duration: 1 });
    const firstHigh = run.move('high', { to: 1, duration: 1 });
    run.advance();
    expect([firstLow.status, firstHigh.status]).toEqual(['blocked', 'blocked']);
    const stopped = run.snapshot();
    expect(run.state().low).toBeCloseTo(1.5, 9);
    expect(run.state().high).toBeCloseTo(1.5, 9);
    expect(run.state().ball).toBeCloseTo(1.5, 9);
    run.restore(before);
    run.move('low', { to: 2, duration: 1 });
    run.move('high', { to: 1, duration: 1 });
    run.advance();
    expect(run.snapshot()).toEqual(stopped);
  });

  it('preserves a retained positive zero at opposite-zero boundary ties', () => {
    const program = bench({ version: 12,
      coordinates: { low: input(-0), high: input(0), spare: input(0), ball: coordinate(0) },
      edges: [follow()],
      spans: { ball: { low: { expression: 'low' }, high: { expression: 'high' } } },
    });
    const run = new Run(program, 1, null);
    run.move('spare', { to: 1, duration: 1 });
    run.advance();
    expect(Object.is(run.state().ball, 0)).toBe(true);
  });

  it('finds periodic contact even when every old uniform probe is at home', () => {
    const program = followBench(0, 1.5, '_b3', {
      skeleton: '(low - (2 * _j0))',
      jumps: [{ name: '_j0', primitive: 'floor', level: '_b0', affine: true }],
    }, [
      { name: '_b0', expression: '(low / 2)' },
      { name: '_b1', expression: 'floor(_b0)' },
      { name: '_b2', expression: '(2 * _b1)' },
      { name: '_b3', expression: '(low - _b2)' },
    ]);
    const run = new Run(program, 1, null);
    const command = run.move('low', { to: 128, duration: 1 });
    run.advance();
    expect(command.status).toBe('blocked');
    expect(run.state().low).toBeGreaterThan(1.4);
    expect(run.state().low).toBeLessThan(1.6);
    expect(run.state().ball).toBeLessThanOrEqual(run.state().high);
  });

  it('finds a narrow incompatible interval between uniform probes', () => {
    const pulse = 'max(0, (1 - (abs((low - 0.133)) / 0.002)))';
    const run = new Run(followBench(0, 0.5, pulse), 1, null);
    run.move('low', { to: 1, duration: 1 });
    run.advance();
    expect(run.state().low).toBeGreaterThan(0.131);
    expect(run.state().low).toBeLessThan(0.133);
    expect(run.state().ball).toBeLessThanOrEqual(0.5);
  });

  it('refuses a curved envelope without committing any bank state', () => {
    const run = new Run(followBench(0, 3, 'sin(low)'), 1, null);
    const before = run.snapshot();
    run.move('low', { to: 1, duration: 1 });
    expect(() => run.advance()).toThrow(/piecewise affine/);
    expect(run.snapshot()).toEqual(before);
  });

  it('refuses positive one-sided contact without a representable positive neighbor', () => {
    const expression = '(((2 * low) + 2.220446049250313e-16) * (low > 0) * (low < 0.5))';
    const plan = { skeleton: '(((2 * low) + 2.220446049250313e-16) * _j0 * _j1)',
      jumps: [
        { name: '_j0', primitive: '>', level: 'low', affine: true },
        { name: '_j1', primitive: '<', level: '(low - 0.5)', affine: true },
      ] };
    const run = new Run(followBench(0, 1, expression, plan), 1, null);
    const before = run.snapshot();
    run.move('low', { to: 1, duration: 1 });
    let first = '';
    try { run.advance(); } catch (error) { first = String(error); }
    expect(first).toMatch(/positive one-sided/);
    expect(run.snapshot()).toEqual(before);
    run.restore(before);
    run.move('low', { to: 1, duration: 1 });
    let replay = '';
    try { run.advance(); } catch (error) { replay = String(error); }
    expect(replay).toBe(first);
    expect(run.snapshot()).toEqual(before);
  });
});

describe('one pass over the edges in program order', () => {
  it('runs a three-stage play chain and releases it on reversal', () => {
    const program = bench({
      coordinates: {
        crank: input(0), a: coordinate(0), b: coordinate(0), c: coordinate(0),
      },
      edges: [play('crank', 'a', -10, 10), play('a', 'b', -10, 10),
              play('b', 'c', -10, 10)],
    });
    const run = new Run(program, 1, null);
    run.move('crank', { by: 100, duration: 1 });
    run.advance();
    expect(run.state()).toEqual({ crank: 100, a: 90, b: 80, c: 70 });
    run.move('crank', { by: -5, duration: 1 });
    run.advance();
    expect(run.state()).toEqual({ crank: 95, a: 90, b: 80, c: 70 });
  });

  it('hands absolute landings through a large-offset play chain', () => {
    const initial = 1e16;
    const program = bench({
      coordinates: {
        x: input(initial), a: coordinate(initial), b: coordinate(initial),
        c: coordinate(initial),
      },
      edges: [play('x', 'a', -329, 3), play('a', 'b', -329, 3),
              play('b', 'c', -329, 3)],
    });
    const run = new Run(program, 1, null);
    run.move('x', { to: 0, duration: 1 });
    run.advance();
    expect(run.state()).toEqual({ x: 0, a: 329, b: 658, c: 987 });
  });

  it('propagates increments along a chain', () => {
    const program = bench({
      coordinates: {
        crank: input(0), 'first.turn': coordinate(0),
        'second.turn': coordinate(0),
      },
      edges: [
        law(['crank'], ['first.turn'], '(2 * crank)', 'crank drives first'),
        law(['first.turn'], ['second.turn'], '(-1.5 * first.turn)',
            'first drives second'),
      ],
    });
    const run = new Run(program, 0.05, null);
    run.move('crank', { by: 10, duration: 0.05 });
    run.advance();
    expect(run.state()).toEqual({
      crank: 10, 'first.turn': 20, 'second.turn': -30,
    });
  });

  it('holds a value no edge determines', () => {
    const program = bench({
      coordinates: { crank: input(0), idle: coordinate(3) },
      edges: [],
      sources: { crank: ['crank'], idle: [] },
    });
    const run = new Run(program, 0.05, null);
    run.move('crank', { by: 10, duration: 0.05 });
    run.advance();
    expect(run.state().idle).toBe(3);
  });

  it('refuses a conflict between two determinations, naming the relation',
     () => {
       const program = bench({
         coordinates: {
           crank: input(0), 'wheel.turn': coordinate(0),
         },
         edges: [
           law(['crank'], ['wheel.turn'], 'crank', 'crank drives wheel'),
           law(['crank'], ['wheel.turn'], '(2 * crank)',
               'the other relation drives wheel'),
         ],
       });
       const run = new Run(program, 0.05, null);
       const command = run.move('crank', { by: 10, duration: 0.05 });
       let message = '';
       try {
         run.advance();
       } catch (error) {
         message = String(error);
       }
       expect(message).toContain('the other relation drives wheel');
       expect(message).toContain('wheel.turn');
       expect(message).toContain('Bench');
       // The tick committed nothing and the command that moved is refused.
       expect(run.state()).toEqual({ crank: 0, 'wheel.turn': 0 });
       expect(run.tick()).toBe(0);
       expect(command.status).toBe('refused');
     });

  it('refuses a check whose prediction disagrees', () => {
    const program = bench({
      coordinates: {
        crank: input(0), slot: coordinate(0), 'wheel.turn': coordinate(0),
      },
      edges: [
        law(['crank'], ['wheel.turn'], 'crank', 'crank drives wheel'),
        law(['crank'], ['slot'], '(3 * crank)', 'crank drives slot'),
        {
          kind: 'check', needs: ['slot', 'wheel.turn'], gives: [],
          description: "the derived coordinate 'slot'", stated_by: 'Bench',
          factors: [0.0, 1], constant: 0, slot: 'slot',
        },
      ],
    });
    const run = new Run(program, 0.05, null);
    run.move('crank', { by: 10, duration: 0.05 });
    expect(() => run.advance())
      .toThrow(/the derived coordinate 'slot'|predicts an increment/);
    expect(run.tick()).toBe(0);
  });
});

describe('a declared bound is a physical stop', () => {
  it('lands absolute requests exactly at both Curta-derived endpoints', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], 'feed', 'direct carriage')],
      spans: { slide: { low: null, high: 3.9075 } },
    });
    const run = new Run(program, 1, 8);
    const reverse = run.move('feed', { to: -4.9425 });
    expect(reverse.status).toBe('completed');
    expect(run.state()).toEqual({ feed: -4.9425, slide: -4.9425 });
    const forward = run.move('feed', { to: 3.9075 });
    expect(forward.status).toBe('completed');
    expect(run.state()).toEqual({ feed: 3.9075, slide: 3.9075 });
    expect(run.stops()).toEqual([]);
  });

  it('does not mistake the adjacent starting float for an outward stop', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], 'feed', 'direct carriage')],
      spans: { slide: { low: null, high: 3.9075 } },
    });
    const run = new Run(program, 1, 8);
    const adjacent = nextAfter(-4.9425, Infinity);
    expect(run.move('feed', { to: adjacent }).status).toBe('completed');
    expect(run.state().feed).toBe(adjacent);
    const forward = run.move('feed', { to: 3.9075 });
    expect(forward.status).toBe('completed');
    expect(run.state()).toEqual({ feed: 3.9075, slide: 3.9075 });
    expect(run.stops()).toEqual([]);
  });

  it('leaves relative and rate requests on their existing delta arithmetic', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], 'feed', 'direct carriage')],
    });
    const relative = new Run(program, 1, 8);
    relative.move('feed', { to: -4.9425 });
    const delta = 3.9075 - relative.state().feed;
    relative.move('feed', { by: delta });
    expect(relative.state().feed).toBe(-4.9425 + delta);
    expect(relative.state().feed).not.toBe(3.9075);
    const rated = new Run(program, 1, 8);
    rated.move('feed', { to: -4.9425 });
    rated.rate('feed', delta);
    rated.advance();
    expect(rated.state().feed).toBe(-4.9425 + delta);
  });

  it('keeps timed interior samples and a retained descendant offset', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(2) },
      edges: [law(['feed'], ['slide'], 'feed', 'offset carriage')],
    });
    const run = new Run(program, 1, 8);
    const command = run.move('feed', { to: -4.9425, duration: 2 });
    run.advance();
    const middle = run.state();
    expect(middle.feed).toBe(-2.47125);
    expect(middle.slide).toBe(2 + middle.feed);
    expect(command.status).toBe('active');
    const taken = run.snapshot();
    run.advance();
    const landed = run.state();
    expect(landed.feed).toBe(-4.9425);
    expect(landed.slide).toBe(2 + -4.9425);
    run.restore(taken);
    run.advance();
    expect(run.state()).toEqual(landed);
  });

  it('restores a legacy active move record without endpoint metadata', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], 'feed', 'direct carriage')],
    });
    const run = new Run(program, 1, 8);
    run.move('feed', { to: -4.9425, duration: 2 });
    run.advance();
    const legacy = run.snapshot();
    delete legacy.commands[0].target;
    run.restore(legacy);
    run.advance();
    expect(run.commands()).toHaveLength(0);
    expect(Number.isFinite(run.state().feed)).toBe(true);
  });

  it('carries terminal landings through wiring and formula without discarding offsets', () => {
    const program = bench({
      coordinates: { feed: input(0), wired: coordinate(2), derived: coordinate(5) },
      edges: [
        { kind: 'wiring', needs: ['feed'], gives: ['wired'],
          description: 'feed wires output', stated_by: 'Bench', factor: 1 },
        { kind: 'formula', needs: ['wired'], gives: ['derived'],
          description: 'wired derives output', stated_by: 'Bench',
          factors: [1], constant: 0, slot: 'derived' },
      ],
    });
    const run = new Run(program, 1, 8);
    run.move('feed', { to: -4.9425 });
    expect(run.state()).toEqual({ feed: -4.9425, wired: 2 - 4.9425, derived: 5 - 4.9425 });
    const held = run.state();
    run.move('feed', { to: 3.9075 });
    const wireDelta = 3.9075 - held.feed;
    const wireEnd = held.wired + wireDelta;
    expect(run.state()).toEqual({
      feed: 3.9075,
      wired: wireEnd,
      derived: held.derived + (wireEnd - held.wired),
    });
  });

  it('refuses malformed absolute targets before mutating a live run', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], 'feed', 'direct carriage')],
    });
    const run = new Run(program, 1, 8);
    run.move('feed', { to: 3.9075, duration: 2 });
    run.advance();
    const before = run.snapshot();
    const live = run.commands()[0];
    for (const target of [Infinity, '3.9075', null]) {
      const malformed = structuredClone(before) as typeof before;
      (malformed.commands[0] as unknown as Record<string, unknown>).target = target;
      expect(() => run.restore(malformed)).toThrow();
      expect(run.snapshot()).toEqual(before);
      expect(live.status).toBe('active');
    }
    const unknown = structuredClone(before);
    unknown.commands[0].input = 'unregistered';
    expect(() => run.restore(unknown)).toThrow();
    expect(run.snapshot()).toEqual(before);
    expect(live.status).toBe('active');
    const misclassified = structuredClone(before);
    misclassified.commands[0].kind = 'rate';
    expect(() => run.restore(misclassified)).toThrow();
    expect(run.snapshot()).toEqual(before);
    expect(live.status).toBe('active');
  });

  it('refuses a fractional native target in an integer-driver snapshot', () => {
    const program = loadProgram({
      format: 'machinome-export', version: 5,
      drivers: { feed: { default: 0, range: null, unit: null, dtype: 'int', scale: null } },
      instructions: {},
      program: {
        identity: 'integer-target-restore', clock: 'time',
        coordinates: { feed: input(0), slide: coordinate(0) },
        intermediates: [], edges: [law(['feed'], ['slide'], 'feed', 'integer slide')],
        spans: {}, sources: { feed: ['feed'], slide: ['feed'] }, limits: LIMITS,
      },
    } as unknown as RunDocument, 'bench://integer-target-restore');
    const run = new Run(program, 1, 8);
    run.move('feed', { to: 4, duration: 2 });
    run.advance();
    const before = run.snapshot();
    const malformed = structuredClone(before);
    malformed.commands[0].target = 4.5;
    expect(() => run.restore(malformed)).toThrow(/invalid native target/);
    expect(run.snapshot()).toEqual(before);
  });

  it('never applies the full target after a genuine earlier physical stop', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], 'feed', 'direct carriage')],
      spans: { slide: { high: 1 } },
    });
    const run = new Run(program, 1, 8);
    run.move('feed', { to: -4.9425 });
    const command = run.move('feed', { to: 3.9075 });
    expect(command.status).toBe('blocked');
    expect(run.state()).toEqual({ feed: 1, slide: 1 });
    expect(run.stops()).toHaveLength(1);
  });

  it('finishes an independent exact target after another command stops mid-tick', () => {
    const program = bench({
      coordinates: {
        brake: input(0), feed: input(-4.9425),
        brakeSlide: coordinate(0), feedSlide: coordinate(-4.9425),
      },
      edges: [
        law(['brake'], ['brakeSlide'], 'brake', 'brake drives its slide'),
        law(['feed'], ['feedSlide'], 'feed', 'feed drives its slide'),
      ],
      spans: { brakeSlide: { high: 1 }, feedSlide: { high: 3.9075 } },
    });
    const run = new Run(program, 1, 8);
    const blocked = run.move('brake', { to: 2, duration: 1 });
    const completed = run.move('feed', { to: 3.9075, duration: 1 });
    run.advance();
    expect(blocked.status).toBe('blocked');
    expect(completed.status).toBe('completed');
    expect(run.state()).toEqual({ brake: 1, feed: 3.9075,
      brakeSlide: 1, feedSlide: 3.9075 });
    expect(run.stops()).toHaveLength(1);
  });

  it('preserves the sign of an exact zero terminal target', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], 'feed', 'direct carriage')],
    });
    const run = new Run(program, 1, 8);
    expect(run.move('feed', { to: -0 }).status).toBe('completed');
    expect(Object.is(run.state().feed, -0)).toBe(true);
    expect(Object.is(run.state().slide, -0)).toBe(true);
  });

  it('carries an exact target through a retained Play and its descendant', () => {
    const program = bench({
      coordinates: { feed: input(0), follower: coordinate(0), slide: coordinate(0) },
      edges: [
        play('feed', 'follower', -1, 1),
        law(['follower'], ['slide'], 'follower', 'follower drives slide'),
      ],
      spans: { slide: { low: null, high: 2.9075 } },
    });
    const run = new Run(program, 1, 8);
    expect(run.move('feed', { to: -4.9425 }).status).toBe('completed');
    expect(run.move('feed', { to: 3.9075 }).status).toBe('completed');
    expect(run.state()).toEqual({ feed: 3.9075, follower: 2.9075, slide: 2.9075 });
    expect(run.stops()).toEqual([]);
  });

  it('retains every affine descendant interior probe of the legacy BY path', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], '(3 * feed)', 'geared slide')],
    });
    const probes = [1 / 64, 7 / 64, 1 / 2, 63 / 64];
    const sampled = (absolute: boolean): number[] => {
      const run = new Run(program, 1, 8);
      run.move('feed', { to: -4.9425 });
      const target = 3.9075;
      const delta = target - run.state().feed;
      const probe = run as unknown as { pass: (...args: unknown[]) => Record<string, number> };
      const original = probe.pass.bind(run);
      const seen: number[] = [];
      const spy = vi.spyOn(probe, 'pass').mockImplementation((...args) => {
        const result = original(...args);
        const path = propagations.get(args[1] as Record<string, number>)?.motions.get('slide');
        if (path) seen.push(...probes.map(t => path.at(t)));
        return result;
      });
      run.move('feed', absolute ? { to: target } : { by: delta });
      spy.mockRestore();
      return seen;
    };
    expect(sampled(true)).toEqual(sampled(false));
  });

  it('does not evaluate a rounded, invalid endpoint before the authored one', () => {
    const program = bench({
      coordinates: { feed: input(-0.2), slide: coordinate(Math.sqrt(0.3)) },
      edges: [law(['feed'], ['slide'], 'sqrt(0.1 - feed)', 'square-root carriage', false)],
    });
    const run = new Run(program, 1, 8);
    expect(run.move('feed', { to: 0.1 }).status).toBe('completed');
    expect(run.state().feed).toBe(0.1);
    expect(Number.isFinite(run.state().slide)).toBe(true);
  });

  it('does not evaluate a rounded invalid endpoint after a retained Play', () => {
    const program = bench({
      coordinates: {
        feed: input(-0.2), ball: coordinate(-1.2), slide: coordinate(Math.sqrt(1.3)),
      },
      edges: [play('feed', 'ball', -1, 1), law(['ball'], ['slide'],
        'sqrt(0.10000000000000009 - ball)', 'curved follower carriage', false)],
    });
    const run = new Run(program, 1, 8);
    expect(run.move('feed', { to: 1.1 }).status).toBe('completed');
    expect(run.state()).toEqual({ feed: 1.1, ball: 0.10000000000000009, slide: 0 });
  });

  it('keeps a planned curved law finite at an exact terminal domain edge', () => {
    const program = bench({
      coordinates: { feed: input(-0.2), slide: coordinate(0) },
      edges: [{ kind: 'law', needs: ['feed'], gives: ['slide'],
        description: 'gated square-root slide', stated_by: 'Bench',
        expressions: ['(sqrt(0.1 - feed) * (feed > 0))'], affine: [false],
        plans: [{ skeleton: '(sqrt(0.1 - feed) * _j0)', jumps: [
          { name: '_j0', primitive: '>', level: 'feed', affine: true },
        ] }] }],
    });
    const run = new Run(program, 1, 8);
    expect(run.move('feed', { to: 0.1 }).status).toBe('completed');
    expect(run.state().feed).toBe(0.1);
    // The positive branch changes by its endpoint difference from the
    // crossing, so this is a retained integrated value, not static pose 0.
    expect(Number.isFinite(run.state().slide)).toBe(true);
    expect(run.state().slide).toBeLessThan(0);
  });

  it('does not reread a stateful call or its binding alias to correct a descendant', async () => {
    for (const viaBinding of [false, true]) {
      vi.resetModules();
      const random = vi.spyOn(Math, 'random')
        .mockReturnValueOnce(0.1).mockReturnValueOnce(0.2).mockReturnValueOnce(0.3);
      try {
        const [{ Run: FreshRun }, { loadProgram: freshLoad }] = await Promise.all([
          import('./run'), import('./program'),
        ]);
        const program = freshLoad({
          format: 'machinome-export', version: 5,
          bindings: viaBinding ? [{ name: 'noise', expression: 'random(1)' }] : [],
          drivers: { feed: { default: -4.9425, range: null, unit: null, dtype: null, scale: null } },
          instructions: {},
          program: {
            identity: 'stateful-terminal', clock: 'time',
            coordinates: { feed: input(-4.9425), slide: coordinate(-4.9425) },
            intermediates: [],
            edges: [law(['feed'], ['slide'], viaBinding
              ? '(feed + noise)' : '(feed + random(1))', 'stateful slide')],
            spans: {}, sources: { feed: ['feed'], slide: ['feed'] }, limits: LIMITS,
          },
        } as unknown as RunDocument, 'bench://stateful-terminal');
        const run = new FreshRun(program, 1, 8);
        const before = random.mock.calls.length;
        expect(run.move('feed', { to: 3.9075 }).status).toBe('completed');
        expect(random.mock.calls.length - before).toBe(2);
        expect(run.state().feed).toBe(3.9075);
        expect(run.state().slide).toBe(3.8075);
      } finally {
        random.mockRestore();
      }
    }
  });

  it('keeps a pre-import live math wrapper on its demanded legacy path', async () => {
    vi.resetModules();
    let calls = 0;
    const sin = vi.spyOn(Math, 'sin').mockImplementation(() => ++calls / 10);
    try {
      const [{ Run: FreshRun }, { loadProgram: freshLoad }] = await Promise.all([
        import('./run'), import('./program'),
      ]);
      const program = freshLoad({
        format: 'machinome-export', version: 5,
        drivers: { feed: { default: -4.9425, range: null, unit: null, dtype: null, scale: null } },
        instructions: {},
        program: {
          identity: 'live-wrapper-terminal', clock: 'time',
          coordinates: { feed: input(-4.9425), slide: coordinate(-4.9425) },
          intermediates: [],
          edges: [law(['feed'], ['slide'], '(feed + sin(1))', 'live wrapper slide')],
          spans: { slide: { high: { expression: '(100000 + feed)' } } },
          sources: { feed: ['feed'], slide: ['feed'] }, limits: LIMITS,
        },
      } as unknown as RunDocument, 'bench://live-wrapper-terminal');
      const relative = new FreshRun(program, 1, 8);
      relative.move('feed', { by: 3.9075 - -4.9425 });
      const relativeCalls = calls;
      const relativeSlide = relative.state().slide;
      calls = 0;
      const absolute = new FreshRun(program, 1, 8);
      expect(absolute.move('feed', { to: 3.9075 }).status).toBe('completed');
      expect(calls).toBe(relativeCalls);
      expect(absolute.state().slide).toBe(relativeSlide);
      expect(absolute.state().feed).toBe(3.9075);
    } finally {
      sin.mockRestore();
    }
  });

  it('still refuses a genuinely invalid authored source state atomically', () => {
    const program = bench({
      coordinates: { feed: input(0.2), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], '(feed > 0.1 ? missing() : feed)', 'invalid-start carriage', false)],
    });
    const run = new Run(program, 1, 8);
    const before = run.snapshot();
    expect(() => run.move('feed', { to: 0.1 })).toThrow();
    expect(run.state()).toEqual(before.bank);
    expect(run.tick()).toBe(before.tick);
  });

  it('keeps the ordered moving-Bound interior scopes of the legacy BY request', () => {
    const program = bench({
      coordinates: { feed: input(0), slide: coordinate(0) },
      edges: [law(['feed'], ['slide'], '(3 * feed)', 'geared slide')],
      spans: { slide: { high: { expression: '(2 * feed)' } } },
    });
    const sampled = (absolute: boolean): number[] => {
      const run = new Run(program, 1, 8);
      run.move('feed', { to: -4.9425 });
      const delta = 3.9075 - run.state().feed;
      const seen: number[] = [];
      const binding = ExpressionPath.prototype.bind;
      const probing = ExpressionPath.prototype.at;
      const first = vi.spyOn(ExpressionPath.prototype, 'bind').mockImplementation(function (values, initial) {
        if ('feed' in values) seen.push(values.feed);
        return binding.call(this, values, initial);
      });
      const later = vi.spyOn(ExpressionPath.prototype, 'at').mockImplementation(function (values) {
        if ('feed' in values) seen.push(values.feed);
        return probing.call(this, values);
      });
      try {
        run.move('feed', absolute ? { to: 3.9075 } : { by: delta });
      } finally {
        first.mockRestore();
        later.mockRestore();
      }
      return seen;
    };
    const absolute = sampled(true);
    const relative = sampled(false);
    expect(absolute.length).toBeGreaterThan(4);
    expect(absolute).toEqual(relative);
  });

  it('keeps jump crossings and replay while landing the input exactly', () => {
    const program = bench({
      coordinates: { feed: input(0), dial: coordinate(0) },
      edges: [{
        kind: 'law', needs: ['feed'], gives: ['dial'],
        description: 'periodic dial', stated_by: 'Bench',
        expressions: ['(feed - floor(feed))'], affine: [true],
        plans: [{ skeleton: '(feed - _j0)', jumps: [
          { name: '_j0', primitive: 'floor', level: 'feed', affine: true },
        ] }],
      }],
    });
    const run = new Run(program, 1, 16);
    run.move('feed', { to: -4.9425 });
    const before = run.snapshot();
    const earlierCrossings = run.crossings().length;
    const probe = run as unknown as { pass: (...args: unknown[]) => Record<string, number> };
    const original = probe.pass.bind(run);
    let exactDialEnd: number | undefined;
    const spy = vi.spyOn(probe, 'pass').mockImplementation((...args) => {
      const result = original(...args);
      exactDialEnd = propagations.get(args[1] as Record<string, number>)?.motions.get('dial')?.end;
      return result;
    });
    expect(run.move('feed', { to: 3.9075 }).status).toBe('completed');
    spy.mockRestore();
    expect(run.state().feed).toBe(3.9075);
    expect(Number.isFinite(run.state().dial)).toBe(true);
    expect(run.state().dial).toBe(exactDialEnd);
    const landed = run.snapshot();
    const crossingCount = run.crossings().length;
    expect(crossingCount).toBeGreaterThan(0);
    run.restore(before);
    run.move('feed', { to: 3.9075 });
    expect(run.snapshot()).toEqual(landed);
    expect(run.crossings()).toHaveLength(crossingCount - earlierCrossings);
  });

  it('locates a downstream play stop from the original input prefix', () => {
    const program = bench({
      coordinates: { x: input(0), y: coordinate(0), z: coordinate(0) },
      edges: [play('x', 'y', -10, 10), play('y', 'z', -10, 10)],
      spans: { z: { low: null, high: 20 } },
    });
    const run = new Run(program, 1, 16);
    const command = run.move('x', { by: 100, duration: 1 });
    run.advance();
    expect(run.state()).toEqual({ x: 40, y: 30, z: 20 });
    expect(command.status).toBe('blocked');
  });

  it('allows clearance before a stopped follower is recollected', () => {
    const program = bench({
      coordinates: {
        x: input(0), a: coordinate(0), b: coordinate(0), c: coordinate(0),
      },
      edges: [play('x', 'a', -10, 10), play('a', 'b', -10, 10),
              play('b', 'c', -10, 10)],
      spans: { c: { low: -20, high: 20 } },
    });
    const run = new Run(program, 1, 16);
    run.move('x', { to: 100, duration: 1 });
    run.advance();
    expect(run.state()).toEqual({ x: 50, a: 40, b: 30, c: 20 });
    run.move('x', { to: 40, duration: 1 });
    run.advance();
    expect(run.state().c).toBe(20);
    const positive = run.move('x', { to: 60, duration: 1 });
    run.advance();
    expect(positive.admitted).toBe(10);
    expect(run.state().x).toBe(50);

    run.move('x', { to: -100, duration: 1 });
    run.advance();
    run.move('x', { to: -40, duration: 1 });
    run.advance();
    expect(run.state().c).toBe(-20);
    const negative = run.move('x', { to: -60, duration: 1 });
    run.advance();
    expect(negative.admitted).toBe(-10);
    expect(run.state().x).toBe(-50);
  });

  it('locates an ordinary bounded observer through the play prefix', () => {
    const program = bench({
      coordinates: {
        x: input(0), a: coordinate(0), b: coordinate(0), c: coordinate(0),
        observer: coordinate(0),
      },
      edges: [play('x', 'a', -10, 10), play('a', 'b', -10, 10),
              play('b', 'c', -10, 10), {
                kind: 'wiring', needs: ['c'], gives: ['observer'],
                description: 'third drives observer', stated_by: 'Bench',
                factor: -2,
              }],
      spans: { observer: { low: -40, high: 40 } },
    });
    const run = new Run(program, 1, 16);
    run.move('x', { to: 100, duration: 1 });
    run.advance();
    expect(run.state()).toEqual({
      x: 50, a: 40, b: 30, c: 20, observer: -40,
    });
    run.move('x', { to: 40, duration: 1 });
    run.advance();
    const recollect = run.move('x', { to: 100, duration: 1 });
    run.advance();
    expect(recollect.admitted).toBe(10);
    expect(run.state().x).toBe(50);
  });

  it('searches a nonlinear observer through its inward excursion', () => {
    const program = bench({
      coordinates: {
        x: input(0), a: coordinate(0), b: coordinate(0), c: coordinate(0),
        observer: coordinate(0),
      },
      edges: [play('x', 'a', -10, 10), play('a', 'b', -10, 10),
              play('b', 'c', -10, 10),
              law(['c'], ['observer'], '(c * c)', 'square observer', false)],
      spans: { observer: { low: null, high: 400 } },
    });
    const run = new Run(program, 1, 16);
    run.move('x', { to: 100, duration: 1 });
    run.advance();
    expect(run.state().x).toBeCloseTo(50, 9);
    run.move('x', { to: 40, duration: 1 });
    run.advance();
    run.move('x', { to: 100, duration: 1 });
    run.advance();
    expect(run.state().x).toBeCloseTo(50, 9);
    run.move('x', { to: -100, duration: 1 });
    run.advance();
    expect(run.state().x).toBeCloseTo(-50, 9);
    expect(run.state().c).toBeCloseTo(-20, 9);
    expect(run.state().observer).toBe(400);
  });

  it('searches a multi-source observer through its play ancestor', () => {
    const program = bench({
      coordinates: {
        x: input(0), motor: input(0), a: coordinate(0), b: coordinate(0),
        c: coordinate(0), observer: coordinate(0),
      },
      edges: [play('x', 'a', -10, 10), play('a', 'b', -10, 10),
              play('b', 'c', -10, 10),
              law(['c', 'motor'], ['observer'], '(c + motor)',
                  'offset observer')],
      spans: { observer: { low: -40, high: 40 } },
    });
    const run = new Run(program, 1, 16);
    run.move('motor', { to: 7, duration: 1 }); run.advance();
    run.move('x', { to: 100, duration: 1 }); run.advance();
    expect(run.state().x).toBeCloseTo(63, 9);
    run.move('x', { to: 53, duration: 1 }); run.advance();
    run.move('x', { to: 100, duration: 1 }); run.advance();
    expect(run.state().x).toBeCloseTo(63, 9);
    run.move('x', { to: -100, duration: 1 }); run.advance();
    expect(run.state().x).toBeCloseTo(-77, 9);
    expect(run.state().observer).toBe(-40);
  });

  const ratchet = () => bench({
    coordinates: { arbor: input(40), 'wheel.turn': coordinate(40) },
    edges: [law(['arbor'], ['wheel.turn'], 'arbor', 'arbor drives wheel')],
    spans: {
      'wheel.turn': {
        low: { expression: '(36 * floor((wheel.turn / 36)))' }, high: null,
      },
    },
  });

  it('commits the coordinate AT its bound and blocks the group', () => {
    const run = new Run(ratchet(), 0.05, 64);
    const command = run.move('arbor', { by: -20, duration: 0.2 });
    run.advance();
    // The last seated tooth is 36 degrees; the tick asked for -5.
    expect(run.state()['wheel.turn']).toBe(36);
    expect(command.status).toBe('blocked');
    expect(command.admitted).toBeCloseTo(-4, 12);
    const stops = run.stops();
    expect(stops).toHaveLength(1);
    expect(stops[0].coordinate).toBe('wheel.turn');
    expect(stops[0].bound).toBe('low');
    expect(stops[0].value).toBe(36);
    expect(stops[0].inputs).toEqual(['arbor']);
    expect(stops[0].t).toBeCloseTo(0.8, 12);
  });

  it('locates a stop behind a NON-affine edge by sampling and bisection',
     () => {
       const program = bench({
         coordinates: { crank: input(0), 'wheel.turn': coordinate(0) },
         edges: [law(['crank'], ['wheel.turn'], '(crank ^ 2)',
                     'crank drives wheel', false)],
         spans: { 'wheel.turn': { low: null, high: 4 } },
       });
       const run = new Run(program, 0.05, 64);
       const command = run.move('crank', { by: 4, duration: 0.05 });
       run.advance();
       expect(run.state()['wheel.turn']).toBe(4);
       // crank^2 reaches 4 at crank = 2, half way through the tick.
       expect(run.stops()[0].t).toBeCloseTo(0.5, 9);
       expect(command.status).toBe('blocked');
       expect(command.admitted).toBeCloseTo(2, 9);
     });

  it('is free to move AWAY from a bound it already stands on', () => {
    const run = new Run(ratchet(), 0.05, 64);
    const command = run.move('arbor', { by: 10, duration: 0.05 });
    run.advance();
    expect(run.state()['wheel.turn']).toBe(50);
    expect(command.status).toBe('completed');
    expect(run.stops()).toHaveLength(0);
  });

  it('does not stop an input reaching it only through a disengaged law',
     () => {
       // `wheel.turn` is pushed by `shaft` only while the clutch is
       // engaged; `sleeve` is what engages it, and is not pushing.
       const program = bench({
         coordinates: {
           shaft: input(0), sleeve: input(0), 'wheel.turn': coordinate(0),
         },
         edges: [{
           kind: 'law', needs: ['shaft', 'sleeve'], gives: ['wheel.turn'],
           description: '(shaft, sleeve) drives wheel.turn',
           stated_by: 'Bench',
           expressions: ['(shaft * (sleeve > 0.5))'], affine: [true],
           plans: [{
             skeleton: '(shaft * _j0)',
             jumps: [{
               name: '_j0', primitive: '>', level: '(sleeve - 0.5)',
               affine: true,
             }],
           }],
         }],
         spans: { 'wheel.turn': { low: null, high: 4 } },
       });
       const run = new Run(program, 0.05, 64);
       const turning = run.move('shaft', { by: 10, duration: 0.05 });
       const engaging = run.move('sleeve', { by: 0.2, duration: 0.05 });
       run.advance();
       // The clutch is open for the whole tick, so the wheel never moves
       // and neither command is blocked.
       expect(run.state()['wheel.turn']).toBe(0);
       expect(turning.status).toBe('completed');
       expect(engaging.status).toBe('completed');
     });
});

describe('the segment loop and atomicity', () => {
  const twoStops = () => bench({
    coordinates: {
      lever_in: input(0), steer: input(0),
      'a.turn': coordinate(0), 'b.turn': coordinate(0),
    },
    edges: [
      law(['lever_in'], ['a.turn'], 'lever_in', 'lever drives a'),
      law(['steer'], ['b.turn'], 'steer', 'steer drives b'),
    ],
    spans: {
      'a.turn': { low: null, high: 1 },
      'b.turn': { low: null, high: 3 },
    },
  });

  it('takes two stops at two fractions of one tick', () => {
    const run = new Run(twoStops(), 0.05, 64);
    const first = run.move('lever_in', { by: 4, duration: 0.05 });
    const second = run.move('steer', { by: 6, duration: 0.05 });
    run.advance();
    expect(run.state()['a.turn']).toBe(1);
    expect(run.state()['b.turn']).toBe(3);
    expect(first.status).toBe('blocked');
    expect(second.status).toBe('blocked');
    const stops = run.stops();
    expect(stops.map((one) => one.coordinate)).toEqual(['a.turn', 'b.turn']);
    expect(stops[0].t).toBeCloseTo(0.25, 12);
    expect(stops[1].t).toBeCloseTo(0.5, 12);
  });

  it('maps a crossing back to the fraction of the TICK across a segment',
     () => {
       // A fold and a stop in one tick: the crossing is located inside
       // the segment before the stop and recorded at its fraction of the
       // whole tick.
       const program = bench({
         coordinates: { crank: input(0), 'wheel.turn': coordinate(0) },
         edges: [{
           kind: 'law', needs: ['crank'], gives: ['wheel.turn'],
           description: 'crank drives wheel.turn', stated_by: 'Bench',
           expressions: ['(crank - floor(crank))'], affine: [true],
           plans: [{
             skeleton: '(crank - _j0)',
             jumps: [{ name: '_j0', primitive: 'floor', level: 'crank',
                       affine: true }],
           }],
         }],
         spans: { 'wheel.turn': { low: null, high: 1.5 } },
       });
       const run = new Run(program, 0.05, 64);
       run.move('crank', { by: 3, duration: 0.05 });
       run.advance();
       const crossings = run.crossings();
       expect(crossings.length).toBeGreaterThan(0);
       for (const crossing of crossings) {
         expect(crossing.t).toBeGreaterThanOrEqual(0);
         expect(crossing.t).toBeLessThanOrEqual(1);
       }
       const stops = run.stops();
       expect(stops).toHaveLength(1);
       // The crossing at t = 1/3 of the tick came before the stop.
       expect(crossings[0].t).toBeCloseTo(1 / 3, 9);
       expect(crossings[0].t).toBeLessThan(stops[0].t);
     });

  it('a tick that refuses in its second segment commits nothing at all',
     () => {
       const program = bench({
         coordinates: {
           lever_in: input(0), 'a.turn': coordinate(0),
           'b.turn': coordinate(0),
         },
         edges: [
           law(['lever_in'], ['a.turn'], 'lever_in', 'lever drives a'),
           // Two relations disagree on `b` -- but only once `a` has
           // stopped and the second segment runs at a different stretch.
           law(['a.turn'], ['b.turn'], 'a.turn', 'a drives b'),
           law(['lever_in'], ['b.turn'], '(2 * lever_in)',
               'lever also drives b'),
         ],
         spans: { 'a.turn': { low: null, high: 1 } },
       });
       const run = new Run(program, 0.05, 64);
       const command = run.move('lever_in', { by: 4, duration: 0.05 });
       expect(() => run.advance()).toThrow();
       expect(run.state())
         .toEqual({ lever_in: 0, 'a.turn': 0, 'b.turn': 0 });
       expect(run.tick()).toBe(0);
       expect(command.status).toBe('refused');
       expect(run.stops()).toHaveLength(0);
       expect(run.crossings()).toHaveLength(0);
     });
});

describe('state', () => {
  const machine = () => bench({
    coordinates: { crank: input(0), 'wheel.turn': coordinate(0) },
    edges: [law(['crank'], ['wheel.turn'], '(2 * crank)', 'crank drives wheel')],
  });

  it('snapshots identity, dt, tick, bank and command records', () => {
    const run = new Run(machine(), 0.05, 8);
    run.move('crank', { by: 10, duration: 0.5 });
    run.advance();
    const state = run.snapshot();
    expect(state.program).toBe('bench');
    expect(state.dt).toBe(0.05);
    expect(state.tick).toBe(1);
    expect(state.bank).toEqual({ crank: 1, 'wheel.turn': 2 });
    expect(state.commands).toHaveLength(1);
  });

  it('restores, cancelling live handles and rebuilding the table', () => {
    const run = new Run(machine(), 0.05, 8);
    run.move('crank', { by: 10, duration: 0.5 });
    run.advance();
    const state = run.snapshot();
    run.advance();
    run.advance();
    const live = run.commands()[0];
    run.restore(state);
    expect(live.status).toBe('cancelled');
    expect(run.tick()).toBe(1);
    expect(run.state()).toEqual({ crank: 1, 'wheel.turn': 2 });
    expect(run.crossings()).toHaveLength(0);
    // And the rebuilt command goes on admitting the same travel.
    run.advance();
    expect(run.state().crank).toBe(2);
  });

  it('refuses a snapshot from another program before touching anything',
     () => {
       const run = new Run(machine(), 0.05, 8);
       run.advance();
       let message = '';
       try {
         run.restore({ program: 'elsewhere', dt: 0.05, tick: 0, bank: {},
                       commands: [] });
       } catch (error) {
         message = String(error);
       }
       expect(message).toContain('elsewhere');
       expect(message).toContain('bench');
       expect(run.tick()).toBe(1);
     });

  it('refuses a snapshot taken at another dt', () => {
    const run = new Run(machine(), 0.05, 8);
    let message = '';
    try {
      run.restore({ program: 'bench', dt: 0.1, tick: 0, bank: {},
                    commands: [] });
    } catch (error) {
      message = String(error);
    }
    expect(message).toContain('0.1');
    expect(message).toContain('0.05');
  });

  it('resets to the initial snapshot', () => {
    const run = new Run(machine(), 0.05, 8);
    run.move('crank', { by: 10, duration: 0.5 });
    run.advance();
    run.advance();
    run.reset();
    expect(run.tick()).toBe(0);
    expect(run.state()).toEqual({ crank: 0, 'wheel.turn': 0 });
    expect(run.commands()).toHaveLength(0);
  });

  it('keeps a bounded ring, and none at all when none was asked for', () => {
    const bounded = new Run(machine(), 0.05, 3);
    for (let step = 0; step < 6; step += 1) bounded.advance();
    expect(bounded.trajectory()).toHaveLength(3);
    expect(bounded.trajectory()[0].tick).toBe(4);

    const none = new Run(machine(), 0.05, null);
    none.advance();
    expect(none.trajectory()).toHaveLength(0);
    expect(none.crossings()).toHaveLength(0);
    expect(none.stops()).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------
// A bound that READS OTHER COORDINATES (design D4-D6). Each bench below
// reproduces a fixture of machinome's own
// `tests/running_project/machine.py`, and every number is that
// repository's `tests/test_running_stops.py`.
// ---------------------------------------------------------------------

const pinLift = (k: number) =>
  `(5 - (5 * min(max(((key.travel - ${k}) / 5), 0.0), 1.0)))`;

const CLEARED =
  '((90 * (abs(p1.lift) <= 0.05)) * (abs(p2.lift) <= 0.05))';

/** `Gate`: the lock's shape reduced to two pins. The plug may turn only
 * while every lift stands inside the shear-line window. */
function gate(captured = false): LoadedProgram {
  return bench({
    coordinates: {
      feed: input(captured ? 20 : 10),
      twist: input(0),
      'key.travel': coordinate(captured ? 20 : 10),
      'p1.lift': coordinate(captured ? 0 : 5),
      'p2.lift': coordinate(captured ? 0 : 5),
      'plug.turn': coordinate(0),
    },
    edges: [
      law(['feed'], ['key.travel'], 'feed', 'feed drives key.travel'),
      law(['twist'], ['plug.turn'], 'twist', 'twist drives plug.turn'),
      law(['key.travel'], ['p1.lift'], pinLift(10),
          'key.travel drives p1.lift', false),
      law(['key.travel'], ['p2.lift'], pinLift(13),
          'key.travel drives p2.lift', false),
    ],
    spans: captured ? {
      'key.travel': { low: { expression: '(20 * (plug.turn > 0))' },
                      high: 20.0 },
      'plug.turn': { low: 0.0, high: { expression: CLEARED } },
    } : {
      'plug.turn': { low: 0.0, high: { expression: CLEARED } },
    },
    sources: {
      feed: ['feed'], twist: ['twist'],
      'key.travel': ['feed'], 'p1.lift': ['feed'], 'p2.lift': ['feed'],
      'plug.turn': ['twist'],
    },
  });
}

function ticks(run: Run, count: number): void {
  for (let at = 0; at < count; at += 1) run.advance();
}

describe('the Gate: a plug that turns only when its pins clear', () => {
  it('retains a self-read pawl path needed by a running bound', () => {
    const program = bench({
      coordinates: { crank: input(0), pawl: coordinate(0) },
      edges: [{
        kind: 'law', needs: ['crank', 'pawl'], gives: ['pawl'],
        description: 'crank drives retained pawl', stated_by: 'Bench',
        expressions: ['((crank / 2) + (2 * (pawl >= 3)))'], affine: [false],
        plans: [{ skeleton: '((crank / 2) + (2 * _j0))', jumps: [
          { name: '_j0', primitive: '>=', level: '(pawl - 3)', affine: true },
        ] }],
      }],
      spans: { crank: { high: { expression: '(10 - pawl)' } } },
      sources: { crank: ['crank'], pawl: ['crank'] },
    });
    expect(program.constraints.get('crank:high')?.reads).toEqual(['pawl']);
    const run = new Run(program, 0.1, 8);
    const before = run.snapshot();
    const probe = run as unknown as {
      searchedConstraint: (...args: unknown[]) => unknown;
    };
    const original = probe.searchedConstraint.bind(run);
    let retained = false;
    const search = vi.spyOn(probe, 'searchedConstraint').mockImplementation(
      (...args: unknown[]) => {
        const deltas = args[4] as Record<string, number>;
        retained ||= propagations.get(deltas)?.motions.has('pawl') ?? false;
        return original(...args);
      });
    try {
      const first = run.move('crank', { by: 10, duration: 0.1 });
      run.advance();
      expect(retained).toBe(true);
      expect(first.status).toBe('blocked');
      expect(first.admitted).toBeGreaterThan(0);
      expect(first.admitted).toBeLessThan(10);
      expect(run.stops().at(-1)?.coordinate).toBe('crank');
      const bank = run.state();
      const stops = run.stops();
      const outcome = [first.status, first.admitted];
      run.restore(before);
      const replay = run.move('crank', { by: 10, duration: 0.1 });
      run.advance();
      expect([replay.status, replay.admitted]).toEqual(outcome);
      expect(run.state()).toEqual(bank);
      expect(run.stops()).toEqual(stops);
      search.mockClear();
      run.advance();
      expect(search).not.toHaveBeenCalled();
      expect(run.state()).toEqual(bank);
      expect(run.stops()).toEqual(stops);
    } finally {
      search.mockRestore();
    }
  });

  it('keeps opposite signed-zero traced endpoints in the moving cone', () => {
    const signed = new Motion(-0, +0, [[0, 1, () => 0]]);
    expect(signed.constant).toBe(true);
    expect(movingConstraintReads(['signed'], new Map([['signed', signed]]),
      { signed: -0 }, { signed: 0 }).has('signed')).toBe(true);
    const loop = new Motion(0, 0, [[0, 1, t => t * (1 - t)]], false);
    expect(movingConstraintReads(['loop'], new Map([['loop', loop]]),
      { loop: 0 }, { loop: 0 }).has('loop')).toBe(true);
  });

  it('does not re-resolve standing bound work at every traced sample', () => {
    const standing = Array.from({ length: 48 }, (_, index) =>
      `abs(plug.turn + ${index + 1})`).join(' + ');
    const upper = `((90 * (feed >= 17.95)) + (0 * (${standing})))`;
    const run = new Run(bench({
      coordinates: { feed: input(20), 'plug.turn': coordinate(30) },
      edges: [],
      spans: { 'plug.turn': { high: { expression: upper } } },
      sources: { feed: ['feed'], 'plug.turn': [] },
    }), 0.1, 8);
    const before = run.snapshot();
    const baseline = expressionMetrics().resolutions;
    const handle = run.move('feed', { by: -5, duration: 0.1 });
    run.advance();
    const resolutions = expressionMetrics().resolutions - baseline;
    expect(handle.status).toBe('blocked');
    expect(handle.admitted).toBeCloseTo(-2.05, 9);
    expect(run.state().feed).toBeCloseTo(17.95, 9);
    expect(run.stops().at(-1)?.coordinate).toBe('plug.turn');
    expect(resolutions).toBeLessThan(10_000);
    const bank = run.state();
    const stop = run.stops().at(-1);
    run.restore(before);
    const repeated = run.move('feed', { by: -5, duration: 0.1 });
    run.advance();
    expect(repeated.status).toBe(handle.status);
    expect(repeated.admitted).toBe(handle.admitted);
    expect(run.state()).toEqual(bank);
    expect(run.stops().at(-1)).toEqual(stop);
  });

  it('reuses a successful finite Bound path across tick searches in one run', () => {
    const standing = Array.from({ length: 48 }, (_, index) =>
      `abs(plug.turn + ${index + 1})`).join(' + ');
    const upper = `((90 * (feed >= 0)) + (0 * (${standing})))`;
    const program = bench({
      coordinates: { feed: input(20), 'plug.turn': coordinate(30) },
      edges: [],
      spans: { 'plug.turn': { high: { expression: upper } } },
      sources: { feed: ['feed'], 'plug.turn': [] },
    });
    const run = new Run(program, 0.1, 8);
    const initial = run.snapshot();
    const bind = vi.spyOn(ExpressionPath.prototype, 'bind');
    try {
      run.move('feed', { by: -2, duration: 0.2 });
      run.advance();
      const afterFirst = run.state();
      run.advance();
      const calls = bind.mock.contexts.filter((path) =>
        (path as unknown as { expression: string }).expression === upper);
      expect(calls).toHaveLength(2);
      expect(calls[1]).toBe(calls[0]);
      expect(afterFirst.feed).toBe(19);
      expect(run.state().feed).toBe(18);
      expect((run as unknown as { boundPaths: Map<unknown, unknown> }).boundPaths.size)
        .toBe(1);
      run.restore(initial);
      expect((run as unknown as { boundPaths: Map<unknown, unknown> }).boundPaths.size)
        .toBe(0);
      run.move('feed', { by: -1, duration: 0.1 });
      run.advance();
      const replay = bind.mock.contexts.filter((path) =>
        (path as unknown as { expression: string }).expression === upper);
      expect(replay[2]).not.toBe(replay[1]);
      const other = new Run(program, 0.1, 8);
      other.move('feed', { by: -1, duration: 0.1 });
      other.advance();
      const independent = bind.mock.contexts.filter((path) =>
        (path as unknown as { expression: string }).expression === upper);
      expect(independent[3]).not.toBe(replay[2]);
    } finally {
      bind.mockRestore();
    }
  });

  it('does not retain a Bound path with a nondeterministic standing call', () => {
    const upper = '(90 + random() + (0 * feed))';
    const run = new Run(bench({
      coordinates: { feed: input(20), 'plug.turn': coordinate(30) },
      edges: [],
      spans: { 'plug.turn': { high: { expression: upper } } },
      sources: { feed: ['feed'], 'plug.turn': [] },
    }), 0.1, 8);
    const bind = vi.spyOn(ExpressionPath.prototype, 'bind');
    try {
      run.move('feed', { by: -2, duration: 0.2 });
      run.advance();
      run.advance();
      const calls = bind.mock.contexts.filter((path) =>
        (path as unknown as { expression: string }).expression === upper);
      expect(calls).toHaveLength(2);
      expect(calls[1]).not.toBe(calls[0]);
      expect((run as unknown as { boundPaths: Map<unknown, unknown> }).boundPaths.size)
        .toBe(0);
    } finally {
      bind.mockRestore();
    }
  });

  it('replaces a retained Bound path when a different read moves', () => {
    const upper = '(90 + (0 * feed) + (0 * other))';
    const run = new Run(bench({
      coordinates: { feed: input(20), other: input(20),
        'plug.turn': coordinate(30) },
      edges: [],
      spans: { 'plug.turn': { high: { expression: upper } } },
      sources: { feed: ['feed'], other: ['other'], 'plug.turn': [] },
    }), 0.1, 8);
    const bind = vi.spyOn(ExpressionPath.prototype, 'bind');
    try {
      run.move('feed', { by: -1, duration: 0.1 });
      run.advance();
      run.move('other', { by: -1, duration: 0.1 });
      run.advance();
      const calls = bind.mock.contexts.filter((path) =>
        (path as unknown as { expression: string }).expression === upper);
      expect(calls).toHaveLength(2);
      expect(calls[1]).not.toBe(calls[0]);
    } finally {
      bind.mockRestore();
    }
  });

  it('does not keep a Bound path after a nonfinite search scope', () => {
    const upper = '(90 + (0 * feed))';
    const run = new Run(bench({
      coordinates: { feed: input(20), 'plug.turn': coordinate(30) },
      edges: [],
      spans: { 'plug.turn': { high: { expression: upper } } },
      sources: { feed: ['feed'], 'plug.turn': [] },
    }), 0.1, 8);
    run.move('feed', { by: -1, duration: 0.1 });
    run.advance();
    const cache = (run as unknown as { boundPaths: Map<unknown, unknown> }).boundPaths;
    expect(cache.size).toBe(1);
    (run as unknown as { bank: Record<string, number> }).bank['plug.turn'] = Infinity;
    run.move('feed', { by: -1, duration: 0.1 });
    run.advance();
    expect(cache.size).toBe(0);
  });

  it('rebuilds a Bound path after the expression generation changes', () => {
    const upper = '(90 + (0 * feed))';
    const run = new Run(bench({
      coordinates: { feed: input(20), 'plug.turn': coordinate(30) },
      edges: [],
      spans: { 'plug.turn': { high: { expression: upper } } },
      sources: { feed: ['feed'], 'plug.turn': [] },
    }), 0.1, 8);
    const bind = vi.spyOn(ExpressionPath.prototype, 'bind');
    try {
      run.move('feed', { by: -2, duration: 0.2 });
      run.advance();
      const before = expressionGeneration();
      retainExpressions();
      releaseExpressions();
      expect(expressionGeneration()).toBeGreaterThan(before);
      run.advance();
      const calls = bind.mock.contexts.filter((path) =>
        (path as unknown as { expression: string }).expression === upper);
      expect(calls).toHaveLength(2);
      expect(calls[1]).not.toBe(calls[0]);
      expect(run.state().feed).toBe(18);
    } finally {
      bind.mockRestore();
    }
  });

  it('evicts a reused Bound path when a later prescribed sample errors', () => {
    const run = new Run(bench({
      coordinates: { feed: input(20), 'plug.turn': coordinate(30) },
      edges: [],
      spans: { 'plug.turn': { high: { expression: '(90 + (0 * feed))' } } },
      sources: { feed: ['feed'], 'plug.turn': [] },
    }), 0.1, 8);
    run.move('feed', { by: -2, duration: 0.2 });
    run.advance();
    const cache = (run as unknown as { boundPaths: Map<unknown, unknown> }).boundPaths;
    expect(cache.size).toBe(1);
    const failure = new Error('sample failed');
    const at = vi.spyOn(ExpressionPath.prototype, 'at').mockImplementation(
      () => { throw failure; });
    try {
      expect(() => run.advance()).toThrow(failure);
      expect(cache.size).toBe(0);
    } finally {
      at.mockRestore();
    }
  });

  it('falls back to generic evaluation for a ternary searched bound', () => {
    const program = bench({
      coordinates: { feed: input(20), 'plug.turn': coordinate(30) },
      edges: [],
      spans: { 'plug.turn': {
        high: { expression: '(feed >= 17.95 ? 90 : 0)' },
      } },
      sources: { feed: ['feed'], 'plug.turn': [] },
    });
    expect(program.constraints.get('plug.turn:high')?.reads).toContain('feed');
    const run = new Run(program, 0.1, 8);
    const bind = vi.spyOn(ExpressionPath.prototype, 'bind');
    try {
      const handle = run.move('feed', { by: -5, duration: 0.1 });
      run.advance();
      expect(bind.mock.results.some(result => result.type === 'throw'
        && result.value instanceof UnsupportedPathNode)).toBe(true);
      expect(handle.status).toBe('completed');
      expect(handle.admitted).toBe(-5);
      expect(run.state().feed).toBe(15);
    } finally {
      bind.mockRestore();
    }
  });

  it('does not evaluate a dead throwing branch before ternary fallback', () => {
    const program = bench({
      coordinates: { feed: input(20), 'plug.turn': coordinate(30) },
      edges: [],
      spans: { 'plug.turn': {
        high: { expression: '(feed ? 90 : missing())' },
      } },
      sources: { feed: ['feed'], 'plug.turn': [] },
    });
    expect(program.constraints.get('plug.turn:high')?.reads).toContain('feed');
    const run = new Run(program, 0.1, 8);
    const handle = run.move('feed', { by: -5, duration: 0.1 });
    expect(() => run.advance()).not.toThrow();
    expect(handle.status).toBe('completed');
    expect(handle.admitted).toBe(-5);
    expect(run.state().feed).toBe(15);
  });

  it('does not turn while a pin crosses (the static-reads path)', () => {
    const run = new Run(gate(), 0.1, 8);
    const handle = run.move('twist', { by: 30, duration: 0.1 });
    run.advance();

    expect(run.state()['plug.turn']).toBe(0);
    expect(run.state().twist).toBe(0);
    expect(handle.status).toBe('blocked');
    expect(handle.admitted).toBe(0);
    expect(run.commands()).toEqual([]);
    expect(run.stops()).toHaveLength(1);
    const stop = run.stops()[0];
    expect(stop.coordinate).toBe('plug.turn');
    expect(stop.bound).toBe('high');
    expect(stop.value).toBe(0);
    expect(stop.t).toBe(0);
    expect(stop.inputs).toEqual(['twist']);
  });

  it('turns once every pin clears', () => {
    const run = new Run(gate(), 0.1, 8);
    const seat = run.move('feed', { to: 20, duration: 0.4 });
    ticks(run, 4);
    expect(seat.status).toBe('completed');
    expect(run.stops()).toEqual([]);

    const handle = run.move('twist', { by: 30, duration: 0.1 });
    run.advance();
    expect(run.state()['plug.turn']).toBeCloseTo(30, 9);
    expect(handle.status).toBe('completed');
    expect(handle.admitted).toBeCloseTo(30, 9);
    expect(run.stops()).toEqual([]);
  });

  it('admits insertion and refuses turning in one tick', () => {
    const run = new Run(gate(), 0.1, 8);
    const feed = run.move('feed', { by: 10, duration: 0.1 });
    const turn = run.move('twist', { by: 30, duration: 0.1 });
    run.advance();

    expect(run.state()['key.travel']).toBeCloseTo(20, 9);
    expect(run.state()['plug.turn']).toBe(0);
    expect(feed.status).toBe('completed');
    expect(feed.admitted).toBeCloseTo(10, 9);
    expect(turn.status).toBe('blocked');
    expect(turn.admitted).toBe(0);

    const again = run.move('twist', { by: 30, duration: 0.1 });
    run.advance();
    expect(again.status).toBe('completed');
    expect(run.state()['plug.turn']).toBeCloseTo(30, 9);
  });

  it('stops the key withdrawing from a turned plug (the sampled path)',
     () => {
    const run = new Run(gate(), 0.1, 8);
    run.move('feed', { to: 20, duration: 0.4 });
    ticks(run, 4);
    run.move('twist', { by: 30, duration: 0.1 });
    run.advance();
    expect(run.state()['plug.turn']).toBeCloseTo(30, 9);
    const seen = run.stops().length;

    const handle = run.move('feed', { by: -5, duration: 0.1 });
    run.advance();

    // The plug stands where it stood; the KEY is stopped where the
    // second pin leaves the window.
    expect(run.state()['plug.turn']).toBeCloseTo(30, 9);
    const travel = run.state()['key.travel'];
    expect(travel).toBeGreaterThanOrEqual(17.95);
    expect(travel).toBeLessThanOrEqual(17.95 + 5.0e-11);
    expect(handle.status).toBe('blocked');
    expect(handle.admitted).toBeCloseTo(travel - 20, 9);

    const stop = run.stops()[seen];
    expect(stop.coordinate).toBe('plug.turn');
    expect(stop.bound).toBe('high');
    // The bound EVALUATED at the committed state, not the 30 the
    // coordinate holds.
    expect(stop.value).toBe(90);
    expect(stop.t).toBeCloseTo(0.41, 9);
    expect(stop.inputs).toEqual(['feed']);
  });

  it('admits the same travel at any cadence', () => {
    const found: [number, number, string][] = [];
    for (const count of [1, 4, 40]) {
      const run = new Run(gate(), 0.1, 64);
      run.move('feed', { to: 20, duration: 0.4 });
      ticks(run, 4);
      run.move('twist', { by: 30, duration: 0.1 });
      run.advance();
      const handle = run.move('feed', { by: -5, duration: 0.1 * count });
      ticks(run, count);
      found.push([run.state()['key.travel'], handle.admitted, handle.status]);
    }
    for (const [travel, admitted, status] of found) {
      expect(status).toBe('blocked');
      expect(travel).toBeCloseTo(found[0][0], 9);
      expect(admitted).toBeCloseTo(found[0][1], 9);
    }
  });

  it('replays a constraint stop identically from a snapshot', () => {
    const run = new Run(gate(), 0.1, 8);
    run.move('feed', { to: 20, duration: 0.4 });
    ticks(run, 4);
    run.move('twist', { by: 30, duration: 0.1 });
    run.advance();
    const taken = run.snapshot();

    const blocked = (): [number, number, StopRecord] => {
      const handle = run.move('feed', { by: -5, duration: 0.1 });
      run.advance();
      const stops = run.stops();
      return [run.state()['key.travel'], handle.admitted,
              stops[stops.length - 1]];
    };

    const first = blocked();
    run.restore(taken);
    const second = blocked();
    expect(first[0]).toBe(second[0]);
    expect(first[1]).toBe(second[1]);
    expect(first[2].coordinate).toBe(second[2].coordinate);
    expect(first[2].value).toBe(second[2].value);
    expect(first[2].t).toBe(second[2].t);
    expect(first[2].inputs).toEqual(second[2].inputs);
  });
});

describe('the Captured gate: the key held by the turned plug', () => {
  it('stops the key at once', () => {
    const run = new Run(gate(true), 0.1, 8);
    run.move('twist', { by: 30, duration: 0.1 });
    run.advance();
    expect(run.state()['plug.turn']).toBeCloseTo(30, 9);
    const seen = run.stops().length;

    const handle = run.move('feed', { by: -5, duration: 0.1 });
    run.advance();

    expect(run.state()['key.travel']).toBe(20);
    expect(handle.status).toBe('blocked');
    expect(handle.admitted).toBe(0);
    const stop = run.stops()[seen];
    expect(stop.coordinate).toBe('key.travel');
    expect(stop.bound).toBe('low');
    expect(stop.value).toBe(20);
    expect(stop.t).toBe(0);
    expect(stop.inputs).toEqual(['feed']);
  });

  it('returns the plug and refuses the withdrawal in one tick', () => {
    const run = new Run(gate(true), 0.1, 8);
    run.move('twist', { by: 30, duration: 0.1 });
    run.advance();

    const back = run.move('twist', { by: -30, duration: 0.1 });
    const out = run.move('feed', { by: -5, duration: 0.1 });
    run.advance();

    expect(run.state()['plug.turn']).toBeCloseTo(0, 9);
    expect(back.status).toBe('completed');
    expect(run.state()['key.travel']).toBe(20);
    expect(out.status).toBe('blocked');
    expect(out.admitted).toBe(0);

    const again = run.move('feed', { by: -5, duration: 0.1 });
    run.advance();
    expect(again.status).toBe('completed');
    expect(run.state()['key.travel']).toBeCloseTo(15, 9);
  });
});

/** `PawlRatchet`: the last seated tooth, lifted out of the way by a
 * second coordinate. The tooth is the COMMITTED arbor's and the pawl's
 * lift is read along the tick's path. */
function pawlRatchet(): LoadedProgram {
  return bench({
    coordinates: {
      arbor: input(40), hoist: input(0),
      'pawl.lift': coordinate(0), 'wheel.turn': coordinate(40),
    },
    edges: [
      law(['arbor'], ['wheel.turn'], 'arbor', 'arbor drives wheel.turn'),
      law(['hoist'], ['pawl.lift'], 'hoist', 'hoist drives pawl.lift'),
    ],
    spans: {
      'wheel.turn': {
        low: {
          expression:
            '((36 * floor((wheel.turn / 36))) - (1000 * (pawl.lift >= 1)))',
        },
        high: null,
      },
    },
    sources: {
      arbor: ['arbor'], hoist: ['hoist'],
      'wheel.turn': ['arbor'], 'pawl.lift': ['hoist'],
    },
  });
}

describe('the PawlRatchet: a committed tooth and an along-path pawl', () => {
  it('releases the reverse when the pawl clears early', () => {
    const run = new Run(pawlRatchet(), 0.1, 8);
    const arbor = run.move('arbor', { by: -10, duration: 0.1 });
    run.move('hoist', { by: 10 / 3, duration: 0.1 });
    run.advance();

    expect(run.state()['wheel.turn']).toBeCloseTo(30, 9);
    expect(arbor.status).toBe('completed');
    expect(arbor.admitted).toBeCloseTo(-10, 9);
    expect(run.stops()).toEqual([]);
  });

  it('does not when the pawl clears late', () => {
    const run = new Run(pawlRatchet(), 0.1, 8);
    const arbor = run.move('arbor', { by: -10, duration: 0.1 });
    run.move('hoist', { by: 2.0, duration: 0.1 });
    run.advance();

    expect(run.state()['wheel.turn']).toBeCloseTo(36.0, 9);
    expect(arbor.status).toBe('blocked');
    expect(arbor.admitted).toBeCloseTo(-4.0, 9);
    expect(run.stops()).toHaveLength(1);
    const stop = run.stops()[0];
    expect(stop.coordinate).toBe('wheel.turn');
    expect(stop.bound).toBe('low');
    expect(stop.value).toBe(36.0);
    expect(stop.t).toBeCloseTo(0.4, 9);
  });
});

describe('a quiet bound costs nothing', () => {
  it('takes no sample when nothing the constraint depends on moves', () => {
    const program = gate();
    const run = new Run(program, 0.1, 8);
    const probe = run as unknown as {
      searchedConstraint: (...args: unknown[]) => unknown;
    };
    const sampled = vi.spyOn(probe, 'searchedConstraint');
    // `feed` moves the pins, which the bound reads: this tick samples.
    run.move('feed', { by: 1, duration: 0.1 });
    run.advance();
    expect(sampled).toHaveBeenCalled();

    // Nothing this constraint depends on moves now: `plug.turn` stands
    // and so do both lifts, so `boundsNow` alone touches the
    // expression -- and it does not, because a constraint side is never
    // evaluated there.
    sampled.mockClear();
    run.advance();
    expect(sampled).not.toHaveBeenCalled();
    expect(run.stops()).toEqual([]);
    sampled.mockRestore();
  });

  it('leaves a coordinate standing outside its bound free', () => {
    // The plug is turned while the pins are clear, then the key is
    // withdrawn far enough to close the window: `plug.turn` stands
    // outside its (now zero) bound and is not dragged back.
    const run = new Run(gate(), 0.1, 16);
    run.move('feed', { to: 20, duration: 0.4 });
    ticks(run, 4);
    run.move('twist', { by: 30, duration: 0.1 });
    run.advance();
    const before = run.state()['plug.turn'];
    run.move('feed', { by: -5, duration: 0.1 });
    run.advance();
    // Blocked where the window closes, and the plug has not moved.
    expect(run.state()['plug.turn']).toBe(before);
    // A second, unrelated tick moves nothing: the standing plug is free.
    run.advance();
    expect(run.state()['plug.turn']).toBe(before);
  });
});

describe('one event carrying a numeric stop and a constraint stop', () => {
  it('asserts the invariant after the whole event is committed', () => {
    // `wheel.turn` carries a numeric low bound reached at the same
    // fraction as `plug.turn`'s constraint: the numeric snap mutates
    // `committed`, and the assertion must run after it (design D6).
    const program = bench({
      coordinates: {
        feed: input(10), twist: input(0), spin: input(0),
        'key.travel': coordinate(10),
        'p1.lift': coordinate(5), 'p2.lift': coordinate(5),
        'plug.turn': coordinate(0), 'wheel.turn': coordinate(0),
      },
      edges: [
        law(['feed'], ['key.travel'], 'feed', 'feed drives key.travel'),
        law(['twist'], ['plug.turn'], 'twist', 'twist drives plug.turn'),
        law(['spin'], ['wheel.turn'], 'spin', 'spin drives wheel.turn'),
        law(['key.travel'], ['p1.lift'], pinLift(10),
            'key.travel drives p1.lift', false),
        law(['key.travel'], ['p2.lift'], pinLift(13),
            'key.travel drives p2.lift', false),
      ],
      spans: {
        'plug.turn': { low: 0.0, high: { expression: CLEARED } },
        'wheel.turn': { low: -5.0, high: null },
      },
      sources: {
        feed: ['feed'], twist: ['twist'], spin: ['spin'],
        'key.travel': ['feed'], 'p1.lift': ['feed'], 'p2.lift': ['feed'],
        'plug.turn': ['twist'], 'wheel.turn': ['spin'],
      },
    });
    const run = new Run(program, 0.1, 8);
    // The plug is blocked at t = 0 (the pins are not cleared) and the
    // wheel reaches its numeric low bound at t = 0 too, because it
    // starts there.
    const turn = run.move('twist', { by: 30, duration: 0.1 });
    const spin = run.move('spin', { by: -10, duration: 0.1 });
    run.advance();

    expect(run.state()['plug.turn']).toBe(0);
    expect(run.state()['wheel.turn']).toBe(-5);
    expect(turn.status).toBe('blocked');
    expect(spin.status).toBe('blocked');
    const kinds = run.stops().map((stop) => `${stop.coordinate}:${stop.bound}`);
    expect(kinds).toContain('plug.turn:high');
    expect(kinds).toContain('wheel.turn:low');
  });
});

describe('the sub-program pass is the segment arithmetic (design D4)', () => {
  it('takes a jumping law inside the sub-program over the truncated path',
     () => {
    // `gate.lift` is driven by a law that JUMPS: it steps to 1 when the
    // hoist passes 2. The bound reads `gate.lift`, so the level at each
    // sample is one pass over that law's PLAN truncated at `t` -- the
    // same arithmetic the segment is later committed by.
    const program = bench({
      coordinates: {
        hoist: input(0), crank: input(0),
        'gate.lift': coordinate(0), 'arm.turn': coordinate(0),
      },
      edges: [
        {
          kind: 'law', needs: ['hoist'], gives: ['gate.lift'],
          description: 'hoist drives gate.lift', stated_by: 'Bench',
          expressions: ['(hoist * (hoist >= 2))'], affine: [false],
          plans: [{
            skeleton: '(hoist * _j0)',
            jumps: [{
              name: '_j0', primitive: '>=', level: '(hoist - 2)',
              affine: true,
            }],
          }],
        },
        law(['crank'], ['arm.turn'], 'crank', 'crank drives arm.turn'),
      ],
      spans: {
        'arm.turn': { low: null, high: { expression: '(90 * (gate.lift < 1))' } },
      },
      sources: {
        hoist: ['hoist'], crank: ['crank'],
        'gate.lift': ['hoist'], 'arm.turn': ['crank'],
      },
    });
    const run = new Run(program, 0.1, 8);
    // The hoist crosses the surface at t = 0.5 of the tick, from which
    // point `gate.lift` follows it; it reaches 1 at t = 0.75, which is
    // where the arm's bound closes.
    run.move('hoist', { by: 4, duration: 0.1 });
    const turn = run.move('crank', { by: 90, duration: 0.1 });
    run.advance();

    expect(turn.status).toBe('blocked');
    // The arm stopped at the fraction the PLAN's truncated path gives,
    // not at either end of the stretch.
    const stop = run.stops()[0];
    expect(stop.coordinate).toBe('arm.turn');
    expect(stop.bound).toBe('high');
    expect(stop.t).toBeGreaterThan(0.74);
    expect(stop.t).toBeLessThanOrEqual(0.75);
    expect(run.state()['arm.turn']).toBeCloseTo(90 * stop.t, 9);
  });

  it('stops the input that carries the level outward and frees the one '
     + 'that relieves it', () => {
    // The plug stands turned with the key seated, and ONE tick moves
    // the key out (which closes the window: outward) while an unrelated
    // input runs. Only `feed` is in the group.
    const run = new Run(gate(), 0.1, 16);
    run.move('feed', { to: 20, duration: 0.4 });
    ticks(run, 4);
    run.move('twist', { by: 30, duration: 0.1 });
    run.advance();

    const out = run.move('feed', { by: -5, duration: 0.1 });
    // `twist` moving the plug BACK relieves the high bound: level(1) is
    // below level(0), so it is not stopped.
    const back = run.move('twist', { by: -5, duration: 0.1 });
    run.advance();

    expect(out.status).toBe('blocked');
    expect(back.status).toBe('completed');
    expect(run.stops()[run.stops().length - 1].inputs).toEqual(['feed']);
  });
});

// ---------------------------------------------------------------------
// A law that READS THE COORDINATE IT DRIVES: the framework's own
// `Clearing` and `StoppedClearing`, reproduced as benches (design D2,
// D4, D5, tasks 5 and 6). Every number below is the framework's own --
// `tests/running_project/machine.py`'s `GAP = 0.5`,
// `STATION = (100.0, 500.0)`, the dial resting at 108 -- and the
// published document for the same machine is in the conformance corpus.
// ---------------------------------------------------------------------

/** `missing_tooth`, published: the setter turns the dial directly, and
 * the ring turns it only while the rack's station reaches it AND the
 * dial is not already standing in its missing-tooth gap. */
const CLEARING_EDGE = {
  kind: 'law',
  needs: ['setter', 'ring', 'wheel.turn'],
  gives: ['wheel.turn'],
  description: '(setter, ring, wheel.turn) drives wheel.turn',
  stated_by: 'Clearing',
  expressions: [
    '(setter + ((ring * (floor(((ring - 100.0) / 400.0)) == 0)) * '
    + '((((wheel.turn + 0.5) - (360.0 * floor(((wheel.turn + 0.5) '
    + '/ 360.0)))) - 1.0) >= 0.0)))',
  ],
  affine: [true],
  plans: [{
    skeleton: '(setter + ((ring * _j1) * _j3))',
    jumps: [
      { name: '_j0', primitive: 'floor', level: '((ring - 100.0) / 400.0)',
        affine: true },
      { name: '_j1', primitive: '==', level: '(_j0 - 0)', affine: true },
      { name: '_j2', primitive: 'floor',
        level: '((wheel.turn + 0.5) / 360.0)', affine: true },
      { name: '_j3', primitive: '>=',
        level: '(((wheel.turn + 0.5) - (360.0 * _j2)) - 1.0)', affine: true },
    ],
  }],
};

const GAP = 0.5;

function clearingRun(dt = 0.05, rest = 108, ringRest = 0,
                     spec: Record<string, unknown> = {}): Run {
  const program = bench({
    coordinates: {
      setter: input(0), ring: input(ringRest),
      'wheel.turn': coordinate(rest),
    },
    edges: [CLEARING_EDGE],
    sources: {
      setter: ['setter'], ring: ['ring'], 'wheel.turn': ['ring', 'setter'],
    },
    ...spec,
  });
  return new Run(program, dt, 400);
}

/** Whether the published gate reads DISENGAGED at `value`, by this
 * viewer's own arithmetic rather than by a tolerance. */
function disengaged(value: number): boolean {
  const shifted = value + GAP;
  return shifted - 360 * Math.floor(shifted / 360) < 2 * GAP;
}

describe('a law that reads the coordinate it drives (tasks 6)', () => {
  it('6.1 loads with the shape the framework publishes', () => {
    const run = clearingRun();
    const edge = run.state !== undefined
      ? (run as unknown as { program: LoadedProgram }).program.edges[0]
      : null;
    expect(edge!.needs).toEqual(['setter', 'ring', 'wheel.turn']);
    expect(edge!.gives).toEqual(['wheel.turn']);
    expect(edge!.retained).toHaveLength(1);
    expect(edge!.retained[0]!.own).toBe('wheel.turn');
    expect(run.state()['wheel.turn']).toBe(108);
  });

  it('6.2 the dial clears to its gap and the RING RUNS ON', () => {
    const run = clearingRun();
    const command = run.move('ring', { by: 600, duration: 0.25 });
    for (let tick = 0; tick < 8; tick += 1) run.advance();
    const dial = run.state()['wheel.turn'];
    // Within the band half-width of a full turn, in the sweep's own
    // direction, at a value the published gate reads DISENGAGED.
    expect(Math.abs(dial - 360)).toBeLessThanOrEqual(GAP);
    expect(dial).toBeLessThan(360);
    expect(disengaged(dial)).toBe(true);
    // The ring completed its whole travel even so.
    expect(run.state().ring).toBeCloseTo(600, 9);
    expect(command.status).toBe('completed');
    // One crossing, in the crossing record, and NO stop.
    expect(run.crossings().filter(
      (one) => one.coordinate === 'wheel.turn' && one.primitive === 'floor',
    ).length).toBeGreaterThanOrEqual(1);
    expect(run.stops()).toEqual([]);
  });

  it('6.3 a second and a third sweep move the dial by NOTHING -- the same '
     + 'float, bit for bit', () => {
    const run = clearingRun();
    run.move('ring', { by: 600, duration: 0.25 });
    for (let tick = 0; tick < 8; tick += 1) run.advance();
    const cleared = run.state()['wheel.turn'];
    for (const sweep of [2, 3]) {
      const command = run.move('ring', { by: 600, duration: 0.25 });
      for (let tick = 0; tick < 8; tick += 1) run.advance();
      expect(Object.is(run.state()['wheel.turn'], cleared)).toBe(true);
      expect(command.status).toBe('completed');
      void sweep;
    }
    expect(run.stops()).toEqual([]);
  });

  it('6.4 swept BACKWARD from inside the station the dial ends on the '
     + 'band\'s UPPER edge and does not move again', () => {
    // The ring RESTS inside its station, so the approach itself turns
    // nothing: the dial stands at 108 with the gate engaged.
    const run = clearingRun(0.05, 108, 300);
    run.move('ring', { by: -250, duration: 0.25 });
    for (let tick = 0; tick < 8; tick += 1) run.advance();
    const dial = run.state()['wheel.turn'];
    expect(disengaged(dial)).toBe(true);
    // The UPPER edge of the band, which is the first value BELOW `GAP`
    // at which the gate disengages.
    expect(dial).toBeLessThan(GAP);
    expect(dial).toBeGreaterThan(GAP - 1e-12);
    const stood = dial;
    run.move('ring', { to: 300, duration: 0.1 });
    for (let tick = 0; tick < 4; tick += 1) run.advance();
    run.move('ring', { by: -250, duration: 0.25 });
    for (let tick = 0; tick < 8; tick += 1) run.advance();
    expect(Object.is(run.state()['wheel.turn'], stood)).toBe(true);
  });

  it('6.5 a dial standing EXACTLY at a band edge holds in the direction '
     + 'that takes it deeper and turns in the one that leaves', () => {
    // At `wheel.turn == 0.5` the gate's level is exactly zero: `>=`
    // reads ENGAGED there, and rule (c) decides the piece by where the
    // level GOES.
    const forward = clearingRun(0.05, GAP, 200);
    forward.move('ring', { by: 50, duration: 0.05 });
    forward.advance();
    // Leaving the band: the dial turns with the ring.
    expect(forward.state()['wheel.turn']).toBe(GAP + 50);

    const backward = clearingRun(0.05, GAP, 200);
    const stood = backward.state()['wheel.turn'];
    expect(stood).toBe(GAP);
    backward.move('ring', { by: -50, duration: 0.05 });
    backward.advance();
    // Deeper into the band: the dial holds, bit for bit.
    expect(Object.is(backward.state()['wheel.turn'], stood)).toBe(true);
  });

  it('6.6 the same sweep at one tick, twelve and two hundred and forty '
     + 'agrees within the run\'s agreement window', () => {
    const answers = [1, 12, 240].map((ticks) => {
      const run = clearingRun(0.25 / ticks);
      const command = run.move('ring', { by: 600, duration: 0.25 });
      for (let tick = 0; tick < ticks * 4; tick += 1) run.advance();
      expect(command.status).toBe('completed');
      expect(run.stops()).toEqual([]);
      return run.state()['wheel.turn'];
    });
    for (const answer of answers) {
      expect(Math.abs(answer - answers[0]))
        .toBeLessThanOrEqual(1e-9 * Math.max(1, Math.abs(answer)));
      expect(disengaged(answer)).toBe(true);
    }
  });

  it('6.7 a run state taken after a partial sweep and restored resumes '
     + 'from the same float and reaches the same band edge', () => {
    const run = clearingRun();
    run.move('ring', { by: 600, duration: 0.25 });
    run.advance();
    run.advance();
    const taken = run.snapshot();
    const midway = run.state()['wheel.turn'];
    for (let tick = 0; tick < 6; tick += 1) run.advance();
    const reached = run.state()['wheel.turn'];

    run.restore(taken);
    expect(Object.is(run.state()['wheel.turn'], midway)).toBe(true);
    for (let tick = 0; tick < 6; tick += 1) run.advance();
    expect(Object.is(run.state()['wheel.turn'], reached)).toBe(true);
  });

  it('6.8 `StoppedClearing`: one segment reports BOTH a landing and a '
     + 'bound on the same coordinate, and the BOUND wins', () => {
    const program = bench({
      coordinates: {
        setter: input(0), ring: input(0), gauge_in: input(0),
        'wheel.turn': coordinate(108), 'gauge.turn': coordinate(0),
      },
      edges: [
        CLEARING_EDGE,
        { kind: 'wiring', needs: ['gauge_in'], gives: ['gauge.turn'],
          description: 'gauge_in drives gauge.turn', stated_by:
          'StoppedClearing', factor: 1.0 },
      ],
      spans: {
        'wheel.turn': { low: null, high: 400.0 },
        'gauge.turn': { low: null, high: 40.0 },
      },
      sources: {
        setter: ['setter'], ring: ['ring'], gauge_in: ['gauge_in'],
        'wheel.turn': ['ring', 'setter'], 'gauge.turn': ['gauge_in'],
      },
    });
    const run = new Run(program, 0.05, 400);
    run.move('ring', { by: 600, duration: 0.25 });
    run.move('gauge_in', { by: 100, duration: 0.25 });
    run.move('setter', { by: 100, duration: 0.25 });
    run.advance();
    run.advance();
    let seen = run.stops().length;
    run.advance();

    // The framework's own third tick, to the digit.
    const bank = run.state();
    expect(bank['wheel.turn']).toBe(400);
    expect(bank['gauge.turn']).toBe(40);
    expect(bank.ring).toBeCloseTo(341.1428571428571, 9);
    expect(bank.setter).toBeCloseTo(56.85714285714286, 9);

    const stops = run.stops().slice(seen);
    expect(stops.map((one) => one.coordinate))
      .toEqual(['gauge.turn', 'wheel.turn']);
    expect(stops[0].t).toBe(0);
    expect(stops[0].inputs).toEqual(['gauge_in']);
    expect(stops[1].value).toBe(400);
    expect(stops[1].t).toBeCloseTo(0.8428571428571429, 9);
    expect(stops[1].inputs).toEqual(['ring', 'setter']);
    seen = 0;
  });
});

describe('what the run does with a landing (design D4, D5, tasks 5)', () => {
  // A gate whose surface is NOT a float the tick's own arithmetic
  // reproduces: the dial holds at `11.9`, and `value + delta` from a
  // rest of `3.7` gives `11.899999999999999` -- one ulp BACK TOWARD the
  // surface, which is the ENGAGED side of the gate. That ulp is the
  // whole of what `landed` is for, so it is what these two pin.
  const LOSSY_EDGE = {
    kind: 'law',
    needs: ['ring', 'wheel.turn'],
    gives: ['wheel.turn'],
    description: '(ring, wheel.turn) drives wheel.turn',
    stated_by: 'Bench',
    expressions: [
      '(ring * (1.0 - ((floor((wheel.turn / 1.7)) - 7.0) >= 0.0)))',
    ],
    affine: [true],
    plans: [{
      skeleton: '(ring * (1.0 - _j1))',
      jumps: [
        { name: '_j0', primitive: 'floor', level: '(wheel.turn / 1.7)',
          affine: true },
        { name: '_j1', primitive: '>=', level: '(_j0 - 7.0)', affine: true },
      ],
    }],
  };

  it('5.2 applies the landing after the FULL-STRETCH pass, before the '
     + 'bounds are examined', () => {
    const program = bench({
      coordinates: { ring: input(0), 'wheel.turn': coordinate(3.7) },
      edges: [LOSSY_EDGE],
      sources: { ring: ['ring'], 'wheel.turn': ['ring'] },
    });
    const run = new Run(program, 0.25, 400);
    run.move('ring', { to: 100, duration: 0.25 });
    run.advance();
    // The float the WALK left it at, not the starting value plus the
    // increment: `3.7 + (11.9 - 3.7)` is `11.899999999999999`, which
    // reads ENGAGED.
    expect(run.state()['wheel.turn']).toBe(11.9);
    expect(3.7 + (11.9 - 3.7)).toBe(11.899999999999999);
    expect(Math.floor(11.899999999999999 / 1.7)).toBe(6);
    // And so a further sweep moves it by nothing at all.
    run.move('ring', { to: 200, duration: 0.25 });
    run.advance();
    expect(run.state()['wheel.turn']).toBe(11.9);
  });

  it('5.2 applies the landing after the SEGMENT pass too -- the place a '
     + 'later stretch cannot quietly put right', () => {
    const program = bench({
      coordinates: {
        ring: input(0), 'shaft.turn': coordinate(0),
        'wheel.turn': coordinate(3.7),
      },
      edges: [
        { kind: 'wiring', needs: ['ring'], gives: ['shaft.turn'],
          description: 'ring drives shaft.turn', stated_by: 'Bench',
          factor: 1.0 },
        LOSSY_EDGE,
      ],
      // A shaft the RING drives, bounded, and reaching its bound AFTER
      // the dial has landed: the stop blocks the ring for the rest of
      // the tick, so the segment's landing is what the tick commits and
      // no later stretch can land it a second time.
      spans: { 'shaft.turn': { low: null, high: 60.0 } },
      sources: {
        ring: ['ring'], 'shaft.turn': ['ring'], 'wheel.turn': ['ring'],
      },
    });
    const run = new Run(program, 0.25, 400);
    const command = run.move('ring', { to: 100, duration: 0.25 });
    run.advance();
    expect(run.stops().map((one) => one.coordinate)).toEqual(['shaft.turn']);
    expect(run.stops()[0].t).toBeCloseTo(0.6, 12);
    expect(run.stops()[0].inputs).toEqual(['ring']);
    expect(run.state()['shaft.turn']).toBe(60);
    expect(command.status).toBe('blocked');
    expect(run.state()['wheel.turn']).toBe(11.9);
  });

  it('5.3 a tick that fails AFTER a cut commits nothing -- not the '
     + 'landing, not the crossing, not the bank', () => {
    const program = bench({
      coordinates: {
        setter: input(0), ring: input(0), 'wheel.turn': coordinate(108),
      },
      edges: [
        CLEARING_EDGE,
        // A second law determining the same coordinate, disagreeing.
        law(['setter'], ['wheel.turn'], '(setter * 7.0)',
            'a second opinion about wheel.turn'),
      ],
      sources: {
        setter: ['setter'], ring: ['ring'], 'wheel.turn': ['ring', 'setter'],
      },
    });
    const run = new Run(program, 0.25, 400);
    const command = run.move('ring', { to: 600, duration: 0.25 });
    expect(() => run.advance()).toThrow(/wheel\.turn/);
    expect(run.state()['wheel.turn']).toBe(108);
    expect(run.state().ring).toBe(0);
    expect(run.tick()).toBe(0);
    expect(run.crossings()).toEqual([]);
    expect(run.stops()).toEqual([]);
    expect(command.status).toBe('refused');
  });

  it('5.3 `refusalKind` maps the landing invariant to its own kind, not '
     + 'to a broken STOP invariant', () => {
    expect(refusalKind(new LandingInvariantError('nowhere'))).toBe('landing');
    expect(refusalKind(new StopInvariantError('runaway'))).toBe('stop');
  });

  it('5.4 a self-read crossing is recorded as a CROSSING and never as a '
     + 'stop, and stops no input', () => {
    const run = clearingRun();
    const command = run.move('ring', { by: 600, duration: 0.25 });
    for (let tick = 0; tick < 8; tick += 1) run.advance();
    expect(run.stops()).toEqual([]);
    expect(command.status).toBe('completed');
    const mine = run.crossings().filter(
      (one) => one.coordinate === 'wheel.turn');
    expect(mine.length).toBeGreaterThan(0);
    for (const one of mine) {
      expect(one.relation)
        .toBe('(setter, ring, wheel.turn) drives wheel.turn');
      expect(['floor', '==', '>=']).toContain(one.primitive);
      expect(one.t).toBeGreaterThanOrEqual(0);
      expect(one.t).toBeLessThanOrEqual(1);
    }
  });
});

// ---------------------------------------------------------------------
// A BLOCK in the run (design D4, D6, tasks 8-9). The documents are the
// framework's own, out of the conformance corpus: the numbers below are
// the producer's and are never recomputed a second way here.
// ---------------------------------------------------------------------

/** One corpus machine's published document, by name, with the bank's
 * rest values optionally overridden -- `Sim(klass, state={...})`. */
function corpusRun(name: string, dt: number,
                   state: Record<string, number> = {}): Run {
  const found = (corpus as unknown as {
    machines: { name: string; document: unknown }[];
  }).machines.find((one) => one.name === name)!;
  const document = JSON.parse(JSON.stringify(found.document));
  for (const [id, value] of Object.entries(state)) {
    document.program.coordinates[id].initial = value;
    if (document.drivers[id] !== undefined) {
      document.drivers[id].default = value;
    }
  }
  return new Run(loadProgram(document as RunDocument, `corpus://${name}`),
                 dt, 16);
}

describe('a block in the run (design D4, D6, tasks 8-9)', () => {
  it('commits exact terminal paths through the published cyclic block', () => {
    const run = corpusRun('ShiftedCarry', 1, { shift: 0 });
    run.move('crank', { to: -4.9425 });
    const probe = run as unknown as { pass: (...args: unknown[]) => Record<string, number> };
    const original = probe.pass.bind(run);
    let ends = new Map<string, number>();
    const spy = vi.spyOn(probe, 'pass').mockImplementation((...args) => {
      const result = original(...args);
      ends = new Map([...propagations.get(args[1] as Record<string, number>)!.motions]
        .map(([key, motion]) => [key, motion.end]));
      return result;
    });
    expect(run.move('crank', { to: 3.9075 }).status).toBe('completed');
    spy.mockRestore();
    for (const key of ['lower.turn', 'higher.turn', 'carry.travel']) {
      if (ends.has(key)) expect(run.state()[key]).toBe(ends.get(key));
    }
  });

  it('commits a terminal endpoint from a minimal selected cyclic block', () => {
    const program = bench({
      coordinates: { feed: input(0), shift: input(0), a: coordinate(0), b: coordinate(0) },
      edges: [
        { kind: 'law', needs: ['feed', 'shift', 'b'], gives: ['a'],
          description: 'feed drives a', stated_by: 'Bench',
          expressions: ['(feed + (b * (shift > 0)))'], affine: [true],
          plans: [{ skeleton: '(feed + (b * _j0))', jumps: [
            { name: '_j0', primitive: '>', level: 'shift', affine: true },
          ] }] },
        law(['a'], ['b'], 'a', 'a drives b'),
      ],
    });
    expect(program.edges.some(edge => edge.kind === 'block')).toBe(true);
    const run = new Run(program, 1, 8);
    run.move('feed', { to: -4.9425 });
    const probe = run as unknown as { pass: (...args: unknown[]) => Record<string, number> };
    const original = probe.pass.bind(run);
    let ends = new Map<string, number>();
    const spy = vi.spyOn(probe, 'pass').mockImplementation((...args) => {
      const result = original(...args);
      ends = new Map([...propagations.get(args[1] as Record<string, number>)!.motions]
        .map(([key, motion]) => [key, motion.end]));
      return result;
    });
    expect(run.move('feed', { to: 3.9075 }).status).toBe('completed');
    spy.mockRestore();
    expect(run.state().a).toBe(ends.get('a'));
    expect(run.state().b).toBe(ends.get('b'));
  });

  it('does not terminal-snap a block output through an inactive source branch', () => {
    const program = bench({
      coordinates: {
        feed: input(-4.9425), other: input(-4.9425), shift: input(0),
        a: coordinate(-4.9425), b: coordinate(-4.9425),
      },
      edges: [
        { kind: 'law', needs: ['feed', 'other', 'shift', 'b'], gives: ['a'],
          description: 'selected other drives a', stated_by: 'Bench',
          expressions: ['(other + ((feed + b) * (shift > 0)))'], affine: [true],
          plans: [{ skeleton: '(other + ((feed + b) * _j0))', jumps: [
            { name: '_j0', primitive: '>', level: 'shift', affine: true },
          ] }] },
        law(['a'], ['b'], 'a', 'a drives b'),
      ],
    });
    expect(program.edges.some(edge => edge.kind === 'block')).toBe(true);
    const run = (absolute: boolean): Record<string, number> => {
      const engine = new Run(program, 1, 8);
      const delta = 3.9075 - -4.9425;
      engine.move('feed', absolute ? { to: 3.9075, duration: 1 }
        : { by: delta, duration: 1 });
      engine.move('other', { by: delta, duration: 1 });
      engine.advance();
      return engine.state();
    };
    const absolute = run(true);
    const relative = run(false);
    expect(absolute.feed).toBe(3.9075);
    expect(absolute.a).toBe(relative.a);
    expect(absolute.b).toBe(relative.b);
  });
  it('9.2 the selected machine equals its FROZEN TWIN: `ShiftedCarry` '
     + 'cranked by 2.0 over 12 ticks of dt = 1/12', () => {
    // The producer's own numbers for THIS document, measured at
    // machinome `0b0f02a`:
    //   Sim(ShiftedCarry(), dt=1/12, state={'shift': s});
    //   move('crank', by=2.0, duration=1.0); run(1/12) x 12
    //   s = 0 -> carry.travel 1.0, crank 2.0, higher.turn 1.5,
    //            lower.turn 2.0
    //   s = 1 -> carry.travel 1.0, crank 2.0, higher.turn 2.0,
    //            lower.turn 0.0
    // The selected machine is its frozen twin: at position 0 the lever
    // is what advances the higher wheel, and it does so for three
    // quarters of the crank's travel; at position 1 the crank turns the
    // higher wheel itself and the lower one does not move at all.
    for (const [shift, expected] of [
      [0, { 'lower.turn': 2.0, 'higher.turn': 1.5, 'carry.travel': 1.0 }],
      [1, { 'lower.turn': 0.0, 'higher.turn': 2.0, 'carry.travel': 1.0 }],
    ] as [number, Record<string, number>][]) {
      const run = corpusRun('ShiftedCarry', 1 / 12, { shift });
      run.move('crank', { by: 2, duration: 1.0 });
      for (let tick = 0; tick < 12; tick += 1) run.advance();
      const state = run.state();
      expect(state.shift).toBe(shift);
      expect(state.crank).toBe(2);
      for (const [id, value] of Object.entries(expected)) {
        expect(state[id]).toBe(value);
      }
    }
  });

  it('9.3 a SELECTION CHANGE ALONE moves nothing -- exactly the number '
     + 'zero, bit for bit', () => {
    const run = corpusRun('ShiftedCarry', 0.05);
    run.move('crank', { by: 2, duration: 0.2 });
    for (let tick = 0; tick < 8; tick += 1) run.advance();
    const before = { ...run.state() };
    // The carriage alone, across its detent and back.
    run.move('shift', { by: 1, duration: 0.2 });
    for (let tick = 0; tick < 8; tick += 1) run.advance();
    run.move('shift', { by: -1, duration: 0.2 });
    for (let tick = 0; tick < 8; tick += 1) run.advance();
    const after = run.state();
    for (const id of ['lower.turn', 'higher.turn', 'carry.travel']) {
      expect(Object.is(after[id], before[id])).toBe(true);
    }
  });

  it('solves a block stop only from its certified physical path', () => {
    const run = corpusRun('RangedBlock', 0.05);
    const spin = run.move('spin', { by: 2, duration: 0.05 });
    run.move('shift', { by: 1, duration: 0.05 });
    run.advance();
    // The source-timed producer independently gives exactly .3 and .6.
    // The old endpoint executor searched this and returned .3 minus an ulp
    // bracket. The member's published affine flag still proves nothing.
    const stops = run.stops();
    expect(stops).toHaveLength(1);
    expect(stops[0].coordinate).toBe('carry.travel');
    expect(stops[0].t).toBe(0.3);
    expect(stops[0].inputs).toEqual(['spin']);
    expect(run.state()['lower.turn']).toBe(0.6);
    expect(run.state().spin).toBe(0.6);
    expect(spin.status).toBe('blocked');
    expect(spin.admitted).toBe(0.6);
    // And the determination really is the block, with `affine` false.
    const program = (run as unknown as { program: LoadedProgram }).program;
    const where = program.determiner.get('carry.travel')!;
    expect(where.edge.kind).toBe('block');
    expect(where.edge.affine[where.index]).toBe(false);
  });

  it('8.4 an input reaching a stopped block coordinate only through an '
     + 'INACTIVE selection is not stopped and completes its whole '
     + 'travel, while the pushing input retires blocked', () => {
    // The carriage stands ABOVE the detent, where the lever reads the
    // HIGHER wheel, and the lever is already at its bound.
    const run = corpusRun('RangedBlock', 0.05,
                          { shift: 1, 'carry.travel': 0.6 });
    // `spin` reaches the lever only through `lower.turn`, which the
    // selection has switched out: it is not stopped by it.
    const spin = run.move('spin', { by: 2, duration: 0.05 });
    run.advance();
    expect(spin.status).toBe('completed');
    expect(run.state().spin).toBe(2);
    expect(run.state()['lower.turn']).toBe(2);
    expect(run.state()['carry.travel']).toBe(0.6);
    expect(run.stops()).toEqual([]);

    // `crank` reaches it through the term the selection leaves ACTIVE,
    // so it is stopped at once and retires blocked with nothing
    // admitted.
    const crank = run.move('crank', { by: 1, duration: 0.05 });
    run.advance();
    expect(crank.status).toBe('blocked');
    expect(crank.admitted).toBe(0);
    expect(run.stops().map((one) => one.inputs)).toEqual([['crank']]);
    expect(run.state()['carry.travel']).toBe(0.6);
  });
});

// ---------------------------------------------------------------------
// A STOP ON A KINKED DETERMINER (openspec `solve-at-the-kink`, design
// §6 case A, tasks 5.1). The corpus's own `KinkedStop`, asserted as an
// IDENTITY and not within the corpus's comparison window: the producer
// SOLVES this stop at its own kink, and so must this viewer.
//
// The law carries no jump node at all -- `4 + 72 * clamp01((lever -
// 113.5) / 11.25)` -- so `edgeCuts` returned `[]` for it and `locate`
// took the one-division fast path STRAIGHT THROUGH the kink. The trap
// that path falls into is a NUMBER: over the whole tick the coordinate
// runs 4 -> 76, so one division puts the stop at (40 - 4) / 72 = 0.5,
// where the coordinate reaches 40 at t = 0.478125 and is standing on
// its flat piece for the first 0.3375 of the tick. The base did not
// give 0.5 -- it SEARCHED, and landed 9.09e-14 out.
// ---------------------------------------------------------------------

describe('a stop on a kinked determiner (design D4 (c))', () => {
  it('5.1 lands on the producer\'s own fraction EXACTLY', () => {
    const run = corpusRun('KinkedStop', 0.1);
    const command = run.move('lever', { by: 40, duration: 0.1 });
    run.advance();
    const stops = run.stops();
    expect(stops).toHaveLength(1);
    expect(stops[0].coordinate).toBe('slide.travel');
    // The producer's own recorded floats, bit for bit.
    expect(stops[0].t).toBe(0.478125);
    expect(run.state()['slide.travel']).toBe(40);
    expect(run.state().lever).toBe(119.125);
    expect(command.admitted).toBe(19.125);
    expect(command.status).toBe('blocked');
    // ... and NOT the fraction a single division over the whole tick
    // gives.
    expect(stops[0].t).not.toBe(0.5);
  });

  /** A clamp with no jump node at all: `clamp(crank, 0, 100)`, bounded
   * at 40. */
  const clamped = (crank: number, travel: number) => bench({
    coordinates: { crank: input(crank), 'wheel.turn': coordinate(travel) },
    edges: [law(['crank'], ['wheel.turn'], 'min(max(crank, 0.0), 100.0)',
                'crank drives wheel', false)],
    spans: { 'wheel.turn': { low: null, high: 40 } },
  });

  it('5.2 brackets the bound between two BREAKPOINTS and divides', () => {
    // The path starts on the clamp's FLAT piece and reaches the bound on
    // the sloped one: `crank` runs -10 -> 50, so the coordinate holds at
    // 10 until the clamp opens at `t = 10/60` and then runs to 60. A
    // single division over the whole tick would put the stop at
    // (40 - 10) / 50 = 0.6, where the coordinate is still at 34.
    const run = new Run(clamped(-10, 10), 0.05, 64);
    const command = run.move('crank', { by: 60, duration: 0.05 });
    run.advance();
    expect(run.state()['wheel.turn']).toBe(40);
    // The closed form of the fixture's own arithmetic: the breakpoint
    // where the clamp opens, and one division inside the piece that
    // brackets the bound.
    const opens = (0 - -10) / (50 - -10);
    const expected = opens + (1 - opens) * (40 - 10) / (60 - 10);
    expect(run.stops()[0].t).toBe(expected);
    expect(run.stops()[0].t).toBeCloseTo(40 / 60, 12);
    expect(run.stops()[0].t).not.toBe(0.6);
    expect(command.admitted).toBe(60 * expected);
  });

  it('does not classify a block from its members\' static shapes', () => {
    // Only a request's determined path can certify its pieces. The
    // published aggregate still carries no unconditional shape promise.
    const run = corpusRun('RangedBlock', 0.05);
    const block = [...run.program.edges].find(
      (edge) => edge.kind === 'block')!;
    expect(block.shapes.every((shape) => shape === null)).toBe(true);
    expect(block.affine.every((flag) => flag === false)).toBe(true);
  });

  it('5.3 leaves the ONE-DIVISION fast path alone where the tick reaches '
     + 'no kink: empty cuts means affine over the whole tick', () => {
    // The same law driven entirely inside the sloped piece: the path IS
    // affine over the tick, so there are no breakpoints at all and the
    // stop is the single exact division `locate` has always taken.
    const run = new Run(clamped(10, 10), 0.05, 64);
    const command = run.move('crank', { by: 40, duration: 0.05 });
    run.advance();
    expect(run.state()['wheel.turn']).toBe(40);
    expect(run.stops()[0].t).toBe((40 - 10) / 40);
    expect(command.admitted).toBe(30);
  });
});
