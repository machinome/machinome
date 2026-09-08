## 1. Prove the endpoint red first

- [ ] 1.1 Add a pure unit contract that 360 frames produce 360 inclusive
  positions and a guarded single-frame course.
- [ ] 1.2 Add browser coverage that scrubbing a twelve-hour document to its
  final position reads `12:00:00`.
- [ ] 1.3 Add browser coverage that a bounded driver's readout accepts an exact
  design-unit number, including outside slider travel.

## 2. Correct the timeline

- [ ] 2.1 Centralize the inclusive timeline step and use it when constructing
  the animation slider.
- [ ] 2.2 Replace bounded sliders' passive readouts with directly editable
  numeric fields that use the existing driver conversion path.
- [ ] 2.3 Document both viewer corrections in the unreleased changelog.

## 3. Validate and deliver

- [ ] 3.1 Run widget unit tests, typecheck, bundle build and focused browser
  tests.
- [ ] 3.2 Validate, sync and archive the OpenSpec change, then commit the
  completed record.
