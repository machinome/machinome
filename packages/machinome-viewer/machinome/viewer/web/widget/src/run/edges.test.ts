/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// One step of the program: what it reads, what it determines, and how
// (`simulation/program.py`'s `class Edge`, reproduced).

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { prepare, valueOf } from '../expressions';
import { nest } from './scope';
import { loadProgram } from './program';
import type { LoadedProgram, RunDocument } from './program';
import { edgeCuts, edgeIncrements, edgeValues, linearOf, predictsOf } from './edges';
import wrappedV12 from './follow-wrapped-v12.json';

const LIMITS = {
  crossing_tolerance: 1e-12, subdivisions: 64, bisection_rounds: 64,
  max_crossings: 1000, agreement: 1e-9,
};

interface Bench {
  coordinates: Record<string, unknown>;
  intermediates?: string[];
  edges: unknown[];
  sources?: Record<string, string[]>;
  drivers?: Record<string, unknown>;
}

function bench(spec: Bench): LoadedProgram {
  const ids = Object.keys(spec.coordinates);
  const inputs = ids.filter(
    (id) => (spec.coordinates[id] as { kind: string }).kind === 'input');
  const sources: Record<string, string[]> = spec.sources ?? Object.fromEntries(
    [...ids, ...(spec.intermediates ?? [])].map(
      (id) => [id, inputs.includes(id) ? [id] : inputs]));
  const drivers = spec.drivers ?? Object.fromEntries(inputs.map((id) => [id, {
    default: 0, range: null, unit: null, dtype: null, scale: null,
  }]));
  return loadProgram({
    format: 'machinome-export',
    version: 5,
    drivers,
    instructions: {},
    program: {
      identity: 'bench',
      clock: 'time',
      coordinates: spec.coordinates,
      intermediates: spec.intermediates ?? [],
      edges: spec.edges,
      spans: {},
      sources,
      limits: { ...LIMITS },
    },
  } as unknown as RunDocument, 'bench://edges');
}

const input = (initial: number) =>
  ({ kind: 'input', initial, domain: null });
const coordinate = (initial: number) =>
  ({ kind: 'coordinate', initial, unit: null, domain: null });

it('evaluates a v12 Follow edge directly without propagation metadata', () => {
  const program = loadProgram(wrappedV12 as unknown as RunDocument, 'producer://follow_wrapped_v12.json');
  const landing: Record<string, number> = {};
  const result = edgeIncrements(program, program.edges[0], { ...program.initial },
    { low: 3, high: 0, 'ball.slide': 0 }, null, 0, landing);
  expect(result).toEqual([['ball.slide', 2]]);
  expect(landing['ball.slide']).toBe(2);
});

describe('a law', () => {
  const program = bench({
    coordinates: { crank: input(0), 'first.turn': coordinate(0) },
    edges: [{
      kind: 'law', needs: ['crank'], gives: ['first.turn'],
      description: 'crank drives first.turn', stated_by: 'Bench',
      expressions: ['(crank ^ 2)'], affine: [false], plans: [null],
    }],
  });
  const edge = program.edges[0];

  it('values its target at the committed state', () => {
    expect(edgeValues(program, edge, { crank: 3, 'first.turn': 0 }))
      .toEqual([['first.turn', 9]]);
  });

  it('increments by the DIFFERENCE of two evaluations, so a kink is exact', () => {
    const values = { crank: 3, 'first.turn': 9 };
    const deltas = { crank: 2, 'first.turn': 0 };
    expect(edgeIncrements(program, edge, values, deltas, null, 0))
      .toEqual([['first.turn', 25 - 9]]);
  });

  it('has no cuts without a plan', () => {
    expect(edgeCuts(program, edge, { crank: 3 }, { crank: 2 }, 0)).toEqual([]);
  });
});

describe('a play edge', () => {
  const program = bench({
    coordinates: { crank: input(0), wheel: coordinate(0) },
    edges: [{
      kind: 'play', needs: ['crank', 'wheel'], gives: ['wheel'],
      description: 'crank plays wheel', stated_by: 'Bench',
      low: -10, high: 10,
    }],
  });
  const edge = program.edges[0];

  it('collects at either flank and releases on reversal', () => {
    expect(edgeIncrements(program, edge, { crank: 0, wheel: 0 },
                          { crank: 30, wheel: 0 }, null, 0))
      .toEqual([['wheel', 20]]);
    expect(edgeIncrements(program, edge, { crank: 30, wheel: 20 },
                          { crank: -5, wheel: 0 }, null, 0))
      .toEqual([['wheel', 0]]);
    expect(edgeIncrements(program, edge, { crank: 25, wheel: 20 },
                          { crank: -30, wheel: 0 }, null, 0))
      .toEqual([['wheel', -15]]);
  });
});

