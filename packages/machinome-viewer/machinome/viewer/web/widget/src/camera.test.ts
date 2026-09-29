/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// Framing is arithmetic on bounds, so it is tested without a renderer:
// three.js maths runs in node, only WebGL and OrbitControls need a
// browser.

import * as THREE from 'three';
import { describe, expect, it } from 'vitest';
import { frameBounds, scriptedView, upDirectionChanged } from './camera';

const FOV = 50;

describe('scriptedView', () => {
  it('copies camera input and target without aliasing caller state', () => {
    const position = new THREE.Vector3(10, 20, 30);
    const target: [number, number, number] = [0, 1, 2];
    const view = scriptedView({camera: position, target});
    position.x = 999; target[1] = 999;
    expect(view.camera.toArray()).toEqual([10, 20, 30]);
    expect(view.target.toArray()).toEqual([0, 1, 2]);
  });
  it.each([[NaN, 2, 3], [Infinity, 2, 3], [1, 2], [1, 2, 3, 4]])(
    'refuses malformed camera coordinates %j', (...values) => {
      expect(() => scriptedView({camera: values as [number, number, number],
        target: [0, 0, 0]})).toThrow(/camera/);
    },
  );
  it('refuses an invalid target and coincident endpoints', () => {
    expect(() => scriptedView({camera: [1, 2, 3], target: [0, NaN, 0]}))
      .toThrow(/target/);
    expect(() => scriptedView({camera: [1, 2, 3], target: [1, 2, 3]}))
      .toThrow(/distinct/);
  });
});

// A scripted view's up direction and field of view (OpenSpec
// `move-up-and-field-of-view`, design D1-D4).
describe('scriptedView up and fov', () => {
  it('copies up and fov without aliasing caller state', () => {
    const up: [number, number, number] = [0, 2, 0];
    const view = scriptedView({camera: [0, 0, 10], target: [0, 0, 0], up, fov: 20});
    up[1] = 999;
    expect(view.up!.toArray()).toEqual([0, 2, 0]);
    expect(view.fov).toBe(20);
    const vector = new THREE.Vector3(1, 0, 0);
    const again = scriptedView({camera: [0, 0, 10], target: [0, 0, 0], up: vector});
    vector.x = 5;
    expect(again.up!.toArray()).toEqual([1, 0, 0]);
  });

  it('leaves up and fov undefined when omitted', () => {
    const view = scriptedView({camera: [0, 0, 10], target: [0, 0, 0]});
    expect(view.up).toBeUndefined();
    expect(view.fov).toBeUndefined();
  });

  it.each([[[NaN, 1, 0]], [[Infinity, 1, 0]], [[1, 0]], [[1, 0, 0, 0]], ['up']])(
    'refuses a non-finite or non-three-dimensional up %j', (up) => {
      expect(() => scriptedView({camera: [0, 0, 10], target: [0, 0, 0],
        up: up as never})).toThrow('setView up must contain three finite coordinates');
    },
  );

  it('refuses a zero up', () => {
    expect(() => scriptedView({camera: [0, 0, 10], target: [0, 0, 0], up: [0, 0, 0]}))
      .toThrow('setView up must not be zero');
  });

  it('refuses an up parallel or anti-parallel to the view direction', () => {
    for (const up of [[0, 0, 1], [0, 0, -3], [0, 0, 1e-9]] as [number, number, number][]) {
      expect(() => scriptedView({camera: [0, 0, 10], target: [0, 0, 0], up}))
        .toThrow('setView up must not be parallel to the view direction');
    }
    // 1e-3 rad off the view direction is a defined roll.
    const view = scriptedView({camera: [0, 0, 10], target: [0, 0, 0],
      up: [Math.sin(1e-3), 0, Math.cos(1e-3)]});
    expect(view.up!.z).toBeCloseTo(Math.cos(1e-3));
  });

  it.each([0, 180, -10, 200, NaN, Infinity, '30'])(
    'refuses a fov of %j', (fov) => {
      expect(() => scriptedView({camera: [0, 0, 10], target: [0, 0, 0],
        fov: fov as number})).toThrow(
        'setView fov must be a finite number of degrees between 0 and 180, exclusive');
    },
  );

  it('does not check the omitted up against the view direction', () => {
    // A camera straight above its target with the default Z up: accepted
    // at API 21 to 27, and still accepted.
    expect(() => scriptedView({camera: [0, 0, 10], target: [0, 0, 0]})).not.toThrow();
  });
});

