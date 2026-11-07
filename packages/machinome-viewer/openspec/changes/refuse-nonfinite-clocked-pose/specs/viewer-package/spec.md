## ADDED Requirements

### Requirement: Clocked final rendered transforms are admitted atomically

As part of the existing requirement "The viewer executes a clocked machine's requests", a mounted clocked machine SHALL refuse a requested final pose when an operation evaluated for that pose throws, yields a non-finite placement operand (`NaN`, positive infinity or negative infinity), or produces a non-finite local or composed rendered transform. The refusal SHALL reach the caller and name the assembly path and offending operation, or the assembly path whose transform composition failed. It SHALL leave the complete standing bank and every standing rendered placement unchanged, including earlier siblings and descendants of a changed ancestor; no events or successful outcome from the refused request SHALL be published. A subsequent render or public `partOnScreen` query SHALL still observe the standing finite pose. The same final-pose admission SHALL apply when a declared instruction requests a move and when a matching-machine snapshot is restored.

This judgement SHALL use operations selected by the existing change/dependency rules and their actual final scope, including shared bindings and ancestor placements. It SHALL NOT evaluate otherwise unused expressions or new intermediate path points to seek an error, treat Driver/State range metadata as a bound, or turn an invalid pose into an admitted clipped request. Finite valid requests SHALL retain their existing bank, events, admitted path endpoints, units and placement semantics without a document or public interface change.

#### Scenario: A rendered descendant consumes an undefined ancestor rotation

- **WHEN** a standard clocked document's rendered descendant is placed by an ancestor operation containing a square root that is zero on its valid interval and undefined at the requested final input
- **THEN** the public machine handle throws a refusal naming that ancestor operation, the whole bank remains at its previous values, and the descendant retains its previous finite visible placement

#### Scenario: A later invalid node does not move an earlier sibling

- **WHEN** the requested final bank would validly move an earlier sibling and a later node's translation or rotation evaluates to NaN or either infinity, or throws
- **THEN** the request is refused and neither sibling nor any other rendered node changes its standing placement

#### Scenario: Events before an invalid final pose do not commit

- **WHEN** a request crosses a committing relation's event before its final rendered transform becomes invalid
- **THEN** no requested driver value or event-written state is banked, no successful event outcome is published, and the next valid request computes its events from the original bank

#### Scenario: Finite local matrices compose to an invalid rendered placement

- **WHEN** a requested pose has finite local matrices whose ancestor composition overflows to a non-finite rendered transform
- **THEN** the request is refused naming the affected path before any candidate placement or bank becomes standing

#### Scenario: A refused instruction or restore retains the visible pose

- **WHEN** a declared instruction requests an invalid final transform, or a matching-machine snapshot asks to restore a bank producing one
- **THEN** the operation throws and leaves the prior bank and all prior visible placements standing

#### Scenario: Valid motion and recovery preserve normal clocked behavior

- **WHEN** a finite valid request crosses an event, an invalid request is refused, and another finite valid request follows
- **THEN** each valid request retains its normal admitted endpoints and events, all rendered parts remain finite, and the refused request contributes no state or visible movement to the later request

#### Scenario: Unused expressions and range metadata do not become new guards

- **WHEN** a final pose is finite under the existing selected operations even though an unused binding is undefined or the requested Driver/State value is outside its advertised range
- **THEN** this rendered-transform admission adds no refusal or clipping, and unaffected branches are not re-evaluated

#### Scenario: A refused candidate cannot poison the standing scope or independent motion

- **WHEN** a refused input candidate has populated a shared binding's numeric memo values, the tree is updated again at its original bank, and after another refusal the host moves only an independent driver without resetting or remounting
- **THEN** the repeated original-bank pose remains finite and unchanged, an affected sibling reads the original input's binding together with the new independent-driver value, the failed branch remains selectively untouched at its standing finite pose, and a later valid request of the original input updates that branch correctly
- **AND** this recovery holds both when the earlier refusal came from a cached non-finite operation result and when operation evaluation threw
