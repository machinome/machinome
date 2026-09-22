# OperatingCurta repeated bind: viewer-specific rejection

The framework's `_PathValue.bind` one-entry result reuse was measured on
OperatingCurta as a useful Python change. This does **not** imply the viewer
needs the same change. Viewer `PathValue.bind` already compares its graph-
referenced input leaves on every later bind and, when they are unchanged,
returns the prior successful bound root before walking any expression nodes.
`ExpressionPath` also retains the same path across adjacent pieces. The
viewer `Run` additionally retains a successful finite Bound path across
searches under the separate standing-bind cycle.

A temporary, removed probe counted binds during eight actual default
`dt=1/240` crank ticks after setting selector 1 on the pinned pre-ball
production OperatingCurta manifest SHA256
`03099125a8642ee28c9dcfe73e2c6a82c3538794ba36ba0300eb738d5049ede9`.
The in-thread viewer run admitted 6° of crank and held 213 coordinates.
On reserved CPU 15, it made 353,850 `PathValue.bind` calls: 11,994 first
binds, 341,214 existing clean-input early returns (96.4% of all binds),
and 642 changed-input later binds. The clean returns already avoided
5,865,290 whole-postorder node visits. The existing comparison scanned
600,267 referenced leaves, averaging 1.70 per bind. Total expression
resolutions over the measured ticks were 8,184,129. The instrumented run's
2.821 process-CPU seconds is a diagnostic observation, not an uninstrumented
before/after benchmark.

Thus a Python-shaped “reuse successful result on unchanged input” patch
would duplicate current viewer behavior. Skipping even the leaf comparison
would require a trustworthy value/presence provenance token; the viewer's
piece scopes are freshly built objects, and object identity cannot certify
unchanged values, getters, signed zero, or first-error order. No such token
is present in the current public or internal contract. This candidate is
rejected; no viewer source, timestep, operators, samples, cache lifetime,
API or document version changed. The temporary probe and external-project
test were removed before this evidence was committed.
