/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
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
// (ADR-128 §3). A state is a READOUT, follow-only; so is the CLOCK --
// but a clock is a readout a TRANSPORT advances (OpenSpec
// `run-the-clock`, design §5), where a state is advanced by nothing but
// the machine. The transport is play/pause, a step of a stated number of
// seconds, and the speed ladder. There is NO scrub and NO reverse: a
// slider implies both directions and the clock refuses one of them by
// decision, so a control that could not honour a drag backwards does not
// offer one.

import {
  BreadcrumbSegment, ControlPath, breadcrumb, displayValue, formatDisplay,
  formatReadout, navigableChildren, scopedIds, SliderPlan,
} from './controls';
import { formatElapsed, ladderFor } from './playback';
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

/** One declared instruction, LISTED and PRESSABLE (OpenSpec
 * `play-the-instruction`, design §9). A press is ONE request the machine
 * makes at once and the viewer DRAWS over the declared duration, so the
 * control carries the outcome of the last press exactly as
 * `RunInstructionControl` does -- the travel admitted, the stops that
 * truncated it, or the refusal's own message -- and nothing else. */
export interface ClockedInstructionControl {
  name: string;
  label: string;
  outcome: ClockedOutcome | null;
}

/** As much of a loaded machine as the chrome reads. `LoadedMachine`
 * satisfies it; a test hand-writes one. */
export interface ClockedMachineView {
  drivers: Readonly<Record<string, ManifestDriver>>;
  states: Readonly<Record<string, ManifestDriver>>;
  instructions: Readonly<Record<string, ManifestInstruction>>;
  clock: string | null;
}

/** The CLOCK's transport (design §5): what a maker presses, and what the
 * readout beside it says. Pure data, like everything else here.
 *
 * `null` for a machine that declares no clock, and for a document that
 * carries no machine -- one question, one truthful answer. */
export interface ClockTransportPlan {
  /** The clock's bank id: what a request names. */
  id: string;
  playing: boolean;
  /** The banked instant, in seconds. */
  seconds: number;
  /** That instant formatted, in the form a run's elapsed readout takes:
   * seconds that never wrap and only grow. */
  elapsed: string;
  /** The playback speed, a multiple of real time -- the SAME one the
   * timeline and the run use. */
  speed: number;
  ladder: number[];
  /** How many seconds a STEP asks for. Never negative: the clock has no
   * reverse, so this control has no minus. */
  step: number;
  /** The message of the request that PAUSED the transport, or null. A
   * refused frame pauses and reports once, rather than repeating a
   * refused request sixty times a second. */
  refusal: string | null;
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
  /** The last outcome of each control, by input id or by instruction
   * name. */
  outcomes?: Readonly<Record<string, ClockedOutcome | null>>;
  /** Whether the clock's transport is running (design §5). */
  clockPlaying?: boolean;
  /** How many seconds a step of the clock asks for. */
  clockStep?: number;
  /** The playback speed, a multiple of real time. */
  speed?: number;
  /** The refusal that paused the transport, or null. */
  clockRefusal?: string | null;
  /** The width of the widest elapsed reading shown so far, so the
   * readout widens once and never narrows. */
  clockWidth?: number;
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
  /** The clock's transport, or `null` where the machine declares no
   * clock. There is never a transport over the DRIVERS: a clocked
   * machine has no cadence for one to run, step or speed. */
  transport: ClockTransportPlan | null;
}

/** One design unit a press. A clocked nudge is an AMOUNT and nothing
 * else: what it asks for is a travel, and how long the viewer DRAWS
 * that travel is `gestureSeconds` below -- the tempo the input's own
 * declared instruction states, or `GESTURE_SECONDS` where the document
 * states none. Neither is a property of the nudge amount itself, so
 * there is still nothing per-input for this constant to scale. */
export const DEFAULT_NUDGE = 1;

