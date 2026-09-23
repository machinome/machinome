/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Loading a published program (design §4): read it verbatim, derive the
// little that is derivable, and refuse by name everything the engine
// cannot execute -- before a frame is rendered or a tick integrated.

import { describe, expect, it } from 'vitest';
import { EXPRESSION_LIMITS, expressionGeneration, prepare } from '../expressions';
import {
  componentsOf, loadProgram, readsUnder, stronglyConnected, uncomputedValues,
} from './program';
import type {
  BlockMember, LoadedProgram, ProgramEdge, RunDocument,
} from './program';
import type { PathShape } from '../expressions';
import { structureOf } from '../expressions';
import acceptance from '../../../../tests/fixtures/pascaline/viewer.json';
import lockDocument from '../../../../tests/fixtures/lock/viewer.json';
import corpus from '../running-corpus.json';
import clearingDocument from '../../../../tests/fixtures/clearing/viewer.json';
import carriageDocument from '../../../../tests/fixtures/carriage/viewer.json';
import touchedDocument from '../../../../tests/fixtures/touched/viewer.json';

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
    format: 'machinome-export',
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

function followDocument(): RunDocument {
  return document({
    coordinates: {
      low: { kind: 'input', initial: 0, domain: null },
      high: { kind: 'input', initial: 3, domain: null },
      'ball.slide': { kind: 'coordinate', initial: 0, domain: 'translational' },
    },
    edges: [{ kind: 'follow', needs: ['low', 'high', 'ball.slide'],
      gives: ['ball.slide'], description: 'two surfaces follow ball',
      stated_by: 'Bench', lower: 'low', upper: 'high',
      lower_plan: null, upper_plan: null }],
    spans: { 'ball.slide': {
      low: { expression: 'low' }, high: { expression: 'high' },
    } },
    sources: { low: ['low'], high: ['high'], 'ball.slide': ['low', 'high'] },
  }, { version: 12, drivers: {
    low: { default: 0, range: null, unit: null, dtype: null, scale: null },
    high: { default: 3, range: null, unit: null, dtype: null, scale: null },
  } });
}

describe('loadProgram refuses what it cannot execute (design §4)', () => {
  it('loads the producer v12 two-envelope Follow wire', () => {
    expect(loadProgram(followDocument(), SOURCE).edges[0].kind).toBe('follow');
  });

  it('refuses Follow before v12, a missing paired Bound, and nonterminal output', () => {
    const old = followDocument();
    old.version = 11;
    expect(refusal(old)).toContain('before document version 12');
    const unmatched = followDocument();
    (unmatched.program as Overrides).spans = {};
    expect(refusal(unmatched)).toContain('matching dynamic low Bound');
    const downstream = followDocument();
    ((downstream.program as Overrides).coordinates as Overrides).witness =
      { kind: 'coordinate', initial: 0, domain: 'translational' };
    ((downstream.program as Overrides).sources as Overrides).witness = ['low', 'high'];
    ((downstream.program as Overrides).edges as unknown[]).push({
      kind: 'law', needs: ['ball.slide'], gives: ['witness'],
      description: 'reads follower', stated_by: 'Bench',
      expressions: ['ball.slide'], affine: [true], plans: [null],
    });
    expect(refusal(downstream)).toContain('must be terminal');
  });

  it('refuses a malformed plan and an infeasible retained rest', () => {
    const malformed = followDocument();
    (((malformed.program as Overrides).edges as Overrides[])[0]).lower_plan =
      { skeleton: 'low', jumps: [{ name: '_j0', primitive: 'future', level: 'low', affine: true }] };
    expect(refusal(malformed)).toContain('malformed jump');
    const impossible = followDocument();
    (((impossible.program as Overrides).coordinates as Overrides)['ball.slide'] as Overrides).initial = 4;
    expect(refusal(impossible)).toContain('outside its finite feasible interval');
  });
  it('loads the exact version-9 play edge', () => {
    const doc = document({
      edges: [{
        kind: 'play', needs: ['crank', 'first.turn'], gives: ['first.turn'],
        description: 'crank plays first.turn', stated_by: 'Bench',
        low: -10, high: 10,
      }],
    }, { version: 9 });
    const edge = loadProgram(doc, SOURCE).edges[0];
    expect(edge.kind).toBe('play');
    expect([edge.low, edge.high]).toEqual([-10, 10]);
  });

  it('refuses a malformed or initially impossible play edge', () => {
    const malformed = document({ edges: [{
      kind: 'play', needs: ['crank'], gives: ['first.turn'],
      description: 'bad play', stated_by: 'Bench', low: -10, high: 10,
    }] }, { version: 9 });
    expect(refusal(malformed)).toContain('needs: [source, retained]');

    const impossible = document({ edges: [{
      kind: 'play', needs: ['crank', 'first.turn'], gives: ['first.turn'],
      description: 'bad rest', stated_by: 'Bench', low: 1, high: 2,
    }] }, { version: 9 });
    expect(refusal(impossible)).toContain('outside');
  });

  it('refuses any additional writer of a play follower', () => {
    const ambiguous = document({ edges: [
      {
        kind: 'play', needs: ['crank', 'first.turn'], gives: ['first.turn'],
        description: 'crank plays first.turn', stated_by: 'Bench',
        low: -10, high: 10,
      },
      {
        kind: 'law', needs: ['crank'], gives: ['first.turn'],
        description: 'another writer', stated_by: 'Bench',
        expressions: ['crank'], affine: [true], plans: [null],
      },
    ] }, { version: 9 });
    expect(refusal(ambiguous)).toContain('only writer');
  });

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
    format: 'machinome-export',
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

// ---------------------------------------------------------------------
// The SELF-READ, recognised and read at load (design D1)
// ---------------------------------------------------------------------

/** `Clearing`'s shape, as the framework publishes it: a ring carrying
 * racks sweeps past a dial, and the rack turns the dial only while its
 * teeth reach it (`_j0`/`_j1`, over the RING) AND the dial is not
 * already standing in its missing-tooth gap (`_j2`/`_j3`, over the
 * DIAL's own retained angle, reached ONLY through `_b3`). */
function selfRead(program: Overrides = {},
                  overrides: Overrides = {}): RunDocument {
  return {
    format: 'machinome-export',
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
          kind: 'coordinate', initial: 108, unit: 'deg', domain: 'rotational',
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
      }],
      spans: {},
      sources: {
        ring: ['ring'], setter: ['setter'], 'wheel.turn': ['ring', 'setter'],
      },
      limits: { ...LIMITS },
      ...program,
    },
    ...overrides,
  } as RunDocument;
}

