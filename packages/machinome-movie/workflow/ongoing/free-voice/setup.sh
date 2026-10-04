#!/usr/bin/env bash
# One-time setup on the CUDA host: a venv beside this script with the whole free chain.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -U pip
# torch on Linux installs the CUDA build by default; qwen-tts pulls it in.
.venv/bin/pip install -U qwen-tts soundfile faster-whisper
.venv/bin/python - <<'PY'
import torch; print("torch", torch.__version__, "cuda", torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")
PY
echo "setup done; now ./run.sh"
