## ADDED Requirements

### Requirement: A repeated constraint bound may reuse exact standing values

For a determined running Bound search, the viewer SHALL reuse previously evaluated standing expression nodes only after a successful search on the same run, same compiled graph generation and same moving-name set, with unchanged referenced input presence and IEEE-754 values and finite numeric search scope. It SHALL evaluate every moving node at the new search's first sample and every later prescribed sample through the existing operators in the existing order. It SHALL not change tick size, search fractions, admission, stop, committed bank, snapshot/restore or replay.

#### Scenario: Repeated standing inputs across ticks
- **WHEN** adjacent searches bind the same Bound with identical finite standing inputs and moving-name set
- **THEN** standing nodes are reused, moving nodes run at the first point, and ordered sampled levels and final bank match uncached execution exactly

#### Scenario: Standing value or presence changes
- **WHEN** a referenced standing input changes value, signed-zero bit or own-property presence
- **THEN** that leaf and its dependent nodes are recomputed in original postorder, with the same result or first error as a full bind

#### Scenario: Cache is not eligible
- **WHEN** a search has nonfinite scope, changed moving-name set, unsupported path structure, changed expression generation or a failed prior search
- **THEN** it uses the existing full bind or generic fallback and does not reuse an ineligible standing value

#### Scenario: Restore and independent mounts
- **WHEN** a run is restored or reset, or two runs of the same document are mounted concurrently
- **THEN** no retained path from the old state or other run can affect the next bound search

#### Scenario: OperatingCurta default-tick crank
- **WHEN** the viewer runs the first 48 default 1/240-second ticks of the pinned OperatingCurta crank after setting selector 1
- **THEN** the 213-coordinate bank and ordered bound samples remain exact while repeated standing-node resolutions and process CPU decrease materially
