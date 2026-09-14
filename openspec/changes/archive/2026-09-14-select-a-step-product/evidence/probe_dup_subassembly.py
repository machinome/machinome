"""Probe: two distinct sub-assemblies sharing one name.

`generate_assembly` keys `_ordered_assembly_names`, `occurrences_by_parent`
and `assembly_class_names` by product NAME. This fixture has two distinct
`Stage` sub-assemblies (one holding `Alpha`, one holding `Beta`), nested
three levels deep because `cadquery.Assembly` refuses same-named siblings.
"""
import os, sys
import cadquery as cq
from solid_node.node.adapters import step as step_module
from solid_node.node.adapters.step import StepAssembly
from solid_node.manager.import_step import generate_parts, generate_assembly

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, 'dup_subassembly.step')

root = cq.Assembly(name='Root')
for side, child_name, size in (('Left', 'Alpha', 1), ('Right', 'Beta', 2)):
    holder = cq.Assembly(name=side)
    stage = cq.Assembly(name='Stage')
    stage.add(cq.Workplane('XY').box(size, size, size), name=child_name,
              loc=cq.Location(cq.Vector(size, 0, 0)))
    holder.add(stage, name='Stage', loc=cq.Location(cq.Vector(0, size * 10, 0)))
    root.add(holder, name=side)
root.export(path, exportType='STEP')

step_module._document_cache.clear()
doc = step_module.cached_document(path)
print('-- products')
for entry in doc.order:
    p = doc.products[entry]
    print(f'   entry={p.entry:<10} name={p.display_name:<8} kind={p.kind}')

a = StepAssembly(path)
print('-- occurrences')
for o in a.occurrences:
    print(f'   identity={o.identity:<12} product={o.product_name!r} parent={o.parent_name!r}')

parts_source, class_names = generate_parts(a, path, OUT)
print('-- class_names', class_names)
assembly_source, root_class = generate_assembly(a, 'dup', path, class_names)
print('-- generated assembly.py')
print(assembly_source)
try:
    compile(assembly_source, 'assembly.py', 'exec')
    print('   compiles OK')
except SyntaxError as e:
    print('  ', type(e).__name__ + ':', e.msg, 'line', e.lineno)
