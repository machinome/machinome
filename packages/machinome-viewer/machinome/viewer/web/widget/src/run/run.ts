/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// What owns a running document's coordinates (`simulation/run.py`'s
// `class Run`, reproduced function for function, minus the tree binding
// -- there is no tree here, only a bank).
//
// The tick's path is integrated by exactly one pass over the whole
// stretch. If that would take a banked coordinate outside a declared
// bound, and FURTHER outside than it stood at the stretch's start, the
// bound is a physical stop: the fraction `t*` at which the coordinate
// reaches it is located, the stretch is re-integrated over `[0, t*]`
// only, the coordinate is committed AT its bound, every input whose
// movement pushes it is stopped for the rest of the tick, and what
// remains is examined again. The earliest `t*` is always taken first.
//
// The tick stays ATOMIC across its segments: the bank, the commands'
// admitted travel and the three records are STAGED and applied only when
// every segment has succeeded.

import { toNative } from '../drivers';
import {
  ExpressionPath, UnsupportedPathNode, calleeName, expressionGeneration,
  structureOf, withExpressions,
} from '../expressions';
import type { NodeId } from '../expressions';
import { ManifestDriver, ManifestInstruction } from '../types';
import { Command, CommandRecord } from './commands';
import { edgeCuts, edgeIncrements, edgeValues, predictsOf } from './edges';
import { CrossingRecord, nextAfter } from './jumps';
import { Motion, propagations } from './motion';
import {
  Constraint, evaluateExpression, LandingInvariantError, ProgramBound,
  ProgramEdge, RunConflict, StopInvariantError, TooManyCrossings,
  UnsupportedLaw,
} from './program';
import type { LoadedProgram } from './program';
import { withProfileIntegrationCache } from './profiles';

/** One declared bound reached inside one tick.
 *
 * A stop is a BOUND OF A COORDINATE, which stops motion; a crossing is a
 * JUMP SURFACE of a law, which moves nothing. They answer different
 * questions and live in different rings. */
export interface StopRecord {
  tick: number;
  coordinate: string;
  bound: 'low' | 'high';
  value: number;
  t: number;
  inputs: string[];
  /** Absent for legacy/command-only stops; never mixed into inputs. */
  time_drives?: string[];
}

export interface TrajectoryEntry {
  tick: number;
  bank: Record<string, number>;
}

/** A running document's whole state, as a value. Carries the compiled
 * program's IDENTITY rather than the program, so restoring it into a
 * machine whose kinematics have moved on is refused rather than
 * silently wrong. */
export interface RunState {
  program: string;
  dt: number;
  tick: number;
  bank: Record<string, number>;
  commands: CommandRecord[];
}

export interface MoveRequest {
  by?: number;
  to?: number;
  duration?: number;
}

/** The bound's moving reads for one traced search. Exported only for the
 * viewer's exact signed-zero and non-affine motion regression tests. */
export function movingConstraintReads(
  reads: readonly string[], paths: ReadonlyMap<string, Motion> | undefined,
  held: Record<string, number>, deltas: Record<string, number>,
): ReadonlySet<string> {
  return new Set(reads.filter((read) => {
    const path = paths?.get(read);
    if (path !== undefined) {
      return !path.constant || !Object.is(path.start, path.end);
    }
    const delta = deltas[read] ?? 0;
    return delta !== 0 || !Object.is(held[read] + delta * 0,
                                    held[read] + delta);
  }));
}

/** One bound this stretch reaches: the coordinate, the side, the bound
 * itself -- a NUMBER, or the `Constraint` for a bound that reads other
 * coordinates -- and, for a constraint, the bracket the search already
 * located, which `eventOf` uses instead of calling `locate`. */
interface ConstraintContact {
  readonly inside: number;
  readonly outside: number;
}
type Reached = [string, 'low' | 'high', number | Constraint, ConstraintContact | null];
type Located = [number, string, 'low' | 'high', number | Constraint, ConstraintContact | null];

type Bounds = [string, number | Constraint | null,
               number | Constraint | null][];

/** Successful prefix propagations only for one reached-Bounds stretch. */
type PrefixReplays = {
  edges: readonly ProgramEdge[];
  deterministic: boolean | undefined;
  samples: Map<number, { deltas: Record<string, number>; landings: Record<string, number> }>;
}[];

/** A Follow's source certificate permits affine constant calls, so a
 * constant-shaped `random(1)` still needs an explicit stateful-call guard. */
function deterministicFollowPrefix(program: LoadedProgram,
                                   edges: readonly ProgramEdge[]): boolean {
  // The producer's first Follow contract admits affine ordinary-law
  // ancestry and one terminal retained output; leave all other shapes
  // on the original replay path, even if they happen to share edges.
  if (edges.length === 0 || edges[edges.length - 1].kind !== 'follow'
      || !edges.slice(0, -1).every(edge => edge.kind === 'law')) return false;
  const bindings = program.bindings.roots() ?? new Map<string, NodeId>();
  const seen = new Set<NodeId>();
  const safe = (id: NodeId): boolean => {
    if (seen.has(id)) return true;
    seen.add(id);
    const node = structureOf(id);
    if (node.kind === 'call') {
      const name = calleeName(id);
      if (name === null || name === 'random' || bindings.has(name)) return false;
    }
    if (node.kind === 'name' && node.name !== null) {
      const head = node.name.split('.')[0];
      const binding = bindings.get(head);
      if (binding !== undefined) {
        if (head !== node.name || !safe(binding)) return false;
      }
    }
    return node.children.every(safe);
  };
  const safeText = (expression: string | null): boolean =>
    expression === null || safe(program.nodeOf(expression));
  const safePlan = (plan: ProgramEdge['lowerPlan']): boolean =>
    plan === null || (safeText(plan.skeleton)
      && plan.jumps.every(jump => safeText(jump.level)));
  return edges.every(edge => edge.expressions.every(safeText) && edge.plans.every(safePlan)
    && safeText(edge.lower) && safeText(edge.upper)
    && safePlan(edge.lowerPlan) && safePlan(edge.upperPlan));
}

function isConstraint(bound: number | Constraint | null):
bound is Constraint {
  return bound !== null && typeof bound === 'object';
}

/** A bounded ring of the most recent entries, or nothing at all. */
class Ring<T> {
  private entries: T[] = [];

  constructor(private readonly limit: number) {}

  push(entry: T): void {
    this.entries.push(entry);
    if (this.entries.length > this.limit) this.entries.shift();
  }

  extend(entries: readonly T[]): void {
    for (const entry of entries) this.push(entry);
  }

  clear(): void {
    this.entries = [];
  }

  list(): T[] {
    return [...this.entries];
  }
}

function ringOf<T>(record: number | null): Ring<T> | null {
  if (record === null || record === undefined) return null;
  if (!Number.isInteger(record) || record < 1) {
    throw new Error(
      `record=${record} is not a number of ticks to keep. Recording is ` +
      'explicit and bounded: no record keeps nothing, and a record of N ' +
      'keeps a ring of the most recent N ticks.');
  }
  return new Ring<T>(record);
}

/** A located fraction, held inside the stretch it was located on. */
function clamped(t: number): number {
  if (t < 0) return 0;
  return t > 1 ? 1 : t;
}

