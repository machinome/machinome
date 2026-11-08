/* Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+ */
import type { ManifestColor, ManifestColorChoice } from './types';
import { evalExpr } from './evaluator';
import type { EvalScope } from './evaluator';

const HEX = /^#[0-9a-f]{6}$/i;

/** Validate the new wire form without changing legacy string/null admission. */
export function assertColor(color: unknown, version: number, where: string): void {
  if (color == null || typeof color === 'string') return;
  if (version < 14) throw new Error(`${where}: conditional color requires document version 14.`);
  if (typeof color !== 'object' || Array.isArray(color)
      || Object.keys(color).sort().join(',') !== 'off,on,when') {
    throw new Error(`${where}: color must be exactly {when, on, off}.`);
  }
  const choice = color as ManifestColorChoice;
  if (typeof choice.when !== 'string' || typeof choice.on !== 'string'
      || typeof choice.off !== 'string' || !HEX.test(choice.on) || !HEX.test(choice.off)) {
    throw new Error(`${where}: color requires a string condition and two six-digit hex colors.`);
  }
}

/** Reserve a colored material before loading; mount resolves the real default
 * before attaching the tree or drawing its first frame. */
export function initialColor(color: ManifestColor): string | null {
  return typeof color === 'object' && color !== null ? color.off : color;
}

export function resolveColor(color: ManifestColor, scope: EvalScope, path: string): string | null {
  if (color === null || typeof color === 'string') return color;
  try {
    const value = evalExpr(color.when, scope);
    if (!Number.isFinite(value)) throw new Error('condition is not finite');
    return value === 0 ? color.off : color.on;
  } catch (error) {
    throw new Error(`Cannot pose ${path || '<root>'}: color condition ${JSON.stringify(color.when)}: ${error instanceof Error ? error.message : String(error)}.`);
  }
}
