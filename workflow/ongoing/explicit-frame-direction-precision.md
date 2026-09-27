# Explicit frame direction precision

Status: provisional pre-spec intent, 27 September 2026. The pilot ratified the
numeric contract below; this note is evidence and intent, not implemented
behavior. The OpenSpec change will govern it.

Curta's source-derived zero-positioning-pin triad loses sub-1e-9 direction
components during frame resolution. Its strict independent moving-pose test
fails despite 6/6 geometric tests passing; removing frame snap diagnostically
passes the unchanged comparison. See `../warts.md` for exact directions.

Retain full normalized/projected/cross-product direction precision only when
both x and z were supplied explicitly (including expressions/callables).
Stating x while omitting default z remains the old snapped path; explicit
z=(0,0,1) is distinct from omitted z for this choice. Track that distinction
internally without an author option. Keep omitted-x principal derivation,
zero/parallel rejection and final mate rotation/axis snap unchanged. The public
resolved read must be the same basis mates actually compose, not a display fix.

Framework docstrings/manual and separately owned Studio API documentation must
state this narrow distinction. No global snapping redesign, new arguments,
string conventions or viewer schema belongs here. Caller tests and files stay
project-owned; root adversarial review precedes synchronization/archive.