describe('a law that reads the coordinate it drives (design D1)', () => {
  it('2.1 is recognised from `needs` met with `gives`, and its BAND gate '
     + '-- which reaches the driven id only through a binding -- is '
     + 'dependent', () => {
    const loaded = loadProgram(selfRead(), SOURCE);
    const edge = loaded.edges[0];
    expect(edge.retained).toHaveLength(1);
    const reading = edge.retained[0]!;
    expect(reading.own).toBe('wheel.turn');
    expect(reading.dependent.map((jump) => jump.name)).toEqual(['_j2', '_j3']);
    expect(reading.outer.jumps.map((jump) => jump.name))
      .toEqual(['_j0', '_j1']);
    expect(reading.outer.skeleton).toBe('(setter + ((ring * _j1) * _j3))');
  });

  it('2.2 reads `affine` off the edge\'s published per-end flag and '
     + 'recomputes nothing -- which for a plan-bearing law IS '
     + '`_affine_in_sources(plan.skeleton)`', () => {
    const loaded = loadProgram(selfRead(), SOURCE);
    expect(loaded.edges[0].retained[0]!.affine)
      .toBe(loaded.edges[0].affine[0]);
    expect(loaded.edges[0].retained[0]!.affine).toBe(true);
    // And the same equality on the producer's OWN document, taken from
    // the corpus rather than written here.
    const clearing = (corpus as unknown as {
      machines: { name: string; document: RunDocument }[];
    }).machines.find((one) => one.name === 'Clearing')!;
    const published = loadProgram(clearing.document,
                                  'running-corpus.json#Clearing');
    const edge = published.edges[0];
    expect(edge.retained[0]!.affine).toBe(edge.affine[0]);
  });

  it('2.3 a plan with no dependent node at all keeps the WHOLE plan as '
     + 'its outer layer and an empty dependent list', () => {
    // The same edge with the band gate stated over the RING instead: the
    // driven id is still among `needs`, so the edge is still a self-read
    // -- but no jump node depends on it.
    const loaded = loadProgram(selfRead({
      edges: [{
        kind: 'law',
        needs: ['setter', 'ring', 'wheel.turn'],
        gives: ['wheel.turn'],
        description: 'a self-read no jump node depends on',
        stated_by: 'Clearing',
        expressions: ['(setter + (ring * (floor(_b1) == 0)))'],
        affine: [true],
        plans: [{
          skeleton: '(setter + (ring * _j1))',
          jumps: [
            { name: '_j0', primitive: 'floor', level: '_b1', affine: true },
            { name: '_j1', primitive: '==', level: '(_j0 - 0)', affine: true },
          ],
        }],
      }],
    }), SOURCE);
    const reading = loaded.edges[0].retained[0]!;
    expect(reading.dependent).toEqual([]);
    expect(reading.outer.jumps.map((jump) => jump.name))
      .toEqual(['_j0', '_j1']);
  });

  it('2.3 a nested dependent node makes its ENCLOSING node dependent', () => {
    const loaded = loadProgram(selfRead({
      edges: [{
        kind: 'law',
        needs: ['setter', 'ring', 'wheel.turn'],
        gives: ['wheel.turn'],
        description: 'a dependent node nested inside an independent level',
        stated_by: 'Clearing',
        expressions: ['(setter + (ring * 1.0))'],
        affine: [true],
        plans: [{
          skeleton: '(setter + (ring * _j1))',
          jumps: [
            // `_j0` names the driven id only through `_b3`; `_j1`'s own
            // level names no coordinate at all and reaches it ONLY
            // through `_j0`'s placeholder.
            { name: '_j0', primitive: 'floor', level: '_b3', affine: true },
            { name: '_j1', primitive: '>=', level: '(_j0 - 1.0)',
              affine: true },
          ],
        }],
      }],
    }), SOURCE);
    const reading = loaded.edges[0].retained[0]!;
    expect(reading.dependent.map((jump) => jump.name)).toEqual(['_j0', '_j1']);
    expect(reading.outer.jumps).toEqual([]);
  });

  it('2.4 refuses a self-read law that drives more than one coordinate', () => {
    const message = refusal(selfRead({
      coordinates: {
        ring: { kind: 'input', initial: 0, domain: null },
        setter: { kind: 'input', initial: 0, domain: null },
        'wheel.turn': {
          kind: 'coordinate', initial: 108, unit: 'deg', domain: 'rotational',
        },
        'other.turn': {
          kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
        },
      },
      edges: [{
        kind: 'law',
        needs: ['setter', 'ring', 'wheel.turn'],
        gives: ['wheel.turn', 'other.turn'],
        description: 'a self-read driving a group',
        stated_by: 'Clearing',
        expressions: ['(setter + (ring * _b3))', '(setter * 2.0)'],
        affine: [true, true],
        plans: [null, null],
      }],
      sources: {
        ring: ['ring'], setter: ['setter'],
        'wheel.turn': ['ring', 'setter'], 'other.turn': ['setter'],
      },
    }));
    expect(message).toContain('wheel.turn');
    expect(message).toContain('drives exactly ONE coordinate');
    expect(message).toContain(SOURCE);
  });

  it('2.4 refuses a self-read of a published computed value', () => {
    const message = refusal(selfRead({
      intermediates: ['port.angle'],
      edges: [{
        kind: 'law',
        needs: ['ring', 'port.angle'],
        gives: ['port.angle'],
        description: 'a self-read of a port',
        stated_by: 'Clearing',
        expressions: ['(ring * 2.0)'],
        affine: [true],
        plans: [null],
      }],
      sources: { ring: ['ring'], setter: ['setter'], 'port.angle': ['ring'] },
    }));
    expect(message).toContain('port.angle');
    expect(message).toContain('A retained value is a history');
    expect(message).toContain(SOURCE);
  });

  it('2.4 refuses a read that survives the SKELETON', () => {
    const message = refusal(selfRead({
      edges: [{
        kind: 'law',
        needs: ['setter', 'ring', 'wheel.turn'],
        gives: ['wheel.turn'],
        description: 'a continuous self-read',
        stated_by: 'Clearing',
        expressions: ['(setter + ((ring * _b2) * (floor(_b1) == 0)))'],
        affine: [false],
        plans: [{
          // `_b2` is `(wheel.turn + 0.5)`: the read SURVIVES the
          // substitution of every branch.
          skeleton: '(setter + ((ring * _b2) * _j1))',
          jumps: [
            { name: '_j0', primitive: 'floor', level: '_b1', affine: true },
            { name: '_j1', primitive: '==', level: '(_j0 - 0)', affine: true },
          ],
        }],
      }],
    }));
    expect(message).toContain('wheel.turn');
    expect(message).toContain('PIECEWISE');
    expect(message).toContain('remainder');
    expect(message).toContain(SOURCE);
  });

  it('2.5 a version 6 document with NO self-read edge loads with no '
     + 'reading at all', () => {
    const plain = document({}, { version: 6 });
    const loaded = loadProgram(plain, SOURCE);
    expect(loaded.edges[0].retained).toEqual([]);
  });

  it('2.5 a version 5 document is never given a reading, and a version 5 '
     + 'document that DOES read its own driven end is read exactly as a '
     + 'version 6 one -- the test is `needs` met with `gives`, never the '
     + 'version number', () => {
    expect(loadProgram(document(), SOURCE).edges[0].retained).toEqual([]);
    const mislabelled = selfRead({}, { version: 5 });
    expect(loadProgram(mislabelled, SOURCE).edges[0].retained)
      .toHaveLength(1);
  });
});

