/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// What a document's `controls` table means, and what a gesture on one
// decides, as pure data and pure vector math (OpenSpec
// `drive-the-run-by-touch`, design D17). Nothing here imports the DOM,
// three.js or the run: vectors are tuples, a ray is an origin and a
// direction, a matrix is the sixteen column-major numbers three.js's
// `matrixWorld` holds. `viewer.ts` keeps the three.js and the DOM and
// decides nothing, which is what lets every decision below be a node
// test beside `runControls.test.ts`'s.

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import {
  chooseMode, EDGE_ON, intersectPlane, MIN_RADIUS, readControls,
  sweepAngle, TurnPlanner, visibleUpTo, worldLine,
} from './partControls';
import type { Vec3 } from './partControls';
import type { Manifest, ManifestNode, RawOperation } from './types';

const node = (name: string, operations: RawOperation[],
              children?: ManifestNode[]): ManifestNode => ({
  name, type: 'AssemblyNode', color: null, operations, children,
});

const ENTRY = {
  default: 0, range: null, unit: 'digit', dtype: null, scale: null,
};

/** The acceptance document's own shape, cut down to one column: a joint
 * node posed by `units.input.turn` with the dial a leaf below it. */
const TREE = node('root', [], [
  node('units', [], [
    node('input', [['r', 'units.input.turn', [1, 0, 0]]], [
      node('dial', []),
      node('ratchet', []),
    ]),
    node('drum', [['r', 'units.drum.turn', [1, 0, 0]]], [
      node('numbers', []),
    ]),
    node('lid', []),
  ]),
]);

const PROGRAM = {
  coordinates: {
    units_entry: { kind: 'input', initial: 0, unit: 'digit', domain: null },
    'units.input.turn': {
      kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
    },
    'units.drum.turn': {
      kind: 'coordinate', initial: 0, unit: 'deg', domain: 'rotational',
    },
  },
};

const BUTTON = {
  kind: 'button',
  part: ['units', 'input', 'dial'],
  instruction: 'Add one',
  joint: ['units', 'input'],
  coordinate: 'units.input.turn',
  axis: [1, 0, 0],
  origin: [0, 0, 0],
};

const TURN = {
  kind: 'turn',
  part: ['units', 'input', 'dial'],
  input: 'units_entry',
  per_unit: -36.0,
  joint: ['units', 'input'],
  coordinate: 'units.input.turn',
  axis: [1, 0, 0],
  origin: [0, 0, 0],
};

function document(controls: unknown, root: ManifestNode = TREE): Manifest {
  return {
    format: 'solid-node-export',
    version: 5,
    animation: { fps: 30, frames: 360 },
    drivers: { units_entry: ENTRY },
    instructions: { 'Add one': { targets: { units_entry: 1 }, duration: 1 } },
    controls,
    root,
  } as unknown as Manifest;
}

/** One control, spread over the shared shapes above. */
function one(overrides: Record<string, unknown> = {},
             base: Record<string, unknown> = TURN): unknown {
  return { 'turn units': { ...base, ...overrides } };
}

function refusal(controls: unknown, root: ManifestNode = TREE,
                 program: unknown = PROGRAM): string {
  try {
    readControls(document(controls, root), '/m.json',
                 program as never);
  } catch (error) {
    return error instanceof Error ? error.message : String(error);
  }
  throw new Error('readControls accepted a table it must refuse');
}

