"""Probe: how the OCCT entry and a name-relative index move when the
document is re-exported with an unrelated product added.

Writes three variants of the duplicate-name fixture into a scratch dir
and prints, for each, every product's entry, name, volume, and its
1-based index among products sharing its name.
"""
import os, sys, tempfile
import cadquery as cq
from solid_node.node.adapters import step as step_module

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def base(path, extra=False, extra_first=False):
    root = cq.Assembly(name='Root')
    sub1 = cq.Assembly(name='Sub1')
    sub1.add(cq.Workplane('XY').box(1, 1, 1), name='Pin')
    sub2 = cq.Assembly(name='Sub2')
    sub2.add(cq.Workplane('XY').box(2, 2, 2), name='Pin')
    if extra and extra_first:
        root.add(cq.Workplane('XY').box(7, 7, 7), name='Bracket')
    root.add(sub1, name='Sub1')
    root.add(sub2, name='Sub2')
    if extra and not extra_first:
        root.add(cq.Workplane('XY').box(7, 7, 7), name='Bracket')
    root.export(path, exportType='STEP')


def report(label, path):
    step_module._document_cache.clear()
    doc = step_module.cached_document(path)
    print(f'-- {label}')
    counts = {}
    for entry in doc.order:
        p = doc.products[entry]
        counts[p.name] = counts.get(p.name, 0) + 1
        shape = doc.shape(p)
        print(f'   entry={p.entry:<10} name={p.display_name:<10} '
              f'index-among-same-name={counts[p.name]} '
              f'volume={shape.Volume():.3f}')


variants = [
    ('original', dict()),
    ('extra product appended last', dict(extra=True)),
    ('extra product inserted first', dict(extra=True, extra_first=True)),
]
for label, kwargs in variants:
    path = os.path.join(OUT, label.replace(' ', '_') + '.step')
    base(path, **kwargs)
    report(label, path)

# Determinism: read the original twice, and re-export it byte-for-byte.
path = os.path.join(OUT, 'original.step')
report('original, read again (same process, cold cache)', path)
