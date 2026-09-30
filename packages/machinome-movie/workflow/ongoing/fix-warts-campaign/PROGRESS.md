# Fix-warts campaign — progress

| when (2026) | what | evidence |
|---|---|---|
| 30 Sep | `react-stage` fast-forwarded into `main` at the pilot's direction ("merge to main"); `npm ci` in the primary checkout; the editable `machinome-movie` re-pointed at `python/` of the primary checkout; Node suite on `main` green from the shared memo | `main` e30b05f |
| 30 Sep | Branch `fix-warts` opened from `main` e30b05f; this plan; the triage of the warts settled without a cycle written into `warts.md` | this commit |
| 30 Sep | Wave 1 opened: worktrees `WTs/narration-end-anchor`, `WTs/speech-key-lookup`, `WTs/pose-repaints`, each from e30b05f, each on an opus agent | this repository |
| 30 Sep | `speech-key-lookup` done as a narrow adjustment (no spec states the key's source): `keyFiles()` gives the checkout's `.env` then the primary work tree's through Git's common directory, environment first, refusal names every place, the key never enters the process environment; pure tests over four throwaway layouts, three pipeline tests with a provider double and fake keys; Node 299 passed (299), 0 from the memo, 606 s (every slow key changed); Python 186 passed. Reviewed and merged | 5b5cd77, merge 1d86942 |
