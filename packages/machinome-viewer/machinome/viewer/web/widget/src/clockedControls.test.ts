/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The CLOCKED chrome, decided as pure data (OpenSpec
// `execute-the-commit`, design §13).

import { describe, expect, it } from 'vitest';
import {
  clockedControlLayer, clockedFollowing, clockedInputControl,
  clockStepAmount, DEFAULT_CLOCK_STEP, DEFAULT_NUDGE, formatClockedOutcome,
  GESTURE_SECONDS, gestureSeconds,
} from './clockedControls';
import type { ClockedMachineView, ClockedOutcome } from './clockedControls';
import type { ManifestInstruction } from './types';

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

  it('LISTS declared instructions PRESSABLE, carrying the outcome of the '
     + 'last press and nothing else', () => {
       // OpenSpec `play-the-instruction`, design §9: the disabled flag
       // and its reason are GONE -- an instruction under a clocked root
       // is one request the viewer draws -- and the control carries an
       // `outcome` exactly as `RunInstructionControl` does.
       const layer = clockedControlLayer({
         machine: MACHINE, values: {}, focus: null,
       });
       expect(layer.instructions).toHaveLength(1);
       const pressed = layer.instructions[0];
       expect(pressed.name).toBe('Turn crank');
       expect(pressed.label).toBe('Turn crank');
       expect(pressed.outcome).toBe(null);
       expect(Object.keys(pressed).sort())
         .toEqual(['label', 'name', 'outcome']);
     });

  it('reports a press WHERE IT WAS MADE, by the instruction\'s name', () => {
    const held: ClockedOutcome = {
      status: 'completed', admitted: 12, unit: 'deg', message: null,
      stops: [{ coordinate: 'knob.travel', side: 'high', bound: 0, value: 0,
                input: 12, fraction: 1 }],
    };
    const layer = clockedControlLayer({
      machine: MACHINE, values: {}, focus: null,
      outcomes: { 'Turn crank': held },
    });
    expect(layer.instructions[0].outcome).toBe(held);
    expect(formatClockedOutcome(layer.instructions[0].outcome))
      .toBe('moved 12 deg, held by knob.travel (high 0)');
    // And an instruction's outcome does NOT leak onto a driver of the
    // same layer: the two are keyed in one table, by different names.
    for (const input of layer.inputs) expect(input.outcome).toBe(null);
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

  it("states how long a drawn GESTURE takes: the TEMPO its input's "
     + 'declared instruction states, and the viewer\'s own short '
     + 'duration where the document states none', () => {
    // A handle declares no duration -- only an instruction does -- so
    // the viewer takes one from the document where the document states
    // one, and states one itself where it does not. The fallback is the
    // running chrome's own fifth of a second (`runControls.ts`'s
    // `DEFAULT_NUDGE.seconds`), for the reason recorded there.
    expect(GESTURE_SECONDS).toBe(0.2);
    expect(typeof DEFAULT_NUDGE).toBe('number');

    // THE TEMPO. `'Turn crank': by crank 360 over 2 s` states a rate:
    // 360 design units in two seconds. A gesture is drawn over the
    // declared duration in the proportion its ADMITTED travel bears to
    // the declared travel.
    const tempo: Record<string, ManifestInstruction> = {
      'Turn crank': { by: { crank: 360 }, duration: 2 },
    };
    expect(gestureSeconds('crank', 360, tempo)).toBe(2);
    expect(gestureSeconds('crank', 30, tempo)).toBeCloseTo(2 / 12, 12);
    // No cap: twice the declared travel is twice the declared stroke.
    expect(gestureSeconds('crank', 720, tempo)).toBe(4);
    // A direction is not a rate: a backwards whole turn takes as long.
    expect(gestureSeconds('crank', -360, tempo)).toBe(2);
    // Zero travel is zero seconds, which the drawing already lands at
    // once -- the old zero-travel rule reached by arithmetic.
    expect(gestureSeconds('crank', 0, tempo)).toBe(0);
    // And an input the instruction does not name keeps the fallback,
    // on the same document.
    expect(gestureSeconds('setting', 30, tempo)).toBe(GESTURE_SECONDS);

    // A `targets` instruction states a LANDING, not a travel: the
    // travel it makes depends on where the input stands, so it states a
    // different rate at every bank and none at its own landing. Not a
    // tempo source, whatever the gesture asks for.
    const landing: Record<string, ManifestInstruction> = {
      'Set four': { targets: { operand: 4 }, duration: 0.5 },
    };
    expect(gestureSeconds('operand', 4, landing)).toBe(GESTURE_SECONDS);
    expect(gestureSeconds('operand', 1, landing)).toBe(GESTURE_SECONDS);

    // A declared travel of ZERO states no rate -- a travel of nothing
    // over some duration -- and is skipped.
    expect(gestureSeconds('crank', 30, {
      Nothing: { by: { crank: 0 }, duration: 2 },
    })).toBe(GESTURE_SECONDS);

    // Nothing declared at all, and nothing naming this input.
    expect(gestureSeconds('crank', 360, {})).toBe(GESTURE_SECONDS);
    expect(gestureSeconds('feed', 360, tempo)).toBe(GESTURE_SECONDS);

    // SEVERAL `by` instructions naming one input: the FIRST the
    // document declares, which is the button nearest the top of the
    // panel. The key order is the producer's declaration order and it
    // survives end to end.
    const two: Record<string, ManifestInstruction> = {
      'Set four': { targets: { operand: 4 }, duration: 0.5 },
      Stroke: { by: { crank: 360 }, duration: 2 },
      Nudge: { by: { crank: 36 }, duration: 10 },
    };
    expect(gestureSeconds('crank', 360, two)).toBe(2);

    // A declared duration of ZERO states a real one -- this travel is
    // drawn in no time -- and is honoured, as its own press is.
    const instant: Record<string, ManifestInstruction> = {
      Snap: { by: { crank: 360 }, duration: 0 },
    };
    expect(gestureSeconds('crank', 360, instant)).toBe(0);
    expect(gestureSeconds('crank', 7, instant)).toBe(0);

    // A non-finite or absurd travel is never answered with a non-finite
    // duration: a drawing of `Infinity` seconds is one nothing lands.
    for (const absurd of [Number.NaN, Infinity, -Infinity, 1e308 * 10]) {
      const answered = gestureSeconds('crank', absurd, tempo);
      expect(Number.isFinite(answered)).toBe(true);
      expect(answered).toBeGreaterThanOrEqual(0);
    }
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

// ---------------------------------------------------------------------
// The panel FOLLOWS a drawing (OpenSpec `play-the-instruction`, design
// §9). While a drawing runs the panel is not rebuilt -- the Curta's is
// 23 inputs and 18 readouts, and this cycle claims a frame costs a pose
// -- so one narrow writer rewrites the fields the frame changed. What
// is decided here is WHICH fields, and what each says; `viewer.ts` puts
// the strings in the DOM.
// ---------------------------------------------------------------------

describe('what a drawn frame rewrites in the panel', () => {
  it('names only the ids the frame moved, split into handles and '
     + 'readouts', () => {
       const following = clockedFollowing(
         MACHINE, { crank: 360, operand: 4, 'w0.digit': 7 },
         ['crank', 'w0.digit']);
       expect(following.inputs.map((one) => one.id)).toEqual(['crank']);
       expect(following.readouts.map((one) => one.id)).toEqual(['w0.digit']);
     });

  it('says what each says, in the SAME words the rebuilt panel uses', () => {
    const following = clockedFollowing(
      MACHINE, { crank: 360, 'w0.digit': 7 }, ['crank', 'w0.digit']);
    const crank = following.inputs[0];
    expect(crank.display).toBe(360);
    expect(crank.readout).toBe('360.0000');
    expect(crank.slider).toBe(null);
    // An integer state reads as the whole number it is, as the rebuilt
    // panel's own readout does.
    expect(following.readouts[0].readout).toBe('7');
  });

  it('carries the slider position where the driver declares a range, '
     + 'PINNED at the end rather than clamping the value', () => {
       const following = clockedFollowing(MACHINE, { operand: 12 },
                                          ['operand']);
       expect(following.inputs[0].display).toBe(12);
       expect(following.inputs[0].slider?.position).toBe(9);
     });

  it('ignores an id the focused machine declares nowhere', () => {
    const following = clockedFollowing(MACHINE, { crank: 1 },
                                       ['crank', 'nothing.at.all']);
    expect(following.inputs.map((one) => one.id)).toEqual(['crank']);
    expect(following.readouts).toEqual([]);
  });

  it('follows a CLOCK as a readout, never as a handle', () => {
    const clocked: ClockedMachineView = {
      ...MACHINE, clock: 'time',
    };
    const following = clockedFollowing(clocked, { time: 2.5 }, ['time']);
    expect(following.inputs).toEqual([]);
    expect(following.readouts[0].id).toBe('time');
    expect(following.readouts[0].readout).toBe('2.5000');
  });
});
