/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The main thread's side of the run (design D2, D3, D8, D9).
//
// Per animation frame the main thread computes how many ticks the
// elapsed wall time has earned, sends ONE `advance` message, and renders
// the bank of the reply. It sends the next `advance` only after the
// reply arrives: one advance in flight, always. That single rule settles
// three questions at once --
//
//   * a hidden page gets no animation frame, sends no advance, and the
//     run stops where it stands: nothing accumulates;
//   * a slow tick drops DISPLAY frames and never mechanics: no tick is
//     skipped, the next advance simply asks for the ticks the stall
//     earned, and the wall-time debt is capped so a long stall cannot
//     produce an unbounded burst;
//   * commands reach the worker in issue order and are applied before
//     the next tick it integrates.
//
// A page whose Content-Security-Policy forbids a blob worker throws at
// `new Worker(...)`. That is caught ONCE, the same engine runs in-thread,
// and `runsInWorker` says so on the handle. The mechanics are identical
// -- same module, same numbers -- and the only difference is which
// thread pays.

import { createSession } from './worker';
import {
  CommandView, Reply, Request,
} from './protocol';
import type {
  ErrorReply, FrameReply, OutcomeReply, ReadyReply, RefusalReply,
} from './protocol';
import type { ProgramCoordinate, RunDocument } from './program';
import type { CrossingRecord } from './jumps';
import type { RunState, StopRecord } from './run';

declare const __WORKER_SOURCE__: string;

/** How the main thread reaches the run: a real worker, an in-thread
 * session, or a test's fake. */
export interface EnginePort {
  post(request: Request): void;
  onReply(handler: (reply: Reply) => void): void;
  dispose(): void;
}

export interface Outcome {
  handle: number;
  input: string;
  status: string;
  admitted: number;
}

export interface CommittedFrame {
  tick: number;
  clock: number;
  bank: Record<string, number>;
  moved: string[];
  crossings: CrossingRecord[];
  stops: StopRecord[];
  commands: CommandView[];
}

export interface RuntimeOptions {
  dt: number;
  record?: number | null;
  /** Test seam: a port to use instead of building one. */
  port?: EnginePort;
  /** Test seam: how a worker is made, so a throwing constructor can be
   * exercised without a Content-Security-Policy. */
  workerFactory?: () => Worker;
  /** Seconds of wall time one displayed frame is budgeted, which is what
   * the advance cap is four of. */
  frameBudget?: number;
  sourceUrl?: string;
  autostart?: boolean;
}

function workerPort(factory: () => Worker): EnginePort {
  const worker = factory();
  return {
    post: (request) => worker.postMessage(request),
    onReply: (handler) => {
      worker.onmessage = (event: MessageEvent) => handler(event.data as Reply);
    },
    dispose: () => worker.terminate(),
  };
}

/** The same engine, on this thread. Replies are delivered through a
 * microtask so both paths are asynchronous in exactly the same shape --
 * a caller can never come to depend on the fallback being synchronous. */
function inThreadPort(): EnginePort {
  let handler: ((reply: Reply) => void) | undefined;
  let alive = true;
  const session = createSession((reply) => {
    if (!alive) return;
    const deliver = handler;
    if (deliver !== undefined) queueMicrotask(() => deliver(reply));
  });
  return {
    post: (request) => { if (alive) session.handle(request); },
    onReply: (fn) => { handler = fn; },
    dispose: () => { alive = false; },
  };
}

/** The worker built from the bundled source, as a blob URL (design D3).
 * There is exactly one published artifact, so the worker's code travels
 * inside it. */
function blobWorker(): Worker {
  const source = typeof __WORKER_SOURCE__ === 'string'
    ? __WORKER_SOURCE__ : '';
  if (source === '') {
    throw new Error('this build carries no worker source');
  }
  const url = URL.createObjectURL(
    new Blob([source], { type: 'text/javascript' }));
  try {
    return new Worker(url);
  } finally {
    URL.revokeObjectURL(url);
  }
}

