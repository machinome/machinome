import ast
import hashlib
import json
import math
import operator
import numpy as np
from molejo import Shape
import host_acceptance as host

source = host.ROOT / 'simulation/viewer_pose.py'
class_ast = next(n for n in ast.parse(source.read_text()).body
                 if isinstance(n, ast.ClassDef) and n.name == 'Expressions')
namespace = dict(ast=ast, math=math, operator=operator)
exec(compile(ast.Module(body=[class_ast], type_ignores=[]),
             str(source), 'exec'), namespace)
original = namespace['Expressions']
defaults = {k: v['default'] for k, v in host.document['drivers'].items()}
result = {'manifest_sha256': hashlib.sha256(
    (host.EXPORT/'manifest.json').read_bytes()).hexdigest(),
    'project_expression_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'comparison': 'published truncated remainder versus unchanged Python floored modulo',
    'poses': []}
for pose in ('rest', 'Home', 'Center', 'Present', 'restored'):
    values = host.document['instructions'][pose]['targets'] if pose in host.document['instructions'] else defaults
    floor = original(host.document); floor.values.update(values)
    published = host.Expressions(host.document); published.values.update(values)
    rows = []
    for path in host.belts:
        payload = host.nodes[path]['flexible']
        floor_params = {k: floor(v) for k,v in payload['params'].items()}
        pub_params = {k: published(v) for k,v in payload['params'].items()}
        a = np.asarray(Shape.from_dict(payload['spec']).evaluate(**floor_params).vertices, dtype=np.float32)
        b = np.asarray(Shape.from_dict(payload['spec']).evaluate(**pub_params).vertices, dtype=np.float32)
        rows.append({'path': path, 'vertex_difference': float(np.max(np.abs(a-b))),
            'different_parameters': {k:{'published':pub_params[k], 'project_floor':floor_params[k]}
                for k in pub_params if abs(pub_params[k]-floor_params[k]) > 1e-10}})
    result['poses'].append({'pose':pose,'drivers':values,'belts':rows})
(host.SCRATCH/'project-sweep-divergence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
