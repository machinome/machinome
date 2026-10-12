## ADDED Requirements

### Requirement: The scoped commit tool injects the project screenshot best-effort
Immediately before a floor-mediated Git commit, `git_commit` SHALL request a
best-effort refresh of `<project>/screenshot.png`, SHALL attempt to stage that
exact path when it is a regular non-symlink file, and SHALL then invoke the
requested Git commit. Rendering, comparing, publishing, or staging the
screenshot SHALL NOT prevent the commit attempt or replace its Git result.

#### Scenario: The refreshed screenshot changed
- **WHEN** `git_commit` refreshes a changed `screenshot.png` and can stage it
- **THEN** the requested commit includes `screenshot.png` together with the paths the agent staged

#### Scenario: The screenshot is unchanged
- **WHEN** `git_commit` refreshes a screenshot whose bytes are unchanged
- **THEN** it performs the requested commit without manufacturing a screenshot diff

#### Scenario: Screenshot rendering fails before commit
- **WHEN** `git_commit` cannot render a new screenshot
- **THEN** it still invokes the requested Git commit and returns that Git operation's result

#### Scenario: Screenshot staging fails before commit
- **WHEN** `git_commit` cannot safely stage `screenshot.png`
- **THEN** it still invokes the requested Git commit and does not stage another path in its place

#### Scenario: The screenshot path is absent
- **WHEN** `git_commit` finds no regular project-root `screenshot.png` after its refresh attempt
- **THEN** it performs the requested Git commit without adding an image
