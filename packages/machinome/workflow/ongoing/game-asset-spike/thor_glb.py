"""Spike: a machinome document as a game asset.

Reads a built document (viewer.json), partitions the tree into co-moving
bodies, merges each body's STLs into one mesh per colour, decimates to a
triangle budget, and writes a GLB whose node hierarchy is the rig: every
variable placement becomes pivot -> joint -> offset nodes with the joint
node carrying the moving rotation or translation. Each declared instruction
becomes an animation clip from the drivers' defaults. The root node's extras
carry the drivers, the bindings and every joint's formula, so a page or an
engine can pose the rig without machinome.

Throwaway spike code. Changes nothing in any repository.

usage: thor_glb.py VIEWER_JSON OUT.glb [--budget N] [--measure OUT.json]
"""
import argparse, json, math, os, re, struct, sys, time
import numpy as np
import trimesh

NUM =re.compile(r'^\s*[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?\s*$')


# ----------------------------------------------------------------- expressions
def deg(f):
    return lambda x: f(math.radians(x))


FUNCS = dict(
    sin=deg(math.sin), cos=deg(math.cos), tan=deg(math.tan),
    asin=lambda x: math.degrees(math.asin(max(-1.0, min(1.0, x)))),
    acos=lambda x: math.degrees(math.acos(max(-1.0, min(1.0, x)))),
    atan=lambda x: math.degrees(math.atan(x)),
    atan2=lambda y, x: math.degrees(math.atan2(y, x)),
    abs=abs, floor=math.floor, ceil=math.ceil, sqrt=math.sqrt, min=min, max=max,
    pow=pow, exp=math.exp, ln=math.log, log=math.log10, round=round,
    sign=lambda x: (x > 0) - (x < 0), mod=lambda a, b: a % b, norm=lambda v: math.sqrt(sum(x * x for x in v)),
)
_compiled = {}


def is_const(e):
    if isinstance(e, (int, float)):
        return True
    if isinstance(e, str):
        return bool(NUM.match(e))
    if isinstance(e, list):
        return all(is_const(x) for x in e)
    return False


def evaluate(expr, scope):
    if isinstance(expr, (int, float)):
        return float(expr)
    if NUM.match(expr):
        return float(expr)
    code = _compiled.get(expr)
    if code is None:
        code = _compiled[expr] = compile(expr.replace('$t', '_t'), '<expr>', 'eval')
    return float(eval(code, {'__builtins__': {}, **FUNCS}, scope))


def make_scope(doc, drivers, t=0.0):
    scope = dict(drivers)
    scope['_t'] = t
    for b in doc.get('bindings') or []:
        scope[b['name']] = evaluate(b['expression'], scope)
    return scope


