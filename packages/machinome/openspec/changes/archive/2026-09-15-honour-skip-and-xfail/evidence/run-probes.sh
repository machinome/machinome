#!/bin/sh
# Every measurement in ../evidence.md, re-runnable from the worktree root:
#
#     sh openspec/changes/honour-skip-and-xfail/evidence/run-probes.sh
#
# Writes transcripts beside this script. `solid test` builds the fixture,
# so it creates evidence/skip_xfail_project/_build/ and __pycache__/ under
# the fixture's own directory; nothing is written anywhere else.
set -e
ROOT=$(pwd)
VENV=/home/asa/devel/libresolid-studio/.venv
E="$ROOT/openspec/changes/honour-skip-and-xfail/evidence"
export PYTHONPATH="$ROOT"

"$VENV/bin/python" "$E/probe_unittest_reference.py" \
    > "$E/out-unittest-reference.txt" 2>&1 || true
"$VENV/bin/python" "$E/probe_runner_mechanism.py" \
    > "$E/out-runner-mechanism.txt" 2>&1 || true

# The build's own chatter is noise here; everything the runner itself
# prints is kept.
FILTER='INFO -|Geometries in cache|Geometry cache size|CGAL |Total rendering|Top level object|   Facets'

cli () {   # cli <output name> <solid test arguments...>
    name=$1
    shift
    cd "$E/skip_xfail_project"
    if "$VENV/bin/solid" test "$@" > "$E/.raw" 2>&1; then
        status=0
    else
        status=$?
    fi
    grep -Ev "$FILTER" "$E/.raw" > "$E/$name"
    printf '\n[exit code %s]\n' "$status" >> "$E/$name"
    rm -f "$E/.raw"
}

cli out-cli-widget.txt widget.py
cli out-cli-sweeper.txt sweeper.py
cli out-cli-faceted.txt --faceted widget.py
cli out-cli-failfast.txt --failfast sweeper.py
echo "probes done"
