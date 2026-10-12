#!/usr/bin/env python3
"""Free-voice spike: design a voice, freeze it as a reference, speak a line
through the clone path, and align the result in the videomaker's record shape.

Chain (all free weights):
  Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign  (Apache-2.0)  designs the voice from words
  Qwen/Qwen3-TTS-12Hz-1.7B-Base         (Apache-2.0)  speaks any line from that reference
  faster-whisper + Whisper weights       (MIT)         word timing for captions

Outputs, in --out:
  reference.wav         the designed voice saying the reference text (the character's identity)
  design-line.wav       the designed voice saying the line directly (design model, comparison only)
  clone-line.wav        the line spoken through the clone path (what production would use)
  clone-line.json       alignment record in the videomaker's shape, when --align is on
  run.json              everything that went in: prompt, texts, models, versions, timings

Run on a CUDA host:  ./run.sh   (see README.md)
"""
import argparse, json, platform, re, sys, time
from pathlib import Path

DESIGN_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
BASE_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"

LINE = ("I'm Machinome, and my purpose is to enable all machines to be open source. "
        "What do you want to build next?")

REFERENCE_TEXT = ("Every machine has a source: how its parts belong together, and how they move. "
                  "Gears, levers, belts and frames. Write it down, and anyone can build it again.")


def read_text(value):
    p = Path(value)
    return p.read_text(encoding="utf-8").strip() if p.is_file() else value


def load(model_id, attn, device):
    import torch
    from qwen_tts import Qwen3TTSModel
    kwargs = dict(device_map=device, dtype=torch.bfloat16)
    if attn != "auto":
        kwargs["attn_implementation"] = attn
    t = time.time()
    model = Qwen3TTSModel.from_pretrained(model_id, **kwargs)
    print(f"loaded {model_id} in {time.time() - t:.1f}s", flush=True)
    return model


def write(path, wav, sr):
    import soundfile as sf
    sf.write(str(path), wav, sr)
    print(f"wrote {path} ({len(wav) / sr:.2f}s @ {sr} Hz)", flush=True)


def spread(text, spans):
    """Character timing from one (start, end) span per whitespace-separated word.

    Characters of a word share its span evenly; whitespace between two words
    spans the gap; leading and trailing whitespace are zero-length. The result
    is monotonic and non-negative, as validateAlignment in src/words.mjs requires.
    """
    parts = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
    if len(parts) != len(spans):
        raise ValueError(f"{len(parts)} words, {len(spans)} spans")
    starts, ends = [0.0] * len(text), [0.0] * len(text)
    prev_end, prev_time = 0, 0.0
    for (s, e), (ws, we) in zip(parts, spans):
        for k in range(prev_end, s):
            starts[k], ends[k] = prev_time, ws
        n = e - s
        for k in range(s, e):
            starts[k] = ws + (we - ws) * (k - s) / n
            ends[k] = ws + (we - ws) * (k - s + 1) / n
        prev_end, prev_time = e, we
    for k in range(prev_end, len(text)):
        starts[k] = ends[k] = prev_time
    last_s = last_e = 0.0
    for k in range(len(text)):
        starts[k] = round(max(starts[k], last_s, 0.0), 4)
        ends[k] = round(max(ends[k], starts[k], last_e), 4)
        last_s, last_e = starts[k], ends[k]
    return {"characters": list(text), "character_start_times_seconds": starts, "character_end_times_seconds": ends}