describe('upDirectionChanged', () => {
  it('an orbit is rebuilt only when the up direction changes', () => {
    const z = new THREE.Vector3(0, 0, 1);
    expect(upDirectionChanged(z, new THREE.Vector3(0, 0, 7))).toBe(false);
    expect(upDirectionChanged(z, new THREE.Vector3(0, 0, -1))).toBe(true);
    expect(upDirectionChanged(z, new THREE.Vector3(0, 1, 0))).toBe(true);
    expect(upDirectionChanged(new THREE.Vector3(1, 1, 0), new THREE.Vector3(3, 3, 0))).toBe(false);
    // Neither argument is changed by asking.
    expect(z.toArray()).toEqual([0, 0, 1]);
  });
});

function unitBoxAt(center: THREE.Vector3): THREE.Box3 {
  return new THREE.Box3().setFromCenterAndSize(
    center,
    new THREE.Vector3(1, 1, 1),
  );
}

describe('frameBounds', () => {
  it('looks at the middle of the model from the established direction', () => {
    const center = new THREE.Vector3(2, -3, 4);
    const framed = frameBounds(unitBoxAt(center), FOV);

    expect(framed).not.toBeNull();
    expect(framed!.target.distanceTo(center)).toBeCloseTo(0);

    // The viewer's established vantage point, unchanged by this cycle
    const direction = framed!.position.clone().sub(center).normalize();
    expect(direction.x).toBeCloseTo(new THREE.Vector3(1, -1, 0.8)
      .normalize().x);
    expect(direction.y).toBeCloseTo(new THREE.Vector3(1, -1, 0.8)
      .normalize().y);
    expect(direction.z).toBeCloseTo(new THREE.Vector3(1, -1, 0.8)
      .normalize().z);
  });

  it('keeps the whole model between the clipping planes', () => {
    const framed = frameBounds(unitBoxAt(new THREE.Vector3()), FOV)!;
    const distance = framed.position.length();

    expect(framed.near).toBeGreaterThan(0);
    expect(framed.near).toBeLessThan(distance);
    expect(framed.far).toBeGreaterThan(distance);
  });

  it('frames a larger model from further away', () => {
    const small = frameBounds(unitBoxAt(new THREE.Vector3()), FOV)!;
    const large = frameBounds(
      new THREE.Box3().setFromCenterAndSize(
        new THREE.Vector3(),
        new THREE.Vector3(100, 100, 100),
      ),
      FOV,
    )!;

    expect(large.position.length()).toBeGreaterThan(small.position.length());
  });

  it('adopts a restored view while still clipping to the model', () => {
    const center = new THREE.Vector3(1, 1, 1);
    const view = {
      camera: new THREE.Vector3(10, 10, 10),
      target: new THREE.Vector3(1, 1, 1),
    };
    const framed = frameBounds(unitBoxAt(center), FOV, view)!;
    const fitted = frameBounds(unitBoxAt(center), FOV)!;

    expect(framed.position.distanceTo(view.camera)).toBeCloseTo(0);
    expect(framed.target.distanceTo(view.target)).toBeCloseTo(0);
    // Clipping still comes from the model, not from where the maker stood
    expect(framed.near).toBeCloseTo(fitted.near);
    expect(framed.far).toBeCloseTo(fitted.far);
  });

  it('carries a host-supplied up direction without changing clipping', () => {
    const box = unitBoxAt(new THREE.Vector3());
    const view = {
      camera: new THREE.Vector3(10, 10, 10),
      target: new THREE.Vector3(),
    };
    const baseline = frameBounds(box, FOV, view)!;
    const up = new THREE.Vector3(0, 1, 0);
    const framed = frameBounds(box, FOV, view, up)!;

    expect(framed.up.distanceTo(up)).toBeCloseTo(0);
    expect(framed.near).toBeCloseTo(baseline.near);
    expect(framed.far).toBeCloseTo(baseline.far);
  });

  it('keeps a model inside the far plane from a distant restored view', () => {
    const center = new THREE.Vector3();
    const box = unitBoxAt(center);
    const view = {
      camera: new THREE.Vector3(1000, 0, 0),
      target: center.clone(),
    };
    const framed = frameBounds(box, FOV, view)!;
    const radius = box.getSize(new THREE.Vector3()).length() / 2;

    expect(framed.position.distanceTo(view.camera)).toBeCloseTo(0);
    expect(framed.far).toBeGreaterThan(
      view.camera.distanceTo(center) + radius,
    );
  });

  it('declines to frame a model that loaded nothing', () => {
    expect(frameBounds(new THREE.Box3(), FOV)).toBeNull();
  });
});
