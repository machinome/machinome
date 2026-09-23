Test assertions
===============

The testing API lives in ``machinome.test``. Tests for ``foo.py`` live in
``test_foo.py`` beside it, or in ``test.py`` for a package; subclass
``TestCase``, or mix ``TestCaseMixin`` into the node class so the tests
live next to the model. The runner builds the node under test, hands it
over as ``self.node`` and as the snake-case name of the test class
(``SpurGearTest`` gives ``self.spur_gear``), and runs every ``test_``
method once per declared instant, restoring operation checkpoints
between. All the standard ``unittest`` assertions are available.

Pairs of parts
--------------

``assertNotIntersecting(node1, node2)``
    The two parts do not overlap.

``assertIntersecting(node1, node2)``
    The two parts have some overlap: a handle is not detached, a key is
    engaged.

``assertIntersectVolumeAbove(node1, node2, min_volume)`` and ``assertIntersectVolumeBelow(node1, node2, max_volume)``
    The overlap volume, in mm³, is above or below a bound.

``assertInside(node1, node2)``
    Every mesh vertex of ``node2`` is classified inside ``node1``.

``assertClose(node1, node2, max_distance)`` and ``assertFar(node1, node2, min_distance)``
    Every mesh vertex of ``node2`` is at most, or at least, that far from
    ``node1``'s surface.

The intersection questions are answered on the exact kernel when both
parts are exact and on meshes otherwise (:doc:`/howto/fast-tests`).
For a direct comparison of two already-placed exact CadQuery shapes,
``machinome.exact.intersect_shapes(first, second)`` returns their native
common. If OCCT reports an empty common but an independent native section
and zero-tolerance solid classification find a point strictly inside both
shapes, it raises ``ExactCommonInconsistency`` rather than claiming
clearance or inventing a volume. If that independent check cannot complete,
it raises ``ExactCommonVerificationError``. Exact intersection assertions
use the same path. The bounded witness search does not certify every empty
common: no witness leaves the ordinary Boolean verdict in place. Face and
edge contact remain subject to the existing zero-volume policy.
``assertInside``, ``assertClose`` and ``assertFar`` always sample
``node2``'s vertices against a mesh surface; they do not inspect points
along edges or faces, so their verdict depends on mesh density, and by
itself does not prove whole-solid containment. Use the intersection
assertions when the contract concerns overlap between a named pair.

Fits, from both sides
---------------------

``assertBlockedBeyond(node, amount, against, axis=(0, 0, 1), volume_epsilon=0.0, along=None, directions='both')``
    Rotated by ``±amount`` degrees about ``axis``, or displaced by
    ``±amount`` mm along the unit vector ``along``, ``node`` must
    intersect ``against``: the fit genuinely locks beyond its play. A
    key, a dog clutch, a hex socket; in translation, a pin captured in
    its bore.

``assertFreeWithin(node, amount, against, axis=(0, 0, 1), volume_epsilon=0.0, along=None, directions='both')``
    The twin: perturbed the same way (``amount`` may be a list), ``node``
    must **not** touch ``against``. A blocking test alone is satisfied by
    an undersized bore that always rubs; free play within a smaller
    amount closes the loophole.

Both perturb ``node`` in its **own** frame: the perturbation is inserted
before every operation of the node, so its rotations, a leading one
included, carry the direction. ``axis`` and ``along`` are mutually
exclusive. ``directions='forward'`` checks only the positive sense, for a
deliberately one-sided contract. ``volume_epsilon`` counts an
intersection below that volume as none; it applies only on the faceted
path, is ignored with a warning when every comparison routed exact, and
is a smell rather than a tool.

.. code-block:: python

    def test_dog_clutch_engages(self):
        self.assertFreeWithin(self.sleeve, 2, self.gear)
        self.assertBlockedBeyond(self.sleeve, 5, self.gear)

    def test_pin_captured_in_bore(self):
        self.assertFreeWithin(self.pin, 0.1, self.bore, along=(1, 0, 0))
        self.assertBlockedBeyond(self.pin, 0.5, self.bore, along=(1, 0, 0))

Whole machines
--------------

These walk the tree from ``node`` down to the **topmost rigid part** on
each branch, the printed solids of :doc:`/concepts/node-tree`, and never
descend into a fusion's ingredients. Neither runs automatically;
``machinome new`` scaffolds the first two into the root test file.

``assertNoDisconnectedSolids(node)``
    Every printed solid is exactly one body: the exact geometry's solid
    count for an exact part, a split of the part's own STL otherwise,
    with no operations composed, so the verdict is the same at every
    instant. Watertightness is not connectedness.