describe('a constant law', () => {
  const program = bench({
    coordinates: { crank: input(0), pin: coordinate(7) },
    edges: [{
      kind: 'law', needs: ['crank'], gives: ['pin'],
      description: 'the pin holds', stated_by: 'Bench',
      expressions: [null], affine: [true], plans: [null],
    }],
  });
  const edge = program.edges[0];

  it('values as zero and contributes zero', () => {
    expect(edgeValues(program, edge, { crank: 5, pin: 7 }))
      .toEqual([['pin', 0]]);
    expect(edgeIncrements(program, edge, { crank: 5, pin: 7 },
                          { crank: 3, pin: 0 }, null, 0))
      .toEqual([['pin', 0]]);
  });
});

describe('a wiring', () => {
  const program = bench({
    coordinates: { crank: input(0), 'slide.travel': coordinate(0) },
    edges: [{
      kind: 'wiring', needs: ['crank'], gives: ['slide.travel'],
      description: 'crank wires slide.travel', stated_by: 'Bench',
      factor: 2.5,
    }],
  });
  const edge = program.edges[0];

  it('values source x factor and increments delta x factor', () => {
    expect(edgeValues(program, edge, { crank: 4, 'slide.travel': 0 }))
      .toEqual([['slide.travel', 10]]);
    expect(edgeIncrements(program, edge, { crank: 4, 'slide.travel': 10 },
                          { crank: 2, 'slide.travel': 0 }, null, 0))
      .toEqual([['slide.travel', 5]]);
  });
});

describe('a formula, forward', () => {
  const program = bench({
    coordinates: {
      a: input(0), b: input(0), derived: coordinate(0),
    },
    edges: [{
      kind: 'formula', needs: ['a', 'b'], gives: ['derived'],
      description: "the derived coordinate 'derived'", stated_by: 'Bench',
      factors: [2, 3], constant: 10, slot: 'derived',
    }],
  });
  const edge = program.edges[0];

  it('is constant + the linear combination, in needs order', () => {
    expect(edgeValues(program, edge, { a: 1, b: 2, derived: 0 }))
      .toEqual([['derived', 10 + 2 + 6]]);
  });

  it('increments with the constant replaced by zero', () => {
    expect(edgeIncrements(program, edge, { a: 1, b: 2, derived: 18 },
                          { a: 1, b: 1, derived: 0 }, null, 0))
      .toEqual([['derived', 5]]);
  });
});

describe('a formula, solved backward into its one term', () => {
  // The producer's own published shape: `needs` carries the SLOT first
  // with factor 0.0, then the other terms, then the solved-for term
  // last with its own coefficient.
  const program = bench({
    coordinates: {
      slot: input(0), other: input(0), own: coordinate(0),
    },
    edges: [{
      kind: 'formula', needs: ['slot', 'other', 'own'], gives: ['own'],
      description: "the derived coordinate 'own'", stated_by: 'Bench',
      factors: [0.0, 3, 2], constant: 10, slot: 'slot',
    }],
  });
  const edge = program.edges[0];

  it('is (slot - constant - the other terms) / its own coefficient', () => {
    // slot = 10 + 3*other + 2*own, so own = (slot - 10 - 3*other) / 2
    expect(edgeValues(program, edge, { slot: 30, other: 2, own: 0 }))
      .toEqual([['own', (30 - 10 - 6) / 2]]);
  });

  it('increments with the constant replaced by zero', () => {
    expect(edgeIncrements(program, edge,
                          { slot: 30, other: 2, own: 7 },
                          { slot: 4, other: 1, own: 0 }, null, 0))
      .toEqual([['own', (4 - 0 - 3) / 2]]);
  });
});

