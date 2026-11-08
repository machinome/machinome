## ADDED Requirements

### Requirement: Model-selected colors follow the standing pose

The viewer SHALL accept the version-14 node color choice `{when, on, off}`, validate both fixed six-digit hex colors and the string scalar expression/binding scope before rendering, and select off for finite zero and on for finite nonzero. It SHALL update the existing body's declared base color from the same standing scope as placement, including ordinary controls, reset, restore and replay. An inherited choice SHALL obey existing nearest-ancestor/explicit-child override semantics, and SHALL NOT change fixed marking colors, geometry, body inventory or model asset identity. Public assembly colors SHALL remain resolved strings/null. An initial powered state SHALL be resolved before the first visible frame.

#### Scenario: An ordinary control changes the same glass

- **WHEN** ordinary model controls change an electrical observation off/on/off
- **THEN** the same glass displays the published off/on/off colors, without new geometry, asset refetch, host actions or a duplicate body

#### Scenario: Restore and replay select the saved state

- **WHEN** a valid powered state is saved, cleared, restored, reset and replayed
- **THEN** the same body returns to the color selected by each standing state with native-equivalent results

#### Scenario: Inheritance and markings keep their meaning

- **WHEN** an ancestor's choice changes while one child declares its own static color and another inherits, and either carries a fixed marking
- **THEN** only the inheriting body follows the ancestor; the explicit child and marking retain their own colors

#### Scenario: A powered default has no dark first frame

- **WHEN** a document's initial bank selects the on color
- **THEN** the first fully loaded visible frame already shows on

### Requirement: Color admission preserves standing appearance

A throwing or non-finite evaluated color condition SHALL refuse the candidate presentation before changing any standing base color or transform. For a clocked request or restore, this SHALL preserve the existing whole-request bank, events, pose and appearance atomicity. A later independent-input request SHALL use standing scope values rather than the refused candidate's memo values. Running physical-bank admission SHALL retain its existing authority; appearance SHALL NOT become a new mechanical bound or integration law.

#### Scenario: A later invalid color cannot recolor an earlier body

- **WHEN** a clocked request would recolor one body and then evaluates an invalid condition on another
- **THEN** it is refused and neither body, the standing bank, nor the request's events change

#### Scenario: A failed candidate does not poison independent motion

- **WHEN** a candidate populates a shared color predicate and is refused, then an independent driver moves without reset/remount
- **THEN** the valid update uses the original standing state and a later valid color change still works

### Requirement: Model color changes preserve the material presentation owner

Hover/highlight/dim/ghost SHALL remain overlays over the current declared model color under the existing material-presentation owner. A state-driven base-color change SHALL NOT capture an overlay as base or restore an obsolete prior model color when the overlay leaves.

#### Scenario: Unhighlight reveals the lamp's new state

- **WHEN** a highlighted dark glass becomes lit and the highlight is removed, in either order with hover removal
- **THEN** it shows the current lit base color with no stale tint or dark value

### Requirement: Conditional color has an explicit reader capability

The viewer SHALL advertise API 30 and document versions 1–14. A version-14 document's existing `clocked`/`program` payloads SHALL identify clocked/running execution, and the absence of both SHALL identify posed execution; both together SHALL refuse. Choice data claiming an older document version, malformed choices, and undeclared predicate inputs SHALL refuse before rendering. Legacy static documents and version-1–13 behavior SHALL remain unchanged. A reader supporting only versions 1–13 SHALL refuse version 14 rather than display a static substitute.

#### Scenario: Three version-14 modes mount correctly

- **WHEN** standard-produced posed, clocked and running color-choice documents are mounted
- **THEN** each retains its own runtime/control/snapshot semantics and the posed one is not misread as a missing program

#### Scenario: An old or malformed reader input does not silently darken the lamp

- **WHEN** an old reader receives version 14, or a color-choice document has invalid palette/scope data or claims an older version
- **THEN** it refuses before rendering the misleading appearance

#### Scenario: Static documents keep their existing result

- **WHEN** the legacy fixture corpus is rendered without conditional color data
- **THEN** its color, geometry, runtime and host interfaces retain their current behavior
