/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// HOW FAR ONE RENDERED FRAME ADVANCES A CLOCKED MACHINE'S CLOCK
// (OpenSpec `run-the-clock`, design §5).
//
// Pure on purpose, exactly as `playback.ts` is: nothing here touches the
// DOM, three.js or the machine, so the decision is made and tested in
// node and `viewer.ts` renders and calls. The transport's CADENCE
// belongs to the page -- the render loop is where the frames are -- and
// the machine stays the corpus's own library, with nothing about a frame
// decided inside it.
//
// The shape is the run's (`src/run/runtime.ts`'s `frame`, ADR-046/048):
// wall seconds since the previous frame, times the playback speed. Two
// differences, both decided rather than inherited:
//
//   - NO REMAINDER IS CARRIED. The run carries a debt because its `dt`
//     quantizes what a frame can earn; a clock request has no
//     quantization -- `by` may be any float -- so the frame's own
//     elapsed seconds are requested as they are. One fewer piece of
//     state, and ten frames of `by` equal one frame of ten times `by`,
//     instant for instant.
//   - THE CAP IS IN SECONDS, not in ticks. It is still four frames'
//     worth of the current speed: wall time beyond it is LOST, visibly,
//     because the seconds readout falls behind the clock on the wall.
//     Losing it is honest where firing a burst of events -- or refusing
//     the frame for crossing more surfaces than the machine admits --
//     is not.

/** One frame's budget, in wall seconds: the 60 Hz the run assumes
 * (`RunRuntime`'s own default). */
export const CLOCK_FRAME_BUDGET = 1 / 60;

/** The most one frame may advance the clock by, in SECONDS: four frames'
 * worth of machine time at the current speed. */
export function clockCap(speed: number,
                         frameBudget = CLOCK_FRAME_BUDGET): number {
  return 4 * speed * frameBudget;
}

/** The seconds ONE rendered frame advances the clock by, from the wall
 * seconds it reports and the playback speed.
 *
 * Zero for a frame of no length, and never negative: a clock request
 * that ran backwards would be refused by the machine, and a frame is not
 * where a maker would learn that. */
export function clockAdvance(elapsedWallSeconds: number, speed: number,
                             frameBudget = CLOCK_FRAME_BUDGET): number {
  if (!Number.isFinite(elapsedWallSeconds) || elapsedWallSeconds <= 0) {
    return 0;
  }
  return Math.min(elapsedWallSeconds * speed, clockCap(speed, frameBudget));
}
