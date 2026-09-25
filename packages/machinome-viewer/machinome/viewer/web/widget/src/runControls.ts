/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// What the RUNNING chrome shows, decided as pure data (OpenSpec
// `drive-the-run-on-screen`, design §2). Nothing here touches the DOM,
// three.js or the run: it reads the loaded program's two tables, the
// focused assembly path and the currently committed bank, and returns
// the controls a layer has. `viewer.ts` renders exactly this and calls
// the same `run()` handle a host would -- which is what keeps the
// on-screen and programmatic doors indistinguishable, and what lets
// every decision below be tested in plain node.
//
// This is a DIFFERENT chrome from `controls.ts`'s, not a widened one.
// A slider writes a position into a coordinate; under a run a
// coordinate is the output of an integration that carries history, so
// writing a position is exactly the re-entry the running mode exists to
// remove -- ten `Add one` on a slider would leave the tens drum where
// one did. The pilot's rule is the same one from the other side: "there
// is no two-way binding between an editable position and the
// mechanism", and "readouts follow committed state and never feed
// another movement request back into the run". So: no slider, and no
// timeline.
//
// Two unit systems meet here exactly as they do in `controls.ts`: the
// bank is NATIVE, while a readout, a nudge amount, a jog rate and a
// command's admitted travel are all DESIGN units -- the units an
// instruction target is stated in and a maker reads.

import {
  BreadcrumbSegment, ControlPath, InstructionControl, breadcrumb,
  displayValue, formatDisplay, formatReadout, navigableChildren, scopedIds,
} from './controls';
import { formatElapsed, ladderFor } from './playback';
import { ManifestDriver, ManifestInstruction } from './types';

/** What a nudge ASKS FOR: a relative travel over a duration. Never a
 * coordinate, and never written anywhere by the editor that sets it. */
export interface NudgePlan {
  /** Design units of travel, signed by the button pressed. */
  amount: number;
  /** Simulated seconds the travel is spread over. */
  seconds: number;
}

/** What a hold-to-jog asks for: design units per simulated second, until
 * the interaction ends. */
export interface JogPlan {
  rate: number;
}

/** One design unit over a fifth of a second (design D3).
 *
 * Not instantaneous: a zero-duration move admits its whole travel in one
 * tick, and while the jump machinery survives that, a stop behind a
 * nonlinear edge is located to first order inside it -- and a nudge that
 * teleports is a nudge nobody can watch. A fifth of a second is long
 * enough to see the carry throw and short enough to feel like a button.
 * It is 48 whole ticks at the default 1/240 step. */
export const DEFAULT_NUDGE: NudgePlan = { amount: 1, seconds: 0.2 };

/** One design unit per simulated second. */
export const DEFAULT_JOG: JogPlan = { rate: 1 };

export type OutcomeStatus =
  'active' | 'completed' | 'blocked' | 'refused' | 'cancelled';

/** What became of the last request a control issued (design D7). */
export interface OutcomeReport {
  status: OutcomeStatus;
  /** The travel the machine actually ADMITTED, in design units; null
   * for a request the run declined before it could move at all. */
  admitted: number | null;
  unit: string | null;
  /** The run's own message, for a refusal. */
  message: string | null;
}

export interface RunInputControl {
  /** The qualified id: what `move` and `rate` are called with. */
  id: string;
  /** The final segment -- the name relative to the focused layer. */
  label: string;
  unit: string | null;
  /** The committed position in NATIVE units, as the bank holds it. */
  value: number;
  /** The same position in DESIGN units. */
  display: number;
  /** What the readout shows: fixed width, follow-only, never a source
   * of a request. */
  readout: string;
  nudge: NudgePlan;
  jog: JogPlan;
  outcome: OutcomeReport | null;
  /** The declaration, for the design-unit conversion a committed frame
   * re-derives this control through -- the same field, for the same
   * reason, `controls.ts`'s `DriverControl` carries. */
  driver: ManifestDriver;
}

/** `controls.ts`'s instruction control, carrying the outcome of the last
 * press (design D7): a button reports where it was pressed. */
export interface RunInstructionControl extends InstructionControl {
  outcome: OutcomeReport | null;
}

export interface TransportPlan {
  running: boolean;
  speed: number;
  ladder: number[];
  /** Elapsed simulation seconds, formatted. */
  elapsed: string;
  tick: number;
  /** The run's own message for a tick it refused, or null. */
  refusal: string | null;
}

export interface TransportInput {
  running: boolean;
  speed: number;
  elapsedSeconds: number;
  tick: number;
  refusal: string | null;
  /** The width of the widest elapsed reading shown so far, so the
   * readout widens once and never narrows. */
  elapsedWidth?: number;
}

/** As much of a loaded program as the chrome reads. `LoadedProgram`
 * satisfies it; a test hand-writes one. */
