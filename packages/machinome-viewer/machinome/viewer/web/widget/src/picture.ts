/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
 */

// What a continuous viewer's frame loop compares to know whether its
// picture can have changed since its last draw (OpenSpec
// `draw-only-when-the-picture-changes`, design Decision 2).
//
// Two of the things a draw reads are counted by their owners: the mount's
// PICTURE REVISION, one counter per mount, carried by the mount's
// material holder and raised by the holder whenever it points a mesh at
// another material and by the tree's four writers (`update` when its
// change set reaches a node, `applyVisibility`, `artifactChanged` and
// `reconcile` when they apply). The camera is not counted but compared
// by VALUE: its world matrix and its projection matrix, 32 numbers,
// under `Object.is`, so every writer of the camera is seen without being
// listened to, and a `NaN` aspect from a zero-sized container equals
// itself.

import type * as THREE from 'three';

/** One mount's picture revision: a counter its owners raise whenever they
 * write something a draw reads. Only whether it moved means anything. */
export class PictureRevision {
  private count = 0;

  /** The revision now. */
  value(): number {
    return this.count;
  }

  /** Something a draw reads was written. */
  raise(): void {
    this.count += 1;
  }
}

/** The camera as a draw reads it: its world matrix, brought up to date
 * as a draw brings it, then its projection matrix -- 32 numbers. */
export function cameraReading(camera: THREE.Camera): number[] {
  camera.updateMatrixWorld();
  return [...camera.matrixWorld.elements, ...camera.projectionMatrix.elements];
}

/** Whether two readings are the same, number for number under
 * `Object.is`: `NaN` equals `NaN`, and `-0` differs from `0`. */
export function sameReading(a: readonly number[], b: readonly number[]): boolean {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i += 1) {
    if (!Object.is(a[i], b[i])) return false;
  }
  return true;
}
