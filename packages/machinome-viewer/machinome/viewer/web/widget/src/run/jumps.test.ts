/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The jump plan (`simulation/program.py`'s `JumpPlan` and its helpers).
// A law that jumps contributes its CONTINUOUS part only: the path is cut
// at every crossing of every jump surface it meets, each jump node holds
// one branch per piece read at that piece's MIDPOINT, and the increment
// is the plain sum of the branch-substituted law's change over the
// pieces. A jump therefore never moves a part.

import { describe, expect, it } from 'vitest';
import {
  along, blockCuts, blockIncrements, branchOf, copySign, CrossingRecord,
  deduplicated, fromOrdinal, merged, nextAfter, onSurface, ordinalOf, planCuts,
  planIncrement, retainedCuts, retainedIncrement, surfacesOf, ulpOf, unlanded,
} from './jumps';
import { edgeIncrements } from './edges';
import {
  LandingInvariantError, loadProgram, refusalKind, UnsupportedLaw,
} from './program';
import type {
  LoadedProgram, ProgramBlock, ProgramPlan, RunDocument,
} from './program';
import corpus from '../running-corpus.json';

const LIMITS = {
  crossing_tolerance: 1e-12, subdivisions: 64, bisection_rounds: 64,
  max_crossings: 1000, agreement: 1e-9,
};

function bench(expression: string, plan: unknown,
               extra: Record<string, unknown> = {}): LoadedProgram {
  return loadProgram({
    format: 'solid-node-export',
    version: 5,
    drivers: {
      crank: { default: 0, range: null, unit: null, dtype: null, scale: null },
    },
    instructions: {},
    program: {
      identity: 'bench',
      clock: 'time',
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'wheel.turn': {
          kind: 'coordinate', initial: 0, unit: null, domain: null,
        },
      },
      intermediates: [],
      edges: [{
        kind: 'law', needs: ['crank'], gives: ['wheel.turn'],
        description: 'crank drives wheel.turn', stated_by: 'Bench',
        expressions: [expression], affine: [false], plans: [plan],
      }],
      spans: {},
      sources: { crank: ['crank'], 'wheel.turn': ['crank'] },
      limits: { ...LIMITS },
      ...extra,
    },
  } as unknown as RunDocument, 'bench://jumps');
}

const sawtooth = () => bench('(crank - floor(crank))', {
  skeleton: '(crank - _j0)',
  jumps: [{ name: '_j0', primitive: 'floor', level: 'crank', affine: true }],
});

function planOf(program: LoadedProgram): ProgramPlan {
  return program.edges[0].plans[0]!;
}

describe('branchOf reads one branch per primitive', () => {
  it('floor and ceil', () => {
    expect(branchOf('floor', 2.7)).toBe(2);
    expect(branchOf('floor', -2.1)).toBe(-3);
    expect(branchOf('ceil', 2.1)).toBe(3);
    expect(branchOf('ceil', -2.7)).toBe(-2);
  });

  it('sign, by the producer\'s own formula', () => {
    expect(branchOf('sign', 3)).toBe(1);
    expect(branchOf('sign', -3)).toBe(-1);
    expect(branchOf('sign', 0)).toBe(0);
    // `Math.sign(-0)` is -0; the producer's `(x > 0) - (x < 0)` is 0.
    expect(Object.is(branchOf('sign', -0), 0)).toBe(true);
  });

  it('% as the truncated QUOTIENT, not a constant', () => {
    expect(branchOf('%', 2.7)).toBe(2);
    expect(branchOf('%', -2.7)).toBe(-2);
    expect(branchOf('%', 0.5)).toBe(0);
  });

  it('each comparison against zero', () => {
    expect(branchOf('<', -1)).toBe(1);
    expect(branchOf('<', 1)).toBe(0);
    expect(branchOf('<=', 0)).toBe(1);
    expect(branchOf('>', 1)).toBe(1);
    expect(branchOf('>=', 0)).toBe(1);
    expect(branchOf('==', 0)).toBe(1);
    expect(branchOf('==', 1)).toBe(0);
    expect(branchOf('!=', 1)).toBe(1);
    expect(branchOf('!=', 0)).toBe(0);
  });
});

describe('surfacesOf', () => {
  // The limits as the engine holds them, from the same five published
  // numbers.
  const LIMITS = {
    crossingTolerance: 1e-12, subdivisions: 64, bisectionRounds: 64,
    maxCrossings: 1000, agreement: 1e-9,
  };
  const floor = { name: '_j0', primitive: 'floor' as const, level: 'crank',
                  affine: true };
  const sign = { name: '_j0', primitive: 'sign' as const, level: 'crank',
                 affine: true };
  const remainder = { name: '_j0', primitive: '%' as const, level: 'crank',
                      affine: true };
  const refuse = (): never => { throw new Error('refused'); };

  it('is exclusive between two level values', () => {
    expect(surfacesOf(floor, 0.5, 3.5, false, LIMITS, refuse))
      .toEqual([1, 2, 3]);
    expect(surfacesOf(floor, 1, 3, false, LIMITS, refuse)).toEqual([2]);
  });

  it('is inclusive when a sample may sit on the surface', () => {
    expect(surfacesOf(floor, 1, 3, true, LIMITS, refuse)).toEqual([1, 2, 3]);
  });

  it('reads either direction of travel', () => {
    expect(surfacesOf(floor, 3.5, 0.5, false, LIMITS, refuse))
      .toEqual([1, 2, 3]);
  });

  it('gives a sign or a comparison its one surface at zero', () => {
    expect(surfacesOf(sign, -1, 1, false, LIMITS, refuse)).toEqual([0]);
    expect(surfacesOf(sign, 1, 2, false, LIMITS, refuse)).toEqual([]);
    expect(surfacesOf(sign, 0, 1, false, LIMITS, refuse)).toEqual([]);
    expect(surfacesOf(sign, 0, 1, true, LIMITS, refuse)).toEqual([0]);
  });

  it('skips the zero surface for %, which is continuous there', () => {
    expect(surfacesOf(remainder, -1.5, 1.5, false, LIMITS, refuse))
      .toEqual([-1, 1]);
  });

  it('refuses a non-finite level', () => {
    expect(() => surfacesOf(floor, 0, Infinity, false, LIMITS, refuse))
      .toThrow('refused');
  });

  it('refuses more surfaces than the published limit', () => {
    expect(() => surfacesOf(floor, 0, 2000, false, LIMITS, refuse))
      .toThrow('refused');
  });
});

describe('deduplicated', () => {
  it('folds a crossing located twice, from either side', () => {
    expect(deduplicated([[0.5, 1], [0.5 + 1e-15, 1], [0.75, 2]], 1e-12))
      .toEqual([[0.5, 1], [0.75, 2]]);
  });

  it('keeps two surfaces at the same fraction', () => {
    expect(deduplicated([[0.5, 1], [0.5, 2]], 1e-12))
      .toEqual([[0.5, 1], [0.5, 2]]);
  });
});

describe('merged', () => {
  it('folds two cuts closer than the tolerance into one', () => {
    expect(merged([0, 1], [0.5, 0.5 + 1e-15], 1e-12)).toEqual([0, 0.5, 1]);
  });

  it('always ends at exactly 1', () => {
    const cuts = merged([0, 1], [1 - 1e-15], 1e-12);
    expect(cuts[cuts.length - 1]).toBe(1);
  });
});

describe('along', () => {
  it('is exactly start + delta at t = 1', () => {
    expect(along({ crank: 0.1 }, { crank: 0.2 }, 1))
      .toEqual({ crank: 0.1 + 0.2 * 1 });
  });
});

