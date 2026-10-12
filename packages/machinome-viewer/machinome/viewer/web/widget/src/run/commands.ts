/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// The handle a `move` or a `rate` returns, and goes on reporting after
// the run has retired it (`simulation/run.py`'s `class Command` and
// `simulation/driver.py`'s `RampProgram`, reproduced).
//
// `requested` and `admitted` are in the input's DESIGN units -- the
// units an instruction target is stated in -- while the bank stays
// native. `blocked` is the status a command whose input was STOPPED
// retires with: the tick happened and the machine would not go further,
// so `admitted` is the travel it actually made and nothing anywhere
// remembers the rest.

import { ManifestDriver } from '../types';

export type CommandStatus =
  'active' | 'completed' | 'blocked' | 'refused' | 'cancelled';

export type CommandKind = 'move' | 'rate';

/** One command frozen into a snapshot entry. */
export interface CommandRecord {
  input: string;
  kind: CommandKind;
  native: number | null;
  nativeRate: number | null;
  ticks: number | null;
  started: number;
  admitted: number;
  status: CommandStatus;
  /** Exact converted native endpoint of an absolute move, when present. */
  target?: number;
}

/** `native` driver state back in the DESIGN units a caller states a move
 * in -- the inverse of `toNative`'s scaling. */
export function designOf(declaration: ManifestDriver, native: number): number {
  if (declaration.scale === null || declaration.scale === undefined) {
    return native;
  }
  return native * declaration.scale;
}

/** A linear ramp: `delta` distributed over `ticks` ticks.
 *
 * For an integer driver the distribution is `start + floor(delta*k/n)`,
 * so every intermediate value is a whole native unit and `k === n` lands
 * exactly on the target. `Math.floor` is Python's `//` for these
 * operands and, unlike truncation, agrees for a negative delta. */
class Ramp {
  private readonly delta: number;

  constructor(private readonly start: number, private readonly target: number,
              private readonly ticks: number,
              private readonly integer: boolean) {
    this.delta = target - start;
  }

  valueAt(k: number): number {
    if (k >= this.ticks) return this.target;
    if (this.integer) {
      return this.start + Math.floor((this.delta * k) / this.ticks);
    }
    return this.start + (this.delta * k) / this.ticks;
  }
}

export interface CommandSpec {
  native?: number | null;
  target?: number;
  nativeRate?: number | null;
  ticks?: number | null;
  value?: number;
}

export class Command {
  status: CommandStatus = 'active';
  admittedNative = 0;
  readonly native: number | null;
  readonly nativeRate: number | null;
  readonly targetNative: number | undefined;
  readonly ticks: number | null;
  private readonly ramp: Ramp | null;

  constructor(
    readonly input: string,
    readonly kind: CommandKind,
    readonly declaration: ManifestDriver,
    readonly started: number,
    spec: CommandSpec = {},
  ) {
    this.native = spec.native ?? null;
    this.targetNative = spec.target;
    this.nativeRate = spec.nativeRate ?? null;
    this.ticks = spec.ticks ?? null;
    this.ramp = kind === 'move' && this.ticks
      ? new Ramp(spec.value ?? 0, (spec.value ?? 0) + (this.native as number),
                 this.ticks, declaration.dtype === 'int')
      : null;
  }

  /** The travel asked for, in design units -- `null` for a rate, which
   * states a speed and no total. */
  get requested(): number | null {
    if (this.kind === 'rate') return null;
    return designOf(this.declaration, this.native as number);
  }

  /** The travel actually admitted so far, in design units. */
  get admitted(): number {
    return designOf(this.declaration, this.admittedNative);
  }

  get remaining(): number | null {
    if (this.kind === 'rate') return null;
    return (this.requested as number) - this.admitted;
  }

  /** A rate's speed in design units per simulated second. */
  get rate(): number | null {
    if (this.kind !== 'rate') return null;
    return designOf(this.declaration, this.nativeRate as number);
  }

  /** Stop this command where it stands. A command already retired keeps
   * whatever it reported. */
  cancel(): this {
    if (this.status === 'active') this.status = 'cancelled';
    return this;
  }

  /** How far this command moves its input over the tick ENDING at
   * `tick` -- a pure function of the tick count since it started, so a
   * replayed run admits exactly the same travel. */
  admits(tick: number, dt: number): number {
    const elapsed = tick - this.started;
    if (elapsed < 0) return 0;
    if (this.kind === 'rate') {
      return this.cumulative(elapsed, dt) - this.cumulative(elapsed - 1, dt);
    }
    if (!this.ticks) {
      // A zero-duration move lands entirely at the tick it was requested
      // on, and nothing after it.
      return elapsed === 0 ? (this.native as number) : 0;
    }
    if (elapsed === 0 || elapsed > this.ticks) return 0;
    return (this.ramp as Ramp).valueAt(elapsed)
      - (this.ramp as Ramp).valueAt(elapsed - 1);
  }

  private cumulative(elapsed: number, dt: number): number {
    if (elapsed <= 0) return 0;
    const travelled = (this.nativeRate as number) * dt * elapsed;
    // TRUNCATED toward zero, so a negative rate rounds the way a
    // positive one does: flooring would make the state LEAD the ideal by
    // up to one native unit where a positive rate LAGS it.
    if (this.declaration.dtype !== 'int') return travelled;
    // `math.trunc` returns a Python int, which has no signed zero.
    const whole = Math.trunc(travelled);
    return whole === 0 ? 0 : whole;
  }

  finished(tick: number): boolean {
    if (this.kind === 'rate') return false;
    return tick - this.started >= (this.ticks ?? 0);
  }

  record(): CommandRecord {
    return {
      input: this.input,
      kind: this.kind,
      native: this.native,
      nativeRate: this.nativeRate,
      ticks: this.ticks,
      started: this.started,
      admitted: this.admittedNative,
      status: this.status,
      ...(this.targetNative !== undefined ? { target: this.targetNative } : {}),
    };
  }
}