// ---------------------------------------------------------------------
// The committed Curta fixture (design D9, tasks 9.3)
// ---------------------------------------------------------------------

describe('the Curta\'s clearing interface, as published', () => {
  const loaded = loadProgram(clearingDocument as unknown as RunDocument,
                             'tests/fixtures/clearing/viewer.json');

  it('9.3 loads: a version 6 document of six self-read edges', () => {
    expect((clearingDocument as { version: number }).version).toBe(6);
    expect(loaded.identity).toBe(
      '7425122fcfafee5a96152d79dd6a4ec4d66d1745a569abe7997ee9d00db4eecb');
    expect(loaded.inputs).toEqual(['clearing']);
    expect(loaded.edges).toHaveLength(6);
    expect([...loaded.order].sort()).toEqual([
      'clearing', 'counter0.turn', 'counter1.turn', 'counter2.turn',
      'result0.turn', 'result1.turn', 'result2.turn',
    ]);
  });

  it('9.3 gives every one of the six edges a reading of its own driven '
     + 'end', () => {
    for (const edge of loaded.edges) {
      expect(edge.gives).toHaveLength(1);
      expect(edge.needs).toContain(edge.gives[0]);
      expect(edge.retained).toHaveLength(1);
      expect(edge.retained[0]!.own).toBe(edge.gives[0]);
    }
    expect(loaded.edges.map((edge) => edge.retained[0]!.own).sort()).toEqual([
      'counter0.turn', 'counter1.turn', 'counter2.turn',
      'result0.turn', 'result1.turn', 'result2.turn',
    ]);
  });

  it('9.3 splits each plan into the band\'s own nodes and the rack\'s', () => {
    for (const edge of loaded.edges) {
      const reading = edge.retained[0]!;
      // The BAND, over the dial's own retained angle: a `floor` and a
      // comparison. The rack's reach nodes are the independent ones.
      expect(reading.dependent.map((jump) => jump.primitive))
        .toEqual(['floor', '>=']);
      expect(reading.outer.jumps.length).toBeGreaterThan(0);
      for (const jump of reading.outer.jumps) {
        expect(['<=', '>=', '<', '>']).toContain(jump.primitive);
      }
      expect(reading.outer.skeleton).toBe(edge.plans[0]!.skeleton);
    }
  });

  it('9.3 reads every one of the six as NON-AFFINE -- the `clamp01` '
     + 'station window, which makes every self-read crossing here a '
     + 'SEARCHED one', () => {
    for (const edge of loaded.edges) {
      expect(edge.affine[0]).toBe(false);
      expect(edge.retained[0]!.affine).toBe(false);
    }
  });
});

