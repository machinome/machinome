/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The acceptance machine, in node: the Pascaline module's own published
// build, run through the engine at the viewer's own step size. It is the
// fourteenth scenario the corpus does not contain (design §12 risk 1),
// and the number it lands on is the framework's -- the module's
// `test_the_second_carry_is_cumulative` pins CARRY_THROW at 65.54.
//
// This is what a POSE could never show: ten separate `Add one`
// instructions leave the tens drum where ten of them left it, not where
// one would have.

import { describe, expect, it } from 'vitest';
import acceptance from '../../../../tests/fixtures/pascaline/viewer.json';
import { Engine } from './engine';
import type { RunDocument } from './program';

const document = acceptance as unknown as RunDocument;
const DT = 1 / 240;

describe('the Pascaline module', () => {
  it('opens at its published rest bank, having taken no tick', () => {
    const engine = Engine.load(document, { dt: DT, record: null });
    expect(engine.tick()).toBe(0);
    expect(engine.clock()).toBe(0);
    expect(engine.state()['tens.drum.turn']).toBe(0);
    expect(engine.state()['units.drum.turn']).toBe(0);
  });

  it('accumulates the carry over ten Add one', () => {
    const engine = Engine.load(document, { dt: DT, record: null });
    for (let press = 0; press < 10; press += 1) {
      engine.trigger('Add one');
      engine.advance(240);
    }
    const state = engine.state();
    expect(engine.tick()).toBe(2400);
    expect(state.units_entry).toBe(10);
    expect(state['units.drum.turn']).toBeCloseTo(360, 9);
    // CARRY_THROW: the framework's own number for ten `Add one`.
    expect(Math.abs(state['tens.drum.turn'] - 65.54))
      .toBeLessThanOrEqual(1e-9 * Math.max(1, 65.54));
  });

  it('shows what an absolute pose could not: one Add one is not ten', () => {
    const once = Engine.load(document, { dt: DT, record: null });
    once.trigger('Add one');
    once.advance(240);
    expect(once.state()['tens.drum.turn'])
      .not.toBeCloseTo(65.54, 6);
  });
});