export interface RunProgramView {
  inputs: readonly string[];
  drivers: Readonly<Record<string, ManifestDriver>>;
  instructions: Readonly<Record<string, ManifestInstruction>>;
}

export interface RunControlsInput {
  /** The program the document carries, or null for one that carries
   * none -- which is every document of versions 1 to 4. */
  program: RunProgramView | null;
  /** The committed bank, in NATIVE units, by qualified id. */
  values: Record<string, number>;
  focus: ControlPath | null;
  rootLabel?: string;
  /** Per-input request settings a maker has edited, by id. */
  nudge?: Readonly<Record<string, NudgePlan>>;
  jog?: Readonly<Record<string, JogPlan>>;
  /** The last outcome of each control, by input id or instruction name. */
  outcomes?: Readonly<Record<string, OutcomeReport | null>>;
  transport: TransportInput;
}

export interface RunControlLayer {
  /** Whether this document has running chrome at all. */
  present: boolean;
  breadcrumb: BreadcrumbSegment[];
  /** The next path segments that lead to a declaring layer. */
  children: string[];
  inputs: RunInputControl[];
  instructions: RunInstructionControl[];
  transport: TransportPlan;
}

function segments(id: string): string[] {
  return id.split('.');
}

/** One input's control, at one committed native value. Exported because
 * a committed frame re-derives exactly this and nothing else. */
export function runInputControl(
  id: string,
  driver: ManifestDriver,
  value: number,
  nudge: NudgePlan = DEFAULT_NUDGE,
  jog: JogPlan = DEFAULT_JOG,
  outcome: OutcomeReport | null = null,
): RunInputControl {
  const display = displayValue(value, driver);
  return {
    id,
    label: segments(id).slice(-1)[0],
    unit: driver.unit,
    value,
    display,
    readout: formatReadout(display),
    nudge,
    jog,
    outcome,
    driver,
  };
}

/** The transport bar's plan: run, pause, step, speed, elapsed, reset --
 * and deliberately no scrubber (design D6). */
export function transportPlan(input: TransportInput): TransportPlan {
  return {
    running: input.running,
    speed: input.speed,
    ladder: ladderFor(input.speed),
    elapsed: formatElapsed(input.elapsedSeconds, input.elapsedWidth ?? 0),
    tick: input.tick,
    refusal: input.refusal,
  };
}

/** Everything the running chrome shows for one focused layer. */
export function runControlLayer(input: RunControlsInput): RunControlLayer {
  const program = input.program;
  const inputIds = program === null ? [] : [...program.inputs];
  const instructionNames = program === null
    ? [] : Object.keys(program.instructions);
  const nudge = input.nudge ?? {};
  const jog = input.jog ?? {};
  const outcomes = input.outcomes ?? {};
  return {
    // A document carrying a program is driven by requests; one carrying
    // none reaches exactly the chrome it reached before this change.
    present: program !== null,
    breadcrumb: breadcrumb(input.focus, input.rootLabel),
    // The SAME focus rule as the posed chrome's, by segment equality and
    // never by string prefix: `x_axis_two.motor` starts with `x_axis` as
    // text and belongs to another branch entirely.
    inputs: scopedIds(inputIds, input.focus).map((id) => runInputControl(
      id,
      (program as RunProgramView).drivers[id],
      input.values[id] ?? (program as RunProgramView).drivers[id].default,
      nudge[id] ?? DEFAULT_NUDGE,
      jog[id] ?? DEFAULT_JOG,
      outcomes[id] ?? null,
    )),
    // A button REFERENCES the instruction rather than repeating its
    // definition, so a travel (`by`) and a target (`targets`) are one
    // button apiece and the run reads which it is.
    instructions: scopedIds(instructionNames, input.focus).map((name) => ({
      name,
      label: segments(name).slice(-1)[0],
      outcome: outcomes[name] ?? null,
    })),
    children: navigableChildren([...inputIds, ...instructionNames],
                                input.focus),
    transport: transportPlan(input.transport),
  };
}

/** What a control says about its last request (design D7).
 *
 * The blocked form is the interesting one, and it says what the pilot
 * asked it to say: the travel the machine actually made, with nothing
 * anywhere remembering the rest. */
export function formatOutcome(report: OutcomeReport | null): string {
  if (report === null) {
    return '';
  }
  const unit = report.unit === null ? '' : ` ${report.unit}`;
  switch (report.status) {
    case 'active':
      return 'running…';
    case 'blocked':
      return report.admitted === null
        ? 'blocked'
        : `blocked after ${formatDisplay(report.admitted)}${unit}`;
    case 'refused':
      return report.message === null
        ? 'refused' : `refused: ${report.message}`;
    case 'cancelled':
      return 'cancelled';
    default:
      return 'completed';
  }
}
