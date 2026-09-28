# Implementation evidence

## Authority and scope

Pilot request of 28 September 2026: improve narration, use a feminine voice,
implement typed highlighted actual machine Python in Videomaker, keep subtitles
external, and rebuild one small animation-and-code scene. Planning commit
`a648fca` precedes implementation. No mechanical/viewer changes or publication.

## Red / green

`npm test` initially failed because the source-scene API did not exist; all
eight existing tests passed. The implemented suite passes 13 tests, including
Git-pinned source integrity, invalid ranges/paths, typing holds/seeking/escaping,
v3 request defaults, lossless WAV wrapping and a real FFmpeg first-sample test.
The film HTML has no caption element. Legacy missing/corrupt/overflow MP3 cache
tests remain green. The release film's existing YAML still passes `check`.

The old hydraulic-sawmill tutorial refuses the now-replaced export because its
duration is stale. This is the intended existing guard, not a compatibility
claim or permission to rewrite that earlier episode.

## Phrase-start investigation

`scripts/review-onsets.mjs` compares the first 350 ms after each cached clip
crosses amplitude 0.005 against the same offset in the mix and final MP4.
All 16 V1 narration mix onsets correlate 0.984–0.99999 with their inputs, and
the music/high-pass/AAC master correlates 0.854–0.927. No onset is absent or
attenuated into silence. Some raw clips start nearly immediately: the final
revolution clip crosses the threshold at 0.125 ms and the work clip at 3 ms.
This does not prove the provider supplied an intact/intelligible first phoneme.
There is no demonstrated edit truncation to claim fixed. The new test uses
one coherent V3 take, PCM acquisition, explicit preroll and no music. Padding
does not recover missing speech. Pilot listening remains required.

## Provider and dependency evidence

Official ElevenLabs API documentation and SDK reference confirm timed synthesis
and PCM output. Public `GET /v1/voices` identified Jessica (`cgSgspJ2msm6clMCkdW9`)
as a premade female American voice, “Playful, Bright, Warm”. The existing scoped
key cannot list voices; no new permission was requested or needed. The actual
V3/PCM request succeeded and returned 23.04 seconds with alignment.

- https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps
- https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices
- https://github.com/highlightjs/highlight.js/blob/main/docs/api.rst

Highlight.js 11.12.0 is pinned, Python only, server-side. Package audit reports
one pre-existing moderate YAML 2.8.1 depth/stack-overflow advisory
GHSA-48c2-rrv3-qjmp; dependency remediation was not folded into this feature.

## Consumer review

Consumer: `Leonardo/videos/machinome-source-study`. Nine 1920×1080 preview
frames cover each typing beat and completed source. Real browser checks pass
camera readback, canvas coverage, panel overflow, text equality, deterministic
pixel replay and invalid-camera state preservation. Visually inspected both
partial and complete code; model framing enlarged after the first preview.
Final encoded-media checks are recorded in the consumer's verification record.
This evidence is not human listening approval or publication authorization.
