# Root review

## Planning gate — 29 September 2026

Approved for implementation under the pilot's delegated film-production
commission, after Sol's proposal and root's adversarial review. This is not
a claim that the pilot individually reviewed these interface details.

The originating Leonardo finding is measured, not inferred from the roadmap:
`videos/demo-incremental-rendering/evidence.md` records 80 captures in 31.67 s,
an identical rerun with zero captures in 1.70 s, and a one-line interior-title
edit causing 80 captures in 32.11 s. Root independently hashed all 80 baseline
and edited PNG pairs: only frames 21–42 changed. Root also verified both MP4
hashes and inspected a contact sheet decoded from the edited MP4. The fixture
shows the actual sawmill and readable overlays, not a substituted model.

The baseline and edited MP4 hashes are respectively
`997b94bd98e54c02a6eb2c6e4e8c31d5a8d25a10728d5423504938ebd2ea3525` and
`50c674071bf64c84856f6978b38bca1eb0f80ab46822d1f4f36bf510fe0b2025`.
Their paths and complete source/viewer/export hashes are in the project
record; preserved artifacts remain in its ignored `_build/evidence/`.

Review refinements incorporated before this planning commit:

- Whole-shot granularity includes the incoming join. The measured fixture
  should reuse A+D (40 frames) and recapture B+C (40), not promise prefix-only
  reuse or the 22-frame observed pixel minimum.
- Global output instants and progress, outgoing continuation, actual reached
  media and measured word inputs determine validity. Nonvisual preload lists
  and unrelated clip extraction ranges are not common dependencies.
- The initial mount is conservatively common. First-shot edits can invalidate
  all shots; no universally minimal cache claim is made.
- Complete generations are attested atomically; failed captures/encodes must
  not masquerade as complete films or destroy a prior good output.
- Skipping cached poses can alter browser raster history. Every incremental
  PNG must equal a separately cold result exactly, including source/text and
  a fractional-grid case; tolerance relaxation is not an acceptable fix.
- Implementation starts with a behavioral failing test against the existing
  renderer. A missing helper import alone does not prove the originating bug.

No implementation or performance benefit has been approved as proven yet.
The apply agent owns focused red/green tests; the evidence agent then renders
real consumers under a separate browser lease; root verifies before closure.
