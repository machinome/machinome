## Why

Leonardo's cam hammer repeats a half-cosine rise/return envelope, with different
return spans for the driven hammer and the physical cam. Deepseek's independent
Leonardo hydraulic sawmill uses the symmetric instance for its feed follower.
Both need the same numeric/deferred periodic law while retaining their timings.

## What Changes

- Add one public helper, `harmonic_cam_lift`, in a cams family and flat exports.
- Specify degree timing, signed full lift, periodic seams and numeric/deferred
  arithmetic without inferring cam geometry or dynamics.
- Migrate both real consumers with Sol agents after red-first implementation;
  preserve the hammer's 80/45-degree return distinction and sawmill's double throw.
- Document and empirically validate each migration with bounded memory use.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: periodic half-cosine rise and return with a remaining base dwell.

## Impact

Independent mechanics source, tests, manual and distribution smoke; two separate
project commits. No framework/viewer changes, new dependencies, publication,
profile generation, inverse law, contact or dynamic certification. Pilot has
authorized autonomous cycles; blocked evidence is recorded rather than hidden.
