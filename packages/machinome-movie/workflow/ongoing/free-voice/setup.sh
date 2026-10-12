#!/usr/bin/env bash
# One-time setup on the CUDA host: a venv beside this script with the whole free chain.
# torch, torchaudio and ctranslate2 ship wheels for CPython 3.10 to 3.12 only (no PyPy),
# so the venv is made from one of those; uv fetches one when the host has none.
set -euo pipefail
cd "$(dirname "$0")"

pick_python() {
  for p in python3.12 python3.11 python3.10 python3; do
    if command -v "$p" >/dev/null 2>&1 && "$p" -c 'import sys, platform; sys.exit(0 if platform.python_implementation() == "CPython" and (3,10) <= sys.version_info[:2] <= (3,12) else 1)'; then
      command -v "$p"; return 0
    fi
  done
  return 1
}

# A venv made from the wrong interpreter (PyPy, or a Python without wheels) is replaced.
if [ -x .venv/bin/python ] && ! .venv/bin/python -c 'import sys, platform; sys.exit(0 if platform.python_implementation() == "CPython" and (3,10) <= sys.version_info[:2] <= (3,12) else 1)'; then
  echo "existing .venv is $(.venv/bin/python -c 'import platform; print(platform.python_implementation(), platform.python_version())'); replacing it"
  rm -rf .venv
fi

if [ ! -x .venv/bin/python ]; then
  if py=$(pick_python); then
    echo "using $py ($("$py" -c 'import platform; print(platform.python_implementation(), platform.python_version())'))"
    "$py" -m venv .venv
  elif command -v uv >/dev/null 2>&1; then
    echo "no CPython 3.10-3.12 on PATH; uv fetches 3.12"
    uv venv --python 3.12 .venv
  else
    echo "no CPython 3.10-3.12 on PATH and no uv. Install one of:" >&2
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh     (then rerun ./setup.sh)" >&2
    echo "  sudo apt install python3.12 python3.12-venv         (Debian/Ubuntu)" >&2
    exit 1
  fi
fi

pip=".venv/bin/pip"
[ -x "$pip" ] || .venv/bin/python -m ensurepip --upgrade
.venv/bin/python -m pip install -U pip
# torch and torchaudio first, so qwen-tts resolves against the CUDA build already present.
.venv/bin/python -m pip install -U torch torchaudio
.venv/bin/python -m pip install -U qwen-tts soundfile faster-whisper
.venv/bin/python - <<'PY'
import sys, torch
print("python", sys.version.split()[0], "torch", torch.__version__, "cuda", torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")
PY
echo "setup done; now ./run.sh"
