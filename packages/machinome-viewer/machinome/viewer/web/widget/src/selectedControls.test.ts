/* SPDX-License-Identifier: AGPL-3.0-only */
import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import * as controls from './partControls';
import type { Manifest, RawOperation } from './types';

const rotation: RawOperation[] = [
  ['t', ['0', '-2', '-3']], ['r', 'body.turn', [1, 0, 0]],
  ['t', ['0', '2', '3']],
];
const translation: RawOperation = ['t', ['0', '0', 'body.lift']];
const program = { coordinates: {
  'body.turn': { domain: 'rotational' },
  'body.lift': { domain: 'translational' },
} };
const turn = {
  kind: 'turn', part: ['body', 'knob'], joint: ['body'],
  coordinate: 'body.turn', input: 'rotation', per_unit: 360,
  axis: [1, 0, 0], origin: [0, 2, 3], operation_span: [0, 3],
};
const slide = {
  ...turn, kind: 'slide', coordinate: 'body.lift', input: 'lift',
  per_unit: 1, axis: [0, 0, 1], origin: [0, 0, 0], operation_span: [3, 4],
};
function document(table: object = { turn, slide },
                  operations: RawOperation[] = [...rotation, translation]): Manifest {
  return {
    version: 5, controls: table, drivers: { rotation: {}, lift: {} },
    instructions: { crank: {} },
    root: { name: 'root', operations: [], children: [{
      name: 'body', operations, children: [{ name: 'knob', operations: [] }],
    }] },
  } as unknown as Manifest;
}
const read = (doc = document()) => controls.readControls(doc, '/composed.json', program);

describe('the reviewed producer exports, without rewriting their documents', () => {
  it.each(['columns', 'selector', 'crank', 'tilted', 'register'])('reads %s', fixture => {
    const path = new URL(`../../../tests/fixtures/direct-motion/${fixture}/manifest.json`, import.meta.url);
    const doc = JSON.parse(readFileSync(path, 'utf8'));
    const entries = controls.readControls(doc, path.href, doc.program);
    expect(entries.map(one => one.name)).toEqual(Object.keys(doc.controls));
  });
});

describe('selected joint placements', () => {
  it('reads independent slide and turn controls on one body', () => {
    const entries = read();
    expect(entries.map(one => one.kind)).toEqual(['turn', 'slide']);
    expect(entries.map(one => one.operationSpan)).toEqual([[0, 3], [3, 4]]);
  });
  it('allows an instruction on a selected sliding joint', () => {
    expect(read(document({ press: { ...slide, kind: 'button', instruction: 'crank' } })))
      .toHaveLength(1);
  });
  it.each([[1, 2], [0, 2], [0, 4], [-1, 3], [0, 9], [0.5, 3], [3, 0]])(
    'refuses an incomplete or invalid pivot span %j', (start, end) => {
      expect(() => read(document({ turn: { ...turn, operation_span: [start, end] } })))
        .toThrow(/turn.*span|turn.*placement/);
    });
  it('refuses a slide on a rotational placement', () => {
    expect(() => read(document({ slide: { ...turn, kind: 'slide' } })))
      .toThrow(/slide.*translational|slide.*rotational/);
  });
  it('refuses duplicate slides by name', () => {
    expect(() => read(document({ slide, other: slide }))).toThrow(/other.*slide/);
  });
  it('requires a span for a slide', () => {
    expect(() => read(document({ slide: { ...slide, operation_span: undefined } })))
      .toThrow(/slide.*span/);
  });
  it('checks all displacement components, not just dependence on the coordinate', () => {
    const bad: RawOperation = ['t', ['0', '0', '(2 * body.lift)']];
    expect(() => read(document({ slide }, [...rotation, bad]))).toThrow(/slide.*placement/);
  });
  it('refuses a nonlinear expression that matches at a few sample positions', () => {
    const bad: RawOperation = ['t', ['0', '0',
      'body.lift + body.lift * (body.lift - 1) * (body.lift - 2)']];
    expect(() => read(document({ slide }, [...rotation, bad]))).toThrow(/slide.*placement/);
  });
  it('resolves shared bindings when validating a placement', () => {
    const doc = document({ slide }, [...rotation, ['t', ['0', '0', '_lift']]]);
    doc.bindings = [{ name: '_lift', expression: 'body.lift' }];
    expect(read(doc)).toHaveLength(1);
  });
  it('refuses a span naming another coordinate even with the right domain', () => {
    const doc = document({ slide }, [...rotation, ['t', ['0', '0', 'body.turn']]]);
    expect(() => read(doc)).toThrow(/slide.*placement/);
  });
});

describe('sliding along the present world rail', () => {
  const line = { origin: [0, 0, 0] as const, axis: [1, 0, 0] as const };
  it('measures signed axis displacement in world units', () => {
    const ray = { origin: [7, 0, 10] as const, direction: [0, 0, -1] as const };
    expect(controls.slidePosition(ray, line)).toBeCloseTo(7);
  });
  it('refuses end-on and nearly end-on views without inventing a scale', () => {
    expect(controls.slidePosition({ origin: [10, 0, 0], direction: [-1, 0, 0] }, line))
      .toBeNull();
    expect(controls.slidePosition({ origin: [10, 0, 0], direction: [-0.999, 0, 0.0447] }, line))
      .toBeNull();
  });
  it.each([1, -1])('uses the same one-request planner with ratio %s', ratio => {
    const planner = new controls.TurnPlanner(2, ratio);
    planner.advance(7);
    expect(planner.next()?.by).toBe(2 * ratio);
    expect(planner.next()).toBeNull();
    planner.retire('blocked');
    expect(planner.next()).toBeNull();
    planner.advance(-10);
    expect(planner.next()?.by).toBe(-2 * ratio);
  });
});
