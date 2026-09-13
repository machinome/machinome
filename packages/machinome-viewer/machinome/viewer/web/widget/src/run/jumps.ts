/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// How a law that jumps is integrated over one tick
// (`simulation/program.py`'s `JumpPlan`, `_branch_of`, `_surfaces`,
// `_deduplicated`, `_merged`, `_along`, `_too_many`, `_no_level`,
// reproduced function for function).
//
// The tick moves the law's sources along the straight line from the
// values they hold to those values plus the increments they were given,
// parametrised by `t` in [0, 1]. That path is cut at every crossing of
// every jump surface it meets. On each open piece every jump node holds
// one BRANCH, read by evaluating its level quantity at the piece's
// MIDPOINT -- a point genuinely inside it, so the value read there IS
// the branch, at any magnitude and from either direction of travel. The
// law with those branches substituted is continuous on the closed piece,
// so the increment is the plain sum of its change over the pieces: no
// epsilon, no one-sided limit rule, no direction test anywhere.

import {
  evaluateExpression, JumpPrimitive, ProgramJump, ProgramLimits, ProgramPlan,
  TooManyCrossings, UnsupportedLaw,
} from './program';
import type { LoadedProgram } from './program';

/** One jump surface met inside one tick. `level` is the surface value in
 * the LEVEL QUANTITY's own units and `t` is the fraction of the tick at
 * which it was reached. */
export interface CrossingRecord {
  tick: number;
  relation: string;
  coordinate: string;
  primitive: string;
  level: number;
  t: number;
}

/** A whole number, never a NEGATIVE zero: the producer's `math.floor`,
 * `math.ceil` and `math.trunc` return Python ints, which have no signed
 * zero, and `float(0)` is +0.0. */
function whole(value: number): number {
  return value === 0 ? 0 : value;
}

const COMPARISONS: Record<string, (level: number) => boolean> = {
  '<': (level) => level < 0,
  '<=': (level) => level <= 0,
  '>': (level) => level > 0,
  '>=': (level) => level >= 0,
  '==': (level) => level === 0,
  '!=': (level) => level !== 0,
};

/** What a jump reads on a piece whose level quantity sits at `level`. */
export function branchOf(primitive: JumpPrimitive, level: number): number {
  if (primitive === 'floor') return whole(Math.floor(level));
  if (primitive === 'ceil') return whole(Math.ceil(level));
  // The producer's `(x > 0) - (x < 0)`, which is 0 at negative zero
  // where a runtime's own sign function answers -0.
  if (primitive === 'sign') {
    return (level > 0 ? 1 : 0) - (level < 0 ? 1 : 0);
  }
  // Not a constant but the integer QUOTIENT: with `q` fixed the node
  // reads `a - q * b`, which is continuous in `t`.
  if (primitive === '%') return whole(Math.trunc(level));
  return COMPARISONS[primitive](level) ? 1 : 0;
}

export function tooMany(described: string, coordinate: string,
                        primitive: string, count: number,
                        limits: ProgramLimits): TooManyCrossings {
  return new TooManyCrossings(
    `${described}: over one tick ${coordinate} would cross ${count} ` +
    `surfaces of ${primitive}, more than the ${limits.maxCrossings} a ` +
    'single law is admitted in one tick. A dt that coarse is not resolving ' +
    'the mechanism: the crossings between the frames are what a jump law ' +
    'is FOR. Step in smaller ticks. The tick committed nothing: the bank, ' +
    'the tick count and the tree stand as they were.');
}

export function noLevel(primitive: string, described: string,
                        coordinate: string, reason?: string): UnsupportedLaw {
  const what = reason ?? (primitive === '%'
    ? 'a divisor of zero' : 'a division by zero in its level quantity');
  return new UnsupportedLaw(
    `${described}: its ${primitive} meets ${what} somewhere on this tick's ` +
    'path, so there is no level quantity to locate a crossing on. The tick ' +
    `committed nothing and ${coordinate} stands where it stood: state the ` +
    'relation so the divisor never reaches zero.');
}

