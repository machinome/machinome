/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Loading a published program (design §4): read it verbatim, derive the
// little that is derivable, and refuse by name everything the engine
// cannot execute -- before a frame is rendered or a tick integrated.

import { describe, expect, it } from 'vitest';
import { EXPRESSION_LIMITS, expressionGeneration, prepare } from '../expressions';
import { loadProgram, uncomputedValues } from './program';
import type { RunDocument } from './program';
import acceptance from '../../../../tests/fixtures/pascaline/viewer.json';
import lockDocument from '../../../../tests/fixtures/lock/viewer.json';

const SOURCE = 'http://example.test/viewer.json';

const LIMITS = {
  crossing_tolerance: 1e-12,
  subdivisions: 64,
  bisection_rounds: 64,
  max_crossings: 1000,
  agreement: 1e-9,
};

interface Overrides { [key: string]: unknown }

/** A minimal, VALID version 5 document: one input, one coordinate, one
 * law. Every refusal case below is this document with one thing wrong. */
function document(program: Overrides = {},
                  document: Overrides = {}): RunDocument {
  return {
    format: 'solid-node-export',
    version: 5,
    drivers: {
      crank: {
        default: 0, range: null, unit: 'deg', dtype: null, scale: null,
      },
    },
    instructions: {},
    program: {
      identity: 'abc',
      clock: 'time',
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'first.turn': {
          kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
        },
      },
      intermediates: [],
      edges: [{
        kind: 'law',
        needs: ['crank'],
        gives: ['first.turn'],
        description: 'crank drives first.turn',
        stated_by: 'Bench',
        expressions: ['(2.0 * crank)'],
        affine: [true],
        plans: [null],
      }],
      spans: {},
      sources: { crank: ['crank'], 'first.turn': ['crank'] },
      limits: { ...LIMITS },
      ...program,
    },
    ...document,
  } as RunDocument;
}

function refusal(doc: RunDocument): string {
  try {
    loadProgram(doc, SOURCE);
  } catch (error) {
    return String((error as Error).message);
  }
  throw new Error('expected loadProgram to refuse this document');
}

