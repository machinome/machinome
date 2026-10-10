"""Apply the clock 02 string decoupling: exact-match replacements, asserted
before anything is written. Usage: restructure.py <src project root> <dst root>
(dst may equal src)."""
import os, sys

src, dst = sys.argv[1:3]
edits = {}

# --- spec.py: the movement no longer carries the cord; a StringGeometry does
spec = open(os.path.join(src, 'simulation/wall_clock_02/spec.py')).read()
r1_old = "        self.string_route = STRING_ROUTE\n"
assert spec.count(r1_old) == 1
r2_old = '''    @property
    def string_hole_z(self):
        \'\'\'Centre height of the source hole through the bottom pillar.\'\'\'
        top = (self.plates.bearing_positions[0][2]
               + self.train.get_arbor(-self.train.powered_wheels)
               .get_total_thickness())
        return top + self.power.get_chain_positions_from_top()[0][0][1]

    @property
    def string_guide_y(self):
        return self.plates.bottom_pillar_positions[0][1]

    @property
    def string_spool_radius(self):
        # The source chain position lies on the spool surface. Molejo sweeps
        # around a centreline, so lift that centreline by the cord radius.
        return (abs(self.weight_axis[0])
                + self.string_route.radius_clearance)

    @property
    def string_spool_z(self):
        \'\'\'Depth of the chain track on the great-wheel spool.\'\'\'
        return self.weight_axis[1] + self.string_route.front_clearance

    @property
    def string_spool_start_point(self):
        angle = math.radians(self.string_route.payout_angle)
        return (self.string_spool_radius * math.cos(angle),
                self.string_spool_radius * math.sin(angle),
                self.string_spool_z)

    @property
    def string_guide_point(self):
        source = (self.weight_axis[0], self.string_guide_y,
                  self.string_hole_z)
        return tuple(value + trim for value, trim
                     in zip(source, self.string_route.guide_trim))

    def string_weight_point(self, drop):
        return (self.weight_axis[0], self.wound_position - drop,
                self.weight_axis[1])


@lru_cache(maxsize=4)
'''
assert spec.count(r2_old) == 1
r2_new = '''class StringGeometry:
    \'\'\'
    Where the cord runs, in the plates' coordinates: the spool it is wound
    on, the hole through the bottom pillar it passes through, and the hook
    it ends at.

    Built from the movement and the route rather than kept on the
    movement, so that the rigid parts, which are all cut from the
    movement, do not depend on the route: tuning `STRING_ROUTE`
    regenerates the cord and nothing else. The string nodes in `clock.py`
    read it through their `string_geometry`.
    \'\'\'

    def __init__(self, movement, route):
        self.movement = movement
        self.string_route = route
        self.weight_drop = movement.weight_drop

    @property
    def string_hole_z(self):
        \'\'\'Centre height of the source hole through the bottom pillar.\'\'\'
        movement = self.movement
        top = (movement.plates.bearing_positions[0][2]
               + movement.train.get_arbor(-movement.train.powered_wheels)
               .get_total_thickness())
        return top + movement.power.get_chain_positions_from_top()[0][0][1]

    @property
    def string_guide_y(self):
        return self.movement.plates.bottom_pillar_positions[0][1]

    @property
    def string_spool_radius(self):
        # The source chain position lies on the spool surface. Molejo sweeps
        # around a centreline, so lift that centreline by the cord radius.
        return (abs(self.movement.weight_axis[0])
                + self.string_route.radius_clearance)

    @property
    def string_spool_z(self):
        \'\'\'Depth of the chain track on the great-wheel spool.\'\'\'
        return self.movement.weight_axis[1] + self.string_route.front_clearance

    @property
    def string_spool_start_point(self):
        angle = math.radians(self.string_route.payout_angle)
        return (self.string_spool_radius * math.cos(angle),
                self.string_spool_radius * math.sin(angle),
                self.string_spool_z)

    @property
    def string_guide_point(self):
        source = (self.movement.weight_axis[0], self.string_guide_y,
                  self.string_hole_z)
        return tuple(value + trim for value, trim
                     in zip(source, self.string_route.guide_trim))

    def string_weight_point(self, drop):
        return (self.movement.weight_axis[0],
                self.movement.wound_position - drop,
                self.movement.weight_axis[1])


def string_geometry(movement):
    \'\'\'The cord's geometry on `movement`, routed by `STRING_ROUTE`.\'\'\'
    return StringGeometry(movement, STRING_ROUTE)


@lru_cache(maxsize=4)
'''
edits['simulation/wall_clock_02/spec.py'] = spec.replace(r1_old, '').replace(r2_old, r2_new)

