## Context

The existing film stage burns alignment captions and has no source panel. Speech
is cached MP3 from multilingual v2. Initial comparison of all 16 V1 clip onsets
against narration.wav finds correlations 0.977–0.99999 over their first 500 ms:
the mix retains them. This does not establish intelligibility or clear the final
music master. The reported clipped starts remain a listening issue to evaluate.

## Goals / Non-Goals

Show real source beside existing 3D, type it with authored narration timing,
deliver optional subtitles, and support a better feminine performance. No Python
execution, alternate mechanics, full-film rebuild, or claim of an audio repair
unsupported by evidence.

## Decisions

- Production `sourceCode` entries select `file` and inclusive `lines: [first,last]`.
  Paths resolve from production.yaml, must be Python files inside the project,
  and bytes must match Git at model.sourceRevision. Record full-file/excerpt hashes.
  Dedent common leading spaces only; preserve everything else. This is stronger
  evidence than duplicated text in the screenplay.
- Shot `code: {snippet, typing: [{from,to,throughLine}]}` uses shot-local seconds
  and absolute source line numbers. Increasing cues reveal complete line groups
  character-by-character; gaps hold. Authors align them after measuring narration.
  At any time this is a pure function, so seeking and resumed renders agree.
- Highlight.js Python grammar renders escaped markup on the Node side. A stable
  side-by-side stage holds code left and the real paused viewer right. Shots
  without code keep their existing layout. No remote runtime dependencies.
- Remove the caption DOM entirely. Keep generated captions.json and captions.srt;
  narrated renders also write `<video-basename>.srt` for player auto-discovery.
- Optional `audio.outputFormat: pcm_24000` wraps provider PCM in a WAV without
  trimming. Legacy MP3 cache identity remains unchanged. V3 requests omit legacy
  continuity fields and use valid stability defaults. A single coherent paragraph
  in the test avoids restarting synthesis for every sentence.
- Explicit speechOffset leaves preroll, never removes samples. Mix without a gate
  or fade-in. Synthetic onset tests prove first samples survive at the offset;
  inspection records distinguish waveform preservation from listening approval.
- Derive replay times, contact sheets and thumbnail indices from episode length.

## Risks / Trade-offs

- Long code lines → wrap while preserving line numbers; fail browser review on
  overflow. Select a small excerpt rather than shrink text indefinitely.
- Speech expressiveness/intelligibility → pilot auditions the short V3 feminine
  scene before full-film regeneration; no claim that automated checks hear it.
- V3 or PCM unavailable → report provider refusal, no hidden model substitution.
- Changed caption default → documented breaking presentation change authorized
  by the pilot; existing mastered videos are untouched.

## Migration Plan

Keep format draft 0.2 with additive source/audio fields and the explicitly changed
caption presentation. Existing cached narration remains usable. Re-rendering old
episodes now yields external subtitles. Reverting the tool commit restores the
old presentation; no media or mechanical source is deleted.

## Open Questions

The pilot's listening judgment of the new voice and phrase beginnings remains
separate from implementation acceptance and publication approval.