/** How long a gesture on a handle NO DECLARED TRAVEL NAMES is drawn
 * over, in WALL seconds (OpenSpec `draw-every-request`, design D2;
 * `draw-at-the-declared-tempo`, design D1, which made it the FALLBACK
 * it is).
 *
 * A declared instruction states its own duration; a handle declares
 * none. Where the document states a TRAVEL on that input over a
 * duration, `gestureSeconds` reads the rate off it. Where it states
 * none, the viewer states this: the running chrome's own number and the
 * running chrome's own reason (`runControls.ts`'s `DEFAULT_NUDGE =
 * {amount: 1, seconds: 0.2}`): *a nudge that teleports is a nudge
 * nobody can watch. A fifth of a second is long enough to see the carry
 * throw and short enough to feel like a button.*
 *
 * It is a DURATION and never a rate of its own. The running chrome can
 * afford a rate because its nudge is a travel over SIMULATED time
 * inside a cadence; a clocked gesture has no cadence, and one design
 * unit per 0.2 s would draw the Curta's 360-degree crank nudge over 72
 * seconds. The rate below is not invented that way either: it is READ
 * off a declaration the document already carries. The playback speed
 * scales neither: the speed means machine time (ADR-063) and a drawing
 * is wall time (ADR-064). */
export const GESTURE_SECONDS = 0.2;

/** How long a gesture on `inputId` that ADMITTED `admitted` design
 * units of travel is drawn over, in WALL seconds (OpenSpec
 * `draw-at-the-declared-tempo`, design D1-D3).
 *
 * `duration x |admitted| / |by|` where a declared instruction states a
 * TRAVEL on that input, and `GESTURE_SECONDS` where none does. The
 * Curta's `'Turn crank': by crank_rotation 360 over 2 s` is the case
 * this exists for: at a fixed fifth of a second its whole-turn nudge
 * moves 30 degrees a frame, and the 11.25-degree tooth passage a maker
 * is watching falls inside one frame.
 *
 * Both sides of the ratio are DESIGN units -- `ClockedRequest.admitted`
 * by its own documented asymmetry with `origin`/`end`, and an
 * instruction's `by` because that is what a press asks in -- so the
 * ratio is unit-free and a driver whose `scale` is not 1 is right for
 * free.
 *
 * The travel that counts is the one ADMITTED and not the one asked for:
 * a gesture an interlock clips is drawn for as far as the machine went,
 * at the declared rate. Scaling by what was asked would crawl through a
 * clipped stroke, and the outcome already says in words that it was
 * stopped.
 *
 * Only a `by=` instruction is a source. A `targets=` instruction states
 * where its driver LANDS: the travel it makes depends on where the
 * input stands when it is pressed, so it states a different rate at
 * every bank and a division by zero at its own landing. A declared
 * travel of ZERO states no rate either and is skipped. Where SEVERAL
 * state one, the FIRST the document declares wins -- the button nearest
 * the top of the panel, the chrome listing them in that same key order.
 *
 * There is no cap: a maker who asks for twice the declared travel has
 * asked to watch twice the declared stroke, and a picture drawn at one
 * rate for its first half and another for the rest is a picture of
 * neither. A handle stays usable throughout and a further gesture lands
 * the drawing at once.
 *
 * A declared duration of zero is HONOURED -- gestures on that input
 * land at once, as its own press does -- and zero travel gives zero
 * seconds, which the drawing already lands in one pose. A travel no
 * arithmetic can turn into a finite number of seconds is answered with
 * the fallback rather than with a drawing that never ends. */
export function gestureSeconds(
  inputId: string,
  admitted: number,
  instructions: Readonly<Record<string, ManifestInstruction>>,
): number {
  for (const name of Object.keys(instructions)) {
    const declared = instructions[name].by?.[inputId];
    if (declared === undefined || !Number.isFinite(declared)
        || declared === 0) {
      continue;
    }
    const seconds = instructions[name].duration
      * Math.abs(admitted) / Math.abs(declared);
    return Number.isFinite(seconds) ? seconds : GESTURE_SECONDS;
  }
  return GESTURE_SECONDS;
}

/** How many seconds one press of STEP asks for. A second is the clock's
 * own unit, and the speed ladder is what makes a long watch short. */
export const DEFAULT_CLOCK_STEP = 1;

/** A step amount this control will accept, in seconds.
 *
 * Elapsed seconds have no reverse, so a negative or non-finite amount is
 * not a travel the transport can ask for and the SETTING is left where
 * it was. Refusing a setting is not the same as repairing a request:
 * nothing a maker asks the machine for is ever clamped. */
export function clockStepAmount(asked: number, current: number): number {
  return Number.isFinite(asked) && asked > 0 ? asked : current;
}

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

