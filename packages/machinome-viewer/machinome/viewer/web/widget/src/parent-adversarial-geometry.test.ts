/* SPDX-License-Identifier: AGPL-3.0-or-later */
import * as THREE from 'three';
import { expect, it, vi } from 'vitest';
const { loadAsync } = vi.hoisted(() => ({ loadAsync: vi.fn() }));
vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({
  STLLoader: class { loadAsync = loadAsync; },
}));
import { WidgetTree } from './tree';

it('disposes geometry when cancellation falls between loader and admission continuations', async () => {
  let resolve!: (geometry: THREE.BufferGeometry) => void;
  loadAsync.mockImplementationOnce(() => new Promise<THREE.BufferGeometry>(yes => { resolve = yes; }));
  const tree = new WidgetTree({ name: 'parent-race', type: 'leaf', color: null,
    operations: [], model: 'parent-race.stl' }, '/');
  const outcome = Promise.allSettled([tree.loaded]);
  const geometry = new THREE.BoxGeometry();
  const dispose = vi.spyOn(geometry, 'dispose');
  resolve(geometry);
  // The loader continuation has accepted the result, but admission has not.
  await Promise.resolve();
  tree.dispose();
  expect((await outcome)[0].status).toBe('rejected');
  expect(tree.group.children).toHaveLength(0);
  expect(dispose).toHaveBeenCalledTimes(1);
});

it.each([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])(
  'does not attach an artifact replacement after disposal at microtask %i', async steps => {
    loadAsync.mockResolvedValueOnce(new THREE.BoxGeometry());
    const tree = new WidgetTree({ name: 'artifact-race', type: 'leaf', color: null,
      operations: [], model: 'artifact-race.stl' }, '/');
    await tree.loaded;
    let resolve!: (geometry: THREE.BufferGeometry) => void;
    loadAsync.mockImplementationOnce(() => new Promise<THREE.BufferGeometry>(yes => { resolve = yes; }));
    const replacement = tree.artifactChanged('artifact-race.stl', '/');
    const outcome = Promise.allSettled([replacement]);
    const geometry = new THREE.BoxGeometry();
    const dispose = vi.spyOn(geometry, 'dispose');
    resolve(geometry);
    for (let step = 0; step < steps; step++) await Promise.resolve();
    tree.dispose();
    const lateAdd = vi.spyOn(tree.group, 'add');
    await outcome;
    expect(lateAdd).not.toHaveBeenCalled();
    expect(dispose).toHaveBeenCalledTimes(1);
  },
);