/** The sources at `t` along the tick's straight path. At `t === 1` this
 * is exactly `start + delta`, the same float the caller computed,
 * because it is the same arithmetic. */
export function along(start: Record<string, number>,
                      delta: Record<string, number>,
                      t: number): Record<string, number> {
  const found: Record<string, number> = {};
  for (const name in start) {
    if (!Object.prototype.hasOwnProperty.call(start, name)) continue;
    found[name] = start[name] + delta[name] * t;
  }
  return found;
}

/** A jump's surfaces between two values of its level quantity. */
export function surfacesOf(
  jump: ProgramJump, low: number, high: number, inclusive: boolean,
  limits: ProgramLimits, refuse: (count: number | null) => never,
): number[] {
  if (jump.primitive === 'sign' || jump.primitive in COMPARISONS) {
    const first = low <= high ? low : high;
    const last = low <= high ? high : low;
    if ((first < 0 && 0 < last) || (inclusive && first <= 0 && 0 <= last)) {
      return [0];
    }
    return [];
  }
  const first = low <= high ? low : high;
  const last = low <= high ? high : low;
  if (!Number.isFinite(first) || !Number.isFinite(last)) {
    refuse(null);
  }
  const span = Math.ceil(last) - Math.floor(first) - 1;
  if (span > limits.maxCrossings) {
    refuse(span);
  }
  const levels: number[] = [];
  if (inclusive) {
    for (let whole = Math.floor(first); whole <= Math.ceil(last); whole += 1) {
      if (first <= whole && whole <= last) levels.push(whole);
    }
  } else {
    for (let whole = Math.floor(first) + 1; whole < Math.ceil(last);
         whole += 1) {
      if (first < whole && whole < last) levels.push(whole);
    }
  }
  if (jump.primitive === '%') {
    // `fmod` is `a - b * trunc(a / b)`, and `trunc` is zero on the whole
    // of (-1, 1): the operator is CONTINUOUS where `a / b` crosses zero
    // and jumps only at a nonzero integer of it.
    return levels.filter((level) => level !== 0);
  }
  return levels;
}

/** One entry per surface actually reached: a crossing that falls on a
 * sub-interval boundary is located twice, from either side. */
export function deduplicated(found: [number, number][],
                             tolerance: number): [number, number][] {
  const ordered = [...found].sort(
    (a, b) => (a[0] - b[0]) || (a[1] - b[1]));
  const kept: [number, number][] = [];
  for (const entry of ordered) {
    const last = kept[kept.length - 1];
    if (last !== undefined && last[1] === entry[1]
        && entry[0] - last[0] <= tolerance) {
      continue;
    }
    kept.push(entry);
  }
  return kept;
}

/** The partition with `found` folded in: two cuts closer than the
 * tolerance are ONE, and the partition always ends at exactly 1. */
export function merged(cuts: number[], found: number[],
                       tolerance: number): number[] {
  const ordered = [...cuts, ...found].sort((a, b) => a - b);
  const kept = [ordered[0]];
  for (const where of ordered.slice(1)) {
    if (where - kept[kept.length - 1] > tolerance) kept.push(where);
  }
  kept[kept.length - 1] = 1;
  return kept;
}

function levelAt(program: LoadedProgram, plan: ProgramPlan, jump: ProgramJump,
                 start: Record<string, number>, delta: Record<string, number>,
                 t: number, inner: Record<string, number>,
                 described: string, coordinate: string): number {
  const values = along(start, delta, t);
  for (const name in inner) {
    if (Object.prototype.hasOwnProperty.call(inner, name)) {
      values[name] = inner[name];
    }
  }
  return levelOf(program, plan, jump, values, described, coordinate);
}

function levelOf(program: LoadedProgram, plan: ProgramPlan, jump: ProgramJump,
                 values: Record<string, number>, described: string,
                 coordinate: string): number {
  void plan;
  const level = evaluateExpression(program, jump.level, values);
  if (!Number.isFinite(level)) {
    // Python raises `ZeroDivisionError` where this runtime answers
    // Infinity or NaN, and refuses a non-finite level for the integer
    // primitives outright. Either way there is no level quantity to
    // locate a crossing on.
    throw noLevel(jump.primitive, described, coordinate,
                  Number.isNaN(level)
                    ? 'a level quantity that is not a number'
                    : undefined);
  }
  return level;
}

