/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */
import { describe, expect, it, vi } from 'vitest';
import corpus from '../running-corpus.json';
import { loadProgram } from './program';
import type { RunDocument } from './program';
import { Run } from './run';
import { Motion, propagations } from './motion';

type PrivateRun = Run & {
  blockReuse: Map<object, unknown>;
  pass: (...args: unknown[]) => Record<string, number>;
  deltasOf: (values: Record<string, number>) => Record<string, number>;
};
const privateRun = (run: Run): PrivateRun => run as PrivateRun;

const paths = (run: Run) => {
  const privateSide = privateRun(run);
  const original = privateSide.pass.bind(run);
  const found: Record<string, unknown>[] = [];
  const spy = vi.spyOn(privateSide, 'pass').mockImplementation((...args) => {
    const result = original(...args);
    const trace = propagations.get(args[1] as Record<string, number>)!;
    const block = run.program.edges.find(edge => edge.kind === 'block')!.block!;
    found.push(Object.fromEntries(block.gives.map(name => {
      const motion = trace.motions.get(name)!;
      return [name, {
        start: motion.start, end: motion.end, affine: motion.affine,
        exactTerminal: motion.exactTerminal, constant: motion.constant,
        cuts: motion.cuts(), first: motion.at(0), middle: motion.at(0.37),
        last: motion.at(1),
      }];
    })));
    return result;
  });
  return { found, spy };
};

const shifted = (): RunDocument => structuredClone(corpus.machines.find(
  machine => machine.name === 'ShiftedCarry')!.document) as unknown as RunDocument;

