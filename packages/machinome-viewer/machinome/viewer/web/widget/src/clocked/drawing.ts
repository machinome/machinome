/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// ONE TRANSITION, DRAWN over its declared duration (OpenSpec
// `play-the-instruction`, design §3, §4, §5; machinome ADR-129).
//
// A clocked instruction is ONE REQUEST: the machine makes it once, at
// the press, and stands at its end from that instant. What is left is a
// PICTURE of a transition that has already happened, and this module is
// the whole of the rule for drawing it.
//
// It takes the request, the bank the machine stood at BEFORE it and the
// declared duration -- and NO MACHINE. That is the structural half of
// "one solve per press": the frame loop's collaborator has nothing to
// solve with, so a later edit cannot quietly put a request back in the
// frame loop. It is also why the rule is decided and tested in plain
// node, where `clockedControls.ts` and `bounds.ts` already are, rather
// than only in a browser.
//
// No DOM, no three.js, no machine. `viewer.ts` advances one of these in
// the render loop beside the clock's transport and poses each frame
// through the change set it already has.

import type { ClockedRequest } from './machine';

/** One frame of a drawing: where the moved input stands, the whole bank
 * as the model should show it, the ids that CHANGED since the frame
 * before, and whether this is the last one. */
export interface DrawnFrame {
  /** The moved input's value at this frame, in NATIVE units -- the units
   * the request's two ends speak. */
  value: number;
  /** The bank to pose from: the start bank, with every commit the
   * fraction has reached applied in path order, and the moved input at
   * `value`. */
  bank: Record<string, number>;
  /** The ids whose value differs from the frame before this one, so a
   * pose re-evaluates only what moved. The FIRST frame is measured
   * against the request's own END bank, because that is where the tree
   * stands when the drawing begins: the request posed it as part of
   * itself (ADR-125's atomicity). */
  moved: string[];
  /** True at and past the declared duration. */
  done: boolean;
}

export interface Drawing {
  /** The id of the one input this transition moves. */
  readonly input: string;
  /** The frame at `elapsedSeconds` since the drawing began. Elapsed time
   * is TOTAL, as `Ramp.valueAt` takes it: a frame is a sample of a
   * function of time, not an accumulation of deltas. */
  advance(elapsedSeconds: number): DrawnFrame;
  /** The LAST frame, from wherever the drawing stands: the request's own
   * end with every commit applied. */
  land(): DrawnFrame;
}

/** Draw `request` -- already made, already committed -- from `start`
 * over `duration` wall seconds.
 *
 * `integer` is whether the moved input is declared a whole number.
 *
 * The duration is WALL seconds and the playback speed does not scale it
 * (design §6): the speed belongs to things that have MACHINE time -- the
 * timeline's loop and the clock's transport -- and an instruction's
 * duration is not machine time. It is what the posed `Ramp` does, which
 * is what "just like the fast_curta" means. */
export function drawing(request: ClockedRequest,
                        start: Record<string, number>,
                        duration: number, integer: boolean): Drawing {
  const { input, origin, end, commits } = request;

  /** How far along the path `elapsedSeconds` stands, in [0, 1]. A
   * duration of zero is ALREADY over: the transition lands in one
   * pose. */
  const fractionAt = (elapsedSeconds: number): number => {
    if (!(duration > 0)) return 1;
    if (!(elapsedSeconds > 0)) return 0;
    return elapsedSeconds >= duration ? 1 : elapsedSeconds / duration;
  };

  /** The moved input's value at `fraction`: `Ramp`'s own linear rule,
   * with ONE deliberate difference.
   *
   * Endpoints are contract and the values between are sampling, exactly
   * as `Ramp` has it: at the end the value is the request's own `end`
   * ITSELF rather than a computed approximation of it, so the last frame
   * stands on the float the machine stands on.
   *
   * The difference is a whole-number input. `Ramp` adds
   * `Math.floor(delta)`, which on a FALLING ramp overshoots by up to one
   * native unit -- a drawn value past the machine's own `end`, showing a
   * tooth the machine never turned. This TRUNCATES TOWARD THE ORIGIN
   * instead: identical to the floor for a rising travel, and never past
   * `end` for a falling one. `Ramp` itself is untouched -- a posed
   * document's ramps are not this module's business. */
  const valueAt = (fraction: number): number => {
    if (fraction >= 1) return end;
    if (fraction <= 0) return origin;
    const delta = (end - origin) * fraction;
    return origin + (integer ? Math.trunc(delta) : delta);
  };

  /** The bank at `fraction`, with the moved input already placed.
   *
   * Commits are keyed on the published FRACTION and never on the value
   * (design §4): the fraction rises from 0 to 1 whichever way the input
   * travels, so a downward transition is drawn by this same line; and it
   * is exact where a drawn value is quantised by the truncation above,
   * which would otherwise apply a commit a frame early or late. */
  const bankAt = (fraction: number, value: number):
  Record<string, number> => {
    const bank: Record<string, number> = { ...start };
    for (const commit of commits) {
      if (commit.fraction <= fraction) Object.assign(bank, commit.targets);
    }
    bank[input] = value;
    return bank;
  };

  // Where the TREE stands as this drawing begins: the request's own end,
  // with every commit applied, which the request posed as part of
  // itself. The first frame's `moved` is measured against it, so frame 0
  // un-poses exactly what the transition is about to re-play.
  let previous = bankAt(1, end);

  const frameAt = (fraction: number): DrawnFrame => {
    const value = valueAt(fraction);
    const bank = bankAt(fraction, value);
    const moved = Object.keys(bank).filter(
      (id) => bank[id] !== previous[id]);
    previous = bank;
    return { value, bank, moved, done: fraction >= 1 };
  };

  return {
    input,
    advance: (elapsedSeconds: number) => frameAt(fractionAt(elapsedSeconds)),
    land: () => frameAt(1),
  };
}
