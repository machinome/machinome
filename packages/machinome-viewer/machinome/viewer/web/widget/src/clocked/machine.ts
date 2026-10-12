/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// ONE REQUEST on a clocked machine: the clip, the events, the commits
// and the pose (`simulation/clocked.py`'s `Clocked.move`, `_clipped`,
// `_judged`, `_next_event` and the session verbs; OpenSpec
// `execute-the-commit`, design §3, §6, §7, §8, §9, §12, and
// `run-the-clock`, design §1, §2, §3).
//
// The one input a request may move is a declared DRIVER or the
// machine's CLOCK, and the path is the same one: the clip, the same
// solver, the same landing rule, the same ordering. Nothing in the
// solve is clock-aware. What IS the clock's own is that no compiled
// constraint ever clips it -- a declared range is a MECHANICAL stop and
// nothing is in the way of the next second -- and that a request which
// would run it backwards is REFUSED rather than stopped.
//
// A pure SYNCHRONOUS library: no DOM, no three.js, no `postMessage`. A
// clocked request is not a cadence -- it is one gesture, one solve, one
// pose -- so putting it in a worker would add a structured-clone round
// trip and a task hop to EVERY gesture, for a computation the whole
// clocked discipline exists to make cheap (design §3). Being a pure
// library is also what lets the conformance corpus replay IN THREAD,
// where a divergence is a stack trace rather than a message that never
// came back.

import { clip, levelReading, boundAt, valueAt } from './bounds';
import type { ClockedStop, LevelReading } from './bounds';
import { committed, halfToEven } from './commit';
import {
  ClockedConflict, ClockedRangeError, ClockedRequestError,
} from './document';
import type { LoadedCommit, LoadedMachine } from './document';
import { nextEvent } from './events';
import type { ManifestDriver } from '../types';
import { evaluateExpression } from '../run/program';
import { withExpressions } from '../expressions';

/** ONE EVENT: where on the path it happened, what the input stood at,
 * which committing relation (or relations) fired there, and what they
 * wrote.
 *
 * One entry per EVENT rather than per relation, because relations that
 * land on one float ARE one event -- they read the same pre-event bank
 * and their targets take their results together, and declaration order
 * is not observable between them. */
export interface ClockedCommit {
  relations: string[];
  fraction: number;
  value: number;
  targets: Record<string, number>;
}

/** What one `move` did: the input, its travel, BOTH ENDS of the path it
 * travelled, the events it fired in path order, how much of the travel
 * the machine ADMITTED (in DESIGN units, the units `by` speaks), and the
 * bounds it STOPPED at. `stops` is empty exactly when the whole travel
 * was made.
 *
 * Mirrors the producer's `Request` field for field (`clocked.py`'s
 * `Request`). */
export interface ClockedRequest {
  input: string;
  by: number | null;
  to: number | null;
  /** The value the moving input STOOD AT when the request began, taken
   * verbatim from the bank and therefore in that input's own NATIVE
   * units -- the units every `ClockedCommit.value` speaks, so that every
   * event's value lies on the segment the two ends span.
   *
   * A deliberate asymmetry with `admitted`, which speaks DESIGN units
   * because that is what `by=` asked in. Neither end is left for a
   * caller to recompute: `origin + admitted / scale` can land on a float
   * this machine never stood at, and a commit landing exactly ON the
   * endpoint would then read as unfired (OpenSpec
   * `play-the-instruction`, design §2). */
  origin: number;
  /** The value it ENDED at: the CLIPPED landing the bank holds
   * afterwards, native, equal to `origin` for a request admitted at zero
   * travel. */
  end: number;
  commits: ClockedCommit[];
  admitted: number;
  stops: ClockedStop[];
}

/** A bank taken against one machine. `identity` is the sha256 the
 * document publishes, so a bank taken against one machine is refused
 * against another and a changed RANGE changes the identity
 * (ADR-128 §13). */
export interface ClockedSnapshot {
  identity: string;
  bank: Record<string, number>;
}

export interface ClockedMachine {
  identity(): string;
  clock(): string | null;
  /** The bank's id order, as the document derives it (design §2). */
  order(): readonly string[];
  /** The committed bank, in NATIVE units, by qualified id. */
  state(): Record<string, number>;
  drivers(): Record<string, ManifestDriver>;
  states(): Record<string, ManifestDriver>;
  /** One request on ONE input -- a declared driver, or the machine's
   * CLOCK where it declares one -- BY a travel or TO a value, in DESIGN
   * units. */
  move(input: string, request: { by?: number; to?: number }): ClockedRequest;
  snapshot(): ClockedSnapshot;
  restore(state: ClockedSnapshot): void;
  reset(): void;
  /** PLAY a declared instruction: the ONE request it states, made
   * through the same executor every other request goes through, and
   * RETURNED. `by` is a `move(id, {by})`, `targets` a `move(id, {to})`,
   * both in design units. The declared `duration` is not read here -- a
   * request is a path and not an interval, and the duration says how
   * long a CONSUMER draws the transition (`src/clocked/drawing.ts`). */
  trigger(name: string): ClockedRequest;
  /** Refused by name: a clocked machine has no cadence to run, step or
   * speed (design §4). */
  step(): never;
  rate(input: string, rate: number): never;
}