describe('the partition and the increment', () => {
  it('cuts an affine level quantity at every surface it SOLVES', () => {
    const program = sawtooth();
    const cuts = planCuts(program, planOf(program), { crank: 0.5 },
                          { crank: 2 }, 'crank drives wheel.turn',
                          'wheel.turn');
    expect(cuts).toEqual([0, 0.25, 0.75, 1]);
  });

  it('sums the branch-substituted law over the pieces', () => {
    const program = sawtooth();
    const crossings: unknown[] = [];
    const increment = planIncrement(
      program, planOf(program), { crank: 0.5 }, { crank: 2 },
      'crank drives wheel.turn', 'wheel.turn',
      crossings as never, 7);
    // A sawtooth's continuous part over 2.0 of travel is 2.0: the jump
    // moved nothing at all.
    expect(increment).toBeCloseTo(2, 12);
    expect(crossings).toEqual([
      { tick: 7, relation: 'crank drives wheel.turn',
        coordinate: 'wheel.turn', primitive: 'floor', level: 1, t: 0.25 },
      { tick: 7, relation: 'crank drives wheel.turn',
        coordinate: 'wheel.turn', primitive: 'floor', level: 2, t: 0.75 },
    ]);
  });

  it('contributes zero over a zero-length path, evaluating nothing', () => {
    const program = sawtooth();
    expect(planIncrement(program, planOf(program), { crank: 0.5 },
                         { crank: 0 }, 'd', 'wheel.turn', null, 0)).toBe(0);
    expect(planCuts(program, planOf(program), { crank: 0.5 }, { crank: 0 },
                    'd', 'wheel.turn')).toEqual([0, 1]);
  });

  it('samples, brackets and bisects a level quantity that is NOT affine', () => {
    const program = bench('(crank - floor((crank ^ 2)))', {
      skeleton: '(crank - _j0)',
      jumps: [{
        name: '_j0', primitive: 'floor', level: '(crank ^ 2)', affine: false,
      }],
    });
    const cuts = planCuts(program, planOf(program), { crank: 0 },
                          { crank: 2 }, 'd', 'wheel.turn');
    // The surfaces of crank^2 at 1, 2, 3 are reached at sqrt(k)/2.
    expect(cuts).toHaveLength(5);
    expect(cuts[1]).toBeCloseTo(Math.sqrt(1) / 2, 11);
    expect(cuts[2]).toBeCloseTo(Math.sqrt(2) / 2, 11);
    expect(cuts[3]).toBeCloseTo(Math.sqrt(3) / 2, 11);
    expect(cuts[4]).toBe(1);
  });

  it('reads each piece\'s branch at its MIDPOINT', () => {
    // A law that is the branch itself: the increment is zero on every
    // piece, and it could only be otherwise if a branch were read at an
    // endpoint, where the level quantity sits exactly ON a surface.
    const program = bench('floor(crank)', {
      skeleton: '_j0',
      jumps: [{ name: '_j0', primitive: 'floor', level: 'crank',
                affine: true }],
    });
    expect(planIncrement(program, planOf(program), { crank: 0 },
                         { crank: 5 }, 'd', 'wheel.turn', null, 0)).toBe(0);
  });

  it('takes the jump nodes in postorder, an inner node cutting first', () => {
    // `_j1`'s level reads `_j0`'s branch, so it is only well posed once
    // `_j0` has already cut the path.
    const program = bench('(crank - floor((crank + floor(crank))))', {
      skeleton: '(crank - _j1)',
      jumps: [
        { name: '_j0', primitive: 'floor', level: 'crank', affine: true },
        { name: '_j1', primitive: 'floor', level: '(crank + _j0)',
          affine: true },
      ],
    });
    const crossings: { primitive: string; level: number; t: number }[] = [];
    planIncrement(program, planOf(program), { crank: 0.5 }, { crank: 1 },
                  'd', 'wheel.turn', crossings as never, 1);
    // Sorted by the fraction of the tick, then by postorder index.
    const fractions = crossings.map((one) => one.t);
    expect([...fractions].sort((a, b) => a - b)).toEqual(fractions);
    expect(crossings.length).toBeGreaterThan(0);
  });

  it('refuses a partition wider than the published crossing limit', () => {
    const program = sawtooth();
    expect(() => planIncrement(program, planOf(program), { crank: 0 },
                               { crank: 5000 }, 'd', 'wheel.turn', null, 0))
      .toThrow(/surfaces/);
  });
});

// ---------------------------------------------------------------------
// The float primitives the far-side landing is defined in terms of
// (design D3, tasks 3). Every expected value below is the answer the
// producer's own `_ordinal`, `math.ulp`, `math.nextafter` and
// `math.copysign` give for the same argument, read off CPython on this
// host rather than reasoned about here.
// ---------------------------------------------------------------------

describe('the float primitives (design D3)', () => {
  it('orders +0 and -0 to the SAME ordinal 0', () => {
    expect(ordinalOf(0)).toBe(0n);
    expect(ordinalOf(-0)).toBe(0n);
  });

  it('is `_ordinal` to the bit, at every magnitude', () => {
    expect(ordinalOf(1)).toBe(4607182418800017408n);
    expect(ordinalOf(-1)).toBe(-4607182418800017408n);
    expect(ordinalOf(1e300)).toBe(9094988921128908188n);
    expect(ordinalOf(-1e300)).toBe(-9094988921128908188n);
    expect(ordinalOf(5e-324)).toBe(1n);
    expect(ordinalOf(0.5)).toBe(4602678819172646912n);
    expect(ordinalOf(2)).toBe(4611686018427387904n);
    expect(ordinalOf(359.5)).toBe(4645032007074578432n);
  });

  it('makes ADJACENT floats differ by exactly one ordinal', () => {
    // At 1.0, across the binade boundary at 1.0 downward, at 1e300 and
    // at the smallest subnormal.
    expect(ordinalOf(1.0000000000000002) - ordinalOf(1)).toBe(1n);
    expect(ordinalOf(1) - ordinalOf(0.9999999999999999)).toBe(1n);
    expect(ordinalOf(nextAfter(1e300, Infinity)) - ordinalOf(1e300)).toBe(1n);
    expect(ordinalOf(5e-324) - ordinalOf(0)).toBe(1n);
  });

  it('round-trips through `fromOrdinal`, negatives and a binade boundary '
     + 'included', () => {
    for (const value of [0, 1, -1, 0.5, 2, -2, 1e300, -1e300, 5e-324,
                         -5e-324, 359.5, 108, 0.9999999999999999,
                         1.0000000000000002]) {
      expect(fromOrdinal(ordinalOf(value))).toBe(value);
    }
    // -0 is the one value that does not round-trip AS ITSELF, because it
    // shares +0's ordinal -- which is the ±0 handling the producer's
    // docstring means.
    expect(Object.is(fromOrdinal(ordinalOf(-0)), 0)).toBe(true);
  });

  it('is `math.nextafter`', () => {
    expect(nextAfter(1, 1)).toBe(1);
    expect(nextAfter(1, 2)).toBe(1.0000000000000002);
    expect(nextAfter(1, 0)).toBe(0.9999999999999999);
    expect(nextAfter(2, 1)).toBe(1.9999999999999998);
    expect(nextAfter(0, 1)).toBe(5e-324);
    expect(nextAfter(0, -1)).toBe(-5e-324);
  });

  it('is `math.ulp`', () => {
    expect(ulpOf(1)).toBe(2.220446049250313e-16);
    expect(ulpOf(359.5)).toBe(5.684341886080802e-14);
    expect(ulpOf(-359.5)).toBe(5.684341886080802e-14);
  });

  it('is `math.copysign(1.0, x)`, NEGATIVE ZERO included', () => {
    expect(copySign(-0)).toBe(-1);
    expect(copySign(0)).toBe(1);
    expect(copySign(-3.5)).toBe(-1);
    expect(copySign(3.5)).toBe(1);
  });
});

// ---------------------------------------------------------------------
// A law that READS THE COORDINATE IT DRIVES (`_Retained`/`_Walk`,
// design D2, tasks 4). The bench is `Clearing`'s own shape: a ring
// carrying nine-tooth racks sweeps past a dial, and a rack turns the
// dial only while its teeth REACH it (the station gate, over the RING)
// and the dial is not already standing in its missing-tooth GAP (the
// band gate, over the DIAL's own retained angle).
// ---------------------------------------------------------------------

/** `Clearing`, loadable: rest `108`, `GAP = 0.5`, `STATION = (100, 500)`. */
function clearing(edge: Record<string, unknown> = {},
                  rest = 108): LoadedProgram {
  return loadProgram({
    format: 'solid-node-export',
    version: 6,
    drivers: {
      ring: { default: 0, range: null, unit: 'deg', dtype: null, scale: null },
      setter: {
        default: 0, range: null, unit: 'deg', dtype: null, scale: null,
      },
    },
    instructions: {},
    bindings: [
      { name: '_b0', expression: '(ring - 100.0)' },
      { name: '_b1', expression: '(_b0 / 400.0)' },
      { name: '_b2', expression: '(wheel.turn + 0.5)' },
      { name: '_b3', expression: '(_b2 / 360.0)' },
    ],
    program: {
      identity: 'clearing',
      clock: 'time',
      coordinates: {
        ring: { kind: 'input', initial: 0, domain: null },
        setter: { kind: 'input', initial: 0, domain: null },
        'wheel.turn': {
          kind: 'coordinate', initial: rest, unit: 'deg', domain: 'rotational',
        },
      },
      intermediates: [],
      edges: [{
        kind: 'law',
        needs: ['setter', 'ring', 'wheel.turn'],
        gives: ['wheel.turn'],
        description: '(setter, ring, wheel.turn) drives wheel.turn',
        stated_by: 'Clearing',
        expressions: [
          '(setter + ((ring * (floor(_b1) == 0)) * '
          + '((_b2 - (360.0 * floor(_b3))) >= 1.0)))',
        ],
        affine: [true],
        plans: [{
          skeleton: '(setter + ((ring * _j1) * _j3))',
          jumps: [
            { name: '_j0', primitive: 'floor', level: '_b1', affine: true },
            { name: '_j1', primitive: '==', level: '(_j0 - 0)', affine: true },
            { name: '_j2', primitive: 'floor', level: '_b3', affine: true },
            {
              name: '_j3', primitive: '>=',
              level: '((_b2 - (360.0 * _j2)) - 1.0)', affine: true,
            },
          ],
        }],
        ...edge,
      }],
      spans: {},
      sources: {
        ring: ['ring'], setter: ['setter'], 'wheel.turn': ['ring', 'setter'],
      },
      limits: { ...LIMITS },
    },
  } as unknown as RunDocument, 'bench://clearing');
}

