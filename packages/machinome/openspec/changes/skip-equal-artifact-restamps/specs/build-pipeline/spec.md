## ADDED Requirements

### Requirement: Exact-equal restamps preserve the standing artifact identity

When the currency timestamp setter observes that an artifact's current integer
`st_mtime_ns` exactly equals the requested integer timestamp, the system SHALL
leave the artifact's timestamps unchanged instead of issuing a redundant
timestamp write. It SHALL use exact equality, without tolerance or rounding.
When the timestamps differ, it SHALL retain the existing best-effort restamp
attempt, including safe behavior on a coarse filesystem or `OSError`.

Suppressing a redundant timestamp write SHALL NOT certify source or artifact
validity. The system SHALL retain compatible-recipe checks, source fingerprints,
retained-source content verification, current/compatible legacy record rules,
generation checks and full artifact identity validation. A content-proven
fallback SHALL still record the current digest, fingerprint and producer recipe
where required, even when the artifact's timestamp needs no write. Other writers
or same-size restored-mtime artifact changes SHALL retain their existing
invalidation/refusal behavior.

#### Scenario: Legacy record refresh preserves an already pinned artifact

- **WHEN** an artifact already has the exact desired mtime, its matching legacy
  digest-only record requires content verification and current-record upgrade,
  and a consumer has already pinned its identity with `ArtifactSnapshot`
- **THEN** source verification succeeds and the currency record is upgraded with
  the correct current digest/fingerprint/recipe
- **AND** that fallback does not alter the artifact's timestamps, bytes or
  standing identity, so the original snapshot still validates

#### Scenario: Equal content below an unchanged maximum refreshes only currency

- **WHEN** contributor metadata changes with retained source content unchanged,
  the aggregate maximum and artifact mtime remain exactly equal, and the
  fingerprint mismatch enters content verification
- **THEN** the current fingerprint is recorded after the matching content proof
- **AND** the system does not issue a redundant artifact timestamp write or
  invalidate a previously pinned artifact through that refresh

#### Scenario: A genuinely changed desired mtime still moves the artifact

- **WHEN** compatible retained sources prove current but their desired maximum
  mtime differs from the artifact's mtime
- **THEN** the system attempts the same integer-nanosecond restamp and records
  current source currency without re-deriving unchanged geometry
- **AND** if filesystem resolution prevents exact equality, content-proven
  currency remains valid for that check without a retry loop

#### Scenario: Matching artifact mtime never bypasses source or recipe proof

- **WHEN** artifact mtime already equals the desired maximum but retained source
  content disagrees, the producer recipe is incompatible, or required currency
  evidence is missing, malformed or unreadable
- **THEN** timestamp equality does not certify current geometry and the existing
  refusal/rebuild behavior remains in force

#### Scenario: Independent artifact mutation still invalidates the pin

- **WHEN** a pinned artifact is changed or replaced independently of currency
  refresh, including a same-size edit with restored mtime
- **THEN** full identity validation and the existing weaker-cache invalidation
  still reject or recompute from the changed artifact

#### Scenario: A timestamp-setting error remains best effort

- **WHEN** the timestamp setter cannot stat or restamp the artifact because the
  filesystem raises `OSError`
- **THEN** it retains the existing non-throwing best-effort reporting behavior
- **AND** no new content proof, artifact creation or weakened consumer identity
  validation is inferred from that error