/** Every jump node's branch at one point of the path, in POSTORDER, so a
 * node nested inside another's argument is determined first. */
function branchesAt(program: LoadedProgram, plan: ProgramPlan,
                    start: Record<string, number>,
                    delta: Record<string, number>, t: number, count: number,
                    described: string,
                    coordinate: string): Record<string, number> {
  const values = along(start, delta, t);
  const found: Record<string, number> = {};
  for (const jump of plan.jumps.slice(0, count)) {
    const level = levelOf(program, plan, jump, values, described, coordinate);
    const branch = branchOf(jump.primitive, level);
    found[jump.name] = branch;
    values[jump.name] = branch;
  }
  return found;
}

function substituted(program: LoadedProgram, plan: ProgramPlan,
                     start: Record<string, number>,
                     delta: Record<string, number>, t: number,
                     branches: Record<string, number>): number {
  const values = along(start, delta, t);
  for (const name in branches) {
    if (Object.prototype.hasOwnProperty.call(branches, name)) {
      values[name] = branches[name];
    }
  }
  return evaluateExpression(program, plan.skeleton, values);
}

function crossingsOf(
  program: LoadedProgram, plan: ProgramPlan, jump: ProgramJump,
  start: Record<string, number>, delta: Record<string, number>,
  inner: Record<string, number>, left: number, right: number,
  described: string, coordinate: string,
): [number, number][] {
  const limits = program.limits;
  const refuse = (count: number | null): never => {
    if (count === null) throw noLevel(jump.primitive, described, coordinate);
    throw tooMany(described, coordinate, jump.primitive, count, limits);
  };
  if (jump.affine) {
    // An affine level quantity is determined everywhere on the piece by
    // its two endpoint values, so every surface between them is SOLVED
    // -- all of them, which is what makes a crank that passes three
    // tooth windows in one tick add three throws rather than one.
    const low = levelAt(program, plan, jump, start, delta, left, inner,
                        described, coordinate);
    const high = levelAt(program, plan, jump, start, delta, right, inner,
                         described, coordinate);
    if (high === low) return [];
    const found: [number, number][] = [];
    for (const level of surfacesOf(jump, low, high, false, limits, refuse)) {
      found.push([left + (right - left) * (level - low) / (high - low), level]);
    }
    return found;
  }
  // Anything else: sampled, bracketed and bisected.
  const width = (right - left) / limits.subdivisions;
  const points: number[] = [];
  for (let step = 0; step < limits.subdivisions; step += 1) {
    points.push(left + width * step);
  }
  points.push(right);
  const levels = points.map((where) => levelAt(
    program, plan, jump, start, delta, where, inner, described, coordinate));
  const found: [number, number][] = [];
  for (let step = 0; step < limits.subdivisions; step += 1) {
    const low = levels[step];
    const high = levels[step + 1];
    for (const level of surfacesOf(jump, low, high, true, limits, refuse)) {
      if (low === level) {
        // A sample that IS on the surface is the crossing; taking it
        // exactly is what keeps the answer exact when a crossing falls
        // on a sub-interval boundary.
        found.push([points[step], level]);
      } else if (high === level) {
        found.push([points[step + 1], level]);
      } else {
        found.push([bisect(program, plan, jump, start, delta, inner, level,
                           points[step], points[step + 1], described,
                           coordinate), level]);
      }
    }
    if (found.length > limits.maxCrossings) break;
  }
  return found;
}