function readingOf(program: LoadedProgram) {
  return program.edges[0].retained[0]!;
}

/** One tick of one driven end's walk, over the bench above. */
function walked(program: LoadedProgram, start: Record<string, number>,
                delta: Record<string, number>,
                crossings: CrossingRecord[] | null = null) {
  return retainedIncrement(program, readingOf(program), start, delta,
                           program.edges[0].description, 'wheel.turn',
                           crossings, 1);
}

describe('the two-layer walk (design D2)', () => {
  it('4.1 reports an increment AND the absolute value a cut left the '
     + 'coordinate at', () => {
    const program = clearing();
    // The ring sweeps its whole station while the dial stands at 108:
    // the dial is carried to its own gap and stops there.
    const found = walked(program,
                         { setter: 0, ring: 100, 'wheel.turn': 108 },
                         { setter: 0, ring: 400, 'wheel.turn': 0 });
    expect(found.landing).toBe(359.5);
    expect(found.increment).toBe(359.5 - 108);
  });

  it('4.1 reports NO landing where no cut placed the coordinate', () => {
    const program = clearing();
    // A ring movement entirely OUTSIDE the station: the rack never
    // reaches the dial, so nothing is cut and nothing is placed.
    const found = walked(program,
                         { setter: 0, ring: 0, 'wheel.turn': 108 },
                         { setter: 0, ring: 50, 'wheel.turn': 0 });
    expect(found.landing).toBe(null);
    expect(found.increment).toBe(0);
  });

  it('4.1 `retainedCuts` reports the breakpoints the two layers together '
     + 'put on the path', () => {
    const program = clearing();
    const cuts = retainedCuts(program, readingOf(program),
                              { setter: 0, ring: 0, 'wheel.turn': 108 },
                              { setter: 0, ring: 600, 'wheel.turn': 0 },
                              'clearing', 'wheel.turn');
    // Layer one cuts where the station opens and closes; layer two cuts
    // where the dial reaches its band.
    expect(cuts[0]).toBe(0);
    expect(cuts[cuts.length - 1]).toBe(1);
    expect(cuts.length).toBeGreaterThan(3);
    for (let at = 1; at < cuts.length; at += 1) {
      expect(cuts[at]).toBeGreaterThanOrEqual(cuts[at - 1]);
    }
  });

  it('4.2 ZEROES the driven coordinate\'s own delta: what it holds on a '
     + 'piece is what the pieces before it produced, never an increment '
     + 'the tick handed it', () => {
    const program = clearing();
    const start = { setter: 0, ring: 100, 'wheel.turn': 108 };
    const quiet = walked(program, start,
                         { setter: 0, ring: 400, 'wheel.turn': 0 });
    // The `StoppedClearing` shape: the SETTER drives the same coordinate,
    // so the tick hands `wheel.turn` an increment of its own before this
    // edge is reached. The walk must not advance `own` along the path by
    // it.
    const loud = walked(program, start,
                        { setter: 0, ring: 400, 'wheel.turn': 250 });
    expect(loud.increment).toBe(quiet.increment);
    expect(loud.landing).toBe(quiet.landing);
  });

  it('4.3 contributes 0 and evaluates NOTHING where no source but the '
     + 'driven coordinate itself moves', () => {
    // A level quantity that divides by a source standing at zero: any
    // evaluation at all refuses the tick, so a clean 0 proves none was
    // made.
    const program = clearing({
      expressions: ['(setter * (floor((1.0 / ring)) == 0))'],
      affine: [false],
      plans: [{
        skeleton: '(setter * _j1)',
        jumps: [
          { name: '_j0', primitive: 'floor', level: '(1.0 / ring)',
            affine: false },
          { name: '_j1', primitive: '==', level: '(_j0 - _b3)',
            affine: false },
        ],
      }],
    });
    const found = walked(program,
                         { setter: 0, ring: 0, 'wheel.turn': 108 },
                         { setter: 0, ring: 0, 'wheel.turn': 400 });
    expect(found.increment).toBe(0);
    expect(found.landing).toBe(null);
  });

  it('4.4 layer one is ADR-107\'s own partition over the INDEPENDENT '
     + 'nodes, its crossings recorded', () => {
    const program = clearing();
    const crossings: CrossingRecord[] = [];
    // The ring enters the station a quarter of the way through the tick.
    walked(program, { setter: 0, ring: 0, 'wheel.turn': 108 },
           { setter: 0, ring: 400, 'wheel.turn': 0 }, crossings);
    const station = crossings.filter((one) => one.primitive === 'floor'
                                     && one.level === 0);
    expect(station).toHaveLength(1);
    expect(station[0].t).toBeCloseTo(0.25, 12);
    expect(station[0].relation)
      .toBe('(setter, ring, wheel.turn) drives wheel.turn');
  });

  it('4.4 is `[0, 1]` and evaluates nothing where the independent subset '
     + 'is empty', () => {
    const program = clearing({
      expressions: ['(setter + (ring * ((_b2 - (360.0 * floor(_b3))) '
                    + '>= 1.0)))'],
      plans: [{
        skeleton: '(setter + (ring * _j3))',
        jumps: [
          { name: '_j2', primitive: 'floor', level: '_b3', affine: true },
          {
            name: '_j3', primitive: '>=',
            level: '((_b2 - (360.0 * _j2)) - 1.0)', affine: true,
          },
        ],
      }],
    });
    expect(readingOf(program).outer.jumps).toEqual([]);
    const found = walked(program, { setter: 0, ring: 0, 'wheel.turn': 108 },
                         { setter: 0, ring: 400, 'wheel.turn': 0 });
    expect(found.landing).toBe(359.5);
  });

  it('4.5 `onSurface` is `_on_surface`: zero for `sign` and a comparison, '
     + 'never a non-finite level, never `%` at zero', () => {
    const floorJump = { name: '_j', primitive: 'floor' as const,
                        level: 'x', affine: true };
    const signJump = { ...floorJump, primitive: 'sign' as const };
    const comparison = { ...floorJump, primitive: '>=' as const };
    const remainder = { ...floorJump, primitive: '%' as const };
    expect(onSurface(signJump, 0)).toBe(true);
    expect(onSurface(signJump, 1)).toBe(false);
    expect(onSurface(comparison, 0)).toBe(true);
    expect(onSurface(comparison, -0)).toBe(true);
    expect(onSurface(comparison, 1e-16)).toBe(false);
    expect(onSurface(floorJump, 3)).toBe(true);
    expect(onSurface(floorJump, 3.5)).toBe(false);
    expect(onSurface(floorJump, Infinity)).toBe(false);
    expect(onSurface(floorJump, NaN)).toBe(false);
    // `%` is continuous where `a / b` crosses zero, so zero is not one
    // of its surfaces.
    expect(onSurface(remainder, 0)).toBe(false);
    expect(onSurface(remainder, 2)).toBe(true);
  });

  it('4.5 a node flipped TWICE at one left end refuses the tick as a '
     + 'sliding mode, in the producer\'s own words', () => {
    // A gate sitting exactly on its surface each of whose branches
    // carries the level back across it: under `>=` true the rate is
    // negative, under `>=` false it is positive.
    const program = clearing({
      expressions: ['(setter * (1.0 - (2.0 * ((wheel.turn - 5.0) >= 0.0))))'],
      affine: [true],
      plans: [{
        skeleton: '(setter * (1.0 - (2.0 * _j0)))',
        jumps: [{
          name: '_j0', primitive: '>=', level: '(wheel.turn - 5.0)',
          affine: true,
        }],
      }],
    }, 5);
    let message = '';
    try {
      walked(program, { setter: 0, ring: 0, 'wheel.turn': 5 },
             { setter: 10, ring: 0, 'wheel.turn': 0 });
    } catch (error) {
      message = (error as Error).message;
    }
    expect(message).toContain(
      'wheel.turn stands exactly on a surface of its >= and each branch '
      + 'carries the level back across it -- a sliding mode, not a '
      + 'mechanism.');
    expect(message).toContain('The tick committed nothing');
  });

  it('4.8 places the coordinate at the nearest representable value on the '
     + 'FAR side of the surface', () => {
    const program = clearing();
    const found = walked(program, { setter: 0, ring: 100, 'wheel.turn': 108 },
                         { setter: 0, ring: 400, 'wheel.turn': 0 });
    // The band's surface is `(wheel.turn + 0.5) / 360 == 1`, which is
    // `wheel.turn == 359.5` exactly; the far side is the first value at
    // which the gate reads DISENGAGED.
    const landing = found.landing!;
    expect((landing + 0.5) / 360).toBeGreaterThanOrEqual(1);
    expect((nextAfter(landing, -Infinity) + 0.5) / 360).toBeLessThan(1);
  });

  it('4.8 does not walk the coordinate where the piece did NOT move it: '
     + 'the level crossed by the sources\' motion while the gate held', () => {
    const program = clearing();
    const crossings: CrossingRecord[] = [];
    // The dial already stands in its gap, so the band gate holds it
    // while the ring sweeps its whole station: the station's own
    // crossings are layer one's and move nothing.
    const found = walked(program,
                         { setter: 0, ring: 0, 'wheel.turn': 359.5 },
                         { setter: 0, ring: 600, 'wheel.turn': 0 }, crossings);
    expect(found.increment).toBe(0);
    expect(found.landing).toBe(null);
  });

  it('4.10 refuses a walk that cuts more than `maxCrossings` times, with '
     + 'the existing message and count', () => {
    const program = clearing({}, 0);
    // A sweep of a hundred thousand degrees cuts the dial's own gate
    // once per turn: far more than the thousand a single law is
    // admitted in one tick.
    expect(() => walked(program, { setter: 0, ring: 100, 'wheel.turn': 0 },
                        { setter: 400000, ring: 400, 'wheel.turn': 0 }))
      .toThrow(/more than the 1000 a single law is admitted in one tick/);
  });
});

