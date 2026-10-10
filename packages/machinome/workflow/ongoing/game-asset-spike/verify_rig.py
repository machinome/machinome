"""Spike helper: prove the GLB rig poses every body exactly as the document does.

For a set of driver values, compose each leaf's world matrix straight from the
document's operation chains (the viewer's rule), then pose the GLB's node
hierarchy from the formulas in its extras and compose the same leaf's world
matrix there. Report the largest difference over all leaves.

usage: verify_rig.py VIEWER_JSON THOR.glb
"""
import json, struct, sys
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__file__))
from thor_glb import make_scope, compose, evaluate, rot, tra, op_is_var, quat

POSES = {
    'home': {}, 'park': dict(art2=80, art3=-135, art5=80, grip=0),
    'place': dict(art1=90, art2=60, art3=-80, art5=-40, art6=90),
    'all': dict(art1=37, art2=-50, art3=120, art4=-77, art5=66, art6=-150, grip=30),
}

doc = json.load(open(sys.argv[1]))
with open(sys.argv[2], 'rb') as f:
    f.read(12)
    n, _ = struct.unpack('<II', f.read(8))
    gltf = json.loads(f.read(n))
nodes = gltf['nodes']
rig = next(nd['extras']['machinome'] for nd in nodes if nd.get('extras', {}).get('machinome', {}).get('joints'))
root_idx = gltf['scenes'][0]['nodes'][0]
parent = {}
for i, nd in enumerate(nodes):
    for c in nd.get('children', []):
        parent[c] = i


def quat_matrix(q):
    x, y, z, w = q
    m = np.eye(4)
    m[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                 [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                 [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return m


def node_local(i, scope):
    nd = nodes[i]
    j = rig['joints'].get(nd['name'])
    if j and j['node'] == i:
        if j['op'] == 'r':
            return quat_matrix(quat(j['axis'], evaluate(j['expressions'][0], scope)))
        return tra([evaluate(e, scope) for e in j['expressions']])
    if 'matrix' in nd:
        return np.array(nd['matrix']).reshape(4, 4).T
    m = np.eye(4)
    if 'translation' in nd:
        m = m @ tra(nd['translation'])
    if 'rotation' in nd:
        m = m @ quat_matrix(nd['rotation'])
    if 'scale' in nd:
        m = m @ np.diag([*nd['scale'], 1])
    return m


def node_world(i, scope, below_root=True):
    chain = []
    while i != root_idx:
        chain.append(i)
        i = parent[i]
    m = np.eye(4)
    for k in reversed(chain):
        m = m @ node_local(k, scope)
    return m   # in document millimetres, Z-up: the root's conversion is left out on purpose


# document side: world matrix of every leaf by path
def doc_leaves(scope):
    out = {}

    def walk(n, acc, path):
        m = acc @ compose(n.get('operations') or [], scope)
        if 'model' in n:
            out[path] = m
        for c in n.get('children') or []:
            walk(c, m, path + '/' + c['name'])
    walk(doc['root'], np.eye(4), doc['root']['name'])
    return out


# rig side: a leaf's world = its body node's world @ the constant placement the generator baked
# into the merged mesh. The generator folded that placement into the vertices, so we compare
# bodies instead: every body's node world against the document world of the body's root node.
body_nodes = {nd['name']: i for i, nd in enumerate(nodes) if 'mesh' in nd}
body_paths = {row['body']: row['path'] for row in json.load(open(sys.argv[3]))['bodies_table']}


def doc_node_world(path, scope):
    parts = path.split('/')
    n = doc['root']
    m = compose(n.get('operations') or [], scope)
    for name in parts[1:]:
        n = next(c for c in n['children'] if c['name'] == name)
        m = m @ compose(n.get('operations') or [], scope)
    return m


for pose, drv in POSES.items():
    drivers = {k: float(v['default']) for k, v in doc['drivers'].items()}
    drivers.update(drv)
    scope = make_scope(doc, drivers)
    worst, worst_body = 0.0, None
    for body, idx in body_nodes.items():
        path = body_paths[body]
        a = node_world(idx, scope)
        b = doc_node_world(path, scope)
        # the generator folds a body's constant ops (its "offset") into the mesh when the node
        # has no variable op, so compare the frames by placing a probe point set
        probe = np.array([[0, 0, 0, 1], [100, 0, 0, 1], [0, 100, 0, 1], [0, 0, 100, 1]], float).T
        d = np.max(np.abs(a @ probe - b @ probe))
        if d > worst:
            worst, worst_body = d, body
    print(f'{pose:<6} bodies {len(body_nodes)}  max probe deviation {worst:.6f} mm  ({worst_body})')