describe('readControls refuses a table it cannot resolve (D1)', () => {
  it('refuses a table that is not an object', () => {
    const message = refusal('everything');
    expect(message).toContain('/m.json');
    expect(message).toContain('controls');
    expect(message).toContain('everything');
  });

  it('refuses an entry that is not an object', () => {
    const message = refusal({ 'turn units': 7 });
    expect(message).toContain('/m.json');
    expect(message).toContain('turn units');
    expect(message).toContain('7');
  });

  it('refuses a kind that is neither a press nor a turn', () => {
    const message = refusal(one({ kind: 'unknown' }));
    expect(message).toContain('turn units');
    expect(message).toContain('unknown');
    expect(message).toContain('button');
  });

  it('refuses a part that is not a list of node names', () => {
    const message = refusal(one({ part: 'units.input.dial' }));
    expect(message).toContain('turn units');
    expect(message).toContain('part');
    expect(message).toContain('units.input.dial');
  });

  it('refuses a joint that is not a list of node names', () => {
    const message = refusal(one({ joint: [1, 2] }));
    expect(message).toContain('turn units');
    expect(message).toContain('joint');
  });

  it('refuses a part naming no node of the document\'s own tree', () => {
    const message = refusal(one({ part: ['units', 'input', 'knob'] }));
    expect(message).toContain('turn units');
    expect(message).toContain('Unknown assembly path');
    expect(message).toContain('units/input/knob');
  });

  it('refuses a part naming an ambiguous node', () => {
    const twins = node('root', [], [
      node('units', [], [
        node('input', [['r', 'units.input.turn', [1, 0, 0]]], [
          node('dial', []), node('dial', []),
        ]),
      ]),
    ]);
    const message = refusal(one(), twins);
    expect(message).toContain('Ambiguous assembly path');
    expect(message).toContain('units/input/dial');
  });

  it('refuses a joint naming no node', () => {
    const message = refusal(one({ joint: ['units', 'axle'] }));
    expect(message).toContain('Unknown assembly path');
    expect(message).toContain('units/axle');
  });

  it('refuses a joint that is not an ancestor-or-self of its part', () => {
    const message = refusal(one({
      joint: ['units', 'drum'], coordinate: 'units.drum.turn',
    }));
    expect(message).toContain('turn units');
    expect(message).toContain('units/drum');
    expect(message).toContain('units/input/dial');
    expect(message).toContain('ancestor');
  });

  it('refuses an instruction the document does not declare, naming what it '
     + 'does', () => {
    const message = refusal(one({ instruction: 'Add two' }, BUTTON));
    expect(message).toContain('turn units');
    expect(message).toContain('Add two');
    expect(message).toContain('Add one');
  });

  it('refuses an input the drivers table does not declare, naming what it '
     + 'does', () => {
    const message = refusal(one({ input: 'tens_entry' }));
    expect(message).toContain('turn units');
    expect(message).toContain('tens_entry');
    expect(message).toContain('units_entry');
  });

  it('refuses a coordinate the program does not publish, naming what it '
     + 'does', () => {
    const message = refusal(one({ coordinate: 'units.carry.turn' }));
    expect(message).toContain('turn units');
    expect(message).toContain('units.carry.turn');
    expect(message).toContain('units.input.turn');
  });

  it('refuses a per_unit that is missing, not finite, or zero', () => {
    for (const bad of [undefined, null, 'thirty-six', Number.NaN,
                       Number.POSITIVE_INFINITY, 0, -0]) {
      const message = refusal(one({ per_unit: bad }));
      expect(message).toContain('turn units');
      expect(message).toContain('per_unit');
      expect(message).toContain('quantum');
    }
  });

  it('refuses an axis or an origin that is not three finite numbers', () => {
    for (const bad of [[1, 0], [1, 0, 0, 0], [1, 0, 'x'],
                       [1, 0, Number.NaN], 'x']) {
      expect(refusal(one({ axis: bad }))).toContain('axis');
      expect(refusal(one({ origin: bad }))).toContain('origin');
    }
  });

  it('refuses an axis of zero length', () => {
    const message = refusal(one({ axis: [0, 0, 0] }));
    expect(message).toContain('turn units');
    expect(message).toContain('axis');
    expect(message).toContain('no direction');
  });

  it('refuses a joint whose leading operations are not the placement', () => {
    // A rotation over another coordinate entirely.
    const other = node('root', [], [
      node('units', [], [
        node('input', [['r', 'units.drum.turn', [1, 0, 0]]],
             [node('dial', [])]),
      ]),
    ]);
    const message = refusal(one(), other);
    expect(message).toContain('turn units');
    expect(message).toContain('units/input');
    expect(message).toContain('units.input.turn');
    expect(message).toContain('units.drum.turn');

    // A rotation that is not the FIRST rotation of the leading run.
    const behind = node('root', [], [
      node('units', [], [
        node('input', [['r', '90', [0, 1, 0]],
                       ['r', 'units.input.turn', [1, 0, 0]]],
             [node('dial', [])]),
      ]),
    ]);
    expect(refusal(one(), behind)).toContain('turn units');

    // No rotation at all: a joint node that poses nothing.
    const still = node('root', [], [
      node('units', [], [
        node('input', [['t', ['1', '0', '0']]], [node('dial', [])]),
      ]),
    ]);
    expect(refusal(one(), still)).toContain('turn units');
  });

  it('refuses two controls of the same kind on one part (D3)', () => {
    const message = refusal({
      'turn units': TURN,
      'turn units again': { ...TURN },
    });
    expect(message).toContain('turn units');
    expect(message).toContain('turn units again');
    expect(message).toContain('units/input/dial');
  });

  it('refuses a controls table on a document that carries no program', () => {
    const message = refusal(one(), TREE, null);
    expect(message).toContain('/m.json');
    expect(message).toContain('controls');
    expect(message).toContain('program');
  });
});

