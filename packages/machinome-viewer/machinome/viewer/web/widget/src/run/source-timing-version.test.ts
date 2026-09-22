/* Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only */
import { describe, expect, it } from 'vitest';
import compact from '../../../../tests/fixtures/source-timing/compact.json';
import timed from '../time-drive-corpus.json';
import running from '../running-corpus.json';
import { assertRenderable } from '../viewer';
import type { Manifest } from '../types';
import { Engine } from './engine';
import type { RunDocument } from './program';

describe('source-timed document v11', () => {
  const documents = [compact.cases[0].document, timed.machines[0].document,
    running.machines.find(machine => machine.name === 'PlayCorpus')!.document];
  it.each(documents)('accepts driver-only, time-drive and Play programs', original => {
    const document = { root: { name: 'test', operations: [], children: [] }, ...structuredClone(original), version: 11 };
    expect(() => assertRenderable(document as unknown as Manifest, '/v11.json')).not.toThrow();
    expect(() => Engine.load(document as unknown as RunDocument, { dt: .1 })).not.toThrow();
  });
  it('still refuses a clock-reading edge without its mapping', () => {
    const document = { ...structuredClone(timed.machines[0].document), version: 11 };
    delete (document.program as { time_drives?: unknown }).time_drives;
    expect(() => Engine.load(document as unknown as RunDocument, { dt: .1 })).toThrow(/time_drives/);
  });
  it('refuses an explicitly empty mapping rather than treating it as absent', () => {
    const document = { ...structuredClone(timed.machines[0].document), version: 11 };
    document.program.time_drives = [];
    expect(() => Engine.load(document as unknown as RunDocument, { dt: .1 })).toThrow(/nonempty/);
  });
});
