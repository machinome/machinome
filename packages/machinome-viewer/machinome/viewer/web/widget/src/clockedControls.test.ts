/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The CLOCKED chrome, decided as pure data (OpenSpec
// `execute-the-commit`, design §13).

import { describe, expect, it } from 'vitest';
import {
  clockedControlLayer, clockedInputControl, clockStepAmount,
  DEFAULT_CLOCK_STEP, DEFAULT_NUDGE, formatClockedOutcome,
} from './clockedControls';
import type { ClockedMachineView, ClockedOutcome } from './clockedControls';

const FREE = { default: 0, range: null, unit: null, dtype: null, scale: null };

const MACHINE: ClockedMachineView = {
  drivers: {
    crank: { ...FREE, unit: 'deg' },
    setting: { ...FREE, unit: 'digit' },
    operand: { ...FREE, default: 1, range: [0, 9], dtype: 'int' },
  },
  states: {
    'w0.digit': { ...FREE, range: [0, 9], dtype: 'int' },
    'w1.digit': { ...FREE, range: [0, 9], dtype: 'int' },
  },
  instructions: { 'Turn crank': { targets: { crank: 360 }, duration: 1 } },
  clock: null,
};

describe('the clocked chrome', () => {
  it('is absent for a document carrying no machine', () => {
    const layer = clockedControlLayer({ machine: null, values: {},
                                        focus: null });
    expect(layer.present).toBe(false);
    expect(layer.inputs).toEqual([]);
    expect(layer.readouts).toEqual([]);
  });

  it('makes a DRIVER a handle: a readout, a nudge and a slider where a '
     + 'range is declared', () => {
    const layer = clockedControlLayer({
      machine: MACHINE, values: { crank: 720, operand: 4 }, focus: null,
    });
    expect(layer.present).toBe(true);
    expect(layer.inputs.map((one) => one.id))
      .toEqual(['crank', 'setting', 'operand']);
    const crank = layer.inputs[0];
    expect(crank.display).toBe(720);
    expect(crank.readout).toBe('720.0000');
    expect(crank.unit).toBe('deg');
    expect(crank.nudge).toBe(DEFAULT_NUDGE);
    // No declared range: a number field, no slider.
    expect(crank.slider).toBe(null);
    expect(crank.numeric).toBe(true);
    const operand = layer.inputs[2];
    expect(operand.slider).toEqual({ min: 0, max: 9, step: 1, position: 4 });
  });

  it('makes a STATE a follow-only readout, and never a handle', () => {
    const layer = clockedControlLayer({
      machine: MACHINE, values: { 'w0.digit': 3 }, focus: ['w0'],
    });
    // Under the focused layer the state is a readout; no input of the
    // layer is a state, at any focus.
    expect(layer.readouts.map((one) => one.id)).toEqual(['w0.digit']);
    expect(layer.readouts[0].kind).toBe('state');
    expect(layer.readouts[0].display).toBe(3);
    for (const focus of [null, ['w0'], ['w1']] as (string[] | null)[]) {
      const found = clockedControlLayer({
        machine: MACHINE, values: {}, focus,
      });
      expect(found.inputs.map((one) => one.id))
        .not.toContain('w0.digit');
    }
  });

  it('reads an INTEGER state as the whole number it is', () => {
    // A state the machine commits as an integer has no fraction to
    // report: `5.0000` claims a precision the coordinate has not got.
    // The CLOCK, which declares no dtype, keeps the fixed decimals a
    // continuous quantity wants.
    // The `Regulator`'s own shape: an int state beside a clock.
    const layer = clockedControlLayer({
      machine: { ...MACHINE, states: { count: { ...FREE, dtype: 'int' } },
                 clock: 'time' },
      values: { count: 5, time: 5.25 }, focus: null,
    });
    const count = layer.readouts.find((one) => one.id === 'count');
    expect(count?.readout).toBe('5');
    const clock = layer.readouts.find((one) => one.kind === 'clock');
    expect(clock?.readout).toBe('5.2500');
  });

  it('makes a CLOCK a readout too, never a handle', () => {
    const layer = clockedControlLayer({
      machine: { ...MACHINE, clock: 'time' }, values: { time: 0 },
      focus: null,
    });
    const clock = layer.readouts.find((one) => one.kind === 'clock');
    expect(clock?.id).toBe('time');
    expect(clock?.unit).toBe('s');
    expect(layer.inputs.map((one) => one.id)).not.toContain('time');
  });

  it('LISTS declared instructions, DISABLED, with the reason', () => {
    const layer = clockedControlLayer({
      machine: MACHINE, values: {}, focus: null,
    });
    expect(layer.instructions).toHaveLength(1);
    expect(layer.instructions[0].name).toBe('Turn crank');
    expect(layer.instructions[0].disabled).toBe(true);
    expect(layer.instructions[0].reason).toContain('no runtime meaning');
  });

  it('has NO transport over its DRIVERS, and none at all for a machine '
     + 'that declares no clock', () => {
    const layer = clockedControlLayer({
      machine: MACHINE, values: {}, focus: null,
    });
    expect(Object.keys(layer).sort()).toEqual(
      ['breadcrumb', 'children', 'inputs', 'instructions', 'present',
       'readouts', 'transport']);
    // A clocked machine has no cadence for a transport over its drivers
    // to run, step or speed, and a machine with no CLOCK has nothing for
    // one to advance either.
    expect(layer.transport).toBe(null);
  });

  it('is absent for a document carrying no machine at all', () => {
    const layer = clockedControlLayer({ machine: null, values: {},
                                        focus: null });
    expect(layer.transport).toBe(null);
  });

  it('offers a TRANSPORT exactly where the machine declares a clock',
     () => {
    const layer = clockedControlLayer({
      machine: { ...MACHINE, clock: 'time' },
      values: { time: 12.5 },
      focus: null,
      clockPlaying: true,
      speed: 60,
    });
    const transport = layer.transport;
    expect(transport).not.toBe(null);
    expect(transport?.id).toBe('time');
    expect(transport?.playing).toBe(true);
    expect(transport?.seconds).toBe(12.5);
    // Elapsed SECONDS, in the form a run's own elapsed readout takes:
    // they never wrap, and they only grow.
    expect(transport?.elapsed).toBe('0:12.50');
    expect(transport?.speed).toBe(60);
    expect(transport?.ladder).toContain(3600);
    expect(transport?.step).toBe(DEFAULT_CLOCK_STEP);
    expect(transport?.refusal).toBe(null);
  });

  it('carries the refusal that PAUSED it, rather than repeating the '
     + 'request', () => {
    const layer = clockedControlLayer({
      machine: { ...MACHINE, clock: 'time' },
      values: { time: 3 },
      focus: null,
      clockPlaying: false,
      clockRefusal: 'would cross 3600 surfaces',
    });
    expect(layer.transport?.playing).toBe(false);
    expect(layer.transport?.refusal).toBe('would cross 3600 surfaces');
  });

  it('takes a step AMOUNT and never a negative one: the clock has no '
     + 'reverse', () => {
    expect(clockStepAmount(2.5, DEFAULT_CLOCK_STEP)).toBe(2.5);
    // A setting refused, which is not the same as repairing a request:
    // the amount stays where it was.
    expect(clockStepAmount(-2, 5)).toBe(5);
    expect(clockStepAmount(0, 5)).toBe(5);
    expect(clockStepAmount(Number.NaN, 5)).toBe(5);
    const layer = clockedControlLayer({
      machine: { ...MACHINE, clock: 'time' }, values: {}, focus: null,
      clockStep: 2,
    });
    expect(layer.transport?.step).toBe(2);
  });

  it('keeps `range` presentation and never a clamp', () => {
    const control = clockedInputControl(
      'operand', MACHINE.drivers.operand, 12);
    expect(control.display).toBe(12);
    expect(control.readout).toBe('12.0000');
    expect(control.pinned).toBe(true);
    expect(control.slider?.position).toBe(9);
  });

  it('reports the STOPS that truncated a request, at the control that '
     + 'made it', () => {
    const held: ClockedOutcome = {
      status: 'completed',
      admitted: 0,
      unit: 'digit',
      message: null,
      stops: [{
        coordinate: 'knob.travel', side: 'low', bound: 0, value: 0,
        input: 0, fraction: 0,
      }],
    };
    expect(formatClockedOutcome(held))
      .toBe('held by knob.travel (low 0)');
    const partial: ClockedOutcome = { ...held, admitted: -2 };
    expect(formatClockedOutcome(partial))
      .toBe('moved -2 digit, held by knob.travel (low 0)');
    const whole: ClockedOutcome = {
      status: 'completed', admitted: 3, unit: 'digit', message: null,
      stops: [],
    };
    expect(formatClockedOutcome(whole)).toBe('moved 3 digit');
    const refused: ClockedOutcome = {
      status: 'refused', admitted: null, unit: null,
      message: 'the clock cannot advance', stops: [],
    };
    expect(formatClockedOutcome(refused))
      .toBe('refused: the clock cannot advance');
    expect(formatClockedOutcome(null)).toBe('');
  });

  it('scopes its controls to the focused layer, by SEGMENT and never by '
     + 'string prefix', () => {
    const machine: ClockedMachineView = {
      drivers: { 'x_axis.motor': FREE, 'x_axis_two.motor': FREE },
      states: {}, instructions: {}, clock: null,
    };
    const layer = clockedControlLayer({
      machine, values: {}, focus: ['x_axis'],
    });
    expect(layer.inputs.map((one) => one.id)).toEqual(['x_axis.motor']);
  });
});
