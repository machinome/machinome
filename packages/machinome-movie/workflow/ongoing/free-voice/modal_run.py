"""Run spike.py on a rented GPU through Modal, from a machine with no GPU.

    modal run modal_run.py                        # the benchmark on a T4, results into ./out
    FREE_VOICE_GPU=A10G modal run modal_run.py    # faster; needs a payment method on the account
    modal run modal_run.py --extra "--language Portuguese --line pt.txt"

The container gets spike.py and voice.txt from this directory; the Hugging
Face cache lives in a Modal volume so the 7 GB of weights download once.
Every output file of the run comes back into ./out.
"""
import os
from pathlib import Path
import modal

HERE = Path(__file__).parent
HF_CACHE = "/hf-cache"
GPU = os.environ.get("FREE_VOICE_GPU", "T4")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libsndfile1", "ffmpeg")
    .pip_install("torch", "torchaudio")
    .pip_install("qwen-tts", "soundfile", "faster-whisper")
    .env({"HF_HOME": HF_CACHE, "HF_HUB_ENABLE_HF_TRANSFER": "0"})
    .add_local_file(HERE / "spike.py", "/work/spike.py")
    .add_local_file(HERE / "voice.txt", "/work/voice.txt")
)
cache = modal.Volume.from_name("free-voice-hf-cache", create_if_missing=True)
app = modal.App("free-voice-spike", image=image)


@app.function(gpu=GPU, timeout=45 * 60, volumes={HF_CACHE: cache})
def run(extra: list[str], inputs: dict[str, bytes]) -> dict[str, bytes]:
    import subprocess, sys
    work = Path("/work")
    for name, data in inputs.items():          # files named on the command line
        (work / name).write_bytes(data)
    out = Path("/tmp/out")
    cmd = [sys.executable, str(work / "spike.py"), "--out", str(out), "--instruct", str(work / "voice.txt"), "--align", *extra]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=work)
    cache.commit()
    return {p.name: p.read_bytes() for p in out.iterdir() if p.is_file()}


@app.local_entrypoint()
def main(extra: str = "", out: str = "out"):
    args = extra.split()
    # Any argument naming a local file travels with the call and is read from /work there.
    inputs, sent = {}, []
    for a in args:
        p = HERE / a
        if p.is_file() and a not in ("voice.txt", "spike.py"):
            inputs[p.name] = p.read_bytes(); sent.append(p.name)
    files = run.remote(args, inputs)
    target = HERE / out
    target.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (target / name).write_bytes(data)
        print(f"wrote {target / name} ({len(data)} bytes)")
