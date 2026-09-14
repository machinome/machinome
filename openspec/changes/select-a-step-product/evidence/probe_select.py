"""Probe: the ambiguity refusal and the document's own identities.

Run from the fix-warts worktree with PYTHONPATH=$PWD.
"""
import os, sys, tempfile
sys.argv = ['probe']
from tests.step_project import parts as fixture_parts
from tests import test_step_node as T
from solid_node.node.adapters import step as step_module

os.environ.setdefault('SOLID_BUILD_DIR', tempfile.mkdtemp())
T.setUpModule()

path = T.DUPLICATE_NAMES_STEP
print('== fixture:', path)
doc = step_module.cached_document(path)
print('-- document order / entries / names / kinds / candidate')
for entry in doc.order:
    p = doc.products[entry]
    print(f'  entry={entry!r} name={p.display_name!r} kind={p.kind} '
          f'is_free={p.is_free} is_assembly={p.is_assembly} candidate={p.is_candidate} '
          f'occurrences={doc.occurrences(p)}')
print('-- inventory()')
print(doc.inventory())
print('-- find("Pin") ->', [p.entry for p in doc.find('Pin')])

print('\n== refusal through StepNode (parts.AmbiguousPin)')
try:
    fixture_parts.AmbiguousPin().assemble()
except Exception as error:
    print(type(error).__name__ + ':', error)

print('\n== StepAssembly view')
from solid_node.node.adapters.step import StepAssembly
a = StepAssembly(path)
for info in a.products:
    print('  product', repr(info))
for occ in a.occurrences:
    print(f'  occurrence identity={occ.identity!r} label_name={occ.label_name!r} '
          f'product_name={occ.product_name!r} parent={occ.parent_name!r}')
