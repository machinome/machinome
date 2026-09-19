/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// One step of the program: what it reads, what it determines, and how
// (`simulation/program.py`'s `class Edge`, reproduced).
//
// The rule is THE SAME ARITHMETIC IN THE SAME ORDER, not an equivalent
// result: where the producer accumulates `total = total + held[key] *
// factor` in `needs` order, so does this. The corpus pins floats to
// `1e-9` relative, and a re-associated sum is exactly how a runtime
// drifts into that window and then out of it.

import { evaluateExpression, ProgramEdge } from './program';
import type { LoadedProgram } from './program';
import {
  blockCuts, blockIncrements, CrossingRecord, kinkedEndCuts, planCuts,
  planIncrement, retainedCuts, retainedIncrement,
} from './jumps';

/** The graph's free names bound to the values its sources hold,
 * optionally advanced by the tick's increments. */
function inputsOf(edge: ProgramEdge, values: Record<string, number>,
                  deltas?: Record<string, number>): Record<string, number> {
  const found: Record<string, number> = {};
  if (deltas === undefined) {
    for (const key of edge.needs) found[key] = values[key];
  } else {
    for (const key of edge.needs) found[key] = values[key] + deltas[key];
  }
  return found;
}

function evaluated(program: LoadedProgram, expression: string | null,
                   inputs: Record<string, number>): number {
  // A law whose expression has no free coordinate -- a constant -- has
  // zero slope everywhere, so it contributes nothing.
  if (expression === null) return 0;
  return evaluateExpression(program, expression, inputs);
}

/** The linear combination this formula edge states, in the direction the
 * rest render resolved it. Forward, that is the formula itself;
 * backward into one term, the formula rearranged for that term --
 * exact, because a derived coordinate is a coefficient map and a
 * constant, not an expression tree. */
export function linearOf(edge: ProgramEdge, held: Record<string, number>,
                         constant?: number): number {
  let total = constant === undefined ? edge.constant : constant;
  if (edge.slot !== null && edge.gives.includes(edge.slot)) {
    edge.needs.forEach((key, index) => {
      total = total + held[key] * edge.factors[index];
    });
    return total;
  }
  // Backward: `gives` is the one term the formula solves for, and
  // `needs` carries the slot first, then the other terms.
  let value = held[edge.slot as string] - total;
  let own: number | undefined;
  edge.needs.forEach((key, index) => {
    const factor = edge.factors[index];
    if (key === edge.slot) return;
    if (key === edge.gives[0] && own === undefined) {
      own = factor;
      return;
    }
    value = value - held[key] * factor;
  });
  return value / (own as number);
}

/** What a CHECK edge's formula says its coordinate should hold, or move
 * by. */
export function predictsOf(edge: ProgramEdge, held: Record<string, number>,
                           constant?: number): number {
  let total = constant === undefined ? edge.constant : constant;
  edge.needs.forEach((key, index) => {
    if (key === edge.slot) return;
    total = total + held[key] * edge.factors[index];
  });
  return total;
}

/** What this edge's targets hold at the committed state. */
export function edgeValues(program: LoadedProgram, edge: ProgramEdge,
                           values: Record<string, number>):
[string, number][] {
  if (edge.kind === 'law') {
    const inputs = inputsOf(edge, values);
    return edge.gives.map((key, index) =>
      [key, evaluated(program, edge.expressions[index], inputs)]);
  }
  // A BLOCK computes nothing outside the bank -- every one of its gives
  // is a coordinate the run banks (design D1.7's third refusal) -- and
  // `Run.valuesOf` skips an edge all of whose gives are bank keys, so it
  // is never asked. It answers nothing here as `Program.values_of` does
  // (design D4.4), through the fall-through below.
  if (edge.kind === 'wiring') {
    return [[edge.gives[0], values[edge.needs[0]] * edge.factor]];
  }
  if (edge.kind === 'formula') {
    return [[edge.gives[0], linearOf(edge, values)]];
  }
  return [];
}

