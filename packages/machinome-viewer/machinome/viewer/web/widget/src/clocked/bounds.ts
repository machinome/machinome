/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// A declared STOP, and where it clips a request
// (`simulation/clocked.py`'s `Bounded`, `_Level` and `Stop`; OpenSpec
// `execute-the-commit`, design §8; machinome ADR-126).
//
//     high side:   g(t) = value(t) - bound(t)
//     low  side:   g(t) = bound(t) - value(t)
//
// `value` is the published CHAIN; `bound` is the declared bound with its
// OWN coordinate taken at the value the request STARTED from and each
// read taken ALONG THE PATH through its own chain. A request admits the
// largest fraction at which `g` does not exceed `max(0, g(0))`.
//
// An event lands BEYOND its surface because the path has reached it; a
// stop lands SHORT of it because that is where the machine still is --
// ONE walk, two directions.

import {
  along, branchesAt, copySign, farSideOf, kinkBreaks, planPartition,
} from '../run/jumps';
import {
  evaluateExpression, kinkLevel, LandingInvariantError, TooManyCrossings,
} from '../run/program';
import { TooManyEvents } from './document';
import type { LoadedBound, LoadedMachine } from './document';

/** ONE bound met on a request path (`Stop`): what stopped, which side of
 * its range, what that bound evaluated to at the landing, what the
 * coordinate is worth there, where the input landed, and the fraction of
 * the REQUESTED travel that was. */
export interface ClockedStop {
  coordinate: string;
  side: 'low' | 'high';
  bound: number;
  value: number;
  input: number;
  fraction: number;
}

/** One compiled constraint as ONE request reads it (`_Level`): the
 * values its level stands at when the request begins, and the threshold
 * those values give it. BOTH are read ONCE, at the request's start. */
export interface LevelReading {
  bound: LoadedBound;
  values: Record<string, number>;
  threshold: number;
}

/** The values this level reads, with the OWN coordinate taken at the
 * value the request STARTS from (`Bounded.standing`), and the threshold
 * `h = max(0, g(0))` (`Bounded.threshold`).
 *
 * The ordinary bound where the machine stands legally, and where it
 * stands where it does NOT: a machine outside a bound may move as long
 * as it does not go FURTHER out, and it may return -- nothing is ever
 * clamped and nothing is silently repaired. */
export function levelReading(machine: LoadedMachine,
                             bound: LoadedBound,
                             bank: Record<string, number>): LevelReading {
  const values: Record<string, number> = {};
  for (const name of bound.names) values[name] = bank[name];
  const chainValues: Record<string, number> = {};
  for (const name of bound.chainNames) chainValues[name] = bank[name];
  values[machine.own] = evaluateExpression(machine, bound.chain, chainValues);
  return {
    bound,
    values,
    threshold: Math.max(0, evaluateExpression(machine, bound.level, values)),
  };
}

function held(reading: LevelReading, inputId: string,
              value: number): Record<string, number> {
  const values = { ...reading.values };
  values[inputId] = value;
  return values;
}

/** The LEVEL with the input at one value (`Bounded.at`). */
export function levelAt(machine: LoadedMachine, reading: LevelReading,
                        inputId: string, value: number): number {
  return evaluateExpression(machine, reading.bound.level,
                            held(reading, inputId, value));
}

/** The declared BOUND with the input at one value (`Bounded.bound_at`). */
export function boundAt(machine: LoadedMachine, reading: LevelReading,
                        inputId: string, value: number): number {
  return evaluateExpression(machine, reading.bound.bound,
                            held(reading, inputId, value));
}

/** The bounded COORDINATE with the input at one value
 * (`Bounded.value_at`). */
export function valueAt(machine: LoadedMachine, reading: LevelReading,
                        inputId: string, value: number): number {
  return evaluateExpression(machine, reading.bound.chain,
                            held(reading, inputId, value));
}

/** Whether this constraint's level can move when `inputId` does
 * (`Bounded.moves_with`). A level no driver moves is not examined for
 * it, and costs nothing. */
export function movesWith(bound: LoadedBound, inputId: string): boolean {
  return bound.plans.has(inputId);
}

function tooManyStops(bound: LoadedBound, inputId: string, delta: number,
                      count: number | null,
                      maxCrossings: number): TooManyEvents {
  return new TooManyEvents(
    `the request move('${inputId}', by=${delta}) would cross ` +
    `${count === null ? 'more than' : count} surfaces of ` +
    `${bound.description}, and ${maxCrossings} is the most one constraint ` +
    'is admitted on one request. The request committed nothing: the bank ' +
    'and the tree stand as they were. Split it into shorter requests.');
}

function unstopped(bound: LoadedBound,
                   inputId: string): LandingInvariantError {
  return new LandingInvariantError(
    `${bound.description}: the level was crossed on this request and no ` +
    `value of '${inputId}' within reach of the crossing's own arithmetic ` +
    'reads the satisfied side, so the stop placed the input nowhere. That ' +
    'is a broken invariant of the clocked solver. The request committed ' +
    'nothing.');
}

/** The skeleton with this piece's branches substituted
 * (`JumpPlan._substituted`). */
