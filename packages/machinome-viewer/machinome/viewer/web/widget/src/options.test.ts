/*
 * solid-node-viewer - the browser viewer for solid-node models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

// The decisions a mount makes before it touches the DOM: what the
// options mean when the host omits them, where meshes are fetched from,
// and which controls a presentation mode is asking for. Kept pure so
// they are testable in node, where there is no document and no WebGL.

import { describe, expect, it } from 'vitest';
import {
  controlPlan, resolveBaseUrl, resolveOptions, showsDriverChrome,
  showsRunControls,
} from './options';

describe('resolveOptions', () => {
  it('reproduces the published export behavior when given nothing', () => {
    const resolved = resolveOptions();

    expect(resolved.animation).toBe('inline');
    expect(resolved.time).toBe(0);
    expect(resolved.autoplay).toBe(true);
    expect(resolved.view).toBeNull();
    expect(resolved.up.toArray()).toEqual([0, 0, 1]);
    expect(resolved.fov).toBe(50);
    expect(resolved.className).toBeNull();
    expect(resolved.role).toBeNull();
    expect(resolved.ariaLabel).toBeNull();
    // A published export shows the driver chrome (ADR-056 stage 3c).
    expect(resolved.driverControls).toBe('inline');
  });

  it('plays at real time unless the host says otherwise', () => {
    // A declared loop plays as long as it is; a document without one
    // ignores the speed altogether (playback.ts decides that).
    expect(resolveOptions().speed).toBe(1);
    expect(resolveOptions({ speed: 720 }).speed).toBe(720);
    expect(resolveOptions({ speed: 0.25 }).speed).toBe(0.25);
  });

  it('refuses a speed that is not a positive finite multiplier', () => {
    for (const bad of [0, -1, NaN, Infinity]) {
      expect(() => resolveOptions({ speed: bad })).toThrow(String(bad));
    }
  });

  it('lets a host building its own panel suppress the chrome', () => {
    expect(resolveOptions({ driverControls: 'none' }).driverControls)
      .toBe('none');
    expect(resolveOptions({ driverControls: 'inline' }).driverControls)
      .toBe('inline');
  });

  it('keeps what the host asked for', () => {
    const resolved = resolveOptions({
      animation: 'toggle',
      time: 0.25,
      autoplay: false,
      className: 'functional-model',
      role: 'img',
      ariaLabel: 'Functional model',
      up: [0, 1, 0],
      fov: 22.5,
      view: { camera: [10, 20, 30], target: [1, 2, 3] },
    });

    expect(resolved.animation).toBe('toggle');
    expect(resolved.time).toBe(0.25);
    expect(resolved.autoplay).toBe(false);
    expect(resolved.className).toBe('functional-model');
    expect(resolved.role).toBe('img');
    expect(resolved.ariaLabel).toBe('Functional model');
    expect(resolved.up.toArray()).toEqual([0, 1, 0]);
    expect(resolved.fov).toBe(22.5);
    expect(resolved.view!.camera.toArray()).toEqual([10, 20, 30]);
    expect(resolved.view!.target.toArray()).toEqual([1, 2, 3]);
  });

  it('clamps time into the animation cycle', () => {
    expect(resolveOptions({ time: 1.5 }).time).toBe(1);
    expect(resolveOptions({ time: -1 }).time).toBe(0);
    expect(resolveOptions({ time: Number.NaN }).time).toBe(0);
  });
});

describe('resolveBaseUrl', () => {
  it('resolves meshes beside a self-contained export by default', () => {
    expect(resolveBaseUrl('https://example.test/models/demo/manifest.json'))
      .toBe('https://example.test/models/demo/');
    expect(resolveBaseUrl('/_build/viewer.json')).toBe('/_build/');
  });

  it('prefers a host-supplied root, for a snapshot served elsewhere', () => {
    expect(resolveBaseUrl('/state/viewer.json', '/artifacts/'))
      .toBe('/artifacts/');
  });

  it('keeps a supplied root joinable to a model path', () => {
    expect(resolveBaseUrl('/state/viewer.json', '/artifacts'))
      .toBe('/artifacts/');
  });

  // The shipped export page mounts this way, so a document URL naming no
  // directory must stay beside the document: an export served under a
  // subpath would otherwise request its models from the server root.
  it('resolves beside a document that names no directory', () => {
    expect(resolveBaseUrl('manifest.json')).toBe('./');
  });

  it('resolves beside such a document carrying a query string', () => {
    expect(resolveBaseUrl('manifest.json?v=2')).toBe('./');
  });
});

describe('controlPlan', () => {
  it('shows the bar inline, as a published export does', () => {
    const plan = controlPlan('inline', true);

    expect(plan.bar).toBe(true);
    expect(plan.toggle).toBe(false);
    expect(plan.collapsed).toBe(false);
    // A published export renders with no stylesheet of its own
    expect(plan.styled).toBe(true);
    expect(plan.hostDriven).toBe(false);
  });

  it('hides the bar behind a toggle the host styles', () => {
    const plan = controlPlan('toggle', true);

    expect(plan.bar).toBe(true);
    expect(plan.toggle).toBe(true);
    expect(plan.collapsed).toBe(true);
    expect(plan.styled).toBe(false);
    expect(plan.hostDriven).toBe(false);
  });

  it('builds nothing when the host wants no controls', () => {
    const plan = controlPlan('none', true);

    expect(plan.bar).toBe(false);
    expect(plan.toggle).toBe(false);
    expect(plan.hostDriven).toBe(false);
  });

  it('yields the clock to the host when animation is external', () => {
    const plan = controlPlan('external', true);

    expect(plan.bar).toBe(false);
    expect(plan.toggle).toBe(false);
    expect(plan.hostDriven).toBe(true);
  });

  it('builds no controls for a model with no $t operation', () => {
    for (const mode of ['inline', 'toggle', 'none', 'external'] as const) {
      const plan = controlPlan(mode, false);
      expect(plan.bar, mode).toBe(false);
      expect(plan.toggle, mode).toBe(false);
    }
  });
});

describe('showsDriverChrome', () => {
  it('shows the chrome for a driver-declaring document by default', () => {
    expect(showsDriverChrome('inline', true)).toBe(true);
  });

  it('shows nothing when the host suppresses it', () => {
    expect(showsDriverChrome('none', true)).toBe(false);
  });

  it('shows nothing for a document that declares no driver', () => {
    // A version 1 document is pixel-identical to before this change,
    // whatever the host asked for.
    expect(showsDriverChrome('inline', false)).toBe(false);
    expect(showsDriverChrome('none', false)).toBe(false);
  });

  it('is independent of the animation bar', () => {
    // A static machine posed only by its drivers has no timeline to
    // scrub and still has controls to drive.
    expect(controlPlan('inline', false).bar).toBe(false);
    expect(showsDriverChrome('inline', true)).toBe(true);
  });
});

// ---------------------------------------------------------------------
// OpenSpec `run-in-the-worker` (design D6, D13): the run's mount option.
// ---------------------------------------------------------------------

describe('resolveOptions: the run', () => {
  it('defaults to 1/240 s, a 600-tick record, and NOT started', () => {
    expect(resolveOptions({}).run).toEqual({
      dt: 1 / 240, record: 600, autostart: false,
      // OpenSpec `drive-the-run-on-screen`, design D3/D4: what a nudge
      // and a jog ASK for, never a coordinate anything writes.
      nudge: { amount: 1, seconds: 0.2 },
      jog: { rate: 1 },
    });
  });

  it('takes a step size the host chooses, once', () => {
    expect(resolveOptions({ run: { dt: 1 / 120 } }).run.dt).toBe(1 / 120);
  });

  it('refuses a non-finite or non-positive step size, naming the value', () => {
    expect(() => resolveOptions({ run: { dt: 0 } })).toThrow(/0/);
    expect(() => resolveOptions({ run: { dt: -1 / 240 } })).toThrow(/-0\.0041|-/);
    expect(() => resolveOptions({ run: { dt: Number.NaN } })).toThrow(/NaN/);
    expect(() => resolveOptions({ run: { dt: Infinity } })).toThrow(/Infinity/);
  });

  it('takes a record length, and none at all', () => {
    expect(resolveOptions({ run: { record: 60 } }).run.record).toBe(60);
    expect(resolveOptions({ run: { record: null } }).run.record).toBeNull();
  });

  it('takes autostart, for a host that wants a machine running on arrival',
     () => {
       expect(resolveOptions({ run: { autostart: true } }).run.autostart)
         .toBe(true);
     });
});

// ---------------------------------------------------------------------
// OpenSpec `drive-the-run-on-screen`: what a nudge and a jog ask for,
// and the one switch that suppresses both chromes.
// ---------------------------------------------------------------------

describe('resolveOptions: the running controls', () => {
  it('takes a nudge amount and duration the host chooses', () => {
    expect(resolveOptions({ run: { nudge: { amount: 5, seconds: 1 } } })
      .run.nudge).toEqual({ amount: 5, seconds: 1 });
  });

  it('takes either half of a nudge on its own', () => {
    expect(resolveOptions({ run: { nudge: { amount: 36 } } }).run.nudge)
      .toEqual({ amount: 36, seconds: 0.2 });
    expect(resolveOptions({ run: { nudge: { seconds: 0.5 } } }).run.nudge)
      .toEqual({ amount: 1, seconds: 0.5 });
  });

  it('takes a jog rate in design units per simulated second', () => {
    expect(resolveOptions({ run: { jog: { rate: 0.25 } } }).run.jog)
      .toEqual({ rate: 0.25 });
  });

  it('refuses a request it could never issue, naming the value', () => {
    expect(() => resolveOptions({ run: { nudge: { amount: Number.NaN } } }))
      .toThrow(/NaN/);
    expect(() => resolveOptions({ run: { nudge: { seconds: -1 } } }))
      .toThrow(/-1/);
    expect(() => resolveOptions({ run: { jog: { rate: Infinity } } }))
      .toThrow(/Infinity/);
  });
});

describe('showsRunControls', () => {
  it('shows the running chrome for a document that carries a program', () => {
    expect(showsRunControls('inline', true)).toBe(true);
  });

  it('shows nothing when the host suppresses the chrome', () => {
    // The SAME switch as the posed chrome's, and it gates the pixels
    // only: a host that suppresses them keeps the whole run API.
    expect(showsRunControls('none', true)).toBe(false);
  });

  it('shows nothing for a document that carries no program', () => {
    expect(showsRunControls('inline', false)).toBe(false);
    expect(showsRunControls('none', false)).toBe(false);
  });
});