export class RunRuntime {
  /** False when the page could not create the worker and the same
   * engine is running on this thread instead. */
  readonly runsInWorker: boolean;

  readonly ready: Promise<void>;

  private readonly port: EnginePort;
  private readonly frameBudget: number;
  private nextId = 1;
  private readonly pending = new Map<number, {
    resolve: (value: never) => void; reject: (error: Error) => void;
  }>();
  private readonly awaiting = new Map<number, {
    expected: number | null; got: Outcome[];
    resolve: (value: Outcome[]) => void;
  }>();
  private readonly frameListeners = new Set<(frame: CommittedFrame) => void>();
  private readonly outcomeListeners = new Set<(outcome: Outcome) => void>();
  private readonly refusalListeners = new Set<(refusal: RefusalReply) => void>();

  private identityOf = '';
  private clockName = 'time';
  private order: string[] = [];
  private coordinateTable: Record<string, ProgramCoordinate> = {};
  private latest: Record<string, number> = {};
  private tickCount = 0;
  private elapsed = 0;
  private playing = false;
  private outstanding: number | null = null;
  private debt = 0;
  private disposed = false;

  private constructor(document: RunDocument, options: RuntimeOptions) {
    this.frameBudget = options.frameBudget ?? 1 / 60;
    let port = options.port;
    let inWorker = false;
    if (port === undefined) {
      try {
        port = workerPort(options.workerFactory ?? blobWorker);
        inWorker = true;
      } catch {
        // A page whose policy forbids a blob worker. Silently degrading
        // would be wrong; failing to open the machine would be worse.
        port = inThreadPort();
      }
    }
    this.runsInWorker = inWorker;
    this.port = port;
    this.ready = new Promise<void>((resolve, reject) => {
      this.pending.set(0, {
        resolve: resolve as unknown as (value: never) => void, reject,
      });
    });
    this.port.onReply((reply) => this.receive(reply));
    this.port.post({
      t: 'load',
      document,
      dt: options.dt,
      record: options.record ?? null,
      sourceUrl: options.sourceUrl,
    });
    this.playing = options.autostart === true;
  }

  static start(document: RunDocument, options: RuntimeOptions): RunRuntime {
    return new RunRuntime(document, options);
  }

  // ------------------------------------------------------------------
  // What a host reads

  identity(): string {
    return this.identityOf;
  }

  clock(): string {
    return this.clockName;
  }

  coordinates(): Record<string, ProgramCoordinate> {
    return this.coordinateTable;
  }

  ids(): readonly string[] {
    return this.order;
  }

  tick(): number {
    return this.tickCount;
  }

  /** Elapsed simulation seconds, which never wrap. */
  elapsedSeconds(): number {
    return this.elapsed;
  }

  bank(): Record<string, number> {
    return { ...this.latest };
  }

  running(): boolean {
    return this.playing;
  }

  start(): void {
    this.playing = true;
  }

  pause(): void {
    this.playing = false;
  }

  onFrame(listener: (frame: CommittedFrame) => void): () => void {
    this.frameListeners.add(listener);
    return () => { this.frameListeners.delete(listener); };
  }

  onOutcome(listener: (outcome: Outcome) => void): () => void {
    this.outcomeListeners.add(listener);
    return () => { this.outcomeListeners.delete(listener); };
  }

  onRefusal(listener: (refusal: RefusalReply) => void): () => void {
    this.refusalListeners.add(listener);
    return () => { this.refusalListeners.delete(listener); };
  }

  // ------------------------------------------------------------------
  // The cadence

  private speed = 1;

  setSpeed(speed: number): void {
    this.speed = speed;
  }

