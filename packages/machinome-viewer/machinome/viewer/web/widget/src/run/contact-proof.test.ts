/*
 * machinome-viewer - the browser viewer for machinome models
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 */
import { describe, expect, it } from 'vitest';
import { prepare } from '../expressions';
import { constantContact, hasMovingSource } from './contact-proof';

function proves(skeleton: string, level: string, start = 0, delta = 1): boolean {
  return constantContact(prepare(skeleton), prepare(level), { x: start, q: -3.2 },
                         { x: delta }, 'q', -3.2, 1);
}

describe('exact constant-contact certificates', () => {
  it('cancels following motion without changing bank arithmetic', () => {
    expect(proves('32+1+x/7', 'q+4.2-(1+x/7)')).toBe(true);
  });
  it('never erases a tiny positive or negative departure, including subnormals', () => {
    for (const tiny of [1e-30, -1e-30, 5e-324, -5e-324]) {
      expect(proves(`x+(${tiny})*x`, 'q-x')).toBe(false);
    }
  });
  it('checks selection across the entire interval, splitting only exact kinks', () => {
    expect(proves('max(x,-1)', 'q-x')).toBe(true);
    expect(proves('min(x,2)', 'q-x')).toBe(true);
    expect(proves('abs(x)', 'q-x')).toBe(true);
    expect(proves('max(x,.5)', 'q-x')).toBe(false);
    expect(proves('abs(x)', 'q-x', -.5)).toBe(false);
    expect(proves('max(x,.5)', 'q-max(x,.5)')).toBe(true);
    expect(proves('abs(x)+min(x,.3)', 'q-abs(x)-min(x,.3)', -.5)).toBe(true);
  });
  it('falls back for unsupported curves, division and exhausted proof work', () => {
    for (const expression of ['sin(x)', '1/(x+1)', 'x*x']) {
      expect(proves(expression, `q-(${expression})`)).toBe(false);
    }
    expect(constantContact(prepare('max(x,.5)'), prepare('q-max(x,.5)'),
      { x: 0, q: 0 }, { x: 1 }, 'q', 0, 1, new Map(), 1)).toBe(false);
  });
  it('resolves shared bindings and refuses a nonfinite input', () => {
    const bindings = new Map([['_b0', prepare('1+x/7')]]);
    expect(constantContact(prepare('32+_b0'), prepare('q+4.2-_b0'),
      { x: 0, q: -3.2 }, { x: 1 }, 'q', -3.2, 1, bindings)).toBe(true);
    expect(hasMovingSource(prepare('_b0'), { x: 1 }, bindings)).toBe(true);
    expect(hasMovingSource(prepare('_b0'), { x: 0 }, bindings)).toBe(false);
    expect(proves('x', 'q-x', Infinity)).toBe(false);
  });
});
