## Why

The Curta Type I result and turns carry sliders seat against their source guide faces. At nominal planar contact, the new exact-common guard called a point about 3–7 × 10⁻¹⁵ mm from those faces strictly interior because zero-tolerance OCCT classification rounded it to IN on both sides. That falsely refused an otherwise empty native common. The originating positioning-ball/frame false-empty still requires refusal.

## What Changes

- Require an alleged shared-interior point to be resolved beyond each native face's own tolerance before it can contradict an empty Boolean.
- Refuse a failed distance/tolerance check rather than silently calling it outside.
- Preserve the existing zero-tolerance classification, finite search, positive native commons, and zero-volume contact policy; introduce no overlap epsilon or inferred volume.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `test-framework`: narrow the empty-exact-common contradiction witness to a reliably interior point, so Curta's planar carry guide contacts remain ordinary contacts while its positioning ball/frame true overlap still refuses.

## Impact

`machinome/exact.py`, focused exact tests, the existing exact-intersection reference and decision record. No viewer or project source change.
