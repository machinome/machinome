# Evidence — preserve native Boolean inputs

## Origin and pins

Curta Type I is an independent project under
`projects/Calculators/Curta-Type-I-3x`. Its committed baseline
`48d71c91bfb0b37c831cb8cd0ecc098dbc86d844` posed native drums afresh;
the reader then had SHA-256
`10a913c45758bb24e88a7ab6e2fe9c433f4657cdf9876f5b71db77d52a11c19c`.
The native-drum cache was an **uncommitted, subsequently withdrawn trial**;
its transient source bytes were not recorded. The committed fresh-native
reader at `0cb681a01202184ee3f146027a9881bc657ecf50` has SHA-256
`6807d34bec012bbd3e637d8a7da80470360c5c74d116e51df971269dd89ac1f7`.
The final 169° and 173° diagnostics ran after project evidence-only commits
at `96a94961be6862e9dab163d013fe6715d1f1d8cf`; the reader and refiner
source hashes below remained unchanged.
The diagnostic [reproduce_curta.py](./reproduce_curta.py) reconstructs the
trial's reader-local drum reuse in-process without changing the project.
The refiner SHA-256 is
`accdb137b2d70da51030b8fb932327704967bea832f7a1e6e0036d747c37888e`;
the world64 seed file
`_build_checks/reverser-phase-midpoints-world64-48d71c9.jsonl` hashes to
`a6955cab207cf1a6dbd24f1beaf73bd49db2750b115d3611d004026a12f7f00a`.
The fresh-native ten-boundary control
`_build_checks/reverser-phase-native-fresh173-48d71c9.jsonl` hashes to
`159206126174a74c828493f2a3850f49514229c867c06453c26aa5ebb9f02878`.

From the Curta project root, the final framework probes are reproducible with:

```sh
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=/home/asa/devel/machinome-studio/machinome/WTs/preserve-native-boolean-inputs:. SOLID_BUILD_DIR=_build_checks /home/asa/devel/machinome-studio/.venv/bin/python /home/asa/devel/machinome-studio/machinome/WTs/preserve-native-boolean-inputs/openspec/changes/archive/2026-09-23-preserve-native-boolean-inputs/reproduce_curta.py --input _build_checks/reverser-phase-midpoints-world64-48d71c9.jsonl --baseline _build_checks/reverser-phase-native-fresh173-48d71c9.jsonl
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=/home/asa/devel/machinome-studio/machinome/WTs/preserve-native-boolean-inputs:. SOLID_BUILD_DIR=_build_checks /home/asa/devel/machinome-studio/.venv/bin/python /home/asa/devel/machinome-studio/machinome/WTs/preserve-native-boolean-inputs/openspec/changes/archive/2026-09-23-preserve-native-boolean-inputs/reproduce_curta.py --input _build_checks/reverser-phase-midpoints-world64-48d71c9.jsonl --single-169
```

These absolute workspace paths matter because this development catalogue's
project directory may be reached through a symlink outside the studio root.
To repeat the red controls, check out the verified framework base
`82bf530cacae1fd7b841a47a35c961eb438b79f8` in a **separate** framework
worktree and point `PYTHONPATH` at that exact absolute worktree path, not the
moving primary `main`. Add `--limit 2` to the first command for the original
reused-input failure. The diagnostic script's `--copy-operands` option then
demonstrates private copies over the unchanged default kernel. After local
integration, the final-source commands can instead point to primary
`/home/asa/devel/machinome-studio/machinome` only after verifying its
`exact.py` SHA-256 is the final hash recorded below. No project source is
edited.

Framework base `82bf530cacae1fd7b841a47a35c961eb438b79f8` has
`machinome/exact.py` SHA-256
`1529c4c75fff7e1879752dee2d22597d0afb2262ebdfeeebf72cc09ea6ffc7dc`.
The rejected protected-mode trial's `exact.py` SHA-256 is
`f0c08c5639fde15b24a37358d2b74792fd800611ed40299daef462d6067c7cd4`.
The revised copied-default candidate's `exact.py` SHA-256 is
`ffc57c6146adafe4f880e5227bc859df05a034ca214dc5b21f56474b6cbfc1dd`.
It deep-copies both operands for Common, Fuse and the empty-common witness
Section, while leaving OCCT in its original default operation mode.

## Red-first and native input mutation

On the unchanged framework, the revised input-isolation tests fail red:
Common, Fuse and Section all receive the original operands at `Build`, and
injected copy failures never occur because no copy is attempted. The
rejected protected-mode trial also fails these tests: it changes the mode,
but still receives the original B-reps.
The reconstructed Curta trial on that same base refused on call 40, station
1, crank 173°, height -3 mm, shaft `207.5123519897461`°, with an invalid
two-solid common whose bogus reported volume was `1241.4637972376165` mm³.
A fresh pose at that exact state returned a valid positive common of
`2.8890132738894073e-12` mm³. In the failing reused-input sequence,
`207.51234436035156`° was the last valid free sample and
`207.51235961914062`° was the last valid positive sample
(`1.767487067998046e-11` mm³); the intervening
`207.5123519897461`° was **invalid**, not a measured positive endpoint.
Only the separate fresh-input control resolved that intermediate sample as
valid and positive.

The diagnostic fingerprint hashes topology counts, every vertex coordinate,
and every vertex, edge and face tolerance. It detected changes to the same
reused top drum after calls 18, 19, 37, 39 and 40, from initial
`1296fd497dfec2b8735310adc4c07d9048277b95dab13b4363c771b66a080f9d`
to final
`76b85b3beab92cf5d25d6ffab8040ebdd2da303556914257a40eff12fa791c65`.
It did not observe gear or lower-drum changes in that 40-call prefix.

