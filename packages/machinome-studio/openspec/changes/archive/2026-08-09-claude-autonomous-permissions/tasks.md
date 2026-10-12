## 1. Profile policy

- [x] 1.1 Extend the resolved runtime model and strict profile validation with
  the required Claude-only `manual` or `autonomous` permission setting.
- [x] 1.2 Declare `permission = "autonomous"` for every shipped Builder and
  Fordesmac Claude role.
- [x] 1.3 Add red-first profile validation tests for missing, invalid, and
  unsupported-backend permission declarations.

## 2. Claude launch behavior

- [x] 2.1 Translate the resolved Claude permission policy to an explicit
  `--permission-mode` argument while preserving safe mode and the declared
  `--tools` list.
- [x] 2.2 Add red-first fake-CLI command tests for autonomous and manual role
  session launch arguments.

## 3. Durable documentation and validation

- [x] 3.1 Draft and accept ADR 0015 documenting the profile-owned autonomous
  policy, available-tool boundary, and absence of OS sandboxing.
- [x] 3.2 Update the architecture overview and ADR index for the accepted
  policy.
- [x] 3.3 Run focused profile/backend tests, the relevant full suite, and
  OpenSpec validation; record any environmental limitation honestly.