function substituted(machine: LoadedMachine, skeleton: string,
                     walk: Record<string, number>,
                     steps: Record<string, number>, t: number,
                     branches: Record<string, number>): number {
  const values = along(walk, steps, t);
  for (const name in branches) {
    if (Object.prototype.hasOwnProperty.call(branches, name)) {
      values[name] = branches[name];
    }
  }
  return evaluateExpression(machine, skeleton, values);
}

/** Where the level first exceeds `threshold` on ONE piece of the
 * partition, as a fraction of the whole path, or `null`
 * (`Bounded._crossed`).
 *
 * A piece whose LEFT end already exceeds it is one the level STEPPED
 * across at the cut behind it: the stop is at the end of the last piece
 * on which the level was satisfied, which is the landing rule with no
 * special case. */
function crossedOn(machine: LoadedMachine, reading: LevelReading,
                   inputId: string, walk: Record<string, number>,
                   steps: Record<string, number>,
                   branches: Record<string, number>, left: number,
                   right: number, threshold: number): number | null {
  const plan = reading.bound.plans.get(inputId);
  if (plan === undefined) return null;
  const { skeleton } = plan.plan;
  let edges = [left, right];
  if (plan.kinks !== null && plan.kinks.length > 0) {
    const at = (t: number): Record<string, number> => {
      const values = along(walk, steps, t);
      for (const name in branches) {
        if (Object.prototype.hasOwnProperty.call(branches, name)) {
          values[name] = branches[name];
        }
      }
      return values;
    };
    edges = [left, ...kinkBreaks(
      plan.kinks, (kink, t) => kinkLevel(machine, kink, at(t)), left, right,
      machine.limits.crossingTolerance), right];
  }
  for (let at = 0; at < edges.length - 1; at += 1) {
    const low = edges[at];
    const high = edges[at + 1];
    const below = substituted(machine, skeleton, walk, steps, low, branches);
    const above = substituted(machine, skeleton, walk, steps, high, branches);
    if (below > threshold) return low;
    if (above <= threshold) continue;
    if (above === below) return high;
    return low + (high - low) * (threshold - below) / (above - below);
  }
  return null;
}

/** The landing this constraint stops the path at, as
 * `{fraction, landing}`, or `null` when it stops nothing
 * (`Bounded.clip`).
 *
 * The path is partitioned at the level's OWN jump surfaces; on each
 * piece every jump node holds one branch, so the skeleton is affine or
 * kinked there and its crossing of `threshold` is ONE DIVISION. The
 * landing is then the nearest representable value of the input on the
 * SATISFIED side, walked in float ordinal space with membership decided
 * by EVALUATING the level and never by comparing a float to a bound. */
export function clip(machine: LoadedMachine, reading: LevelReading,
                     inputId: string, start: number, delta: number):
{ fraction: number; landing: number } | null {
  const { bound } = reading;
  const plan = bound.plans.get(inputId);
  if (plan === undefined || delta === 0) return null;
  const walk: Record<string, number> = {};
  for (const name of bound.names) walk[name] = reading.values[name];
  walk[machine.own] = reading.values[machine.own];
  walk[inputId] = start;
  const steps: Record<string, number> = {};
  for (const name in walk) {
    if (Object.prototype.hasOwnProperty.call(walk, name)) steps[name] = 0;
  }
  steps[inputId] = delta;
  let cuts: number[];
  try {
    cuts = planPartition(machine, plan.plan, walk, steps, bound.description,
                         bound.coordinate);
  } catch (error) {
    if (error instanceof TooManyCrossings) {
      throw tooManyStops(bound, inputId, delta, null,
                         machine.limits.maxCrossings);
    }
    throw error;
  }
  let crossed: number | null = null;
  for (let at = 0; at < cuts.length - 1; at += 1) {
    const left = cuts[at];
    const right = cuts[at + 1];
    const branches = branchesAt(machine, plan.plan, walk, steps,
                                (left + right) / 2, plan.plan.jumps.length,
                                bound.description, bound.coordinate);
    crossed = crossedOn(machine, reading, inputId, walk, steps, branches,
                        left, right, reading.threshold);
    if (crossed !== null) break;
  }
  if (crossed === null) return null;
  if (crossed === 0) {
    // A level already AT its limit and pushed FURTHER admits ZERO
    // travel: the request moves nothing, fires nothing and reports its
    // stop. Said HERE, off the crossing, rather than left to the walk:
    // where the input stands at a value whose ulp is finer than the
    // LEVEL's, the walk finds a landing half an ulp of the level beyond
    // the start -- a travel the level cannot express -- and the low side
    // of a bound would then admit what the high side of the same bound
    // refuses, only because the coordinate happens to stand near zero
    // (ADR-128's closure).
    return { fraction: 0, landing: start };
  }
  const star = start + delta * crossed;
  const direction = copySign(delta);
  const satisfied = (value: number): number =>
    Number(levelAt(machine, reading, inputId, value) <= reading.threshold);
  const landing = farSideOf(satisfied, 0, star, -direction,
                            () => unstopped(bound, inputId),
                            Math.max(Math.abs(start), Math.abs(start + delta)));
  const fraction = (landing - start) / delta;
  if (fraction <= 0) return { fraction: 0, landing: start };
  if (fraction >= 1) return null;
  return { fraction, landing };
}