/** A READOUT's text. An INTEGER coordinate reads as the whole number
 * it is.
 *
 * `formatReadout`'s four fixed decimals are a CONTINUOUS quantity's
 * policy: a readout that changes sixty times a second under a drag
 * wants one constant shape rather than the shortest one. A state the
 * machine commits as an integer has no fraction to report, and `5.0000`
 * claims a precision the coordinate has not got. A SCALED int still
 * reads as a float, because its DESIGN value is not whole. */
function readoutText(display: number, declaration: ManifestDriver): string {
  return declaration.dtype === 'int' && Number.isInteger(display)
    ? String(display) : formatReadout(display);
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
    readout: readoutText(display, declaration),
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
      transport: null,
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
    // A CLOCK is a readout, never a POSITIONAL handle: it is not a key
    // of `drivers`, and the transport above -- and nothing else --
    // advances it.
    ...scopedIds(clockIds, input.focus).map((id) => readoutOf(
      id, CLOCK_DECLARATION, input.values[id] ?? 0, 'clock')),
  ];
  const speed = input.speed ?? 1;
  const seconds = machine.clock === null
    ? 0 : input.values[machine.clock] ?? 0;
  return {
    present: true,
    breadcrumb: breadcrumb(input.focus, input.rootLabel),
    // A machine with no clock is offered NO transport, exactly as it is
    // offered no driver transport: there is nothing for one to advance.
    transport: machine.clock === null ? null : {
      id: machine.clock,
      playing: input.clockPlaying ?? false,
      seconds,
      elapsed: formatElapsed(seconds, input.clockWidth ?? 0),
      speed,
      ladder: ladderFor(speed),
      step: input.clockStep ?? DEFAULT_CLOCK_STEP,
      refusal: input.clockRefusal ?? null,
    },
    inputs: scopedIds(driverIds, input.focus).map((id) => clockedInputControl(
      id, machine.drivers[id],
      input.values[id] ?? machine.drivers[id].default,
      nudge[id] ?? DEFAULT_NUDGE,
      outcomes[id] ?? null,
    )),
    readouts,
    // An instruction's outcome is keyed by its NAME, in the same table a
    // driver's is keyed by its id: one press, one report, where it was
    // made.
    instructions: scopedIds(instructionNames, input.focus).map((name) => ({
      name,
      label: segments(name).slice(-1)[0],
      outcome: outcomes[name] ?? null,
    })),
    children: navigableChildren(
      [...driverIds, ...stateIds, ...clockIds, ...instructionNames],
      input.focus),
  };
}

/** One handle the panel must rewrite while a drawing runs, and one
 * readout. A narrow pair, not a control: the panel is NOT rebuilt per
 * frame (design §9), so what a frame changes is a field's text and a
 * thumb's position and nothing else. */
export interface FollowedInput {
  id: string;
  /** The position in DESIGN units, as the field shows it. */
  display: number;
  readout: string;
  /** The thumb, where the driver declares a range. The range bounds the
   * THUMB and never the value, exactly as it does in a rebuilt panel. */
  slider: SliderPlan | null;
}

export interface FollowedReadout {
  id: string;
  display: number;
  readout: string;
}

export interface Following {
  inputs: FollowedInput[];
  readouts: FollowedReadout[];
}

/** What a drawn frame rewrites in the panel: the moved ids, split into
 * the handles and the readouts that carry them, each saying what the
 * rebuilt panel would have said (OpenSpec `play-the-instruction`, design
 * §9).
 *
 * `moved` comes from the drawing's own frame, so no comparison is made
 * twice, and an id the focused machine declares nowhere is passed over
 * rather than invented. */
export function clockedFollowing(machine: ClockedMachineView,
                                 bank: Record<string, number>,
                                 moved: readonly string[]): Following {
  const inputs: FollowedInput[] = [];
  const readouts: FollowedReadout[] = [];
  for (const id of moved) {
    const value = bank[id];
    if (value === undefined) continue;
    const driver = machine.drivers[id];
    if (driver !== undefined) {
      const display = displayValue(value, driver);
      inputs.push({
        id,
        display,
        readout: formatReadout(display),
        slider: sliderPlan(display, driver),
      });
      continue;
    }
    const declaration = machine.states[id]
      ?? (machine.clock !== null && id === machine.clock
        ? CLOCK_DECLARATION : undefined);
    if (declaration === undefined) continue;
    const display = displayValue(value, declaration);
    readouts.push({
      id, display, readout: readoutText(display, declaration),
    });
  }
  return { inputs, readouts };
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
