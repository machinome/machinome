/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// Every decision the RUNNING chrome makes, made here where it can be
// tested (OpenSpec `drive-the-run-on-screen`, design §2). `viewer.ts`
// renders what these functions return and decides nothing of its own:
// there is no DOM test framework in this bench, so anything deciding
// must live here -- exactly the split `controls.ts` already has.
//
// The running chrome is a DIFFERENT chrome, not the posed one widened:
// a slider writes a position into a coordinate, and under a run a
// coordinate is the output of an integration that carries history. So
// there is no slider here, and no timeline.

import { describe, expect, it } from 'vitest';
import { breadcrumb, navigableChildren } from './controls';
import { SPEED_LADDER } from './playback';
import {
  DEFAULT_JOG, DEFAULT_NUDGE, formatOutcome, runControlLayer, transportPlan,
} from './runControls';
import type { RunControlsInput, RunProgramView } from './runControls';
import { ManifestDriver, ManifestInstruction } from './types';

const digit = (): ManifestDriver => ({
  default: 0, range: null, unit: 'digit', dtype: null, scale: null,
});

const ustep = (): ManifestDriver => ({
  default: 0, range: [0, 100], unit: 'mm', dtype: 'int', scale: 0.0125,
});

// One machine shaped like the acceptance document's, plus a deeper
// branch and a decoy whose id STARTS WITH the focus as text and belongs
// to another branch entirely.
const program = (): RunProgramView => ({
  inputs: ['units_entry', 'x_axis.motor', 'x_axis_two.motor',
           'head.spindle.feed'],
  drivers: {
    units_entry: digit(),
    'x_axis.motor': ustep(),
    'x_axis_two.motor': ustep(),
    'head.spindle.feed': ustep(),
  },
  instructions: {
    'Add one': { by: { units_entry: 1 }, duration: 1 },
    'x_axis.Home': { targets: { 'x_axis.motor': 0 }, duration: 2 },
  } as Record<string, ManifestInstruction>,
});

const transport = () => ({
  running: false, speed: 1, elapsedSeconds: 0, tick: 0, refusal: null,
});

const layer = (overrides: Partial<RunControlsInput> = {}) =>
  runControlLayer({
    program: program(),
    values: { units_entry: 0, 'x_axis.motor': 0, 'x_axis_two.motor': 0,
              'head.spindle.feed': 0 },
    focus: null,
    transport: transport(),
    ...overrides,
  });