def align(audio, text, language, whisper_size, device):
    """Word timing from Whisper, spread over the characters of the exact text.

    The record keeps the narration's own characters, so the videomaker's
    caption and word-onset code reads it unchanged. Whisper only supplies the
    timing; its words are matched to the text's words in order. When the
    counts differ, the heard span is spread over the text's words in
    proportion to their length, and the mismatch is reported in run.json.
    """
    from faster_whisper import WhisperModel
    dev = "auto" if device == "auto" else device.split(":")[0]
    model = WhisperModel(whisper_size, device=dev, compute_type="float16" if dev == "cuda" else "int8")
    segments, _ = model.transcribe(str(audio), word_timestamps=True, language=language, initial_prompt=text)
    heard = [w for s in segments for w in s.words]
    words = [m.group() for m in re.finditer(r"\S+", text)]
    report = {"text_words": len(words), "heard_words": len(heard),
              "heard": [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for w in heard]}
    if not heard:
        return None, report
    if len(heard) == len(words):
        spans = [(w.start, w.end) for w in heard]
    else:
        print(f"alignment: Whisper heard {len(heard)} words, text has {len(words)}; timing interpolated", flush=True)
        total = sum(len(w) for w in words)
        t0, t1 = heard[0].start, heard[-1].end
        cursor, spans = t0, []
        for w in words:
            d = (t1 - t0) * len(w) / total
            spans.append((cursor, cursor + d)); cursor += d
    return spread(text, spans), report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="out", help="output directory")
    ap.add_argument("--instruct", default="voice.txt", help="voice description, a file or the text itself")
    ap.add_argument("--line", default=LINE, help="the line to speak, a file or the text itself")
    ap.add_argument("--reference-text", default=REFERENCE_TEXT, help="what the designed voice says to fix its identity")
    ap.add_argument("--language", default="English")
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--attn", default="sdpa", choices=["sdpa", "flash_attention_2", "eager", "auto"],
                    help="attention backend; flash_attention_2 needs the flash-attn wheel")
    ap.add_argument("--align", action="store_true", help="also align the clone line with faster-whisper")
    ap.add_argument("--whisper", default="small", help="Whisper size for alignment (tiny, base, small, medium)")
    ap.add_argument("--skip-design-line", action="store_true", help="do not speak the line through the design model")
    a = ap.parse_args()

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    instruct, line, ref_text = read_text(a.instruct), read_text(a.line), read_text(a.reference_text)
    run = {"instruct": instruct, "line": line, "reference_text": ref_text, "language": a.language,
           "design_model": DESIGN_MODEL, "base_model": BASE_MODEL, "attn": a.attn,
           "python": platform.python_version(), "timings": {}}
    try:
        import torch, qwen_tts
        run["torch"] = torch.__version__; run["qwen_tts"] = getattr(qwen_tts, "__version__", "?")
        run["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none"
    except Exception as e:  # noqa: BLE001
        print(f"cannot import the chain: {e}", file=sys.stderr); sys.exit(2)
    print(f"GPU: {run['gpu']}", flush=True)

    # 1. Design the voice: the reference clip is the character's identity.
    design = load(DESIGN_MODEL, a.attn, a.device)
    t = time.time()
    wavs, sr = design.generate_voice_design(text=ref_text, language=a.language, instruct=instruct)
    run["timings"]["reference"] = round(time.time() - t, 2)
    write(out / "reference.wav", wavs[0], sr)
    if not a.skip_design_line:
        t = time.time()
        wavs2, sr2 = design.generate_voice_design(text=line, language=a.language, instruct=instruct)
        run["timings"]["design_line"] = round(time.time() - t, 2)
        write(out / "design-line.wav", wavs2[0], sr2)
    del design
    torch.cuda.empty_cache()

    # 2. Speak the line through the clone path: what every later narration would do.
    base = load(BASE_MODEL, a.attn, a.device)
    t = time.time()
    prompt = base.create_voice_clone_prompt(ref_audio=str(out / "reference.wav"), ref_text=ref_text)
    wavs3, sr3 = base.generate_voice_clone(text=line, language=a.language, voice_clone_prompt=prompt)
    run["timings"]["clone_line"] = round(time.time() - t, 2)
    write(out / "clone-line.wav", wavs3[0], sr3)
    run["sample_rate"] = sr3
    del base
    torch.cuda.empty_cache()

    # 3. Timing for captions, in the videomaker's alignment shape.
    if a.align:
        t = time.time()
        try:
            alignment, report = align(out / "clone-line.wav", line, "en" if a.language == "English" else None,
                                      a.whisper, a.device)
        except Exception as e:  # noqa: BLE001  (missing cuDNN for ctranslate2 is the usual cause)
            print(f"alignment on {a.device} failed ({e}); retrying on the CPU", flush=True)
            alignment, report = align(out / "clone-line.wav", line, "en" if a.language == "English" else None,
                                      a.whisper, "cpu")
        run["timings"]["align"] = round(time.time() - t, 2)
        run["alignment_report"] = report
        if alignment:
            record = {"provider": "qwen3-tts", "voice": "reference.wav", "model": BASE_MODEL,
                      "format": f"pcm_{sr3}", "request": {"text": line, "language": a.language},
                      "alignment": alignment, "duration": round(len(wavs3[0]) / sr3, 3)}
            (out / "clone-line.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
            print(f"wrote {out / 'clone-line.json'}", flush=True)
    (out / "run.json").write_text(json.dumps(run, indent=1), encoding="utf-8")
    print(json.dumps(run["timings"]), flush=True)


if __name__ == "__main__":
    main()