# ---------------------------------------------------------------- matrices
def rot(axis, angle_deg):
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    s, c = math.sin(math.radians(angle_deg)), math.cos(math.radians(angle_deg))
    x, y, z = a
    C = 1 - c
    m = np.eye(4)
    m[:3, :3] = [[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                 [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                 [z * x * C - y * s, z * y * C + x * s, c + z * z * C]]
    return m


def tra(v):
    m = np.eye(4)
    m[:3, 3] = v
    return m


def op_matrix(op, scope):
    if op[0] == 'r':
        return rot(op[2], evaluate(op[1], scope))
    return tra([evaluate(e, scope) for e in op[1]])


def compose(ops, scope):
    """Ops apply in order: matrix = M_opN ... M_op1 (the viewer's rule)."""
    m = np.eye(4)
    for op in ops:
        m = op_matrix(op, scope) @ m
    return m


def quat(axis, angle_deg):
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    h = math.radians(angle_deg) / 2
    return [float(a[0] * math.sin(h)), float(a[1] * math.sin(h)), float(a[2] * math.sin(h)), float(math.cos(h))]


def op_is_var(op):
    return (op[0] == 'r' and not is_const(op[1])) or (op[0] == 't' and not is_const(op[1]))


# ------------------------------------------------------------ classification
def classify(exprs, doc, drivers):
    """Which drivers an expression list reads, and whether it is affine in them."""
    rng = np.random.default_rng(7)
    names = list(drivers)
    ranges = {k: (v.get('range') or [v['default'] - 1, v['default'] + 1]) for k, v in doc['drivers'].items()}

    def sample():
        return {k: float(rng.uniform(*ranges[k])) for k in names}

    def f(q):
        s = make_scope(doc, q)
        return np.array([evaluate(e, s) for e in exprs])

    base = sample()
    fb = f(base)
    deps = []
    for k in names:
        changed = False
        for _ in range(3):
            q = dict(base)
            q[k] = float(rng.uniform(*ranges[k]))
            if np.max(np.abs(f(q) - fb)) > 1e-9:
                changed = True
                break
        if changed:
            deps.append(k)
    if not deps:
        return dict(cls='constant', reads=[])
    if len(exprs) == 1 and exprs[0].strip() in names:
        return dict(cls='joint', reads=deps)
    # least squares fit f = c + sum k_d q_d over 16 samples
    qs = [sample() for _ in range(16)]
    A = np.array([[1.0] + [q[k] for k in deps] for q in qs])
    F = np.array([f(q) for q in qs])
    coef, *_ = np.linalg.lstsq(A, F, rcond=None)
    resid = np.max(np.abs(A @ coef - F))
    scale = max(1.0, np.max(np.abs(F)))
    if resid < 1e-6 * scale:
        affine = {'const': coef[0].tolist(), **{d: coef[i + 1].tolist() for i, d in enumerate(deps)}}
        return dict(cls='affine', reads=deps, affine=affine)
    return dict(cls='formula', reads=deps)


# ------------------------------------------------------------------ GLB
class Glb:
    FLOAT, UINT = 5126, 5125

    def __init__(self):
        self.buf = bytearray()
        self.views, self.accessors = [], []

    def accessor(self, arr, ctype, atype, target=None, minmax=False):
        arr = np.ascontiguousarray(arr)
        data = arr.tobytes()
        while len(self.buf) % 4:
            self.buf += b'\0'
        view = dict(buffer=0, byteOffset=len(self.buf), byteLength=len(data))
        if target:
            view['target'] = target
        self.buf += data
        self.views.append(view)
        acc = dict(bufferView=len(self.views) - 1, componentType=ctype, count=int(arr.shape[0]), type=atype)
        if minmax:
            acc['min'] = np.atleast_1d(arr.min(axis=0)).tolist()
            acc['max'] = np.atleast_1d(arr.max(axis=0)).tolist()
        self.accessors.append(acc)
        return len(self.accessors) - 1

    def write(self, gltf, path):
        gltf['buffers'] = [dict(byteLength=len(self.buf))]
        gltf['bufferViews'] = self.views
        gltf['accessors'] = self.accessors
        js = json.dumps(gltf, separators=(',', ':')).encode()
        while len(js) % 4:
            js += b' '
        bin_ = bytes(self.buf)
        while len(bin_) % 4:
            bin_ += b'\0'
        total = 12 + 8 + len(js) + 8 + len(bin_)
        with open(path, 'wb') as f:
            f.write(struct.pack('<4sII', b'glTF', 2, total))
            f.write(struct.pack('<II', len(js), 0x4E4F534A))
            f.write(js)
            f.write(struct.pack('<II', len(bin_), 0x004E4942))
            f.write(bin_)


# ------------------------------------------------------------------ build
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('document')
    ap.add_argument('out')
    ap.add_argument('--budget', type=int, default=100_000, help='triangle budget for the whole asset; 0 = no decimation')
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--measure', default=None)
    ap.add_argument('--models', default=None, help='directory of substitute meshes at the same relative paths (coarser tessellation)')
    args = ap.parse_args()

    t0 = time.time()
    doc = json.load(open(args.document))
    base = os.path.dirname(args.document)
    drivers = {k: float(v['default']) for k, v in doc['drivers'].items()}
    rest = make_scope(doc, drivers)

    nodes, meshes, materials, mat_index = [], [], [], {}
    joints = {}          # gltf node index -> {name, path, op, axis, exprs, class}
    bodies = []          # per body measurements
    names_used = {}
    flexible, skipped = [], []
    mesh_cache = {}

    def unique(name):
        n = names_used.get(name, 0)
        names_used[name] = n + 1
        return name if n == 0 else f'{name}#{n}'

    def material(color):
        if color not in mat_index:
            h = (color or '#9aa0a6').lstrip('#')
            rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
            materials.append(dict(name=color or 'default', pbrMetallicRoughness=dict(
                baseColorFactor=[*(c ** 2.2 for c in rgb), 1.0], metallicFactor=0.0, roughnessFactor=0.75)))
            mat_index[color] = len(materials) - 1
        return mat_index[color]

    def add_node(name, parent, **kw):
        nodes.append(dict(name=name, **kw))
        idx = len(nodes) - 1
        if parent is not None:
            nodes[parent].setdefault('children', []).append(idx)
        return idx

    def load_mesh(rel):
        if rel not in mesh_cache:
            path = os.path.join(base, rel)
            if args.models and os.path.exists(os.path.join(args.models, rel)):
                path = os.path.join(args.models, rel)
            mesh_cache[rel] = trimesh.load(path, force='mesh')
        return mesh_cache[rel]

    class Body:
        def __init__(self, name, frame, path):
            self.name, self.frame, self.path = name, frame, path
            self.parts = {}   # color -> list of (vertices, faces)
            self.pieces = 0

        def add(self, docnode, matrix):
            m = load_mesh(docnode['model'])
            v = trimesh.transform_points(m.vertices, matrix)
            self.parts.setdefault(docnode.get('color'), []).append((v, m.faces.copy()))
            self.pieces += 1

    def walk(n, parent, acc, body, path, color):
        """n: document node; parent: gltf node its content hangs from; acc: constant
        matrix from n's local frame to parent's frame; body: current Body or None."""
        color = n.get('color') or color
        n = dict(n, color=color)
        ops = n.get('operations') or []
        var_idx = [i for i, op in enumerate(ops) if op_is_var(op)]
        if not var_idx:
            acc = acc @ compose(ops, rest)
            if body is None:
                body = Body(unique(n['name']), parent, path)
                bodies.append(body)
            if 'model' in n:
                body.add(n, acc)
            elif 'flexible' in n:
                flexible.append(path)
            for c in n.get('children') or []:
                walk(c, parent, acc, body, path + '/' + c['name'], color)
            return
        # one or more variable ops: build the chain from the outermost (last applied)
        frame, frame_acc = parent, acc
        last = len(ops)
        for i in reversed(var_idx):
            post = ops[i + 1:last]
            m_post = frame_acc @ compose(post, rest)
            if not np.allclose(m_post, np.eye(4)):
                frame = add_node(n['name'] + '.pivot', frame, matrix=m_post.T.flatten().tolist())
            op = ops[i]
            jname = unique(n['name'])
            if op[0] == 'r':
                frame = add_node(jname, frame, rotation=quat(op[2], evaluate(op[1], rest)))
                exprs = [op[1]]
            else:
                frame = add_node(jname, frame, translation=[evaluate(e, rest) for e in op[1]])
                exprs = list(op[1])
            info = dict(name=jname, path=path, op=op[0], axis=op[2] if op[0] == 'r' else None, expressions=exprs)
            info.update(classify(exprs, doc, drivers))
            joints[frame] = info
            nodes[frame]['extras'] = dict(machinome=info)
            frame_acc = np.eye(4)
            last = i
        pre = ops[:last]
        m_pre = compose(pre, rest)
        if not np.allclose(m_pre, np.eye(4)):
            frame = add_node(n['name'] + '.offset', frame, matrix=m_pre.T.flatten().tolist())
        body = Body(unique(n['name'] + '.body'), frame, path)
        bodies.append(body)
        if 'model' in n:
            body.add(n, np.eye(4))
        elif 'flexible' in n:
            flexible.append(path)
        for c in n.get('children') or []:
            walk(c, frame, np.eye(4), body, path + '/' + c['name'], color)

    # Z-up millimetres -> Y-up metres at the root
    root = add_node(doc['root']['name'], None, rotation=quat([1, 0, 0], -90), scale=[0.001, 0.001, 0.001])
    walk(doc['root'], root, np.eye(4), None, doc['root']['name'], None)

    # merge, decimate, emit meshes
    glb = Glb()
    total_before = sum(sum(len(f) for _, f in parts) for b in bodies for parts in b.parts.values())
    ratio = (args.budget / total_before) if args.budget and total_before > args.budget else 1.0
    total_after = 0
    body_rows = []
    for b in bodies:
        if not b.parts:
            continue
        prims, before, after = [], 0, 0
        for color, parts in b.parts.items():
            vs, fs, off = [], [], 0
            for v, f in parts:
                vs.append(v)
                fs.append(f + off)
                off += len(v)
            v = np.vstack(vs)
            f = np.vstack(fs)
            before += len(f)
            if ratio < 1.0 and len(f) > 64:
                import fast_simplification
                target = max(64, int(len(f) * ratio))
                v, f = fast_simplification.simplify(v.astype(np.float64), f.astype(np.int64), target_reduction=1 - target / len(f))
            tm = trimesh.Trimesh(v, f, process=True)
            v, f = tm.vertices, tm.faces
            after += len(f)
            pos = glb.accessor(v.astype(np.float32), Glb.FLOAT, 'VEC3', 34962, minmax=True)
            nrm = glb.accessor(tm.vertex_normals.astype(np.float32), Glb.FLOAT, 'VEC3', 34962)
            idx = glb.accessor(f.astype(np.uint32).reshape(-1), Glb.UINT, 'SCALAR', 34963)
            prims.append(dict(attributes=dict(POSITION=pos, NORMAL=nrm), indices=idx, material=material(color)))
        meshes.append(dict(name=b.name, primitives=prims))
        add_node(b.name, b.frame, mesh=len(meshes) - 1)
        total_after += after
        body_rows.append(dict(body=b.name, path=b.path, pieces=b.pieces, colours=len(b.parts), triangles_before=before, triangles_after=after))

    # animation clips: one per instruction, from the drivers' defaults to its targets
    animations = []
    for iname, inst in (doc.get('instructions') or {}).items():
        targets = inst.get('targets') or {}
        if not targets:
            continue
        duration = float(inst.get('duration') or 1.0)
        n = max(2, int(round(duration * args.fps)) + 1)
        times = np.linspace(0.0, duration, n, dtype=np.float32)
        samples = {j: [] for j in joints}
        for t in times:
            q = {k: v + (float(targets.get(k, v)) - v) * (t / duration) for k, v in drivers.items()}
            s = make_scope(doc, q)
            for j, info in joints.items():
                if info['op'] == 'r':
                    samples[j].append(quat(info['axis'], evaluate(info['expressions'][0], s)))
                else:
                    samples[j].append([evaluate(e, s) for e in info['expressions']])
        tacc = glb.accessor(times, Glb.FLOAT, 'SCALAR', minmax=True)
        samplers, channels = [], []
        for j, info in joints.items():
            arr = np.array(samples[j], dtype=np.float32)
            if np.allclose(arr, arr[0]):
                continue
            out = glb.accessor(arr, Glb.FLOAT, 'VEC4' if info['op'] == 'r' else 'VEC3')
            samplers.append(dict(input=tacc, output=out, interpolation='LINEAR'))
            channels.append(dict(sampler=len(samplers) - 1, target=dict(node=j, path='rotation' if info['op'] == 'r' else 'translation')))
        if channels:
            animations.append(dict(name=iname, samplers=samplers, channels=channels))

    classes = {}
    for info in joints.values():
        classes[info['cls']] = classes.get(info['cls'], 0) + 1
    rig = dict(
        document=os.path.realpath(args.document).split('machinome-projects/')[-1],
        meshes='re-tessellated from the B-rep files beside the document' if args.models else 'the document\'s own STLs',
        format=doc.get('format'), version=doc.get('version'), units='millimetres in the document; the root node scales to metres and turns Z-up to Y-up',
        drivers={k: dict(default=v['default'], range=v.get('range'), unit=v.get('unit')) for k, v in doc['drivers'].items()},
        bindings=doc.get('bindings') or [],
        joints={nodes[j]['name']: dict(node=j, **info) for j, info in joints.items()},
        instructions={k: dict(targets=v.get('targets'), duration=v.get('duration')) for k, v in (doc.get('instructions') or {}).items()},
        functions='sin cos tan asin acos atan atan2 in degrees; ln log mod sign; else as JavaScript Math',
    )
    nodes[root]['extras'] = dict(machinome=rig)
    gltf = dict(asset=dict(version='2.0', generator='machinome game-asset spike 2026-10-04',
                           copyright='Thor by AngelLM, CC-BY-SA-4.0; simulation additions per the project NOTICE'),
                scene=0, scenes=[dict(nodes=[root])], nodes=nodes, meshes=meshes, materials=materials)
    if animations:
        gltf['animations'] = animations
    glb.write(gltf, args.out)

    def stl_triangles(path):
        with open(path, 'rb') as fh:
            fh.read(80)
            n = struct.unpack('<I', fh.read(4))[0]
        return n if os.path.getsize(path) == 84 + 50 * n else len(trimesh.load(path, force='mesh').faces)

    fine_placed = 0

    def count_fine(n):
        nonlocal fine_placed
        if 'model' in n:
            fine_placed += stl_triangles(os.path.join(base, n['model']))
        for c in n.get('children') or []:
            count_fine(c)
    count_fine(doc['root'])

    measure = dict(
        document=rig['document'], budget=args.budget, seconds=round(time.time() - t0, 1),
        meshes=rig['meshes'], triangles_fine_placed=fine_placed,
        pieces=sum(b.pieces for b in bodies), bodies=len(body_rows), gltf_nodes=len(nodes), joints=len(joints),
        joint_classes=classes, triangles_before=total_before, triangles_after=total_after,
        materials=len(materials), clips=[a['name'] for a in animations], flexible_dropped=flexible,
        glb_bytes=os.path.getsize(args.out), bodies_table=body_rows,
        joints_table=[dict(name=nodes[j]['name'], cls=i['cls'], reads=i['reads'], op=i['op'], expressions=i['expressions']) for j, i in joints.items()],
    )
    if args.measure:
        json.dump(measure, open(args.measure, 'w'), indent=1)
    print(json.dumps({k: v for k, v in measure.items() if k not in ('bodies_table', 'joints_table')}, indent=1))


if __name__ == '__main__':
    main()
