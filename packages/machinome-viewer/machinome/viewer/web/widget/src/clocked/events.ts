/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// Where a committing relation FIRES on one request path
// (`simulation/clocked.py`'s `Committing.next_event` and `_located`,
// mirrored step for step; OpenSpec `execute-the-commit`, design §6).
//
// This module is a CONSUMER of the running executor's locator and adds
// no second one: `surfacesOf` solves an affine level by one division,
// `kinkBreaks` cuts a kinked one at its own breakpoints, `branchOf`
// reads a branch, `onSurface` says whether the path BEGINS on a
// surface, `deduplicated` folds a crossing located twice, and
// `farSideOf` walks the landing in float ordinal space. Nothing here
// bisects, samples or compares a value to a surface, and NO TOLERANCE
// IS INTRODUCED AT ALL: under a clocked root every crossing is SOLVED,
// so two relations fire at one event exactly when their far-side
// landings are the same float.

import {
  along, branchOf, copySign, deduplicated, farSideOf, kinkBreaks, nextAfter,
  noLevel, onSurface, surfacesOf,
} from '../run/jumps';
import {
  evaluateExpression, kinkLevel, LandingInvariantError,
} from '../run/program';
import type { PathHost, ProgramJump } from '../run/program';
import { TooManyEvents } from './document';
import type { LoadedCommit, LoadedMachine } from './document';

/** One crossing of one relation's level: where on the path it sits, and
 * the value of the level's own quantity there. */
type Crossing = [number, number];

/** The earliest RISING crossing of one relation's level, as the caller
 * reads it. `where` is the fraction of THIS path -- the caller rescales
 * it to the whole request -- and `landing` is the nearest representable
 * value of the input on the FAR side of the surface, which the event
 * both READS and RESUMES from, so no event can fire twice. */
export interface LocatedEvent {
  where: number;
  landing: number;
}

/** `JumpPlan._level`'s refusal rules, over a clocked level
 * (`_leveled`): a level quantity that is not a finite number refuses
 * the request for an INTEGER-branch primitive, and is an ordinary
 * reading for a comparison or a `sign`, whose one surface is zero. */
function leveled(host: PathHost, jump: ProgramJump,
                 values: Record<string, number>, described: string,
                 coordinate: string): number {
  const level = evaluateExpression(host, jump.level, values);
  if ((jump.primitive === 'floor' || jump.primitive === 'ceil'
       || jump.primitive === '%') && !Number.isFinite(level)) {
    throw noLevel(jump.primitive, described, coordinate,
                  Number.isNaN(level)
                    ? 'a level quantity that is not a number' : undefined);
  }
  return level;
}

export function tooManyEvents(commit: LoadedCommit, inputId: string,
                              delta: number, count: number | null,
                              maxCrossings: number): TooManyEvents {
  return new TooManyEvents(
    `the request move('${inputId}', by=${delta}) would cross ` +
    `${count === null ? 'more than' : count} surfaces of the committing ` +
    `relation ${commit.description}, and ${maxCrossings} is the most one ` +
    'relation is admitted on one request. The request committed nothing: ' +
    'the bank and the tree stand as they were. Split it into shorter ' +
    'requests.');
}

function unlandedEvent(commit: LoadedCommit,
                       jump: ProgramJump): LandingInvariantError {
  return new LandingInvariantError(
    `${commit.description}: ${commit.targets.join(', ')} was cut at a ` +
    `surface of ${jump.primitive} and no value within reach of the ` +
    'segment\'s own arithmetic reads the other branch, so the cut placed ' +
    'the input nowhere. That is a broken invariant of the clocked ' +
    'solver. The request committed nothing.');
}

/** An AFFINE stretch of the level quantity, SOLVED
 * (`JumpPlan._solved`): determined everywhere on it by its two endpoint
 * values, so every surface between them is found by one division -- all
 * of them, which is what makes a crank passing three tooth windows in
 * one request commit three strokes rather than one.
 *
 * `closed` takes the stretch's RIGHT end inclusively. The LEFT end is
 * exclusive either way: at the path's own left end that surface is not
 * one the piece crosses -- it is added by `located` below, off
 * `onSurface` -- and at an interior breakpoint it was reached by the
 * sub-piece before. */
function solved(host: PathHost, machine: LoadedMachine, commit: LoadedCommit,
                jump: ProgramJump, standing: Record<string, number>,
                steps: Record<string, number>, left: number, right: number,
                closed: boolean, inputId: string, delta: number): Crossing[] {
  const described = commit.description;
  const coordinate = commit.targets.join(', ');
  const refuse = (count: number | null): never => {
    if (count === null) throw noLevel(jump.primitive, described, coordinate);
    throw tooManyEvents(commit, inputId, delta, count,
                        machine.limits.maxCrossings);
  };
  const low = leveled(host, jump, along(standing, steps, left), described,
                      coordinate);
  const high = leveled(host, jump, along(standing, steps, right), described,
                       coordinate);
  if (high === low) return [];
  const found: Crossing[] = [];
  for (const level of surfacesOf(jump, low, high, closed, machine.limits,
                                 refuse)) {
    if (closed && level === low) continue;
    found.push([left + (right - left) * (level - low) / (high - low), level]);
  }
  return found;
}