describe('loadProgram refuses what it cannot execute (design §4)', () => {
  it('1. a version 5 document with no program', () => {
    const doc = document();
    delete (doc as Record<string, unknown>).program;
    const message = refusal(doc);
    expect(message).toContain('program');
    expect(message).toContain(SOURCE);
  });

  it('1. a program that is not an object', () => {
    expect(refusal(document({}, { program: 7 }))).toContain('program');
  });

  it('1. a missing published key, naming the key', () => {
    const doc = document();
    delete ((doc as Record<string, Overrides>).program).sources;
    expect(refusal(doc)).toContain('sources');
  });

  it('2. a coordinate whose kind is unknown', () => {
    const message = refusal(document({
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'first.turn': { kind: 'port', initial: 0, unit: null, domain: null },
      },
    }));
    expect(message).toContain('first.turn');
    expect(message).toContain('port');
  });

  it('2. a coordinate whose initial is not a finite number', () => {
    const message = refusal(document({
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'first.turn': {
          kind: 'coordinate', initial: null, unit: null, domain: null,
        },
      },
    }));
    expect(message).toContain('first.turn');
    expect(message).toContain('initial');
  });

  it('3. an input the drivers table does not declare', () => {
    const message = refusal(document({
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        lever: { kind: 'input', initial: 0, domain: null },
        'first.turn': {
          kind: 'coordinate', initial: 0, unit: null, domain: null,
        },
      },
      sources: { crank: ['crank'], lever: ['lever'], 'first.turn': ['crank'] },
    }));
    expect(message).toContain('lever');
  });

  it('3. a driver the program does not declare as an input', () => {
    const message = refusal(document({}, {
      drivers: {
        crank: { default: 0, range: null, unit: null, dtype: null, scale: null },
        lever: { default: 0, range: null, unit: null, dtype: null, scale: null },
      },
    }));
    expect(message).toContain('lever');
  });

  it('4. an id set that cannot be nested, naming both', () => {
    const message = refusal(document({
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'first.turn': {
          kind: 'coordinate', initial: 0, unit: null, domain: null,
        },
      },
      intermediates: ['first.turn.inner'],
      sources: {
        crank: ['crank'], 'first.turn': ['crank'], 'first.turn.inner': [],
      },
    }));
    expect(message).toContain('first.turn');
    expect(message).toContain('first.turn.inner');
  });

  it('5. a clock colliding with a coordinate', () => {
    const message = refusal(document({ clock: 'first.turn' }));
    expect(message).toContain('first.turn');
    expect(message).toContain('clock');
  });

  it('5. a clock colliding with a driver id', () => {
    const message = refusal(document({ clock: 'crank' }));
    expect(message).toContain('crank');
  });

  it('6. an edge whose kind the engine does not know', () => {
    const message = refusal(document({
      edges: [{
        kind: 'coupling', needs: ['crank'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench',
      }],
    }));
    expect(message).toContain('coupling');
    expect(message).toContain('law');
  });

  it('6. a law whose expressions are not aligned with gives', () => {
    const message = refusal(document({
      edges: [{
        kind: 'law', needs: ['crank'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench',
        expressions: ['crank', 'crank'], affine: [true], plans: [null],
      }],
    }));
    expect(message).toContain('expressions');
  });

  it('6. a law whose affine flags are not aligned with gives', () => {
    const message = refusal(document({
      edges: [{
        kind: 'law', needs: ['crank'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench',
        expressions: ['crank'], affine: [], plans: [null],
      }],
    }));
    expect(message).toContain('affine');
  });

  it('6. a check with a non-empty gives', () => {
    const message = refusal(document({
      edges: [
        {
          kind: 'law', needs: ['crank'], gives: ['first.turn'],
          description: 'd', stated_by: 'Bench',
          expressions: ['crank'], affine: [true], plans: [null],
        },
        {
          kind: 'check', needs: ['crank', 'first.turn'], gives: ['first.turn'],
          description: 'c', stated_by: 'Bench',
          factors: [1, 0], constant: 0, slot: 'first.turn',
        },
      ],
    }));
    expect(message).toContain('check');
    expect(message).toContain('gives');
  });

  it('6. a formula without a slot', () => {
    const message = refusal(document({
      edges: [{
        kind: 'formula', needs: ['crank'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench', factors: [2], constant: 0,
      }],
    }));
    expect(message).toContain('slot');
  });

  it('6. a formula whose factors are not aligned with needs', () => {
    const message = refusal(document({
      edges: [{
        kind: 'formula', needs: ['crank'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench', factors: [2, 3], constant: 0,
        slot: 'first.turn',
      }],
    }));
    expect(message).toContain('factors');
  });

  it('6. a formula without a constant', () => {
    const message = refusal(document({
      edges: [{
        kind: 'formula', needs: ['crank'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench', factors: [2],
        slot: 'first.turn',
      }],
    }));
    expect(message).toContain('constant');
  });

  it('7. a needs id naming a value nothing knows', () => {
    const message = refusal(document({
      edges: [{
        kind: 'law', needs: ['nowhere'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench',
        expressions: ['nowhere'], affine: [true], plans: [null],
      }],
    }));
    expect(message).toContain('nowhere');
  });

  it('7. a gives id naming a value nothing knows', () => {
    const message = refusal(document({
      edges: [{
        kind: 'law', needs: ['crank'], gives: ['nowhere'],
        description: 'd', stated_by: 'Bench',
        expressions: ['crank'], affine: [true], plans: [null],
      }],
    }));
    expect(message).toContain('nowhere');
  });

  it('8. a jump primitive outside the published ten', () => {
    const message = refusal(document({
      edges: [{
        kind: 'law', needs: ['crank'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench',
        expressions: ['round(crank)'], affine: [false],
        plans: [{
          skeleton: '_j0',
          jumps: [{
            name: '_j0', primitive: 'round', level: 'crank', affine: true,
          }],
        }],
      }],
    }));
    expect(message).toContain('round');
    expect(message).toContain('floor');
    expect(message).toContain('!=');
  });

  it('9. two plans sharing a placeholder', () => {
    const message = refusal(document({
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'first.turn': {
          kind: 'coordinate', initial: 0, unit: null, domain: null,
        },
        'second.turn': {
          kind: 'coordinate', initial: 0, unit: null, domain: null,
        },
      },
      sources: {
        crank: ['crank'], 'first.turn': ['crank'], 'second.turn': ['crank'],
      },
      edges: [
        {
          kind: 'law', needs: ['crank'], gives: ['first.turn'],
          description: 'a', stated_by: 'Bench',
          expressions: ['floor(crank)'], affine: [false],
          plans: [{
            skeleton: '_j0',
            jumps: [{
              name: '_j0', primitive: 'floor', level: 'crank', affine: true,
            }],
          }],
        },
        {
          kind: 'law', needs: ['crank'], gives: ['second.turn'],
          description: 'b', stated_by: 'Bench',
          expressions: ['ceil(crank)'], affine: [false],
          plans: [{
            skeleton: '_j0',
            jumps: [{
              name: '_j0', primitive: 'ceil', level: 'crank', affine: true,
            }],
          }],
        },
      ],
    }));
    expect(message).toContain('_j0');
  });

  it('10. a law expression whose free names are not among its needs', () => {
    const message = refusal(document({
      edges: [{
        kind: 'law', needs: ['crank'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench',
        expressions: ['(2.0 * lever)'], affine: [true], plans: [null],
      }],
    }));
    expect(message).toContain('lever');
  });

  it('10. a skeleton naming a placeholder that is not its plan\'s', () => {
    const message = refusal(document({
      edges: [{
        kind: 'law', needs: ['crank'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench',
        expressions: ['floor(crank)'], affine: [false],
        plans: [{
          skeleton: '_j9',
          jumps: [{
            name: '_j0', primitive: 'floor', level: 'crank', affine: true,
          }],
        }],
      }],
    }));
    expect(message).toContain('_j9');
  });

  it('10. a bound reading a name the program never declares', () => {
    const message = refusal(document({
      spans: {
        'first.turn': { low: { expression: '(36 * floor((nowhere / 36)))' },
                        high: null },
      },
    }));
    expect(message).toContain('nowhere');
    expect(message).toContain('first.turn');
  });

  it('11. a span over a coordinate the bank does not hold', () => {
    const message = refusal(document({
      spans: { 'no.such.thing': { low: 0, high: null } },
    }));
    expect(message).toContain('no.such.thing');
  });

  it('11. a bound that is neither null, a number nor an expression', () => {
    const message = refusal(document({
      spans: { 'first.turn': { low: 'nope', high: null } },
    }));
    expect(message).toContain('first.turn');
  });

  it('12. a limit that is missing', () => {
    const limits: Overrides = { ...LIMITS };
    delete limits.agreement;
    expect(refusal(document({ limits }))).toContain('agreement');
  });

  it('12. a limit that is not a finite number', () => {
    expect(refusal(document({ limits: { ...LIMITS, subdivisions: null } })))
      .toContain('subdivisions');
  });

  it('13. a sources key naming an unknown id', () => {
    const message = refusal(document({
      sources: { crank: ['crank'], 'first.turn': ['crank'], nowhere: [] },
    }));
    expect(message).toContain('nowhere');
  });

  it('13. a sources member naming an unknown id', () => {
    const message = refusal(document({
      sources: { crank: ['crank'], 'first.turn': ['elsewhere'] },
    }));
    expect(message).toContain('elsewhere');
  });

  it('14. a computed value an edge READS that no edge gives', () => {
    const message = refusal(document({
      intermediates: ['ghost'],
      edges: [{
        kind: 'law', needs: ['crank', 'ghost'], gives: ['first.turn'],
        description: 'd', stated_by: 'Bench',
        expressions: ['(crank + ghost)'], affine: [true], plans: [null],
      }],
      sources: { crank: ['crank'], 'first.turn': ['crank'], ghost: [] },
    }));
    expect(message).toContain('ghost');
  });

  it('14. accepts a computed value nothing reads (the Pascaline\'s six)', () => {
    expect(() => loadProgram(document({
      intermediates: ['ghost'],
      sources: { crank: ['crank'], 'first.turn': ['crank'], ghost: [] },
    }), SOURCE)).not.toThrow();
  });
});

describe('loadProgram reads a good program verbatim', () => {
  it('keeps the coordinate order, kinds, units, domains and rest values', () => {
    const loaded = loadProgram(document(), SOURCE);
    expect(loaded.order).toEqual(['crank', 'first.turn']);
    expect(loaded.inputs).toEqual(['crank']);
    expect(loaded.coordinates['first.turn'])
      .toEqual({ kind: 'coordinate', initial: 0, unit: 'deg',
                 domain: 'rotational' });
    expect(loaded.initial).toEqual({ crank: 0, 'first.turn': 0 });
    expect(loaded.clock).toBe('time');
    expect(loaded.identity).toBe('abc');
    expect(loaded.limits.agreement).toBe(1e-9);
    expect(loaded.limits.subdivisions).toBe(64);
  });

  it('derives the determiner map by inverting gives', () => {
    const loaded = loadProgram(document(), SOURCE);
    const found = loaded.determiner.get('first.turn')!;
    expect(found.edge.description).toBe('crank drives first.turn');
    expect(found.index).toBe(0);
    expect(loaded.determiner.has('crank')).toBe(false);
  });

  it('prepares one node id per published expression', () => {
    const loaded = loadProgram(document(), SOURCE);
    expect(loaded.nodeOf('(2.0 * crank)')).toBe(prepare('(2.0 * crank)'));
  });

  it('names every id an expression of the document may read', () => {
    const loaded = loadProgram(document(), SOURCE);
    expect([...loaded.declaredNames].sort())
      .toEqual(['crank', 'first.turn', 'time']);
  });
});

describe('the acceptance document', () => {
  const loaded = loadProgram(acceptance as unknown as RunDocument,
                             'tests/fixtures/pascaline/viewer.json');

  it('loads the Pascaline module\'s published program', () => {
    expect(loaded.order).toHaveLength(12);
    expect(loaded.order.slice(0, 3))
      .toEqual(['hundreds_entry', 'tens_entry', 'units_entry']);
    expect(loaded.inputs).toHaveLength(3);
    expect(loaded.intermediates).toHaveLength(6);
    expect(loaded.edges).toHaveLength(9);
    expect(loaded.spans).toEqual({});
    expect(loaded.limits.agreement).toBe(1e-9);
    expect(loaded.identity).toBe(
      '62bb22d2e3742320248ab18069ef0d7cfeece0a317527d1efb728a2f33e68b4b');
  });

  it('carries three plans, each one floor jump', () => {
    const plans = loaded.edges.flatMap(
      (edge) => edge.plans.filter((plan) => plan !== null));
    expect(plans).toHaveLength(3);
    for (const plan of plans) {
      expect(plan!.jumps).toHaveLength(1);
      expect(plan!.jumps[0].primitive).toBe('floor');
      expect(plan!.jumps[0].affine).toBe(true);
    }
    expect(new Set(plans.map((plan) => plan!.jumps[0].name)).size).toBe(3);
  });

  it('publishes six computed values no edge determines', () => {
    // Design §15 finding 1: they are accepted as declared names because
    // nothing reads them, and refused the moment something does.
    expect([...uncomputedValues(loaded)].sort()).toEqual([
      'hundreds.stop.angle', 'hundreds.wheel',
      'tens.stop.angle', 'tens.wheel',
      'units.stop.angle', 'units.wheel',
    ]);
  });
});

describe('the held node ids are generation-guarded (design D12)', () => {
  it('re-prepares from the expression strings after a store reset', () => {
    const loaded = loadProgram(document(), SOURCE);
    const before = loaded.nodeOf('(2.0 * crank)');
    const generation = expressionGeneration();

    // Force a reset the way the ceiling would: lower it, then prepare
    // one more expression.
    const ceiling = EXPRESSION_LIMITS.nodes;
    try {
      EXPRESSION_LIMITS.nodes = 1;
      prepare('(1 + 2)');
    } finally {
      EXPRESSION_LIMITS.nodes = ceiling;
    }
    expect(expressionGeneration()).toBeGreaterThan(generation);

    const after = loaded.nodeOf('(2.0 * crank)');
    expect(after).toBe(prepare('(2.0 * crank)'));
    // And it still evaluates to the same number, which is the point.
    expect(before).not.toBe(undefined);
  });
});

// ---------------------------------------------------------------------
// A bound that READS OTHER COORDINATES (design D1-D3).
// ---------------------------------------------------------------------

/** A two-input bench whose `gate.lift` is driven by `lift` and whose
 * `first.turn` is driven by `crank`, plus one published computed value
 * an edge determines. Every constraint case below is this with one
 * span. */
function reading(program: Overrides = {},
                 extra: Overrides = {}): RunDocument {
  return {
    format: 'solid-node-export',
    version: 5,
    drivers: {
      crank: { default: 0, range: null, unit: 'deg', dtype: null, scale: null },
      lift: { default: 0, range: null, unit: 'mm', dtype: null, scale: null },
    },
    instructions: {},
    program: {
      identity: 'abc',
      clock: 'time',
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        lift: { kind: 'input', initial: 0, domain: null },
        'first.turn': {
          kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
        },
        'gate.lift': {
          kind: 'coordinate', initial: 0, unit: 'mm', domain: 'linear',
        },
      },
      intermediates: ['port.angle'],
      edges: [
        {
          kind: 'law', needs: ['crank'], gives: ['first.turn'],
          description: 'crank drives first.turn', stated_by: 'Bench',
          expressions: ['(2.0 * crank)'], affine: [true], plans: [null],
        },
        {
          kind: 'law', needs: ['lift'], gives: ['gate.lift'],
          description: 'lift drives gate.lift', stated_by: 'Bench',
          expressions: ['(1.0 * lift)'], affine: [true], plans: [null],
        },
        {
          kind: 'law', needs: ['first.turn'], gives: ['port.angle'],
          description: 'first.turn drives port.angle', stated_by: 'Bench',
          expressions: ['(1.0 * first.turn)'], affine: [true], plans: [null],
        },
      ],
      spans: {},
      sources: {
        crank: ['crank'], lift: ['lift'],
        'first.turn': ['crank'], 'gate.lift': ['lift'],
        'port.angle': ['crank'],
      },
      limits: { ...LIMITS },
      ...program,
    },
    ...extra,
  } as RunDocument;
}

describe('a bound may read other coordinates (design D1-D3)', () => {
  it('loads a bound naming a second bank coordinate', () => {
    const loaded = loadProgram(reading({
      spans: {
        'first.turn': {
          low: null,
          high: { expression: '(90 * (abs(gate.lift) <= 0.05))' },
        },
      },
    }), SOURCE);
    const entry = loaded.constraints.get('first.turn:high')!;
    expect(entry).toBeDefined();
    expect(entry.identifier).toBe('first.turn');
    expect(entry.side).toBe('high');
    expect(entry.reads).toEqual(['gate.lift']);
  });

  it('loads a bound reaching its read ONLY through the bindings table',
     () => {
    // The lock's own shape: the expression names `_b0` and nothing
    // else, and the coordinate is reached only through the table.
    const loaded = loadProgram(reading({
      spans: {
        'first.turn': { low: null, high: { expression: '(90 * _b1)' } },
      },
    }, {
      bindings: [
        { name: '_b0', expression: '(gate.lift <= 0.05)' },
        { name: '_b1', expression: '(_b0 * 1.0)' },
      ],
    }), SOURCE);
    const entry = loaded.constraints.get('first.turn:high')!;
    expect(entry.reads).toEqual(['gate.lift']);
  });

  it('sorts the reads, and never holds the own coordinate', () => {
    const loaded = loadProgram(reading({
      spans: {
        'first.turn': {
          low: null,
          high: { expression: '((first.turn * 0) + (gate.lift + lift))' },
        },
      },
    }), SOURCE);
    expect(loaded.constraints.get('first.turn:high')!.reads)
      .toEqual(['gate.lift', 'lift']);
  });

  it('derives the sub-program: the determining edges, in published '
     + 'order, and never a check', () => {
    const loaded = loadProgram(reading({
      spans: {
        'first.turn': {
          low: null, high: { expression: '(90 * (gate.lift <= 0.05))' },
        },
      },
      edges: [
        ...(reading().program as { edges: unknown[] }).edges,
        {
          kind: 'check', needs: ['crank'], gives: [],
          description: 'a check on first.turn', stated_by: 'Bench',
          slot: 'first.turn', factors: [2.0], constant: 0,
        },
      ],
    }), SOURCE);
    const entry = loaded.constraints.get('first.turn:high')!;
    // The `port.angle` edge determines nothing either needs, and the
    // check determines nothing at all.
    expect(entry.edges.map((edge) => edge.description)).toEqual([
      'crank drives first.turn', 'lift drives gate.lift',
    ]);
  });

  it('derives the candidates: the union of the reaching-input lists',
     () => {
    const loaded = loadProgram(reading({
      spans: {
        'first.turn': {
          low: null, high: { expression: '(90 * (gate.lift <= 0.05))' },
        },
      },
    }), SOURCE);
    expect(loaded.constraints.get('first.turn:high')!.candidates)
      .toEqual(['crank', 'lift']);
  });

  it('makes no entry for a self-only bound, a number or an absent side',
     () => {
    const loaded = loadProgram(reading({
      spans: {
        'first.turn': { low: 0, high: { expression: '(36 * first.turn)' } },
        'gate.lift': { low: null, high: null },
      },
    }), SOURCE);
    expect(loaded.constraints.size).toBe(0);
  });

  it('refuses a bound naming a published computed value, saying so',
     () => {
    const message = refusal(reading({
      spans: {
        'first.turn': { low: null, high: { expression: '(90 * port.angle)' } },
      },
    }));
    expect(message).toContain('port.angle');
    expect(message).toContain('a published computed value');
    expect(message).toContain('read the joint the port follows');
    expect(message).toContain('(90 * port.angle)');
  });

  it('refuses a bound naming the clock', () => {
    const message = refusal(reading({
      spans: {
        'first.turn': { low: null, high: { expression: '(90 * time)' } },
      },
    }));
    expect(message).toContain('time');
    expect(message).toContain('may not read');
  });

  it('refuses a bound naming an unknown id', () => {
    const message = refusal(reading({
      spans: {
        'first.turn': { low: null, high: { expression: '(90 * nowhere)' } },
      },
    }));
    expect(message).toContain('nowhere');
  });

  it('refuses a bound naming a jump plan\'s branch placeholder', () => {
    const message = refusal(reading({
      spans: {
        'first.turn': { low: null, high: { expression: '(90 * _j0)' } },
      },
      edges: [
        {
          kind: 'law', needs: ['crank'], gives: ['first.turn'],
          description: 'crank drives first.turn', stated_by: 'Bench',
          expressions: ['(2.0 * crank)'], affine: [true],
          plans: [{
            skeleton: '(36.0 * _j0)',
            jumps: [{
              name: '_j0', primitive: 'floor', level: 'crank', affine: true,
            }],
          }],
        },
        ...(reading().program as { edges: unknown[] }).edges.slice(1),
      ],
    }));
    expect(message).toContain('_j0');
    expect(message).toContain('may not read');
  });
});

// ---------------------------------------------------------------------
// The lock's own published document (design D8): the guard against a
// wrong closure, because the corpus's `Captured` machine carries no
// bindings at all and cannot catch it.
// ---------------------------------------------------------------------

describe('the pin tumbler lock\'s published document', () => {
  const loaded = loadProgram(lockDocument as unknown as RunDocument,
                             'tests/fixtures/lock/viewer.json');

  it('loads: what was refused before this cycle', () => {
    expect(loaded.identity).toBe(
      'b45402a563493d03462a51b456059300c74c75c61f74bc206a7f38cc7746c867');
    expect(loaded.order).toHaveLength(16);
    expect(loaded.edges).toHaveLength(14);
  });

  it('derives three constraints: both sides of the plug and the '
     + 'key\'s capture', () => {
    expect([...loaded.constraints.keys()].sort()).toEqual([
      'plug.key.insert:low', 'plug.turn:high', 'plug.turn:low',
    ]);
  });

  it('reads the five pin lifts THROUGH the bindings table', () => {
    for (const side of ['low', 'high']) {
      const entry = loaded.constraints.get(`plug.turn:${side}`)!;
      // The expression itself names only `_b10 … _b22`; the CLOSURE is
      // the five lifts.
      expect(entry.expression).toContain('_b10');
      expect(entry.expression).not.toContain('plug.p1.lift');
      expect(entry.reads).toEqual([
        'plug.p1.lift', 'plug.p2.lift', 'plug.p3.lift', 'plug.p4.lift',
        'plug.p5.lift',
      ]);
      expect(entry.edges.map((edge) => edge.description)).toEqual([
        'insertion drives plug.key.insert',
        'rotation drives plug.turn',
        'plug.key.insert drives plug.p1.lift',
        'plug.key.insert drives plug.p2.lift',
        'plug.key.insert drives plug.p3.lift',
        'plug.key.insert drives plug.p4.lift',
        'plug.key.insert drives plug.p5.lift',
      ]);
      expect(entry.candidates).toEqual(['insertion', 'rotation']);
    }
  });

  it('reads the plug directly on the key\'s own low bound', () => {
    const entry = loaded.constraints.get('plug.key.insert:low')!;
    expect(entry.reads).toEqual(['plug.turn']);
    expect(entry.edges.map((edge) => edge.description)).toEqual([
      'insertion drives plug.key.insert', 'rotation drives plug.turn',
    ]);
    expect(entry.candidates).toEqual(['insertion', 'rotation']);
  });

  it('leaves the five numeric driver-pin spans alone', () => {
    for (const id of ['d1.lift', 'd2.lift', 'd3.lift', 'd4.lift',
                      'd5.lift']) {
      expect(loaded.spans[id]).toEqual({ low: -6.9, high: 6.1 });
      expect(loaded.constraints.has(`${id}:low`)).toBe(false);
      expect(loaded.constraints.has(`${id}:high`)).toBe(false);
    }
  });
});