# --- shared/motion.py: the wound string nodes read a string_geometry hook
motion = open(os.path.join(src, 'simulation/shared/motion.py')).read()
m1_old = '''    def render(self):
        route = self.built.string_route
        return Shape(
            profile=Circle(radius=route.diameter / 2),
            path=[
                Helix(radius=self.built.string_spool_radius,
                      turns=P.wraps, height=P.coil_height),
                Line(to=(P.guide_x, P.guide_y, P.guide_z)),
'''
assert motion.count(m1_old) == 1
m1_new = '''    @property
    def string_geometry(self):
        \'\'\'What the cord is routed from: the movement, unless the clock
        keeps its cord's geometry apart from it (see the assembly).\'\'\'
        return self.built

    def render(self):
        geometry = self.string_geometry
        route = geometry.string_route
        return Shape(
            profile=Circle(radius=route.diameter / 2),
            path=[
                Helix(radius=geometry.string_spool_radius,
                      turns=P.wraps, height=P.coil_height),
                Line(to=(P.guide_x, P.guide_y, P.guide_z)),
'''
motion = motion.replace(m1_old, m1_new)
m2_old = '''    The concrete clock supplies only physical geometry on ``built``:
    ``string_spool_radius``, ``string_spool_start_point``,
    ``string_guide_point``, ``string_weight_point(drop)``, ``string_route``
    and ``weight_drop``.  Its concrete subclass wires a ``cord`` leaf to
    these ports. Fine routing and payout behaviour therefore live here once.
    \'\'\'

    @staticmethod
    def _distance(start, end):
        return sqrt(sum((right - left) ** 2
                        for left, right in zip(start, end)))
'''
assert motion.count(m2_old) == 1
m2_new = '''    The concrete clock supplies only physical geometry on
    ``string_geometry``: ``string_spool_radius``,
    ``string_spool_start_point``, ``string_guide_point``,
    ``string_weight_point(drop)``, ``string_route`` and ``weight_drop``.
    That is ``built``, the movement, unless the clock keeps its cord's
    geometry apart from the movement so that tuning the cord does not
    rebuild the parts cut from it, as wall clock 02 does. Its concrete
    subclass wires a ``cord`` leaf to these ports. Fine routing and payout
    behaviour therefore live here once.
    \'\'\'

    @staticmethod
    def _distance(start, end):
        return sqrt(sum((right - left) ** 2
                        for left, right in zip(start, end)))

    @property
    def string_geometry(self):
        \'\'\'What the cord is routed from; the movement unless overridden.\'\'\'
        return self.built
'''
motion = motion.replace(m2_old, m2_new)
head, rest = motion.split('class WoundWeightStringAssembly(WoundStringDrive):', 1)
body, tail = rest.split('class PulleyWeightString(MolejoNode):', 1)
assert body.count('self.built') == 10, body.count('self.built')   # 9 readers + the hook's own return
body = body.replace('return self.built\n', 'RETURN_HOOK\n', 1)
body = body.replace('self.built', 'self.string_geometry').replace('RETURN_HOOK\n', 'return self.built\n')
assert body.count('self.built') == 1
motion = head + 'class WoundWeightStringAssembly(WoundStringDrive):' + body + 'class PulleyWeightString(MolejoNode):' + tail
edits['simulation/shared/motion.py'] = motion

# --- clock.py: the string nodes take their geometry from spec.string_geometry
clock = open(os.path.join(src, 'simulation/wall_clock_02/clock.py')).read()
c1_old = "from . import colours\n"
assert clock.count(c1_old) == 1
c2_old = '''class WeightString(shared.WoundWeightString, Design):
    pass
'''
assert clock.count(c2_old) == 1
c2_new = '''class WeightString(shared.WoundWeightString, Design):
    @property
    def string_geometry(self):
        return spec.string_geometry(self.built)
'''
c3_old = '''        weight_z=shared.WoundStringDrive.weight_z,
        **DESIGN,
    )
'''
assert clock.count(c3_old) == 1
c3_new = c3_old + '''
    @property
    def string_geometry(self):
        \'\'\'The cord's geometry, kept apart from the movement in `spec` so
        that tuning the cord does not rebuild the parts cut from it.\'\'\'
        return spec.string_geometry(self.built)
'''
edits['simulation/wall_clock_02/clock.py'] = (clock.replace(c1_old, "from . import colours, spec\n")
                                              .replace(c2_old, c2_new).replace(c3_old, c3_new))

# --- test_clock.py: the string test reads the cord's geometry through the hook
test = open(os.path.join(src, 'simulation/wall_clock_02/test_clock.py')).read()
t_old = '''        string = self.node.movement.string
        self.assertIsInstance(string.cord, MolejoNode)
        self.assertEqual(string.cord.color, '#8000ff')
        self.assertIs(self.built.string_route, STRING_ROUTE)
        self.assertEqual(string.guide_point[0], self.built.weight_axis[0])
        self.assertEqual(string.guide_point[2], self.built.string_hole_z)
        self.assertGreater(self.built.string_spool_z,
                           self.built.string_hole_z)
        self.assertGreater(self.built.string_spool_z,
                           self.built.weight_axis[1])
        self.assertGreater(self.built.string_spool_radius,
                           abs(self.built.weight_axis[0]))
'''
assert test.count(t_old) == 1
t_new = '''        string = self.node.movement.string
        geometry = string.string_geometry
        self.assertIsInstance(string.cord, MolejoNode)
        self.assertEqual(string.cord.color, '#8000ff')
        self.assertIs(geometry.string_route, STRING_ROUTE)
        self.assertIs(string.cord.string_geometry.string_route, STRING_ROUTE)
        self.assertFalse(hasattr(self.built, 'string_route'))
        self.assertEqual(string.guide_point[0], self.built.weight_axis[0])
        self.assertEqual(string.guide_point[2], geometry.string_hole_z)
        self.assertGreater(geometry.string_spool_z, geometry.string_hole_z)
        self.assertGreater(geometry.string_spool_z, self.built.weight_axis[1])
        self.assertGreater(geometry.string_spool_radius,
                           abs(self.built.weight_axis[0]))
'''
edits['simulation/wall_clock_02/test_clock.py'] = test.replace(t_old, t_new)

for rel, text in edits.items():
    path = os.path.join(dst, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        fh.write(text)
    print('wrote', path)
