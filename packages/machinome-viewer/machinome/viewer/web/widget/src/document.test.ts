/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The schema v2 consumer gate, INVERTED (ADR-056 stage 3b, design D8).
//
// The export delta's manifest contract says a consumer SHALL either
// evaluate driver-referencing expressions or fail loudly on a non-empty
// `drivers` table rather than render a wrong pose. Stage 3a took the
// second branch: this viewer evaluated `$t` and nothing else, so it
// refused every non-empty table. It now takes the first -- a document
// with drivers loads and renders at the pose its table's defaults
// imply, so these tests changed meaning with the capability.
//
// What stays refused is a MALFORMED document: one whose expressions
// name a qualified id its own table does not declare. There is no value
// to bind for it, and rendering it anyway would show a wrong machine
// rather than an error. The producer guarantees this cannot happen
// (every referenced id appears in the table); the gate is what makes a
// broken producer loud instead of silent.

import { describe, expect, it } from 'vitest';
import {
  assertRenderable, mountRetained, RENDERED_VERSIONS,
} from './viewer';
import { expressionMetrics, prepare, releaseExpressions } from './expressions';
import {
  Manifest, ManifestFlexible, ManifestNode, RawOperation,
} from './types';
import markedFixture from '../../../tests/fixtures/marked/manifest.json';

const node = (name: string, operations: RawOperation[],
              children?: ManifestNode[]): ManifestNode => ({
  name, type: 'AssemblyNode', color: null, operations, children,
});

// The valve spring of `tests/flexible_project/spring.py`, as the
// producer publishes it: the spec verbatim and one expression per
// parameter.
const SPRING_SPEC = {
  molejo: '0.1',
  profile: { type: 'circle', radius: 2.0 },
  path: [{ type: 'helix', radius: 14.0, turns: 6.5,
           height: { param: 'height' } }],
  loop: false,
  tessellation: { path: 240, profile: 16 },
};

const spring = (overrides: Partial<ManifestFlexible> = {}): ManifestNode => ({
  name: 'spring', type: 'LeafNode', color: null, operations: [],
  flexible: {
    tech: 'molejo', spec: SPRING_SPEC,
    params: { height: '(46.8 - valvetrain.lift)' },
    ...overrides,
  },
});

const lift = {
  default: 0.0, range: [0.0, 12.0], unit: 'mm',
  dtype: 'float', scale: null,
};

const document = (overrides: Partial<Manifest>): Manifest => ({
  format: 'machinome-export',
  version: 2,
  animation: { fps: 30, frames: 360 },
  root: node('root', []),
  ...overrides,
});

const motor = {
  default: 8000, range: [0, 8000], unit: 'ustep',
  dtype: 'int', scale: 0.0125,
};

