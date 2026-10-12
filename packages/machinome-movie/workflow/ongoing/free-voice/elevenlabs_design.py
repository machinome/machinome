#!/usr/bin/env python3
"""The same benchmark on ElevenLabs Voice Design, for comparison with the free chain.

Reads the key the videomaker's speech command uses (ELEVENLABS_API_KEY in the
environment or the checkout's .env), designs a voice from voice-elevenlabs.txt
speaking the line, and writes every preview to out/elevenlabs-<n>.mp3 with its
generated_voice_id in out/elevenlabs.json. Nothing is saved to the voice
library: creating the voice from a preview is a separate, deliberate step.
"""
import base64, json, os, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
LINE = ("I'm Machinome, and my purpose is to enable all machines to be open source. "
        "What do you want to build next?")


def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if k is not None:
        return k
    for env in (HERE.parents[2] / ".env",):
        if env.is_file():
            for line in env.read_text().splitlines():
                if line.startswith("ELEVENLABS_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"')
    sys.exit("no ELEVENLABS_API_KEY in the environment or the videomaker's .env")


def main():
    description = (HERE / "voice-elevenlabs.txt").read_text().strip()
    text = (HERE / sys.argv[1]).read_text().strip() if len(sys.argv) > 1 else LINE
    body = {"voice_description": description, "text": text, "model_id": "eleven_ttv_v3",
            "guidance_scale": float(os.environ.get("GUIDANCE", "5"))}
    req = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-voice/design?output_format=mp3_44100_128",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"xi-api-key": key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs HTTP {e.code}: {e.read().decode()[:400]}")
    out = HERE / "out"; out.mkdir(exist_ok=True)
    record = {"description": description, "text": data.get("text", text), "model_id": body["model_id"],
              "guidance_scale": body["guidance_scale"], "previews": []}
    for i, p in enumerate(data["previews"], 1):
        f = out / f"elevenlabs-{i}.mp3"
        f.write_bytes(base64.b64decode(p["audio_base_64"]))
        record["previews"].append({"file": f.name, "generated_voice_id": p["generated_voice_id"],
                                   "duration_secs": p.get("duration_secs"), "language": p.get("language")})
        print(f"wrote {f} ({p.get('duration_secs')}s) id {p['generated_voice_id']}")
    (out / "elevenlabs.json").write_text(json.dumps(record, indent=1))


if __name__ == "__main__":
    main()
