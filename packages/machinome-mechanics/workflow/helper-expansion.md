# Empirical helper expansion

Pilot authority: 2026-09-20 conversation. Implement the audited shortlist,
one public helper per OpenSpec cycle; after implementation use gpt-5.6-sol
subagents to refactor consumers and report issues. Validate in at least two
distinct project repositories, sync baseline specs, archive and merge locally
before starting the next helper. No per-cycle ratification is required. Skip a
blocked helper with evidence; do not archive unfinished work. No push or release.

Each cycle records its exact consumer commits, validation commands, results,
limits and any issues in its own `validation.md`. Existing project evidence and
user changes are preserved. Refactors preserve mechanics and public controls;
new design choices exposed by validation are reported, not silently substituted.

| Order | Public helper | Empirical consumers to verify | State |
| --- | --- | --- | --- |
| 1 | `rolling_travel` | Dragon R1; Thor; six additional repositories | validated, archived for local integration |
| 2 | `rolling_angle` | Prusa3-vanilla; Kossel | queued |
| 3 | `pulley_pitch_radius` | Thor; Open Robot Actuator | queued |
| 4 | `belt_tangent_points` | Thor; Prusa3-vanilla | queued |
| 5 | `belt_path_metrics` | Thor; Prusa3-vanilla | queued |
| 6 | `belt_pulley_angle` | Metamaquina2; Prusa3-vanilla; Kossel | queued |
| 7 | `two_link_angles` | YouCanBuildBiPed; ZeroBug; Spiderbot | queued |
| 8 | `four_bar_pose` | Dragon R1; Strandbeest | queued |
| 9 | `cycloidal_ratio` | CycloidalDrive; OpenCycloid | queued |
| 10 | `harmonic_cam_lift` | Leonardo cam hammer; Deepseek sawmill | queued |
| 11 | `internal_mesh_angle` | Thor; OpenTorque | queued |
| 12 | `differential_angles` | Thor; Dragon R1 | queued |
| 13 | `indexed_advance` | Pascaline-module; Deepseek sawmill | queued |

Names and consumer selection remain working assumptions until each cycle's
source inspection confirms its contract. Do not manufacture a second consumer
or change a project's behavior merely to meet the threshold.