  /** One animation frame's worth of wall time. Speed is a multiple of
   * real time and changes how many ticks that earns -- never the step
   * size, so watching a machine faster does not simulate it coarser. */
  frame(elapsedWallSeconds: number): void {
    if (this.disposed || !this.playing) return;
    this.debt += elapsedWallSeconds * this.speed;
    // The debt is capped at four frames' worth (design D9): a stall
    // longer than that loses the wall time beyond the cap rather than
    // integrating it in a burst. Losing it is visible -- the elapsed
    // readout falls behind the clock on the wall -- and integrating it
    // is not.
    if (this.outstanding !== null) return;
    const earned = Math.floor(this.debt / this.dtOf());
    if (earned <= 0) {
      // The fractional REMAINDER is carried across frames, so x0.1 --
      // where one frame earns a fiftieth of a tick -- does not round to
      // zero ticks a frame and stall forever.
      return;
    }
    // The cap is four frames' worth of ticks (design D9). A stall longer
    // than that -- a garbage collection, a long-running extension, a
    // laptop lid -- LOSES the wall time beyond the cap rather than
    // integrating it in a burst: losing it is visible, because the
    // elapsed readout falls behind the clock on the wall, and
    // integrating it is not.
    const cap = Math.max(1, Math.floor(
      (4 * this.speed * this.frameBudget) / this.dtOf()));
    this.debt -= earned * this.dtOf();
    this.sendAdvance(Math.min(earned, cap));
  }

  private dt = 0;

  private dtOf(): number {
    return this.dt;
  }

  private sendAdvance(ticks: number): number {
    const id = this.nextId;
    this.nextId += 1;
    this.outstanding = id;
    this.port.post({ t: 'advance', id, ticks });
    return id;
  }