/** What this edge's targets MOVE BY over the tick.
 *
 * A law with no jump in it is the difference of two exact evaluations,
 * which is what makes a kink exact -- and that is the FIRST thing tested
 * here, so a continuous law pays nothing for the jump machinery. A law
 * that jumps takes its plan, which cuts the tick at every crossing and
 * sums the pieces.
 *
 * A law that READS THE COORDINATE IT DRIVES is walked piece by piece
 * instead, and REPORTS into `landings` the absolute value that end holds
 * at the tick's end where at least one cut placed it: the run commits
 * that float rather than `value + delta`, exactly where it commits a
 * stop at its bound. A law with no self-read pays ONE array-length test
 * for all of this and nothing else. */
export function edgeIncrements(
  program: LoadedProgram, edge: ProgramEdge, values: Record<string, number>,
  deltas: Record<string, number>, crossings: CrossingRecord[] | null,
  tick: number, landings: Record<string, number> | null = null,
): [string, number][] {
  if (edge.kind === 'law') {
    const start = inputsOf(edge, values);
    const carriesPlan = edge.plans.some((plan) => plan !== null);
    if (!carriesPlan) {
      const end = inputsOf(edge, values, deltas);
      return edge.gives.map((key, index) => [
        key,
        evaluated(program, edge.expressions[index], end)
          - evaluated(program, edge.expressions[index], start),
      ]);
    }
    const delta: Record<string, number> = {};
    for (const key of edge.needs) delta[key] = deltas[key];
    const end = inputsOf(edge, values, deltas);
    const retained = edge.retained;
    return edge.gives.map((key, index) => {
      const plan = edge.plans[index];
      if (plan === null) {
        return [key,
                evaluated(program, edge.expressions[index], end)
                  - evaluated(program, edge.expressions[index], start)];
      }
      const reading = retained.length > 0 ? retained[index] : null;
      if (reading === null) {
        return [key, planIncrement(program, plan, start, delta,
                                   edge.description, edge.gives[index],
                                   crossings, tick)];
      }
      const { increment, landing } = retainedIncrement(
        program, reading, start, delta, edge.description, edge.gives[index],
        crossings, tick);
      if (landing !== null && landings !== null) landings[key] = landing;
      return [key, increment];
    });
  }
  if (edge.kind === 'block') {
    return blockIncrements(program, edge.block!, values, deltas, crossings,
                           tick, landings);
  }
  if (edge.kind === 'wiring') {
    return [[edge.gives[0], deltas[edge.needs[0]] * edge.factor]];
  }
  if (edge.kind === 'formula') {
    return [[edge.gives[0], linearOf(edge, deltas, 0)]];
  }
  return [];
}

/** The breakpoints of the driven end at `index` along the tick's path,
 * or `[]` where that end carries no jump plan. */
export function edgeCuts(program: LoadedProgram, edge: ProgramEdge,
                         values: Record<string, number>,
                         deltas: Record<string, number>,
                         index: number): number[] {
  if (edge.kind === 'block') {
    return blockCuts(program, edge.block!, values, deltas);
  }
  if (edge.kind !== 'law') return [];
  const plan = edge.plans[index];
  if (plan === null && edge.kinks[index] === null) return [];
  const start = inputsOf(edge, values);
  const delta: Record<string, number> = {};
  for (const key of edge.needs) delta[key] = deltas[key];
  if (plan === null) {
    // A law with NO jump node at all: its only breakpoints are its own
    // KINKS, over the whole tick as one piece. Left returning `[]` here,
    // `locate` would divide straight THROUGH the kink -- not a rounding
    // error but a wrong stop (openspec `solve-at-the-kink`, design
    // D4 (c)).
    return kinkedEndCuts(program, edge.kinks[index]!, start, delta);
  }
  const reading = edge.retained.length > 0 ? edge.retained[index] : null;
  if (reading !== null) {
    return retainedCuts(program, reading, start, delta, edge.description,
                        edge.gives[index]);
  }
  return planCuts(program, plan, start, delta, edge.description,
                  edge.gives[index]);
}
