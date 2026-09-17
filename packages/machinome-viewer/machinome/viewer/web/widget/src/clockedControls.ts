/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// What the CLOCKED chrome shows, decided as pure data (OpenSpec
// `execute-the-commit`, design §13). Nothing here touches the DOM,
// three.js or the machine: it reads the loaded machine's two tables, the
// focused assembly path and the currently committed bank, and returns
// the controls a layer has. `viewer.ts` renders exactly this and calls
// the same `machine()` handle a host would.
//
// A THIRD chrome, not a widened one.
//
//   - `controls.ts`'s slider WRITES a position into a driver, which is
//     what poses a document with no machine at all.
//   - `runControls.ts` refuses a slider, because under a RUN a
//     coordinate carries history and writing a position is the re-entry
//     the running mode exists to remove.
//   - a CLOCKED driver is positional again: the bank holds where it
//     stands and `move(id, {to})` is a straight path from there. So the
//     slider comes back -- but every gesture is ONE REQUEST, and the
//     request's outcome is reported where it was made.
//
// The other half of the split is the handle rule: every key of `drivers`
// is an input a person may move and no key of `states` ever is
// (ADR-128 §3). A state is a READOUT, follow-only; so is the clock,
// which this build refuses a request on.

import {
  BreadcrumbSegment, ControlPath, breadcrumb, displayValue, formatDisplay,
  formatReadout, navigableChildren, scopedIds, SliderPlan,
} from './controls';
import type { OutcomeReport, OutcomeStatus } from './runControls';
import type { ClockedStop } from './clocked/bounds';
import { ManifestDriver, ManifestInstruction } from './types';

export type { OutcomeStatus };

/** What became of the last request a control issued (design §13), on
 * `runControls.ts`'s own shape, widened by the STOPS that truncated the
 * travel.
 *
 * A gesture an interlock holds is REPORTED, not swallowed: `admitted: 0`
 * with a stop naming the coordinate, the side and the bound is what a
 * maker must see when the knob will not move, and it is the difference
 * between an operable machine and a broken control. */
export interface ClockedOutcome extends OutcomeReport {
  stops: readonly ClockedStop[];
}

/** One driver's control: a HANDLE. */
export interface ClockedInputControl {
  /** The qualified id: what `move` is called with. */
  id: string;
  label: string;
  unit: string | null;
  /** The banked position in NATIVE units. */
  value: number;
  /** The same position in DESIGN units -- what a request speaks. */
  display: number;
  readout: string;
  /** The slider, where the driver declares a `range`. `range` remains
   * PRESENTATION and never a clamp: a request past it is admitted
   * exactly as the framework admits one. */
  slider: SliderPlan | null;
  /** True when there is no range and the value needs a number field. */
  numeric: boolean;
  /** True when the banked value lies outside the declared travel: the
   * thumb is pinned at an end while the readout stays truthful. */
  pinned: boolean;
  /** How far a ± press asks for, in DESIGN units. */
  nudge: number;
  outcome: ClockedOutcome | null;
  driver: ManifestDriver;
}

/** One state's, or the clock's, readout: follow-only, and NEVER a source
 * of a request. */
export interface ClockedReadout {
  id: string;
  label: string;
  unit: string | null;
  value: number;
  display: number;
  readout: string;
  /** `state` for a declared State, `clock` for the elapsed base. */
  kind: 'state' | 'clock';
}

/** One declared instruction, LISTED and DISABLED: ADR-128 §14 publishes
 * the table in the version 5 shape and gives it no runtime meaning.
 * Hiding it would make the panel disagree with the document a maker can
 * read; showing it live would offer a gesture that cannot be honoured. */
export interface ClockedInstructionControl {
  name: string;
  label: string;
  disabled: true;
  /** The reason, for a reader and for assistive tools. */
  reason: string;
}

/** As much of a loaded machine as the chrome reads. `LoadedMachine`
 * satisfies it; a test hand-writes one. */
export interface ClockedMachineView {
  drivers: Readonly<Record<string, ManifestDriver>>;
  states: Readonly<Record<string, ManifestDriver>>;
  instructions: Readonly<Record<string, ManifestInstruction>>;
  clock: string | null;
}

export interface ClockedControlsInput {
  /** The machine the document carries, or null for a document that
   * carries none -- which is every document below version 8. */
  machine: ClockedMachineView | null;
  /** The committed bank, in NATIVE units, by qualified id. */
  values: Record<string, number>;
  focus: ControlPath | null;
  rootLabel?: string;
  /** Per-input nudge amounts a maker has edited, in DESIGN units. */
  nudge?: Readonly<Record<string, number>>;
  /** The last outcome of each control, by input id. */
  outcomes?: Readonly<Record<string, ClockedOutcome | null>>;
}

export interface ClockedControlLayer {
  /** Whether this document has clocked chrome at all. */
  present: boolean;
  breadcrumb: BreadcrumbSegment[];
  /** The next path segments that lead to a declaring layer. */
  children: string[];
  inputs: ClockedInputControl[];
  readouts: ClockedReadout[];
  instructions: ClockedInstructionControl[];
}