// ---------------------------------------------------------------------
// The first cut, and the three defects the framework's own
// implementation found after ratification (design D2, tasks 4.6-4.7).
// Each of these is red when the correction it pins is removed.
// ---------------------------------------------------------------------

/** A gate that changes the RATE rather than holding the part: one
 * `floor` per 36 degrees of the dial's own angle, and half again the
 * ring's speed above the first tooth. */
function rateGate(rest: number): LoadedProgram {
  return clearing({
    expressions: ['(ring * (1.0 + (0.5 * (floor((wheel.turn / 36.0)) '
                  + '>= 1.0))))'],
    affine: [true],
    plans: [{
      skeleton: '(ring * (1.0 + (0.5 * _j1)))',
      jumps: [
        { name: '_j0', primitive: 'floor', level: '(wheel.turn / 36.0)',
          affine: true },
        { name: '_j1', primitive: '>=', level: '(_j0 - 1.0)', affine: true },
      ],
    }],
  }, rest);
}

describe('the first cut (design D2, tasks 4.6-4.7)', () => {
  it('4.6 takes the EARLIEST surface only and DECIDES AGAIN -- where '
     + '`crossingsOf` would return all of them from one solve', () => {
    const program = rateGate(0);
    const crossings: CrossingRecord[] = [];
    walked(program, { setter: 0, ring: 0, 'wheel.turn': 0 },
           { setter: 0, ring: 200, 'wheel.turn': 0 }, crossings);
    const teeth = crossings.filter((one) => one.primitive === 'floor');
    // Tooth 1 is reached at 36/200 of the tick, under the rate the piece
    // BEGINS at. Tooth 2 is then reached 36 degrees later at the rate
    // the first cut put the gate into -- 300, not 200 -- so at
    // 0.18 + 36/300 and NOT at 72/200 = 0.36, which is where one solve
    // over the whole tick would have put it.
    expect(teeth[0].t).toBeCloseTo(0.18, 12);
    expect(teeth[1].t).toBeCloseTo(0.3, 12);
    expect(teeth[1].t).not.toBeCloseTo(0.36, 6);
  });

  it('4.7 defect one: a level that does not MOVE crosses nothing, and a '
     + 'surface EQUAL to a sub-interval\'s left sample is not a crossing '
     + 'of it -- the PHANTOM that reports one surface over and over', () => {
    // The searched path: the same machine with the skeleton published
    // NOT affine, so every crossing falls to the 64-sample search. Once
    // the dial is landed in its gap the band gate HOLDS it, and its
    // `floor` level then sits exactly on the surface it was landed at
    // for the whole of every later piece.
    const program = clearing({ affine: [false] });
    const crossings: CrossingRecord[] = [];
    const found = walked(program,
                         { setter: 0, ring: 100, 'wheel.turn': 108 },
                         { setter: 0, ring: 400, 'wheel.turn': 0 },
                         crossings);
    expect(found.landing).toBe(359.5);
    // ONE cut: the `floor` and the comparison reach their surfaces at one
    // fraction and are one cut, and nothing is reported after it.
    const fractions = new Set(crossings.map((one) => one.t));
    expect(fractions.size).toBe(1);
  });

  it('4.7 defect two: a flipped node takes the branch of the region the '
     + 'level departs INTO, never the branch at the probe -- which on a '
     + 'gate that changes the rate is a whole tooth away', () => {
    // The dial stands EXACTLY on a tooth boundary and the ring is swept
    // fast enough that the first probe sample is a whole tooth past it.
    const program = clearing({
      expressions: ['(ring * (1.0 - (floor((wheel.turn / 36.0)) >= 1.0)))'],
      affine: [true],
      plans: [{
        skeleton: '(ring * (1.0 - _j1))',
        jumps: [
          { name: '_j0', primitive: 'floor', level: '(wheel.turn / 36.0)',
            affine: true },
          { name: '_j1', primitive: '>=', level: '(_j0 - 1.0)',
            affine: true },
        ],
      }],
    }, 0);
    const found = walked(program, { setter: 0, ring: 0, 'wheel.turn': 0 },
                         { setter: 0, ring: 4000, 'wheel.turn': 0 });
    // The piece begins in tooth 0, where the gate is OPEN: the dial runs
    // to the next tooth boundary and the gate then holds it there. A
    // flip to the branch at the probe -- tooth 1, 62.5 degrees away at
    // the first of 64 samples -- closes the gate at the left end and
    // the dial never moves at all.
    expect(found.landing).toBe(36);
    expect(found.increment).toBe(36);
  });

  it('4.7 defect three: a genuine crossing a hair inside a piece\'s left '
     + 'end is NOT folded away -- folding it drives the part through its '
     + 'gap', () => {
    // The dial stands 1e-13 short of its band, and the ring carries it
    // a thousand degrees over the tick: the crossing is at about 1e-16
    // of the tick, a ten-thousandth of the crossing tolerance inside the
    // left end, and it is a real one.
    const program = clearing({}, 359.5 - 1e-13);
    const found = walked(program,
                         { setter: 0, ring: 100, 'wheel.turn': 359.5 - 1e-13 },
                         { setter: 0, ring: 400, 'wheel.turn': 0 });
    expect(found.landing).toBe(359.5);
    // `merged` and `deduplicated` belong to LAYER ONE. Folded into the
    // left end, this piece would integrate whole and leave the dial a
    // thousand degrees on, through its gap and out the other side.
    expect(found.increment).toBeLessThan(1);
  });

  it('4.8 two dependent nodes crossing at one fraction are ONE cut, each '
     + 'taking its far side', () => {
    // A `floor` per 36 degrees and a `sign` about the same 36 degrees:
    // both reach a surface at exactly the dial's 36th degree.
    const program = clearing({
      expressions: ['(ring * (1.0 - (((floor((wheel.turn / 36.0)) '
                    + '+ sign((wheel.turn - 36.0))) - 1.0) >= 0.0)))'],
      affine: [true],
      plans: [{
        skeleton: '(ring * (1.0 - _j2))',
        jumps: [
          { name: '_j0', primitive: 'floor', level: '(wheel.turn / 36.0)',
            affine: true },
          { name: '_j1', primitive: 'sign', level: '(wheel.turn - 36.0)',
            affine: true },
          { name: '_j2', primitive: '>=', level: '((_j0 + _j1) - 1.0)',
            affine: true },
        ],
      }],
    }, 0);
    const crossings: CrossingRecord[] = [];
    const found = walked(program, { setter: 0, ring: 0, 'wheel.turn': 0 },
                         { setter: 0, ring: 200, 'wheel.turn': 0 },
                         crossings);
    const first = crossings.filter((one) => one.t === crossings[0].t);
    expect(first.map((one) => one.primitive).sort())
      .toEqual(['floor', 'sign']);
    expect(found.landing).toBe(36);
  });

  it('4.9 the unlanded refusal names the relation, the coordinate and the '
     + 'primitive, and says the tick committed nothing', () => {
    // No test can REACH this by construction -- a cut exists because the
    // level crossed the surface, so the branch differs somewhere on
    // either side of it and 200 doublings of a ulp cover every distance
    // a double expresses -- which is why the message itself is what is
    // pinned here. The code says so where it throws.
    const error = unlanded('the rack drives wheel.turn', 'wheel.turn',
                           'floor', 200);
    expect(error).toBeInstanceOf(LandingInvariantError);
    expect(error.message).toContain('the rack drives wheel.turn');
    expect(error.message).toContain('wheel.turn was cut at a surface of '
                                    + 'floor');
    expect(error.message).toContain('200 doublings of a ulp');
    expect(error.message).toContain('the cut placed the coordinate nowhere');
    expect(error.message).toContain('broken invariant of the run rather than '
                                    + 'a dt that is too coarse');
    expect(error.message).toContain('The tick committed nothing');
  });
});

