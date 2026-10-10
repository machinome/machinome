"""Apply a change's MODIFIED requirement blocks to the baseline specs,
exactly as `openspec archive` would, without its refusal to drop a
scenario the change deliberately removes. Usage:
    sync_modified.py <repo> <change>
"""
import re
import sys
from pathlib import Path

repo, change = Path(sys.argv[1]), sys.argv[2]
HEADER = re.compile(r'^### Requirement: (.+?)\s*$', re.M)


def blocks(text):
    """{name: raw block} for every requirement block in `text`, block =
    header through the line before the next `### Requirement:` or `## `."""
    out = {}
    matches = list(HEADER.finditer(text))
    for i, m in enumerate(matches):
        start = m.start()
        end = len(text)
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        nxt = re.search(r'^## ', text[m.end():], re.M)
        if nxt and m.end() + nxt.start() < end:
            end = m.end() + nxt.start()
        out[m.group(1).strip()] = text[start:end]
    return out


for delta in sorted((repo / 'openspec/changes' / change / 'specs').glob('*/spec.md')):
    cap = delta.parent.name
    text = delta.read_text()
    mod = re.search(r'^## MODIFIED Requirements\s*$(.*?)(?=^## |\Z)', text, re.M | re.S)
    if not mod:
        print(cap, 'no MODIFIED section'); continue
    modified = blocks(mod.group(1))
    base = repo / 'openspec/specs' / cap / 'spec.md'
    current = base.read_text()
    have = blocks(current)
    for name, raw in modified.items():
        if name not in have:
            sys.exit(f'{cap}: requirement not found: {name}')
        old = have[name]
        new = raw.rstrip('\n') + '\n' + ('\n' if old.endswith('\n\n') else '')
        current = current.replace(old, new, 1)
        print(f'{cap}: replaced "{name}" ({old.count(chr(10))} -> {new.count(chr(10))} lines)')
    base.write_text(current)
