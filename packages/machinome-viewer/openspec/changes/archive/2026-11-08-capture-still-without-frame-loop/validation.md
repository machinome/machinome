# Validation — 8 November 2026

The implemented correction consumes existing API 29 and ADR-077. No new ADR,
architecture change, document version, package version, dependency or public
option is introduced. Source changes are confined to capture.py and its tests.
The coordinator reviewed the planning artifacts and implementation under the
pilot's advance finish-and-integrate authority.

## Regression and browser proof

- The selection/redraw regression failed against base `5c07ea93682bc1007849cefe7ef30f96710fd409`: four failures (three eligible-mode subcases and final public redraw), with continuous-path cases passing. The retained raw run uses an isolated baseline package and pytest importlib mode, so the test path cannot accidentally select the candidate package.
- The completed capture suite passes 34 tests and eight subtests, with no skips, on the locked Python 3.12 bench. The earlier Python 3.11 run also passed.
- All 66 existing widget browser tests passed in the combined run. That combined run's one failure was the new observation fixture expecting running-style `coordinates` in a clocked document; the expectation was corrected to its published driver/state defaults and the complete capture suite rerun green. The original result is retained rather than rewritten.
- Real capture-produced pages prove a posed requested instant and camera/up/FOV, clocked initial bank with instructions, no simulation requests, final redraw, 160 ms without additional RAF callbacks on eligible stills, and the retained continuous running/rest and posed-instruction paths. Existing marking/alpha/chrome tests pass. A malformed clocked document remains a loader refusal.
- Public OrbitControls normalization changes camera values by about 1e-14; observation compares camera coordinates to 1e-10. This is a camera arithmetic comparison, not a geometry or bank tolerance.

## Enigma proof

Input: project main `1dd1e48ed1e604bf15c972c94e9eff42d094b3a7`, declared model
`simulation.candidate_machine:CandidateMachineInspection`, 2,023 published leaf
nodes, document SHA256
`f6ffa7958cf787d2d5b06f246a11d380ef4b3851f8585756a653650629ddbf6a`.
Every one of its 572 referenced artifact paths is pinned in
[evidence/enigma-inputs.json](evidence/enigma-inputs.json). Baseline and candidate
used separate unchanged staging copies, the same locked environment, identical
bundle bytes, production headless Chromium/SwiftShader arguments, time zero,
automatic camera fit and 1100 × 800 pixels. Capture owns its ordinary ephemeral
loopback server; no alternative display or fixed port was introduced.

| Public command | Budget | Observed command time | Terminal result |
| --- | --- | --- | --- |
| baseline `machinome viewer capture` | 180 s | 180.198 s | budget timeout, exit -15, no PNG |
| candidate `machinome viewer capture` | 180 s | 27.415 s | exit 0, inspected PNG |
| candidate ordinary `machinome snapshot --viewer web` | 240 s including preparation | 105.485 s | exit 0, inspected PNG |

The watchdog checks at 0.2-second intervals; the baseline elapsed time reflects
that polling granularity, not an enlarged timeout. Its failure is retained and
is not used to invent a speedup ratio. Every exact owned process identity was
cleaned up; terminal receipts report no survivors. Studio's server identity
remained live throughout and was never stopped, suspended or restarted.

The ordinary private staged document was observed after 79.723 s; its 543 rigid
model assets all match the frozen publication. First browser observation is
recorded separately in its terminal receipt. The staged snapshot is version 3
because the ordinary command bakes the standing pose; it does not replace the
version 4 published interactive document. The two accepted PNGs are byte-identical:
SHA256 `6f6c529a27f7129c209fe0787e245b959d4aaea32af5c393526a357d2f758f6e`,
157,086 bytes, 1100 × 800, alpha extrema 0 and 255. Both were visually inspected:
complete fitted machine, keyboard lettering and rotor markings, no viewer chrome.

The first ordinary command also produced an inspected image and printed
“Snapshot saved”, but the observer read its staging JSON mid-write and failed
before collecting its exit status. Its return code is UNKNOWN, explicitly
retained under [evidence/ordinary-observer-failure](evidence/ordinary-observer-failure).
The coordinator reviewed and authorized the in-scope harness correction: tolerate
the incomplete JSON read, enforce cleanup in finally, and repeat only the ordinary
confirmation at the same 240-second cap. The valid matched pair was not repeated.
The corrected confirmation has an exact exit-0 receipt and no observer error.

An earlier preflight refused to start a capture while Studio had an automatic
snapshot running. It is retained separately. The accepted jobs' preflights and
periodic samples show no competing build/capture job; Studio reported no build
or error and event sequence 137854. Postflight confirms the project Git tree,
model source, published document and every pinned publication artifact are
unchanged.

This establishes ordinary static photographs. Interactive Studio keeps its
continuous mount; its screenshot limitations, complete coupled typing and powered
lamp acceptance remain separate. Publication, push and contact were not performed.

## Completion

The coordinator owns local main integration and registered worktree cleanup.
This branch retains exactly the planning commit and one content commit over the
recorded base. The snapshot-capture baseline receives the tested requirement;
the completed change and its evidence are archived together. No new ADR is needed.