// ---------------------------------------------------------------------
// The walk's own arithmetic (design D5). The producer's `HeldAngle`:
// a self-read dial whose law is `setter + ring * (wheel > 0.5) *
// (lift < 0.5)`, with the setter standing at 72, the ring at zero and
// only the LIFT moving. The lift's comparison is an OUTER node and the
// dial's own is a DEPENDENT one, so moving the lift alone re-partitions
// the tick while every term of the substituted law stands exactly where
// it stood -- and a piece whose skeleton does not move must leave the
// coordinate at the EXACT float it held.
//
// A version 6 document with no block anywhere: this is a correction to
// the walk, not to the block.
// ---------------------------------------------------------------------

/** `HeldAngle`, loadable: rest `71.99999999999996`, setter `72`. */
function heldAngle(rest = 71.99999999999996): LoadedProgram {
  return loadProgram({
    format: 'solid-node-export',
    version: 6,
    drivers: {
      setter: {
        default: 72, range: null, unit: 'deg', dtype: null, scale: null,
      },
      lift: { default: 0, range: null, unit: 'mm', dtype: null, scale: null },
      ring: { default: 0, range: null, unit: 'deg', dtype: null, scale: null },
    },
    instructions: {},
    program: {
      identity: 'held-angle',
      clock: 'time',
      coordinates: {
        setter: { kind: 'input', initial: 72, domain: null },
        lift: { kind: 'input', initial: 0, domain: null },
        ring: { kind: 'input', initial: 0, domain: null },
        'wheel.turn': {
          kind: 'coordinate', initial: rest, unit: 'deg', domain: 'rotational',
        },
      },
      intermediates: [],
      edges: [{
        kind: 'law',
        needs: ['setter', 'lift', 'ring', 'wheel.turn'],
        gives: ['wheel.turn'],
        description: '(setter, lift, ring, wheel.turn) drives wheel.turn',
        stated_by: 'HeldAngle',
        expressions: [
          '(setter + ((ring * (wheel.turn > 0.5)) * (lift < 0.5)))',
        ],
        affine: [true],
        plans: [{
          skeleton: '(setter + ((ring * _j0) * _j1))',
          jumps: [
            {
              name: '_j0', primitive: '>', level: '(wheel.turn - 0.5)',
              affine: true,
            },
            {
              name: '_j1', primitive: '<', level: '(lift - 0.5)',
              affine: true,
            },
          ],
        }],
      }],
      spans: {},
      sources: {
        setter: ['setter'], lift: ['lift'], ring: ['ring'],
        'wheel.turn': ['setter', 'lift', 'ring'],
      },
      limits: { ...LIMITS },
    },
  } as unknown as RunDocument, 'bench://held-angle');
}

describe('the walk\'s own arithmetic (design D5, tasks 2)', () => {
  it('2.1 a piece whose SKELETON does not move leaves the coordinate at '
     + 'the exact float it held', () => {
    const program = heldAngle();
    const held = 71.99999999999996;
    const reading = program.edges[0].retained[0]!;
    // The dial's own comparison is the DEPENDENT node and the lift's is
    // the independent one, which is the shape that makes this visible.
    expect(reading.dependent.map((jump) => jump.name)).toEqual(['_j0']);
    expect(reading.outer.jumps.map((jump) => jump.name)).toEqual(['_j1']);

    const { increment, landing } = retainedIncrement(
      program, reading,
      { setter: 72, lift: 0, ring: 0, 'wheel.turn': held },
      { setter: 0, lift: 0.2, ring: 0, 'wheel.turn': 0 },
      program.edges[0].description, 'wheel.turn', null, 1);

    // A TRUE zero, not an ulp: `own_left + (S - base)`, the difference
    // taken first. Read the other way round the dial lands on
    // 71.99999999999994, two ulps below where it stood, for no
    // mechanical reason at all.
    expect(landing).toBe(null);
    expect(Object.is(increment, 0)).toBe(true);
    expect(held + increment).toBe(held);
    expect(held + increment).not.toBe(71.99999999999994);
  });
});

// ---------------------------------------------------------------------
// A BLOCK, ordered PIECE BY PIECE (design D2-D4, tasks 6-9). The bench
// is the Curta's carry reduced to two members and one selector each:
// `higher.turn` is driven by the crank BELOW the detent and by the carry
// ABOVE it, and `carry.travel` by `higher.turn` BELOW it -- so the pair
// is a cycle whose active direction FLIPS with `shift`.
// ---------------------------------------------------------------------

/** One corpus machine's published document, by name. */
function machine(name: string): RunDocument {
  const found = (corpus as unknown as {
    machines: { name: string; document: RunDocument }[];
  }).machines.find((one) => one.name === name);
  return found!.document;
}

function blockBench(coordinates: Record<string, unknown>,
                    edges: unknown[]): LoadedProgram {
  const ids = Object.keys(coordinates);
  const inputs = ids.filter(
    (id) => (coordinates[id] as { kind: string }).kind === 'input');
  return loadProgram({
    format: 'solid-node-export',
    version: 7,
    drivers: Object.fromEntries(inputs.map((id) => [id, {
      default: 0, range: null, unit: null, dtype: null, scale: null,
    }])),
    instructions: {},
    program: {
      identity: 'block-bench',
      clock: 'time',
      coordinates,
      intermediates: [],
      edges,
      spans: {},
      sources: Object.fromEntries(
        ids.map((id) => [id, inputs.includes(id) ? [id] : inputs])),
      limits: { ...LIMITS },
    },
  } as unknown as RunDocument, 'bench://block');
}

const blockInput = (initial: number) =>
  ({ kind: 'input', initial, domain: null });
const blockCoordinate = (initial: number) =>
  ({ kind: 'coordinate', initial, unit: null, domain: null });

/** The two-member detent bench. */
function detent(higher = 0, carry = 0): LoadedProgram {
  return blockBench({
    crank: blockInput(0),
    shift: blockInput(0),
    'higher.turn': blockCoordinate(higher),
    'carry.travel': blockCoordinate(carry),
  }, [
    {
      kind: 'law',
      needs: ['crank', 'shift', 'carry.travel'],
      gives: ['higher.turn'],
      description: 'the crank drives higher.turn',
      stated_by: 'Bench',
      expressions: [
        '((crank * (shift < 0.5)) + (carry.travel * (shift >= 0.5)))',
      ],
      affine: [true],
      plans: [{
        skeleton: '((crank * _j0) + (carry.travel * _j1))',
        jumps: [
          { name: '_j0', primitive: '<', level: '(shift - 0.5)',
            affine: true },
          { name: '_j1', primitive: '>=', level: '(shift - 0.5)',
            affine: true },
        ],
      }],
    },
    {
      kind: 'law',
      needs: ['higher.turn', 'shift'],
      gives: ['carry.travel'],
      description: 'higher.turn drives carry.travel',
      stated_by: 'Bench',
      expressions: ['(higher.turn * (shift < 0.5))'],
      affine: [true],
      plans: [{
        skeleton: '(higher.turn * _j2)',
        jumps: [
          { name: '_j2', primitive: '<', level: '(shift - 0.5)',
            affine: true },
        ],
      }],
    },
  ]);
}

/** `LandedCarry`'s shape: the lever is pushed by the lower wheel while
 * the carriage is below the detent and only until it is HOME -- an
 * ADR-121 read of its own travel, which cuts the path and LANDS it --
 * and by the higher wheel above the detent, with no gate at all, so a
 * later piece of the same tick moves it on. */