/** Every crossing of this relation's level on the path, in path order
 * (`Committing._located`).
 *
 * BOTH ends are taken: a request that ends exactly ON a surface has
 * reached it -- `move('crank', by=360)` with `at = floor(crank / 360)`
 * IS one stroke -- and a request that BEGINS on one has reached it too
 * when its far side lies ahead. Which of the two requests a surface
 * belongs to is decided by the LANDING and not here (ADR-128 closure 1).
 */
function located(host: PathHost, machine: LoadedMachine,
                 commit: LoadedCommit, jump: ProgramJump,
                 standing: Record<string, number>,
                 steps: Record<string, number>, inputId: string,
                 delta: number): Crossing[] {
  const described = commit.description;
  const coordinate = commit.targets.join(', ');
  let found: Crossing[];
  if (jump.shape === 'kinked' && jump.kinks !== null
      && jump.kinks.length > 0) {
    const breaks = kinkBreaks(
      jump.kinks,
      (kink, t) => kinkLevel(host, kink, along(standing, steps, t)),
      0, 1, machine.limits.crossingTolerance);
    const edges = [0, ...breaks, 1];
    found = [];
    for (let at = 0; at < edges.length - 1; at += 1) {
      // EVERY sub-piece is closed on the right, the last one included:
      // both ends of the whole path are taken.
      found = found.concat(solved(host, machine, commit, jump, standing,
                                  steps, edges[at], edges[at + 1], true,
                                  inputId, delta));
    }
    found = deduplicated(found, machine.limits.crossingTolerance);
  } else {
    found = solved(host, machine, commit, jump, standing, steps, 0, 1, true,
                   inputId, delta);
  }
  if (found.length > machine.limits.maxCrossings) {
    throw tooManyEvents(commit, inputId, delta, found.length,
                        machine.limits.maxCrossings);
  }
  found = [...found].sort((a, b) => a[0] - b[0]);
  // `solved` excludes a piece's left end, which is right for an interior
  // breakpoint -- the sub-piece before it reached that surface -- so the
  // path's OWN opening surface is added here, read off the level the
  // path starts at.
  const opening = leveled(host, jump, along(standing, steps, 0), described,
                          coordinate);
  if (onSurface(jump, opening)
      && !(found.length > 0 && found[0][0] === 0)) {
    found.unshift([0, opening]);
  }
  return found;
}

/** The earliest RISING crossing of `commit`'s level on the straight path
 * from `start` to `start + delta`, or `null`
 * (`Committing.next_event`). */
export function nextEvent(machine: LoadedMachine, commit: LoadedCommit,
                          bank: Record<string, number>, inputId: string,
                          start: number, delta: number): LocatedEvent | null {
  const jump = commit.jumps.get(inputId);
  if (jump === undefined || delta === 0) return null;
  const host: PathHost = machine;
  const standing: Record<string, number> = {};
  const steps: Record<string, number> = {};
  for (const id of commit.sources) {
    standing[id] = bank[id];
    steps[id] = 0;
  }
  standing[inputId] = start;
  steps[inputId] = delta;
  const found = located(host, machine, commit, jump, standing, steps,
                        inputId, delta);
  if (found.length === 0) return null;
  const edges = [0, ...found.map(([where]) => where), 1];

  const levelAt = (value: number): number => {
    const values = { ...standing };
    values[inputId] = value;
    return evaluateExpression(host, commit.level, values);
  };
  const branchAt = (value: number): number =>
    branchOf(jump.primitive, levelAt(value));

  const direction = copySign(delta);
  const endpoint = start + delta;
  const scale = Math.max(Math.abs(start), Math.abs(endpoint));
  for (let index = 0; index < found.length; index += 1) {
    const where = found[index][0];
    let before: number;
    if (where === 0) {
      // The path BEGINS on this surface, so there is no piece behind it
      // to read a branch from: the branch the request stands in is read
      // AT THE START, and the far side is asked for at the NEXT
      // REPRESENTABLE VALUE the path reaches. Where that reads the same
      // branch the machine already stands on the far side -- a request
      // resuming from its own landing -- and the surface is not this
      // request's. Where it differs, the landing is that value and the
      // surface is this request's first event (ADR-128 closure 1).
      before = branchAt(start);
      if (branchAt(nextAfter(start, direction > 0 ? Infinity : -Infinity))
          === before) {
        continue;
      }
    } else {
      const values = along(standing, steps, (edges[index] + where) / 2);
      before = branchOf(jump.primitive,
                        evaluateExpression(host, commit.level, values));
    }
    const landing = farSideOf(branchAt, before, start + delta * where,
                              direction, () => unlandedEvent(commit, jump),
                              scale);
    if (direction * (landing - endpoint) > 0) {
      // The landing lies BEYOND this request's endpoint, which a STRICT
      // comparison reached exactly does: the crossing belongs to the
      // request whose PATH CONTAINS its landing, and that is the next
      // one, which begins on this surface and takes it at fraction zero.
      continue;
    }
    // RISING is read from the branch the path came from and the branch
    // AT THE LANDING -- which is the nearest point of the piece the path
    // is going into, and the only reading available where the crossing
    // is the request's own endpoint (design §6).
    if (branchAt(landing) > before) return { where, landing };
  }
  return null;
}