describe('assertRenderable', () => {
  it('accepts Machinome and legacy solid-node document formats', () => {
    expect(() => assertRenderable(document(), '/m.json')).not.toThrow();
    expect(() => assertRenderable(
      document({ format: 'solid-node-export' }), '/legacy.json',
    )).not.toThrow();
  });

  it('refuses an unrelated document format', () => {
    expect(() => assertRenderable(
      document({ format: 'other-export' }), '/other.json',
    )).toThrow(/other-export/);
  });

  it('accepts a version 1 document, which carries no table at all', () => {
    expect(() =>
      assertRenderable(document({ version: 1, drivers: undefined }), '/m.json'),
    ).not.toThrow();
  });

  it('accepts a version 2 document with an empty driver table', () => {
    expect(() =>
      assertRenderable(document({ drivers: {} }), '/m.json'),
    ).not.toThrow();
  });

  it('leaves a $t document alone: animation time is not a driver', () => {
    const manifest = document({
      drivers: {},
      root: node('root', [['r', '(360.0 * $t)', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('accepts a non-empty table whose ids its expressions declare', () => {
    // Stage 3a refused exactly this document. It now renders.
    const manifest = document({
      drivers: { 'x_axis.motor': motor },
      root: node('root', [], [
        node('x_axis', [], [
          node('carriage', [['t', ['(x_axis.motor * 0.0125)', '0', '0']]]),
        ]),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('refuses an expression naming an id the table does not declare', () => {
    const manifest = document({
      drivers: { 'x_axis.motor': motor },
      root: node('root', [], [
        node('z_axis', [['r', '(z_axis.motor * 0.1125)', [0, 0, 1]]]),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/z_axis\.motor/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses a driver expression under an empty table too', () => {
    const manifest = document({
      drivers: {},
      root: node('root', [['t', ['(x_axis.motor * 0.0125)', '0', '0']]]),
    });

    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/x_axis\.motor/);
  });

  it('names the undeclared id even beside a legal one', () => {
    const manifest = document({
      drivers: { 'x_axis.motor': motor },
      root: node('root', [['t', [
        '((x_axis.motor * 0.0125) + (y_axis.motor * 0.0125))', '0', '0',
      ]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/y_axis\.motor/);
  });
});

// Schema v3 (the flexible node shape). The producer emits the LOWEST
// version its content needs, so this viewer accepts the whole range it
// can render and refuses anything outside it -- the same posture it
// takes toward a `tech` it cannot evaluate, and for the same reason:
// a schema this build cannot read is not a document to guess at.
describe('assertRenderable on a flexible document', () => {
  it('accepts a version 3 document carrying a flexible node', () => {
    const manifest = document({
      version: 3,
      drivers: { 'valvetrain.lift': lift },
      root: node('engine', [], [node('valvetrain', [], [spring()])]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('refuses a technology it cannot evaluate, naming node and tech', () => {
    const manifest = document({
      version: 3,
      drivers: { 'valvetrain.lift': lift },
      root: node('engine', [], [spring({ tech: 'wibble' })]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/spring/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/wibble/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/molejo/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  // A `tech` this viewer evaluates, carrying a spec its bundled evaluator
  // cannot read -- what a document written for an older molejo is. The
  // document is refused whole, like an unevaluable technology, rather
  // than loading a tree that throws on a later frame.
  it('refuses a spec its evaluator cannot read, naming node and reason', () => {
    const manifest = document({
      version: 3,
      drivers: { 'valvetrain.lift': lift },
      root: node('engine', [], [
        spring({ spec: { ...SPRING_SPEC, molejo: 1 } }),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/spring/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/spec\.molejo/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses a version it does not render, naming it and the ones it does', () => {
    // OpenSpec `run-in-the-worker`: version 5 is now RENDERED (see the
    // `assertRenderable on a document carrying a program` suite below),
    // so the version this test names moved to 6. OpenSpec
    // `execute-the-self-read`: version 6 is now rendered too, so it
    // moved again to 7. OpenSpec `execute-the-selection`: version 7 --
    // a program carrying a BLOCK -- is rendered too, so it moves to 8:
    // the next one still refused, and the same sentence a version 5
    // document got from every viewer released so far. OpenSpec
    // `execute-the-commit`: version 8 -- a root that declares a State --
    // is rendered too, so it moves to 9. OpenSpec
    // `execute-running-play`: version 9 carries PLAY, so it moves to 10.
    // `execute-running-time-drives`: version 10 is executed; 11 is refused.
    const manifest = document({
      version: 12 as unknown as Manifest['version'],
      root: node('root', []),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/\b12\b/);
    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('holds a `params` expression to the same drivers table', () => {
    // `params` is an expression like any other, so an id its own table
    // does not declare is the same malformed document as an operation's
    // -- there is no value to bind, and evaluating it anyway would show
    // a wrong SHAPE instead of a wrong pose.
    const manifest = document({
      version: 3,
      drivers: {},
      root: node('engine', [], [spring()]),
    });

    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/valvetrain\.lift/);
  });

  it('leaves a `$t` parameter alone: animation time is not a driver', () => {
    const manifest = document({
      version: 3,
      drivers: {},
      root: node('engine', [], [
        spring({ params: { height: '(46.8 - (12.0 * $t))' } }),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });
});

// OpenSpec `read-expression-bindings` (design D7). Version 4's `bindings`
// table is validated at load, beside every refusal already here: a
// malformed table is refused naming the entry, a dangling reference is
// refused naming it (whether reached from an operation, a flexible
// `params` entry, or another binding's own expression), and a name that
// IS a binding is never reported as an undeclared driver -- the
// grasshopper document's exact shape, an empty `drivers` table whose
// every operation names an entry.
describe('assertRenderable on a document carrying bindings', () => {
  it('accepts a version 4 document carrying a table', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      bindings: [{ name: '_b0', expression: '(360.0 * $t)' }],
      root: node('root', [['r', '_b0', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('is a binding name, not an undeclared driver -- the grasshopper document\'s own shape', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      drivers: {},
      bindings: [
        { name: '_b0', expression: '($t * 43200.0)' },
        { name: '_b1', expression: 'floor(_b0)' },
      ],
      root: node('escapement', [['r', '_b1', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('refuses an operation naming an entry the table does not carry', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      bindings: [{ name: '_b0', expression: '$t' }],
      root: node('root', [['r', '_b99', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/_b99/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('reaches assertRenderable, rather than raising bare, for a malformed table', () => {
    // The 1.1 shape-and-validation cases, reached through the loader
    // this time: `bindingTable` throws, and `assertRenderable` -- which
    // calls it before walking a single expression -- does not catch or
    // reword it.
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      bindings: [
        { name: '_b0', expression: '$t' },
        { name: '_b0', expression: '(2.0 * $t)' },
      ],
      root: node('root', []),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/_b0/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/m\.json/);
  });

  it('refuses an undeclared driver id named from an ENTRY\'s own expression', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      drivers: { 'x_axis.motor': motor },
      bindings: [{ name: '_b0', expression: '(y_axis.motor * 2.0)' }],
      root: node('root', [['r', '_b0', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/y_axis\.motor/);
  });

  it('refuses a flexible leaf\'s `params` naming a dangling entry', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      drivers: {},
      bindings: [{ name: '_b0', expression: '$t' }],
      root: node('engine', [], [spring({ params: { height: '_b99' } })]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/_b99/);
  });

  it('resolves a chain of entries reached from an operation', () => {
    const manifest = document({
      version: 4 as unknown as Manifest['version'],
      drivers: { 'x_axis.motor': motor },
      bindings: [
        { name: '_b0', expression: '($t * 2.0)' },
        { name: '_b1', expression: '(_b0 + x_axis.motor)' },
      ],
      root: node('root', [['r', '_b1', [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });
});

// D10: an expression form the shared evaluation cannot support -- an
// inline function, which nothing the producer emits carries -- is
// refused when the document is LOADED, beside the refusals above.
// `assertRenderable` already walks every operation's and every
// flexible node's `params` expression through `freeVariables` before
// anything is rendered, so once that walk reads the shared DAG this
// refusal happens here, with no change to viewer.ts.
describe('assertRenderable refuses an inline function (D10)', () => {
  it('names the form and quotes the expression, for an operation', () => {
    const expression = '(x => x + 1)';
    const manifest = document({
      root: node('root', [['r', expression, [0, 0, 1]]]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/Func/);
    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/x => x \+ 1/);
  });

  it('names the form and quotes the expression, for a flexible `params` entry', () => {
    const manifest = document({
      version: 3,
      drivers: {},
      root: node('engine', [], [
        spring({ params: { height: '(x => x + 1)' } }),
      ]),
    });

    expect(() => assertRenderable(manifest, '/m.json')).toThrow(/Func/);
  });

  it('truncates a very long refused expression rather than quoting it whole', () => {
    const expression = `(x => ${'1 + '.repeat(100)}1)`;
    const manifest = document({
      root: node('root', [['r', expression, [0, 0, 1]]]),
    });

    let message = '';
    try {
      assertRenderable(manifest, '/m.json');
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message.length).toBeLessThan(expression.length);
  });
});

// A refused mount must leave no hold on the shared table (D8): the
// spec's "disposing of the last viewer on the page leaves none of it"
// has to hold for a page whose viewer refused a document too, or a
// `machinome develop` session that republishes a broken document and then
// a good one leaks a hold forever -- no handle, no dispose(), and
// nothing ever brings the mount count back to zero. `mountRetained`
// (viewer.ts) is the fix: it retains the shared table ONLY once its
// `action` -- `mount()`'s initial document load, `loadDocument` ->
// `assertRenderable`, exactly the D10 refusal surface -- has already
// succeeded. `mount()` itself needs a DOM/WebGL environment this
// package's suite does not set up, so this exercises the extracted,
// directly-testable piece that carries the actual fix.
describe('mountRetained holds the shared table only for a mount that succeeded (D8)', () => {
  it('a refused action never retains, so one later successful mount/dispose cycle alone empties the table', async () => {
    const refusal = new Error('refused: undeclared driver');

    await expect(mountRetained(async () => {
      throw refusal;
    })).rejects.toThrow(refusal);

    // If the refused attempt above HAD retained (the bug), this single
    // balanced retain/release from a genuinely successful mount would
    // leave the earlier, dangling hold still standing, and the table
    // would NOT come back to empty.
    await mountRetained(async () => {
      prepare('(9100001 + 1)');
    });
    releaseExpressions();

    expect(expressionMetrics().nodes).toBe(0);
  });

  it('retains once the action succeeds, so its own dispose (a matching release) does empty the table', async () => {
    await mountRetained(async () => {
      prepare('(9200002 + 2)');
    });
    expect(expressionMetrics().nodes).toBeGreaterThan(0);

    releaseExpressions(); // the handle's dispose(), in the real mount()

    expect(expressionMetrics().nodes).toBe(0);
  });
});

// ---------------------------------------------------------------------
// OpenSpec `run-in-the-worker` (design §4, §10). A version 5 document is
// a version 4 one plus the compiled mechanical program, and the names
// its expressions may read widen with it: the program's clock, its bank
// coordinates, the values it publishes as computed, and -- inside a jump
// plan's own expressions -- that plan's branch placeholders.
// ---------------------------------------------------------------------

const PROGRAM = {
  identity: 'a-program',
  clock: 'time',
  coordinates: {
    crank: { kind: 'input', initial: 0, domain: null },
    'units.drum.turn': {
      kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
    },
  },
  intermediates: [],
  edges: [{
    kind: 'law',
    needs: ['crank'],
    gives: ['units.drum.turn'],
    description: 'crank drives units.drum.turn',
    stated_by: 'Bench',
    expressions: ['(36.0 * crank)'],
    affine: [true],
    plans: [null],
  }],
  spans: {},
  sources: { crank: ['crank'], 'units.drum.turn': ['crank'] },
  limits: {
    crossing_tolerance: 1e-12, subdivisions: 64, bisection_rounds: 64,
    max_crossings: 1000, agreement: 1e-9,
  },
};

const entry = {
  default: 0, range: null, unit: 'digit', dtype: null, scale: null,
};

const running = (overrides: Record<string, unknown> = {},
                 program: Record<string, unknown> = {}): Manifest =>
  document({
    version: 5 as unknown as Manifest['version'],
    drivers: { crank: entry },
    // The pose names the joint COORDINATE, not the driver: under a run
    // it is the bank that poses the geometry.
    root: node('root', [['r', 'units.drum.turn', [0, 0, 1]]]),
    ...overrides,
  } as Partial<Manifest>) as Manifest & { program?: unknown };

function withProgram(overrides: Record<string, unknown> = {},
                     program: Record<string, unknown> = {}): Manifest {
  const manifest = running(overrides) as Manifest & { program?: unknown };
  manifest.program = { ...PROGRAM, ...program };
  return manifest;
}

describe('assertRenderable on a document carrying a program', () => {
  it('renders versions 1 through 11 and says so in its list', () => {
    expect(RENDERED_VERSIONS).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
  });

  it('accepts a version 6 document -- one whose program carries a law '
     + 'that reads the coordinate it drives -- and hands back its loaded '
     + 'program', () => {
    const manifest = withProgram(
      { version: 6 as unknown as Manifest['version'] });
    const { program } = assertRenderable(manifest, '/m.json');
    expect(program).not.toBeNull();
    expect(program!.identity).toBe('a-program');
  });

  it('refuses a version 6 document with NO program at all -- the second '
     + 'clause of the gate must not let it through as a treeful document '
     + 'with nothing to run', () => {
    const manifest = running({ version: 6 as unknown as Manifest['version'] });
    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/"program"/);
  });

  it('accepts a version 7 document -- one whose program carries a BLOCK, '
     + 'a cycle every selection breaks -- and hands back its loaded '
     + 'program', () => {
    const manifest = withProgram(
      { version: 7 as unknown as Manifest['version'] });
    const { program } = assertRenderable(manifest, '/m.json');
    expect(program).not.toBeNull();
    expect(program!.identity).toBe('a-program');
  });

  it('refuses a version 12 document by name, naming what it renders', () => {
    const manifest = withProgram(
      { version: 12 as unknown as Manifest['version'] });
    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/renders versions 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11/);
  });

  it('refuses a document carrying BOTH a program and a clocked machine',
     () => {
    // Two machines: a root publishes one or the other, and version 8 is
    // a property of the ROOT'S DECLARATION (OpenSpec
    // `execute-the-commit`, design §1).
    const manifest = withProgram(
      { version: 8 as unknown as Manifest['version'] });
    (manifest as unknown as { clocked: unknown }).clocked = {};
    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/two machines/);
  });

  it('11.5 the PROGRAM gate is a FLOOR and does not move: a version 7 '
     + 'document with no program at all still meets the program '
     + 'refusal, not the treeful path', () => {
    const manifest = running({ version: 7 as unknown as Manifest['version'] });
    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/"program"/);
  });

  it('accepts a version 5 document and hands back its loaded program', () => {
    const { program } = assertRenderable(withProgram(), '/m.json');
    expect(program).not.toBeNull();
    expect(program!.identity).toBe('a-program');
    expect(program!.order).toEqual(['crank', 'units.drum.turn']);
  });

  it('hands back no program for a document that carries none', () => {
    const { program } = assertRenderable(
      document({ version: 4 as unknown as Manifest['version'] }), '/m.json');
    expect(program).toBeNull();
  });

  it('refuses a version 5 document with no program at all', () => {
    const manifest = running();
    expect(() => assertRenderable(manifest, '/m.json'))
      .toThrow(/"program"/);
  });

  it('refuses a malformed program by the loader\'s own messages', () => {
    expect(() => assertRenderable(
      withProgram({}, { limits: { subdivisions: 64 } }), '/m.json'))
      .toThrow(/crossing_tolerance/);
    expect(() => assertRenderable(
      withProgram({}, {
        edges: [{ ...PROGRAM.edges[0], kind: 'coupling' }],
      }), '/m.json')).toThrow(/coupling/);
  });

  it('admits the clock, a coordinate and a computed value as names', () => {
    expect(() => assertRenderable(withProgram({
      root: node('root', [
        ['r', 'units.drum.turn', [0, 0, 1]],
        ['t', ['time', 'crank', '0']],
      ]),
    }), '/m.json')).not.toThrow();
  });

  it('admits a plan\'s placeholder inside that plan, and nowhere else', () => {
    const planned = {
      edges: [{
        kind: 'law',
        needs: ['crank'],
        gives: ['units.drum.turn'],
        description: 'crank drives units.drum.turn',
        stated_by: 'Bench',
        expressions: ['(crank - floor(crank))'],
        affine: [true],
        plans: [{
          skeleton: '(crank - _j0)',
          jumps: [{ name: '_j0', primitive: 'floor', level: 'crank',
                    affine: true }],
        }],
      }],
    };
    expect(() => assertRenderable(withProgram({}, planned), '/m.json'))
      .not.toThrow();
    // The same placeholder in a POSE expression is not a declared name.
    expect(() => assertRenderable(withProgram({
      root: node('root', [['r', '_j0', [0, 0, 1]]]),
    }, planned), '/m.json')).toThrow(/_j0/);
  });

  it('admits a bindings entry that names a placeholder, which a version 5 '
     + 'document publishes', () => {
    // Design §15 finding 2: a plan's skeleton shares subexpressions into
    // the same table, so the table carries entries only the plan can
    // evaluate. This viewer never evaluates the table forward, so they
    // cost it nothing -- and a placeholder reached from an OPERATION is
    // still refused, by the case above.
    const planned = {
      edges: [{
        kind: 'law',
        needs: ['crank'],
        gives: ['units.drum.turn'],
        description: 'crank drives units.drum.turn',
        stated_by: 'Bench',
        expressions: ['(crank - floor(crank))'],
        affine: [true],
        plans: [{
          skeleton: '(crank - _b1)',
          jumps: [{ name: '_j0', primitive: 'floor', level: 'crank',
                    affine: true }],
        }],
      }],
    };
    const manifest = withProgram({
      bindings: [{ name: '_b1', expression: '(1.0 * _j0)' }],
    } as Record<string, unknown>, planned);
    expect(() => assertRenderable(manifest, '/m.json')).not.toThrow();
  });

  it('still refuses a name that is none of those', () => {
    expect(() => assertRenderable(withProgram({
      root: node('root', [['r', 'nowhere.at.all', [0, 0, 1]]]),
    }), '/m.json')).toThrow(/nowhere\.at\.all/);
  });

  it('refuses a pose that reads a computed value no edge determines', () => {
    // Design §15 finding 1: a published computed value nothing computes
    // is admitted as a NAME and refused the moment something reads it.
    expect(() => assertRenderable(withProgram({
      root: node('root', [['r', 'units.wheel', [0, 0, 1]]]),
    }, { intermediates: ['units.wheel'],
         sources: { ...PROGRAM.sources, 'units.wheel': [] } }), '/m.json'))
      .toThrow(/units\.wheel/);
  });
});

// ---------------------------------------------------------------------
// OpenSpec `drive-the-run-by-touch` (design D1, D2). A version 5
// document MAY carry a `controls` table beside `instructions`; it joins
// this same refusal surface, after the program its entries reference
// and before the tree walk, so a table this viewer cannot resolve is
// refused BEFORE a single thing is rendered. A document carrying no key
// reaches exactly the code it reached before.
// ---------------------------------------------------------------------

const dial = node('dial', []);
const joint = node('input', [['r', 'units.drum.turn', [1, 0, 0]]], [dial]);
const column = node('units', [], [joint, node('lid', [])]);

const TURN_CONTROL = {
  kind: 'turn',
  part: ['units', 'input', 'dial'],
  input: 'crank',
  per_unit: -36.0,
  joint: ['units', 'input'],
  coordinate: 'units.drum.turn',
  axis: [1, 0, 0],
  origin: [0, 0, 0],
};

const BUTTON_CONTROL = {
  kind: 'button',
  part: ['units', 'input', 'dial'],
  instruction: 'Add one',
  joint: ['units', 'input'],
  coordinate: 'units.drum.turn',
  axis: [1, 0, 0],
  origin: [0, 0, 0],
};

function touchable(controls: unknown,
                   root: ManifestNode = node('root', [], [column])): Manifest {
  const manifest = withProgram({
    root,
    instructions: { 'Add one': { targets: { crank: 1 }, duration: 1 } },
  } as Record<string, unknown>);
  (manifest as { controls?: unknown }).controls = controls;
  return manifest;
}

describe('assertRenderable on a document carrying controls', () => {
  it('hands back the parsed controls, in the document\'s own key order', () => {
    const { controls } = assertRenderable(
      touchable({ 'units dial': BUTTON_CONTROL, 'turn units': TURN_CONTROL }),
      '/m.json');
    expect(controls.map((one) => one.name))
      .toEqual(['units dial', 'turn units']);
    expect(controls[1].perUnit).toBe(-36);
    expect(controls[1].joint).toEqual(['units', 'input']);
  });

  it('hands back [] for a document carrying no controls key', () => {
    expect(assertRenderable(withProgram(), '/m.json').controls).toEqual([]);
    expect(assertRenderable(
      document({ version: 4 as unknown as Manifest['version'] }),
      '/m.json').controls).toEqual([]);
  });

  it('refuses a part its own tree does not contain, naming it', () => {
    expect(() => assertRenderable(
      touchable({ 'turn units': { ...TURN_CONTROL, part: ['units', 'knob'] } }),
      '/m.json')).toThrow(/Unknown assembly path: units\/knob/);
  });

  it('refuses an instruction the document does not declare', () => {
    expect(() => assertRenderable(
      touchable({ 'units dial': { ...BUTTON_CONTROL,
                                  instruction: 'Add two' } }),
      '/m.json')).toThrow(/Add two.*Add one/s);
  });

  it('refuses a ratio of zero, saying the gesture has no quantum', () => {
    expect(() => assertRenderable(
      touchable({ 'turn units': { ...TURN_CONTROL, per_unit: 0 } }),
      '/m.json')).toThrow(/quantum/);
  });

  it('refuses a joint whose leading operations are not the placement', () => {
    const wrong = node('root', [], [node('units', [], [
      node('input', [['r', 'crank', [1, 0, 0]]], [node('dial', [])]),
    ])]);
    expect(() => assertRenderable(
      touchable({ 'turn units': TURN_CONTROL }, wrong), '/m.json'))
      .toThrow(/units\/input/);
  });

  it('accepts a joint placed off its node\'s origin', () => {
    const offset = node('root', [], [node('units', [], [
      node('input', [['t', ['0', '-3', '0']],
                     ['r', 'units.drum.turn', [1, 0, 0]],
                     ['t', ['0', '3', '0']]], [node('dial', [])]),
    ])]);
    const { controls } = assertRenderable(
      touchable({ 'turn units': { ...TURN_CONTROL, origin: [0, 3, 0] } },
                offset), '/m.json');
    expect(controls[0].origin).toEqual([0, 3, 0]);
  });

  it('refuses a controls table on a document that carries no program', () => {
    const posed = document({
      version: 4 as unknown as Manifest['version'],
      root: node('root', [], [column]),
    }) as Manifest & { controls?: unknown };
    posed.controls = { 'turn units': TURN_CONTROL };
    expect(() => assertRenderable(posed, '/m.json'))
      .toThrow(/controls.*no program/s);
  });

  it('refuses the table before the tree is walked for driver ids', () => {
    // A document that is wrong in BOTH ways: the controls refusal is
    // the one that fires, because the table is read before the walk.
    const bad = touchable(
      { 'turn units': { ...TURN_CONTROL, per_unit: 0 } },
      node('root', [['r', 'nowhere.at.all', [0, 0, 1]]], [column]));
    expect(() => assertRenderable(bad, '/m.json')).toThrow(/quantum/);
  });
});

// OpenSpec `draw-what-a-part-carries`, design D6: a `markings` list this
// viewer cannot read is refused BY NAME -- the document, the node and
// the marking -- before anything is rendered, on the surface an
// unreadable bindings table, an inexecutable program and an unresolvable
// controls table already stand on. Half-reading is the failure mode: a
// viewer that reads nine digits and silently drops the tenth shows a
// FALSE register.
describe('assertRenderable on a document carrying markings', () => {
  const marked = (markings: unknown, overrides: Partial<ManifestNode> = {}) => {
    const part = {
      ...node('dial', []), model: 'dial.stl', mtime: 1, ...overrides,
    } as ManifestNode & { markings?: unknown };
    part.markings = markings;
    return document({ root: node('root', [], [part as ManifestNode]) });
  };

  const digits = { name: 'digits', model: 'dial.marking-digits.stl',
                   color: '#FFFFFF', mtime: 2 };

  it('accepts the marked bench the framework publishes', () => {
    expect(() => assertRenderable(
      markedFixture as unknown as Manifest, '/marked.json')).not.toThrow();
  });

  it('accepts a marking whose optional mtime is absent', () => {
    const { name, model, color } = digits;
    expect(() => assertRenderable(marked([{ name, model, color }]), '/m.json'))
      .not.toThrow();
  });

  it('refuses a markings value that is not a list, naming document and node', () => {
    expect(() => assertRenderable(marked({ digits }), '/m.json'))
      .toThrow(/\/m\.json.*"dial".*markings.*list/s);
  });

  it('refuses an entry that is not an object, naming where it is', () => {
    expect(() => assertRenderable(marked(['digits']), '/m.json'))
      .toThrow(/\/m\.json.*"dial".*0.*object/s);
  });

  it('refuses a marking whose name is not a non-empty string', () => {
    expect(() => assertRenderable(
      marked([{ ...digits, name: '' }]), '/m.json'))
      .toThrow(/\/m\.json.*"dial".*name/s);
    expect(() => assertRenderable(
      marked([{ ...digits, name: 7 }]), '/m.json'))
      .toThrow(/\/m\.json.*"dial".*name/s);
  });

  it('refuses a marking that names no artifact, naming node and marking', () => {
    expect(() => assertRenderable(
      marked([{ ...digits, model: '' }]), '/m.json'))
      .toThrow(/\/m\.json.*"dial".*"digits".*artifact/s);
    expect(() => assertRenderable(
      marked([{ ...digits, model: undefined }]), '/m.json'))
      .toThrow(/\/m\.json.*"dial".*"digits".*artifact/s);
  });

  it('refuses a colour that is not six hexadecimal digits', () => {
    for (const colour of ['white', '#FFF', '#GGGGGG', '#FFFFFFF', null, 16777215]) {
      expect(() => assertRenderable(
        marked([{ ...digits, color: colour }]), '/m.json'))
        .toThrow(/\/m\.json.*"dial".*"digits".*colour/s);
    }
  });

  it('refuses two markings of one node sharing a name', () => {
    expect(() => assertRenderable(marked([
      digits, { ...digits, model: 'other.stl' },
    ]), '/m.json')).toThrow(/\/m\.json.*"dial".*"digits".*twice/s);
  });

  it('refuses a markings list on a node that carries children', () => {
    expect(() => assertRenderable(
      marked([digits], { model: undefined, children: [node('pin', [])] }),
      '/m.json')).toThrow(/\/m\.json.*"dial".*rigid/s);
  });

  it('refuses a markings list on a flexible node', () => {
    const flexible = { ...spring(), model: undefined } as ManifestNode
      & { markings?: unknown };
    flexible.markings = [digits];
    expect(() => assertRenderable(
      document({ version: 3, drivers: { 'valvetrain.lift': lift },
                 root: node('root', [], [flexible as ManifestNode]) }),
      '/m.json')).toThrow(/\/m\.json.*"spring".*rigid/s);
  });

  it('refuses the markings before the tree is walked for driver ids', () => {
    // Wrong in BOTH ways: the markings refusal is the one that fires,
    // because a marking is read where the node is visited and the
    // undeclared-driver report is assembled only after the whole walk.
    const bad = marked([{ ...digits, color: 'white' }],
                       { operations: [['r', 'nowhere.at.all', [0, 0, 1]]] });
    expect(() => assertRenderable(bad, '/m.json')).toThrow(/colour/);
  });

  it('validates a document with no markings key exactly as it did', () => {
    // The stripped twin of the committed fixture: the same document,
    // one `del` away, reaching exactly the validation it reached before
    // this viewer could read a markings list.
    const twin = JSON.parse(JSON.stringify(markedFixture)) as Manifest;
    const strip = (one: ManifestNode) => {
      delete (one as { markings?: unknown }).markings;
      (one.children ?? []).forEach(strip);
    };
    strip(twin.root);
    expect(() => assertRenderable(twin, '/twin.json')).not.toThrow();
    expect(JSON.stringify(assertRenderable(twin, '/twin.json')))
      .toEqual(JSON.stringify(
        assertRenderable(markedFixture as unknown as Manifest, '/marked.json')));
  });
});
