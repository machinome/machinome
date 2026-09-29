/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import * as THREE from 'three';
import type { ViewInput, VectorInput } from './viewer';

/** A validated scripted view: camera and target always, and the up
 * direction and field of view only when the host supplied them. */
export interface ScriptedView extends ViewerView {
  up?: THREE.Vector3;
  fov?: number;
}

/** The sine of the angle below which an up direction counts as parallel
 * to the view direction: three.js's `lookAt` has no defined roll there
 * (OpenSpec `move-up-and-field-of-view`, design D3). */
const PARALLEL_SINE = 1e-6;

/** Validate every field before the caller changes any visible state.
 *
 * `up` and `fov` are checked only when given (OpenSpec
 * `move-up-and-field-of-view`, design D2-D3): an omitted one keeps the
 * viewer's current value, and the retained up is NOT checked against
 * the view direction, because API 21 to 27 accept a camera straight
 * above its target with the default Z up and three.js resolves it. */
export function scriptedView(view: ViewInput): ScriptedView {
  function vector(value: VectorInput, name: string): THREE.Vector3 {
    const values = Array.isArray(value) ? value
      : value instanceof THREE.Vector3 ? value.toArray() : [];
    if (values.length !== 3 || !values.every(v => typeof v === 'number' && Number.isFinite(v))) {
      throw new Error(`setView ${name} must contain three finite coordinates`);
    }
    return new THREE.Vector3(values[0], values[1], values[2]);
  }
  const camera = vector(view?.camera, 'camera');
  const target = vector(view?.target, 'target');
  if (camera.equals(target)) throw new Error('setView camera and target must be distinct');
  const scripted: ScriptedView = {camera, target};
  if (view?.up !== undefined) {
    const up = vector(view.up!, 'up');
    if (up.lengthSq() === 0) throw new Error('setView up must not be zero');
    const direction = target.clone().sub(camera);
    const sine = direction.clone().cross(up).length() / (direction.length() * up.length());
    if (!(sine >= PARALLEL_SINE)) {
      throw new Error('setView up must not be parallel to the view direction');
    }
    scripted.up = up;
  }
  if (view?.fov !== undefined) {
    const fov = view.fov;
    if (typeof fov !== 'number' || !Number.isFinite(fov) || fov <= 0 || fov >= 180) {
      throw new Error('setView fov must be a finite number of degrees between 0 and 180, exclusive');
    }
    scripted.fov = fov;
  }
  return scripted;
}

/** Whether an adopted up direction differs from the one the orbit
 * controls were built with, so they must be built again: three.js's
 * `OrbitControls` fixes its orbit axis when constructed (design D4).
 * A scaled copy of the same direction is the same direction. */
export function upDirectionChanged(current: THREE.Vector3,
                                   next: THREE.Vector3): boolean {
  return current.clone().normalize()
    .distanceTo(next.clone().normalize()) > 1e-12;
}

export interface ViewerView {
  camera: THREE.Vector3;
  target: THREE.Vector3;
}

export interface FramedCamera {
  position: THREE.Vector3;
  target: THREE.Vector3;
  up: THREE.Vector3;
  near: number;
  far: number;
}

export function frameBounds(
  box: THREE.Box3,
  fov: number,
  view: ViewerView | null = null,
  up: THREE.Vector3 = new THREE.Vector3(0, 0, 1),
): FramedCamera | null {
  if (box.isEmpty()) {
    return null;
  }
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();
  const distance = (size / 2) /
    Math.tan((fov * Math.PI) / 360) * 1.2;
  const position = view?.camera.clone() ?? center.clone().addScaledVector(
    new THREE.Vector3(1, -1, 0.8).normalize(), distance,
  );
  const radius = size / 2;
  const far = view === null
    ? distance * 100
    : Math.max(distance * 100, position.distanceTo(center) + radius * 2);

  return {
    position,
    target: view?.target.clone() ?? center,
    up: up.clone(),
    near: distance / 100,
    far,
  };
}
