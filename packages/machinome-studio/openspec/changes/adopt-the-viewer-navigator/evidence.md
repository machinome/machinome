# Evidence — adopt-the-viewer-navigator

The implementer fills this file in as the increments land; the reviewer reads
it instead of re-running the cycle. Every section below is required. A command
without its output, a count without its baseline, or a red step recorded only
as "failed" is not evidence.

## 0. Baseline

Worktree, branch, and the head this change starts from (the planning commit).

Record, verbatim, the invocation and the counts of:

- `npm --prefix floor/frontend run test`
- `npm --prefix floor/frontend run build`
- the Python suite
- `head -c 512 …/solid-node-viewer/WTs/viewer-navigator/solid_node_viewer/widget/dist/solid-widget.js`
  (the banner naming the viewer API) and the file's size in bytes
- `/home/asa/devel/libresolid-studio/.venv/bin/solid-node-viewer describe`
  (the version the installed package reports, which is why discovery alone
  skips today)

Name every pre-existing skip or failure and why.

## 1. The gate rises to the navigator API

### 1.1 Red

The four assertions, the command, and the failure text of each — they must fail
on the API number and the missing declaration, not on an import or a fixture.

### 1.2 Green

The same command, passing. Plus `npm --prefix floor/frontend run test`, proving
the re-vendored declaration still types the studio as it stands.

### 1.3 What was vendored

The viewer package version, viewer API version, and viewer-worktree commit the
typings were copied from, and the list of `ViewerHandle` members deliberately
left out.

## 2. The Model panel mounts the viewer's navigator

### 2.1 Red

`test_model_panel_mounts_and_disposes_the_viewer_navigator`, its command, and
the failure — `navigators` undefined because nothing calls `mountNavigator`.

### 2.2 Green

The same command passing, plus the frontend type-check, the frontend build, and
the whole `tests/test_shop_lifecycle_e2e.py` file with counts.

### 2.3 Coverage hand-off

For each scenario of the two deleted tests
(`test_model_panel_navigates_the_viewer_assembly`,
`test_model_panel_controls_the_supplied_framework_viewer`), the assertion in
2.1's or 3.1's test that carries it now. Anything genuinely dropped is named
here as dropped, with why.

## 3. The look, proved against the real bundle

### 3.1 Red

`test_model_panel_presents_the_viewer_navigator` with `SHOP_E2E_VIEWER_BUNDLE`
exported, and the failure: the computed colours are the navigator's neutral
defaults. **A skipped run is not a red run** — if it skipped, the bundle was not
supplied and this step is not done.

### 3.2 Green

The same command passing, and the same command WITHOUT the env var, showing the
skip message naming `SHOP_E2E_VIEWER_BUNDLE` and the version discovery found.

### 3.3 Pixels

A screenshot of the Model panel against the real bundle, beside one from the
planning head, and what differs. Expected: the `Show full assembly` affordance
moved from the panel header to the navigator's toolbar, and the twisty column is
one pixel narrower. Anything else is a finding, not a detail.

## 4. The deletion

The grep proving nothing still names the removed DOM, and the full suite after
the deletion — counts compared against section 0's baseline, with every
difference explained.

## 5. Findings

Anything in the code that contradicted the design, anything the implementation
forced a decision on, and anything the reviewer should look at first.