describe('readControls accepts what the producer publishes (D1, D6)', () => {
  it('answers [] for a document carrying no controls key', () => {
    const manifest = document(undefined);
    delete (manifest as { controls?: unknown }).controls;
    expect(readControls(manifest, '/m.json', PROGRAM as never)).toEqual([]);
    // And for a document carrying no program either, which is every
    // version 1 to 4 document.
    expect(readControls(manifest, '/m.json', null)).toEqual([]);
  });

  it('accepts a button and a turn on ONE part, which is the dial', () => {
    const loaded = readControls(
      document({ 'units dial': BUTTON, 'turn units': TURN }),
      '/m.json', PROGRAM as never);
    expect(loaded.map((control) => control.name))
      .toEqual(['units dial', 'turn units']);
    expect(loaded[0].kind).toBe('button');
    expect(loaded[0].instruction).toBe('Add one');
    expect(loaded[0].perUnit).toBeNull();
    expect(loaded[1].kind).toBe('turn');
    expect(loaded[1].input).toBe('units_entry');
    expect(loaded[1].perUnit).toBe(-36);
  });

  it('accepts a joint placed off its node\'s origin: t(-a), r, t(a)', () => {
    // The shape a `Revolute(at=a)` publishes. `operationsMatrix`
    // composes as M_n · … · M_1, so the LEADING translation is the
    // innermost one and `origin` is its negation -- which is what makes
    // the leading run a rotation about the own-frame line (origin, axis).
    const offset = node('root', [], [
      node('units', [], [
        node('input', [['t', ['0', '-3', '0']],
                       ['r', 'units.input.turn', [1, 0, 0]],
                       ['t', ['0', '3', '0']]],
             [node('dial', [])]),
      ]),
    ]);
    const loaded = readControls(
      document(one({ origin: [0, 3, 0] }), offset), '/m.json',
      PROGRAM as never);
    expect(loaded).toHaveLength(1);
    expect(loaded[0].origin).toEqual([0, 3, 0]);
    // The entry's origin IS the negated leading translation: that is
    // what puts `origin` in the frame `matrixWorld` maps from (D6).
    const leading = (offset.children![0].children![0]
      .operations[0] as ['t', string[]])[1].map(Number);
    // `+ 0` only to normalise the negative zero `-0` reads back as.
    expect(loaded[0].origin).toEqual(leading.map((value) => -value + 0));
  });

  it('reads the committed `touched` fixture: six entries, key order, every '
     + 'field carried through', () => {
    const fixture = JSON.parse(readFileSync(
      new URL('../../../tests/fixtures/touched/viewer.json', import.meta.url),
      'utf8')) as Manifest & { program: { coordinates: object } };
    const loaded = readControls(fixture, 'viewer.json', fixture.program as never);

    expect(loaded.map((control) => control.name)).toEqual([
      'hundreds dial', 'tens dial', 'turn hundreds', 'turn tens',
      'turn units', 'units dial',
    ]);
    expect(loaded.map((control) => control.kind)).toEqual([
      'button', 'button', 'turn', 'turn', 'turn', 'button',
    ]);
    expect(loaded[4]).toEqual({
      name: 'turn units',
      kind: 'turn',
      part: ['units', 'input', 'dial'],
      instruction: null,
      input: 'units_entry',
      perUnit: -36.0,
      joint: ['units', 'input'],
      coordinate: 'units.input.turn',
      axis: [1, 0, 0],
      origin: [0, 0, 0],
    });
    expect(loaded[5]).toEqual({
      name: 'units dial',
      kind: 'button',
      part: ['units', 'input', 'dial'],
      instruction: 'Add one',
      input: null,
      perUnit: null,
      joint: ['units', 'input'],
      coordinate: 'units.input.turn',
      axis: [1, 0, 0],
      origin: [0, 0, 0],
    });
    // Three columns, each with one button and one turn on its dial.
    expect(new Set(loaded.map((control) => control.part.join('/')))).toEqual(
      new Set(['units/input/dial', 'tens/input/dial',
               'hundreds/input/dial']));
  });
});

