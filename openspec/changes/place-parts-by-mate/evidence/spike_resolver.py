"""Resolver spike, in the terms of workflow/ongoing/mates-and-sketches.md 5.1/5.2.

A Frame is an origin and a right-handed triad in its declarer's own frame.
`moving.on(fixed, freedom)` resolves to ONE rest placement of the moving
child in the fixed frame's owner:  P_owner o F_fixed o inverse(F_moving),
plus the joint copied literally from the moving frame (axis = z, at = at).
Checked here against what Thor's render() methods write by hand today.
"""
import math

def unit(v):
    n = math.sqrt(sum(c*c for c in v)); return tuple(c/n for c in v)
def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def dot(a, b): return sum(x*y for x, y in zip(a, b))

class Frame:
    """Frame(at, z, x=None): z is the line a revolute turns about."""
    def __init__(self, at=(0, 0, 0), z=(0, 0, 1), x=None):
        self.at = tuple(float(c) for c in at)
        z = unit(z)
        if x is None:   # next principal axis in right-hand order after z
            k = max(range(3), key=lambda i: abs(z[i]))
            if any(abs(z[i]) > 1e-9 for i in range(3) if i != k):
                raise ValueError('diagonal z: name x')
            x = [0.0, 0.0, 0.0]; x[(k + 1) % 3] = 1.0 if z[k] > 0 else -1.0
        x = unit(x); o = dot(x, z); x = unit(tuple(x[i] - o*z[i] for i in range(3)))
        self.x, self.z = x, z; self.y = cross(z, x)
    def matrix(self):
        # columns x y z, then translation
        R = [[self.x[i], self.y[i], self.z[i]] for i in range(3)]
        return R, list(self.at)

def compose(A, B):
    Ra, ta = A; Rb, tb = B
    R = [[sum(Ra[i][k]*Rb[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    t = [sum(Ra[i][k]*tb[k] for k in range(3)) + ta[i] for i in range(3)]
    return R, t
def invert(M):
    R, t = M; Ri = [[R[j][i] for j in range(3)] for i in range(3)]
    return Ri, [-sum(Ri[i][k]*t[k] for k in range(3)) for i in range(3)]
def rotation(angle, axis):
    x, y, z = unit(axis); c = math.cos(math.radians(angle)); s = math.sin(math.radians(angle)); d = 1-c
    return [[x*x*d+c, x*y*d-z*s, x*z*d+y*s],[y*x*d+z*s, y*y*d+c, y*z*d-x*s],[z*x*d-y*s, z*y*d+x*s, z*z*d+c]], [0.0,0.0,0.0]
def as_render(M):
    """The (angle, axis, translate) a render() would write: rotate then translate."""
    R, t = M; tr = R[0][0]+R[1][1]+R[2][2]; ang = math.degrees(math.acos(max(-1, min(1, (tr-1)/2))))
    if ang < 1e-9: return 0.0, (0,0,1), tuple(t)
    if abs(ang-180) < 1e-6:
        k = max(range(3), key=lambda i: R[i][i]); a=[0,0,0]; a[k]=math.sqrt((R[k][k]+1)/2)
        for j in range(3):
            if j!=k: a[j]=(R[k][j]+R[j][k])/(4*a[k])
        return 180.0, tuple(a), tuple(t)
    s = 2*math.sin(math.radians(ang))
    return ang, ((R[2][1]-R[1][2])/s, (R[0][2]-R[2][0])/s, (R[1][0]-R[0][1])/s), tuple(t)

def on(moving, fixed, owner_placement=None):
    """The resolver: rest placement of the moving child in the assembly's frame."""
    P = owner_placement or ([[1,0,0],[0,1,0],[0,0,1]], [0,0,0])
    return compose(compose(P, fixed.matrix()), invert(moving.matrix()))

def same(M, angle, axis, t, tol=1e-6):
    R = rotation(angle, axis)[0]
    return all(abs(M[0][i][j]-R[i][j]) < tol for i in range(3) for j in range(3)) and all(abs(M[1][i]-t[i]) < tol for i in range(3))

# ---- the elbow: Art2 (upper arm) carries Art3 (forearm root) ----------------
ELBOW_ALONG_ARM, ELBOW_ACROSS_ARM, ELBOW_ACROSS_FOREARM = 160.0, 68.0, 81.5
art2_elbow = Frame(at=(0, ELBOW_ALONG_ARM, ELBOW_ACROSS_ARM), z=(0, 0, 1))          # on Art2, its own frame
art3_hinge = Frame(at=(0, 0, ELBOW_ACROSS_FOREARM), z=(0, 1, 0), x=(1, 0, 0))     # on Art3, its own frame
M = on(art3_hinge, art2_elbow)
print('elbow  resolver ->', as_render(M))
print('elbow  Art2.render today: rotate(90, X); translate(0, %.1f, %.1f)' % (ELBOW_ALONG_ARM + ELBOW_ACROSS_FOREARM, ELBOW_ACROSS_ARM))
assert same(M, 90.0, (1,0,0), (0, ELBOW_ALONG_ARM + ELBOW_ACROSS_FOREARM, ELBOW_ACROSS_ARM))
print('elbow  joint copied from the moving frame: Revolute(axis=%s, at=%s)  == Art3.elbow today' % (art3_hinge.z, art3_hinge.at))
assert art3_hinge.z == (0,1,0) and art3_hinge.at == (0,0,81.5)
# with x left to its default the SAME two lines meet, but the rest attitude differs:
Md = on(Frame(at=(0, 0, ELBOW_ACROSS_FOREARM), z=(0, 1, 0)), art2_elbow)
print('elbow  with default x ->', as_render(Md), ' (a different zero of the coordinate)')

# ---- the shoulder: Art1 (housing) carries Art2 (upper arm) -----------------
art1_shoulder = Frame(at=(0, 0, 123.0), z=(0, 1, 0))                        # on Art1
art2_shoulder = Frame(at=(0, 0, 68.0), z=(0, 0, 1), x=(0, 1, 0))            # on Art2
M2 = on(art2_shoulder, art1_shoulder)
print('shoulder resolver ->', as_render(M2))
print('shoulder Art1.render today: rotate(180, (0, .7071, .7071)); translate(0, -68, 123)')
assert same(M2, 180.0, (0, math.sqrt(.5), math.sqrt(.5)), (0, -68.0, 123.0))
print('OK: both hand-written placements are what the two frame pairs resolve to')