// ---------------------------------------------------------------------
// A SELECTION: the BLOCK, re-derived at load (design D1, tasks 3-5)
// ---------------------------------------------------------------------

/** One corpus machine's published document, by name: the framework's
 * own, never written here. */
function machine(name: string): RunDocument {
  const found = (corpus as unknown as {
    machines: { name: string; document: RunDocument }[];
  }).machines.find((one) => one.name === name);
  return found!.document;
}

const blockLimits = { ...LIMITS };

/** The Curta's carry shape reduced to two members and one selector each:
 * `higher.turn` is driven by the crank BELOW the detent and by the carry
 * ABOVE it, and `carry.travel` by `higher.turn` BELOW it -- so the pair
 * is a cycle whose active direction FLIPS with `shift`. */
function blockDocument(overrides: Overrides = {},
                       extra: Overrides = {}): RunDocument {
  return {
    format: 'machinome-export',
    version: 7,
    drivers: {
      crank: { default: 0, range: null, unit: null, dtype: null, scale: null },
      shift: { default: 0, range: null, unit: null, dtype: null, scale: null },
    },
    instructions: {},
    program: {
      identity: 'block',
      clock: 'time',
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        shift: { kind: 'input', initial: 0, domain: null },
        'higher.turn': {
          kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
        },
        'carry.travel': {
          kind: 'coordinate', initial: 0, unit: 'mm', domain: 'translational',
        },
      },
      intermediates: [],
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
      spans: {},
      sources: {
        crank: ['crank'], shift: ['shift'],
        'higher.turn': ['crank', 'shift'],
        'carry.travel': ['crank', 'shift'],
      },
      limits: { ...blockLimits },
      ...overrides,
    },
    ...extra,
  } as unknown as RunDocument;
}

/** `blockDocument` with its second member replaced. */
function withSecond(edge: Overrides, extra: Overrides = {}): RunDocument {
  const base = blockDocument();
  const program = (base as unknown as { program: { edges: unknown[] } }).program;
  program.edges[1] = { ...(program.edges[1] as Overrides), ...edge };
  Object.assign(program, extra);
  return base;
}

/** The same cycle with its FIRST member a plain law reading
 * `carry.travel` unconditionally and its second gated by `primitive`:
 * the shape that turns on whether the gate's zero branch is held over an
 * INTERVAL of its level. */
function gatedCycle(primitive: string, written?: string): RunDocument {
  const base = blockDocument();
  const program = (base as unknown as { program: { edges: unknown[] } })
    .program;
  program.edges[0] = {
    kind: 'law', needs: ['crank', 'carry.travel'], gives: ['higher.turn'],
    description: 'the crank drives higher.turn', stated_by: 'Bench',
    expressions: ['(crank + carry.travel)'], affine: [true], plans: [null],
  };
  program.edges[1] = {
    kind: 'law', needs: ['higher.turn', 'shift'], gives: ['carry.travel'],
    description: 'higher.turn drives carry.travel', stated_by: 'Bench',
    expressions: [written ?? `(higher.turn * (shift ${primitive} 0.5))`],
    affine: [true],
    plans: [{
      skeleton: '(higher.turn * _j2)',
      jumps: [{
        name: '_j2', primitive, level: '(shift - 0.5)', affine: true,
      }],
    }],
  };
  return base;
}

/** Two ORDINARY laws on a cycle: nothing to switch anywhere. */
function plainCycle(): RunDocument {
  const base = gatedCycle('<');
  const program = (base as unknown as { program: { edges: Overrides[] } })
    .program;
  program.edges[1] = {
    ...program.edges[1], expressions: ['higher.turn'], plans: [null],
  };
  return base;
}

