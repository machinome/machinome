# React stage campaign — progress

| when (2026) | what | evidence |
|---|---|---|
| 30 Sep | Pilot's new goal after inspecting *Cut and Advance*: implement the stage, the template owns the screen, no hard-coded chrome, source beside the model, then a new film | this conversation; `plan.md` quotes it |
| 30 Sep | Branch `react-stage` opened from `declarative-python` 8dd2474; toolchain committed (React 19.3.0, react-dom, esbuild 0.28.2, TypeScript 7.0.2, vitest 5.0.3, jsdom 30.1.1, exact) | 5dae43f |
| 30 Sep | Worktree `WTs/one-runner` (branch `one-runner`) opened from 5dae43f; cycle A running on an opus agent | this repository |
| 30 Sep | The contract written: `docs/movie-document.md` for `machinome-movie/0.2`, `schema/machinome-movie-0.2.json` (valid against draft 2020-12), this plan | this commit |
| 30 Sep | Leonardo: `videos/cut_and_advance/spec.md` rewritten as version 2 (the project template, source in three chapters, the Jobs element, the target `movie.py`) | Leonardo 7c9fefc |
| 30 Sep | Worktree `WTs/declarative-stage` (branch `declarative-stage`) opened from be98523; cycle P running on an opus agent beside cycle A; editable install of `machinome-movie` points at it while it runs | this repository |
| 30 Sep | Cycle A `one-runner` ratified (planning 82ba537, implementation 8b1202b; vitest, two projects, one Chromium and one asset server per run, the verdict and artefact memos in `.test-memo/`, ADR-003; 218 tests cold 340 s, warm 4.9 s with 96 passed from the memo) and merged into `react-stage` | c1040c5, `openspec/changes/archive/2026-09-30-one-runner/evidence.md` |
| 30 Sep | Merged tree after A: Node suite cold 218 passed (340 s) | `.test-memo/` in `WTs/react-stage` |
| 30 Sep | Cycle P `declarative-stage` ratified (planning 121a86c, implementation f5eb59f; ADR-005; 185 pytest) with the orchestrator's rulings on its nine contract findings (1782192: a dot bounds a token, `line=` on an emphasis, merged set props, draw is an entrance only; 186 pytest) and merged into `react-stage` | b109fd3, `openspec/changes/archive/2026-09-30-declarative-stage/evidence.md` |
| 30 Sep | Leonardo spec: the coupling emphasis names line 415 | Leonardo aa3f762 |
| 30 Sep | Between P and S the Node suite of `react-stage` is red on the removed 0.1 schema and fixtures, as P's wart 4 records; cycle S starts from b109fd3 | this commit |
| 30 Sep | Worktree `WTs/react-stage-runtime` (branch `react-stage-runtime`) at 502ef71; cycle S running on an opus agent | this repository |
| 30 Sep | Leonardo: `movie.py` version 2 written from the spec and evaluated to 0.2 (5 chapters, 12 shots, sets `leonardo` and `leonardo-split`, element `jobs`, emphasis on lines 413–415 by line 415, 425–435, 472–486); `stage.tsx` a placeholder until the runtime lands | Leonardo (commit after aa3f762) |
