## ADDED Requirements

### Requirement: Equivalent running law folds share only successful tick-local structure

During one running tick, the simulator SHALL be allowed to reuse a successful immutable folded law graph only for the identical expression root and complete bit-identical finite built-in numeric substitution. The reuse SHALL be bounded and discarded at the tick boundary, including an unsuccessful tick. When identity or numeric safety cannot be established, the original fold SHALL determine the result or first error. Reuse SHALL change no expression arithmetic, sampled constraint value or order, stop, bank, refusal, snapshot, document, or author declaration.

#### Scenario: Curta repeatedly reaches the same Follow branch
- **WHEN** a Curta Follow tick folds the same root and substitution at repeated Bound probes
- **THEN** successful structure can be reused while its ordered Bound samples and final bank remain bit-identical to complete folding

#### Scenario: A distinct or uncertain substitution
- **WHEN** the root differs, any substitution differs including the sign of zero, or a value is custom, non-finite, or cannot be proved safe
- **THEN** the earlier fold is not reused and the original fold determines the value or first error

#### Scenario: Failure, eviction, and another tick or run
- **WHEN** folding fails, the bounded working set evicts an entry, a tick fails or completes, or another run begins
- **THEN** no unproven or prior-tick result is trusted and every required fold can be performed by the original path