describe('one Run reuses only successful constant cyclic blocks', () => {
  it('retains one result for a repeated quiet block, with identical bank and history', () => {
    const program = loadProgram(shifted(), 'corpus://ShiftedCarry');
    const block = program.edges.find(edge => edge.kind === 'block')!.block!;
    const run = new Run(program, 0.05, 8);
    const uncached = new Run(program, 0.05, 8);
    const entries = privateRun(run).blockReuse;
    const uncachedEntries = privateRun(uncached).blockReuse;
    const cachedPaths = paths(run);
    const ordinaryPaths = paths(uncached);

    run.advance();
    uncached.advance();
    expect(entries.size).toBe(1);
    const first = entries.get(block);
    run.advance();
    uncachedEntries.clear();
    uncached.advance();
    expect(entries.size).toBe(1);
    expect(entries.get(block)).toBe(first);
    expect(run.state()).toEqual(uncached.state());
    expect(run.crossings()).toEqual(uncached.crossings());
    expect(run.stops()).toEqual(uncached.stops());
    expect(cachedPaths.found).toEqual(ordinaryPaths.found);
    cachedPaths.spy.mockRestore();
    ordinaryPaths.spy.mockRestore();
  });

  it('declines moving and leave-return paths even with zero net delta', () => {
    const run = new Run(loadProgram(shifted(), 'corpus://ShiftedCarry'), 0.05, 8);
    const inner = privateRun(run);
    run.advance();
    const block = run.program.edges.find(edge => edge.kind === 'block')!.block!;
    const entry = inner.blockReuse.get(block);
    const values = run.state();
    const deltas = inner.deltasOf({});
    const trace = propagations.get(deltas)!;
    trace.motions.set('shift', new Motion(values.shift, values.shift,
      [[0, 0.5, t => values.shift + t],
       [0.5, 1, t => values.shift + 1 - t]], false));
    inner.pass(values, deltas, [], 0, {}, {
      stored: inner.blockReuse, pending: new Map(),
    });
    expect(inner.blockReuse.get(block)).toBe(entry);
    run.move('shift', { by: 1, duration: 0.05 });
    run.advance();
    expect(inner.blockReuse.get(block)).toBe(entry);
    run.advance();
    expect(inner.blockReuse.size).toBe(1);
    expect(inner.blockReuse.get(block)).not.toBe(entry);
  });

  it('publishes only after a successful tick and clears on restore, reset and new Run', () => {
    const program = loadProgram(shifted(), 'corpus://ShiftedCarry');
    const run = new Run(program, 0.05, 8);
    const inner = privateRun(run);
    const before = run.snapshot();
    const original = inner.pass.bind(run);
    const injected = vi.spyOn(inner, 'pass').mockImplementation((...args) => {
      original(...args);
      throw new Error('later edge failed');
    });
    expect(() => run.advance()).toThrow('later edge failed');
    expect(inner.blockReuse.size).toBe(0);
    expect(run.snapshot()).toEqual(before);
    injected.mockRestore();
    run.advance();
    expect(inner.blockReuse.size).toBe(1);
    expect(privateRun(new Run(program, 0.05, 8)).blockReuse.size).toBe(0);
    const taken = run.snapshot();
    expect(() => run.restore({ ...taken, program: 'other' })).toThrow();
    expect(inner.blockReuse.size).toBe(1);
    run.restore(taken);
    expect(inner.blockReuse.size).toBe(0);
    run.advance();
    expect(inner.blockReuse.size).toBe(1);
    run.reset();
    expect(inner.blockReuse.size).toBe(0);
  });

  it('declines a stateful member or a shadowed numeric call', () => {
    for (const expression of ['random(1)', 'sqrt(1)', 'sin(shift)', 'plan-only-random']) {
      const document = shifted();
      const raw = document.program as { edges: {
        kind: string; gives: string[]; expressions: (string | null)[] }[] };
      const member = raw.edges.find(edge => edge.kind === 'law'
        && edge.gives.includes('higher.turn'))!;
      if (expression === 'plan-only-random') {
        const plan = (member as unknown as { plans: {
          jumps: { level: string }[] }[] }).plans[0];
        plan.jumps[0].level = `(${plan.jumps[0].level} + (0 * random(1)))`;
      } else {
        member.expressions[0] = `(${member.expressions[0]} + (0 * ${expression}))`;
      }
      if (expression.startsWith('sqrt')) {
        document.bindings = [...(document.bindings ?? []),
          { name: 'sqrt', expression: '1' }];
      }
      const program = loadProgram(document, `corpus://uncertain-${expression}`);
      const selected = program.edges.find(edge => edge.kind === 'block')!.block!;
      expect(selected.members.some(member => member.own === 'higher.turn')).toBe(true);
      const run = new Run(program, 0.05, 8);
      run.advance();
      run.advance();
      expect(privateRun(run).blockReuse.size, expression).toBe(0);
    }
  });

  it('keeps signed-zero and exact-terminal source metadata out of a prior hit', () => {
    const program = loadProgram(shifted(), 'corpus://ShiftedCarry');
    const run = new Run(program, 0.05, 8);
    const inner = privateRun(run);
    run.advance();
    const block = program.edges.find(edge => edge.kind === 'block')!.block!;
    const first = inner.blockReuse.get(block);
    const values = run.state();
    const deltas = inner.deltasOf({});
    const trace = propagations.get(deltas)!;
    trace.motions.set('shift', new Motion(values.shift, values.shift,
      [[0, 1, () => values.shift]], true, true));
    const pending = new Map<object, unknown>();
    inner.pass(values, deltas, [], 0, {}, {
      stored: inner.blockReuse, pending,
    });
    expect(inner.blockReuse.get(block)).toBe(first);
    expect(pending.get(block)).not.toBe(first);

    const negative = shifted();
    const coordinates = (negative.program as { coordinates: Record<string,
      { initial: number }> }).coordinates;
    coordinates.shift.initial = -0;
    const other = new Run(loadProgram(negative, 'corpus://signed-zero'), 0.05, 8);
    expect(Object.is(other.state().shift, -0)).toBe(true);
    other.advance();
    expect(privateRun(other).blockReuse.size).toBe(0);
  });

  it('preserves the scheduled stateful call cadence on a moving cyclic member', async () => {
    vi.resetModules();
    const random = vi.spyOn(Math, 'random').mockReturnValue(0.125);
    try {
      const [{ Run: FreshRun }, { loadProgram: freshLoad }] = await Promise.all([
        import('./run'), import('./program'),
      ]);
      const document = shifted();
      const raw = document.program as { edges: {
        kind: string; gives: string[]; expressions: (string | null)[];
        plans: (unknown | null)[] }[] };
      const member = raw.edges.find(edge => edge.kind === 'law'
        && edge.gives.includes('higher.turn'))!;
      member.expressions[0] = `(${member.expressions[0]} + (0 * random(1)))`;
      const plan = member.plans[0] as { skeleton: string };
      plan.skeleton = `(${plan.skeleton} + (0 * random(1)))`;
      const program = freshLoad(document, 'corpus://stateful-block');
      const cached = new FreshRun(program, 0.05, 8);
      const ordinary = new FreshRun(program, 0.05, 8);
      const counts: number[] = [];
      for (const run of [cached, ordinary]) {
        run.advance();
        run.move('shift', { by: 1, duration: 0.05 });
        const before = random.mock.calls.length;
        run.advance();
        counts.push(random.mock.calls.length - before);
        expect(privateRun(run).blockReuse.size).toBe(0);
      }
      expect(counts[0]).toBeGreaterThan(0);
      expect(counts[1]).toBe(counts[0]);
      expect(cached.state()).toEqual(ordinary.state());
      expect(cached.crossings()).toEqual(ordinary.crossings());
      expect(cached.stops()).toEqual(ordinary.stops());
    } finally {
      random.mockRestore();
    }
  });

  it('retains ordinary crossing and stop work for a moving block', () => {
    const document = structuredClone(corpus.machines.find(
      machine => machine.name === 'RangedBlock')!.document) as unknown as RunDocument;
    const run = new Run(loadProgram(document, 'corpus://RangedBlock'), 0.05, 8);
    run.move('spin', { by: 2, duration: 0.05 });
    run.move('shift', { by: 1, duration: 0.05 });
    run.advance();
    expect(run.stops()).toHaveLength(1);
    expect(privateRun(run).blockReuse.size).toBe(0);
  });

  it('does not turn a terminal block landing into a cached quiet result', () => {
    const run = new Run(loadProgram(shifted(), 'corpus://ShiftedCarry'), 1, 8);
    const inner = privateRun(run);
    run.advance();
    const block = run.program.edges.find(edge => edge.kind === 'block')!.block!;
    const before = inner.blockReuse.get(block);
    run.move('crank', { to: -4.9425 });
    const ordinary = inner.pass.bind(run);
    let sawLanding = false;
    const spy = vi.spyOn(inner, 'pass').mockImplementation((...args) => {
      const result = ordinary(...args);
      const landings = args[4] as Record<string, number>;
      sawLanding ||= block.gives.some(name => name in landings);
      return result;
    });
    expect(run.move('crank', { to: 3.9075 }).status).toBe('completed');
    spy.mockRestore();
    expect(sawLanding).toBe(true);
    expect(inner.blockReuse.get(block)).toBe(before);
  });

  it('keeps a malformed moving member on the original error path', () => {
    const document = shifted();
    const raw = document.program as { edges: {
      kind: string; gives: string[]; expressions: (string | null)[];
      plans: ({ skeleton: string } | null)[] }[] };
    const member = raw.edges.find(edge => edge.kind === 'law'
      && edge.gives.includes('higher.turn'))!;
    member.expressions[0] = `(${member.expressions[0]} + min())`;
    member.plans[0]!.skeleton = `(${member.plans[0]!.skeleton} + min())`;
    const run = new Run(loadProgram(document, 'corpus://bad-member'), 0.05, 8);
    const before = run.snapshot();
    run.advance();
    run.move('shift', { by: 1, duration: 0.05 });
    const active = run.snapshot();
    expect(() => run.advance()).toThrow();
    expect(run.snapshot().bank).toEqual(active.bank);
    expect(run.snapshot().tick).toBe(active.tick);
    expect(privateRun(run).blockReuse.size).toBeLessThanOrEqual(1);
    expect(before.bank).toEqual(active.bank);
  });
});