describe('runControlLayer', () => {
  it('is present only for a document that carries a program', () => {
    expect(layer().present).toBe(true);
    expect(runControlLayer({
      program: null, values: {}, focus: null, transport: transport(),
    }).present).toBe(false);
  });

  it('shows the focused layer by segment equality, never by prefix', () => {
    // `x_axis_two.motor` starts with `x_axis` as TEXT. It is another
    // branch of the machine, and the running chrome must not show it
    // under a focus of `x_axis`.
    const focused = layer({ focus: ['x_axis'] });

    expect(focused.inputs.map((one) => one.id)).toEqual(['x_axis.motor']);
    expect(focused.instructions.map((one) => one.name))
      .toEqual(['x_axis.Home']);
  });

  it('shows the root layer at the root focus', () => {
    const root = layer();

    expect(root.inputs.map((one) => one.id)).toEqual(['units_entry']);
    expect(root.instructions.map((one) => one.name)).toEqual(['Add one']);
  });

  it('reuses the posed chrome breadcrumb and navigable children', () => {
    const focused = layer({ focus: ['x_axis'], rootLabel: 'mill' });

    expect(focused.breadcrumb).toEqual(breadcrumb(['x_axis'], 'mill'));
    expect(layer({ rootLabel: 'mill' }).children).toEqual(navigableChildren(
      ['units_entry', 'x_axis.motor', 'x_axis_two.motor',
       'head.spindle.feed', 'Add one', 'x_axis.Home'], null));
  });

  it('reads a position in design units with its declared unit', () => {
    const focused = runControlLayer({
      program: program(),
      // 8000 microsteps at 0.0125 mm each: the bank is NATIVE and the
      // readout is what a maker reads.
      values: { 'x_axis.motor': 8000 },
      focus: ['x_axis'],
      transport: transport(),
    });

    const motor = focused.inputs[0];
    expect(motor.label).toBe('motor');
    expect(motor.unit).toBe('mm');
    expect(motor.value).toBe(8000);
    expect(motor.display).toBe(100);
    expect(motor.readout).toBe('100.0000');
  });

  it('defaults a nudge to one design unit over a fifth of a second', () => {
    expect(DEFAULT_NUDGE).toEqual({ amount: 1, seconds: 0.2 });
    expect(DEFAULT_JOG).toEqual({ rate: 1 });
    expect(layer().inputs[0].nudge).toEqual(DEFAULT_NUDGE);
    expect(layer().inputs[0].jog).toEqual(DEFAULT_JOG);
  });

  it('carries an edited amount or rate into the plan and moves nothing', () => {
    // Ratified: "Amount and rate editors configure future commands, not
    // current mechanical coordinates."
    const edited = layer({
      nudge: { units_entry: { amount: 5, seconds: 1 } },
      jog: { units_entry: { rate: 3 } },
    });

    expect(edited.inputs[0].nudge).toEqual({ amount: 5, seconds: 1 });
    expect(edited.inputs[0].jog).toEqual({ rate: 3 });
    expect(edited.inputs[0].value).toBe(0);
    expect(edited.inputs[0].display).toBe(0);
  });

  it('gives a relative instruction a button like an absolute one', () => {
    // `Add one` is declared as a TRAVEL (`by`), which is what version 5
    // publishes and what the shipped instruction button cannot read.
    const root = layer();
    const focused = layer({ focus: ['x_axis'] });

    expect(root.instructions).toEqual([
      { name: 'Add one', label: 'Add one', outcome: null }]);
    expect(focused.instructions).toEqual([
      { name: 'x_axis.Home', label: 'Home', outcome: null }]);
  });

  it('reports the last outcome at the control that issued it', () => {
    const reported = layer({
      outcomes: {
        units_entry: { status: 'blocked', admitted: 0.5, unit: 'digit',
                       message: null },
        'Add one': { status: 'completed', admitted: 1, unit: 'digit',
                     message: null },
      },
    });

    expect(reported.inputs[0].outcome?.status).toBe('blocked');
    expect(reported.instructions[0].outcome?.status).toBe('completed');
  });

  it('has no slider and no timeline anywhere in its plan', () => {
    const written = JSON.stringify(layer());

    expect(written).not.toContain('slider');
    expect(written).not.toContain('timeline');
  });
});

describe('transportPlan', () => {
  it('carries the run, the speed ladder, the tick and the elapsed clock', () => {
    const plan = transportPlan({
      running: true, speed: 10, elapsedSeconds: 65.54, tick: 15730,
      refusal: null,
    });

    expect(plan.running).toBe(true);
    expect(plan.speed).toBe(10);
    expect(plan.ladder).toEqual([...SPEED_LADDER]);
    expect(plan.tick).toBe(15730);
    expect(plan.elapsed).toBe('1:05.54');
    expect(plan.refusal).toBeNull();
  });

  it('offers a host-set speed the ladder lacks', () => {
    expect(transportPlan({ ...transport(), speed: 7 }).ladder).toContain(7);
  });

  it('carries the run\'s own refusal message', () => {
    const plan = transportPlan({
      ...transport(),
      refusal: "two relations disagree about 'units.drum.turn'",
    });

    expect(plan.refusal).toBe(
      "two relations disagree about 'units.drum.turn'");
  });

  it('never narrows the elapsed readout once it has widened', () => {
    expect(transportPlan({ ...transport(), elapsedSeconds: 5,
                           elapsedWidth: 8 }).elapsed).toBe('00:05.00');
  });
});

describe('formatOutcome', () => {
  it('says nothing for a control nobody has pressed', () => {
    expect(formatOutcome(null)).toBe('');
  });

  it('says how far a blocked request actually got', () => {
    // The pilot's own sentence: the travel the machine actually made,
    // with nothing remembering the rest.
    expect(formatOutcome({ status: 'blocked', admitted: 12.5, unit: 'mm',
                           message: null })).toBe('blocked after 12.5 mm');
  });

  it('carries the run\'s own reason for a refusal', () => {
    expect(formatOutcome({
      status: 'refused', admitted: null, unit: 'digit',
      message: "'units_entry' is already owned by a move command",
    })).toBe("refused: 'units_entry' is already owned by a move command");
  });

  it('names the other three outcomes plainly', () => {
    const report = (status: 'completed' | 'cancelled' | 'active') => ({
      status, admitted: 1, unit: 'digit', message: null,
    });
    expect(formatOutcome(report('completed'))).toBe('completed');
    expect(formatOutcome(report('cancelled'))).toBe('cancelled');
    expect(formatOutcome(report('active'))).toBe('running…');
  });
});