function bisect(program: LoadedProgram, plan: ProgramPlan, jump: ProgramJump,
                start: Record<string, number>, delta: Record<string, number>,
                inner: Record<string, number>, level: number, low: number,
                high: number, described: string, coordinate: string): number {
  let below = levelAt(program, plan, jump, start, delta, low, inner,
                      described, coordinate) - level;
  let lower = low;
  let upper = high;
  for (let round = 0; round < program.limits.bisectionRounds; round += 1) {
    if (upper - lower <= program.limits.crossingTolerance) break;
    const middle = (lower + upper) / 2;
    const here = levelAt(program, plan, jump, start, delta, middle, inner,
                         described, coordinate) - level;
    if (here === 0 || (here < 0) !== (below < 0)) {
      upper = middle;
    } else {
      lower = middle;
      below = here;
    }
  }
  return (lower + upper) / 2;
}

function partition(program: LoadedProgram, plan: ProgramPlan,
                   start: Record<string, number>,
                   delta: Record<string, number>, described: string,
                   coordinate: string, crossings: CrossingRecord[] | null,
                   tick: number): number[] {
  const limits = program.limits;
  let cuts = [0, 1];
  const located: [number, number, string, number][] = [];
  plan.jumps.forEach((jump, index) => {
    let found: [number, number][] = [];
    for (let at = 0; at < cuts.length - 1; at += 1) {
      const left = cuts[at];
      const right = cuts[at + 1];
      const inner = branchesAt(program, plan, start, delta,
                               (left + right) / 2, index, described,
                               coordinate);
      found = found.concat(crossingsOf(program, plan, jump, start, delta,
                                       inner, left, right, described,
                                       coordinate));
      if (found.length > limits.maxCrossings) {
        throw tooMany(described, coordinate, jump.primitive, found.length,
                      limits);
      }
    }
    if (found.length === 0) return;
    found = deduplicated(found, limits.crossingTolerance);
    cuts = merged(cuts, found.map(([where]) => where),
                  limits.crossingTolerance);
    if (cuts.length - 2 > limits.maxCrossings) {
      throw tooMany(described, coordinate, jump.primitive, cuts.length - 2,
                    limits);
    }
    for (const [where, level] of found) {
      located.push([where, index, jump.primitive, level]);
    }
  });
  if (crossings !== null && located.length > 0) {
    // Sorted by the fraction of the tick, and by the graph's postorder
    // where two coincide, so the listing is deterministic.
    located.sort((a, b) => (a[0] - b[0]) || (a[1] - b[1]));
    for (const [where, , primitive, level] of located) {
      crossings.push({
        tick, relation: described, coordinate, primitive, level, t: where,
      });
    }
  }
  return cuts;
}

/** The CONTINUOUS part of this law's change over one tick. */
export function planIncrement(
  program: LoadedProgram, plan: ProgramPlan, start: Record<string, number>,
  delta: Record<string, number>, described: string, coordinate: string,
  crossings: CrossingRecord[] | null, tick: number,
): number {
  if (!Object.values(delta).some((value) => value !== 0)) {
    // A zero-length path contributes zero without evaluating anything --
    // and must never reach the sum below, where a one-point piece would
    // read as minus a jump.
    return 0;
  }
  const cuts = partition(program, plan, start, delta, described, coordinate,
                         crossings, tick);
  let total = 0;
  for (let at = 0; at < cuts.length - 1; at += 1) {
    const left = cuts[at];
    const right = cuts[at + 1];
    const branches = branchesAt(program, plan, start, delta,
                                (left + right) / 2, plan.jumps.length,
                                described, coordinate);
    total += substituted(program, plan, start, delta, right, branches)
      - substituted(program, plan, start, delta, left, branches);
  }
  return total;
}

/** The breakpoints this law's own jumps put on the tick's path.
 *
 * Between two consecutive cuts every jump node holds one branch, so a
 * law whose SKELETON is affine has a value that is affine in `t` there
 * -- which is what lets a stop on it be SOLVED piece by piece rather
 * than searched. */
export function planCuts(
  program: LoadedProgram, plan: ProgramPlan, start: Record<string, number>,
  delta: Record<string, number>, described: string, coordinate: string,
): number[] {
  if (!Object.values(delta).some((value) => value !== 0)) return [0, 1];
  return partition(program, plan, start, delta, described, coordinate, null, 0);
}
