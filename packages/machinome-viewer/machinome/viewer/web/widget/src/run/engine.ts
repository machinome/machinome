/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The engine's façade (`simulation/sim.py`'s running branch): build from
// the program-bearing keys of a document, take commands, integrate
// ticks, and answer state.
//
// This is a pure library: no DOM, no three.js, no `postMessage`. That is
// what lets the conformance corpus replay it IN-THREAD under vitest,
// where a divergence is a stack trace rather than a message that never
// came back -- and `worker.ts` is a thin decoder around exactly this
// object.

import { Command } from './commands';
import { CrossingRecord } from './jumps';
import { loadProgram, ProgramCoordinate } from './program';
import type { LoadedProgram, RunDocument } from './program';
import { Run, RunState, StopRecord, TrajectoryEntry, MoveRequest } from './run';

export interface EngineOptions {
  /** Simulated seconds per tick. The document publishes none: the step
   * is the executing runtime's choice. */
  dt: number;
  /** How many recent ticks to keep in each of the three rings, or null
   * for no record at all. */
  record?: number | null;
  /** Quoted in a refusal. */
  sourceUrl?: string;
}

export class Engine {
  private readonly run: Run;

  constructor(readonly program: LoadedProgram, readonly dt: number,
              record: number | null = null) {
    this.run = new Run(program, dt, record);
  }

  static load(document: RunDocument, options: EngineOptions): Engine {
    const program = loadProgram(document, options.sourceUrl ?? 'the document');
    return new Engine(program, options.dt, options.record ?? null);
  }

  // ------------------------------------------------------------------
  // What the machine is

  identity(): string {
    return this.program.identity;
  }

  clockName(): string {
    return this.program.clock;
  }

  order(): readonly string[] {
    return this.program.order;
  }

  coordinates(): Record<string, ProgramCoordinate> {
    return Object.fromEntries(Object.entries(this.program.coordinates)
      .map(([id, entry]) => [id, { ...entry }]));
  }

  // ------------------------------------------------------------------
  // Where it stands

  tick(): number {
    return this.run.tick();
  }

  /** Elapsed simulation seconds, which never wrap. */
  clock(): number {
    return this.run.clock();
  }

  state(): Record<string, number> {
    return this.run.state();
  }

  positions(): Float64Array<ArrayBufferLike> {
    return this.run.positions();
  }

  commands(): Command[] {
    return this.run.commands();
  }

  crossings(): CrossingRecord[] {
    return this.run.crossings();
  }

  stops(): StopRecord[] {
    return this.run.stops();
  }

  trajectory(): TrajectoryEntry[] {
    return this.run.trajectory();
  }

  // ------------------------------------------------------------------
  // What it is told

  move(input: string, request: MoveRequest): Command {
    return this.run.move(input, request);
  }

  rate(input: string, rate: number): Command | null {
    return this.run.rate(input, rate);
  }

  trigger(name: string): Command[] {
    return this.run.trigger(name);
  }

  cancel(input: string): Command | null {
    return this.run.cancel(input);
  }

  /** Integrate exactly `ticks` ticks. */
  advance(ticks = 1): void {
    for (let step = 0; step < ticks; step += 1) this.run.advance();
  }

  /** `seconds` as a whole number of ticks, refusing a duration that is
   * not one (`Sim._ticks`). */
  ticksFor(seconds: number, what = 'duration'): number {
    return this.run.ticksFor(seconds, what);
  }

  snapshot(): RunState {
    return this.run.snapshot();
  }

  restore(state: RunState): void {
    this.run.restore(state);
  }

  reset(): void {
    this.run.reset();
  }
}
