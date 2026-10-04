# Free-voice spike

Working record, 4 October 2026. The videomaker's narration comes from
ElevenLabs, a proprietary model. This spike tests a chain with free weights
end to end, for a voice character that belongs to nobody: designed from a
description, frozen as a reference clip, and spoken through the clone path
for every later line.

| Step | Model | Licence |
| --- | --- | --- |
| Design the voice from words | `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` | Apache-2.0 |
| Speak any line in that voice | `Qwen/Qwen3-TTS-12Hz-1.7B-Base` | Apache-2.0 |
| Word timing for captions | faster-whisper with Whisper weights | MIT |

The benchmark is one prompt, `voice.txt`, speaking one line. The prompt
describes a plain human voice on purpose: the test is how far the model
gets on naturalness before any character is layered on. Qwen's own prompt
style is followed (sex, age, range, then manner), with the reference text in
character so the clip that fixes the identity already sounds like the thing.

## Run on the CUDA host

```sh
./setup.sh      # once: venv, qwen-tts, faster-whisper
./run.sh        # the benchmark; about 7 GB of downloads on first run
```

`run.sh` passes extra flags to `spike.py`: `--attn flash_attention_2` when
the flash-attn wheel is installed (faster; `sdpa` is the default and needs
nothing), `--language Portuguese` with `--line` and `--reference-text` for
the Portuguese check, `--whisper medium` for tighter timing.

## What comes out, in `out/`

- `reference.wav`: the designed voice saying the reference text. If the voice
  is approved, this file is the character and is kept immutable; a second
  design run gives a different voice.
- `design-line.wav`: the line said by the design model directly. Comparison
  only; production never runs this path twice.
- `clone-line.wav`: the line spoken through the clone path from the
  reference. This is what every narration would sound like.
- `clone-line.json`: the alignment in the shape `src/speech.mjs` caches
  today (`characters`, `character_start_times_seconds`,
  `character_end_times_seconds` over the narration's own characters), so
  captions and word onsets read it unchanged. Whisper's words are matched to
  the text's words in order; a count mismatch is reported in `run.json` and
  the timing is interpolated.
- `run.json`: prompt, texts, model ids, versions, GPU, per-step timings.

## What to listen for

1. Does `clone-line.wav` keep the voice of `reference.wav`? The clone path is
   the one that matters; the design path is heard once.
2. Naturalness against the ElevenLabs takes of the first episode: pacing,
   the pauses at commas, the lift on the question.
3. The alignment: play `clone-line.wav` against the word onsets in
   `clone-line.json` once the record is dropped into a take.

## Not decided here

The speech provider is still ElevenLabs. Making it pluggable, naming the
provider in the cache record and keeping the reference clip under version
control are the change this spike is evidence for, not part of it.
