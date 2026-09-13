/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The tick (`simulation/run.py`'s `class Run`, reproduced): admissions,
// one propagation over the edges in program order, stops located inside
// the tick with the group of inputs that push them, segments, and the
// atomicity that makes a refused tick commit nothing at all.

import { describe, expect, it } from 'vitest';
import { Run } from './run';
import { loadProgram } from './program';
import type { LoadedProgram, RunDocument } from './program';

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
}): LoadedProgram {
  const ids = Object.keys(spec.coordinates);
  const inputs = ids.filter(
    (id) => (spec.coordinates[id] as { kind: string }).kind === 'input');
  return loadProgram({
    format: 'solid-node-export',
    version: 5,
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

describe('one pass over the edges in program order', () => {
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
