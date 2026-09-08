/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// How fast the timeline runs, and what the readout says (OpenSpec change
// `real-time-playback`). Pure on purpose: nothing here touches the DOM or
// three.js, so it is decided and tested in node and `viewer.ts` renders
// exactly what it returns.
//
// The framework declares what one turn of `$t` IS -- `animation.loop`,
// the seconds of machine time a turn covers, when the root declares a
// time base -- and the expressions it publishes already carry the
// multiplication. Speed is the viewer's decision: the maker chooses how
// fast to watch, and the default is real time.

import type { Manifest } from './types';

export type Animation = Manifest['animation'];

/** The multipliers the speed control offers: slow motion for a fast
 * mechanism, thousands of times real time for a clock. */
export const SPEED_LADDER: readonly number[] =
  [0.1, 0.25, 0.5, 1, 2, 5, 10, 60, 360, 3600];

/** Distance between adjacent scrub positions when `frames` counts the
 * positions, including both 0 and 1. A single static frame still needs a
 * valid positive HTML range step. */
export function timelineStep(frames: number): number {
  return frames > 1 ? 1 / (frames - 1) : 1;
}

/** Integer slider position for a normalized timeline value. HTML range
 * validation can represent this exactly even when the normalized step is a
 * repeating decimal such as 1/359. */
export function timelinePosition(time: number, frames: number): number {
  return time * Math.max(frames - 1, 0);
}

/** Normalized timeline value for an integer slider position. */
export function timelineTime(position: number, frames: number): number {
  return frames > 1 ? position / (frames - 1) : 0;
}

/** Wall-clock seconds one turn of `$t` takes. Without a declared loop
 * this is `frames / fps`, exactly as it always was, and speed is
 * meaningless; with one it is the loop divided by the speed. */
export function cycleSecondsFor(animation: Animation, speed: number): number {
  if (animation.loop === undefined || animation.loop === null) {
    return animation.frames / animation.fps;
  }
  return animation.loop / speed;
}

/** The next 0..1 time after `elapsed` wall seconds of a cycle. */
export function advance(time: number, elapsed: number, cycleSeconds: number): number {
  return (time + elapsed / cycleSeconds) % 1;
}

/** The ladder with `speed` in it: a host-set value the ladder lacks is
 * still offered, in order, so the control always shows the truth. */
export function ladderFor(speed: number): number[] {
  if (SPEED_LADDER.includes(speed)) {
    return [...SPEED_LADDER];
  }
  return [...SPEED_LADDER, speed].sort((a, b) => a - b);
}

/** A positive finite multiplier, or a loud refusal naming the value. */
export function assertSpeed(speed: number): number {
  if (typeof speed !== 'number' || !Number.isFinite(speed) || speed <= 0) {
    throw new Error(
      `Playback speed must be a positive finite multiplier, not ${speed}`);
  }
  return speed;
}

/** The machine time at `seconds` into a loop of `loop` seconds, in the
 * form the loop's length calls for: `h:mm:ss` for an hour or more,
 * `m:ss.s` for a minute or more, seconds with two decimals otherwise. */
export function formatMachineTime(seconds: number, loop: number): string {
  if (loop >= 3600) {
    const whole = Math.floor(seconds);
    const h = Math.floor(whole / 3600);
    const m = Math.floor((whole % 3600) / 60);
    const s = whole % 60;
    return `${h}:${pad(m)}:${pad(s)}`;
  }
  if (loop >= 60) {
    const m = Math.floor(seconds / 60);
    const s = seconds - m * 60;
    const tenths = (Math.round(s * 10) / 10).toFixed(1);
    return `${m}:${tenths.length < 4 ? '0' : ''}${tenths}`;
  }
  return `${seconds.toFixed(2)} s`;
}

function pad(value: number): string {
  return value < 10 ? `0${value}` : String(value);
}