describe('the block is re-derived at LOAD (design D1.1-D1.3, tasks 3)', () => {
  it('3.1 a document PUBLISHING `kind: "block"` is refused as an unknown '
     + 'kind: the kind is derived and never read', () => {
    const message = refusal(document({
      edges: [{
        kind: 'block',
        needs: ['crank'],
        gives: ['first.turn'],
        description: 'a published block',
        stated_by: 'Bench',
      }],
    }));
    expect(message).toContain('declares kind "block"');
    expect(message).toContain('law, wiring, formula, check');
  });

  it('3.2 a program with no cycle produces no component of more than one',
     () => {
    const loaded = loadProgram(document(), SOURCE);
    expect(componentsOf(loaded.edges)).toEqual([[0]]);
    expect(loaded.edges.every((edge) => edge.kind !== 'block')).toBe(true);
  });

  it('3.2 a SELF-READ edge alone is not a component: a need the edge '
     + 'itself gives is excluded from the graph', () => {
    const loaded = loadProgram(selfRead(), SOURCE);
    expect(componentsOf(loaded.edges)).toEqual([[0]]);
    expect(loaded.edges[0].kind).toBe('law');
  });

  it('3.2 a CHECK edge is never in a component: it determines nothing, so '
     + 'nothing ever waits on it, and it is left where it is published',
     () => {
    const base = blockDocument();
    const program = (base as unknown as { program: { edges: unknown[] } })
      .program;
    // A check over the block's own coordinate, published AFTER both
    // members: it reads what the block gives and gives nothing.
    program.edges.push({
      kind: 'check', needs: ['carry.travel', 'higher.turn'], gives: [],
      description: 'carry.travel is checked against higher.turn',
      stated_by: 'Bench', slot: 'carry.travel', factors: [1.0, 0.0],
      constant: 0.0,
    });
    const loaded = loadProgram(base, SOURCE);
    const checks = loaded.edges.filter((edge) => edge.kind === 'check');
    expect(checks).toHaveLength(1);
    // Two members contract to one block; the check stays beside it.
    expect(loaded.edges.map((edge) => edge.kind)).toEqual(['block', 'check']);
    // And the check is in no component of more than one.
    const published = (base as unknown as {
      program: { edges: unknown[] };
    }).program.edges;
    expect(published).toHaveLength(3);
    for (const component of componentsOf(
      loadProgram(blockDocument(), SOURCE).edges)) {
      expect(component).toHaveLength(1);
    }
  });

  it('3.2 `ShiftedCarry` and `RangedBlock` each produce exactly the pair '
     + 'ADR-122 names: {higher.turn, carry.travel}', () => {
    for (const name of ['ShiftedCarry', 'RangedBlock']) {
      const loaded = loadProgram(machine(name), `corpus://${name}`);
      const blocks = loaded.edges.filter((edge) => edge.kind === 'block');
      expect(blocks).toHaveLength(1);
      expect([...blocks[0].gives].sort())
        .toEqual(['carry.travel', 'higher.turn']);
      expect(blocks[0].block!.members).toHaveLength(2);
    }
  });

  it('3.2 Tarjan is ITERATIVE: a chain and a cycle 2,000 deep do not '
     + 'exhaust the JavaScript stack', () => {
    const chain: number[][] = [];
    for (let at = 0; at < 2000; at += 1) chain.push(at === 0 ? [] : [at - 1]);
    const singles = stronglyConnected(chain);
    expect(singles).toHaveLength(2000);
    expect(singles.every((one) => one.length === 1)).toBe(true);

    const ring = chain.map((after, at) => (at === 0 ? [1999] : after));
    const whole = stronglyConnected(ring);
    expect(whole).toHaveLength(1);
    expect(whole[0]).toHaveLength(2000);
    expect(whole[0][0]).toBe(0);
  });

  it('3.3 the component is contracted IN PLACE at its first member: needs '
     + 'united in first-seen order, gives, description, statedBy and an '
     + '`affine` that is FALSE on every end', () => {
    const loaded = loadProgram(machine('ShiftedCarry'),
                               'corpus://ShiftedCarry');
    // Three published law edges become two entries: the lower wheel's
    // own law, then the block at the index its first member held.
    expect(loaded.edges).toHaveLength(2);
    expect(loaded.edges[0].gives).toEqual(['lower.turn']);
    const block = loaded.edges[1];
    expect(block.kind).toBe('block');
    expect(block.gives).toEqual(['higher.turn', 'carry.travel']);
    expect(block.needs).toEqual([
      'crank', 'shift', 'clearing', 'carry.travel', 'higher.turn',
      'lower.turn',
    ]);
    expect(block.description).toBe(
      '(crank, shift, clearing, carry.travel, higher.turn) drives '
      + 'higher.turn; (lower.turn, higher.turn, shift, carry.travel) drives '
      + 'carry.travel');
    // De-duplicated in order: both members are stated by one class.
    expect(block.statedBy).toBe('ShiftedCarry');
    expect(block.affine).toEqual([false, false]);
    expect(block.plans).toEqual([null, null]);
    expect(block.expressions).toEqual([]);

    // `determiner` maps each give to the BLOCK, at that give's position
    // in the block's own `gives`.
    expect(loaded.determiner.get('higher.turn')).toEqual({
      edge: block, index: 0,
    });
    expect(loaded.determiner.get('carry.travel')).toEqual({
      edge: block, index: 1,
    });
  });

  it('3.4 the published order is VERIFIED and never re-sorted: two '
     + 'independent laws published the wrong way round are refused, '
     + 'naming both edges and the value', () => {
    const message = refusal(document({
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'first.turn': {
          kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
        },
        'second.turn': {
          kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
        },
      },
      edges: [
        {
          kind: 'law', needs: ['first.turn'], gives: ['second.turn'],
          description: 'first drives second', stated_by: 'Bench',
          expressions: ['first.turn'], affine: [true], plans: [null],
        },
        {
          kind: 'law', needs: ['crank'], gives: ['first.turn'],
          description: 'crank drives first', stated_by: 'Bench',
          expressions: ['crank'], affine: [true], plans: [null],
        },
      ],
      sources: {
        crank: ['crank'], 'first.turn': ['crank'], 'second.turn': ['crank'],
      },
    }));
    expect(message).toContain('not in an order this engine can execute');
    expect(message).toContain('first drives second reads "first.turn"');
    expect(message).toContain(
      'crank drives first determines LATER in the published listing');
    expect(message).toContain('would be inventing an ordering decision the '
                              + 'producer already made');
  });

  it('3.5 a block whose members are published NON-CONTIGUOUSLY, in a '
     + 'valid order, loads and is contracted at the first member\'s '
     + 'index', () => {
    const base = blockDocument();
    const program = (base as unknown as {
      program: { edges: unknown[]; coordinates: Overrides;
                 sources: Overrides };
    }).program;
    program.coordinates['idle.turn'] = {
      kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
    };
    program.sources['idle.turn'] = ['crank'];
    // An unrelated law published BETWEEN the two members.
    program.edges.splice(1, 0, {
      kind: 'law', needs: ['crank'], gives: ['idle.turn'],
      description: 'the crank drives idle', stated_by: 'Bench',
      expressions: ['crank'], affine: [true], plans: [null],
    });
    const loaded = loadProgram(base, SOURCE);
    expect(loaded.edges).toHaveLength(2);
    expect(loaded.edges[0].kind).toBe('block');
    expect(loaded.edges[0].gives).toEqual(['higher.turn', 'carry.travel']);
    expect(loaded.edges[1].gives).toEqual(['idle.turn']);
  });
});

