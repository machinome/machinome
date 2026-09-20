/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The worker's side: a THIN DECODER around the engine (design D1).
//
// Nothing here decides anything about mechanics. It loads a program,
// applies the requests it is handed in the order they arrive, integrates
// the ticks it is asked for, and posts back one frame per advance with
// the committed bank, what moved in it, the crossings and stops located
// inside it, and every command that is still active or retired in it.
//
// `createSession` is the whole worker, testable with a plain function
// for `post`: the bottom of this file wires it to `self` only when it is
// actually running inside a worker, so importing this module in-thread
// (the fallback of D3, and every test) costs nothing.

import { Command } from './commands';
import { Engine } from './engine';
import {
  bankOf, CommandView, errorOf, movedIndices, refusalOf, Reply, Request,
} from './protocol';
import { refusalKind } from './program';

interface Tracked {
  handle: number;
  command: Command;
  request: number;
}

export interface Session {
  handle(request: Request): void;
}

export function createSession(post: (reply: Reply) => void): Session {
  let engine: Engine | null = null;
  let order: readonly string[] = [];
  let previous: Float64Array<ArrayBufferLike> = new Float64Array(0);
  let crossingsSeen = 0;
  let stopsSeen = 0;
  let nextHandle = 0;
  const tracked: Tracked[] = [];

  const viewOf = (entry: Tracked): CommandView => ({
    handle: entry.handle,
    input: entry.command.input,
    kind: entry.command.kind,
    status: entry.command.status,
    requested: entry.command.requested,
    admitted: entry.command.admitted,
    remaining: entry.command.remaining,
    rate: entry.command.rate,
  });

  /** Every command that has retired since the last sweep, reported to
   * whoever asked for it. */
  const retire = (): void => {
    for (let index = tracked.length - 1; index >= 0; index -= 1) {
      const entry = tracked[index];
      if (entry.command.status === 'active') continue;
      post({
        t: 'outcome',
        id: entry.request,
        handle: entry.handle,
        input: entry.command.input,
        status: entry.command.status,
        admitted: entry.command.admitted,
      });
      tracked.splice(index, 1);
    }
  };

  const track = (command: Command, request: number): Tracked => {
    const entry = { handle: nextHandle, command, request };
    nextHandle += 1;
    tracked.push(entry);
    return entry;
  };

  const frame = (id: number, run: Engine): void => {
    const bank = run.positions();
    const allCrossings = run.crossings();
    const allStops = run.stops();
    const crossings = allCrossings.slice(crossingsSeen);
    const stops = allStops.slice(stopsSeen);
    crossingsSeen = allCrossings.length;
    stopsSeen = allStops.length;
    const moved = movedIndices(previous, bank);
    previous = bank;
    post({
      t: 'frame',
      id,
      tick: run.tick(),
      clock: run.clock(),
      bank,
      moved,
      crossings,
      stops,
      commands: tracked.map(viewOf),
    });
  };

  const handle = (request: Request): void => {
    if (request.t === 'dispose') {
      engine = null;
      tracked.length = 0;
      return;
    }
    if (request.t === 'load') {
      try {
        engine = Engine.load(request.document, {
          dt: request.dt,
          record: request.record,
          sourceUrl: request.sourceUrl,
        });
        order = engine.order();
        previous = bankOf(engine.state(), order);
        post({
          t: 'ready',
          id: 0,
          identity: engine.identity(),
          clock: engine.clockName(),
          dt: engine.dt,
          order: [...order],
          coordinates: engine.coordinates(),
          bank: previous,
        });
      } catch (error) {
        post(errorOf(error, 0));
      }
      return;
    }
    const run = engine;
    if (run === null) {
      post(errorOf(new Error('no program is loaded'), request.id));
      return;
    }
    if (request.t === 'advance') {
      try {
        run.advance(request.ticks);
      } catch (error) {
        // A TICK that committed nothing. The commands that moved are
        // already retired `refused` by the run itself.
        retire();
        post(refusalOf(error, request.id, run.tick(), refusalKind(error)));
        return;
      }
      retire();
      frame(request.id, run);
      return;
    }
    if (request.t === 'command') {
      const created: number[] = [];
      try {
        if (request.op === 'move') {
          created.push(track(run.move(request.input as string, {
            by: request.by, to: request.to, duration: request.duration,
          }), request.id).handle);
        } else if (request.op === 'rate') {
          const command = run.rate(request.input as string,
                                   request.rate as number);
          // A release -- `rate(input, 0)` -- creates nothing: it retires
          // the rate that was running, under the handle that created it.
          if (command !== null && request.rate !== 0) {
            created.push(track(command, request.id).handle);
          }
        } else if (request.op === 'trigger') {
          for (const command of run.trigger(request.name as string)) {
            created.push(track(command, request.id).handle);
          }
        } else {
          run.cancel(request.input as string);
        }
      } catch (error) {
        post(errorOf(error, request.id));
        return;
      }
      // Posted BEFORE any retirement, so a caller always learns how many
      // handles it is waiting for before the first of them reports.
      post({ t: 'issued', id: request.id, handles: created });
      // A zero-duration move settles at the current tick, so a command
      // may already be retired before any advance. Publish that commit
      // BEFORE its outcome: a paused host awaiting winding must see the
      // wound bank and pose without needing to advance time to refresh it.
      if (tracked.some(entry => entry.request === request.id
          && entry.command.kind === 'move' && entry.command.ticks === 0)) {
        frame(request.id, run);
      }
      retire();
      return;
    }
    // A control request.
    try {
      if (request.op === 'snapshot') {
        post({ t: 'state', id: request.id, state: run.snapshot() });
        return;
      }
      if (request.op === 'restore') {
        run.restore(request.state!);
      } else {
        run.reset();
      }
      retire();
      crossingsSeen = 0;
      stopsSeen = 0;
      frame(request.id, run);
    } catch (error) {
      post(errorOf(error, request.id));
    }
  };

  return { handle };
}

// Wired to the worker's own port only when this module is genuinely
// running inside one. In-thread -- the D3 fallback and every test -- the
// import costs nothing.
declare const self: {
  postMessage?: (message: unknown) => void;
  onmessage?: ((event: { data: Request }) => void) | null;
  importScripts?: unknown;
} | undefined;

if (typeof self !== 'undefined' && self !== null
    && typeof self.postMessage === 'function'
    && typeof self.importScripts !== 'undefined') {
  const session = createSession(
    (reply) => (self.postMessage as (message: unknown) => void)(reply));
  self.onmessage = (event: { data: Request }) => session.handle(event.data);
}