function landedCarry(): LoadedProgram {
  return blockBench({
    crank: blockInput(0),
    shift: blockInput(0),
    'lower.turn': blockCoordinate(0),
    'higher.turn': blockCoordinate(0),
    'carry.travel': blockCoordinate(0),
  }, [
    {
      kind: 'wiring', needs: ['crank'], gives: ['lower.turn'], factor: 1.0,
      description: 'the crank is wired to lower.turn', stated_by: 'Bench',
    },
    {
      kind: 'law',
      needs: ['crank', 'shift', 'carry.travel'],
      gives: ['higher.turn'],
      description: '(crank, shift, carry.travel) drives higher.turn',
      stated_by: 'Bench',
      expressions: [
        '(((crank * (shift < 0.5)) * (carry.travel >= 0.5)) '
        + '+ (crank * (shift >= 0.5)))',
      ],
      affine: [true],
      plans: [{
        skeleton: '(((crank * _j0) * _j1) + (crank * _j2))',
        jumps: [
          { name: '_j0', primitive: '<', level: '(shift - 0.5)',
            affine: true },
          { name: '_j1', primitive: '>=', level: '(carry.travel - 0.5)',
            affine: true },
          { name: '_j2', primitive: '>=', level: '(shift - 0.5)',
            affine: true },
        ],
      }],
    },
    {
      kind: 'law',
      needs: ['lower.turn', 'higher.turn', 'shift', 'carry.travel'],
      gives: ['carry.travel'],
      description: '(lower.turn, higher.turn, shift, carry.travel) drives '
        + 'carry.travel',
      stated_by: 'Bench',
      expressions: [
        '(((lower.turn * (shift < 0.5)) * (carry.travel < 1.0)) '
        + '+ (higher.turn * (shift >= 0.5)))',
      ],
      affine: [true],
      plans: [{
        skeleton: '(((lower.turn * _j3) * _j4) + (higher.turn * _j5))',
        jumps: [
          { name: '_j3', primitive: '<', level: '(shift - 0.5)',
            affine: true },
          { name: '_j4', primitive: '<', level: '(carry.travel - 1.0)',
            affine: true },
          { name: '_j5', primitive: '>=', level: '(shift - 0.5)',
            affine: true },
        ],
      }],
    },
  ]);
}

/** The block of a loaded bench, and a spy that records every branch
 * vector the ordering was asked for. */
function watched(block: ProgramBlock) {
  const asked: Record<string, number>[] = [];
  const spied: ProgramBlock = {
    members: block.members,
    gives: block.gives,
    activeReads: (index, forced) => {
      asked.push(forced);
      return block.activeReads(index, forced);
    },
  };
  return { spied, asked };
}