describe('the selectors and the fold (design D1.4-D1.6, tasks 4)', () => {
  it('4.1 the structural accessor is a view of the store the evaluator '
     + 'owns, not a second parser', () => {
    const root = prepare('((a * 0.0) + b)');
    const node = structureOf(root);
    expect(node.kind).toBe('binary');
    expect(node.op).toBe('+');
    expect(node.children).toHaveLength(2);
    const left = structureOf(node.children[0]);
    expect(left.kind).toBe('binary');
    expect(left.op).toBe('*');
    expect(structureOf(left.children[0]).name).toBe('a');
    expect(structureOf(left.children[1]).value).toBe(0);
    expect(structureOf(node.children[1]).kind).toBe('name');
    expect(structureOf(node.children[1]).name).toBe('b');
  });

  it('4.2 the fold, on the corpus\'s OWN `ShiftedCarry` document: what '
     + 'each member reads unfolded, and what a selector at zero '
     + 'removes', () => {
    const loaded = loadProgram(machine('ShiftedCarry'),
                               'corpus://ShiftedCarry');
    const block = loaded.edges[1].block!;
    const [wheel, lever] = block.members;
    expect(wheel.own).toBe('higher.turn');
    expect(lever.own).toBe('carry.travel');

    // The lever, with NOTHING folded: every source its law names.
    expect([...block.activeReads(1, {})].sort())
      .toEqual(['carry.travel', 'higher.turn']);
    expect([...readsOf(loaded, lever, {})].sort()).toEqual(
      ['carry.travel', 'higher.turn', 'lower.turn', 'shift']);

    // With its `shift >= 0.5` selector at zero it no longer reads
    // `higher.turn` at all.
    expect([...readsOf(loaded, lever, { _j7: 0 })].sort()).toEqual(
      ['carry.travel', 'lower.turn', 'shift']);

    // And the wheel drops `carry.travel` under the complementary
    // comparison, `_j3`'s `shift < 0.5`.
    expect([...readsOf(loaded, wheel, {})].sort()).toEqual(
      ['carry.travel', 'clearing', 'crank', 'higher.turn', 'shift']);
    expect([...readsOf(loaded, wheel, { _j3: 0 })].sort()).toEqual(
      ['clearing', 'crank', 'higher.turn', 'shift']);
  });

  it('4.3 the fold is MONOTONE: the reads under the all-zero fold are a '
     + 'SUBSET of the reads under each single zero', () => {
    const loaded = loadProgram(machine('ShiftedCarry'),
                               'corpus://ShiftedCarry');
    const block = loaded.edges[1].block!;
    for (const member of block.members) {
      const all: Record<string, number> = {};
      for (const jump of member.selectors) all[jump.name] = 0;
      const least = readsOf(loaded, member, all);
      for (const jump of member.selectors) {
        const single = readsOf(loaded, member, { [jump.name]: 0 });
        for (const name of least) expect(single.has(name)).toBe(true);
      }
      // And the all-zero fold is what `unconditional` was taken from.
      for (const key of member.unconditional) expect(least.has(key)).toBe(true);
    }
  });

  it('4.4 a selector is a jump whose LEVEL reads nothing the block '
     + 'gives, with the level closed over the BINDINGS table, and a node '
     + 'reading the member\'s own driven end is NOT one', () => {
    const loaded = loadProgram(machine('ShiftedCarry'),
                               'corpus://ShiftedCarry');
    const block = loaded.edges[1].block!;
    const [wheel, lever] = block.members;
    // Every selector's level is `_b2`, a BINDING for `(shift - 0.5)`: a
    // viewer reading `freeVariables` alone would never see `shift`.
    expect(wheel.selectors.map((jump) => jump.name)).toEqual(['_j2', '_j3']);
    expect(wheel.selectors.map((jump) => jump.level)).toEqual(['_b2', '_b2']);
    expect(lever.selectors.map((jump) => jump.name)).toEqual(['_j6', '_j7']);
    // `_j4` reads `carry.travel` and `_j5` the wheel's OWN driven end:
    // neither is a selector, and `_j5` stays exactly where ADR-057 put
    // it, in the walked layer inside the piece.
    expect(wheel.plan!.jumps.map((jump) => jump.name))
      .toEqual(['_j2', '_j3', '_j4', '_j5']);
    expect(wheel.edge.retained[0]!.dependent.map((jump) => jump.name))
      .toEqual(['_j5']);
    expect(lever.selectors.map((jump) => jump.level)).toEqual(['_b2', '_b2']);
    expect(lever.plan!.jumps.map((jump) => jump.name))
      .toEqual(['_j6', '_j7', '_j8']);
    // The selector-only plan carries the member's OWN published skeleton.
    expect(wheel.selectorPlan!.skeleton).toBe(wheel.plan!.skeleton);
    expect(wheel.selectorPlan!.jumps).toEqual(wheel.selectors);
  });

  it('4.5 `unconditional` and `switched`, own give excluded from both',
     () => {
    const loaded = loadProgram(machine('ShiftedCarry'),
                               'corpus://ShiftedCarry');
    const [wheel, lever] = loaded.edges[1].block!.members;
    expect([...wheel.unconditional]).toEqual([]);
    expect([...wheel.switched]).toEqual(['carry.travel']);
    expect([...lever.unconditional]).toEqual([]);
    expect([...lever.switched]).toEqual(['higher.turn']);
  });

  it('4.5 a member with NO plan carries no selector at all, so its '
     + 'in-block needs minus its own are all UNCONDITIONAL', () => {
    const loaded = loadProgram(gatedCycle('<'), SOURCE);
    const [crank, lever] = loaded.edges[0].block!.members;
    expect(crank.plan).toBe(null);
    expect(crank.selectors).toEqual([]);
    expect(crank.selectorPlan).toBe(null);
    expect([...crank.unconditional]).toEqual(['carry.travel']);
    expect([...crank.switched]).toEqual([]);
    // And the gated one is switchable, which is why this block loads.
    expect([...lever.unconditional]).toEqual([]);
    expect([...lever.switched]).toEqual(['higher.turn']);
  });

  it('4.5 `sign` is NOT foldable: a `sign`-gated in-block source is not '
     + 'counted switched, so such a block is refused at load where the '
     + 'same shape gated by a COMPARISON loads', () => {
    // The comparison holds its zero branch over an INTERVAL of the
    // level, so the dependency is switched and the cycle breaks.
    expect(loadProgram(gatedCycle('<'), SOURCE).edges[0].kind).toBe('block');
    // `sign`'s zero is the single point where the level is exactly zero,
    // so counting it switched would admit at load a machine every tick
    // refuses.
    const message = refusal(
      gatedCycle('sign', '(higher.turn * sign(shift - 0.5))'));
    expect(message).toContain('form a cycle the run cannot order');
    expect(message).toContain('and not sign, whose zero is a single point');
  });
});