describe('a check', () => {
  const program = bench({
    coordinates: {
      slot: input(0), a: input(0), b: coordinate(0),
    },
    edges: [
      {
        kind: 'law', needs: ['a'], gives: ['b'],
        description: 'a drives b', stated_by: 'Bench',
        expressions: ['a'], affine: [true], plans: [null],
      },
      {
        kind: 'check', needs: ['slot', 'a', 'b'], gives: [],
        description: "the derived coordinate 'slot'", stated_by: 'Bench',
        factors: [0.0, 1, 1], constant: 5, slot: 'slot',
      },
    ],
  });
  const edge = program.edges[1];

  it('determines nothing', () => {
    expect(edgeValues(program, edge, { slot: 0, a: 1, b: 1 })).toEqual([]);
    expect(edgeIncrements(program, edge, { slot: 0, a: 1, b: 1 },
                          { slot: 0, a: 1, b: 1 }, null, 0)).toEqual([]);
  });

  it('predicts over every need but the slot', () => {
    expect(predictsOf(edge, { slot: 99, a: 1, b: 2 })).toBe(5 + 1 + 2);
    expect(predictsOf(edge, { slot: 0, a: 1, b: 2 }, 0)).toBe(3);
  });
});

describe('the accumulation order is the producer\'s', () => {
  // `total = total + held[key] * factor`, in `needs` order, and never a
  // re-association: these three terms sum to 1e16 in that order and to
  // 10000000000000002 in the other.
  const program = bench({
    coordinates: {
      big: input(0), one: input(0), two: input(0), derived: coordinate(0),
    },
    edges: [{
      kind: 'formula', needs: ['big', 'one', 'two'], gives: ['derived'],
      description: 'the sum', stated_by: 'Bench',
      factors: [1, 1, 1], constant: 0, slot: 'derived',
    }],
  });
  const edge = program.edges[0];
  const held = { big: 1e16, one: 1, two: 1, derived: 0 };

  it('sums in needs order, to the last bit', () => {
    expect(linearOf(edge, held)).toBe(1e16);
    // The same three numbers, re-associated, differ in the last bits --
    // which is what the corpus's 1e-9 window would hide until it did not.
    expect(((0 + 1) + 1) + 1e16).toBe(10000000000000002);
  });
});

