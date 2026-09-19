/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import * as THREE from 'three';
import type {
  ViewerOptions, AnimationMode, DriverControlsMode, PartControlsMode,
  VectorInput,
} from './viewer';
import type { ViewerView } from './camera';
import { assertSpeed } from './playback';
import { DEFAULT_JOG, DEFAULT_NUDGE } from './runControls';
import type { JogPlan, NudgePlan } from './runControls';

/** The run's own mount options (OpenSpec `run-in-the-worker`, D6, D13).
 *
 * `dt` is the VIEWER's choice -- the document publishes none -- and is
 * fixed for the life of a mount, because a run state carries its step
 * size and a restore across two of them is refused by the framework's
 * own rule. Changing it means a new mount. */
export interface ResolvedRunOptions {
  dt: number;
  record: number | null;
  autostart: boolean;
  /** What a nudge and a jog ASK FOR (OpenSpec `drive-the-run-on-screen`,
   * design D3/D4). They configure the request a control will make and
   * write no coordinate anywhere: typing 5 into the amount moves
   * nothing, and the next `+` asks for five. */
  nudge: NudgePlan;
  jog: JogPlan;
}

/** 1/240 s: the step the campaign's own interface sketch uses, four
 * ticks per frame at 60 Hz and real time, and inside the
 * cadence-independent band the acceptance machine has already measured
 * (its narrowest carry window is 1/12 s, which is twenty ticks). */
export const DEFAULT_DT = 1 / 240;

/** 600 ticks, 2.5 s at the default step. */
export const DEFAULT_RECORD = 600;

/** A finite number a request can actually be stated in, or a loud
 * refusal naming the value. `nonNegative` is for a duration, which a
 * negative number is not. */
export function assertRequestValue(what: string, value: number,
                                   nonNegative = false): number {
  if (typeof value !== 'number' || !Number.isFinite(value)
      || (nonNegative && value < 0)) {
    throw new Error(
      `a run's ${what} must be a finite ${nonNegative ? 'non-negative ' : ''}`
      + `number; got ${value}.`);
  }
  return value;
}

export function assertDt(dt: number): number {
  if (typeof dt !== 'number' || !Number.isFinite(dt) || dt <= 0) {
    throw new Error(
      `a run's step size must be a positive number of simulated seconds ` +
      `per tick; got ${dt}.`);
  }
  return dt;
}

export interface ResolvedViewerOptions {
  renderMode: 'continuous' | 'on-demand';
  baseUrl: string | null;
  animation: AnimationMode;
  driverControls: DriverControlsMode;
  /** Whether the parts a document's controls table names are touchable
   * (OpenSpec `drive-the-run-by-touch`, design D14). INDEPENDENT of
   * `driverControls`: the two gate different pixels. */
  partControls: PartControlsMode;
  time: number;
  speed: number;
  autoplay: boolean;
  view: ViewerView | null;
  up: THREE.Vector3;
  fov: number;
  className: string | null;
  role: string | null;
  ariaLabel: string | null;
  run: ResolvedRunOptions;
}

export interface ControlPlan {
  bar: boolean;
  toggle: boolean;
  collapsed: boolean;
  styled: boolean;
  hostDriven: boolean;
}

export function resolveOptions(
  options: ViewerOptions = {},
): ResolvedViewerOptions {
  const renderMode = options.renderMode ?? 'continuous';
  if (!['continuous', 'on-demand'].includes(renderMode)) throw new Error('Unknown renderMode');
  if (renderMode === 'on-demand' && (options.animation !== 'external' || options.autoplay !== false
      || options.driverControls !== 'none' || options.partControls !== 'none')) {
    throw new Error('on-demand rendering requires external animation, autoplay false and no interactive controls');
  }
  const time = Number.isFinite(options.time) ? options.time! : 0;
  return {
    renderMode,
    baseUrl: options.baseUrl ?? null,
    animation: options.animation ?? 'inline',
    // Presented by default, like the animation bar: a self-contained
    // export is opened by a maker with no host code behind it.
    driverControls: options.driverControls ?? 'inline',
    // Presented by default, like the panel: a maker who opens a
    // self-contained export of a machine its author declared controls
    // on should be able to touch it.
    partControls: options.partControls ?? 'inline',
    time: Math.min(Math.max(time, 0), 1),
    // Real time by default: a declared loop plays as long as it is. A
    // document without a loop ignores this and plays frames / fps.
    speed: options.speed === undefined ? 1 : assertSpeed(options.speed),
    autoplay: options.autoplay ?? true,
    view: options.view ? {
      camera: resolveVector(options.view.camera),
      target: resolveVector(options.view.target),
    } : null,
    up: resolveVector(options.up, [0, 0, 1]),
    fov: Number.isFinite(options.fov) && options.fov! > 0 ? options.fov! : 50,
    className: options.className ?? null,
    role: options.role ?? null,
    ariaLabel: options.ariaLabel ?? null,
    run: {
      dt: options.run?.dt === undefined
        ? DEFAULT_DT : assertDt(options.run.dt),
      record: options.run?.record === undefined
        ? DEFAULT_RECORD : options.run.record,
      autostart: options.run?.autostart ?? false,
      nudge: {
        amount: options.run?.nudge?.amount === undefined
          ? DEFAULT_NUDGE.amount
          : assertRequestValue('nudge amount', options.run.nudge.amount),
        seconds: options.run?.nudge?.seconds === undefined
          ? DEFAULT_NUDGE.seconds
          : assertRequestValue('nudge duration', options.run.nudge.seconds,
                               true),
      },
      jog: {
        rate: options.run?.jog?.rate === undefined
          ? DEFAULT_JOG.rate
          : assertRequestValue('jog rate', options.run.jog.rate),
      },
    },
  };
}

