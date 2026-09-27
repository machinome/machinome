# External-wrapper cache identity

Status: provisional pre-spec note, 27 September 2026. The pilot ratified the
narrow direction below; this note is evidence and intent, not a spec or an
implemented capability. The OpenSpec change `external-wrapper-cache-identity`
will own the requirements and implementation plan.

Curta's two `FittedDialType2` wrappers in `simulation/dial_fits.py` and
`simulation/dial_frames.py` import the same STEP, retain the same inherited
adjustment, and differ by the framed wrapper's `axle` frame and source closure.
Both claim one cache path, alternately invalidating it. See `../warts.md`
for measured mtimes, digests and the interrupted build.

Use defining Python source relative to the artifact-owning project root,
together with qualname and the existing parameters, only for external-file
wrappers. Do not hash absolute checkout paths or import aliases. Keep ordinary
Python canonical identity bytes and generated site/fresh-mate specializations
unchanged. Keep source currency, recipe currency and artifact layout unchanged.

The artifact source already must belong to a discoverable project for full
node construction. A defining wrapper outside a manifest is not newly refused:
its source can be expressed relative to that existing artifact project root,
including `..`. This does not add no-manifest project support or change source
containment checks.

Proof must include real differing cached geometry, two current artifacts after
a terminating build, relocation/import-alias stability, parameter/name and
ordinary-node invariants, specialization identity, and unchanged freshness.
STEP-to-STL caching is the originating case; synthetic differing-adjustment
fixtures must also cover STEP and STL's shared wrapper-origin failure. No
mechanical-contract or viewer work belongs to this cycle.
