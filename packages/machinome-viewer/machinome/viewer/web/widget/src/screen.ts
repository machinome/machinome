/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// Where things stand on screen (OpenSpec `track-a-part-on-screen`,
// design D3 and D5): the arithmetic `controls()` has always done for a
// declared control's part, moved out of `viewer.ts` unchanged so a
// host's `partOnScreen` and `project` answer by the SAME rule, and so it
// is tested without WebGL.
//
// Every position is in VIEWPORT CSS pixels -- the frame of a `DOMRect`
// and of a pointer event's `clientX`/`clientY` -- found by offsetting
// normalised device coordinates by the canvas's own client rectangle.

import * as THREE from 'three';

export interface Point {
  x: number;
  y: number;
}

/** A rectangle in viewport CSS pixels. */
export interface ScreenRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

/** The canvas's client rectangle: what `getBoundingClientRect()` gives. */
export interface CanvasBounds {
  left: number;
  top: number;
  width: number;
  height: number;
  right: number;
  bottom: number;
}

/** How finely a rectangle is searched for a point on its part (design
 * D15 of `drive-the-run-by-touch`). Bounded on purpose: the answer is
 * `null` rather than an unbounded hunt. */
export const POINT_GRID = 7;

const scratch = new THREE.Vector3();

/** Where a world point lands, in viewport CSS pixels, or `null` when it
 * is at or behind the camera plane, where a projection is meaningless.
 * A point in front of the camera that falls outside the canvas is
 * answered with a position outside it. The camera's `matrixWorldInverse`
 * and projection matrix must be current. */
export function projectToViewport(
  world: THREE.Vector3 | readonly [number, number, number],
  camera: THREE.Camera,
  canvas: CanvasBounds,
): Point | null {
  if (world instanceof THREE.Vector3) {
    scratch.copy(world);
  } else {
    scratch.set(world[0], world[1], world[2]);
  }
  const point = scratch.clone();
  if (scratch.applyMatrix4(camera.matrixWorldInverse).z >= 0) {
    return null;
  }
  const projected = point.project(camera);
  return {
    x: canvas.left + ((projected.x + 1) / 2) * canvas.width,
    y: canvas.top + ((1 - projected.y) / 2) * canvas.height,
  };
}

/** The union of each mesh's geometry box, in world coordinates. The
 * meshes' `matrixWorld` must be current. */
export function worldBounds(meshes: readonly THREE.Mesh[]): THREE.Box3 {
  const bounds = new THREE.Box3();
  for (const mesh of meshes) {
    if (mesh.geometry.boundingBox === null) {
      mesh.geometry.computeBoundingBox();
    }
    const box = mesh.geometry.boundingBox;
    if (box !== null) {
      bounds.union(box.clone().applyMatrix4(mesh.matrixWorld));
    }
  }
  return bounds;
}

/** The rectangle enclosing a world box's in-front corners, or `null`
 * when the box is empty, no corner is in front of the camera, or the
 * rectangle lies wholly outside the canvas. It is NOT clipped to the
 * canvas: a box partly off screen reports a rectangle past its edge. */
export function boundsOnScreen(
  box: THREE.Box3,
  camera: THREE.Camera,
  canvas: CanvasBounds,
): ScreenRect | null {
  if (box.isEmpty()) {
    return null;
  }
  let left = Infinity;
  let right = -Infinity;
  let top = Infinity;
  let bottom = -Infinity;
  let anyInFront = false;
  for (let index = 0; index < 8; index += 1) {
    // Behind the camera a projection is meaningless, so such a corner
    // is left out rather than folded back into the rectangle.
    const corner = projectToViewport([
      index & 1 ? box.max.x : box.min.x,
      index & 2 ? box.max.y : box.min.y,
      index & 4 ? box.max.z : box.min.z,
    ], camera, canvas);
    if (corner === null) {
      continue;
    }
    anyInFront = true;
    left = Math.min(left, corner.x);
    right = Math.max(right, corner.x);
    top = Math.min(top, corner.y);
    bottom = Math.max(bottom, corner.y);
  }
  if (!anyInFront || right < canvas.left || left > canvas.right
      || bottom < canvas.top || top > canvas.bottom) {
    return null;
  }
  return { x: left, y: top, width: right - left, height: bottom - top };
}

/** A point inside the canvas and inside `rect` at which `reaches` holds:
 * the rectangle's centre first -- which on a real dial may be the
 * axle's hole -- then a `POINT_GRID` x `POINT_GRID` grid in row order.
 * `null` says honestly that no probe of the bounded search found one.
 * `reaches` is never asked about a point outside the canvas. */
export function searchPoint(
  rect: ScreenRect,
  canvas: CanvasBounds,
  reaches: (point: Point) => boolean,
): Point | null {
  const probe = (point: Point): boolean =>
    point.x >= canvas.left && point.x <= canvas.right
    && point.y >= canvas.top && point.y <= canvas.bottom
    && reaches(point);
  const centre = { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
  if (probe(centre)) {
    return centre;
  }
  for (let row = 0; row < POINT_GRID; row += 1) {
    for (let column = 0; column < POINT_GRID; column += 1) {
      const point = {
        x: rect.x + (rect.width * (column + 0.5)) / POINT_GRID,
        y: rect.y + (rect.height * (row + 0.5)) / POINT_GRID,
      };
      if (probe(point)) {
        return point;
      }
    }
  }
  return null;
}
