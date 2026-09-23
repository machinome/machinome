/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

import { afterEach, describe, expect, it, vi } from 'vitest';
import { loadProfiles, profileOverlap, withProfileIntegrationCache } from './profiles';

const TRIANGLE = { points: [[0, 0], [1, 0], [0, 1]], polygons: [[0, 1, 2]] };

function call(table: ReturnType<typeof loadProfiles>, leftTx = 0, rightTx = 0): number {
  return profileOverlap(table, 0, 0, 0, leftTx, 0, 0, rightTx, 0);
}

afterEach(() => vi.restoreAllMocks());

describe('private per-integration profile work', () => {
  it('deep-freezes validated profile data used as cache identity', () => {
    const table = loadProfiles([TRIANGLE]);
    expect(Object.isFrozen(table)).toBe(true);
    expect(Object.isFrozen(table[0])).toBe(true);
    expect(Object.isFrozen(table[0].points)).toBe(true);
    expect(Object.isFrozen(table[0].points[0])).toBe(true);
    expect(Object.isFrozen(table[0].polygons)).toBe(true);
    expect(Object.isFrozen(table[0].polygons[0])).toBe(true);
  });

  it('reuses a successful exact pair inside one integration but not outside it', () => {
    const table = loadProfiles([TRIANGLE]);
    withProfileIntegrationCache(table, (stats) => {
      expect(call(table)).toBe(1);
      expect(call(table)).toBe(1);
      expect(stats.pairHits).toBe(1);
      expect(stats.pairEntries).toBe(1);
      expect(stats.placementEntries).toBe(1);
    });
    expect(call(table)).toBe(1);
    withProfileIntegrationCache(table, (stats) => {
      expect(call(table)).toBe(1);
      expect(stats.pairHits).toBe(0);
    });
  });

  it('distinguishes positive and negative zero in exact pair and placement keys', () => {
    const table = loadProfiles([TRIANGLE]);
    withProfileIntegrationCache(table, (stats) => {
      expect(call(table, +0, 0)).toBe(1);
      expect(call(table, -0, 0)).toBe(1);
      expect(stats.pairHits).toBe(0);
      expect(stats.placementHits).toBe(1);
      expect(stats.pairEntries).toBe(2);
      expect(stats.placementEntries).toBe(2);
    });
  });

  it('does not publish a valid left placement if the right placement fails', () => {
    const table = loadProfiles([TRIANGLE]);
    withProfileIntegrationCache(table, (stats) => {
      expect(() => call(table, 0, 1e16)).toThrow(/transformed edge collapsed/i);
      expect(() => call(table, 0, 1e16)).toThrow(/transformed edge collapsed/i);
      expect(stats.pairEntries).toBe(0);
      expect(stats.placementEntries).toBe(0);
      expect(call(table, 0, 0)).toBe(1);
      expect(stats.pairEntries).toBe(1);
      expect(stats.placementEntries).toBe(1);
    });
  });

  it('does not publish either placement if a later SAT projection fails', () => {
    const table = loadProfiles([{ points: [[0, 0], [1e200, 0], [0, 1e200]],
      polygons: [[0, 1, 2]] }]);
    withProfileIntegrationCache(table, (stats) => {
      expect(() => call(table)).toThrow(/projection.*nonfinite/i);
      expect(() => call(table)).toThrow(/projection.*nonfinite/i);
      expect(stats.pairEntries).toBe(0);
      expect(stats.placementEntries).toBe(0);
    });
  });

  it('starts a fresh cache for the next integration and isolates another table', () => {
    const a = loadProfiles([TRIANGLE]);
    const b = loadProfiles([{ points: [[3, 0], [4, 0], [3, 1]], polygons: [[0, 1, 2]] }]);
    withProfileIntegrationCache(a, (stats) => {
      expect(call(a)).toBe(1);
      expect(call(b)).toBe(1);
      expect(stats.pairEntries).toBe(1);
    });
    withProfileIntegrationCache(a, (stats) => {
      expect(call(a)).toBe(1);
      expect(stats.pairHits).toBe(0);
    });
  });

  it('does not cache a nonfinite or non-primitive placement error', () => {
    const table = loadProfiles([TRIANGLE]);
    withProfileIntegrationCache(table, (stats) => {
      expect(() => call(table, Number.NaN)).toThrow(/nonfinite/i);
      expect(() => call(table, Number.NaN)).toThrow(/nonfinite/i);
      expect(() => call(table, '0' as unknown as number)).toThrow(/nonfinite/i);
      expect(() => call(table, '0' as unknown as number)).toThrow(/nonfinite/i);
      expect(stats.pairEntries).toBe(0);
      expect(stats.placementEntries).toBe(0);
    });
  });

  it('bypasses both caches while numeric builtins are replaced', () => {
    const table = loadProfiles([TRIANGLE]);
    const cosine = vi.spyOn(Math, 'cos');
    withProfileIntegrationCache(table, (stats) => {
      expect(call(table)).toBe(1);
      expect(call(table)).toBe(1);
      expect(stats.pairEntries).toBe(0);
      expect(stats.placementEntries).toBe(0);
    });
    expect(cosine).toHaveBeenCalledTimes(4);
  });

  it('caps retained entries without refusing a valid larger request', () => {
    const table = loadProfiles([TRIANGLE]);
    withProfileIntegrationCache(table, (stats) => {
      for (let i = 0; i < 1025; i += 1) call(table, i * 3, 0);
      expect(stats.pairEntries).toBe(1024);
      expect(stats.placementEntries).toBe(256);
      expect(call(table, 0, 0)).toBe(1);
      expect(stats.pairHits).toBe(0);
    });
  });

  it('discards an integration cache after an error', () => {
    const table = loadProfiles([TRIANGLE]);
    expect(() => withProfileIntegrationCache(table, (stats) => {
      expect(call(table)).toBe(1);
      expect(stats.pairEntries).toBe(1);
      throw new Error('later integration error');
    })).toThrow(/later integration error/i);
    withProfileIntegrationCache(table, (stats) => {
      expect(call(table)).toBe(1);
      expect(stats.pairHits).toBe(0);
    });
  });
});