// ---------------------------------------------------------------------
// The gesture's geometry (design D6, D10). A matrix is the sixteen
// COLUMN-MAJOR numbers three.js's `Matrix4.elements` holds, so these
// helpers build exactly what `operationsMatrix` would.

const RAD = Math.PI / 180;

/** Column-major, like `THREE.Matrix4.elements`. */
function columns(m: number[][]): number[] {
  // `m` is written ROW-major for legibility; transpose it here.
  return [
    m[0][0], m[1][0], m[2][0], m[3][0],
    m[0][1], m[1][1], m[2][1], m[3][1],
    m[0][2], m[1][2], m[2][2], m[3][2],
    m[0][3], m[1][3], m[2][3], m[3][3],
  ];
}

function identity(): number[][] {
  return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
}

function multiply(a: number[][], b: number[][]): number[][] {
  return a.map((row, i) => b[0].map((_, j) =>
    row.reduce((sum, value, k) => sum + value * b[k][j], 0)));
}

function translation(x: number, y: number, z: number): number[][] {
  return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]];
}

/** Right-handed about x, exactly as `makeRotationAxis([1,0,0], θ)`. */
function rotationX(degrees: number): number[][] {
  const c = Math.cos(degrees * RAD);
  const s = Math.sin(degrees * RAD);
  return [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]];
}

function rotationZ(degrees: number): number[][] {
  const c = Math.cos(degrees * RAD);
  const s = Math.sin(degrees * RAD);
  return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
}

function near(actual: Vec3, expected: Vec3, places = 9): void {
  actual.forEach((value, index) => {
    expect(value).toBeCloseTo(expected[index], places);
  });
}

