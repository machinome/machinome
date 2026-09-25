/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { evaluateExpression, loadProgram } from './program';
import { inspectProfileExpression, prepare } from '../expressions';
import { loadProfiles, profileOverlap } from './profiles';
import { Run } from './run';
import producerV13 from './profile-overlap-v13.json';
import producerOutcome from './profile-overlap-v13-outcome.json';
import numericCorpus from './profile-overlap-numeric-corpus.json';
import type { RunDocument } from './program';

const SOURCE = 'http://example.test/profile.json';
const LIMITS = {
  crossing_tolerance: 1e-12, subdivisions: 64, bisection_rounds: 64,
  max_crossings: 1000, agreement: 1e-9,
};

function profileDocument(profiles: unknown): RunDocument {
  return {
    format: 'machinome-export', version: 13,
    drivers: { crank: { default: 0, range: null, unit: null, dtype: null, scale: null } },
    instructions: {},
    program: {
      identity: 'profile-test', clock: 'time',
      coordinates: {
        crank: { kind: 'input', initial: 0, domain: null },
        'slide.x': { kind: 'coordinate', initial: 0, domain: 'translational' },
      },
      intermediates: [],
      edges: [{ kind: 'law', needs: ['crank'], gives: ['slide.x'],
        description: 'crank drives slide', stated_by: 'Bench',
        expressions: ['crank'], affine: [true], plans: [null] }],
      spans: { 'slide.x': { high: { expression:
        '10 - profileOverlap(0, 0, crank, 0, 0, 0, 0, 0)' } } },
      sources: { crank: ['crank'], 'slide.x': ['crank'] },
      limits: LIMITS, profiles,
    },
  } as RunDocument;
}

const TRIANGLE = { points: [[0, 0], [1, 0], [0, 1]], polygons: [[0, 1, 2]] };

function bits(value: number): string {
  const view = new DataView(new ArrayBuffer(8));
  view.setFloat64(0, value, false);
  return view.getBigUint64(0, false).toString(16).padStart(16, '0');
}

