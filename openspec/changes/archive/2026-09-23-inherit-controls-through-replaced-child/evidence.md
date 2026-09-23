# Evidence

## Origin and red reproduction

The unchanged Curta adoption worktree at
`projects/Calculators/Curta-Type-I-3x/_build_worktrees/adopt-reverser-contact`
declares `LoopOperatingTrial(OperatingCurta)`, replaces `carriage` with
`LoopRunningCarriage`, and explicitly copies 25 ancestor controls before
adding one loop Turn. Project trial source SHA-256
`6bbfb8081f1e6219cb9bb228d3c80e3b2c212f5ee306e95ac8fe1a502e4a039d`.
Its original `_build_checks/operating-loop-trial-01.log` shows class
definition refusing `shift carriage`: the first `carriage` segment is
listed among `LoopOperatingTrial`'s children but is a different
declaration object. A minimal public test in
`tests/test_inherited_replaced_child_controls.py` reproduced that exact
class-definition failure before the runtime correction (1 test, 1 error).

## Candidate and framework gates

The producer admits only the unchanged ancestor-table control under
the same entry name across a subclass-compatible same-path child
replacement. Its effective part/joint path is resolved at compile;
missing nested paths refuse by control name. Foreign same-name refs,
new controls borrowing an ancestor child, unvalidated mixin tables, and
incompatible replacements still refuse. Synthetic focused tests are
10/10 green. Existing
control/direct-motion/running-document tests are 208/208 green. The
final full framework suite on the provenance-hardened runtime passed
3,713 tests, with 4 skipped and 2,233 subtests passed, in 396.86
seconds. Its predecessor before the final marker guard passed 3,711
tests, 4 skipped and 2,233 subtests in 381.14 seconds; the later two
tests explicitly pin marker provenance and a borrowed ancestor child.

The Curta trial imports unchanged with 26 controls and constructs
`Sim(LoopOperatingTrial(), 1/240, meshes=False)` with 26 compiled
controls. A direct producer document is version 13, still has 26
controls, and carries program identity
`2b6b59dbb135bd0c0ced9ba87fcc8df9dc36588138d1b0294ce7b8543588df1b`.
At that probe, `control.py` SHA-256 was
`48ec176d98980445061830eeba68869900fc6420fb52ee34efdf3f7769b2d374`;
the final provenance hardening to require the ancestor's own validated
controls marker changed it to
`6994068fb2c8a5d53930c230eb30bdc1972e395de420a33b8662fa62566f448c`
and `program.py` was
`101ac4f22e2c45fa7deb8da6b922d55f89f899683f72ffd3dae449a45d8cc9d2`.

The originating project's retained operating test passed 2/2 under
the candidate: the existing clear and new loop controls are both
present; the loop request sequence reached partial 30, blocked 90.4,
blocked again on retry, relieved to 45, blocked at -0.4 and returned
to rest 0. Unrelated coordinates and restore/replay snapshots remained
exact. Project log `_build_checks/operating-loop-trial-02.log` SHA-256
`496168d06ac3837780c8019597d3eebe56e5c98e2f76cd25a80cb25aef48bb42`.
The same two tests were rerun against the final hardened source and passed
2/2 in 11.018 seconds; retained log
`_build_checks/operating-loop-final-framework-01.log` SHA-256
`fbd70b453040941d222849ee66fa4c8e806f8c1aae65c05a9da451f893dcd32b`.
The broader project preservation gate passed 3 tests in 154.076 seconds:
the 216-coordinate trial bank differs from the 214-coordinate source only
by the new driver and swivel, old bank entries are exact at seven states,
386 existing rigid meshes and all flexible pieces are unchanged, and
the control table is 26 rather than 25 entries. Its retained log
`_build_checks/operating-loop-preservation-01.log` SHA-256 is
`8e8e0430b11a61d0cec1d68a6d0bacdfc510a3531d3121b13736311f3feea3e3`.

## Paired viewer gate

The initial hosted export refused before gestures: viewer API26 keyed a
control only by `(part, kind)` and rejected two Turn controls on one
visible clearing-ring leaf despite their distinct explicit selected
joints. Its red report is
`_build_checks/operating-loop-trial-pointers-01.json` SHA-256
`e2228ef9848f7dd3dc9813b920154961911813c500c27a58f48ec68eef5f2355`.
The viewer-owned API27 correction keeps document v13 and the producer
wire unchanged, distinguishes the two named joint handles, and keeps
the selected handles stable under pointer hover. The originating
project's final hosted report
`_build_checks/operating-loop-api27-two-turn-pointers-02.json` SHA-256
`eeebe9139cb60acbbe3ef9e8e63c466e923c201b4c0dedcaa88bbbd4239ac1c5`
passed on the unchanged exported document SHA-256
`46f7d5245d260423046d295a7866b08b6f95f410941c3892b5ba855356fcc029`
and viewer bundle SHA-256
`4e4580332e33c75042c2e188f80fbd3b8712280dabc1e56a895310651160339c`.
The mounted run had 216 coordinates, 26 controls, identity
`2b6b59dbb135bd0c0ced9ba87fcc8df9dc36588138d1b0294ce7b8543588df1b`
and `dt=1/240`. The clear handle admitted +1 only to clearing, and
the deploy handle +4 only to loop; both released with no remaining
command or browser error. Root inspected the hosted pixels.

## Limits

This corrects declaration validation, not the Curta's mounting geometry
or contact law. The new driver and control legitimately change the
trial document; no whole-document byte-identity claim is made. The
producer document remains v13 with ordinary compiled controls. Its two
controls on one visible leaf name distinct joints, coordinates and
operation spans. The paired viewer correction is separately owned and
must be integrated with its own evidence; this producer cycle does not
claim to change viewer behavior or prove the Curta's broader mounting
geometry from these control checks.