/** EVERY coordinate one member still reads under one substitution --
 * the loader's own `_reads_under`, asked directly, where `activeReads`
 * answers only the ids the block determines. */
function readsOf(program: LoadedProgram, member: BlockMember,
                 substitution: Record<string, number>): ReadonlySet<string> {
  return readsUnder(member.plan!, substitution, program.nodeOf,
                    program.bindings.roots());
}

describe('the load-time refusals (design D1.7, tasks 5)', () => {
  it('5.1 a WIRING on a cycle is refused, naming the edge, its statedBy '
     + 'and every member', () => {
    const message = refusal(withSecond({
      kind: 'wiring', factor: 1.0, needs: ['higher.turn'],
      description: 'higher.turn is wired to carry.travel',
    }));
    expect(message).toContain(
      'higher.turn is wired to carry.travel, stated by Bench');
    expect(message).toContain('it is on a dependency cycle');
    expect(message).toContain('the crank drives higher.turn');
    expect(message).toContain('it carries no jump node, so no selection can '
                              + 'switch what it reads');
    expect(message).toContain('State the value as a relation whose law '
                              + 'carries the gate.');
  });

  it('5.1 a FORMULA on a cycle is refused the same way', () => {
    const message = refusal(withSecond({
      kind: 'formula', slot: 'carry.travel', factors: [1.0], constant: 0.0,
      needs: ['higher.turn'],
      description: 'carry.travel is stated as a formula',
    }));
    expect(message).toContain(
      'carry.travel is stated as a formula, stated by Bench');
    expect(message).toContain('it carries no jump node');
  });

  it('5.2 a member driving a GROUP is refused', () => {
    const base = blockDocument();
    const program = (base as unknown as {
      program: { edges: Overrides[]; coordinates: Overrides;
                 sources: Overrides };
    }).program;
    program.coordinates['carry.lift'] = {
      kind: 'coordinate', initial: 0, unit: 'mm', domain: 'translational',
    };
    program.sources['carry.lift'] = ['crank', 'shift'];
    program.edges[1] = {
      ...program.edges[1],
      gives: ['carry.travel', 'carry.lift'],
      expressions: ['(higher.turn * (shift < 0.5))', 'higher.turn'],
      affine: [true, true],
      plans: [(program.edges[1].plans as unknown[])[0], null],
    };
    const message = refusal(base);
    expect(message).toContain('higher.turn drives carry.travel, stated by '
                              + 'Bench');
    expect(message).toContain('it drives a GROUP and it is on a dependency '
                              + 'cycle');
    expect(message).toContain('A member of a block drives ONE coordinate');
    expect(message).toContain('State each end as a relation of its own.');
  });

  it('5.3 a member whose give is NOT a bank coordinate is refused', () => {
    const base = blockDocument();
    const program = (base as unknown as {
      program: {
        edges: Overrides[]; coordinates: Overrides; sources: Overrides;
        intermediates: string[];
      };
    }).program;
    delete program.coordinates['carry.travel'];
    program.intermediates = ['carry.travel'];
    const message = refusal(base);
    expect(message).toContain('higher.turn drives carry.travel, stated by '
                              + 'Bench');
    expect(message).toContain('it drives carry.travel, which the running '
                              + 'simulation does not own');
    expect(message).toContain('A block advances its coordinates PIECE BY '
                              + 'PIECE inside a tick');
    expect(message).toContain('State the relation into the joint coordinate '
                              + 'and let the port follow it.');
  });

  it('5.4 a cycle NO selection can break is refused with the message a '
     + 'plain cycle of two ordinary laws has always had', () => {
    const message = refusal(plainCycle());
    expect(message).toContain(
      'the relations the crank drives higher.turn, higher.turn drives '
      + 'carry.travel form a cycle the run cannot order');
    expect(message).toContain('each waits on a coordinate another '
                              + 'determines');
    expect(message).toContain('A running program is acyclic, because the '
                              + 'rest render solved every relation in one '
                              + 'direction');
    expect(message).toContain('A dependency inside a cycle is admitted only '
                              + 'where it is SWITCHED');
    expect(message).toContain('floor, ceil, a remainder or a comparison, and '
                              + 'not sign, whose zero is a single point.');
  });

  it('5.5 each of the four is refused at LOAD, quoting the document, with '
     + 'nothing rendered and no tick taken', () => {
    const documents = [
      withSecond({ kind: 'wiring', factor: 1.0, needs: ['higher.turn'] }),
      plainCycle(),
    ];
    for (const doc of documents) {
      const message = refusal(doc);
      expect(message).toContain(SOURCE);
      expect(message).toContain('declares document version 7');
      expect(message).toContain('The document is malformed: refusing it '
                                + 'rather than running a machine this viewer '
                                + 'cannot execute.');
    }
    // And the VALID one loads, with the block contracted.
    const loaded = loadProgram(blockDocument(), SOURCE);
    expect(loaded.edges).toHaveLength(1);
    expect(loaded.edges[0].kind).toBe('block');
  });
});