  /** Integrate exactly `ticks` ticks, whether or not the run is started
   * -- which is what makes a headless or a scripted drive
   * deterministic. */
  step(ticks = 1): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      const send = () => {
        const id = this.sendAdvance(ticks);
        this.pending.set(id, {
          resolve: resolve as unknown as (value: never) => void, reject,
        });
      };
      if (this.outstanding === null) send();
      else this.queue.push(send);
    });
  }

  private readonly queue: (() => void)[] = [];

  // ------------------------------------------------------------------
  // Requests

  move(input: string, request: { by?: number; to?: number;
                                 duration?: number }): Promise<Outcome[]> {
    return this.command({
      op: 'move', input, by: request.by, to: request.to,
      duration: request.duration,
    });
  }

  rate(input: string, rate: number): Promise<Outcome[]> {
    return this.command({ op: 'rate', input, rate });
  }

  trigger(name: string): Promise<Outcome[]> {
    return this.command({ op: 'trigger', name });
  }

  cancel(input: string): void {
    const id = this.nextId;
    this.nextId += 1;
    this.port.post({ t: 'command', id, op: 'cancel', input });
  }

  private command(
    args: Omit<Request & { t: 'command' }, 't' | 'id'>,
  ): Promise<Outcome[]> {
    const id = this.nextId;
    this.nextId += 1;
    return new Promise<Outcome[]>((resolve, reject) => {
      // How many handles this request created is the RUN's answer, not a
      // guess: an `issued` reply says so before the first of them
      // reports.
      this.awaiting.set(id, { expected: null, got: [], resolve });
      this.pending.set(id, {
        resolve: (() => undefined) as unknown as (value: never) => void,
        reject,
      });
      this.port.post({ t: 'command', id, ...args } as Request);
    });
  }

  snapshot(): Promise<RunState> {
    return this.control('snapshot');
  }

  restore(state: RunState): Promise<void> {
    return this.control('restore', state);
  }

  reset(): Promise<void> {
    return this.control('reset');
  }

  private control(op: 'reset' | 'snapshot' | 'restore',
                  state?: RunState): Promise<never> {
    const id = this.nextId;
    this.nextId += 1;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.port.post({ t: 'control', id, op, state });
    });
  }

  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    this.port.post({ t: 'dispose' });
    this.port.dispose();
    this.frameListeners.clear();
    this.outcomeListeners.clear();
    this.refusalListeners.clear();
  }

  // ------------------------------------------------------------------
  // Replies

  private receive(reply: Reply): void {
    if (reply.t === 'ready') {
      this.adopt(reply);
      return;
    }
    if (reply.t === 'frame') {
      this.commit(reply);
      return;
    }
    if (reply.t === 'outcome') {
      this.settle(reply);
      return;
    }
    if (reply.t === 'refusal') {
      this.refuse(reply);
      return;
    }
    if (reply.t === 'issued') {
      const waiting = this.awaiting.get(reply.id);
      if (waiting !== undefined) {
        waiting.expected = reply.handles.length;
        this.finish(reply.id, waiting);
      }
      return;
    }
    if (reply.t === 'state') {
      const waiting = this.pending.get(reply.id);
      this.pending.delete(reply.id);
      waiting?.resolve(reply.state as never);
      return;
    }
    this.fail(reply);
  }

  private adopt(reply: ReadyReply): void {
    this.identityOf = reply.identity;
    this.clockName = reply.clock;
    this.dt = reply.dt;
    this.order = reply.order;
    this.coordinateTable = reply.coordinates;
    this.latest = {};
    reply.order.forEach((id, index) => {
      this.latest[id] = reply.bank[index];
    });
    const waiting = this.pending.get(0);
    this.pending.delete(0);
    waiting?.resolve(undefined as never);
  }

  private commit(reply: FrameReply): void {
    this.tickCount = reply.tick;
    this.elapsed = reply.clock;
    this.order.forEach((id, index) => { this.latest[id] = reply.bank[index]; });
    const frame: CommittedFrame = {
      tick: reply.tick,
      clock: reply.clock,
      bank: { ...this.latest },
      moved: reply.moved.map((index) => this.order[index]),
      crossings: reply.crossings,
      stops: reply.stops,
      commands: reply.commands,
    };
    for (const listener of [...this.frameListeners]) listener(frame);
    const waiting = this.pending.get(reply.id);
    if (waiting !== undefined) {
      this.pending.delete(reply.id);
      waiting.resolve(undefined as never);
    }
    this.done(reply.id);
  }

  private settle(reply: OutcomeReply): void {
    const outcome: Outcome = {
      handle: reply.handle,
      input: reply.input,
      status: reply.status,
      admitted: reply.admitted,
    };
    for (const listener of [...this.outcomeListeners]) listener(outcome);
    const waiting = this.awaiting.get(reply.id);
    if (waiting === undefined) return;
    waiting.got.push(outcome);
    this.finish(reply.id, waiting);
  }

  /** A command request settles when every handle it created has
   * retired -- a `trigger` claims one per input it moves, in issue
   * order, and a release creates none at all. */
  private finish(id: number, waiting: {
    expected: number | null; got: Outcome[];
    resolve: (value: Outcome[]) => void;
  }): void {
    if (waiting.expected === null) return;
    if (waiting.got.length < waiting.expected) return;
    this.awaiting.delete(id);
    this.pending.delete(id);
    waiting.resolve(waiting.got);
  }

  private refuse(reply: RefusalReply): void {
    this.tickCount = reply.tick;
    // The run PAUSES at a refusal rather than retrying the same
    // admissions sixty times a second.
    this.playing = false;
    for (const listener of [...this.refusalListeners]) listener(reply);
    const waiting = this.pending.get(reply.id);
    if (waiting !== undefined) {
      this.pending.delete(reply.id);
      waiting.reject(new Error(reply.message));
    }
    this.done(reply.id);
  }

  private fail(reply: ErrorReply): void {
    const waiting = this.pending.get(reply.id);
    this.pending.delete(reply.id);
    this.awaiting.delete(reply.id);
    if (waiting !== undefined) waiting.reject(new Error(reply.message));
    else if (reply.id === 0) {
      const load = this.pending.get(0);
      this.pending.delete(0);
      load?.reject(new Error(reply.message));
    }
    this.done(reply.id);
  }

  private done(id: number): void {
    if (this.outstanding !== id) return;
    this.outstanding = null;
    const next = this.queue.shift();
    if (next !== undefined) next();
  }
}
