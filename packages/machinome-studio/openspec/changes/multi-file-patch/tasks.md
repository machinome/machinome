## 1. Multi-file patch application

- [ ] 1.1 Add red-first tests for a diff describing several project files, a
  per-file result report, and an unchanged tree when one file's context does
  not match; record the expected red failures.
- [ ] 1.2 Add red-first tests for creation from `/dev/null`, deletion to
  `/dev/null`, a header resolving outside the project, and a `path` argument
  that disagrees with the diff.
- [ ] 1.3 Implement parse-and-verify-then-write: build a per-file plan from
  each file header, resolve every path through the containment gate, verify all
  plans against current content, and only then create, write, and delete.
- [ ] 1.4 Make `path` optional in the tool schema and validate it against the
  diff's single file when it is supplied.

## 2. Agent-facing contract

- [ ] 2.1 Update the `apply_patch` docstring and `unified_diff` parameter
  description to state multi-file support, `/dev/null` creation and deletion,
  all-or-nothing application, and the still-unsupported `*** Begin Patch`
  envelope.
- [ ] 2.2 Confirm the existing tool-documentation test still holds for the
  changed schema.

## 3. Validation and completion

- [ ] 3.1 Run the scoped-tool tests and the complete shop test suite.
- [ ] 3.2 Run strict OpenSpec validation.
- [ ] 3.3 Sync the delta specification into the baseline specs, archive the
  change, and commit the completed implementation record.
