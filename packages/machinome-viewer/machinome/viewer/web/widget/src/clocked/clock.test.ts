/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The PER-FRAME ADVANCE, decided in node (OpenSpec `run-the-clock`,
// design §5, task 4). Pure arithmetic and one cap; everything that
// touches a frame, a machine or the DOM is `viewer.ts`'s.

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { bindingTable } from '../bindings';
import type { Manifest } from '../types';
import { clockAdvance, CLOCK_FRAME_BUDGET, clockCap } from './clock';
import { loadClocked } from './document';
import type { ClockedDocument } from './document';
import { clockedMachine } from './machine';
import type { ClockedMachine } from './machine';

const fixture = JSON.parse(readFileSync(
  new URL('../clocked-corpus.json', import.meta.url), 'utf8')) as {
    machines: { name: string; document: Record<string, unknown> }[];
  };

function corpusMachine(name: string): ClockedMachine {
  const found = fixture.machines.find((one) => one.name === name);
  if (found === undefined) throw new Error(`no corpus machine ${name}`);
  const document = JSON.parse(JSON.stringify(found.document));
  const url = `clocked-corpus.json#${name}`;
  return clockedMachine(loadClocked(document as ClockedDocument, url,
                                    bindingTable(document as Manifest, url)));
}

describe('the seconds one frame advances the clock by', () => {
  it('is the wall seconds times the speed, at real time', () => {
    expect(clockAdvance(1 / 60, 1)).toBe(1 / 60);
    expect(clockAdvance(0.008, 1)).toBe(0.008);
    // A fractional remainder is NOT carried (design §5): `by` may be any
    // float, so the frame's own elapsed seconds are requested as they
    // are, and ten frames equal one frame of ten times the travel.
    let total = 0;
    for (let at = 0; at < 10; at += 1) total += clockAdvance(0.001, 1);
    expect(total).toBeCloseTo(clockAdvance(0.01, 1), 12);
  });

  it('is the wall seconds times the speed at x3600 too', () => {
    // The ladder's top rung exists for exactly this: a 16 ms frame
    // carrying a minute of machine time.
    expect(clockAdvance(1 / 60, 3600)).toBe(60);
    expect(clockAdvance(0.001, 60)).toBe(0.06);
  });

  it('asks for NOTHING on a zero-length frame', () => {
    expect(clockAdvance(0, 1)).toBe(0);
    expect(clockAdvance(0, 3600)).toBe(0);
    // ... and never for a negative advance, whatever a clock that went
    // backwards between two timestamps reports.
    expect(clockAdvance(-0.5, 1)).toBe(0);
  });

  it('CAPS a stall at four frames\' worth of the current speed', () => {
    // The run's own cap (`src/run/runtime.ts:286-295`, ADR-046 design
    // D9), in seconds rather than ticks: wall time beyond it is LOST,
    // visibly, because the seconds readout falls behind the clock on the
    // wall. Losing it is honest where firing a burst is not.
    expect(clockCap(1)).toBe(4 * 1 * CLOCK_FRAME_BUDGET);
    expect(clockAdvance(10, 1)).toBe(clockCap(1));
    expect(clockAdvance(10, 3600)).toBe(clockCap(3600));
    expect(clockCap(3600)).toBe(240);
    // A frame INSIDE the cap is untouched.
    expect(clockAdvance(1 / 60, 3600)).toBe(60);
  });
});

describe('what the cap is FOR', () => {
  it('keeps a stalled frame inside the machine\'s own max_crossings', () => {
    // The consequence, not the arithmetic (task 4.2). `Regulator`
    // releases once a second and admits 1000 crossings of one relation
    // on one request. A 10 s stall at x3600 would be 36 000 seconds of
    // machine time -- 36 000 events -- and the machine would refuse the
    // whole frame. Capped, it is 240 seconds and 240 events, which the
    // machine executes.
    const machine = corpusMachine('Regulator');
    const capped = clockAdvance(10, 3600);
    expect(capped).toBe(240);
    const request = machine.move('time', { by: capped });
    expect(request.commits).toHaveLength(240);
    expect(machine.state().time).toBe(240);
    expect(machine.state().count).toBe(240);

    // And the uncapped travel the same stall would have asked for is
    // exactly what the machine refuses.
    const uncapped = corpusMachine('Regulator');
    let caught: { kind?: string } = {};
    try {
      uncapped.move('time', { by: 10 * 3600 });
    } catch (error) {
      caught = error as { kind?: string };
    }
    expect(caught.kind).toBe('TooManyEvents');
    expect(uncapped.state().time).toBe(0);
  });
});
