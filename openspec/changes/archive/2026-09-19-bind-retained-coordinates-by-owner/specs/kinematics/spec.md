## ADDED Requirements

### Requirement: Qualified joint assignments affect only their addressed owner

Under a running root, a qualified joint-coordinate assignment through
`set_state` SHALL change only the addressed joint's bound value and LOCAL
joint placement, even when
ancestors or descendants own coordinates with the same local name. Every other
joint SHALL retain its own bound value and local joint placement; a
descendant's WORLD pose SHALL still compose the changed ancestor placement
with its retained local placement and the declared rest transforms. A bare
coordinate name claimed by more than one declaration
SHALL remain ambiguous, name the colliding qualified IDs, and leave every
snapshot, bound coordinate and pose unchanged.

#### Scenario: A qualified single-coordinate name stops at its owner

- **WHEN** `carrier.turn` is delivered through a tree in which descendants
  also own locally named `turn` coordinates
- **THEN** only `carrier` changes bound value and local joint placement, each
  descendant retains its own bound value and local joint placement, and each
  descendant's world pose composes the changed carrier placement

#### Scenario: A bare coordinate spelling still discovers every claimant

- **WHEN** bare `turn` is bound on a running subtree with several coordinate
  owners, or with both coordinate and driver claimants
- **THEN** binding is refused as ambiguous with all colliding qualified IDs,
  and every snapshot, coordinate and pose remains as it was before the request

#### Scenario: Qualified multi-coordinate names keep their established owner

- **WHEN** a qualified entry such as `chassis.pose.roll` reaches the node that
  owns the multi-coordinate joint
- **THEN** `pose.roll` binds and places only that joint, without changing the
  local coordinate or joint placement of a descendant whose path or coordinate
  name shares either segment; descendant world poses still compose ancestor
  motion
