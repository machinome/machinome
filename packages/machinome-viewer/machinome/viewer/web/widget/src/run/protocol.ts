/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The message protocol between the main thread and the run (design §2).
//
// One request type carries the cadence; everything else is a request
// with a correlated reply. The types live here and are shared by both
// sides, so the compiler checks the wire.
//
// A bank travels POSITIONALLY, as a `Float64Array` in the `order` the
// `ready` message fixed once, and `moved` is indices into it: a
// twelve-coordinate machine costs 96 bytes a frame and a three-hundred
// one costs 2.4 kB, where a string-keyed object would cost a structured
// clone of three hundred keys sixty times a second for no gain.

import type { CommandStatus } from './commands';
import type { CrossingRecord } from './jumps';
import type { ProgramCoordinate, RefusalKind } from './program';
import type { RunDocument } from './program';
import type { RunState, StopRecord } from './run';

// ---------------------------------------------------------------------
// main -> worker

export interface LoadRequest {
  t: 'load';
  /** The program-bearing keys only: the tree, the pieces and the
   * animation block never cross. */
  document: RunDocument;
  dt: number;
  record: number | null;
  sourceUrl?: string;
}

export interface AdvanceRequest {
  t: 'advance';
  id: number;
  ticks: number;
}

export interface CommandRequest {
  t: 'command';
  id: number;
  op: 'move' | 'rate' | 'trigger' | 'cancel';
  input?: string;
  name?: string;
  by?: number;
  to?: number;
  duration?: number;
  rate?: number;
}

export interface ControlRequest {
  t: 'control';
  id: number;
  op: 'reset' | 'snapshot' | 'restore';
  state?: RunState;
}

export interface DisposeRequest {
  t: 'dispose';
}

export type Request =
  LoadRequest | AdvanceRequest | CommandRequest | ControlRequest
  | DisposeRequest;

// ---------------------------------------------------------------------
// worker -> main

export interface CommandView {
  handle: number;
  input: string;
  kind: 'move' | 'rate';
  status: CommandStatus;
  requested: number | null;
  admitted: number;
  remaining: number | null;
  rate: number | null;
}

export interface ReadyReply {
  t: 'ready';
  id: number;
  identity: string;
  clock: string;
  dt: number;
  /** The bank's id order, fixed at load; every `bank` afterwards is a
   * positional array in it and every `moved` is indices into it. */
  order: string[];
  coordinates: Record<string, ProgramCoordinate>;
  bank: Float64Array<ArrayBufferLike>;
}

export interface FrameReply {
  t: 'frame';
  id: number;
  tick: number;
  clock: number;
  bank: Float64Array<ArrayBufferLike>;
  moved: number[];
  crossings: CrossingRecord[];
  stops: StopRecord[];
  commands: CommandView[];
}

export interface OutcomeReply {
  t: 'outcome';
  id: number;
  handle: number;
  input: string;
  status: CommandStatus;
  admitted: number;
  message?: string;
}

/** A TICK that committed nothing, carrying the framework's own message
 * text. The run pauses at a refusal rather than retrying the same
 * admissions sixty times a second. */
export interface RefusalReply {
  t: 'refusal';
  id: number;
  tick: number;
  kind: RefusalKind | 'unknown';
  message: string;
}

/** A REQUEST the run declined, leaving the run untouched. */
export interface ErrorReply {
  t: 'error';
  id: number;
  message: string;
}

/** What a command request CREATED: one handle per command the run
 * issued for it. A `trigger` claims one per input it moves, in issue
 * order, and a caller cannot know how many until the run says. */
export interface IssuedReply {
  t: 'issued';
  id: number;
  handles: number[];
}

export interface StateReply {
  t: 'state';
  id: number;
  state: RunState;
}

export type Reply =
  ReadyReply | FrameReply | OutcomeReply | RefusalReply | ErrorReply
  | IssuedReply | StateReply;

// ---------------------------------------------------------------------
// Encoding

/** The bank as a positional array in `order`. */
export function bankOf(state: Record<string, number>,
                       order: readonly string[]):
Float64Array<ArrayBufferLike> {
  const found = new Float64Array(order.length);
  order.forEach((id, index) => { found[index] = state[id]; });
  return found;
}

/** The indices of every position whose value moved between two banks.
 * `Object.is` so a coordinate that reached exactly the value it held is
 * not reported as moved, and a NaN is reported once rather than every
 * frame. */
export function movedIndices(before: Float64Array<ArrayBufferLike>,
                             after: Float64Array<ArrayBufferLike>):
number[] {
  const found: number[] = [];
  for (let index = 0; index < after.length; index += 1) {
    if (!Object.is(before[index], after[index])) found.push(index);
  }
  return found;
}

/** Those indices back as qualified ids, which is what the tree's bound
 * re-evaluation reads. */
export function namesOf(order: readonly string[],
                        indices: readonly number[]): string[] {
  return indices.map((index) => order[index]);
}

export function refusalOf(error: unknown, id: number, tick: number,
                          kind: RefusalKind | null): RefusalReply {
  return {
    t: 'refusal',
    id,
    tick,
    kind: kind ?? 'unknown',
    message: error instanceof Error ? error.message : String(error),
  };
}

export function errorOf(error: unknown, id: number): ErrorReply {
  return {
    t: 'error',
    id,
    message: error instanceof Error ? error.message : String(error),
  };
}