describe('worldLine reads the gesture\'s line off the joint (D6)', () => {
  it('carries the origin by the full map and the axis by its rotation', () => {
    // The site carry: the column is placed, then turned about z.
    const site = multiply(translation(0, 0, 50), rotationZ(90));
    const world = worldLine(columns(site), [1, 0, 0], [0, 0, 0]);
    near(world.origin, [0, 0, 50]);
    near(world.axis, [0, 1, 0]);
  });

  it('gives the SAME line whatever angle the joint stands at -- the '
     + 'rotation-alone shape', () => {
    // `M_n · … · M_1` with the joint's own rotation FIRST, then its
    // placement: the acceptance document's own shape.
    const place = multiply(translation(0, 25, 24.8), rotationZ(30));
    const at = (turn: number) =>
      worldLine(columns(multiply(place, rotationX(turn))), [1, 0, 0],
                [0, 0, 0]);
    const rest = at(0);
    const turned = at(137.5);
    near(turned.origin, rest.origin);
    near(turned.axis, rest.axis);
    // And it really is the placed origin and the placed axis.
    near(rest.origin, [0, 25, 24.8]);
    near(rest.axis, [Math.cos(30 * RAD), Math.sin(30 * RAD), 0]);
  });

  it('gives the SAME line whatever angle the joint stands at -- the '
     + 'translate / rotate / translate-back shape', () => {
    // `Revolute(at=a)` with a = [0, 3, 0]: operations
    // [t(-a), r, t(a)] compose to t(a) · r · t(-a), a rotation about
    // the own-frame point a. The entry publishes `origin = a`.
    const a: Vec3 = [0, 3, 0];
    const place = translation(10, 0, 0);
    const at = (turn: number) => worldLine(
      columns(multiply(place, multiply(translation(0, 3, 0),
        multiply(rotationX(turn), translation(0, -3, 0))))),
      [1, 0, 0], a);
    const rest = at(0);
    const turned = at(-95);
    near(turned.origin, rest.origin);
    near(turned.axis, rest.axis);
    // The line runs through the world image of `origin`, which the
    // placement fixes -- not through the node's placed origin.
    near(rest.origin, [10, 3, 0]);
    near(rest.axis, [1, 0, 0]);
  });

  it('normalises the axis even when the declared one is not unit', () => {
    const world = worldLine(columns(identity()), [0, 0, 4], [1, 2, 3]);
    near(world.axis, [0, 0, 1]);
    near(world.origin, [1, 2, 3]);
  });
});

describe('intersectPlane and sweepAngle', () => {
  const plane = { origin: [0, 0, 0] as Vec3, axis: [0, 0, 1] as Vec3 };

  it('meets the plane where the ray crosses it', () => {
    const met = intersectPlane(
      { origin: [1, 2, 10], direction: [0, 0, -1] }, plane);
    near(met as Vec3, [1, 2, 0]);
  });

  it('answers null for a ray parallel to the plane', () => {
    expect(intersectPlane(
      { origin: [0, 0, 5], direction: [1, 0, 0] }, plane)).toBeNull();
  });

  it('measures a signed, right-handed angle in degrees about the axis',
     () => {
    const axis: Vec3 = [0, 0, 1];
    expect(sweepAngle([1, 0, 0], [0, 1, 0], axis)).toBeCloseTo(90, 9);
    expect(sweepAngle([0, 1, 0], [1, 0, 0], axis)).toBeCloseTo(-90, 9);
    expect(sweepAngle([1, 0, 0], [1, 0, 0], axis)).toBeCloseTo(0, 9);
    // Right-handed: reversing the axis reverses the sign.
    expect(sweepAngle([1, 0, 0], [0, 1, 0], [0, 0, -1])).toBeCloseTo(-90, 9);
    // A component along the axis costs nothing: both are projected.
    expect(sweepAngle([1, 0, 7], [0, 1, -3], axis)).toBeCloseTo(90, 9);
  });

  it('unwraps past half a turn by accumulating per-move deltas', () => {
    const axis: Vec3 = [0, 0, 1];
    const at = (degrees: number): Vec3 =>
      [Math.cos(degrees * RAD), Math.sin(degrees * RAD), 0];
    let sweep = 0;
    let previous = at(0);
    // Twelve steps of 40 degrees: 480 degrees, which a bare atan2
    // would fold back to 120.
    for (let step = 1; step <= 12; step += 1) {
      const current = at(step * 40);
      sweep += sweepAngle(previous, current, axis);
      previous = current;
    }
    expect(sweep).toBeCloseTo(480, 6);
  });
});

