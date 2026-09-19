/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// A qualified id nests at EVERY segment (design D10, ADR-046). A joint
// coordinate id is three segments or more -- `units.drum.turn` -- and
// the shipped builder splits at the first dot only, so it reaches the
// evaluator as `{units: {'drum.turn': 7}}` and resolves to nothing.

import { describe, expect, it } from 'vitest';
import { assertNestable, nest } from './scope';
import { evalExpr } from '../evaluator';
import { DriverStore } from '../drivers';

describe('nest', () => {
  it('nests a three-segment id at every segment', () => {
    expect(nest({ 'units.drum.turn': 7 }))
      .toEqual({ units: { drum: { turn: 7 } } });
  });

  it('keeps a bare id at the top level', () => {
    expect(nest({ crank: 4 })).toEqual({ crank: 4 });
  });

  it('nests a two-segment id as it always did', () => {
    expect(nest({ 'x_axis.motor': 8000 }))
      .toEqual({ x_axis: { motor: 8000 } });
  });

  it('shares an owner between two ids', () => {
    expect(nest({ 'units.drum.turn': 7, 'units.input.turn': 2, tens_entry: 1 }))
      .toEqual({
        units: { drum: { turn: 7 }, input: { turn: 2 } },
        tens_entry: 1,
      });
  });

  it('nests a five-segment id', () => {
    expect(nest({ 'a.b.c.d.e': 1 }))
      .toEqual({ a: { b: { c: { d: { e: 1 } } } } });
  });

  it('makes a three-segment id evaluate to its value', () => {
    expect(evalExpr('(-1 * units.drum.turn)',
                    { time: 0, drivers: nest({ 'units.drum.turn': 7 }) }))
      .toBe(-7);
  });

  it('is what the shipped driver scope could not do', () => {
    // The measurement design D10 quotes, kept as a case of its own: a
    // scope built by splitting at the FIRST dot leaves `drum.turn` as
    // one key of `units`, and the member chain finds nothing there.
    const shipped: Record<string, unknown> = { units: { 'drum.turn': 7 } };
    expect(evalExpr('(-1 * units.drum.turn)',
                    { time: 0, drivers: shipped as never })).toBeNaN();
  });
});

describe('DriverStore.scope', () => {
  it('nests a three-segment driver id', () => {
    const store = new DriverStore({
      'units.drum.turn': {
        default: 7, range: null, unit: null, dtype: null, scale: null,
      },
    });
    expect(evalExpr('(-1 * units.drum.turn)',
                    { time: 0, drivers: store.scope() })).toBe(-7);
  });
});

describe('assertNestable', () => {
  it('accepts ids that nest', () => {
    expect(() => assertNestable(['units.drum.turn', 'units.input.turn', 'a']))
      .not.toThrow();
  });

  it('refuses an id that is a strict prefix of another, naming both', () => {
    let message = '';
    try {
      assertNestable(['a.b', 'a.b.c']);
    } catch (error) {
      message = String(error);
    }
    expect(message).toContain('a.b');
    expect(message).toContain('a.b.c');
  });

  it('does not confuse a shared prefix segment with a prefix id', () => {
    expect(() => assertNestable(['a.bc', 'a.b.c'])).not.toThrow();
  });
});
