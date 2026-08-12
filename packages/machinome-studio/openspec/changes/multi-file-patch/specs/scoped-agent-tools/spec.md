## MODIFIED Requirements

### Requirement: Filesystem write tools
The tool set SHALL provide `write_file`, `edit_file`, `apply_patch`,
`delete_file`, `move_file`, and `make_dir` for modifying project files.

`apply_patch` SHALL accept a standard unified diff describing one or more
files, SHALL derive each target from the diff's own file headers, and SHALL
apply the whole diff as a single operation that either changes every file it
describes or changes none of them. Its `path` argument SHALL be optional and,
when supplied, SHALL name the only file the diff describes.

#### Scenario: Targeted edit
- **WHEN** `edit_file` is called with an old and new string that match
  exactly once in the target file
- **THEN** the file is updated with the replacement and no other content
  changes

#### Scenario: Unified diff patch
- **WHEN** `apply_patch` is called with a unified diff against a file in the
  project
- **THEN** the file is updated to match the diff's result

#### Scenario: One patch changes several files
- **WHEN** `apply_patch` is called with a diff whose headers describe several
  files in the project
- **THEN** every described file is updated to match the diff's result and the
  call reports each file it changed

#### Scenario: One file in a multi-file patch does not match
- **WHEN** `apply_patch` is called with a multi-file diff and any file's
  context does not match its current content
- **THEN** no file in the project is modified and the error names the file,
  hunk, and line that did not match

#### Scenario: A patch creates and deletes files
- **WHEN** `apply_patch` is called with a diff that adds a file from
  `/dev/null` and removes another file to `/dev/null`
- **THEN** the new file is created with the diff's content, the removed file is
  deleted, and both are reported in the result

#### Scenario: A patch reaches outside the project
- **WHEN** `apply_patch` is called with a diff whose file header resolves
  outside the active project
- **THEN** the call is rejected and no file is modified

#### Scenario: The supplied path disagrees with the diff
- **WHEN** `apply_patch` is called with a `path` argument and a diff that
  describes a different or additional file
- **THEN** the call is rejected and no file is modified

#### Scenario: A patch uses an unsupported format
- **WHEN** `apply_patch` is called with a `*** Begin Patch` envelope rather
  than a unified diff
- **THEN** the call is rejected with an error naming the expected unified-diff
  format and no file is modified