export interface MachineOptions {
  /** Called with the bank a request is about to commit, BEFORE it is
   * assigned, so a pose that refuses leaves the bank standing
   * (ADR-125's atomicity). */
  pose?: (bank: Record<string, number>) => void;
}

/** `target`, expressed in DESIGN units, as native machine state
 * (`Driver.native`). The rounding happens ONCE, here, at the moment a
 * design-unit target becomes machine state. */
function native(declaration: ManifestDriver, target: number): number {
  const value = declaration.scale === null
    ? target : target / declaration.scale;
  return declaration.dtype === 'int' ? halfToEven(value) : value;
}

function twoAnswers(identifier: string, first: LoadedCommit,
                    second: LoadedCommit, inputId: string,
                    landing: number): ClockedConflict {
  return new ClockedConflict(
    `the state '${identifier}' is written by two committing relations at ` +
    `ONE event -- ${first.description} and ${second.description} both fire ` +
    `at ${inputId} = ${landing}. A state may be written at several ` +
    'DIFFERENT events, and has one answer at each: fold these two laws ' +
    'into one, or move one event off the other\'s landing. The request ' +
    'committed nothing.');
}

export function clockedMachine(machine: LoadedMachine,
                               options: MachineOptions = {}): ClockedMachine {
  let bank: Record<string, number> = { ...machine.initial };

  const posed = (next: Record<string, number>): void => {
    // The pose is part of the request, so it happens BEFORE the bank is
    // assigned and its refusal leaves everything standing.
    if (options.pose !== undefined) options.pose(next);
    bank = next;
  };

  /** The declaration of the ONE input a request may name: a declared
   * driver, or -- under the elapsed base -- the clock
   * (`Clocked._input`). */
  const declarationOf = (inputId: string): ManifestDriver => {
    if (machine.clock !== null && inputId === machine.clock) {
      // A clock has no scale and no dtype: elapsed seconds are what
      // they are, so `native()` is the identity and `by`, `to` and
      // `admitted` are all plain seconds. No conversion happens
      // anywhere, and that is a decision (`run-the-clock`, design §1).
      return { default: 0, range: null, unit: 's', dtype: null, scale: null };
    }
    const driver = machine.drivers[inputId];
    if (driver !== undefined) return driver;
    if (machine.states[inputId] !== undefined) {
      throw new ClockedRequestError(
        `move('${inputId}', ...) names a State. A state is written by the ` +
        'machine at an event, through the committing relation that names ' +
        'it as a target, and a request moves a DRIVER: name the input ' +
        'whose motion the event is located on.');
    }
    const known = Object.keys(machine.drivers).sort().join(', ') || 'none';
    throw new ClockedRequestError(
      `move('${inputId}', ...) names no declared driver of this machine. A ` +
      'request moves ONE declared driver by its qualified id -- a joint ' +
      'coordinate\'s value comes from the pose the drivers and the states ' +
      `produce, never from a request; declared: ${known}.`);
  };

  /** The next event on the remaining path: its landing, and every
   * relation that fires there (`Clocked._next_event`).
   *
   * Two relations are ONE event exactly when their far-side landings are
   * the SAME float. No tolerance decides it: a tolerance stated as a
   * fraction of the request's travel would make one long request merge
   * events that several short requests keep apart. */
  const eventOn = (values: Record<string, number>, inputId: string,
                   current: number, delta: number):
  { landing: number; firing: LoadedCommit[] } | null => {
    let earliest: { where: number; landing: number } | null = null;
    const landings = new Map<LoadedCommit, number>();
    for (const relation of machine.commits) {
      if (!relation.jumps.has(inputId)) continue;
      const found = nextEvent(machine, relation, values, inputId, current,
                              delta);
      if (found === null) continue;
      landings.set(relation, found.landing);
      if (earliest === null || found.where < earliest.where) earliest = found;
    }
    if (earliest === null) return null;
    const { landing } = earliest;
    const firing = machine.commits.filter(
      (relation) => landings.get(relation) === landing);
    return { landing, firing };
  };

  /** `target` truncated to where the machine's declared stops allow, and
   * the stops met there (`Clocked._clipped`).
   *
   * A request stopped at ZERO travel is ADMITTED: it moves nothing,
   * fires nothing, poses nothing new and reports its stop. That is what
   * an interlock does, and it is what makes a clocked machine
   * operable. */
  const clipped = (levels: LevelReading[], inputId: string, origin: number,
                   target: number): { target: number; stops: ClockedStop[] } => {
    const requested = target - origin;
    if (levels.length === 0 || requested === 0) return { target, stops: [] };
    const found: { fraction: number; landing: number;
                   level: LevelReading; }[] = [];
    for (const level of levels) {
      const reached = clip(machine, level, inputId, origin, requested);
      if (reached !== null) {
        found.push({ ...reached, level });
      }
    }
    if (found.length === 0) return { target, stops: [] };
    // The EARLIEST fraction wins -- the first of them where two are
    // equal, as `min` takes it.
    let earliest = found[0];
    for (const entry of found) {
      if (entry.fraction < earliest.fraction) earliest = entry;
    }
    const landing = earliest.landing;
    const stops = found
      .filter((entry) => entry.landing === landing)
      .map((entry) => ({
        coordinate: entry.level.bound.coordinate,
        side: entry.level.bound.side,
        bound: boundAt(machine, entry.level, inputId, landing),
        value: valueAt(machine, entry.level, inputId, landing),
        input: landing,
        // The fraction's SIGN is part of the contract: the producer
        // computes it exactly here, and normalises nothing, so a stop at
        // zero travel on a NEGATIVE request carries `-0`.
        fraction: (landing - origin) / requested,
      }));
    return { target: landing, stops };
  };

  /** Every compiled constraint, over the bank the request ends at
   * (`Clocked._judged`).
   *
   * With the clip in front of the events the only thing that can still
   * carry a coordinate out of range is a COMMIT -- a state an event
   * wrote, which the clip read at its pre-request value. Made BEFORE the
   * tree is posed, so a refused request never poses at all. */
  const judged = (levels: LevelReading[], next: Record<string, number>,
                  inputId: string, by: number | null,
                  to: number | null): void => {
    for (const level of levels) {
      const { bound } = level;
      const values: Record<string, number> = {};
      for (const name of bound.names) values[name] = next[name];
      values[machine.own] = level.values[machine.own];
      if (evaluateExpression(machine, bound.level, values) > level.threshold) {
        const asked = to === null ? `by=${by}` : `to=${to}`;
        throw new ClockedRangeError(
          `${bound.node}: joint '${bound.joint}' -- the coordinate ` +
          `'${bound.coordinate}' -- declares a ${bound.side} bound of ` +
          `${evaluateExpression(machine, bound.bound, values)} ` +
          `${bound.unit ?? 'units'}, and the request ` +
          `move('${inputId}', ${asked}) ends with it at ` +
          `${evaluateExpression(machine, bound.chain, values)}, which is ` +
          'outside it. The clip read that bound over the bank the request ' +
          'STARTED from; an event inside the request committed a state ' +
          'that moved it. The request committed nothing: the bank, the ' +
          'tree and the record stand as they were. Split the request at ' +
          'that event.');
      }
    }
  };

  return {
    identity: () => machine.identity,
    clock: () => machine.clock,
    order: () => machine.order,
    state: () => ({ ...bank }),
    drivers: () => ({ ...machine.drivers }),
    states: () => ({ ...machine.states }),

    move(inputId: string, request: { by?: number; to?: number }):
    ClockedRequest {
      return withExpressions(() => {
        const by = request.by === undefined ? null : request.by;
        const to = request.to === undefined ? null : request.to;
        const declaration = declarationOf(inputId);
        if ((by === null) === (to === null)) {
          throw new ClockedRequestError(
            `move('${inputId}', ...) states exactly one of by= (how far to ` +
            'travel) and to= (where to land), both in design units; got ' +
            `by=${by} and to=${to}.`);
        }
        const origin = bank[inputId];
        const target = to !== null
          ? native(declaration, to) : origin + native(declaration, by as number);
        if (machine.clock !== null && inputId === machine.clock
            && target < origin) {
          // TIME NEVER REVERSES (`Clocked.move`, `clocked.py:2064-2082`),
          // checked exactly where the producer checks it: AFTER the by/to
          // exclusivity refusal and after `target` is computed, BEFORE the
          // clip. The order is observable -- a request stating both `by`
          // and `to` on a backwards clock gets the exclusivity message --
          // so it is mirrored rather than re-derived.
          //
          // A REFUSAL and not a stop: a stop reports a bound the machine
          // MET, and no bound was met. ZERO is admitted and falls straight
          // through: `target === origin` makes the clip return at once and
          // the event loop breaks on `delta === 0`.
          const asked = to === null ? `by=${by}` : `to=${to}`;
          throw new ClockedRequestError(
            `move('${inputId}', ${asked}) asks this machine's clock to run ` +
            `BACKWARDS: it stands at ${origin} seconds and the request ends ` +
            `at ${target}. Elapsed seconds never wrap and never reverse -- no ` +
            'bound was met and nothing stopped, the request has no meaning. ' +
            'Restore a snapshot taken at the earlier instant, or reset the ' +
            'machine, to stand before it again.');
        }

        // STEP 0: the request's travel is CLIPPED to the largest fraction
        // at which every compiled constraint is still satisfied, ONCE,
        // over the bank as it stands here, BEFORE the first event is
        // located.
        const levels = machine.bounds.map(
          (bound) => levelReading(machine, bound, bank));
        const { target: clippedTarget, stops } = clipped(levels, inputId, origin,
                                                         target);
        const working = { ...bank };
        const commits: ClockedCommit[] = [];
        let current = origin;
        const span = clippedTarget - origin;
        for (;;) {
          const delta = clippedTarget - current;
          if (delta === 0) break;
          const event = eventOn(working, inputId, current, delta);
          if (event === null) break;
          const { landing, firing } = event;
          // SYNCHRONOUS reads: every relation firing here reads the bank
          // as it stood BEFORE the event, including a state this same
          // event writes and a state another relation writes at it.
          // Declaration order is therefore not observable.
          const staged: Record<string, number> = {};
          const writers = new Map<string, LoadedCommit>();
          for (const relation of firing) {
            const written = committed(machine, relation, working, inputId,
                                      landing);
            for (const identifier of Object.keys(written)) {
              const first = writers.get(identifier);
              if (first !== undefined) {
                throw twoAnswers(identifier, first, relation, inputId, landing);
              }
              writers.set(identifier, relation);
              staged[identifier] = written[identifier];
            }
          }
          Object.assign(working, staged);
          working[inputId] = landing;
          commits.push({
            relations: firing.map((relation) => relation.description),
            fraction: span === 0 ? 1 : (landing - origin) / span,
            value: landing,
            targets: { ...staged },
          });
          current = landing;
        }
        working[inputId] = clippedTarget;
        judged(levels, working, inputId, by, to);
        // Nothing above touched the bank: a request refused anywhere
        // between here and its first event committed NOTHING.
        posed(working);
        const scale = declaration.scale;
        return {
          input: inputId,
          by,
          to,
          origin,
          end: clippedTarget,
          commits,
          admitted: (clippedTarget - origin) * (scale === null ? 1 : scale),
          stops,
        };
      });
    },

    snapshot: () => ({ identity: machine.identity, bank: { ...bank } }),

    restore(state: ClockedSnapshot): void {
      if (state === null || typeof state !== 'object'
          || typeof state.identity !== 'string') {
        throw new ClockedRequestError(
          'restore() takes a bank taken by machine.snapshot().');
      }
      if (state.identity !== machine.identity) {
        throw new ClockedRequestError(
          `that snapshot was taken over the machine ${state.identity} and ` +
          `this one is ${machine.identity}. A snapshot restores into the ` +
          'machine it was taken from: its drivers, its states and its ' +
          'relations are what its bank means.');
      }
      posed({ ...state.bank });
    },

    reset(): void {
      posed({ ...machine.initial });
    },

    trigger(name: string): ClockedRequest {
      // The producer's own verb, mirrored where the producer put it
      // (`Sim.trigger` under a clocked root): resolve the instruction,
      // take its ONE entry, and delegate to `move`. Nothing converts,
      // rounds or clamps on the way -- `move` performs the one
      // `native()` conversion -- so the half-to-even agreement is
      // inherited rather than re-stated.
      const instruction = machine.instructions[name];
      if (instruction === undefined) {
        const declared = Object.keys(machine.instructions).sort()
          .map((one) => `'${one}'`).join(', ') || 'none';
        throw new ClockedRequestError(
          `trigger('${name}') names no declared instruction of this ` +
          `machine; declared: ${declared}.`);
      }
      // ONE driver, and exactly one form: the producer's compile refused
      // every other arity before this document existed, and this
      // viewer's loader refuses a document carrying one (design §10).
      const relative = instruction.by !== undefined;
      const stated = (relative ? instruction.by : instruction.targets) as
        Record<string, number>;
      const [inputId, amount] = Object.entries(stated)[0];
      return this.move(inputId, relative ? { by: amount } : { to: amount });
    },

    step(): never {
      throw new ClockedRequestError(
        'step() asks this machine to integrate a tick. A clocked machine ' +
        'has no cadence: it has a few retained values, closed-form ' +
        'positions between events, and a commit at each event. Move a ' +
        'driver instead.');
    },

    rate(inputId: string): never {
      throw new ClockedRequestError(
        `rate('${inputId}', ...) asks this machine for a continuing ` +
        'velocity. A clocked machine has no cadence for one to run in: ' +
        'every gesture is ONE request on a straight path. Move a driver ' +
        'instead.');
    },
  };
}
