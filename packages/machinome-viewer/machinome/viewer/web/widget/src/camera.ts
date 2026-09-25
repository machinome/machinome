/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import * as THREE from 'three';
import type { ViewInput, VectorInput } from './viewer';

/** Validate both endpoints before the caller changes any visible state. */
export function scriptedView(view: ViewInput): ViewerView {
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
  return {camera, target};
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