describe('chooseMode fixes the measurement at pointerdown (D10)', () => {
  const line = { origin: [0, 0, 0] as Vec3, axis: [0, 0, 1] as Vec3 };
  const camera: Vec3 = [0, 0, 10];

  it('measures in the joint\'s plane when the ray is not edge-on', () => {
    const choice = chooseMode(
      { origin: [3, 0, 10], direction: [0, 0, -1] }, line, camera);
    expect(choice.mode).toBe('plane');
    near(choice.reference as Vec3, [1, 0, 0]);
  });

  it('falls back to the screen below EDGE_ON', () => {
    expect(EDGE_ON).toBe(0.15);
    // A ray 8 degrees off the plane: sin 8° = 0.139 < 0.15.
    const shallow = Math.sin(8 * RAD);
    const along = Math.cos(8 * RAD);
    expect(chooseMode({ origin: [0, -20, 3], direction: [0, along, -shallow] },
                      line, camera).mode).toBe('screen');
    // And 10 degrees off it, sin 10° = 0.174, is in-plane.
    const steeper = Math.sin(10 * RAD);
    expect(chooseMode(
      { origin: [0, -20, 3],
        direction: [0, Math.cos(10 * RAD), -steeper] },
      line, camera).mode).toBe('plane');
  });

  it('falls back to the screen when the pointer came down ON the axis',
     () => {
    expect(MIN_RADIUS).toBeGreaterThan(0);
    const choice = chooseMode(
      { origin: [0, 0, 10], direction: [0, 0, -1] }, line, camera);
    expect(choice.mode).toBe('screen');
  });

  it('signs the screen fallback by which way the axis points', () => {
    // Axis pointing TOWARD the camera reads counter-clockwise: +1.
    const toward = chooseMode(
      { origin: [0, -20, 0], direction: [0, 1, 0] },
      { origin: [0, 0, 0], axis: [0, 0, 1] }, [0, 0, 10]);
    expect(toward.mode).toBe('screen');
    expect(toward.screenSign).toBe(1);
    // Axis pointing AWAY from it: -1.
    const away = chooseMode(
      { origin: [0, -20, 0], direction: [0, 1, 0] },
      { origin: [0, 0, 0], axis: [0, 0, -1] }, [0, 0, 10]);
    expect(away.mode).toBe('screen');
    expect(away.screenSign).toBe(-1);
    // Exactly edge-on the dot product is zero and the sign is genuinely
    // arbitrary; the documented convention is +1.
    const edge = chooseMode(
      { origin: [0, -20, 0], direction: [0, 1, 0] },
      { origin: [0, 0, 0], axis: [0, 0, 1] }, [0, 0, 0]);
    expect(edge.mode).toBe('screen');
    expect(edge.screenSign).toBe(1);
  });
});

