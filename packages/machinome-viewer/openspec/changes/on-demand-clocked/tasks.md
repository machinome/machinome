## 1. Red first

- [ ] 1.1 Record the base: `npx vitest run`, `npx tsc --noEmit` at `main`
      94cfcc0, and the API 28 bundle built in this worktree. Never install
      `node_modules`.
- [ ] 1.2 `options.test.ts` (red: the helpers do not exist):
      - `resolveOptions` still admits on-demand only with the four
        conditions (pinned, green today);
      - `assertOnDemandDocument` accepts a clocked document with and
        without instructions, a posed document without instructions, and
        anything under continuous; refuses a program naming the program
        and the mode, a program carrying `clocked` as a program, and a
        posed document with instructions with today's message;
      - `assertFrameLoop` is silent under continuous and throws under
        on-demand naming the verb and `'on-demand'`.
- [ ] 1.3 `version.test.ts`: the API is 29 (red at 28).
- [ ] 1.4 `tests/test_widget_e2e.py`, a class over the calculator fixture
      (`export_calculator`) and the regulator fixture, run red against the
      API 28 bundle:
      - `test_a_clocked_machine_mounts_on_demand_and_poses_by_restore`:
        on-demand mount; capture at the origin; `restore` of a bank with
        the crank at 180 then `setView(viewer.view())`, capture; restore
        the origin, restore the mid bank again, capture; mid differs from
        origin, the two mid captures are equal; `state()` equals the bank
        given; a capture after `restore` alone equals the one after
        `restore` + `setView`.
      - `test_on_demand_requests_answer_as_continuous`: the same requests
        on an on-demand and a continuous mount give equal results.
      - `test_trigger_is_refused_on_demand`: names `on-demand`; the bank
        and the capture are unchanged.
      - `test_a_clock_does_not_play_on_demand`: regulator, `setClockPlaying(true)`
        refused naming `on-demand`, `clockPlaying()` false,
        `setClockPlaying(false)` accepted, `move(clock, {by: 0.5})` moves
        the clock.
      - `test_an_on_demand_clocked_mount_shows_no_control`.
      - `test_a_program_is_still_refused_on_demand`: the running fixture
        refused naming `program` and `on-demand`.
      Update the API pins in `test_bundle.py`, `test_widget_e2e.py` and
      `test_documentation.py` to 29.

## 2. Implement

- [ ] 2.1 `options.ts`: `assertOnDemandDocument` and `assertFrameLoop`
      (design D1, D4).
- [ ] 2.2 `viewer.ts`: the mount and `manifestChanged` call
      `assertOnDemandDocument`; `machine().trigger` and
      `setClockPlaying(true)` call `assertFrameLoop`; the `renderMode`
      doc comment.
- [ ] 2.3 `package.json`: `machinomeViewerApi` 29; `version.test.ts`
      records why.

## 3. Document

- [ ] 3.1 `docs/reference/mount.rst` (`renderMode`: accepts a clocked
      machine, refuses a program and a posed document with instructions,
      draws no full-screen control), `docs/reference/clocked.rst` (the
      on-demand rules for `move`, `restore`, `reset`, `trigger`,
      `setClockPlaying`, and redrawing with `setView(viewer.view())`),
      `docs/compatibility.rst` (API 29), `docs/embedding.rst`.
- [ ] 3.2 `CHANGELOG.md`: an `Unreleased` section above 0.7.1 naming API
      29; adjust the pins in `tests/test_documentation.py` that forbid
      one (the pilot's ruling of 29 September 2026: a change writes its
      changelog entry when it lands).
- [ ] 3.3 ADR-077 under `workflow/adrs/EXPORT/` and its index line.

## 4. Validate and close

- [ ] 4.1 `npm test`, `npm run typecheck`, `npm run build`, then the whole
      Python suite, one at a time, on the final content.
- [ ] 4.2 `evidence.md`; sync the delta spec, `openspec validate --strict`,
      archive; one implementation commit in this repository only.
