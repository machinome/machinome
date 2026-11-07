# Avoid exact-equal artifact timestamp writes

Status: maintenance plan approved by root's delegated review under active pilot
goal authority, 2026-11-07; apply authorized after planning commit gates. No cure for
Enigma's unexplained delayed ctime changes is claimed. This note is evidence
and intent; the OpenSpec proposal is the reviewable contract.

Origin: `/mnt/data/machinome-projects/enigma-i`, ordinary declared
`simulation.candidate_machine:CandidateMachineInspection`, source publication
diagnosis at project `a3bd96a7e2da90e8a04c38fd3861163a0d514e90` and framework
`b0829b39809e64e889e56eb9bececa57cd3430ad`. Plain ordinary builds v4/v5/v6
refused ctime changes while artifacts were pinned. The v3 full-publication trace
passed after two caught refusals, with project/framework pins and viewer document
bytes unchanged. It counted eight exact-equal mtime restamps on the two watched
artifacts; every one changed ctime and produced an audit/syscall/inotify event.
Six other ctime-only jumps lacked corresponding events in the recorded window.
No watched child writable open/mmap/write or writable `/proc` handle was found.
Idle artifacts, disposable restamp copies and isolated production facts work
were negative reproductions. The actual delayed-change writer is unresolved.

Durable origin evidence is under project `sources/derived/`:

- `standard-model-artifact-diagnostic-v3/analysis.json`, SHA-256
  `b435fd058173a0b94b249ac5bbc3e19bd0dc35e222d513d86b613ad3914162ed`;
- its `same-mtime-restamp-review.json`, SHA-256
  `3e6de4db3bf2c4acc460194da8b50fc22e6a7cda929e2b2cbe44b18bde3d5b6a`;
- its process receipt, worker/observer logs and source-pinned scripts;
- `artifact-idle-observation-v1/`, `artifact-copy-restamp-control-v1/` and
  `artifact-facts-control-v1/`, retaining the negative controls.

The independently supported maintenance need is narrower: `currency.restamp`
sets an already-correct exact mtime again, updating atime/ctime without improving
currency. `_content_verified` still must prove compatible recipe and retained
source bytes and must refresh the current digest/fingerprint record. An exact
mtime equality check at the mutation helper can skip the redundant syscall
without changing those proofs or `ArtifactSnapshot`'s full identity validation.
No tolerance, content shortcut, guard weakening, new API or document version is
needed. `currency.publish_text` already uses this desired-state distinction.

Authority: workspace `/home/asa/devel/machinome/goal.md` requires delivery through
the declared model/ordinary build and correction of limitations in the owning
package. Root assigned a standalone maintenance cycle under that goal. Root
reviewed and approved its full planning state on 2026-11-07, releasing planning
commit 1, red-first apply, focused/WT caller checks and sync/archive/completion
commit 2. Local integration is authorized after root reviews green caller
evidence and the exact two-commit handoff. This is delegated review, not a claim
of human review of finished text. No push/publication.
The unratified lamp-color API change remains separate and unchanged.

Managed bench: `machinome/WTs/skip-equal-artifact-restamps`, same-named branch,
slot 15, source primary clean `main` at `b0829b39`. Proposed OpenSpec change:
`packages/machinome/openspec/changes/skip-equal-artifact-restamps/`. Real red proof
must hold an `ArtifactSnapshot` across matching-mtime content-proven record
refresh; green must preserve that pin while updating the record. Caller checks
then use the WT-owned runtime and, after authorized integration, the installed
runtime's plain canonical build, without hand-editing cache or document data.
