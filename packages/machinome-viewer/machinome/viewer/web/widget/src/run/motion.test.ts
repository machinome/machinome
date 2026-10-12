/* Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later */
import { describe, expect, it } from 'vitest';
import { Motion, alongSources, copyHolding, sourceDeltas } from './motion';
import { activeShape } from './active-shape';
import { prepare, withExpressions } from '../expressions';

describe('request-local physical motion', () => {
  it('restricts the movement and dwell without drawing a new chord', () => {
    const motion = new Motion(0, 1, [[0, .25, t => 4*t], [.25, 1, () => 1]]);
    const restricted = motion.restrict(.125, .625);
    expect(restricted.start).toBe(.5);
    expect(restricted.end).toBe(1);
    expect(restricted.at(.25)).toBe(1);
    expect(restricted.at(.5)).toBe(1);
  });
  it('memoizes a pure curve within this motion only', () => {
    let calls = 0;
    const motion = new Motion(0, 1, [[0, 1, t => { calls += 1; return t*t; }]], false);
    const restricted = motion.restrict(.25, .75);
    expect(restricted.at(.5)).toBe(.25);
    const before = calls;
    expect(motion.at(.5)).toBe(.25);
    expect(restricted.at(.5)).toBe(.25);
    expect(calls).toBe(before);
    expect(Motion.line(4, 2).at(.5)).toBe(5);
  });
  it('does not call a zero-net excursion constant or lose it in a copy', () => {
    const motion = new Motion(0, 0, [[0, .5, t => 2*t], [.5, 1, t => 2-2*t]]);
    expect(motion.constant).toBe(false);
    const delta = sourceDeltas(new Map([['x', motion], ['own', Motion.line(3, 2)]]));
    const held = copyHolding(delta, 'own');
    expect(alongSources({ x: 0, own: 3 }, held, .5)).toEqual({ x: 1, own: 3 });
    expect(alongSources({ x: 0, own: 3 }, delta, .5)).toEqual({ x: 1, own: 4 });
  });
  it('classifies only the actual branch, following shared bindings', () => withExpressions(() => {
    const root = prepare('base + curve * gate');
    const bindings = new Map([['curve', prepare('x * x')], ['base', prepare('2 * y')]]);
    const closed = activeShape(root, { gate: 0 }, bindings);
    expect(closed.shape).toBe('affine');
    expect([...closed.names]).toEqual(['y']);
    expect(activeShape(root, { gate: 1 }, bindings).shape).toBe(null);
  }));
});
