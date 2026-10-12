/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

/** Physical paths, scoped to one propagation. No sampled approximation. */
export type Piece = [number, number, (t: number) => number];
/** Immutable scalar result of one committed, effect-free cyclic block. */
export interface ConstantBlockEntry {
  readonly key: readonly (string | number | boolean)[];
  readonly generation: number;
  readonly outputs: readonly { readonly name: string; readonly start: number;
    readonly end: number; readonly exactTerminal: boolean; readonly increment: number }[];
}

export interface ConstantBlockReuse {
  readonly stored: ReadonlyMap<object, ConstantBlockEntry>;
  readonly pending: Map<object, ConstantBlockEntry>;
}
export class Motion {
  readonly constant: boolean;
  private readonly cache = new Map<number, number>();

  constructor(readonly start: number, readonly end: number,
              public pieces: Piece[], readonly affine = true,
              readonly exactTerminal = false) {
    this.cache.set(0, start);
    this.cache.set(1, end);
    this.constant = affine && start === end
      && (!exactTerminal || Object.is(start, end))
      && pieces.every(([a, b, at]) => at(a) === start && at(b) === start);
    if (this.constant) this.pieces = [[0, 1, () => start]];
  }

  static line(start: number, delta: number): Motion {
    return new Motion(start, start + delta, [[0, 1, t => start + delta * t]]);
  }

  at(t: number): number {
    const cached = this.cache.get(t);
    if (cached !== undefined) return cached;
    let low = 0;
    let high = this.pieces.length - 1;
    while (low < high) {
      const mid = Math.floor((low + high) / 2);
      if (this.pieces[mid][1] <= t) low = mid + 1;
      else high = mid;
    }
    const value = this.pieces[low][2](t);
    this.cache.set(t, value);
    return value;
  }

  cuts(left = 0, right = 1): number[] {
    return this.pieces.map(piece => piece[1]).filter(t => left < t && t < right);
  }

  restrict(left: number, right: number): Motion {
    const width = right - left;
    const edges = [left, ...this.cuts(left, right), right];
    return new Motion(this.at(left), this.at(right), edges.slice(0, -1).map(
      (a, i) => [(a - left) / width, (edges[i + 1] - left) / width,
        t => this.at(left + width * t)]), this.affine,
      this.exactTerminal && right === 1);
  }
}

export interface Propagation {
  motions: Map<string, Motion>;
  /** Present only during a Run's primary integration pass, never prefix replay. */
  blockReuse?: ConstantBlockReuse;
  /** Absolute endpoints of the rare full-terminal absolute request. */
  terminals?: Map<string, number>;
  demanded: ReadonlySet<string>;
  untraced: Set<string>;
  followCuts?: Map<string, number[]>;
  followClosures?: Map<string, [number, number, number, number][]>;
}
// Metadata cannot become a bank key or survive a serialized snapshot.
export const propagations = new WeakMap<Record<string, number>, Propagation>();
const sources = new WeakMap<Record<string, number>, Map<string, Motion>>();

export function sourceDeltas(motions: Map<string, Motion>): Record<string, number> {
  const delta: Record<string, number> = {};
  for (const [name, motion] of motions) {
    delta[name] = motion.end - motion.start
      || (!motion.affine || motion.cuts().length ? 1 : 0);
  }
  sources.set(delta, motions);
  return delta;
}

export function curved(delta: Record<string, number>): boolean {
  return sources.has(delta);
}

export function copyHolding(delta: Record<string, number>, own: string): Record<string, number> {
  const copy = { ...delta, [own]: 0 };
  const original = sources.get(delta);
  if (original) {
    const paths = new Map(original);
    paths.delete(own);
    sources.set(copy, paths);
  }
  return copy;
}

export function alongSources(start: Record<string, number>, delta: Record<string, number>,
                             t: number): Record<string, number> {
  const paths = sources.get(delta);
  return Object.fromEntries(Object.keys(start).map(name => [name,
    paths?.get(name)?.at(t) ?? start[name] + (delta[name] ?? 0) * t]));
}
