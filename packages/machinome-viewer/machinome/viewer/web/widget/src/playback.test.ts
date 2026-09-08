/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Real-time playback from a declared loop (OpenSpec change
// `real-time-playback`). Everything that decides how fast the timeline
// runs and what the readout says is pure, so it is tested here in node;
// `viewer.ts` renders exactly what these return.

import { describe, expect, it } from 'vitest';
import {
  SPEED_LADDER, advance, assertSpeed, cycleSecondsFor, formatMachineTime,
  ladderFor, timelinePosition, timelineStep, timelineTime,
} from './playback';

describe('timelineStep', () => {
  it('counts both endpoints among the declared frames', () => {
    expect(timelineStep(360)).toBe(1 / 359);
    expect(Math.round(1 / timelineStep(360)) + 1).toBe(360);
  });

  it('guards a single-frame timeline', () => {
    expect(timelineStep(1)).toBe(1);
  });

  it('maps exact integer frame indices onto normalized time', () => {
    expect(timelinePosition(0, 360)).toBe(0);
    expect(timelinePosition(1, 360)).toBe(359);
    expect(timelineTime(359, 360)).toBe(1);
    expect(timelinePosition(1, 1)).toBe(0);
    expect(timelineTime(0, 1)).toBe(0);
  });
});

describe('cycleSecondsFor', () => {
  it('plays frames / fps when the document declares no loop', () => {
    expect(cycleSecondsFor({ fps: 30, frames: 360 }, 1)).toBe(12);
    // Speed is meaningless without a loop: the old behaviour, exactly.
    expect(cycleSecondsFor({ fps: 30, frames: 360 }, 720)).toBe(12);
  });

  it('plays the declared loop at real time by default', () => {
    expect(cycleSecondsFor({ fps: 30, frames: 360, loop: 43200 }, 1))
      .toBe(43200);
  });

  it('divides the loop by the speed', () => {
    expect(cycleSecondsFor({ fps: 30, frames: 360, loop: 43200 }, 720))
      .toBe(60);
    expect(cycleSecondsFor({ fps: 30, frames: 360, loop: 1.5 }, 0.1))
      .toBe(15);
  });
});

describe('advance', () => {
  it('moves the 0..1 time by the elapsed share of a cycle and wraps', () => {
    expect(advance(0, 6, 12)).toBe(0.5);
    expect(advance(0.75, 6, 12)).toBeCloseTo(0.25);
  });
});

describe('ladderFor', () => {
  it('offers the fixed ladder from slow motion to thousands of times', () => {
    expect(SPEED_LADDER).toEqual([0.1, 0.25, 0.5, 1, 2, 5, 10, 60, 360, 3600]);
    expect(ladderFor(1)).toEqual(SPEED_LADDER);
  });

  it('inserts a host-set speed the ladder lacks, in order', () => {
    expect(ladderFor(720)).toEqual(
      [0.1, 0.25, 0.5, 1, 2, 5, 10, 60, 360, 720, 3600]);
    expect(ladderFor(0.05)[0]).toBe(0.05);
  });
});

describe('formatMachineTime', () => {
  it('reads h:mm:ss for a loop of an hour or more', () => {
    expect(formatMachineTime(0, 43200)).toBe('0:00:00');
    expect(formatMachineTime(21600, 43200)).toBe('6:00:00');
    expect(formatMachineTime(3661.9, 43200)).toBe('1:01:01');
  });

  it('reads m:ss.s for a loop of a minute or more', () => {
    expect(formatMachineTime(90, 120)).toBe('1:30.0');
    expect(formatMachineTime(5.25, 60)).toBe('0:05.3');
  });

  it('reads seconds with two decimals for a short loop', () => {
    expect(formatMachineTime(0.75, 1.5)).toBe('0.75 s');
    expect(formatMachineTime(0, 1.5)).toBe('0.00 s');
  });
});

describe('assertSpeed', () => {
  it('accepts a positive finite multiplier', () => {
    expect(assertSpeed(1)).toBe(1);
    expect(assertSpeed(0.1)).toBe(0.1);
    expect(assertSpeed(3600)).toBe(3600);
  });

  it('refuses anything else, naming the value', () => {
    for (const bad of [0, -5, NaN, Infinity, -Infinity]) {
      expect(() => assertSpeed(bad)).toThrow(String(bad));
    }
  });
});
