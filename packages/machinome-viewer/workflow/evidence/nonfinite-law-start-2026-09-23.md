# A non-finite law start can enter the running bank

This is a separate finding encountered while testing exact absolute
endpoints. It was initially unratified; the viewer now has the separate
ratified `refuse-nonfinite-running-law-start` change, whose implementation
remains separate and pending. It is not an endpoint-correction requirement
or a claim about the current Curta's declared paths.

On viewer main `b976a172a7964b269183eaee289c8cf26668cd58`, a public
version-5 running document with initial `feed=0.2`, `slide=0`, and one
`law(['feed'], ['slide'], 'sqrt(0.1 - feed)')` was loaded and given the
zero-duration request `move('feed', { to: 0.1 })`. The law is invalid at its
authored start because `sqrt(0.1 - 0.2)` is NaN. The command returned
`completed` at tick 0 and `state()` returned `{feed: 0.1, slide: NaN}`.
The same result was observed in the isolated endpoint worktree before
adding a refusal control. A separate branch-throwing authored-start control
does refuse atomically, so this finding is specifically about numeric NaN.
This manually assembled document is viewer-accepted but is not claimed to
be producer-exportable with its invalid initial law value. The separate
change also has a valid-rest companion that starts at `feed=0` and moves
to `0.2` to exercise the first invalid endpoint from a valid state.

The minimal document's variable content is:

```json
{
  "format": "machinome-export",
  "version": 5,
  "drivers": {"feed": {"default": 0.2, "range": null, "unit": null, "dtype": null, "scale": null}},
  "instructions": {},
  "program": {
    "identity": "nonfinite-sqrt-start",
    "clock": "time",
    "coordinates": {
      "feed": {"kind": "input", "initial": 0.2, "domain": null},
      "slide": {"kind": "coordinate", "initial": 0, "unit": null, "domain": null}
    },
    "intermediates": [],
    "edges": [{"kind": "law", "needs": ["feed"], "gives": ["slide"],
      "description": "square-root carriage", "stated_by": "Bench",
      "expressions": ["sqrt(0.1 - feed)"], "affine": [false], "plans": [null]}],
    "spans": {},
    "sources": {"feed": ["feed"], "slide": ["feed"]},
    "limits": {"crossing_tolerance": 1e-12, "subdivisions": 64,
      "bisection_rounds": 64, "max_crossings": 1000, "agreement": 1e-9}
  }
}
```

Baseline command: `npx vitest run src/run/nonfinite-baseline-diagnostic.test.ts`
in the endpoint worktree, with the temporary diagnostic importing the
`b976a17` primary `Run` and `loadProgram` source by absolute path. It exited
0 and printed `baseline-main-b976a17 completed 0 { feed: 0.1, slide: NaN }`.
That temporary test was removed; the document and result above preserve the
reproduction. No numerical-error semantics were changed in the endpoint
cycle.
