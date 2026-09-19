#!/bin/sh
# Every probe of this change, in order. Run from the worktree root:
#
#   sh openspec/changes/name-the-missing-file/evidence/run-probes.sh
#
# WORKTREE is this framework worktree; PY is the workspace venv.
set -u
WORKTREE=$(cd "$(dirname "$0")/../../../.." && pwd)
HERE="$WORKTREE/openspec/changes/name-the-missing-file/evidence"
PY=/home/asa/devel/libresolid-studio/.venv/bin/python
SOLID=/home/asa/devel/libresolid-studio/.venv/bin/solid

# `a_directory` is the "declared source exists but is not a file" case; it
# is empty, so it is created here rather than committed.
mkdir -p "$HERE/probe_project/a_directory" "$HERE/probe_project/_build.lock"

echo "### probe_when.py"
PYTHONPATH="$WORKTREE" "$PY" "$HERE/probe_when.py" 2>&1

echo
echo "### probe_declarative.py"
PYTHONPATH="$WORKTREE" "$PY" "$HERE/probe_declarative.py" 2>&1

echo
echo "### probe_vanishing.py"
PYTHONPATH="$WORKTREE" "$PY" "$HERE/probe_vanishing.py" 2>&1

echo
echo "### probe_bare.py"
PYTHONPATH="$WORKTREE" "$PY" "$HERE/probe_bare.py" 2>&1

for model in parts:MissingStl parts:MissingStep assembly:Rig \
             parts:DirectoryStl parts:DirectoryStep; do
    echo
    echo "### solid build, model = $model"
    sed -i "s|^model = .*|model = \"$model\"|" "$HERE/probe_project/pyproject.toml"
    (cd "$HERE/probe_project" && PYTHONPATH="$WORKTREE" "$SOLID" build 2>&1 | tail -4)
done
sed -i 's|^model = .*|model = "parts:MissingStl"|' "$HERE/probe_project/pyproject.toml"

# Leave no build tree or generated source behind.
rm -rf "$HERE/probe_project/_build" "$HERE/probe_project/__pycache__" \
       "$HERE/__pycache__" "$HERE/probe_project/vanishing.js" \
       "$HERE/probe_project/a_directory" "$HERE/probe_project/_build.lock"
