/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */

/** Document-owned finite convex polygons. No CAD or decomposition occurs here. */
export interface ConvexProfile {
  readonly points: readonly (readonly [number, number])[];
  readonly polygons: readonly (readonly number[])[];
}

function fail(detail: string): never {
  throw new Error(`invalid finite convex profile: ${detail}`);
}

function object(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/** Convert a finite IEEE-754 value to its exact integer times 2^exponent. */
function binary(value: number): [bigint, number] {
  const buffer = new ArrayBuffer(8);
  const view = new DataView(buffer);
  view.setFloat64(0, value, false);
  const bits = view.getBigUint64(0, false);
  const sign = (bits >> 63n) === 0n ? 1n : -1n;
  const exponent = Number((bits >> 52n) & 0x7ffn);
  const fraction = bits & ((1n << 52n) - 1n);
  if (exponent === 0) return [sign * fraction, -1074];
  return [sign * ((1n << 52n) | fraction), exponent - 1075];
}

type ExactPoint = readonly [bigint, bigint];

function orientation(a: ExactPoint, b: ExactPoint, c: ExactPoint): bigint {
  return (b[0] - a[0]) * (c[1] - a[1])
    - (b[1] - a[1]) * (c[0] - a[0]);
}

function between(a: bigint, b: bigint, c: bigint): boolean {
  return (a <= b && b <= c) || (c <= b && b <= a);
}

function onSegment(a: ExactPoint, b: ExactPoint, p: ExactPoint): boolean {
  return orientation(a, b, p) === 0n
    && between(a[0], p[0], b[0]) && between(a[1], p[1], b[1]);
}

function intersects(a: ExactPoint, b: ExactPoint,
                    c: ExactPoint, d: ExactPoint): boolean {
  const abC = orientation(a, b, c);
  const abD = orientation(a, b, d);
  const cdA = orientation(c, d, a);
  const cdB = orientation(c, d, b);
  if (abC === 0n && onSegment(a, b, c)) return true;
  if (abD === 0n && onSegment(a, b, d)) return true;
  if (cdA === 0n && onSegment(c, d, a)) return true;
  if (cdB === 0n && onSegment(c, d, b)) return true;
  return ((abC < 0n && abD > 0n) || (abC > 0n && abD < 0n))
    && ((cdA < 0n && cdB > 0n) || (cdA > 0n && cdB < 0n));
}

function validateLoop(loop: readonly number[], exact: readonly ExactPoint[],
                      profileIndex: number, polygonIndex: number): void {
  const where = `${profileIndex} polygon ${polygonIndex}`;
  if (loop.length < 3) fail(`${where} has fewer than three vertices`);
  const vertices = loop.map((index) => exact[index]);
  for (let i = 0; i < vertices.length; i += 1) {
    const a = vertices[i];
    const b = vertices[(i + 1) % vertices.length];
    if (a[0] === b[0] && a[1] === b[1]) fail(`${where} has a zero edge`);
    for (let j = 0; j < i; j += 1) {
      if (a[0] === vertices[j][0] && a[1] === vertices[j][1]) {
        fail(`${where} repeats a vertex`);
      }
    }
  }
  let twiceArea = 0n;
  for (let i = 0; i < vertices.length; i += 1) {
    const prev = vertices[(i + vertices.length - 1) % vertices.length];
    const here = vertices[i];
    const next = vertices[(i + 1) % vertices.length];
    twiceArea += here[0] * next[1] - here[1] * next[0];
    const turn = orientation(prev, here, next);
    if (turn < 0n) fail(`${where} is not CCW convex`);
    if (turn === 0n) {
      const firstX = here[0] - prev[0];
      const firstY = here[1] - prev[1];
      const nextX = next[0] - here[0];
      const nextY = next[1] - here[1];
      if (firstX * nextX + firstY * nextY <= 0n) {
        fail(`${where} has an adjacent backtracking edge`);
      }
    }
  }
  if (twiceArea <= 0n) fail(`${where} has nonpositive area`);
  for (let i = 0; i < vertices.length; i += 1) {
    const a = vertices[i];
    const b = vertices[(i + 1) % vertices.length];
    for (let j = i + 1; j < vertices.length; j += 1) {
      if (j === i + 1 || (i === 0 && j === vertices.length - 1)) continue;
      if (intersects(a, b, vertices[j], vertices[(j + 1) % vertices.length])) {
        fail(`${where} has crossing or touching nonadjacent edges`);
      }
    }
  }
}

/** Exact-binary geometric validation, preserving every serialized number/order. */
export function loadProfiles(raw: unknown): readonly ConvexProfile[] {
  if (!Array.isArray(raw) || raw.length === 0) fail('table must be a nonempty array');
  return Object.freeze(raw.map((entry, profileIndex): ConvexProfile => {
    if (!object(entry) || !Array.isArray(entry.points)
        || !Array.isArray(entry.polygons) || entry.polygons.length === 0) {
      fail(`${profileIndex} requires points and nonempty polygons`);
    }
    const points = entry.points.map((point: unknown, index: number): readonly [number, number] => {
      if (!Array.isArray(point) || point.length !== 2
          || !point.every((value) => typeof value === 'number' && Number.isFinite(value))) {
        fail(`${profileIndex} point ${index} must have two finite coordinates`);
      }
      return Object.freeze([point[0], point[1]]) as readonly [number, number];
    });
    if (points.length < 3) fail(`${profileIndex} has fewer than three points`);
    // Every finite binary double is an exact integer on one common power-of-two grid.
    const pairs = points.map(([x, y]) => [binary(x), binary(y)] as const);
    let exponent = Infinity;
    for (const [x, y] of pairs) {
      if (x[1] < exponent) exponent = x[1];
      if (y[1] < exponent) exponent = y[1];
    }
    const exact = pairs.map(([x, y]): ExactPoint => [
      x[0] << BigInt(x[1] - exponent), y[0] << BigInt(y[1] - exponent),
    ]);
    const polygons = entry.polygons.map((loop: unknown, polygonIndex: number): readonly number[] => {
      if (!Array.isArray(loop) || loop.some((index) => !Number.isInteger(index)
          || index < 0 || index >= points.length)) {
        fail(`${profileIndex} polygon ${polygonIndex} has an invalid point index`);
      }
      validateLoop(loop, exact, profileIndex, polygonIndex);
      return Object.freeze([...loop]);
    });
    return Object.freeze({ points: Object.freeze(points), polygons: Object.freeze(polygons) });
  }));
}

type Point = readonly [number, number];
type Axis = readonly [number, number];
interface PlacedPolygon {
  points: readonly Point[];
  axes: readonly Axis[];
  minX: number; maxX: number; minY: number; maxY: number;
}

/** Pure, bounded work shared only by one synchronous Run integration attempt. */
interface ProfileIntegrationCache {
  readonly table: readonly ConvexProfile[];
  readonly pairs: Map<string, number>;
  readonly placed: Map<string, readonly PlacedPolygon[]>;
  readonly stats: ProfileCacheStats;
}

/** Internal counted-work evidence; the widget/host API does not expose it. */
export interface ProfileCacheStats {
  pairHits: number;
  placementHits: number;
  pairEntries: number;
  placementEntries: number;
}

const PAIR_CAP = 1024;
const PLACEMENT_CAP = 256;
const ORIGINAL_COS = Math.cos;
const ORIGINAL_SIN = Math.sin;
const ORIGINAL_FINITE = Number.isFinite;
const ORIGINAL_INTEGER = Number.isInteger;
let activeCache: ProfileIntegrationCache | null = null;

export function withProfileIntegrationCache<T>(
  table: readonly ConvexProfile[], action: (stats: ProfileCacheStats) => T,
): T {
  const previous = activeCache;
  const stats: ProfileCacheStats = {
    pairHits: 0, placementHits: 0, pairEntries: 0, placementEntries: 0,
  };
  activeCache = { table, pairs: new Map(), placed: new Map(), stats };
  try { return action(stats); }
  finally { activeCache = previous; }
}

function numberBits(value: number): string {
  const view = new DataView(new ArrayBuffer(8));
  view.setFloat64(0, value, false);
  return view.getBigUint64(0, false).toString(16).padStart(16, '0');
}

function placementKey(index: number, angle: number, tx: number, ty: number): string | null {
  if (typeof angle !== 'number' || !Number.isFinite(angle)
      || typeof tx !== 'number' || !Number.isFinite(tx)
      || typeof ty !== 'number' || !Number.isFinite(ty)) return null;
  return `${index}:${numberBits(angle)}:${numberBits(tx)}:${numberBits(ty)}`;
}

function remembered<V>(entries: Map<string, V>, key: string): V | undefined {
  return entries.get(key);
}

function retain<V>(entries: Map<string, V>, key: string, value: V, cap: number): void {
  entries.delete(key);
  entries.set(key, value);
  if (entries.size > cap) entries.delete(entries.keys().next().value!);
}

function touch<V>(entries: Map<string, V>, key: string): void {
  const value = entries.get(key);
  if (value !== undefined) retain(entries, key, value, entries.size);
}

function finite(value: number, detail: string): number {
  if (!Number.isFinite(value)) throw new Error(`profileOverlap ${detail} is nonfinite`);
  return value;
}

function place(profile: ConvexProfile, angle: number, tx: number, ty: number): readonly PlacedPolygon[] {
  // Match producer's first-error order: XY first, then angle.
  finite(tx, 'x translation'); finite(ty, 'y translation'); finite(angle, 'angle');
  const theta = finite(angle * 0.017453292519943295, 'radian angle');
  const c = finite(Math.cos(theta), 'cosine');
  const s = finite(Math.sin(theta), 'sine');
  return profile.polygons.map((loop): PlacedPolygon => {
    // Transform only polygon vertices, in polygon order. The producer never
    // evaluates unused table points or a later polygon before this one's axes.
    const vertices = loop.map((index): Point => {
      const [x, y] = profile.points[index];
      const cx = finite(c * x, 'x rotation product');
      const sy = finite(s * y, 'x rotation product');
      const sx = finite(s * x, 'y rotation product');
      const cy = finite(c * y, 'y rotation product');
      return [finite(finite(cx - sy, 'x rotation sum') + tx, 'transformed x'),
        finite(finite(sx + cy, 'y rotation sum') + ty, 'transformed y')];
    });
    const axes = vertices.map((u, index): Axis => {
      const v = vertices[(index + 1) % vertices.length];
      const nx = finite(u[1] - v[1], 'world axis x');
      const ny = finite(v[0] - u[0], 'world axis y');
      if (nx === 0 && ny === 0) {
        throw new Error('profileOverlap transformed edge collapsed');
      }
      return [nx, ny];
    });
    let minX = vertices[0][0]; let maxX = minX;
    let minY = vertices[0][1]; let maxY = minY;
    for (const [x, y] of vertices.slice(1)) {
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    }
    return { points: vertices, axes, minX, maxX, minY, maxY };
  });
}

function projection(polygon: PlacedPolygon, [nx, ny]: Axis): readonly [number, number] {
  const projected = (point: Point): number => {
    const px = finite(point[0] * nx, 'projection x product');
    const py = finite(point[1] * ny, 'projection y product');
    return finite(px + py, 'projection sum');
  };
  let low = projected(polygon.points[0]); let high = low;
  for (const point of polygon.points.slice(1)) {
    const value = projected(point);
    if (value < low) low = value;
    if (value > high) high = value;
  }
  return [low, high];
}

/** Pointwise inclusive contact: all placement/axis validation precedes AABB exit. */
export function profileOverlap(
  table: readonly ConvexProfile[], leftIndex: number, rightIndex: number,
  leftAngle: number, leftTx: number, leftTy: number,
  rightAngle: number, rightTx: number, rightTy: number,
): number {
  if (!Number.isInteger(leftIndex) || leftIndex < 0 || leftIndex >= table.length
      || !Number.isInteger(rightIndex) || rightIndex < 0 || rightIndex >= table.length) {
    throw new Error('profileOverlap invalid profile table index');
  }
  const cache = activeCache?.table === table
    && Math.cos === ORIGINAL_COS && Math.sin === ORIGINAL_SIN
    && Number.isFinite === ORIGINAL_FINITE && Number.isInteger === ORIGINAL_INTEGER
    ? activeCache : null;
  const leftKey = cache === null ? null
    : placementKey(leftIndex, leftAngle, leftTx, leftTy);
  const rightKey = cache === null ? null
    : placementKey(rightIndex, rightAngle, rightTx, rightTy);
  // Either ineligible placement bypasses BOTH maps, including a pure side.
  if (cache === null || leftKey === null || rightKey === null) {
    return overlapPlaced(place(table[leftIndex], leftAngle, leftTx, leftTy),
      place(table[rightIndex], rightAngle, rightTx, rightTy));
  }
  const pairKey = `${leftKey}|${rightKey}`;
  const prior = remembered(cache.pairs, pairKey);
  if (prior !== undefined) {
    cache.stats.pairHits += 1;
    touch(cache.pairs, pairKey);
    return prior;
  }
  const knownLeft = remembered(cache.placed, leftKey);
  const left = knownLeft ?? place(table[leftIndex], leftAngle, leftTx, leftTy);
  const knownRight = remembered(cache.placed, rightKey);
  const right = knownRight ?? place(table[rightIndex], rightAngle, rightTx, rightTy);
  const result = overlapPlaced(left, right);
  // Commit new placements together only after BOTH placements and SAT succeed.
  if (knownLeft !== undefined) { cache.stats.placementHits += 1; touch(cache.placed, leftKey); }
  else retain(cache.placed, leftKey, left, PLACEMENT_CAP);
  if (knownRight !== undefined) { cache.stats.placementHits += 1; touch(cache.placed, rightKey); }
  else retain(cache.placed, rightKey, right, PLACEMENT_CAP);
  retain(cache.pairs, pairKey, result, PAIR_CAP);
  cache.stats.pairEntries = cache.pairs.size;
  cache.stats.placementEntries = cache.placed.size;
  return result;
}

function overlapPlaced(left: readonly PlacedPolygon[], right: readonly PlacedPolygon[]): number {
  for (const a of left) for (const b of right) {
    if (a.maxX < b.minX || b.maxX < a.minX
        || a.maxY < b.minY || b.maxY < a.minY) continue;
    let separated = false;
    for (const axis of [...a.axes, ...b.axes]) {
      const [aLow, aHigh] = projection(a, axis);
      const [bLow, bHigh] = projection(b, axis);
      if (aHigh < bLow || bHigh < aLow) { separated = true; break; }
    }
    if (!separated) return +1.0;
  }
  return +0.0;
}