describe('version-13 finite convex profile contact', () => {
  it('inspects a 10,000-alias chain without exhausting the JS stack', () => {
    for (const tail of ['crank', 'profileOverlap(0, 0, 0, 0, 0, 0, 0, 0)']) {
      const roots = new Map<string, number>();
      roots.set('_b0', prepare(tail));
      for (let i = 1; i <= 10_000; i++) {
        roots.set(`_b${i}`, prepare(`_b${i - 1}`));
      }
      expect(inspectProfileExpression(prepare('_b10000'), roots, 1))
        .toBe(tail !== 'crank');
      const document = profileDocument([TRIANGLE]);
      document.bindings = [{ name: '_b0', expression: tail }];
      for (let i = 1; i <= 10_000; i++) {
        document.bindings.push({ name: `_b${i}`, expression: `_b${i - 1}` });
      }
      (((document.program as Record<string, unknown>).spans as Record<string, unknown>)['slide.x'] as Record<string, unknown>).high =
        { expression: '10 - _b10000' };
      loadProgram(document, SOURCE);
    }
  });

  it('refuses a self-crossing pentagram before a run starts', () => {
    // A star can have locally positive turns yet cross its own edges.
    const profile = { points: [
      [0, 3], [1.7633557568774194, -2.4270509831248424],
      [-2.8531695488854605, 0.9270509831248424],
      [2.8531695488854605, 0.9270509831248424],
      [-1.7633557568774194, -2.4270509831248424],
    ], polygons: [[0, 1, 2, 3, 4]] };
    expect(() => loadProgram(profileDocument([profile]), SOURCE))
      .toThrow(/profile.*(cross|simple|convex)/i);
  });

  it('refuses a repeated vertex and zero edge before a run starts', () => {
    const profile = { points: TRIANGLE.points,
      polygons: [[0, 1, 1, 2]] };
    expect(() => loadProgram(profileDocument([profile]), SOURCE))
      .toThrow(/profile.*(repeat|edge|vertex)/i);
  });

  it('evaluates a direct profile call in its document table context', () => {
    const program = loadProgram(profileDocument([TRIANGLE]), SOURCE);
    expect(evaluateExpression(program,
      'profileOverlap(0, 0, 0, 0, 0, 0, 0, 0)', { crank: 0, 'slide.x': 0 }))
      .toBe(1);
    expect(evaluateExpression(program,
      'profileOverlap(0, 0, 0, 0, 0, 0, 3, 0)', { crank: 0, 'slide.x': 0 }))
      .toBe(0);
  });

  it('refuses nonliteral and out-of-range profile indices at load', () => {
    const dynamic = profileDocument([TRIANGLE]);
    (((dynamic.program as Record<string, unknown>).spans as Record<string, unknown>)['slide.x'] as Record<string, unknown>).high =
      { expression: '10 - profileOverlap(crank, 0, 0, 0, 0, 0, 0, 0)' };
    expect(() => loadProgram(dynamic, SOURCE)).toThrow(/literal nonnegative integers/i);
    const outside = profileDocument([TRIANGLE]);
    (((outside.program as Record<string, unknown>).spans as Record<string, unknown>)['slide.x'] as Record<string, unknown>).high =
      { expression: '10 - profileOverlap(1, 0, 0, 0, 0, 0, 0, 0)' };
    expect(() => loadProgram(outside, SOURCE)).toThrow(/outside the table/i);
  });

  it('refuses a profile call in a law rather than a numeric Bound', () => {
    const doc = profileDocument([TRIANGLE]);
    (((doc.program as Record<string, unknown>).edges as Record<string, unknown>[])[0]).expressions =
      ['profileOverlap(0, 0, 0, 0, 0, 0, 0, 0)'];
    expect(() => loadProgram(doc, SOURCE)).toThrow(/outside a numeric Bound/i);
  });

  it('counts touching as contact and a strict gap as clear', () => {
    const table = loadProfiles([TRIANGLE]);
    expect(profileOverlap(table, 0, 0, 0, 0, 0, 0, 1, 0)).toBe(1);
    expect(profileOverlap(table, 0, 0, 0, 0, 0, 0, 1.0001, 0)).toBe(0);
  });

  it('refuses a world-space collapsed edge before disjoint AABB exit', () => {
    const table = loadProfiles([TRIANGLE]);
    expect(() => profileOverlap(table, 0, 0, 0, 1e16, 0, 0, 1e18, 0))
      .toThrow(/transformed edge collapsed/i);
  });

  it('reports the producer first error when several placement inputs are invalid', () => {
    const table = loadProfiles([TRIANGLE]);
    expect(() => profileOverlap(table, 0, 0,
      Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY,
      0, 0, 0)).toThrow(/x translation.*nonfinite/i);
    expect(() => profileOverlap(table, 0, 0,
      0, 0, 0,
      Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY))
      .toThrow(/x translation.*nonfinite/i);
  });

  it('does not transform an unreferenced table point', () => {
    const table = loadProfiles([{ points: [
      [0, 0], [1, 0], [0, 1], [1.7e308, 1.7e308],
    ], polygons: [[0, 1, 2]] }]);
    expect(profileOverlap(table, 0, 0, 45, 0, 0, 45, 0, 0)).toBe(1);
  });

  it('reports first-polygon axis collapse before a later polygon overflows', () => {
    const table = loadProfiles([{ points: [
      [0, 0], [1, 0], [0, 1],
      [1.7e308, 0], [0, 1.7e308], [-1.7e308, 0],
    ], polygons: [[0, 1, 2], [3, 4, 5]] }]);
    expect(() => profileOverlap(table, 0, 0, 45, 1e16, 1e16, 45, 0, 0))
      .toThrow(/transformed edge collapsed/i);
  });

  it('matches the producer pointwise numeric and malformed-polygon corpus', () => {
    const polygon = numericCorpus.profile[0];
    const table = loadProfiles([{ points: polygon,
      polygons: [polygon.map((_point, index) => index)] }]);
    for (const row of numericCorpus.cases) {
      const call = () => profileOverlap(table, 0, 0, row.left_angle,
        row.left_xy[0], row.left_xy[1], row.right_angle,
        row.right_xy[0], row.right_xy[1]);
      if ('error' in row) expect(call, row.name).toThrow(/collapsed/i);
      else expect(call(), row.name).toBe(row.result);
    }
    for (const row of numericCorpus.invalid_polygons) {
      expect(() => loadProfiles([{ points: row.points,
        polygons: [row.points.map((_point, index) => index)] }]), row.name)
        .toThrow(/profile/i);
    }
    expect(loadProfiles([{ points: numericCorpus.valid_collinear,
      polygons: [numericCorpus.valid_collinear.map((_point, index) => index)] }]))
      .toHaveLength(1);
  });

  it('never reuses a shared expression result across two profile tables', () => {
    const shifted = { points: [[10, 0], [11, 0], [10, 1]], polygons: [[0, 1, 2]] };
    const a = loadProgram(profileDocument([TRIANGLE, TRIANGLE]), SOURCE);
    const b = loadProgram(profileDocument([TRIANGLE, shifted]), SOURCE);
    const expression = 'profileOverlap(0, 1, 0, 0, 0, 0, 0, 0)';
    const bank = { crank: 0, 'slide.x': 0 };
    expect(evaluateExpression(a, expression, bank)).toBe(1);
    expect(evaluateExpression(b, expression, bank)).toBe(0);
    expect(evaluateExpression(a, expression, bank)).toBe(1);
  });

  it('keeps two mounted Runs with the same expression and bank isolated', () => {
    const shifted = { points: [[10, 0], [11, 0], [10, 1]], polygons: [[0, 1, 2]] };
    const create = (second: typeof TRIANGLE) => {
      const doc = profileDocument([TRIANGLE, second]);
      (((doc.program as Record<string, unknown>).spans as Record<string, unknown>)['slide.x'] as Record<string, unknown>).high =
        { expression: '10 - profileOverlap(0, 1, 0, 0, 0, 0, 0, 0)' };
      return new Run(loadProgram(doc, SOURCE), 1, 8);
    };
    const a = create(TRIANGLE);
    const b = create(shifted);
    const initialA = a.snapshot();
    const initialB = b.snapshot();
    a.move('crank', { to: 11, duration: 1 });
    b.move('crank', { to: 11, duration: 1 });
    a.advance();
    b.advance();
    expect(a.state().crank).toBeCloseTo(9, 8);
    expect(b.state().crank).toBeCloseTo(10, 8);
    const reachedA = a.state();
    const reachedB = b.state();
    a.restore(initialA);
    b.restore(initialB);
    b.move('crank', { to: 11, duration: 1 });
    a.move('crank', { to: 11, duration: 1 });
    b.advance();
    a.advance();
    expect(a.state()).toEqual(reachedA);
    expect(b.state()).toEqual(reachedB);
  });

  it('uses the contact flag only inside an ordinary numeric Bound stop', () => {
    const run = new Run(loadProgram(profileDocument([TRIANGLE]), SOURCE), 1, null);
    run.move('crank', { to: 11, duration: 1 });
    run.advance();
    expect(run.state()['slide.x']).toBeCloseTo(9, 8);
    expect(run.state().crank).toBeCloseTo(9, 8);
  });

  it('executes the same contact through a document binding in a Bound', () => {
    const doc = profileDocument([TRIANGLE]);
    doc.bindings = [{ name: '_b1',
      expression: 'profileOverlap(0, 0, 0, 0, 0, 0, 0, 0)' }];
    (((doc.program as Record<string, unknown>).spans as Record<string, unknown>)['slide.x'] as Record<string, unknown>).high =
      { expression: '10 - _b1' };
    const run = new Run(loadProgram(doc, SOURCE), 1, null);
    run.move('crank', { to: 11, duration: 1 });
    run.advance();
    expect(run.state()['slide.x']).toBeCloseTo(9, 8);
  });

  it('loads a version-13 program carrying both Follow and profile contact', () => {
    const doc = profileDocument([TRIANGLE]);
    const raw = doc.program as Record<string, unknown>;
    Object.assign(doc.drivers, {
      low: { default: 0, range: null, unit: null, dtype: null, scale: null },
      high: { default: 3, range: null, unit: null, dtype: null, scale: null },
    });
    Object.assign(raw.coordinates as Record<string, unknown>, {
      low: { kind: 'input', initial: 0, domain: null },
      high: { kind: 'input', initial: 3, domain: null },
      ball: { kind: 'coordinate', initial: 0, domain: 'translational' },
    });
    (raw.edges as Record<string, unknown>[]).push({
      kind: 'follow', needs: ['low', 'high', 'ball'], gives: ['ball'],
      lower: 'low', upper: 'high', lower_plan: null, upper_plan: null,
      description: 'two surfaces retain ball', stated_by: 'Bench',
    });
    Object.assign(raw.spans as Record<string, unknown>, {
      ball: { low: { expression: 'low' }, high: { expression: 'high' } },
    });
    Object.assign(raw.sources as Record<string, unknown>, {
      low: ['low'], high: ['high'], ball: ['low', 'high'],
    });
    const run = new Run(loadProgram(doc, SOURCE), 1, 8);
    run.move('low', { to: 2, duration: 1 });
    run.move('crank', { to: 1, duration: 1 });
    run.advance();
    expect(run.state().ball).toBe(2);
    expect(run.state()['slide.x']).toBe(1);
  });

  it('executes the exact producer-serialized v13 Bound and replays the stop', () => {
    const program = loadProgram(producerV13 as RunDocument, 'producer://profile_overlap_v13.json');
    expect(program.profiles).toHaveLength(1);
    const run = new Run(program, producerOutcome.request.dt, 8);
    const initial = run.snapshot();
    const request = run.move(producerOutcome.request.input,
      { by: producerOutcome.request.by, duration: producerOutcome.request.duration });
    run.advance();
    expect(request.status).toBe(producerOutcome.expected.status);
    expect(bits(request.admitted)).toBe(producerOutcome.expected.admitted_bits);
    for (const [id, expected] of Object.entries(producerOutcome.expected.bank_bits)) {
      expect(bits(run.state()[id])).toBe(expected);
    }
    const [stop] = run.stops();
    expect(stop.tick).toBe(producerOutcome.expected.stop.tick);
    expect(stop.coordinate).toBe(producerOutcome.expected.stop.coordinate);
    expect(stop.bound).toBe(producerOutcome.expected.stop.bound);
    expect(bits(stop.value)).toBe(producerOutcome.expected.stop.value_bits);
    expect(bits(stop.t)).toBe(producerOutcome.expected.stop.t_bits);
    expect(stop.inputs).toEqual(producerOutcome.expected.stop.inputs);
    expect(stop.time_drives ?? []).toEqual(producerOutcome.expected.stop.time_drives);
    const reached = run.state();
    run.restore(initial);
    run.move(producerOutcome.request.input,
      { by: producerOutcome.request.by, duration: producerOutcome.request.duration });
    run.advance();
    expect(run.state()).toEqual(reached);
  });
});

const actualCurtaDocument = process.env.CURTA_PROFILE_V13_DOCUMENT;
it.skipIf(!actualCurtaDocument)(
  'loads the pinned actual-cover v13 Bound and replays its numeric stop', () => {
    const body = JSON.parse(readFileSync(actualCurtaDocument!, 'utf8')) as RunDocument;
    const program = loadProgram(body, 'producer://curta-profile-actual-v13.json');
    expect(body.version).toBe(13);
    expect(program.identity).toBe(
      'e3da06055f59da9eeb6b58ea38883d11e0fe456e42693c2e003f234135cd253f');
    expect(program.profiles).toHaveLength(2);
    const run = new Run(program, 0.1, 8);
    const initial = run.snapshot();
    const request = run.move('height', { to: 5, duration: 0.1 });
    run.advance();
    expect(request.status).toBe('blocked');
    expect(request.admitted).toBe(0.5);
    expect(run.state().height).toBe(0.5);
    expect(run.state()['wheel.turn']).toBe(0.5);
    const reached = run.state();
    run.restore(initial);
    run.move('height', { to: 5, duration: 0.1 });
    run.advance();
    expect(run.state()).toEqual(reached);
  },
);