describe('TurnPlanner commits quanta, one at a time (D11)', () => {
  /** The acceptance dial: one digit, -36 degrees of sweep per digit. */
  const dialPlanner = () => new TurnPlanner(1, -36);

  it('is one nudge amount times the published ratio', () => {
    expect(dialPlanner().quantum).toBe(36);
    expect(new TurnPlanner(5, -36).quantum).toBe(180);
    expect(new TurnPlanner(1, 0.5).quantum).toBe(0.5);
  });

  it('issues nothing until the sweep crosses one whole quantum', () => {
    const planner = dialPlanner();
    planner.advance(-35.9);
    expect(planner.next()).toBeNull();
    planner.advance(-0.1);
    expect(planner.next()).toEqual({ by: 1, step: -1 });
  });

  it('signs the request through the ratio, not through the sweep', () => {
    // -36 degrees of sweep on per_unit = -36 asks for +1 DIGIT.
    const back = dialPlanner();
    back.advance(-40);
    expect(back.next()).toEqual({ by: 1, step: -1 });
    const forward = dialPlanner();
    forward.advance(40);
    expect(forward.next()).toEqual({ by: -1, step: 1 });
    // A positive ratio keeps the sweep's own sign.
    const positive = new TurnPlanner(2, 18);
    positive.advance(40);
    expect(positive.next()).toEqual({ by: 2, step: 1 });
  });

  it('keeps at most ONE request in flight, because the run says so', () => {
    const planner = dialPlanner();
    planner.advance(-120);
    expect(planner.next()).toEqual({ by: 1, step: -1 });
    expect(planner.outstanding).toBe(true);
    // Three quanta owed, and still nothing more is asked for.
    expect(planner.next()).toBeNull();
    expect(planner.next()).toBeNull();
    planner.retire('completed');
    expect(planner.origin).toBe(-36);
    expect(planner.next()).toEqual({ by: 1, step: -1 });
  });

  it('derives what is owed from where the pointer stands, so forward and '
     + 'back nets out', () => {
    const planner = dialPlanner();
    planner.advance(-50);
    expect(planner.next()).toEqual({ by: 1, step: -1 });
    // While that one is in flight the maker drags back past the start.
    planner.advance(60);
    planner.retire('completed');
    expect(planner.origin).toBe(-36);
    // sweep is +10, origin -36: 46 degrees owed forward, one quantum.
    expect(planner.next()).toEqual({ by: -1, step: 1 });
    planner.retire('completed');
    expect(planner.origin).toBe(0);
    expect(planner.next()).toBeNull();
    // Nothing was queued for the two quanta the round trip passed
    // through: one out, one back.
    expect(planner.sweep).toBe(10);
  });

  it('leaves the origin where it is when a request does not complete', () => {
    for (const outcome of ['blocked', 'refused', 'cancelled'] as const) {
      const planner = dialPlanner();
      planner.advance(-100);
      expect(planner.next()).toEqual({ by: 1, step: -1 });
      planner.retire(outcome);
      expect(planner.origin).toBe(0);
      expect(planner.stalled).toBe(-1);
      // Held there, however long: no second request in that direction.
      expect(planner.next()).toBeNull();
      planner.advance(-500);
      expect(planner.next()).toBeNull();
      expect(planner.next()).toBeNull();
    }
  });

  it('releases the stall when the maker backs off, and at once when they '
     + 'reverse', () => {
    const planner = dialPlanner();
    planner.advance(-40);
    planner.next();
    planner.retire('blocked');
    expect(planner.next()).toBeNull();
    // Back inside one quantum: the latch lifts.
    planner.advance(20);
    expect(planner.next()).toBeNull();
    expect(planner.stalled).toBe(0);
    planner.advance(-30);
    expect(planner.next()).toEqual({ by: 1, step: -1 });

    // A reversal past a whole quantum the OTHER way is issued at once,
    // because it is not the stalled direction.
    const reversed = dialPlanner();
    reversed.advance(-40);
    reversed.next();
    reversed.retire('blocked');
    reversed.advance(80);
    expect(reversed.next()).toEqual({ by: -1, step: 1 });
  });

  it('issues nothing at all when the nudge amount is zero', () => {
    const planner = new TurnPlanner(0, -36);
    expect(planner.quantum).toBe(0);
    planner.advance(3600);
    expect(planner.next()).toBeNull();
  });

  it('ignores a retire with nothing in flight', () => {
    const planner = dialPlanner();
    planner.retire('completed');
    expect(planner.origin).toBe(0);
    expect(planner.outstanding).toBe(false);
  });
});

describe('visibleUpTo filters the pick three.js will not (D5)', () => {
  const chain = (flags: boolean[]) => {
    let parent: { visible: boolean; parent: never } | null = null;
    const nodes = flags.map((visible) => {
      const node = { visible, parent } as never as
        { visible: boolean; parent: never };
      parent = node;
      return node;
    });
    return { root: nodes[0], leaf: nodes[nodes.length - 1] };
  };

  it('keeps a hit whose mesh and every ancestor up to the scene are shown',
     () => {
    const { root, leaf } = chain([true, true, true, true]);
    expect(visibleUpTo(leaf, root)).toBe(true);
  });

  it('drops a hit on a hidden mesh', () => {
    const { root, leaf } = chain([true, true, true, false]);
    expect(visibleUpTo(leaf, root)).toBe(false);
  });

  it('drops a hit under a hidden GROUP -- what `applyVisibility` sets for '
     + 'a subtree the navigator hid', () => {
    const { root, leaf } = chain([true, false, true, true]);
    expect(visibleUpTo(leaf, root)).toBe(false);
  });

  it('stops at the scene, so a hidden scene root hides everything', () => {
    const { root, leaf } = chain([false, true, true, true]);
    expect(visibleUpTo(leaf, root)).toBe(false);
  });
});
