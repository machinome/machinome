## MODIFIED Requirements

### Requirement: An empty B-rep common contradicted by strict shared interior is refused

When a B-rep intersection Boolean reports no solids, the system SHALL refuse that result as a clearance verdict if an independent native section and zero-tolerance solid classifiers find one point classified inside both operands and demonstrably separated from every boundary face by more than that face's native tolerance, whose six neighbours at half its smaller distance to the two solids' faces, along ±x, ±y and ±z, the same classifiers also find inside both. A point unresolved at the boundary SHALL NOT count as a contradiction, and neither SHALL a point that any of those neighbours puts outside either solid, nor a point whose nearest boundary point in either solid lies inside a face or a two-faced edge and shows it outside that solid or within that face's native tolerance. The system SHALL NOT infer an overlap volume from that point, a section curve alone, or a mesh result. The same behavior SHALL apply to direct `machinome.engine.brep.intersect_shapes` calls, which the `brep-engine` capability specifies, and to B-rep test assertions, which reach that same operation through the B-rep engine seam. A finite search with no resolved witness SHALL retain the prior Boolean verdict, without claiming universal certification of its emptiness.

#### Scenario: Curta sphere/frame false-empty
- **WHEN** the unchanged Curta Type I positioning sphere and native frame are compared at the documented outer radial position and either 0.2 mm axial perturbation, where the B-rep engine's common is empty but a point is reliably inside both solids beyond their native face tolerances
- **THEN** the B-rep comparison refuses the inconsistent empty result instead of reporting clearance or manufacturing a positive volume

#### Scenario: Curta planar carry-guide contact
- **WHEN** a candidate lies within the native face tolerance of both opposed carry-slider and guide contact faces despite zero-tolerance classifiers reporting IN
- **THEN** that candidate does not contradict the empty common, and the finite search continues without an overlap waiver

#### Scenario: OpenAstroMount bearing seat
- **WHEN** OpenAstroMount's F206 housing and UC206 insert, which meet on two concentric spheres of radius 31 mm, are compared at a right ascension pose where the insert's classifier reports IN at one candidate 0.1357 mm outside its sphere and OUT at that candidate's neighbours
- **THEN** that candidate does not contradict the empty common, and the comparison returns the empty common as clearance

#### Scenario: Wall clock 02's weight shell on its screw
- **WHEN** wall clock 02's weight shell and its screw, which touch, are compared and the B-rep common is empty
- **THEN** the comparison returns the empty common as clearance without consulting the shell's classifier at any stencil point, each point the screw holds being read as outside the shell, or on the boundary of one of the two, from their nearest boundary points

#### Scenario: Zero-volume boundary contact
- **WHEN** B-rep solids only meet at a face or edge and no point is reliably inside both
- **THEN** the guard does not turn the contact into positive overlap or change its existing empty/non-empty and zero-volume policy

#### Scenario: Ordinary disjoint, overlapping and contained solids
- **WHEN** a B-rep common is correctly empty for disjoint solids, or correctly non-empty for overlapping or contained solids
- **THEN** the comparison retains the native Boolean's existing count and volume semantics

#### Scenario: Independent check fails
- **WHEN** the native section, classifier, face distance, or native face tolerance cannot be evaluated while checking an empty common
- **THEN** the B-rep comparison refuses to return a clearance verdict from that failed check
