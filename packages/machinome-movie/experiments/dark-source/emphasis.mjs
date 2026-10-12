// Experimental source-word emphasis; no stable format contract.
import assert from 'node:assert/strict';

export function resolveEmphasis({source, firstLine, line, phrase, words, alignment, offset, holdSeconds}) {
  const {characters, character_start_times_seconds: starts, character_end_times_seconds: ends} = alignment;
  assert.ok(Array.isArray(characters) && characters.length > 0 &&
    starts?.length === characters.length && ends?.length === characters.length, 'Invalid alignment');
  for (let i = 0; i < starts.length; i++) {
    assert.ok(Number.isFinite(starts[i]) && Number.isFinite(ends[i]) && starts[i] >= 0 &&
      ends[i] >= starts[i] && (i === 0 || starts[i] >= starts[i - 1]), 'Invalid alignment timing');
  }
  assert.ok(Number.isFinite(offset) && offset >= 0 && Number.isFinite(holdSeconds) && holdSeconds >= 0);
  const speech = characters.join('');
  const phraseStart = speech.indexOf(phrase);
  assert.ok(phrase && phraseStart >= 0 && speech.lastIndexOf(phrase) === phraseStart, 'Missing or ambiguous spoken phrase');
  const charIndex = index => Array.from(speech.slice(0, index)).length;
  const to = offset + ends[charIndex(phraseStart + phrase.length) - 1] + holdSeconds;
  const lines = source.split('\n');
  const target = lines[line - firstLine];
  assert.ok(Number.isInteger(line) && typeof target === 'string', 'Missing source token line');
  const lineStart = lines.slice(0, line - firstLine).reduce((n, text) => n + text.length + 1, 0);
  assert.ok(Array.isArray(words) && words.length > 0 && new Set(words).size === words.length);
  const cues = words.map(word => {
    assert.match(word, /^[A-Za-z_]\w*$/);
    const sourceMatches = [...target.matchAll(new RegExp(`\\b${word}\\b`, 'g'))];
    assert.equal(sourceMatches.length, 1, `Missing or ambiguous source token: ${word}`);
    const spokenMatches = [...phrase.matchAll(new RegExp(`\\b${word}\\b`, 'g'))];
    assert.equal(spokenMatches.length, 1, `Missing or ambiguous spoken token: ${word}`);
    const spokenStart = phraseStart + spokenMatches[0].index;
    const start = lineStart + sourceMatches[0].index;
    return {word, line, start, end: start + word.length,
      from: offset + starts[charIndex(spokenStart)],
      wordEnd: offset + ends[charIndex(spokenStart + word.length) - 1], to};
  });
  for (let i = 1; i < cues.length; i++) assert.ok(cues[i].from > cues[i - 1].from, 'Words must follow narration order');
  return cues;
}

export function activeEmphasis(cues, time) {
  return cues.filter(cue => time >= cue.from && time < cue.to);
}