describe('every evaluation gets a FRESH scope object (design D11)', () => {
  it('a mutated scope object returns the previous pass\'s number', () => {
    const id = prepare('(fresh.source * 3)');
    const reused = { time: 0, drivers: nest({ 'fresh.source': 2 }) };
    const first = valueOf(id, reused);
    // Mutating in place is exactly what the engine must never do: the
    // identity fast path sees the same object and reuses the memo.
    (reused.drivers as Record<string, Record<string, number>>)
      .fresh.source = 5;
    const second = valueOf(id, reused);
    expect(first).toBe(6);
    expect(second).toBe(6);

    const a = valueOf(id, { time: 0, drivers: nest({ 'fresh.source': 2 }) });
    const b = valueOf(id, { time: 0, drivers: nest({ 'fresh.source': 5 }) });
    expect(a).toBe(6);
    expect(b).toBe(15);
  });

  it('no module under src/run/ evaluates through a scope of its own', () => {
    // One call site, by construction: `evaluateExpression` in program.ts
    // builds a fresh literal per call and is the only thing in the
    // engine that reaches the evaluator at all.
    const sources = [
      'program.ts', 'edges.ts', 'jumps.ts', 'commands.ts', 'run.ts',
      'engine.ts', 'scope.ts', 'runtime.ts', 'worker.ts', 'protocol.ts',
    ];
    const callers: string[] = [];
    for (const name of sources) {
      let text: string;
      try {
        text = readFileSync(new URL(name, import.meta.url), 'utf8');
      } catch {
        continue;
      }
      if (/\bvalueOf\s*\(/.test(text) || /\bevalExpr\s*\(/.test(text)) {
        callers.push(name);
      }
    }
    expect(callers).toEqual(['program.ts']);
  });
});

// ---------------------------------------------------------------------
// A law that READS THE COORDINATE IT DRIVES: the dispatch, and the
// landing report (design D4, tasks 5.1).
// ---------------------------------------------------------------------

const CLEARING = {
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

function clearingProgram(): LoadedProgram {
  return bench({
    coordinates: {
      setter: { kind: 'input', initial: 0, domain: null },
      ring: { kind: 'input', initial: 0, domain: null },
      'wheel.turn': {
        kind: 'coordinate', initial: 108, unit: 'deg', domain: 'rotational',
      },
    },
    edges: [CLEARING],
    sources: {
      setter: ['setter'], ring: ['ring'], 'wheel.turn': ['ring', 'setter'],
    },
  });
}

describe('edgeIncrements reports a landing (design D4)', () => {
  it('5.1 fills `landings` for a driven end at least one of whose cuts '
     + 'placed it', () => {
    const program = clearingProgram();
    const edge = program.edges[0];
    const values = { setter: 0, ring: 100, 'wheel.turn': 108 };
    const deltas = { setter: 0, ring: 400, 'wheel.turn': 0 };
    const landings: Record<string, number> = {};
    const found = edgeIncrements(program, edge, values, deltas, null, 1,
                                 landings);
    expect(landings['wheel.turn']).toBe(359.5);
    expect(found).toEqual([['wheel.turn', 359.5 - 108]]);
  });

  it('5.1 reports NO landing where no cut placed the coordinate', () => {
    const program = clearingProgram();
    const landings: Record<string, number> = {};
    edgeIncrements(program, program.edges[0],
                   { setter: 0, ring: 0, 'wheel.turn': 108 },
                   { setter: 0, ring: 50, 'wheel.turn': 0 }, null, 1,
                   landings);
    expect(landings).toEqual({});
  });

  it('5.1 leaves `landings` alone for an edge with NO self-read -- one '
     + 'array-length test and nothing else', () => {
    const program = bench({
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'wheel.turn': {
          kind: 'coordinate', initial: 0, unit: null, domain: null,
        },
      },
      edges: [{
        kind: 'law', needs: ['crank'], gives: ['wheel.turn'],
        description: 'crank drives wheel.turn', stated_by: 'Bench',
        expressions: ['(crank - floor(crank))'], affine: [false],
        plans: [{
          skeleton: '(crank - _j0)',
          jumps: [{ name: '_j0', primitive: 'floor', level: 'crank',
                    affine: true }],
        }],
      }],
    });
    expect(program.edges[0].retained).toEqual([]);
    const landings: Record<string, number> = {};
    edgeIncrements(program, program.edges[0], { crank: 0, 'wheel.turn': 0 },
                   { crank: 2.5, 'wheel.turn': 0 }, null, 1, landings);
    expect(landings).toEqual({});
  });

  it('5.1 `edgeCuts` routes a self-read end through the two-layer walk', () => {
    const program = clearingProgram();
    const cuts = edgeCuts(program, program.edges[0],
                          { setter: 0, ring: 0, 'wheel.turn': 108 },
                          { setter: 0, ring: 600, 'wheel.turn': 0 }, 0);
    // Layer one's station crossings AND layer two's own band cut, which
    // `planCuts` alone would not have: the station opens at 1/6 and
    // closes at 5/6, and the dial reaches its gap in between.
    expect(cuts[0]).toBe(0);
    expect(cuts[cuts.length - 1]).toBe(1);
    expect(cuts.length).toBeGreaterThan(3);
  });
});

// ---------------------------------------------------------------------
// A BLOCK edge (design D2.1, D4.3, D4.4, tasks 6.1 and 8.3)
// ---------------------------------------------------------------------

/** The detent bench: two members whose active direction flips with
 * `shift`, contracted by the loader into ONE block entry. */
function detentBlock(): LoadedProgram {
  return bench({
    coordinates: {
      crank: input(0), shift: input(0),
      'higher.turn': coordinate(0), 'carry.travel': coordinate(0),
    },
    edges: [
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
    ],
  });
}

describe('a block edge', () => {
  const program = detentBlock();
  const edge = program.edges[0];
  const values = { crank: 0, shift: 0, 'higher.turn': 0, 'carry.travel': 0 };
  const deltas = { crank: 2, shift: 1, 'higher.turn': 0, 'carry.travel': 0 };

  it('6.1 is what the loader hands the run, and `edgeIncrements` routes '
     + 'to the block on `kind === "block"`', () => {
    expect(program.edges).toHaveLength(1);
    expect(edge.kind).toBe('block');
    expect(edge.block).not.toBe(null);
    expect(edgeIncrements(program, edge, values, deltas, null, 0, null))
      .toEqual([['higher.turn', 1], ['carry.travel', 1]]);
  });

  it('8.3 `edgeCuts` on a block is the SELECTOR partition, for either '
     + 'of its ends', () => {
    expect(edgeCuts(program, edge, values, deltas, 0)).toEqual([0, 0.5, 1]);
    expect(edgeCuts(program, edge, values, deltas, 1)).toEqual([0, 0.5, 1]);
    // A stretch no selector crosses is one piece.
    expect(edgeCuts(program, edge, values,
                    { ...deltas, shift: 0 }, 0)).toEqual([0, 1]);
  });

  it('8.3 `edgeValues` returns NOTHING for a block, and `Run.valuesOf` '
     + 'never asks: every give of a block is a bank key', () => {
    expect(edgeValues(program, edge, values)).toEqual([]);
    const bank = new Set(program.order);
    expect(edge.gives.every((key) => bank.has(key))).toBe(true);
  });
});