/** Python's `round`: half to EVEN, which is not `Math.round`. */
function roundHalfToEven(value: number): number {
  const floor = Math.floor(value);
  const rest = value - floor;
  if (rest > 0.5) return floor + 1;
  if (rest < 0.5) return floor;
  return floor % 2 === 0 ? floor : floor + 1;
}

export class Run {
  private bank: Record<string, number>;
  private ticks = 0;
  private readonly active = new Map<string, Command>();
  private readonly ring: Ring<TrajectoryEntry> | null;
  private readonly crossingRing: Ring<CrossingRecord> | null;
  private readonly stopRing: Ring<StopRecord> | null;
  private readonly bankKeys: Set<string>;
  private readonly spans: [string, ProgramBound, ProgramBound][];
  private readonly initial: RunState;
  /** One successful finite search path per declared constraint, never shared
   * across runs or retained through restore. */
  private readonly boundPaths = new Map<Constraint, {
    path: ExpressionPath;
    moving: ReadonlySet<string>;
    generation: number;
  }>();

  constructor(readonly program: LoadedProgram, readonly dt: number,
              record: number | null = null) {
    if (!Number.isFinite(dt) || dt <= 0) {
      throw new Error(
        `dt=${dt} is not a step size. The step size is a positive number ` +
        'of simulated seconds per tick.');
    }
    this.ring = ringOf<TrajectoryEntry>(record);
    // A second ring of the same length for the CROSSINGS located inside
    // a tick, and a third for the STOPS. No record builds none of them,
    // so a run that records nothing pays nothing for the record.
    this.crossingRing = ringOf<CrossingRecord>(record);
    this.stopRing = ringOf<StopRecord>(record);
    this.bank = { ...program.initial };
    this.bankKeys = new Set(program.order);
    this.spans = Object.entries(program.spans).map(
      ([id, span]) => [id, span.low, span.high]);
    this.initial = this.snapshot();
  }

  // ------------------------------------------------------------------
  // What a caller reads

  tick(): number {
    return this.ticks;
  }

  /** The elapsed simulation seconds: computed from the integer tick
   * count on every access, never accumulated, so it is the exact instant
   * the run stands at. */
  clock(): number {
    return this.ticks * this.dt;
  }

  state(): Record<string, number> {
    const found: Record<string, number> = {};
    for (const id of Object.keys(this.bank).sort()) found[id] = this.bank[id];
    return found;
  }

  /** The bank as a positional array in the program's own id order, which
   * is what a frame message carries. */
  positions(): Float64Array<ArrayBufferLike> {
    const found = new Float64Array(this.program.order.length);
    this.program.order.forEach((id, index) => { found[index] = this.bank[id]; });
    return found;
  }

  commands(): Command[] {
    return [...this.active.values()];
  }

  trajectory(): TrajectoryEntry[] {
    return this.ring === null ? [] : this.ring.list();
  }

  crossings(): CrossingRecord[] {
    return this.crossingRing === null ? [] : this.crossingRing.list();
  }

  stops(): StopRecord[] {
    return this.stopRing === null ? [] : this.stopRing.list();
  }

  // ------------------------------------------------------------------
  // Requests