/** One design unit a press. A clocked request is instantaneous by
 * construction -- there is no cadence for it to be spread over -- so a
 * nudge is a travel and nothing else. */
export const DEFAULT_NUDGE = 1;

const INSTRUCTIONS_DISABLED =
  'A clocked machine publishes its instruction table and gives it no '
  + 'runtime meaning: move a driver instead.';

function segments(id: string): string[] {
  return id.split('.');
}

function sliderPlan(display: number,
                    driver: ManifestDriver): SliderPlan | null {
  const range = driver.range;
  if (range === null || range.length !== 2
      || range.some((one) => one === null || !Number.isFinite(one))) {
    return null;
  }
  const [min, max] = range as number[];
  return {
    min,
    max,
    step: driver.dtype === 'int' ? 1 : null,
    position: Math.min(Math.max(display, min), max),
  };
}

/** One input's control, at one committed native value. Exported because
 * an accepted request re-derives exactly this and nothing else. */
export function clockedInputControl(
  id: string, driver: ManifestDriver, value: number,
  nudge: number = DEFAULT_NUDGE,
  outcome: ClockedOutcome | null = null,
): ClockedInputControl {
  const display = displayValue(value, driver);
  const slider = sliderPlan(display, driver);
  return {
    id,
    label: segments(id).slice(-1)[0],
    unit: driver.unit,
    value,
    display,
    readout: formatReadout(display),
    slider,
    numeric: slider === null,
    // The range bounds the THUMB, never the value: a machine driven past
    // its travel says so instead of pretending it stopped.
    pinned: slider !== null && slider.position !== display,
    nudge,
    outcome,
    driver,
  };
}

function readoutOf(id: string, declaration: ManifestDriver, value: number,
                   kind: 'state' | 'clock'): ClockedReadout {
  const display = displayValue(value, declaration);
  return {
    id,
    label: segments(id).slice(-1)[0],
    unit: declaration.unit,
    value,
    display,
    readout: formatReadout(display),
    kind,
  };
}

const CLOCK_DECLARATION: ManifestDriver = {
  default: 0, range: null, unit: 's', dtype: null, scale: null,
};

/** Everything the clocked chrome shows for one focused layer. */
export function clockedControlLayer(
  input: ClockedControlsInput): ClockedControlLayer {
  const machine = input.machine;
  if (machine === null) {
    return {
      present: false,
      breadcrumb: breadcrumb(input.focus, input.rootLabel),
      children: [],
      inputs: [],
      readouts: [],
      instructions: [],
    };
  }
  const driverIds = Object.keys(machine.drivers);
  const stateIds = Object.keys(machine.states);
  const clockIds = machine.clock === null ? [] : [machine.clock];
  const instructionNames = Object.keys(machine.instructions);
  const nudge = input.nudge ?? {};
  const outcomes = input.outcomes ?? {};
  const readouts: ClockedReadout[] = [
    ...scopedIds(stateIds, input.focus).map((id) => readoutOf(
      id, machine.states[id],
      input.values[id] ?? machine.states[id].default, 'state')),
    // A CLOCK is a readout, never a handle: it is not a key of
    // `drivers`, and this build refuses a request on it (design §9).
    ...scopedIds(clockIds, input.focus).map((id) => readoutOf(
      id, CLOCK_DECLARATION, input.values[id] ?? 0, 'clock')),
  ];
  return {
    present: true,
    breadcrumb: breadcrumb(input.focus, input.rootLabel),
    inputs: scopedIds(driverIds, input.focus).map((id) => clockedInputControl(
      id, machine.drivers[id],
      input.values[id] ?? machine.drivers[id].default,
      nudge[id] ?? DEFAULT_NUDGE,
      outcomes[id] ?? null,
    )),
    readouts,
    instructions: scopedIds(instructionNames, input.focus).map((name) => ({
      name,
      label: segments(name).slice(-1)[0],
      disabled: true as const,
      reason: INSTRUCTIONS_DISABLED,
    })),
    children: navigableChildren(
      [...driverIds, ...stateIds, ...clockIds, ...instructionNames],
      input.focus),
  };
}

/** What a control says about its last request (design §13).
 *
 * The STOPPED form is the interesting one: the travel the machine
 * actually made, and the interlock that held it, named. */
export function formatClockedOutcome(report: ClockedOutcome | null): string {
  if (report === null) return '';
  const unit = report.unit === null ? '' : ` ${report.unit}`;
  if (report.status === 'refused') {
    return report.message === null ? 'refused' : `refused: ${report.message}`;
  }
  const travelled = report.admitted === null
    ? '' : `${formatDisplay(report.admitted)}${unit}`;
  if (report.stops.length === 0) {
    return report.admitted === null ? 'completed' : `moved ${travelled}`;
  }
  const held = report.stops
    .map((stop) => `${stop.coordinate} (${stop.side} ${formatDisplay(
      stop.bound)})`)
    .join(', ');
  return report.admitted === 0
    ? `held by ${held}` : `moved ${travelled}, held by ${held}`;
}