describe('a block is ordered PIECE BY PIECE (design D2, tasks 6)', () => {
  it('6.2 the SELECTOR partition is located over the WHOLE stretch, in '
     + 'the members\' order and each member\'s postorder', () => {
    const program = detent();
    const block = program.edges[0].block!;
    const crossings: CrossingRecord[] = [];
    blockIncrements(program, block,
                    { crank: 0, shift: 0, 'higher.turn': 0,
                      'carry.travel': 0 },
                    { crank: 2, shift: 1, 'higher.turn': 0,
                      'carry.travel': 0 },
                    crossings, 7, {});
    // `shift` sweeps its detent at exactly half the stretch, and the
    // selectors are located there -- in the members' own order, each
    // under that member's description and driven coordinate.
    //
    // TWO crossings and not three: the first member's `>=` reads the
    // SAME surface as its `<`, and once the `<` has cut the path at 0.5
    // the `>=` is asked over `[0, 0.5]` and `[0.5, 1]`, where
    // `surfacesOf(..., inclusive = false)` does not count a surface a
    // piece begins or ends on. That is ADR-107's own partition, reached
    // here unchanged.
    const selectors = crossings.filter((one) => one.t === 0.5);
    expect(selectors).toHaveLength(2);
    expect(selectors.map((one) => one.primitive)).toEqual(['<', '<']);
    expect(selectors.map((one) => one.coordinate)).toEqual(
      ['higher.turn', 'carry.travel']);
    expect(selectors.map((one) => one.relation)).toEqual([
      'the crank drives higher.turn', 'higher.turn drives carry.travel',
    ]);
    expect(selectors.every((one) => one.tick === 7)).toBe(true);
    // And the partition itself is what `edgeCuts` answers for a block.
    expect(blockCuts(program, block,
                     { crank: 0, shift: 0, 'higher.turn': 0,
                       'carry.travel': 0 },
                     { crank: 2, shift: 1, 'higher.turn': 0,
                       'carry.travel': 0 })).toEqual([0, 0.5, 1]);
  });

  it('6.3 the order is memoised by the branch VALUE vector: a `floor` '
     + 'selector passing three windows makes FOUR keys and not one', () => {
    const program = blockBench({
      crank: blockInput(0),
      index: blockInput(0),
      'a.turn': blockCoordinate(0),
      'b.travel': blockCoordinate(0),
    }, [
      {
        kind: 'law',
        needs: ['crank', 'index', 'b.travel'],
        gives: ['a.turn'],
        description: 'the crank drives a.turn',
        stated_by: 'Bench',
        expressions: ['((crank * floor(index)) + (b.travel * (index >= 10.0)))'],
        affine: [true],
        plans: [{
          skeleton: '((crank * _j0) + (b.travel * _j1))',
          jumps: [
            { name: '_j0', primitive: 'floor', level: 'index', affine: true },
            { name: '_j1', primitive: '>=', level: '(index - 10.0)',
              affine: true },
          ],
        }],
      },
      {
        kind: 'law',
        needs: ['a.turn', 'index'],
        gives: ['b.travel'],
        description: 'a.turn drives b.travel',
        stated_by: 'Bench',
        expressions: ['(a.turn * (index >= 10.0))'],
        affine: [true],
        plans: [{
          skeleton: '(a.turn * _j2)',
          jumps: [
            { name: '_j2', primitive: '>=', level: '(index - 10.0)',
              affine: true },
          ],
        }],
      },
    ]);
    const { spied, asked } = watched(program.edges[0].block!);
    blockIncrements(program, spied,
                    { crank: 0, index: 0, 'a.turn': 0, 'b.travel': 0 },
                    { crank: 1, index: 3.5, 'a.turn': 0, 'b.travel': 0 },
                    null, 0, null);
    // Four pieces, four DISTINCT keys, two members asked per key.
    expect(asked).toHaveLength(8);
    const windows = asked.filter((entry) => '_j0' in entry)
      .map((entry) => entry._j0);
    expect(windows).toEqual([0, 1, 2, 3]);
    // Keyed by the VALUE and not by a boolean: four keys, not one.
    const keys = new Set(asked.map((entry) => JSON.stringify(entry)));
    expect(keys.size).toBe(4 + 1);
  });

  it('6.4 a still-cyclic piece REFUSES the tick, word for word, with the '
     + 'piece bounds, the relations and each selector\'s primitive, level '
     + 'and value', () => {
    // The producer's `BothActive`: two laws each gated `shift >= 0.5`,
    // orderable below the detent and cyclic above it.
    const program = blockBench({
      crank: blockInput(0),
      shift: blockInput(0),
      'lower.turn': blockCoordinate(0),
      'higher.turn': blockCoordinate(0),
    }, [
      {
        kind: 'law',
        needs: ['crank', 'shift', 'higher.turn'],
        gives: ['lower.turn'],
        description: '(crank, shift, higher.turn) drives lower.turn',
        stated_by: 'BothActive',
        expressions: ['(crank + (higher.turn * (shift >= 0.5)))'],
        affine: [true],
        plans: [{
          skeleton: '(crank + (higher.turn * _j0))',
          jumps: [{ name: '_j0', primitive: '>=', level: '(shift - 0.5)',
                    affine: true }],
        }],
      },
      {
        kind: 'law',
        needs: ['crank', 'shift', 'lower.turn'],
        gives: ['higher.turn'],
        description: '(crank, shift, lower.turn) drives higher.turn',
        stated_by: 'BothActive',
        expressions: ['(crank + (lower.turn * (shift >= 0.5)))'],
        affine: [true],
        plans: [{
          skeleton: '(crank + (lower.turn * _j1))',
          jumps: [{ name: '_j1', primitive: '>=', level: '(shift - 0.5)',
                    affine: true }],
        }],
      },
    ]);
    const block = program.edges[0].block!;
    const values = { crank: 0, shift: 0, 'lower.turn': 0, 'higher.turn': 0 };
    // BELOW the detent the whole stretch orders.
    expect(blockIncrements(program, block, values,
                           { crank: 1, shift: 0, 'lower.turn': 0,
                             'higher.turn': 0 }, null, 0, null))
      .toEqual([['lower.turn', 1], ['higher.turn', 1]]);
    // Driven PAST it, the piece above the detent is refused.
    let error: unknown = null;
    try {
      blockIncrements(program, block, values,
                      { crank: 1, shift: 1, 'lower.turn': 0,
                        'higher.turn': 0 }, null, 0, null);
    } catch (thrown) {
      error = thrown;
    }
    expect(error).toBeInstanceOf(UnsupportedLaw);
    const message = String((error as Error).message);
    expect(message).toContain('over the piece [0.5, 1] of this tick the '
                              + 'relations');
    expect(message).toContain('(crank, shift, higher.turn) drives '
                              + 'lower.turn, (crank, shift, lower.turn) '
                              + 'drives higher.turn');
    expect(message).toContain('form a cycle the run cannot order: each '
                              + 'waits on a coordinate another determines');
    expect(message).toContain('the selection this piece was read under '
                              + 'leaves every dependency on this cycle '
                              + 'active');
    expect(message).toContain(
      'The selectors read lower.turn: >= on (shift - 0.5) reads 1; '
      + 'higher.turn: >= on (shift - 0.5) reads 1.');
    expect(message).toContain('The tick committed nothing: the bank, the '
                              + 'tick count and the tree stand as they '
                              + 'were.');
    // It is an `UnsupportedLaw`, so `RefusalKind` gains nothing.
    expect(refusalKind(error)).toBe('law');
  });

  it('6.5 a member reading a coordinate the block gives is handed what '
     + 'THIS piece advanced it to, not zero', () => {
    const program = detent();
    const block = program.edges[0].block!;
    // Below the detent the crank drives `higher.turn`, which drives
    // `carry.travel` IN THE SAME PIECE: the second member must see the
    // first member's own increment.
    expect(blockIncrements(program, block,
                           { crank: 0, shift: 0, 'higher.turn': 0,
                             'carry.travel': 0 },
                           { crank: 2, shift: 0, 'higher.turn': 0,
                             'carry.travel': 0 }, null, 0, null))
      .toEqual([['higher.turn', 2], ['carry.travel', 2]]);
  });

  it('6.5 the ORDER flips with the selection, and a source the block '
     + 'does not give moves by `deltas * (right - left)` on its piece',
     () => {
    const program = detent();
    const { spied, asked } = watched(program.edges[0].block!);
    const found = blockIncrements(program, spied,
                                  { crank: 0, shift: 0, 'higher.turn': 0,
                                    'carry.travel': 0 },
                                  { crank: 2, shift: 1, 'higher.turn': 0,
                                    'carry.travel': 0 }, null, 0, null);
    // Piece one, below the detent: the crank turns the wheel by its own
    // travel over HALF the stretch, and the wheel carries the lever.
    // Piece two, above it: the wheel reads the lever and the lever
    // reads nothing, so the lever runs FIRST and moves by nothing.
    expect(found).toEqual([['higher.turn', 1], ['carry.travel', 1]]);
    expect(asked.map((entry) => JSON.stringify(entry))).toEqual([
      '{"_j0":1,"_j1":0}', '{"_j2":1}',
      '{"_j0":0,"_j1":1}', '{"_j2":0}',
    ]);
  });

  it('6.6 the in-block value is ADVANCED between pieces: the producer\'s '
     + 'own negative control, which sums to 2.0 rather than 1.0', () => {
    // `spikes/pieces.py`: the lever edge `(lower.turn, carry.travel)
    // drives carry.travel`, law `lo * (own < 1)`, over a stretch in
    // which `lower.turn` sweeps 0 -> 2 from `carry.travel == 0`.
    const program = blockBench({
      'lower.turn': blockInput(0),
      'carry.travel': blockCoordinate(0),
    }, [{
      kind: 'law',
      needs: ['lower.turn', 'carry.travel'],
      gives: ['carry.travel'],
      description: '(lower.turn, carry.travel) drives carry.travel',
      stated_by: 'FixedZero',
      expressions: ['(lower.turn * (carry.travel < 1.0))'],
      affine: [true],
      plans: [{
        skeleton: '(lower.turn * _j0)',
        jumps: [{ name: '_j0', primitive: '<', level: '(carry.travel - 1.0)',
                  affine: true }],
      }],
    }]);
    const edge = program.edges[0];
    const over = (left: number, right: number, own: number) => {
      const values = { 'lower.turn': 0 + 2 * left, 'carry.travel': own };
      const deltas = { 'lower.turn': 2 * (right - left), 'carry.travel': 0 };
      const found: CrossingRecord[] = [];
      const landings: Record<string, number> = {};
      const got = Object.fromEntries(edgeIncrements(
        program, edge, values, deltas, found, 0, landings));
      return { increment: got['carry.travel'], landings, found };
    };

    const whole = over(0, 1, 0);
    expect(whole.increment).toBe(1);
    expect(whole.landings['carry.travel']).toBe(1);
    expect(whole.found.map((one) => [one.primitive, one.level, one.t]))
      .toEqual([['<', 0, 0.5]]);

    // Piece by piece, cut at 0.25 and 0.6, the in-block coordinate
    // ADVANCED.
    const pieces: [number, number][] = [[0, 0.25], [0.25, 0.6], [0.6, 1]];
    let own = 0;
    let total = 0;
    let landing: number | null = null;
    const rescaled: number[] = [];
    for (const [left, right] of pieces) {
      const piece = over(left, right, own);
      total += piece.increment;
      const found = piece.landings['carry.travel'];
      own = found === undefined ? own + piece.increment : found;
      if (found !== undefined) landing = own;
      for (const one of piece.found) {
        rescaled.push(left + one.t * (right - left));
      }
    }
    expect(total).toBe(1);
    expect(landing).toBe(1);
    expect(own).toBe(1);
    // The crossing rescales to exactly the fraction the whole-stretch
    // run reported.
    expect(rescaled).toEqual([0.5]);

    // THE NEGATIVE CONTROL: the same three pieces with the in-block
    // value NOT advanced. This is the one thing the implementation must
    // not get wrong, and the producer measured it rather than asserting
    // it.
    let unadvanced = 0;
    for (const [left, right] of pieces) unadvanced += over(left, right, 0).increment;
    expect(unadvanced).toBe(2);
  });

  it('6.7 a member\'s own crossings are rescaled out of their piece and '
     + 'the WHOLE located list is sorted by fraction', () => {
    const program = landedCarry();
    const block = program.edges[1].block!;
    const crossings: CrossingRecord[] = [];
    blockIncrements(program, block,
                    { crank: 0, shift: 0, 'lower.turn': 0, 'higher.turn': 0,
                      'carry.travel': 0 },
                    { crank: 4, shift: 1, 'lower.turn': 4, 'higher.turn': 0,
                      'carry.travel': 0 },
                    crossings, 3, {});
    // Sorted by the fraction of the stretch, whichever was computed
    // first.
    const fractions = crossings.map((one) => one.t);
    expect([...fractions].sort((a, b) => a - b)).toEqual(fractions);
    expect(crossings.map((one) => [one.coordinate, one.primitive, one.t]))
      .toEqual([
        // The lever's OWN gate, cut strictly inside the first piece and
        // rescaled out of it, and the wheel's own latch on the lever
        // reaching its set point -- both before the detent.
        ['carry.travel', '<', 0.25],
        ['higher.turn', '>=', 0.25],
        // Then the two selectors, located over the WHOLE stretch.
        ['higher.turn', '<', 0.5],
        ['carry.travel', '<', 0.5],
      ]);
  });

  it('8.1 what a block REPORTS for a coordinate a piece landed is the '
     + 'ADVANCED ABSOLUTE at the stretch\'s end, not the landing', () => {
    const program = landedCarry();
    const block = program.edges[1].block!;
    const values = { crank: 0, shift: 0, 'lower.turn': 0, 'higher.turn': 0,
                     'carry.travel': 0 };
    const landings: Record<string, number> = {};
    const found = blockIncrements(program, block, values,
                                  { crank: 4, shift: 1, 'lower.turn': 4,
                                    'higher.turn': 0, 'carry.travel': 0 },
                                  null, 0, landings);
    // The lever lands at its gate in the first piece and the higher
    // wheel drives it further in the second.
    expect(found).toEqual([['higher.turn', 3], ['carry.travel', 3]]);
    expect(landings['carry.travel']).toBe(3);
    // `Run.landed` OVERWRITES `value + delta` with a reported landing,
    // so the advanced absolute is what must be reported: it is
    // `values + total`, and it is NOT the landing itself.
    expect(landings['carry.travel'])
      .toBe(values['carry.travel'] + found[1][1]);

    // The landing itself, measured: the SAME stretch truncated at the
    // detent, where the lever lands and nothing moves it after. Three is
    // not one -- the producer measured exactly this, `1.0 != 3.0`, by
    // reverting to the other rule.
    const truncated: Record<string, number> = {};
    blockIncrements(program, block, values,
                    { crank: 2, shift: 0.5, 'lower.turn': 2,
                      'higher.turn': 0, 'carry.travel': 0 },
                    null, 0, truncated);
    expect(truncated['carry.travel']).toBe(1);
    expect(landings['carry.travel']).not.toBe(truncated['carry.travel']);
  });

  it('8.1 a coordinate NO piece landed is reported as an increment only',
     () => {
    const program = detent();
    const landings: Record<string, number> = {};
    blockIncrements(program, program.edges[0].block!,
                    { crank: 0, shift: 0, 'higher.turn': 0,
                      'carry.travel': 0 },
                    { crank: 2, shift: 1, 'higher.turn': 0,
                      'carry.travel': 0 }, null, 0, landings);
    expect(landings).toEqual({});
  });

  it('6.8 the two-argument call shape: complete, side-effect-free and '
     + 'recording nothing -- and still refusing a cyclic piece', () => {
    const program = detent();
    const block = program.edges[0].block!;
    const values = { crank: 0, shift: 0, 'higher.turn': 0,
                     'carry.travel': 0 };
    const deltas = { crank: 2, shift: 1, 'higher.turn': 0,
                     'carry.travel': 0 };
    const crossings: CrossingRecord[] = [];
    const landings: Record<string, number> = {};
    const recorded = blockIncrements(program, block, { ...values },
                                     { ...deltas }, crossings, 1, landings);
    const quiet = blockIncrements(program, block, { ...values },
                                  { ...deltas }, null, 0, null);
    expect(quiet).toEqual(recorded);
    expect(crossings.length).toBeGreaterThan(0);
    // Nothing the caller passed was mutated.
    expect(values).toEqual({ crank: 0, shift: 0, 'higher.turn': 0,
                            'carry.travel': 0 });
    expect(deltas).toEqual({ crank: 2, shift: 1, 'higher.turn': 0,
                            'carry.travel': 0 });
  });
});

