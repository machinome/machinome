## MODIFIED Requirements

### Requirement: The orchestrator closes the shop floor
The system SHALL allow a maker to close shop-floor. The shop runtime SHALL end
the foreman, designer, and machinist sessions through the selected backend and
stop the shop-floor service before telling the maker that the shop is closed.

Closing SHALL complete within a bounded time. Ending a session that has active
work SHALL NOT prevent the runtime from closing, and no agent subprocess SHALL
be left running after the maker is told the shop is closed. When the selected
backend owns more than one agent subprocess, this SHALL hold for every one of
them.

#### Scenario: A maker closes the shop
- **WHEN** a maker closes the shop
- **THEN** the runtime ends all three shop-agent sessions, stops shop-floor, and reports that the shop is closed

#### Scenario: A maker closes the shop while work is active
- **WHEN** a maker closes the shop while one or more agents have active work
- **THEN** the runtime ends the active shop runtime without leaving an agent session or broker process running

#### Scenario: Closing does not hang on an agent that will not stop
- **WHEN** a maker closes the shop and the agent subprocess does not exit when asked
- **THEN** the runtime forces it to stop, completes the close, and reports that the shop is closed

#### Scenario: Ending active work does not abort the close
- **WHEN** ending an agent's active work reports an error while the shop is closing
- **THEN** the runtime still ends the remaining sessions, stops shop-floor, and reports that the shop is closed

#### Scenario: Closing releases every process of a multi-process backend
- **WHEN** a maker closes the shop running a backend that owns one subprocess per role and one of those subprocesses does not exit when asked
- **THEN** the runtime forces that subprocess to stop, still releases the others, and reports that the shop is closed

## ADDED Requirements

### Requirement: A maker can open the shop with the Claude backend
The shop runtime SHALL support opening the shop with the Claude backend, using
the same broker, role cards, skills, and product pipeline as the other backends.

#### Scenario: A maker opens the shop with the Claude backend
- **WHEN** a maker opens the shop with `--backend claude`
- **THEN** the runtime uses the Claude backend for all three agent sessions

#### Scenario: Claude role sessions are sandboxed to the project
- **WHEN** the runtime opens the shop with the Claude backend after preparing `projects/<name>`
- **THEN** each Foreman, Designer, and Machinist session uses that verified repository as its workspace boundary
