# Codex hub discovery correction — 26 September 2026

The pilot reported that Codex was absent from the desktop hub after the
backend restoration, and requested a fix and a fresh local Studio test.
The hub's discovery roster still contained only Claude and OpenCode.

This is a direct, narrow conformance correction under AGENTS.md, based on
`5530283`, not a new backend or authority change. The existing
`shop-project-hub` requirement already requires every supported backend to be
listed as found or missing. Runtime qualification, explicit model selection,
dedicated authentication and tool policy remain unchanged.

The probe now includes Codex with the same bounded `--version` observation as
the other backends. It does not log in, start an app-server or acquire the
Studio credential store. The hub says "detected", not "ready", and omits a
model when no profile default exists rather than inventing "default". The
existing React rendering/fetch flow is preserved. The manual's hub paragraph
and the design reference reflect the displayed observation.

## Evidence

- Red: discovery tests missed Codex, the API inventory missed Codex, the
  browser timed out waiting for its row, and the documentation test rejected
  the two-backend description. An initial API attempt used the wrong Python
  on subprocess PATH; the rerun with the workspace venv reached the intended
  missing-Codex assertion.
- Green: 53 focused probe, manual, full floor API and Codex qualification
  tests passed. A subsequent run passed all six probe tests, including
  version-error/timeout handling, and both hub browser checks (8 tests).
- Frontend type check and production build passed. Vite retains its existing
  large-chunk advisory. Strict nitpicky Sphinx HTML build passed.
- Full unittest discovery: 486 tests in 266.522 seconds, OK with one optional
  workspace-installation skip. The suite emitted resource/deprecation warnings
  and its existing ignored asyncio "Event loop is closed" shutdown warning;
  exit status was zero.
- Fresh local test Studio, PID 882608, served an empty temporary catalogue at
  `http://127.0.0.1:37927/`. Its real detection results showed Claude, OpenCode
  and `codex-cli 0.157.1`, with "3 detected". The 1440×900 screenshot was
  inspected at `/tmp/studio-codex-hub-list.png`; the Codex row is visible and
  readable. The changed manual's built HTML was opened and read too.
- The test server was stopped and its listening port confirmed closed. No
  project was opened, no model called and no desktop session disturbed.

The screenshot and generated frontend/manual bundles are local verification
artifacts, not tracked source. No publication or push is authorized.
