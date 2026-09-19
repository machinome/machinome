# Design

Validate and copy both input vectors before mutating the viewer. Reject
non-finite/non-three-dimensional vectors, coincident camera/target and use after
disposal. Reuse existing bounds-derived clipping and mount-time up/FOV. Update
orbit target and render before returning; do not remount or refetch geometry.
`view()` remains a detached snapshot. A browser screenshot after the call
captures the new view; the operation does not claim a cross-GPU raster identity.

The existing `setTime()` already poses and renders synchronously. Together the
two host operations supply the posed-film use case without a new renderer API,
exposing Three.js, or modifying machine playback. Validate the vectors in unit
tests and exercise the actual mount, view return, time, visibility and pixels
through the originating project's headless filming workflow.
