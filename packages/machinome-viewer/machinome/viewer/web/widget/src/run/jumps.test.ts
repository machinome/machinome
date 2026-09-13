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
  along, branchOf, deduplicated, merged, planCuts, planIncrement, surfacesOf,
} from './jumps';
import { loadProgram } from './program';
import type { LoadedProgram, ProgramPlan, RunDocument } from './program';

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
