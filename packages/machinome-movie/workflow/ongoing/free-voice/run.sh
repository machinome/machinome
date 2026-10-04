#!/usr/bin/env bash
# The benchmark: one voice prompt (voice.txt), the line, the clone path, the alignment.
# First run downloads two 1.7B checkpoints (about 7 GB) and a Whisper model into ~/.cache.
set -euo pipefail
cd "$(dirname "$0")"
exec .venv/bin/python spike.py --out out --instruct voice.txt --align "$@"
