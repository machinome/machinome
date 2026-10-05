#!/bin/bash
# verify.sh <repo> <old-prefix>
#   old-prefix: "origin/" in the rehearsal clone, "refs/original/refs/heads/" in the real repo.
# Checks the rewritten history against the plan. Exit 0 only when every check passes.
set -u
REPO=$1; OLD=$2; BASE=bf24687da524264c43dcecad76527ce71431e343
S=$(dirname "$(readlink -f "$0")")
cd "$REPO" || exit 2
fail=0
ok()   { echo "ok    $*"; }
bad()  { echo "FAIL  $*"; fail=1; }

REL=$(git log --format=%H --grep='^licence: Machinome is GPL-2.0-or-later' main | tail -1)
[ -n "$REL" ] && ok "licence commit $REL" || bad "no licence commit on main"
[ "$(git rev-parse $REL^)" = "$BASE" ] && ok "licence commit's parent is bf24687" || bad "licence commit's parent is $(git rev-parse --short $REL^)"

n=$(git rev-list --count $REL..main); [ "$n" = 75 ] && ok "75 commits after the licence commit" || bad "$n commits after the licence commit"
m=$(git rev-list --merges --count $REL..main); [ "$m" = 8 ] && ok "8 merges" || bad "$m merges"
for b in dume-native-freecad native-freecad-assembly record-voron-warts; do
  e=$(git rev-list --count main..$b); [ "$e" = 1 ] && ok "$b is one commit beyond main" || bad "$b is $e commits beyond main"
done

fmt='%an|%ae|%ad|%cn|%ce|%cd|%s'
for b in main dume-native-freecad native-freecad-assembly record-voron-warts; do
  if diff -q <(git log --topo-order --format="$fmt" $BASE..${OLD}$b) <(git log --topo-order --format="$fmt" $REL..$b) >/dev/null; then ok "$b: authors, dates, messages identical"; else bad "$b: metadata differs"; fi
done
if diff -q <(git log --graph --format=%s $BASE..${OLD}main) <(git log --graph --format=%s $REL..main) >/dev/null; then ok "main: graph identical"; else bad "main: graph differs"; fi

bad_commits=0
for c in $(git rev-list $REL..main main..dume-native-freecad main..native-freecad-assembly main..record-voron-warts); do
  err=""
  [ -z "$(git grep -l 'SPDX-License-Identifier: Apache-2.0' $c -- . 2>/dev/null)" ] || err="$err apache-header"
  [ -z "$(git grep -l 'SPDX-License-Identifier: AGPL' $c -- . 2>/dev/null)" ] || err="$err agpl-header"
  git cat-file -e $c:LICENSES/GPL-2.0-or-later.txt 2>/dev/null || err="$err no-gpl-text"
  git cat-file -e $c:LICENSES/CERN-OHL-S-2.0.txt 2>/dev/null || err="$err no-ohl-text"
  git cat-file -e $c:NOTICE 2>/dev/null && err="$err notice-present"
  git show $c:pyproject.toml | grep -q 'license = "GPL-2.0-or-later OR CERN-OHL-S-2.0+"' || err="$err pyproject-expression"
  git show $c:pyproject.toml | grep -qi apache && err="$err pyproject-apache"
  git show $c:LICENSE | cmp -s - "$S/LICENSE" || err="$err licence-statement"
  if [ -n "$err" ]; then bad "$(git rev-parse --short $c):$err"; bad_commits=$((bad_commits+1)); fi
done
[ $bad_commits = 0 ] && ok "every rewritten commit carries the instruments and no old header"

echo "--- files that differ between old main and new main, by directory:"
git diff --name-only ${OLD}main main | awk -F/ '{print ($0 ~ /\// ? $1"/" : $0)}' | sort | uniq -c
unexpected=$(git diff --name-only ${OLD}main main | grep -v -E '^(LICENSE|LICENSES/.*|NOTICE|MANIFEST.in|pyproject.toml|CREDITS.md|AI-USE.md|openspec/specs/framework-identity/spec.md|docs/conf.py)$' | grep -v -E '\.py$|\.toml$')
[ -z "$unexpected" ] && ok "old main -> new main: only instruments and headers differ" || bad "unexpected differences: $(echo $unexpected | tr '\n' ' ')"
for f in README.rst HISTORY.rst docs/architecture.md; do git diff --quiet ${OLD}main main -- $f && ok "$f untouched at the tip" || bad "$f changed at the tip"; done

git merge-base --is-ancestor $BASE main && ok "main is a fast-forward of bf24687" || bad "main does not descend from bf24687"
echo "tip: $(git rev-parse main)   licence commit: $REL"
exit $fail
