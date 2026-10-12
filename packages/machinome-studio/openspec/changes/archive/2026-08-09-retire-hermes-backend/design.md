## Context

Hermes entered the shop as the first proof that orchestration could be
backend-neutral. Its implementation now owns a substantial ACP client,
Hermes-version-specific steering and cancellation behavior, and a bespoke fake
server. OpenCode subsequently supplied the desired multi-provider route with a
cleaner server/session integration. The pilot has decided that Hermes belongs
to a different tool class and should no longer be maintained as an
`AgentBackend`.

The retirement crosses the adapter registry, CLI, strict profile schema,
built-in profile data, tests, product specifications, runtime guidance,
reference architecture, reference design, and ADR history. Historical ADRs,
archived OpenSpec changes, and sprint evidence remain historical records.

## Goals / Non-Goals

**Goals:**

- Make Codex, Claude, and OpenCode the complete supported backend set.
- Remove all executable Hermes/ACP integration and its dedicated test surface.
- Remove Hermes policy from the strict profile schema and shipped profiles.
- Make active specs and documentation accurately describe the remaining
  system.
- Preserve the historical rationale while recording that ADR 0007 is no longer
  operative.

**Non-Goals:**

- Redesign Hermes as another kind of shop tool.
- Change the portable `AgentBackend` protocol or the remaining adapters.
- Add OpenCode tables to profiles; ADR 0012's bounded compatibility exception
  remains in force.
- Rewrite archived changes, sprint records, or empirical traces.

## Decisions

1. **Remove Hermes rather than retain a compatibility stub.** The CLI and
   factory will reject `hermes` as unsupported. A stub would preserve a false
   product promise and keep Hermes visible in validation and documentation.
   Continuing to maintain the ACP adapter was rejected because its cost no
   longer buys a distinct provider capability.

2. **Keep the portable backend seam.** Hermes proved the seam and can be
   retired without collapsing it. Codex, Claude, and OpenCode continue to
   implement the same orchestration boundary. Reworking Hermes to fit that seam
   was rejected because the pilot considers it a different class of tool.

3. **Make Codex and Claude the profile-explicit policy set.** OpenCode retains
   its existing adapter-owned compatibility policy; Hermes tables and
   Hermes-only validation branches disappear. This reduces the manifest
   contract without altering the OpenCode exception.

4. **Preserve history but remove active claims.** ADR 0016 supersedes ADR 0007
   and amends ADRs 0006 and 0011. Historical ADR bodies, archived OpenSpec
   changes, and sprint evidence remain intact; baseline specs, architecture,
   guidance, README content, and reference design are updated to current truth.

5. **Use negative contract tests for the breaking removal.** Before deleting
   the implementation, tests will assert that CLI/factory/profile surfaces no
   longer accept or require Hermes. Those assertions provide the red state;
   deleting Hermes code and policy turns them green.

## Risks / Trade-offs

- **Existing automation passes `--backend hermes`** → The CLI fails clearly;
  operators must select Codex, Claude, or OpenCode.
- **Removal accidentally weakens the generic backend seam** → Retain and run
  the shared orchestrator tests plus all remaining backend acceptance suites.
- **Active Hermes references survive in less obvious surfaces** → Search the
  tracked tree after implementation, classifying only historical records as
  intentional survivors.
- **Deleting fixture-heavy tests hides unrelated coverage** → Remove only the
  Hermes acceptance class and fixture, and run the complete test suite to catch
  shared coverage loss.

## Migration Plan

1. Add failing contract tests for the supported backend set and profile schema.
2. Remove Hermes selection, registry loading, adapter code, profile tables, and
   Hermes-only tests/fixture.
3. Update baseline specs, runtime guidance, README, architecture, reference
   design, and ADR records.
4. Run focused tests, the complete suite, OpenSpec validation, and a tracked
   reference scan.
5. Sync delta specs, archive the change, and commit the completed record.

Rollback is a revert of the implementation commit; historical material remains
available to recover the removed adapter if the product decision changes.

## Open Questions

None. A future Hermes integration would require a new decision describing the
tool class and boundary that actually fits it.
