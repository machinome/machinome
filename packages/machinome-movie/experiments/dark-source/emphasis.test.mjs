import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveEmphasis, activeEmphasis} from './emphasis.mjs';

const phrase = 'Here, the waterwheel drives the crankshaft.';
const source = 'class Mill:\n    water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)';
const alignment = {
  characters: Array.from('Intro. ' + phrase),
  character_start_times_seconds: Array.from('Intro. ' + phrase, (_, i) => i / 10),
  character_end_times_seconds: Array.from('Intro. ' + phrase, (_, i) => (i + 1) / 10),
};
const input = {source, firstLine: 365, line: 366, phrase,
  words: ['waterwheel', 'drives', 'crankshaft'], alignment, offset: 0.8, holdSeconds: 1};

test('emphasis targets literal source tokens and measured spoken onsets', () => {
  const cues = resolveEmphasis(input);
  for (const cue of cues) {
    assert.equal(source.slice(cue.start, cue.end), cue.word);
    assert.equal(cue.from, alignment.characters.join('').indexOf(cue.word) / 10 + 0.8);
  }
  assert.equal(cues[0].start, source.indexOf('waterwheel'));
  assert.deepEqual(activeEmphasis(cues, cues[1].from).map(c => c.word), ['waterwheel', 'drives']);
  assert.deepEqual(activeEmphasis(cues, cues[2].from).map(c => c.word), input.words);
  assert.deepEqual(activeEmphasis(cues, cues[2].to), []);
});

test('emphasis refuses stale source, missing or ambiguous speech, and invalid alignment', () => {
  assert.throws(() => resolveEmphasis({...input, line: 365}), /source token/);
  assert.throws(() => resolveEmphasis({...input, words: ['waterwheeel']}), /source token/);
  assert.throws(() => resolveEmphasis({...input, phrase: 'Not spoken'}), /spoken phrase/);
  assert.throws(() => resolveEmphasis({...input, phrase: 'the'}), /spoken phrase/);
  assert.throws(() => resolveEmphasis({...input, alignment: {...alignment, character_end_times_seconds: []}}), /alignment/);
});

test('half-open cues replay deterministically without early emphasis', () => {
  const cues = resolveEmphasis(input);
  const first = cues[0];
  assert.deepEqual(activeEmphasis(cues, first.from - 0.001), []);
  assert.equal(activeEmphasis(cues, first.from)[0].word, 'waterwheel');
  assert.deepEqual(activeEmphasis(cues, first.from), activeEmphasis(cues, first.from));
});