describe('the forced branch, threaded (design D3, tasks 7)', () => {
  /** `LandedCarry`'s lever: its two SELECTORS sit in ADR-057's
   * independent layer and its LATCH -- a read of its own travel -- in
   * the dependent one. */
  const lever = () => {
    const program = landedCarry();
    // The two members are contracted into ONE block entry, so the
    // member's own edge is reached through the block.
    const member = program.edges[1].block!.members[1];
    return { program, edge: member.edge, reading: member.edge.retained[0]! };
  };

  it('7.1 a selector is always an INDEPENDENT node in ADR-057\'s split, '
     + 'which is a consequence and not an assumption', () => {
    const { reading } = lever();
    expect(reading.outer.jumps.map((jump) => jump.name))
      .toEqual(['_j3', '_j5']);
    expect(reading.dependent.map((jump) => jump.name)).toEqual(['_j4']);
  });

  it('7.2 the forced branch is held through the WHOLE walk, the far-side '
     + 'landing included, and flipping it CHANGES THE ANSWER', () => {
    const { program, edge, reading } = lever();
    const start = { 'lower.turn': 0, 'higher.turn': 0, shift: 0,
                    'carry.travel': 0 };
    const delta = { 'lower.turn': 1, 'higher.turn': 0, shift: 0,
                    'carry.travel': 0 };
    const under = (forced: Record<string, number>) => retainedIncrement(
      program, reading, start, delta, edge.description, 'carry.travel',
      null, 0, forced);
    // Below the detent the lower wheel pushes the lever.
    expect(under({ _j3: 1, _j5: 0 }).increment).toBe(1);
    // Above it the lever reads the HIGHER wheel, which is not moving:
    // the producer's own reverted-forcing measurement, `0.0 != 1.0`.
    expect(under({ _j3: 0, _j5: 1 }).increment).toBe(0);

    // And with the lower wheel driven past the latch's surface the walk
    // CUTS and lands, still under the branch the block forced.
    const landed = retainedIncrement(
      program, reading, start,
      { ...delta, 'lower.turn': 2 }, edge.description, 'carry.travel',
      null, 0, { _j3: 1, _j5: 0 });
    expect(landed.landing).not.toBe(null);
    expect(landed.landing).toBeCloseTo(1, 12);
    expect(landed.increment).toBe(landed.landing);
  });

  it('7.4 a FORCED node\'s crossings are NOT located inside the piece: '
     + 'the block located them over the whole stretch already', () => {
    const { program, edge, reading } = lever();
    const start = { 'lower.turn': 0, 'higher.turn': 0, shift: 0,
                    'carry.travel': 0 };
    const delta = { 'lower.turn': 1, 'higher.turn': 0, shift: 1,
                    'carry.travel': 0 };
    const unforced: CrossingRecord[] = [];
    retainedIncrement(program, reading, start, delta, edge.description,
                      'carry.travel', unforced, 0);
    // The selector's own surface, located by the member itself.
    expect(unforced.map((one) => [one.primitive, one.level, one.t]))
      .toEqual([['<', 0, 0.5]]);

    const forced: CrossingRecord[] = [];
    retainedIncrement(program, reading, start, delta, edge.description,
                      'carry.travel', forced, 0, { _j3: 1, _j5: 0 });
    expect(forced).toEqual([]);
  });

  it('7.4 `partition` skips a forced node and `branchesAt` returns the '
     + 'forced value: the ONLY two places forcing is read', () => {
    const { program, edge } = lever();
    const plan = edge.plans[0]!;
    const start = { 'lower.turn': 0, 'higher.turn': 0, shift: 0,
                    'carry.travel': 0 };
    const delta = { 'lower.turn': 1, 'higher.turn': 0, shift: 1,
                    'carry.travel': 0 };
    // Unforced, the selector cuts the path at the detent.
    expect(planCuts(program, plan, start, delta, edge.description,
                    'carry.travel')).toEqual([0, 0.5, 1]);
    // Forced, it does not.
    expect(planCuts(program, plan, start, delta, edge.description,
                    'carry.travel', { _j3: 1, _j5: 0 })).toEqual([0, 1]);
    // And the branch the caller forced is the one the increment runs
    // under, whatever the level would have said.
    expect(planIncrement(program, plan, start, delta, edge.description,
                         'carry.travel', null, 0, { _j3: 0, _j5: 1 }))
      .toBe(0);
  });

  it('7.5 a law with NO block pays exactly one optional argument: every '
     + 'call with `forced` omitted is the call with `forced` null', () => {
    const program = clearing();
    const reading = readingOf(program);
    const start = { setter: 0, ring: 0, 'wheel.turn': 108 };
    const delta = { setter: 0, ring: 600, 'wheel.turn': 0 };
    const plain = retainedIncrement(program, reading, start, delta,
                                    'described', 'wheel.turn', null, 0);
    const explicit = retainedIncrement(program, reading, start, delta,
                                       'described', 'wheel.turn', null, 0,
                                       null);
    expect(explicit).toEqual(plain);
    expect(retainedCuts(program, reading, start, delta, 'described',
                        'wheel.turn', null))
      .toEqual(retainedCuts(program, reading, start, delta, 'described',
                            'wheel.turn'));
    const sawtoothPlan = planOf(sawtooth());
    const sawtoothProgram = sawtooth();
    expect(planIncrement(sawtoothProgram, sawtoothPlan, { crank: 0 },
                         { crank: 2.5 }, 'd', 'wheel.turn', null, 0, null))
      .toBe(planIncrement(sawtoothProgram, sawtoothPlan, { crank: 0 },
                          { crank: 2.5 }, 'd', 'wheel.turn', null, 0));
  });
});

describe('the framework\'s own numbers, mirrored (tasks 9)', () => {
  /** The corpus's own `ShiftedCarry` document, loaded. */
  const shifted = (swap = false) => {
    const source = JSON.parse(JSON.stringify(machine('ShiftedCarry')));
    if (swap) {
      const edges = source.program.edges;
      [edges[1], edges[2]] = [edges[2], edges[1]];
    }
    return loadProgram(source as RunDocument, 'corpus://ShiftedCarry');
  };

  it('9.1 one tick at dt = 1.0 cranked by 2.0: `lower.turn 2.0`, '
     + '`higher.turn 1.0`, `carry.travel 1.0` -- whatever order the two '
     + 'members are published in', () => {
    for (const swap of [false, true]) {
      const program = shifted(swap);
      const values: Record<string, number> = {
        clearing: 0, crank: 0, shift: 0, 'carry.travel': 0,
        'higher.turn': 0, 'lower.turn': 0,
      };
      const deltas: Record<string, number> = {
        clearing: 0, crank: 2, shift: 0, 'carry.travel': 0,
        'higher.turn': 0, 'lower.turn': 0,
      };
      const found: Record<string, number> = {};
      for (const edge of program.edges) {
        for (const [key, increment] of edgeIncrements(
          program, edge, values, deltas, null, 0, null)) {
          deltas[key] = increment;
          found[key] = increment;
        }
      }
      expect(found['lower.turn']).toBe(2);
      expect(found['higher.turn']).toBe(1);
      expect(found['carry.travel']).toBe(1);
    }
  });
});