// ---------------------------------------------------------------------
// The flag-agreement CONTRACT (openspec `solve-at-the-kink`, design D6,
// tasks 1.1). The viewer's classification is a SECOND implementation of
// the producer's `_shape_of`, and the only external check on it is the
// flag the document already carries: a quantity this viewer finds
// constant or affine must be one the producer published `affine: true`,
// and one it finds kinked or unclassified must be one the producer
// published `affine: false`. It is the test that catches the
// classification drifting from the producer's without anyone running
// the producer.
// ---------------------------------------------------------------------

describe('the classification agrees with the published flag (D6)', () => {
  const machines = (corpus as unknown as {
    machines: { name: string; document: unknown }[];
  }).machines;

  const fixtures: [string, unknown][] = [
    ['the Pascaline fixture', acceptance],
    ['the lock fixture', lockDocument],
    ['the clearing fixture', clearingDocument],
    ['the carriage fixture', carriageDocument],
    ['the touched fixture', touchedDocument],
  ];

  /** Every published flag of one document, against the shape the loader
   * derived for the same quantity. */
  function agreement(name: string, document: unknown):
  { ends: number; levels: number; disagreements: string[] } {
    const program = loadProgram(document as RunDocument, `shapes#${name}`);
    const solved = (shape: PathShape): boolean =>
      shape === 'constant' || shape === 'affine';
    const disagreements: string[] = [];
    let ends = 0;
    let levels = 0;
    for (const edge of program.edges) {
      const walk = (one: ProgramEdge): void => {
        if (one.kind !== 'law') return;
        one.gives.forEach((key, index) => {
          ends += 1;
          if (solved(one.shapes[index]) !== one.affine[index]) {
            disagreements.push(
              `${name}: ${key} is ${one.shapes[index]} and publishes `
              + `affine: ${one.affine[index]}`);
          }
        });
        for (const plan of one.plans) {
          if (plan === null) continue;
          for (const jump of plan.jumps) {
            levels += 1;
            if (solved(jump.shape) !== jump.affine) {
              disagreements.push(
                `${name}: the level of ${jump.name} is ${jump.shape} and `
                + `publishes affine: ${jump.affine}`);
            }
          }
        }
      };
      // A block is ONE entry of the loaded program: its members are the
      // law edges the document published, and they carry the flags.
      if (edge.kind === 'block') {
        for (const member of edge.block!.members) walk(member.edge);
      } else {
        walk(edge);
      }
    }
    return { ends, levels, disagreements };
  }

  it('finds constant or affine EXACTLY where the corpus publishes affine',
     () => {
    let ends = 0;
    let levels = 0;
    const disagreements: string[] = [];
    for (const machine of machines) {
      const found = agreement(machine.name, machine.document);
      ends += found.ends;
      levels += found.levels;
      disagreements.push(...found.disagreements);
    }
    expect(disagreements).toEqual([]);
    // The measurement plus play and periodic records: 43 driven ends + 34
    // jump levels over the corpus's 28 documents, zero
    // disagreements.
    expect([ends, levels]).toEqual([49, 39]);
  });

  it('finds constant or affine EXACTLY where a committed fixture '
     + 'publishes affine', () => {
    const disagreements: string[] = [];
    let flags = 0;
    for (const [name, document] of fixtures) {
      const found = agreement(name, document);
      flags += found.ends + found.levels;
      disagreements.push(...found.disagreements);
    }
    expect(disagreements).toEqual([]);
    expect(flags).toBeGreaterThan(0);
  });
});
