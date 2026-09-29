/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

// Where things stand on screen (OpenSpec `track-a-part-on-screen`,
// design D3 and D5) is arithmetic on a camera and a canvas rectangle, so
// it is tested here without WebGL: three.js maths runs in node.

import * as THREE from 'three';
import { describe, expect, it } from 'vitest';
import {
  boundsOnScreen, POINT_GRID, projectToViewport, searchPoint, worldBounds,
} from './screen';
import type { CanvasBounds, Point } from './screen';

/** A canvas 400 x 300 CSS pixels whose top-left corner is NOT the
 * viewport's, so an answer that forgets the offset is wrong. */
const CANVAS: CanvasBounds = {
  left: 50, top: 20, width: 400, height: 300, right: 450, bottom: 320,
};

/** A camera on +Z looking at the origin, Y up, matrices current. */
function cameraOnZ(distance = 10): THREE.PerspectiveCamera {
  const camera = new THREE.PerspectiveCamera(50, 400 / 300, 0.1, 1000);
  camera.position.set(0, 0, distance);
  camera.up.set(0, 1, 0);
  camera.lookAt(0, 0, 0);
  camera.updateMatrixWorld();
  camera.updateProjectionMatrix();
  return camera;
}

describe('projectToViewport', () => {
  it('projects a world point to viewport pixels of an offset canvas', () => {
    const camera = new THREE.PerspectiveCamera(50, 400 / 300, 0.1, 1000);
    camera.position.set(8, -6, 5);
    camera.up.set(0, 0, 1);
    camera.lookAt(1, 2, 3);
    camera.updateMatrixWorld();
    camera.updateProjectionMatrix();
    const target = projectToViewport([1, 2, 3], camera, CANVAS)!;
    expect(target.x).toBeCloseTo(250);
    expect(target.y).toBeCloseTo(170);
    // Up on the screen is smaller y in the viewport's frame.
    const above = projectToViewport([1, 2, 4], camera, CANVAS)!;
    expect(above.y).toBeLessThan(target.y);
  });

  it('answers null for a point at or behind the camera plane', () => {
    const camera = cameraOnZ(10);
    expect(projectToViewport([0, 0, 20], camera, CANVAS)).toBeNull();
    expect(projectToViewport([3, 1, 10], camera, CANVAS)).toBeNull();
    expect(projectToViewport([0, 0, 9.99], camera, CANVAS)).not.toBeNull();
  });

  it('answers a position outside the canvas for a point off to the side', () => {
    const camera = cameraOnZ(10);
    const far = projectToViewport([100, 0, 0], camera, CANVAS)!;
    expect(far.x).toBeGreaterThan(CANVAS.right);
  });
});

describe('boundsOnScreen', () => {
  it('bounds a box by its in-front corners only', () => {
    const camera = cameraOnZ(10);
    // A box straddling the camera plane z = 10: its four corners at
    // z = 12 are behind the camera and must not be folded back in.
    const box = new THREE.Box3(new THREE.Vector3(-1, -1, 0),
                               new THREE.Vector3(1, 1, 12));
    const rect = boundsOnScreen(box, camera, CANVAS)!;
    expect(rect).not.toBeNull();
    const front = [[-1, -1, 0], [1, 1, 0]].map((corner) =>
      projectToViewport(corner as [number, number, number], camera, CANVAS)!);
    expect(rect.x).toBeCloseTo(front[0].x);
    expect(rect.x + rect.width).toBeCloseTo(front[1].x);
    expect(rect.y).toBeCloseTo(front[1].y);
    expect(rect.y + rect.height).toBeCloseTo(front[0].y);
  });

  it('answers null for a box wholly behind the camera or wholly off the canvas', () => {
    const camera = cameraOnZ(10);
    const behind = new THREE.Box3(new THREE.Vector3(-1, -1, 11),
                                  new THREE.Vector3(1, 1, 12));
    expect(boundsOnScreen(behind, camera, CANVAS)).toBeNull();
    const aside = new THREE.Box3(new THREE.Vector3(100, -1, -1),
                                 new THREE.Vector3(102, 1, 1));
    expect(boundsOnScreen(aside, camera, CANVAS)).toBeNull();
    expect(boundsOnScreen(new THREE.Box3(), camera, CANVAS)).toBeNull();
  });

  it('does not clip a box that is partly off the canvas', () => {
    const camera = cameraOnZ(10);
    const box = new THREE.Box3(new THREE.Vector3(0, -1, -1),
                               new THREE.Vector3(100, 1, 1));
    const rect = boundsOnScreen(box, camera, CANVAS)!;
    expect(rect).not.toBeNull();
    expect(rect.x).toBeGreaterThan(CANVAS.left);
    expect(rect.x + rect.width).toBeGreaterThan(CANVAS.right);
  });
});

describe('worldBounds', () => {
  it("unions each mesh's box in world coordinates", () => {
    const geometry = new THREE.BoxGeometry(2, 2, 2);
    const a = new THREE.Mesh(geometry);
    const b = new THREE.Mesh(geometry);
    const group = new THREE.Group();
    group.position.set(0, 0, 10);
    b.position.set(5, 0, 0);
    group.add(a, b);
    group.updateMatrixWorld(true);
    const box = worldBounds([a, b]);
    expect(box.min.toArray()).toEqual([-1, -1, 9]);
    expect(box.max.toArray()).toEqual([6, 1, 11]);
    expect(worldBounds([]).isEmpty()).toBe(true);
  });
});

describe('searchPoint', () => {
  const rect = { x: 100, y: 50, width: 70, height: 140 };

  it('tries the centre first, then the grid in row order, then answers null', () => {
    const probes: Point[] = [];
    expect(searchPoint(rect, CANVAS, (point) => {
      probes.push(point);
      return false;
    })).toBeNull();
    expect(POINT_GRID).toBe(7);
    expect(probes.length).toBe(1 + POINT_GRID * POINT_GRID);
    expect(probes[0]).toEqual({ x: 135, y: 120 });
    expect(probes[1]).toEqual({ x: 105, y: 60 });
    expect(probes[2]).toEqual({ x: 115, y: 60 });
    expect(probes[1 + POINT_GRID]).toEqual({ x: 105, y: 80 });

    const centre = searchPoint(rect, CANVAS, () => true);
    expect(centre).toEqual({ x: 135, y: 120 });
    let count = 0;
    const third = searchPoint(rect, CANVAS, () => (count += 1) === 3);
    expect(third).toEqual({ x: 115, y: 60 });
  });

  it('never probes a point outside the canvas', () => {
    const probes: Point[] = [];
    const wide = { x: 0, y: 0, width: 700, height: 700 };
    searchPoint(wide, CANVAS, (point) => { probes.push(point); return false; });
    expect(probes.length).toBeGreaterThan(0);
    expect(probes.length).toBeLessThan(1 + POINT_GRID * POINT_GRID);
    for (const point of probes) {
      expect(point.x).toBeGreaterThanOrEqual(CANVAS.left);
      expect(point.x).toBeLessThanOrEqual(CANVAS.right);
      expect(point.y).toBeGreaterThanOrEqual(CANVAS.top);
      expect(point.y).toBeLessThanOrEqual(CANVAS.bottom);
    }
  });
});