``assertNoSolidInterference(node)``
    No two printed solids share positive volume in world coordinates at
    the runner's current instant. Exact boundary contact passes; there
    is no epsilon and will be none, because a volume waiver can hide a
    real narrow penetration. Where parts must run free, encode clearance
    in the model and state a fit contract. Decorate the test with
    ``@testing_steps`` or ``@testing_instant`` when the contract must
    cover motion, or sweep it in a scenario. Internally a sweep-and-prune
    index emits only pairs whose bounds overlap, chosen in whichever
    frame makes the boxes smallest, and a pair whose surfaces come
    nowhere near each other is decided empty without a kernel call.

``assertJoined(node1, node2, min_weld_volume=0.0)``
    Two features of the **same** printed solid meet directly, with a
    shared volume of at least ``min_weld_volume``. Tangential contact is
    not a join; a pair from two different solids fails naming both.

Gravity
-------

``assertAssemblySupported(node, gravity=(0, 0, -1), max_drop=1.0, ground=None, supports=None, stability_margin=0.0)``
answers the opposite question to interference: not whether two parts
share material, but whether the assembly can exist. It proves two things
about the printed solids at the runner's instant.

**Reachability.** A solid is directly supported by another when,
displaced by ``max_drop`` along the normalized ``gravity``, it intersects
that solid with positive volume: resting on a face, sitting in its
clearance gap, hanging by an engaged lip. Those relations form a support
graph, and a part is supported only if the graph leads it to a grounded
solid; a block on a floating bracket is reported with the bracket. With
``ground=None`` the solids reaching within ``max_drop`` of the assembly's
furthest extent along gravity are grounded, which is what an unmodelled
floor would touch. Pass ``ground`` (a node or nodes) for an assembly hung
from a ceiling or bolted to an unmodelled frame; those become the only
seeds, and no floor exists.

**Equilibrium.** Reaching ground is not standing up: a bar resting on
one support at one end reaches ground and falls over. So the assertion
then proves frictionless static equilibrium: some distribution of
push-only normal forces over the detected contacts balances every
non-anchored solid's weight and the torque about its centre of mass, all
at once, decided by one deterministic linear program. Contacts are found
by the drop and by a symmetric lift, so an engaged couple, a pin
cantilevered in a snug hole, balances legitimately. The failure names the
solid that cannot be balanced and whether force or torque does not close.
The virtual floor is a real anchored body, so a top-heavy part on too
small a foot fails.

``supports=[(supported, supporter), ...]`` declares holds the assertion
deliberately cannot prove, press fits, glue, friction, and keeps the
exemption visible in the test; a declared edge transmits an unrestricted
wrench and grounds the supported solid, but a declared supporter must
still be grounded itself. ``stability_margin`` (mm) shrinks every
contact patch toward its centroid first, so a knife-edge balance, which
is an equilibrium at the default, is rejected and robustness becomes an
explicit statement.

``max_drop`` is the one real judgement: larger than the design's vertical
clearance play, or a part in its clearance gap reads as floating, and
smaller than the thinnest supporting feature plus the gap above it, or
the drop tunnels through its support. The 1.0 default sits between
printed clearances (0.5 mm or less) and printed walls (1.2 mm or more).

What passing means: reachability, force balance, torque balance and
toppling over the detected contacts. What it does not mean: friction,
adhesion, purely lateral wall reactions, the toppling of a single solid
on the floor, and every dynamic effect. Zero or one selected solid passes
without loading geometry. Its bounds stay conservative world boxes
always, because gravity is a world-frame fact.

Instants
--------

``@testing_instant(t)`` pins the timeline at one instant;
``@testing_steps(n, start=0, end=1)`` sweeps it (``n >= 2``, the last
instant exactly ``end``), seconds under a declared loop. A method decorated
this way runs once per instant, and a skip at one instant with passes at
the rest is reported passed, saying how many instants it skipped. A
machine driven by inputs rather than time is swept with a scenario or
with ``set_state`` in a loop.

.. _skip-and-expected-failure:

Skipping a test and marking a known gap
---------------------------------------

A test that does not apply, the exact kernel not installed, a part this
project does not have, says so with ``self.skipTest(reason)`` anywhere in
the method or in ``setUp``; ``unittest``'s own decorators work too, on a
method or a whole class. A skipped test is reported by name with its
reason and counts as neither a pass nor a failure.

A known, accepted gap, a regression not fixed yet or a kernel limit, is
marked ``@unittest.expectedFailure`` instead of being deleted or left
red. A marked method that raises is reported an expected failure with no
traceback and does not count as a failure. A marked method that does
**not** raise is an unexpected success, and that **fails the run**: a
green suite must not stand over a statement about the machine that is no
longer true. The summary line reports each count that is non-zero.

Deprecated
----------

``assertNoPairwiseIntersections(node, volume_epsilon=0.0)`` walks every
leaf pair and warns. ``assertNoSolidInterference`` replaces it, with the
deliberate scope change: topmost rigid solids instead of every leaf, and
no overlap epsilon.