  /** A duration in seconds as a whole number of ticks. */
  ticksFor(value: number, what: string): number {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      throw new Error(`${what} ${value} is not a number of seconds.`);
    }
    const count = roundHalfToEven(value / this.dt);
    if (Math.abs(count * this.dt - value) > 1e-9) {
      throw new Error(
        `${what} ${value} is not a whole number of dt=${this.dt} ticks.`);
    }
    return count;
  }

  move(inputId: string, request: MoveRequest = {}): Command {
    const declaration = this.declarationOf(inputId);
    const { by, to, duration } = request;
    if ((by === undefined || by === null)
        === (to === undefined || to === null)) {
      throw new Error(
        `move('${inputId}', ...) states exactly one of by= (how far to ` +
        'travel) and to= (where to land), both in design units; got ' +
        `by=${by} and to=${to}.`);
    }
    const value = this.bank[inputId];
    const target = to !== undefined && to !== null
      ? toNative(to, declaration) : undefined;
    const native = target !== undefined
      ? target - value
      : toNative(by as number, declaration);
    const ticks = this.ticksFor(duration ?? 0,
                                `duration of the move on '${inputId}'`);
    this.claim(inputId);
    const command = new Command(inputId, 'move', declaration, this.ticks,
                                { native, target, ticks, value });
    this.active.set(inputId, command);
    if (!ticks) {
      // A zero-duration move settles at the CURRENT tick, without
      // advancing the clock.
      this.integrate(this.ticks, false, command);
    }
    return command;
  }

  rate(inputId: string, rate: number): Command | null {
    const declaration = this.declarationOf(inputId);
    if (rate === 0) {
      const running = this.active.get(inputId);
      if (running === undefined || running.kind !== 'rate') return null;
      running.status = 'completed';
      this.active.delete(inputId);
      return running;
    }
    this.claim(inputId);
    const nativeRate = declaration.scale === null
      || declaration.scale === undefined ? rate : rate / declaration.scale;
    const command = new Command(inputId, 'rate', declaration, this.ticks,
                                { nativeRate });
    this.active.set(inputId, command);
    return command;
  }

  /** A declared instruction: its targets as moves TO, its travels as
   * moves BY -- every input claimed before any command starts, so an
   * ownership conflict refuses the whole instruction and leaves nothing
   * running. */
  trigger(name: string): Command[] {
    const instruction = this.program.instructions[name] as
      (ManifestInstruction & { by?: Record<string, number> }) | undefined;
    if (instruction === undefined) {
      const known = Object.keys(this.program.instructions).sort().join(', ')
        || 'none';
      throw new Error(
        `no instruction '${name}' in this document; declared: ${known}`);
    }
    const relative = instruction.by !== undefined;
    const stated = (relative ? instruction.by : instruction.targets) as
      Record<string, number>;
    for (const inputId of Object.keys(stated)) {
      this.declarationOf(inputId);
      this.claim(inputId);
    }
    const issued: Command[] = [];
    for (const [inputId, amount] of Object.entries(stated)) {
      issued.push(relative
        ? this.move(inputId, { by: amount, duration: instruction.duration })
        : this.move(inputId, { to: amount, duration: instruction.duration }));
    }
    return issued;
  }

  cancel(inputId: string): Command | null {
    const command = this.active.get(inputId);
    if (command === undefined) return null;
    command.cancel();
    this.active.delete(inputId);
    return command;
  }

  private claim(inputId: string): void {
    const owner = this.active.get(inputId);
    if (owner !== undefined) {
      throw new Error(
        `'${inputId}' is already owned by a ${owner.kind} command. An input ` +
        'has one owner at a time: cancel that command, or release the rate ' +
        'with rate(input, 0), before asking for another.');
    }
  }

  private declarationOf(inputId: string): ManifestDriver {
    const declaration = this.program.drivers[inputId];
    if (declaration === undefined) {
      const known = Object.keys(this.program.drivers).sort().join(', ')
        || 'none';
      throw new Error(
        `'${inputId}' is not a declared input of this document. Only a ` +
        'declared input can be moved -- a joint coordinate is what a ' +
        `relation moves, not what a command does; the declared inputs ` +
        `are: ${known}.`);
    }
    return declaration;
  }

  // ------------------------------------------------------------------
  // The tick

  advance(): void {
    this.integrate(this.ticks + 1, true);
  }

  integrate(tick: number, advance: boolean, only: Command | null = null): void {
    if (this.program.profiles === undefined) {
      withExpressions(() => this.integrateScoped(tick, advance, only));
    } else {
      withProfileIntegrationCache(this.program.profiles,
        () => withExpressions(() => this.integrateScoped(tick, advance, only)));
    }
  }

  private integrateScoped(tick: number, advance: boolean, only: Command | null): void {
    const admissions: Record<string, number> = {};
    for (const [inputId, command] of this.active) {
      admissions[inputId] = (only !== null && command !== only)
        ? 0 : command.admits(tick, this.dt);
    }
    const moved: Command[] = [];
    for (const inputId of Object.keys(admissions)) {
      if (admissions[inputId]) moved.push(this.active.get(inputId)!);
    }
    for (const id of this.program.timeDrives) admissions[id] = advance ? this.dt : 0;

    // Each bound as a number for THIS tick, from the committed bank,
    // before any segment: every segment of one tick is measured against
    // the same number.
    const bounds = this.boundsNow();
    let staged = this.bank;
    const admitted: Record<string, number> = {};
    for (const inputId of Object.keys(admissions)) admitted[inputId] = 0;
    let stopped = new Set<string>();
    // Fresh lists per tick, appended to the rings only on COMMIT, so a
    // refused tick records nothing.
    const crossings: CrossingRecord[] | null =
      this.crossingRing === null ? null : [];
    const stops: StopRecord[] | null = this.stopRing === null ? null : [];
    // Every stop event stops at least one moving admission, and a stopped
    // admission stays stopped for this tick. Count both operator inputs and
    // independent time drives in the finite event limit.
    const limit = moved.length + (advance ? this.program.timeDrives.length : 0);
    let start = 0;
    let events = 0;

    try {
      for (;;) {
        const stretch = 1 - start;
        const scaled = this.scaled(admissions, stopped, stretch);
        const values = this.valuesOf(staged, admitted);
        let deltas = this.deltasOf(scaled);
        let found: CrossingRecord[] | null = crossings === null ? null : [];
        let landings: Record<string, number> = {};
        // Keep the old delta/ramp for every interior fraction. The explicit
        // target is visible only at the full terminal endpoint, before any
        // bound is tested; a later stopped segment is replayed without it.
        const trace = propagations.get(deltas)!;
        for (const [inputId, command] of this.active) {
          const target = command.targetNative;
          if (target === undefined || stopped.has(inputId) || !command.finished(tick)
              || (only !== null && command !== only)) continue;
          if (Object.is(staged[inputId] + (scaled[inputId] ?? 0), target)) continue;
          trace.terminals ??= new Map();
          trace.terminals.set(inputId, target);
          const startValue = values[inputId];
          const delta = scaled[inputId] ?? 0;
          trace.motions.set(inputId, new Motion(startValue, target,
            [[0, 1, t => startValue + delta * t]], true, true));
          landings[inputId] = target;
        }
        this.pass(values, deltas, found, tick, landings);
        let committed: Record<string, number> = {};
        for (const id of Object.keys(staged)) {
          committed[id] = staged[id] + (deltas[id] ?? 0);
        }
        this.landed(committed, landings);
        const reached = this.reachedBounds(staged, committed, bounds,
                                           values, scaled, deltas);
        if (reached.length === 0) {
          record(crossings, found, start, 1);
          staged = committed;
          for (const inputId of Object.keys(scaled)) {
            admitted[inputId] += scaled[inputId];
          }
          break;
        }

        events += 1;
        if (events > limit) {
          throw new StopInvariantError(this.runaway(reached, limit));
        }
        const event = this.eventOf(reached, staged, values, deltas);
        const where = event[0][0];
        const boundary = start + where * stretch;

        const segment: Record<string, number> = {};
        for (const inputId of Object.keys(scaled)) {
          segment[inputId] = scaled[inputId] * where;
        }
        deltas = this.deltasOf(segment);
        found = crossings === null ? null : [];
        landings = {};
        this.pass(values, deltas, found, tick, landings);
        committed = {};
        for (const id of Object.keys(staged)) {
          committed[id] = staged[id] + (deltas[id] ?? 0);
        }
        this.landed(committed, landings);

        const blocked = new Set<string>();
        for (const [, identifier, side, bound, contact] of event) {
          let value: number;
          let group: string[];
          if (isConstraint(bound)) {
            // NOTHING to snap to -- the bound at `t*` is on one side of
            // a step or the other, and the coordinate that stopped may
            // not have moved at all -- and nothing to snap FOR: the
            // sample arithmetic IS the segment arithmetic, so the
            // committed state satisfies the bound by construction.
            // Asserted below rather than trusted.
            value = this.constraintBound(bound, committed);
            group = this.constraintGroup(bound, scaled, values, staged, contact!);
          } else {
            // AT the bound, exactly. The localization's own error is
            // absorbed here rather than left to raise later.
            committed[identifier] = bound;
            value = bound;
            group = this.groupOf(identifier, scaled, values);
          }
          for (const inputId of group) blocked.add(inputId);
          if (stops !== null) {
            const timeDrives = group.filter(id => this.program.timeDrives.includes(id)).sort();
            stops.push({
              tick, coordinate: identifier, bound: side, value,
              t: boundary, inputs: group.filter(id => this.program.inputs.includes(id)).sort(),
              ...(timeDrives.length ? { time_drives: timeDrives } : {}),
            });
          }
        }
        // A SECOND loop, after every entry's group and record: a
        // numeric snap on another entry of the same event mutates
        // `committed`, and the assertion must see the state the segment
        // actually commits (design D6).
        for (const [, , , bound] of event) {
          if (isConstraint(bound)) this.assertInside(bound, committed);
        }
        if (blocked.size === 0) {
          throw new StopInvariantError(this.runaway(reached, limit));
        }

        record(crossings, found, start, boundary);
        staged = committed;
        for (const inputId of Object.keys(segment)) {
          admitted[inputId] += segment[inputId];
        }
        stopped = new Set([...stopped, ...blocked]);
        start = boundary;
      }
    } catch (error) {
      if (error instanceof RunConflict || error instanceof TooManyCrossings
          || error instanceof UnsupportedLaw
          || error instanceof StopInvariantError
          || error instanceof LandingInvariantError) {
        // A tick that fails commits nothing, every segment of it
        // included.
        this.refuse(moved);
      }
      throw error;
    }

    // Nothing above committed anything. From here the tick is taken.
    this.bank = staged;
    if (advance) this.ticks = tick;
    for (const inputId of Object.keys(admitted)) {
      const command = this.active.get(inputId);
      if (command !== undefined) command.admittedNative += admitted[inputId];
    }
    this.block(stopped);
    for (const [inputId, command] of [...this.active]) {
      if (only !== null && command !== only) {
        // A zero-duration move is one EXTRA pass at the current tick: it
        // must not retire a command whose own tick has not been admitted
        // in it.
        continue;
      }
      if (command.finished(tick)) {
        command.status = 'completed';
        this.active.delete(inputId);
      }
    }
    if (this.ring !== null) {
      this.ring.push({ tick: this.ticks, bank: { ...this.bank } });
      this.crossingRing!.extend(crossings!);
      this.stopRing!.extend(stops!);
    }
  }

  /** A coordinate whose own law READ it and whose walk took at least one
   * cut is committed at the value that walk LEFT it at.
   *
   * `value + delta` is not enough on its own: `x + (y - x) !== y` for
   * about six pairs of floats in a hundred, so an exact landing inside
   * the plan would still be a ulp out in the bank the next tick starts
   * from -- and a ulp back toward the surface is the ENGAGED side of the
   * gate. Applied where the segment already writes an absolute value for
   * a stop, and BEFORE the stops are located, so a stop on the same
   * coordinate in the same segment overwrites it: a physical bound is a
   * bound of the coordinate itself. */
  private landed(committed: Record<string, number>,
                 landings: Record<string, number>): void {
    for (const key of Object.keys(landings)) committed[key] = landings[key];
  }

  /** ONE propagation over the compiled program, over whatever stretch
   * `deltas` describes. Mutates and returns `deltas`; raises rather than
   * retiring anything, because a segment is not a tick. */
  private pass(values: Record<string, number>,
               deltas: Record<string, number>,
               found: CrossingRecord[] | null,
               tick: number,
               landings: Record<string, number> | null = null):
  Record<string, number> {
    const determined = new Set<string>();
    for (const edge of this.program.edges) {
      if (edge.kind === 'check') {
        const predicted = predictsOf(edge, deltas, 0);
        const received = deltas[edge.slot as string];
        if (!this.agree(predicted, received)) {
          throw new RunConflict(this.conflict(edge, predicted, received));
        }
        continue;
      }
      for (const [key, delta] of edgeIncrements(this.program, edge, values,
                                                deltas, found, tick,
                                                landings)) {
        if (determined.has(key) && !this.agree(deltas[key], delta)) {
          throw new RunConflict(this.disagreement(edge, key, delta));
        }
        deltas[key] = delta;
        determined.add(key);
      }
    }
    return deltas;
  }

  private agree(left: number, right: number): boolean {
    return Math.abs(left - right) <= this.program.limits.agreement
      * Math.max(1, Math.abs(left), Math.abs(right));
  }

  /** Each input's admission over one stretch: nothing for a stopped
   * input, and the tick's own admission UNTOUCHED over a full stretch,
   * so an unsegmented tick is the arithmetic it always was. */
  private scaled(admissions: Record<string, number>, stopped: Set<string>,
                 stretch: number): Record<string, number> {
    const found: Record<string, number> = {};
    for (const inputId of Object.keys(admissions)) {
      if (stopped.has(inputId)) found[inputId] = 0;
      else if (stretch === 1) found[inputId] = admissions[inputId];
      else found[inputId] = admissions[inputId] * stretch;
    }
    return found;
  }

  private deltasOf(admissions: Record<string, number>): Record<string, number> {
    const deltas: Record<string, number> = {};
    propagations.set(deltas, {
      motions: new Map(), untraced: new Set(),
      demanded: new Set([
        ...this.program.edges.flatMap(edge => edge.needs.filter(key => !edge.gives.includes(key))),
        ...[...this.program.constraints.values()].flatMap(bound => bound.reads),
      ]),
    });
    for (const id of this.program.order) deltas[id] = 0;
    for (const id of this.program.intermediates) deltas[id] = 0;
    for (const id of this.program.timeDrives) deltas[id] = 0;
    for (const inputId of Object.keys(admissions)) {
      if (admissions[inputId]) deltas[inputId] = admissions[inputId];
    }
    return deltas;
  }

  /** The bank, plus every computed value the program derives from it:
   * recomputed here rather than stored. */
  private valuesOf(bank: Record<string, number>,
                   admitted: Record<string, number> = {}): Record<string, number> {
    const values: Record<string, number> = { ...bank };
    for (const id of this.program.timeDrives) values[id] = this.clock() + (admitted[id] ?? 0);
    for (const edge of this.program.edges) {
      if (edge.gives.every((key) => this.bankKeys.has(key))) {
        // Nothing this edge computes is a computed value, so its values
        // were computed here and discarded. Skipping it is
        // behaviour-neutral and removes one evaluation per law per tick.
        continue;
      }
      for (const [key, value] of edgeValues(this.program, edge, values)) {
        if (!this.bankKeys.has(key)) values[key] = value;
      }
    }
    return values;
  }

  // ------------------------------------------------------------------
  // Stops

  /** Every banked coordinate that ends the stretch OUTSIDE a bound and
   * FURTHER outside than it began it. A coordinate already at or below
   * its low bound that moves UP is free, and one that does not move at
   * all is free. */
  private reachedBounds(held: Record<string, number>,
                        committed: Record<string, number>,
                        bounds: Bounds,
                        values: Record<string, number>,
                        admissions: Record<string, number>,
                        deltas: Record<string, number>): Reached[] {
    const found: Reached[] = [];
    const prefixReplays: PrefixReplays = [];
    for (const [identifier, low, high] of bounds) {
      const value = committed[identifier];
      const was = held[identifier];
      for (const [side, bound] of
        [['low', low], ['high', high]] as [('low' | 'high'),
                                           number | Constraint | null][]) {
        if (!isConstraint(bound)) continue;
        const followPath = propagations.get(deltas)?.followCuts?.has(identifier) ?? false;
        if (!followPath && bound.reads.every((read) => committed[read] === held[read])) {
          // Nothing the bound READS moves over this stretch, so the
          // bound is a NUMBER for it -- its expression at the tick's
          // committed own value and the reads' standing values -- and
          // the coordinate is stopped or freed exactly as a bound over
          // its own value alone is, at the cost of one evaluation
          // rather than `subdivisions` sub-program passes.
          if (value === was) continue;
          const number = this.constraintBound(bound, held);
          if (side === 'low' && value < number && value < was) {
            found.push([identifier, 'low', number, null]);
          } else if (side === 'high' && value > number && value > was) {
            found.push([identifier, 'high', number, null]);
          }
          continue;
        }
        const located = this.constraintReached(
          bound, held, committed, values, admissions, deltas, prefixReplays);
        if (located !== null) found.push([identifier, side, bound, located]);
      }
      const plainLow = isConstraint(low) ? null : low;
      const plainHigh = isConstraint(high) ? null : high;
      if (plainLow !== null && value < plainLow && value < was) {
        found.push([identifier, 'low', plainLow, null]);
      } else if (plainHigh !== null && value > plainHigh && value > was) {
        found.push([identifier, 'high', plainHigh, null]);
      }
    }
    return found;
  }

  // ------------------------------------------------------------------
  // A bound that reads other coordinates: the CONSTRAINT (design D4-D6)

  /** The fraction of the stretch at which `constraint` is first carried
   * outward, or `null`.
   *
   * DETECTION AND LOCALIZATION ARE ONE PROCEDURE, and it looks INSIDE
   * the stretch: a constraint over moving reads can be violated inside
   * a stretch and satisfied again at its end, and a test at the ends
   * alone commits all of them.
   *
   * A constraint is examined only when something it depends on MOVES, so
   * a stretch in which the bounded coordinate and every read stand still
   * evaluates nothing at all. */
  private constraintReached(constraint: Constraint,
                            held: Record<string, number>,
                            committed: Record<string, number>,
                            values: Record<string, number>,
                            admissions: Record<string, number>,
                            deltas: Record<string, number>,
                            prefixReplays?: PrefixReplays): ConstraintContact | null {
    const keys = [constraint.identifier, ...constraint.reads];
    const followPath = propagations.get(deltas)?.followCuts?.has(constraint.identifier) ?? false;
    if (!followPath && keys.every((key) => committed[key] === held[key])) return null;
    return this.searchedConstraint(constraint, held, values, admissions, deltas,
                                   prefixReplays);
  }

  /** The level sampled at `subdivisions` fractions of the stretch,
   * stopped at the FIRST sample carried outward, and the crossing
   * bisected to `crossingTolerance`.
   *
   * `t*` is the INSIDE end of the final bracket -- the last fraction at
   * which the bound is satisfied -- not its midpoint: a bound that reads
   * other coordinates carries a comparison in every sighting, and a
   * level with a jump in it is what the search is for. Retain the outside
   * end too: attribution uses this contact, not a later free endpoint. */
  private searchedConstraint(constraint: Constraint,
                             held: Record<string, number>,
                             values: Record<string, number>,
                             admissions: Record<string, number>,
                             deltas: Record<string, number>,
                             prefixReplays?: PrefixReplays):
  ConstraintContact | null {
    const own = this.bank[constraint.identifier];
    const paths = propagations.get(deltas)?.motions;
    const keys = [constraint.identifier, ...constraint.reads];
    const determined = paths && keys.every(key => paths.has(key) || !this.program.determiner.has(key));
    // The first sample binds the expression's standing graph. Later samples
    // read only nodes depending on an actually moving path. A constant Motion
    // can still have opposite signed-zero cached endpoints: comparing its
    // start/end with Object.is keeps that read in the moving cone.
    const moving = determined
      ? movingConstraintReads(constraint.reads, paths, held, deltas) : null;
    const prior = this.boundPaths.get(constraint);
    const reusable = moving !== null && prior !== undefined
      && prior.generation === expressionGeneration()
      && prior.moving.size === moving.size
      && [...moving].every((name) => prior.moving.has(name));
    if (!determined || !reusable) this.boundPaths.delete(constraint);
    let boundPath: ExpressionPath | null = null;
    let cacheable = false;
    let pathBound = false;
    let pathDisabled = false;
    const level = (t: number): number => {
      if (!determined) return this.constraintLevel(constraint, held, values, admissions,
                                                   t, own, prefixReplays);
      const at = (key: string) => paths.get(key)?.at(t) ?? held[key] + (deltas[key] ?? 0) * t;
      const scope: Record<string, number> = { [constraint.identifier]: own };
      for (const read of constraint.reads) scope[read] = at(read);
      let finite = Number.isFinite(own);
      for (const read of constraint.reads) {
        if (!Number.isFinite(scope[read])) finite = false;
      }
      if (pathBound && !finite) cacheable = false;
      let bound: number;
      if (pathDisabled) {
        bound = evaluateExpression(this.program, constraint.expression, scope);
      } else {
        try {
          if (!pathBound) {
            cacheable = finite;
            if (!cacheable) this.boundPaths.delete(constraint);
            boundPath = reusable && cacheable ? prior!.path
              : new ExpressionPath(constraint.expression, moving!,
                                   this.program.bindings.roots);
          }
          bound = Number(pathBound ? boundPath!.at(scope)
            : boundPath!.bind(scope, reusable && cacheable));
          pathBound = true;
        } catch (error) {
          if (!(error instanceof UnsupportedPathNode)) throw error;
          pathDisabled = true;
          this.boundPaths.delete(constraint);
          bound = evaluateExpression(this.program, constraint.expression, scope);
        }
      }
      const value = at(constraint.identifier);
      return constraint.side === 'high' ? value - bound : bound - value;
    };
    const finish = (contact: ConstraintContact | null): ConstraintContact | null => {
      if (cacheable && pathBound && !pathDisabled && boundPath?.reusableStanding()) {
        this.boundPaths.set(constraint, {
          path: boundPath, moving: moving!, generation: expressionGeneration(),
        });
      }
      return contact;
    };
    try {
      const start = level(0);
      const outward = (here: number): boolean => here > 0 && here > start;
      const subdivisions = this.program.limits.subdivisions;
      const trace = propagations.get(deltas);
      const followCuts = trace?.followCuts?.get(constraint.identifier);
      const closureRows = trace?.followClosures?.get(constraint.identifier) ?? [];
      const closures = new Map(closureRows.map(([where, value, low, high]) =>
        [where, constraint.side === 'low' ? low - value : value - high]));
      const samples = followCuts === undefined
        ? Array.from({ length: subdivisions }, (_unused, index) => (index + 1) / subdivisions)
        : [...new Set([
          ...Array.from({ length: subdivisions }, (_unused, index) => (index + 1) / subdivisions),
          ...followCuts.filter(cut => cut > 0),
          ...followCuts.filter(cut => cut > 0).map(cut => nextAfter(cut, -Infinity)),
        ])].sort((a, b) => a - b);
      let previous = 0;
      for (const where of samples) {
        const here = level(where);
        if (closures.has(where) && outward(closures.get(where)!)) {
          const before = nextAfter(where, -Infinity);
          if (!outward(here) && !outward(level(before))) {
            throw new UnsupportedLaw(`${constraint.identifier} Follow envelope has a positive ` +
              `one-sided ${constraint.side} Bound level at ${where}, but no representable ` +
              'neighbor brackets that contact. The tick was not committed.');
          }
        }
        if (!outward(here)) {
          previous = where;
          continue;
        }
        let low = previous;
        let high = where;
        for (let round = 0; round < this.program.limits.bisectionRounds;
          round += 1) {
          if (high - low <= this.program.limits.crossingTolerance) break;
          const middle = (low + high) / 2;
          if (outward(level(middle))) high = middle;
          else low = middle;
        }
        return finish({ inside: low, outside: high });
      }
      return finish(null);
    } catch (error) {
      this.boundPaths.delete(constraint);
      throw error;
    }
  }

  /** The CONSTRAINT LEVEL at the fraction `t` of the stretch: outside is
   * positive.
   *
   * One pass over the bound's SUB-PROGRAM with every admission scaled by
   * `t`, on a FRESH delta map -- never `pass`'s, which mutates and
   * raises. The joint's own coordinate INSIDE the bound takes the value
   * it holds in the tick's COMMITTED bank, which is what makes a
   * ratchet's tooth the tooth it started the tick on; every read takes
   * the value it has along the path. */
  private constraintLevel(constraint: Constraint,
                          held: Record<string, number>,
                          values: Record<string, number>,
                          admissions: Record<string, number>,
                          t: number, own: number,
                          prefixReplays?: PrefixReplays): number {
    const carriesFollow = constraint.edges.some((edge) => edge.kind === 'follow');
    const reusable = prefixReplays !== undefined && carriesFollow
      && Number.isFinite(t) && t !== 0;
    let group = reusable ? prefixReplays.find(entry =>
      entry.edges.length === constraint.edges.length
      && entry.edges.every((edge, index) => edge === constraint.edges[index])) : undefined;
    if (reusable && group === undefined) {
      group = {
        edges: constraint.edges,
        deterministic: undefined,
        samples: new Map(),
      };
      prefixReplays!.push(group);
    }
    const prior = group?.deterministic ? group.samples.get(t) : undefined;
    let deltas: Record<string, number>;
    let landings: Record<string, number> | null;
    if (prior !== undefined) {
      ({ deltas, landings } = prior);
    } else {
      const scaled: Record<string, number> = {};
      for (const inputId of Object.keys(admissions)) {
        scaled[inputId] = admissions[inputId] * t;
      }
      deltas = this.deltasOf(scaled);
      const carriesPlay = carriesFollow || constraint.edges.some((edge) => edge.kind === 'play');
      landings = carriesPlay ? {} : null;
      for (const edge of constraint.edges) {
        for (const [key, increment] of edgeIncrements(
          this.program, edge, values, deltas, null, 0, landings)) {
          deltas[key] = increment;
        }
      }
      if (group !== undefined && group.deterministic === undefined) {
        // The ordinary prefix gets first chance to fail. Structural
        // eligibility is only an optional optimization, so a failure in
        // that extra inspection falls back to the original evaluator.
        try {
          group.deterministic = deterministicFollowPrefix(this.program,
                                                          constraint.edges);
        } catch {
          group.deterministic = false;
        }
      }
      if (group?.deterministic) {
        group.samples.set(t, { deltas, landings: landings! });
      }
    }
    const scope: Record<string, number> = { [constraint.identifier]: own };
    for (const read of constraint.reads) {
      scope[read] = landings?.[read] ?? (held[read] + deltas[read]);
    }
    const bound = evaluateExpression(
      this.program, constraint.expression, scope);
    const value = landings?.[constraint.identifier]
      ?? (held[constraint.identifier] + deltas[constraint.identifier]);
    return constraint.side === 'high' ? value - bound : bound - value;
  }

  /** The bound EVALUATED at the committed state: the number a stop
   * records, which for a constraint is not the value the coordinate now
   * holds. The own coordinate is still the TICK's committed bank. */
  private constraintBound(constraint: Constraint,
                          committed: Record<string, number>): number {
    const scope: Record<string, number> = {
      [constraint.identifier]: this.bank[constraint.identifier],
    };
    for (const read of constraint.reads) scope[read] = committed[read];
    return evaluateExpression(this.program, constraint.expression, scope);
  }

  /** The committed state satisfies the bound by construction; this says
   * so out loud, so a broken invariant is a refused tick rather than a
   * picometre of penetration nobody reported. */
  private assertInside(constraint: Constraint,
                       committed: Record<string, number>): void {
    const bound = this.constraintBound(constraint, committed);
    const value = committed[constraint.identifier];
    const level = constraint.side === 'high' ? value - bound : bound - value;
    if (level > 0) {
      throw new StopInvariantError(
        `${constraint.identifier} was stopped by its ${constraint.side} ` +
        `bound, and at the state the segment commits that bound evaluates ` +
        `to ${bound} while the coordinate holds ${value} -- outside it by ` +
        `${level}. The sample that located the stop and the segment that ` +
        'committed it are the same arithmetic over the same edges, so ' +
        'this is a broken invariant of the run. The tick committed ' +
        'nothing.');
    }
  }

  /** The inputs a constraint stops: its own candidates -- the inputs
   * reaching the bounded coordinate OR anything it reads -- filtered by
   * whether their own admission ALONE carries the LEVEL outward across
   * the located contact bracket. Replay both sightings from the original
   * stretch origin, keeping the own argument frozen at tick start.
   *
   * One rule covers both directions: an input moving the bounded
   * coordinate against the constraint is stopped, an input moving a read
   * so as to make a STANDING position invalid is stopped where the
   * constraint becomes active, and an input moving a read so as to
   * RELIEVE it runs its full tick. */
  private constraintGroup(constraint: Constraint,
                          admissions: Record<string, number>,
                          values: Record<string, number>,
                          held: Record<string, number>,
                          contact: ConstraintContact): string[] {
    const own = this.bank[constraint.identifier];
    const found: string[] = [];
    for (const candidate of constraint.candidates) {
      const delta = admissions[candidate] ?? 0;
      if (!delta) continue;
      const alone = { [candidate]: delta };
      const before = this.constraintLevel(
        constraint, held, values, alone, contact.inside, own);
      const after = this.constraintLevel(
        constraint, held, values, alone, contact.outside, own);
      if (after - before > 0) found.push(candidate);
    }
    return found;
  }

  /** The EARLIEST stop of this stretch, with everything within the
   * crossing tolerance of it: one event, one segment boundary, the union
   * of their groups. Ties are therefore never resolved by ordering;
   * there is no ordering to get wrong. */
  private eventOf(reached: Reached[], held: Record<string, number>,
                  values: Record<string, number>,
                  deltas: Record<string, number>): Located[] {
    const located: Located[] = reached.map(
      ([identifier, side, bound, where]) => [
        where === null
          ? this.locate(identifier, side, bound as number, held, values,
                        deltas)
          : where.inside,
        identifier, side, bound, where,
      ]);
    located.sort((a, b) => (a[0] - b[0])
      || (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0)
      || (a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0));
    const first = located[0][0];
    return located.filter(
      (entry) => entry[0] - first <= this.program.limits.crossingTolerance);
  }

  /** The smallest fraction of the STRETCH at which `identifier` reaches
   * `bound`, by the framework's three cases. */
  private locate(identifier: string, side: 'low' | 'high', bound: number,
                 held: Record<string, number>, values: Record<string, number>,
                 deltas: Record<string, number>): number {
    const determination = this.program.determiner.get(identifier);
    if (determination === undefined) {
      throw new StopInvariantError(
        `${identifier} left its declared range over this tick and no ` +
        'relation determines it, so nothing can have moved it. The tick ' +
        'committed nothing.');
    }
    const { edge, index } = determination;
    const value = held[identifier];
    if (this.program.timeDrives.length
        && (this.program.sources[identifier] ?? []).some(id => this.program.timeDrives.includes(id))) {
      // A downstream affine edge does not make its upstream time path affine.
      // Locate against the same original admissions the truncated commit uses.
      return this.searchFromSources(identifier, side, bound, held, values, deltas);
    }
    // A PLAY follower may still stand at its bound while its upstream
    // clearance is being recollected. Its contact path, not the retained
    // coordinate's standing value, locates the first outward push.
    const throughPlay = this.locateThroughPlay(edge, bound, held, values,
                                               deltas);
    if (throughPlay !== null) return throughPlay;
    if (this.hasPlayAncestor(edge)) {
      return this.searchFromSources(identifier, side, bound, held, values,
                                    deltas);
    }
    if ((bound - value) * (side === 'high' ? 1 : -1) <= 0) {
      // Already at or beyond it: the stop is at the very start of the
      // stretch, and the coordinate stands where it stands.
      return 0;
    }
    const motion = propagations.get(deltas)?.motions.get(identifier);
    if (motion) {
      return motion.affine
        ? this.piecewise(edge, identifier, bound, value, values, deltas, [0, ...motion.cuts(), 1])
        : this.searched(edge, identifier, bound, value, values, deltas);
    }
    if (edge.affine[index] || edge.shapes[index] === 'kinked') {
      // AFFINE or KINKED: either way the value is piecewise affine in
      // `t` over the breakpoints `edgeCuts` gives, and the stop is
      // SOLVED there rather than searched (openspec `solve-at-the-kink`,
      // design D4 (c)). `edge.affine` is the two-valued flag the
      // document publishes and says something narrower; the shape the
      // loader derived is what this decision needs.
      const cuts = edgeCuts(this.program, edge, values, deltas, index);
      if (cuts.length === 0) {
        // Linear in `t`: one division, exact, no extra evaluation.
        const travel = deltas[identifier];
        return travel ? clamped((bound - value) / travel) : 0;
      }
      return this.piecewise(edge, identifier, bound, value, values, deltas,
                            cuts);
    }
    return this.searched(edge, identifier, bound, value, values, deltas);
  }

  /** Invert an ordinary one-source affine observer, then walk a play
   * chain's contact offsets back to its originating driver. */
  private locateThroughPlay(edge: ProgramEdge, bound: number,
                            held: Record<string, number>,
                            values: Record<string, number>,
                            deltas: Record<string, number>): number | null {
    let target = bound;
    let current = edge;
    while (current.kind !== 'play') {
      const source = current.needs[0];
      if (current.kind === 'wiring') {
        if (!current.factor) return null;
        target = values[source]
          + (target - held[current.gives[0]]) / current.factor;
      } else if (current.kind === 'law' && current.needs.length === 1
                 && current.gives.length === 1
                 && current.affine[0] && current.expressions[0] !== null) {
        const expression = current.expressions[0];
        const at0 = evaluateExpression(this.program, expression,
                                       { [source]: 0 });
        const at1 = evaluateExpression(this.program, expression,
                                       { [source]: 1 });
        const slope = at1 - at0;
        if (!slope) return null;
        target = values[source]
          + (target - held[current.gives[0]]) / slope;
      } else {
        return null;
      }
      const upstream = this.program.determiner.get(source)?.edge;
      if (upstream === undefined) return null;
      current = upstream;
    }
    for (;;) {
      const direction = deltas[current.gives[0]] > 0 ? 1 : -1;
      target += direction > 0 ? current.high as number : current.low as number;
      const source = current.needs[0];
      if (this.program.inputs.includes(source)) {
        const travel = deltas[source];
        return travel ? clamped((target - held[source]) / travel) : 0;
      }
      const upstream = this.program.determiner.get(source)?.edge;
      if (upstream === undefined || upstream.kind !== 'play') {
        throw new StopInvariantError(
          `${edge.description} lost its driver-rooted play prefix while ` +
          'locating a stop. The tick committed nothing.');
      }
      current = upstream;
    }
  }

  private hasPlayAncestor(edge: ProgramEdge): boolean {
    const pending: ProgramEdge[] = [edge];
    const seen = new Set<ProgramEdge>();
    while (pending.length > 0) {
      const current = pending.pop()!;
      if (seen.has(current)) continue;
      if (current.kind === 'play') return true;
      seen.add(current);
      for (const need of current.needs) {
        const upstream = this.program.determiner.get(need)?.edge;
        if (upstream !== undefined) pending.push(upstream);
      }
    }
    return false;
  }

  /** Replay the original operator and time admissions while searching a
   * nonlinear path or play observer. A departure from an exact-bound plateau
   * toward the inside is free; only the later outward departure is a stop. */
  private searchFromSources(identifier: string, side: 'low' | 'high',
                            bound: number, held: Record<string, number>,
                            values: Record<string, number>,
                            deltas: Record<string, number>): number {
    const level = (where: number): number => {
      const scaled: Record<string, number> = {};
      for (const input of [...this.program.inputs, ...this.program.timeDrives]) {
        scaled[input] = (deltas[input] ?? 0) * where;
      }
      const replay = this.deltasOf(scaled);
      const landings: Record<string, number> = {};
      this.pass(values, replay, null, 0, landings);
      return (landings[identifier]
        ?? (held[identifier] + (replay[identifier] ?? 0))) - bound;
    };
    const outward = (value: number) => side === 'high' ? value > 0 : value < 0;
    const steps = this.program.limits.subdivisions;
    let low = 0;
    let below = level(0);
    for (let step = 1; step <= steps; step += 1) {
      const high = step / steps;
      const above = level(high);
      if (!outward(below) && outward(above)) {
        let left = low;
        let right = high;
        for (let round = 0; round < this.program.limits.bisectionRounds;
          round += 1) {
          if (right - left <= this.program.limits.crossingTolerance) break;
          const middle = (left + right) / 2;
          if (outward(level(middle))) right = middle;
          else left = middle;
        }
        return (left + right) / 2;
      }
      low = high;
      below = above;
    }
    return 1;
  }

  /** An affine skeleton with a jump plan: piecewise affine in `t`, with
   * breakpoints at the plan's own cuts, solved linearly inside the piece
   * that brackets the bound. Exact. */
  private piecewise(edge: ProgramEdge, key: string, bound: number,
                    value: number, values: Record<string, number>,
                    deltas: Record<string, number>, cuts: number[]): number {
    let left = 0;
    let below = value;
    for (const cut of cuts.slice(1)) {
      const here = value + this.along(edge, key, values, deltas, cut);
      if (Math.min(below, here) <= bound && bound <= Math.max(below, here)) {
        if (here === below) return left;
        return left + (cut - left) * (bound - below) / (here - below);
      }
      left = cut;
      below = here;
    }
    return 1;
  }

  /** Anything else: sampled, bracketed and bisected under the same three
   * published limits a searched jump crossing uses. */
  private searched(edge: ProgramEdge, key: string, bound: number,
                   value: number, values: Record<string, number>,
                   deltas: Record<string, number>): number {
    const { subdivisions, bisectionRounds, crossingTolerance } =
      this.program.limits;
    const points: number[] = [];
    for (let step = 0; step <= subdivisions; step += 1) {
      points.push(step / subdivisions);
    }
    const levels = points.map(
      (where) => value + this.along(edge, key, values, deltas, where) - bound);
    for (let step = 0; step < subdivisions; step += 1) {
      let below = levels[step];
      const above = levels[step + 1];
      if (below === 0) return points[step];
      if (above === 0) return points[step + 1];
      if ((below < 0) === (above < 0)) continue;
      let low = points[step];
      let high = points[step + 1];
      for (let round = 0; round < bisectionRounds; round += 1) {
        if (high - low <= crossingTolerance) break;
        const middle = (low + high) / 2;
        const here = value
          + this.along(edge, key, values, deltas, middle) - bound;
        if (here === 0 || (here < 0) !== (below < 0)) {
          high = middle;
        } else {
          low = middle;
          below = here;
        }
      }
      return (low + high) / 2;
    }
    return 1;
  }

  /** The increment `key` receives over the stretch truncated at `t`. */
  private along(edge: ProgramEdge, key: string,
                values: Record<string, number>,
                deltas: Record<string, number>, t: number): number {
    const motion = propagations.get(deltas)?.motions.get(key);
    if (motion) return motion.at(t) - values[key];
    const truncated: Record<string, number> = {};
    for (const other of Object.keys(deltas)) truncated[other] = deltas[other] * t;
    for (const [given, increment] of edgeIncrements(
      this.program, edge, values, truncated, null, 0)) {
      if (given === key) return increment;
    }
    return 0;
  }

  /** The inputs a stop on `identifier` stops: the candidates the
   * compiled program says reach it, filtered by whether their own
   * movement over this stretch actually PUSHES it. */
  private groupOf(identifier: string, admissions: Record<string, number>,
                  values: Record<string, number>): string[] {
    const found: string[] = [];
    for (const candidate of [...(this.program.sources[identifier] ?? [])]
      .sort()) {
      const delta = admissions[candidate] ?? 0;
      if (delta && this.pushes(candidate, delta, identifier, values)) {
        found.push(candidate);
      }
    }
    return found;
  }

  /** Whether `candidate`'s own admission, with every other input's set
   * to zero, gives `key` a nonzero increment. An input coupled to `key`
   * only through a law that is currently disengaged -- an open clutch, a
   * carry outside its window -- contributes nothing and is not stopped. */
  private pushes(candidate: string, delta: number, key: string,
                 values: Record<string, number>): boolean {
    const deltas = this.deltasOf({ [candidate]: delta });
    const determination = this.program.determiner.get(key)?.edge;
    const landings: Record<string, number> | null = determination !== undefined
      && this.hasPlayAncestor(determination) ? {} : null;
    for (const edge of this.program.edges) {
      if (edge.kind === 'check') continue;
      if (edge.needs.some((need) => deltas[need])
          || (edge.timeDrive !== undefined && deltas[edge.timeDrive])
          || edge.block?.members.some(member => member.edge.timeDrive !== undefined
            && deltas[member.edge.timeDrive])) {
        for (const [gives, increment] of edgeIncrements(
          this.program, edge, values, deltas, null, 0, landings)) {
          deltas[gives] = increment;
        }
      }
      if (edge.gives.includes(key)) break;
    }
    return landings !== null && key in landings
      ? landings[key] !== this.bank[key]
      : deltas[key] !== 0;
  }

  /** Every active command whose input is in the stopped group retires
   * reporting `blocked`, with the travel it actually admitted, and its
   * input is released so a new command may be issued at once. */
  private block(stopped: Set<string>): void {
    for (const inputId of [...stopped].sort()) {
      const command = this.active.get(inputId);
      if (command !== undefined) {
        this.active.delete(inputId);
        command.status = 'blocked';
      }
    }
  }

  private runaway(reached: Reached[], limit: number): string {
    const named = reached.map(([identifier]) => identifier).join(', ');
    return (
      `${named} left a declared bound over this tick, and locating the stop ` +
      `stopped no input that was moving -- after ${limit} event(s), one per ` +
      'input admitting travel. Every stop stops at least one moving input, ' +
      'so this is a broken invariant of the run rather than a coarse dt. ' +
      'The tick committed nothing.');
  }

  /** A tick that fails commits nothing, and every command that moved an
   * input in it is retired reporting `refused` with the travel it had
   * admitted before. */
  private refuse(moved: Command[]): void {
    for (const command of moved) {
      command.status = 'refused';
      this.active.delete(command.input);
    }
  }

  private conflict(edge: ProgramEdge, predicted: number,
                   received: number): string {
    const coordinate = edge.slot as string;
    const binder = this.program.determiner.get(coordinate);
    const by = binder !== undefined
      ? `${binder.edge.description} (stated by ${binder.edge.statedBy})`
      : 'nothing in the program';
    return (
      `${coordinate}: ${edge.description}, stated by ${edge.statedBy}, ` +
      `predicts an increment of ${predicted} over this tick, while ${by} ` +
      `gives it ${received}. Two increments that disagree on one ` +
      'coordinate are a conflict, and the framework does not compare two ' +
      'values to decide which is right. The tick committed nothing: the ' +
      'bank, the tick count and the pose stand as they were, and the ' +
      'commands that moved an input in it are retired as refused.');
  }

  private disagreement(edge: ProgramEdge, key: string, delta: number): string {
    return (
      `${key}: ${edge.description}, stated by ${edge.statedBy}, gives it an ` +
      `increment of ${delta} over this tick, while another relation gives ` +
      `${key} a different one. Two increments that disagree on one ` +
      'coordinate are a conflict; the tick committed nothing.');
  }

  /** Each declared bound as a NUMBER for this tick: evaluated once, at
   * the tick's start, from the committed bank, so every segment of one
   * tick is measured against the same number. */
  private boundsNow(): Bounds {
    return this.spans.map(([identifier, low, high]) => [
      identifier,
      this.program.constraints.get(`${identifier}:low`)
        ?? this.boundOf(low, identifier),
      this.program.constraints.get(`${identifier}:high`)
        ?? this.boundOf(high, identifier),
    ]);
  }

  private boundOf(bound: ProgramBound, identifier: string): number | null {
    if (bound === null) return null;
    if (typeof bound === 'number') return bound;
    return evaluateExpression(this.program, bound.expression,
                              { [identifier]: this.bank[identifier] });
  }

  // ------------------------------------------------------------------
  // Snapshot, restore, reset

  snapshot(): RunState {
    const bank: Record<string, number> = {};
    for (const id of Object.keys(this.bank).sort()) bank[id] = this.bank[id];
    return {
      program: this.program.identity,
      dt: this.dt,
      tick: this.ticks,
      bank,
      commands: [...this.active.values()].map((command) => command.record()),
    };
  }

  restore(state: RunState): void {
    if (state === null || typeof state !== 'object') {
      throw new Error(
        `restore() takes a state taken by snapshot(), not ${state}.`);
    }
    if (state.program !== this.program.identity) {
      throw new Error(
        `that run state was taken over the program ${state.program}, and ` +
        `this run executes ${this.program.identity}. A state restores into ` +
        'the machine it was taken from: its coordinates, its inputs and ' +
        'its relations are what its bank means.');
    }
    if (state.dt !== this.dt) {
      throw new Error(
        `that run state was taken at dt=${state.dt} and this run steps at ` +
        `dt=${this.dt}. A command admits its travel per tick, so a bank ` +
        'restored across two step sizes would replay a different movement.');
    }
    for (const record of state.commands) {
      if (!Object.prototype.hasOwnProperty.call(record, 'target')) continue;
      const target = record.target;
      const declaration = this.program.drivers[record.input];
      if (declaration === undefined || record.kind !== 'move' || record.status !== 'active'
          || typeof target !== 'number'
          || !Number.isFinite(target)
          || (declaration?.dtype === 'int' && !Number.isInteger(target))) {
        throw new Error(
          `restore() has an invalid native target for '${record.input}'. ` +
          'An absolute move target must be a finite number in native units.');
      }
    }
    for (const command of this.active.values()) command.status = 'cancelled';
    this.active.clear();
    this.boundPaths.clear();
    for (const record of state.commands) {
      const declaration = this.program.drivers[record.input];
      const command = new Command(
        record.input, record.kind, declaration, record.started, {
          native: record.native,
          target: record.target,
          nativeRate: record.nativeRate,
          ticks: record.ticks,
          value: state.bank[record.input] - record.admitted,
        });
      command.admittedNative = record.admitted;
      command.status = record.status;
      this.active.set(record.input, command);
    }
    this.bank = { ...state.bank };
    this.ticks = state.tick;
    if (this.ring !== null) {
      this.ring.clear();
      this.crossingRing!.clear();
      this.stopRing!.clear();
    }
  }

  reset(): void {
    this.restore(this.initial);
  }
}

/** A segment's crossings, their fractions mapped back to the TICK.
 *
 * A segment's partition is in the fraction of the SEGMENT, and a
 * crossing's `t` is the fraction of the tick: without this the same
 * crossing would be reported at a different fraction depending on
 * whether a stop happened to cut the tick after it. */
function record(crossings: CrossingRecord[] | null,
                found: CrossingRecord[] | null,
                first: number, last: number): void {
  if (crossings === null || found === null || found.length === 0) return;
  const width = last - first;
  for (const entry of found) {
    crossings.push({ ...entry, t: first + entry.t * width });
  }
}
