"""Spike question 1: the facts of a clocked export, read from its files.

    <venv>/bin/python export_facts.py <export directory> <out.json>

Reads `manifest.json` and the directory; writes what the note reports: the
document's version, whether it carries `states`, `instructions` and a
`clocked` object with an identity, whether `source-revision.txt` is there,
the drivers, the instruction, the assembly paths under the input selectors
and the result register (the names a take's layers and highlights would
use), the number of meshes the tree references and the files on disk.
"""

import json
import os
import sys


def walk(node, path, out):
    out.append((path, node))
    for child in node.get('children', []):
        walk(child, path + [child['name']], out)


def main(export, out):
    with open(os.path.join(export, 'manifest.json')) as f:
        manifest = json.load(f)
    nodes = []
    walk(manifest['root'], [], nodes)
    models = [n.get('model') for _, n in nodes if n.get('model')]
    files, size = [], 0
    for directory, _, names in os.walk(export):
        for name in names:
            full = os.path.join(directory, name)
            files.append(os.path.relpath(full, export))
            size += os.path.getsize(full)
    clocked = manifest.get('clocked') or {}

    def under(prefix):
        return ['/'.join(p) for p, n in nodes if p[:len(prefix)] == prefix and len(p) > len(prefix)]

    facts = {
        'format': manifest.get('format'),
        'version': manifest.get('version'),
        'top_level_keys': list(manifest),
        'has_states': 'states' in manifest,
        'states': sorted(manifest.get('states', {})),
        'has_instructions': 'instructions' in manifest,
        'instructions': manifest.get('instructions'),
        'has_clocked': 'clocked' in manifest,
        'clocked_keys': sorted(clocked),
        'identity': clocked.get('identity'),
        'animation': manifest.get('animation'),
        'drivers': {k: {f: v.get(f) for f in ('default', 'range', 'unit', 'dtype', 'scale')}
                    for k, v in manifest.get('drivers', {}).items()},
        'source_revision_txt': os.path.exists(os.path.join(export, 'source-revision.txt')),
        'tree_nodes': len(nodes),
        'mesh_references': len(models),
        'distinct_meshes': len(set(map(str, models))),
        'files': len(files),
        'stl_files': sum(f.endswith('.stl') for f in files),
        'bytes_on_disk': size,
        'manifest_bytes': os.path.getsize(os.path.join(export, 'manifest.json')),
        'input_selector_paths': under(['input_selectors', 'selectors']),
        'result_register_paths': [p for p in under(['carriage', 'registers'])
                                  if 'result_register' in p],
        'crank_paths': under(['main_drive', 'crank']),
    }
    with open(out, 'w') as f:
        json.dump(facts, f, indent=1)
        f.write('\n')
    for key in ('version', 'has_states', 'has_instructions', 'has_clocked', 'identity',
                'source_revision_txt', 'tree_nodes', 'mesh_references', 'distinct_meshes',
                'files', 'stl_files', 'bytes_on_disk', 'manifest_bytes'):
        print(f'{key}: {facts[key]}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
