## ADDED Requirements

### Requirement: An empty exact common contradicted by strict shared interior is refused

When an exact intersection Boolean reports no solids, the system SHALL refuse that result as a clearance verdict if an independent native section and zero-tolerance solid classifiers find one point strictly inside both operands. The system SHALL NOT infer an overlap volume from that point, a section curve alone, or a faceted result. The same behavior SHALL apply to direct `machinome.exact.intersect_shapes` calls and to exact test assertions that use that comparison path. A finite search with no witness SHALL retain the prior Boolean verdict, without claiming universal certification of its emptiness.

#### Scenario: Curta sphere/frame false-empty
- **WHEN** the unchanged Curta Type I positioning sphere and native frame are compared at the documented outer radial position and either 0.2 mm axial perturbation, where OCCT common is empty but a point is strictly inside both solids
- **THEN** the exact comparison refuses the inconsistent empty result instead of reporting clearance or manufacturing a positive volume

#### Scenario: Zero-volume boundary contact
- **WHEN** exact solids only meet at a face or edge and no point is strictly inside both
- **THEN** the guard does not turn the contact into positive overlap or change its existing empty/non-empty and zero-volume policy

#### Scenario: Ordinary disjoint, overlapping and contained solids
- **WHEN** an exact common is correctly empty for disjoint solids, or correctly non-empty for overlapping or contained solids
- **THEN** the comparison retains the native Boolean's existing count and volume semantics

#### Scenario: Independent check fails
- **WHEN** the native section or classifier cannot complete while checking an empty common
- **THEN** the exact comparison refuses to return a clearance verdict from that failed check
