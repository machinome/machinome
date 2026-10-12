## Context

`setView` (API 21, change `scripted-camera`, applied and not yet archived)
calls `scriptedView(view)` in `camera.ts`, which checks and copies `camera`
and `target`, then `applyFrame(next)` and `renderer.render`. `applyFrame`
computes near and far with `frameBounds(visibleBounds(scene), camera.fov,
view, resolved.up)` and copies `framed.up` into `camera.up`, so every
framing (mount, `setRoot`, a republish that moved the root, `setView`)
writes the **mount-time** up back. `camera.fov` is set once from
`resolved.fov` when the `PerspectiveCamera` is built. `captureView()`
returns `{camera, target}` as fresh `THREE.Vector3`s, and `View` is an
alias of `ViewerView`, the same type `resolveOptions` stores the mount's
`view` option in and `frameBounds` takes.

`OrbitControls` (three 0.156.1) computes, in its constructor's `update`
closure, the quaternion that maps `object.up` to +Y and never recomputes
it. Changing `camera.up` afterwards still renders the new roll (the
controls' `update()` round-trips the offset through that quaternion and its
inverse, then calls `lookAt`, which reads the current `camera.up`), but a
pointer orbit keeps turning about the mount-time axis, and the polar clamp
(`spherical.makeSafe()`) is taken about that old axis too.

The part surface holds the controls as its `orbit` collaborator, which it
uses only for `orbit.enabled` (`PartSurfaceHost.orbit: { enabled: boolean }`).

## Goals / Non-Goals

**Goals:**

- A host changes up direction and field of view with the same call and the
  same guarantees as camera and target: validated first, drawn before
  returning, no reload, no change to machine state.
- What the host set is what it reads back, and what every later framing
  keeps.

**Non-Goals:**

- No interpolation: the host computes each frame's values, as it already
  does for camera and target.
- No orbit paths and no "frame this part" operation.
- No change to the mount options `up` and `fov`, including their current
  leniency (see Risks).
- No orthographic camera, zoom, or focal-length spelling.

## Decisions

### D1. The shapes

```ts
export interface ViewInput {
  camera: VectorInput;
  target: VectorInput;
  up?: VectorInput;
  fov?: number;
}
export interface View {
  camera: THREE.Vector3;
  target: THREE.Vector3;
  up: THREE.Vector3;
  fov: number;
}
```

`View` stops being an alias of `ViewerView`: the mount option `view` and
`frameBounds` keep `ViewerView` (`{camera, target}`). Passing a `view()`
snapshot to a later `setView` restores all four; passing it as a mount's
`view` option restores camera and target only, as today, and the mount
options `up` and `fov` remain the mount-time spelling of the other two.
`fov` is the vertical field of view in degrees, the `PerspectiveCamera`
meaning and the unit of the mount option.

### D2. Omitted means unchanged

The viewer keeps `up` and `fov` as its own state, initialised from the
resolved mount options. An omitted `up` or `fov` keeps the current value.
`applyFrame` passes the current `up` to `frameBounds` rather than
`resolved.up`, and `camera.fov` is set before `frameBounds` runs, so near
and far are derived at the new field of view. `setRoot`, `manifestChanged`
and `reload()` therefore keep the adopted values.

### D3. Refusals, all before any mutation

Extending `scriptedView`, which already refuses non-finite and
non-three-dimensional `camera`/`target` and coincident endpoints:

- `up` given and not three finite numbers: `setView up must contain three
  finite coordinates`.
- `up` given and zero-length: `setView up must not be zero`.
- `up` given and parallel or anti-parallel to the view direction
  (`target - camera`): refused when the sine of the angle between them is
  below 1e-6, `setView up must not be parallel to the view direction`.
  three.js's `lookAt` has no defined roll there.
- `fov` given and not a finite number with `0 < fov < 180`:
  `setView fov must be a finite number of degrees between 0 and 180,
  exclusive`.
- A disposed viewer: as today.

When `up` is **omitted**, the parallel check is not applied to the retained
up. API 21 to 27 accept a camera straight above its target with the default
Z-up, and three.js resolves that case with its own perturbation; refusing
it now would break calls that work today. The reference states the
difference.

`up` is stored and reported as given (a copy, not normalised), so a host
reading back the view compares equal to what it sent; `lookAt` uses only
its direction.

### D4. Orbit follows the adopted up

When an adopted `up` differs in direction from the one the current orbit
controls were built with (normalised vectors differ), the viewer disposes
those controls and builds new `OrbitControls` on the same camera and
canvas, carrying over `rotateSpeed`, `target` and `enabled`. The part
surface's `orbit` collaborator becomes a stable object whose `enabled`
getter and setter delegate to the current controls, so a gesture that
suspends orbiting suspends whichever controls exist. A call with the same
direction, or with `up` omitted, replaces nothing, so a film that holds up
constant builds no controls per frame. `dispose()` disposes the current
controls. In on-demand mode no pointer orbits, but the replacement keeps
the two modes on one code path.

### D5. Reading back

`view()` returns `{camera, target, up, fov}` with fresh vectors each call,
so editing a snapshot never moves the viewer, as the existing requirement
demands.

## Risks / Trade-offs

- [Replacing orbit controls mid-session] -> damping is off in this viewer
  and no gesture state is carried across a scripted call; a gesture in
  progress when a host calls `setView` with a new up loses its orbit drag,
  which a host changing the view under a maker's pointer already does.
- [Mount options stay lenient] -> the mount accepts a zero or non-finite
  `up` and silently falls back to 50 degrees for an invalid `fov`. Refusing
  at mount would change a published contract and is not what the film
  needs; recorded as a finding in evidence rather than changed here.
- [Parallel check only when `up` is given] -> two rules for one degenerate
  case. The alternative, refusing on the retained up, breaks existing
  calls; stated in the reference.

## Migration Plan

Additive for callers: a `setView` without `up` and `fov` behaves as before,
except that a later `setRoot` no longer resets a mount-time up it never
changed (the values are equal). `view()` gains two fields; hosts that read
`camera` and `target` are unaffected.

## Open Questions

None.
