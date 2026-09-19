# Adversarial and visual review — 2026-09-19

The root agent reviewed the separate Sol implementer's changes before spec
synchronization or archival. The Sol proposer and implementer were distinct
agents. Scope remains the owner-delivery conformance fix for operating Curta;
no Curta geometry, laws, tolerances, source or tests were edited.

## Adversarial findings

All findings were resolved before this review passed:

1. Stopping every consumed name would suppress the established ambiguity
   check for originally bare coordinates. Only originally qualified entries
   may stop at their addressed owner.
2. A single provenance bit per projected mapping key loses a bare claimant
   when bare and qualified names collapse to the same key. Mixed-name cases
   were reproduced red in both orders, then passed with ordered variants.
3. Grouping variants or preferring qualified values changes established
   last-write behavior for accepted aliases of a single owner. The final
   carrier preserves caller order; base and candidate agree for both orders
   of `slide.travel` and `travel`.
4. Publication assertions must check each node's own qualified rotation
   expression, not merely search for all identifiers somewhere in the document.
   World-transform assertions must check intermediate owners as well as the
   leaf so that canceling errors cannot pass. Both tests were strengthened.

Independent final stress checks covered all 720 permutations of the Curta
minimal probe's complete retained bank plus time. Every ordering retained
owner slots `(20, -90, -146)` and the exact simulation snapshot. Bare `turn`
combined with each of the three qualified paths in both orders (six cases)
was refused as ambiguous with all claimants identified and exact rollback.

The implementer's 312-test regression run and unchanged Curta acceptance
(2 minimal tests and 3 faceted geometry tests) passed. The reviewer additionally
ran:

```text
PYTHONPATH="$PWD" /home/asa/devel/machinome-studio/.venv/bin/python -m unittest \
  tests.test_state_binding tests.test_running_corpus \
  tests.test_retained_coordinate_delivery
Ran 55 tests in 1.751s: OK
```

This includes existing state-binding compatibility and running-document corpus
checks; no schema, version, public API or architecture change is needed.

## Actual Curta mesh evidence

Project checkpoint: `1aaad6c37c1117b3582977a199ebf4c5722c4c97`.
Framework baseline: `c62319e1974b88d8cfd2dd13fd205c7bf2533991`.
Candidate: planning commit `0ccdc6bdc11637a06ebb233b3075e1602a661f57`
plus the reviewed implementation identified below.

The adjacent `curta_pose_images.py` imports the unchanged project, loads actual
faceted world meshes, compares them with the requested rigid motion and verifies
exact snapshot restoration. Run it with the selected framework first on
`PYTHONPATH`, the workspace Python, and explicit project/output arguments:

```text
PYTHONPATH=<framework-checkout> <shop>/.venv/bin/python \
  <change>/evidence/curta_pose_images.py \
  <shop>/projects/Calculators/Curta-Type-I-3x <temporary-output-directory>
```

The script logs the imported framework module and project commit. Builds and
images remain outside both repositories. Baseline exited 1 on the expected
bank/bound mismatch; candidate exited 0.

| Motion | Baseline bank / bound | Candidate bank / bound | Baseline max vertex error | Candidate max vertex error |
| --- | --- | --- | --- | --- |
| Carriage lift 6 mm, rotation 20 degrees | -146 / 20 | -146 / -146 | 3.2745586775469775 mm | 2.1316282072803006e-14 mm |
| Lift 6 mm, clearing-ring rotation -90 degrees | -90 / 0 | -90 / -90 | 86.96744330392521 mm | 7.105427357601002e-15 mm |

The root reviewer opened both image files. Captures show rest, moved and
restored geometry at equal camera settings within each row. A red marker tracks
the same material vertex so the nearly symmetric clearing cover's rotation is
visible. The baseline fails to rotate that cover; the candidate rotates it
correctly. Candidate carriage movement preserves the result dial's retained
local angle. Both candidate restored meshes are vertex-for-vertex identical
to rest. This is focused pose evidence, not a claim that the whole Curta
mechanism or its deferred arithmetic is complete.

Temporary captures (not committed):

- `/tmp/machinome-retained-pose-hcPzlH/base/curta-retained-poses.png`
- `/tmp/machinome-retained-pose-hcPzlH/candidate/curta-retained-poses.png`

SHA-256 identities of reviewed content and captures:

```text
e913ada7e7f915a005d9353e36e86a3bbb74046c4d830724f081050a9996d70b  machinome/node/assembly.py
6f2c468803280c6babb680a036ccafb35a3604a2dda3216589911498ee38fe70  tests/test_retained_coordinate_delivery.py
717ccaed049ba1e394dfead734f4864e25ad3f931a4ac2cd3ac3b3a880fbe880  evidence/curta_pose_images.py
1b2d5db4fd8f53ab71b298e17678082f8a500e21f1d4acac0a74429d03a44feb  base/curta-retained-poses.png
4a86d4dffcc2b2d9f9d3f511d767fe9cdf98f08d6d435a28b825c96e921413d9  candidate/curta-retained-poses.png
```

## Verdict

Pass: no outstanding review findings. All 14 implementation tasks are complete.
Proceed with the pilot-authorized spec sync and archive. No ADR is required:
the fix restores the existing owner-qualified retained-coordinate contract.
Archival does not authorize integration into framework main or publication.