## Rejected protected-mode trial

The same process-local reused-drum sequence under this trial completed
all 200 native calls and all ten height-minus-3 boundaries. The diagnostic
checked both drum operands and the fresh gear after **each** call and
reported `input_mutations: []`. Focused real-OCCT tests separately checked
both input fingerprints around Common, Fuse and an empty-common Section,
and retained disjoint, tangent and positive-volume controls. The focused
exact suite passed 18 tests and 13 subtests in independent peer review.

Against the fresh-native baseline, the candidate's exact contact booleans,
zero/positive classification for both drums, and shaft endpoints match for
all ten boundaries. Full endpoint dictionaries are **not** bit-identical:
five positive left-endpoint top-drum volumes differ (candidate / fresh,
mm³):

| Boundary index | Candidate | Fresh-native |
| ---: | ---: | ---: |
| 0 | 2.2762822757720675e-12 | 1.5913085305774733e-12 |
| 2 | 2.2762823478656957e-12 | 2.511784264074889e-12 |
| 4 | 2.276282411507806e-12 | 2.4348147477522325e-12 |
| 6 | 2.2762823623622254e-12 | 2.255273460912726e-12 |
| 8 | 2.27628219248961e-12 | 9.91769589416577e-13 |

No difference was converted to zero or clearance. The candidate boundary
SHA-256 is
`374e0093793feea84a5e2fc4ee1ea762fe5331dd06157b87a8bfb5582646c48e`;
the fresh-native boundary SHA-256 is
`b6a48b84fc41f93e4371fc590764e6f3ccc5b21c0407609fc1e164551fa293ce`.
This is classification-level, not numeric-bit, parity.

The unfingerprinted protected-mode trial took 68.94 process-CPU seconds for the 200
calls after setup. With every-operand fingerprinting, the same sequence
took 97.45 process-CPU seconds after setup. These results are **not** an
acceptance gate for the final design. A separate fresh-input Curta common at
crank 169°, shaft `150.7459411621095`°, height -3 mm and lift zero exposed a
decisive regression: protected mode returned an **invalid** two-solid top-drum
common, while the default mode returned a **valid** two-solid common. Both
reported volume `4.241072983936974e-09` mm³; the bottom-drum common was a
valid empty in both. Changing parallel mode did not repair the protected
result. This trial was rejected rather than interpreting its invalid result
as contact or clearance.

## Copied-default controls

In a process-local test over the unchanged framework, deep-copying both
operands before each default Common made the 169° result valid, then completed
all 200 reused-drum calls and all ten 173° boundaries without any caller
operand fingerprint change. Every boundary endpoint dictionary, including
the tiny positive volumes, is bit-identical to the fresh-input default-mode
control: both SHA-256
`b6a48b84fc41f93e4371fc590764e6f3ccc5b21c0407609fc1e164551fa293ce`.
With every-call operand fingerprinting, that process-local copied-default
trial took 94.01 process-CPU seconds after setup. This is a finite project
measurement, not a general performance claim. The destructive no-copy
baseline fails at call 40, so a 200-call before/after speed ratio would be
misleading. The framework's exact placement cache remains bounded at 512;
private copies are not stored there.

Under the final framework source SHA above, a fresh 169° pose returned a
valid two-solid top common with the same exact volume
`4.241072983936974e-09` mm³ and a valid empty bottom common. Focused exact
tests passed 83 tests and 15 subtests, including actual B-rep identity at
`Build` for both inputs of Common, Fuse and Section; injected copy failures
retain pair-named refusals. The independent reviewer found no source blocker.
The actual framework implementation (without the process-local copy wrapper)
also completed the original 200-call/ten-boundary Curta sequence with
`input_mutations: []` after every call and **bit-identical** endpoint records
against the fresh-native default control, SHA-256
`b6a48b84fc41f93e4371fc590764e6f3ccc5b21c0407609fc1e164551fa293ce`.
Its instrumented refine took 141.63 process-CPU seconds while four other
native survey shards were running. That is not directly comparable to the
94.01-second process-local probe above; neither is a reliable speedup or
slowdown claim. The important result is exact behavior and input preservation.

The same two original Curta `ReverserToothEnvelopeTest` caller methods passed
**2/2 in 109.065 s** under final copied-default source SHA above, with INFO
logging disabled. They cover complete-print admitted contact/clearance and
nonzero retained shaft-phase/drum-lift placement; no project runtime source
was changed for this framework gate.

Two original Curta `ReverserToothEnvelopeTest` caller methods—complete-print
admitted contact/clearance and retained shaft-phase/drum-lift placement—passed
2/2 in 103.690 s under the **rejected protected-mode trial**; these are
not the final-source caller gate reported above. Its full isolated framework suite
passed 3620 tests and 2137 subtests with 4 skips and 53 warnings in 430.01 s;
this green suite did not catch the external 169° regression. The final copied-
default full framework suite passed **3622 tests, 2139 subtests**, with
4 skips and 53 warnings in 460.38 s. The final-source caller results are
recorded above. The independent reviewer found no source or record blocker.
The browser viewer does not use native OCCT Booleans.

## Limits

The fingerprint is deliberately specific; it does not prove byte-identity of
every B-rep p-curve or connectivity record. The private exact B-rep copies
separate caller-owned topology/tolerances from the default OCCT Boolean;
the actual trial verifies that the previously drifting subshape tolerances
no longer drift.
This change neither repairs a shape already mutated before process restart
nor proves all future OCCT operations will be valid. The Curta reader still
rejects invalid commons; the framework's Build-failure and independent
false-empty refusals remain in force. `intersect_shapes` does not itself
universally check `isValid()` on every nonempty common. No mesh fallback or
positive-volume waiver is introduced.