function resolveVector(
  value: VectorInput | undefined,
  fallback?: readonly [number, number, number],
): THREE.Vector3 {
  const selected = value ?? fallback;
  if (!selected) {
    throw new Error('a viewer vector is required');
  }
  if (Array.isArray(selected)) {
    return new THREE.Vector3(selected[0], selected[1], selected[2]);
  }
  return (selected as THREE.Vector3).clone();
}

export function resolveBaseUrl(sourceUrl: string, baseUrl?: string): string {
  const root = baseUrl ?? sourceUrl.replace(/[?#].*$/, '').replace(/[^/]*$/, '');
  // A document naming no directory is beside its models, not at the server
  // root -- './' keeps the base joinable without rooting it at the host.
  if (!root) return './';
  return root.endsWith('/') ? root : `${root}/`;
}

/** Whether this mount presents the driver chrome (ADR-056 stage 3c,
 * design D9).
 *
 * Two independent conditions, and neither is the animation bar's: the
 * host must want the chrome, and the document must declare a driver for
 * there to be any. A driverless document is therefore untouched by this
 * option, and a host suppressing the chrome still holds the whole
 * driving API -- what is gated is the pixels, not the interface.
 */
export function showsDriverChrome(
  mode: DriverControlsMode,
  declaresDrivers: boolean,
): boolean {
  return mode === 'inline' && declaresDrivers;
}

/** Whether this mount presents the RUNNING chrome (OpenSpec
 * `drive-the-run-on-screen`).
 *
 * The same switch as the posed chrome's, and the same two independent
 * conditions: the host must want the chrome, and the document must
 * carry a program for there to be any. What is gated is the pixels, not
 * the interface -- a host that suppresses them keeps the whole run API.
 */
export function showsRunControls(
  mode: DriverControlsMode,
  carriesProgram: boolean,
): boolean {
  return mode === 'inline' && carriesProgram;
}

/** Whether this mount presents the PART affordance (OpenSpec
 * `drive-the-run-by-touch`, design D14).
 *
 * The same shape as the two switches above, and deliberately its OWN
 * switch: a host that builds its own instrument panel still wants the
 * dial pressable, and the shop floor is exactly that host. What is
 * gated is the cursor, the highlight, the title and the pick -- never
 * the interface: `controls()` answers and the run API is whole either
 * way.
 */
export function showsPartControls(
  mode: PartControlsMode,
  declaresControls: boolean,
): boolean {
  return mode === 'inline' && declaresControls;
}

export function controlPlan(
  mode: AnimationMode,
  animated: boolean,
): ControlPlan {
  if (!animated) {
    return { bar: false, toggle: false, collapsed: false, styled: false,
      hostDriven: mode === 'external' };
  }

  switch (mode) {
    case 'toggle':
      return { bar: true, toggle: true, collapsed: true, styled: false,
        hostDriven: false };
    case 'none':
      return { bar: false, toggle: false, collapsed: false, styled: false,
        hostDriven: false };
    case 'external':
      return { bar: false, toggle: false, collapsed: false, styled: false,
        hostDriven: true };
    case 'inline':
      return { bar: true, toggle: false, collapsed: false, styled: true,
        hostDriven: false };
  }
}
