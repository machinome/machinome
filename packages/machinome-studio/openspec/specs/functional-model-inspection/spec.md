# Functional Model Inspection Specification

## Purpose

Present a completed solid-node build in the shop floor without loading project
Python into Floor.
## Requirements
### Requirement: The shop floor builds the selected functional model before opening
When opening a named project shop floor, the system SHALL use a solid-node CLI
one-shot build of the project's default `root` functional model before starting
the Floor service or agent runtime. The build SHALL produce a complete
`_build` viewer snapshot and all referenced model files before Floor can be
declared open. The Model area SHALL consume only that completed snapshot and
its referenced model files. Floor MAY list, read, and atomically replace
verified project source as inert text for the Code area, but it SHALL NOT
import, execute, reload, or interpret that source.

#### Scenario: A named project has a buildable default model
- **WHEN** the maker opens the shop for a named project whose default `root` model builds successfully
- **THEN** the system completes one solid-node CLI build and makes the complete `_build` model artifacts available before starting Floor

#### Scenario: The build command succeeds without a complete publication
- **WHEN** the initial build does not leave a readable viewer snapshot and every referenced model artifact
- **THEN** the system treats preparation as failed and does not start Floor or its agents

#### Scenario: The maker first opens the reported browser location
- **WHEN** the system has reported a named project shop as open
- **THEN** the browser can retrieve the already-validated initial viewer snapshot rather than receiving a no-build response

#### Scenario: The maker opens project source
- **WHEN** the maker reads a verified text file through Code
- **THEN** Floor returns inert text without using it as functional-model input or executing it

### Requirement: The shop floor refreshes a changed functional model
While a named project shop floor is open, the system SHALL keep the maker's
functional-model view current with the project's model source. The system SHALL
build the project when its model source changes, including an atomic maker save
from Code, and SHALL separately observe the project's published build output.
Each file that becomes newly published
there SHALL be reported to connected browsers as one event naming that file and
nothing further about it, without regard to what the file is. The system SHALL
report such an event whichever publisher produced the file, including a
publisher that is not the shop. The system SHALL NOT report the removal of a
file, SHALL NOT compare, open, or interpret published contents to decide what
to report, and SHALL NOT import or execute project Python. A build reads the
model source it loads; the system SHALL treat only source that is created,
modified, relocated, or removed as changed, and SHALL NOT treat a build's own
reads as a change. The Code save operation SHALL NOT invoke a separate build.

#### Scenario: Any author changes the model
- **WHEN** the project's model source changes while the shop floor is open, by whichever author changed it
- **THEN** the system builds the model and reports each artifact the build published

#### Scenario: The maker saves Python source in Code
- **WHEN** an accepted Code save atomically replaces a Python model source file
- **THEN** the existing source watcher observes it and coalesces it into the same build path used for an agent write

#### Scenario: The maker saves a non-source file in Code
- **WHEN** an accepted Code save changes a file the source watcher does not treat as model source
- **THEN** the Code save operation starts no model build of its own

#### Scenario: A publisher other than the shop changes the model
- **WHEN** a build the shop did not run publishes an artifact into the project's build output while the shop floor is open
- **THEN** the system reports that artifact to connected browsers just as it reports one from its own build

#### Scenario: One part of the model changes
- **WHEN** a change to the model republishes one artifact and leaves the project's other artifacts untouched
- **THEN** the system reports that one artifact and reports no event for the untouched ones

#### Scenario: A build reads the model source it is building
- **WHEN** a build the shop ran reads the project's model source files while the shop floor is open
- **THEN** the system runs no further build on account of those reads

#### Scenario: A rebuild produces no change to the published model
- **WHEN** a rebuild completes and leaves the published model artifacts unchanged
- **THEN** the system reports no model artifact to connected browsers

#### Scenario: A node is removed from the model
- **WHEN** a change removes a node and its artifact ceases to be published
- **THEN** the system reports the published artifacts that changed and reports no event naming the removed artifact

### Requirement: The shop floor updates the displayed model in place
The Floor browser SHALL mount the viewer once for as long as the shop floor is
open and SHALL answer each reported artifact by updating that mounted viewer,
never by mounting a replacement. It SHALL decide what to update from the
reported artifact's path alone: the published document reconciles the rendered
tree, the failure record updates the reported failure, and any other artifact
replaces the geometry of the nodes referencing that exact path. The browser
SHALL NOT open, compare, or interpret an artifact's contents, and SHALL NOT
request an artifact that no reported path named. A browser that has obtained a
Floor run snapshot SHALL receive every later reported artifact, including one
published before its live-event subscription is established, and apply it to
the mounted viewer without a page reload.

#### Scenario: One part of the model is republished
- **WHEN** the shop floor reports one model artifact of a model with many
- **THEN** the browser requests that artifact and no other, and the parts it
  did not name keep the geometry they are already displaying

#### Scenario: The maker's view survives a change
- **WHEN** the maker has rotated, panned, or zoomed the functional model and
  any artifact of it is reported
- **THEN** the same rendered canvas remains in the page, and the camera
  position, orientation, zoom, and orbit target are unchanged

#### Scenario: An artifact is republished under the name it already had
- **WHEN** a change republishes an artifact at the path the browser has
  already fetched once
- **THEN** the browser displays the republished contents rather than the
  contents it fetched before

#### Scenario: The model gains and loses parts
- **WHEN** a change adds one node and removes another, and the shop floor
  reports the republished document
- **THEN** the browser reconciles the displayed model to the document, showing
  the added node and dropping the removed one, without requesting geometry for
  the parts the document still names unchanged

#### Scenario: A change moves nothing but placement
- **WHEN** a change alters only placement or colour and the shop floor reports
  the republished document
- **THEN** the displayed model reflects the change and the browser requests no
  model geometry

#### Scenario: A publication arrives during the browser subscription hand-off
- **WHEN** an already-open Floor browser has read its run snapshot, an
  assembly-to-fusion build publishes `viewer.json`, and the browser's live
  event subscription becomes active afterward
- **THEN** the browser reconciles the mounted model to the fused publication
  without navigating, reloading, or mounting a second viewer

### Requirement: A failed model update leaves the model standing
A request the browser cannot complete SHALL NOT remove the displayed model. The
browser SHALL keep the mounted viewer, the rendered model, and the maker's view
in place, report the failure beside the model rather than in place of it, and
remain able to apply the next reported artifact. Recovering from a failed
update SHALL NOT require the maker to reload the page.

#### Scenario: An artifact cannot be fetched
- **WHEN** the browser cannot fetch an artifact the shop floor reported
- **THEN** the model that is already displayed remains displayed with the
  maker's view intact, and the maker is told the update failed

#### Scenario: The next change arrives after a failure
- **WHEN** an artifact fetch has failed and the shop floor later reports
  another artifact
- **THEN** the browser applies that update to the still-mounted viewer, and
  the reported failure is cleared without a page reload

#### Scenario: The model cannot be shown at all
- **WHEN** the browser cannot mount the viewer when the shop floor opens
- **THEN** the maker is told why, and a later reported artifact is attempted
  rather than ignored

### Requirement: The shop floor reports a failed model build
A failed build records itself in the project's build output. The system SHALL
report that record to connected browsers as published build output, on the same
terms as any other artifact and whichever publisher produced it, and SHALL keep
every artifact that is currently published available for inspection. A partially
updated model is a legitimate published state: the system SHALL NOT withhold
published artifacts, restore superseded ones, or represent the model as
complete. The system SHALL NOT maintain a separate report of a build failure it
observed, and SHALL NOT read the failure record to decide what to report.

Being unable to run a build at all is a failure of the shop rather than of the
model, produces no build output, and SHALL be reported separately.

#### Scenario: The model source is broken
- **WHEN** the project's model source changes so that the build the shop runs fails
- **THEN** the maker is shown that the build failed together with the reported reason, and the artifacts published so far remain inspectable

#### Scenario: A build the shop did not run fails
- **WHEN** a build the shop did not run fails and records the failure in the project's build output
- **THEN** the maker is shown that failure on the same terms as one from the shop's own build

#### Scenario: A failing build has already published part of the model
- **WHEN** a build publishes some artifacts and then fails before publishing the rest
- **THEN** the system reports the failure and leaves the newly published artifacts in place rather than presenting the model as it was before the build

#### Scenario: The maker fixes the model
- **WHEN** a build succeeds after a previously reported failure, withdrawing the failure record and republishing the model
- **THEN** the reported failure is cleared
- **AND** the browser is told about each artifact that build republished

#### Scenario: The build cannot be run
- **WHEN** the shop cannot run a build of the project at all
- **THEN** the maker is told that the shop could not build, distinctly from the model having failed to build

### Requirement: The shop floor serves an artifact through a concurrent republication
The system SHALL serve any artifact of the project's published build output for
as long as that artifact is published, including while another artifact of the
same model is being republished. A publication occurring between a request and
its response SHALL NOT cause the system to report the requested artifact as
unknown. The system SHALL serve nothing outside the project's build output.

#### Scenario: An artifact is requested while the model is republished
- **WHEN** the browser requests a published artifact at the moment a build republishes another artifact of the same model
- **THEN** the system serves the requested artifact rather than reporting it unknown

#### Scenario: An artifact is requested while it is itself being replaced
- **WHEN** the browser requests an artifact that a build is concurrently replacing
- **THEN** the system serves either the previous or the new artifact in full, and never a partially written one

#### Scenario: A path outside the build output is requested
- **WHEN** a request names a path that resolves outside the project's published build output
- **THEN** the system reports it unknown and serves nothing

### Requirement: The shop floor presents the complete static viewer experience
The Floor browser SHALL render completed build artifacts with the established
solid-node viewer semantics while obtaining only `viewer.json` and referenced
model files through Floor's static artifact route. It SHALL use nested node
groups, complete OpenSCAD expression evaluation, inherited colours, normal
material for uncoloured models, a Z-up fitted camera, and working orbit
rotation and zoom. A capability that solid-node adds to that viewer SHALL reach
the shop floor without the shop reproducing it.

#### Scenario: A colourless V8 model is displayed
- **WHEN** the build snapshot has no explicit or inherited colour for a model
- **THEN** Floor renders that mesh with the established viewer's normal-based material rather than a uniform grey material

#### Scenario: A build contains time-based operations
- **WHEN** any operation in the build snapshot references `$t`
- **THEN** Floor autoplays the model and provides a compact Timeline toggle; the timeline slider and play/pause controls remain hidden until the maker requests them

#### Scenario: The maker is inspecting a model when it refreshes
- **WHEN** the maker has rotated, panned, or zoomed the functional model and a successful rebuild refreshes it
- **THEN** Floor updates only the parts the rebuild republished, leaving the rest of the rendered model and the maker's camera position, orientation, zoom, and orbit target as they were

#### Scenario: solid-node improves how models are seen
- **WHEN** the installed solid-node changes how it renders a published model
- **THEN** the shop floor shows that change without a corresponding shop change

### Requirement: The shop floor requires a usable solid-node viewer to open
When opening a named project shop floor, the system SHALL obtain the browser
viewer from the installed solid-node through its CLI, which reports the viewer
package installed beside it. The viewer the floor requires SHALL be one that
updates a mounted model in place from a named artifact and from the published
document. When the installed solid-node reports no viewer — because the
`solid-node-viewer` package is not installed — or reports one the floor cannot
use, the system SHALL treat preparation as failed, report the reason and its
remedy, and SHALL NOT start Floor or its agents. The maker SHALL NOT be shown a
shop that is open with a model pane that cannot render.

#### Scenario: The installed solid-node ships no viewer
- **WHEN** the maker opens the shop and the installed solid-node has no viewer package installed beside it
- **THEN** the shop does not open, and the maker is told that the viewer is unavailable together with the framework's remedy, installing the `viewer` extra

#### Scenario: The installed viewer is older than the floor requires
- **WHEN** the maker opens the shop and the installed viewer package does not meet the interface the floor depends on
- **THEN** the shop does not open, and the maker is told which viewer the floor requires and which one is installed

#### Scenario: The installed viewer cannot update in place
- **WHEN** the maker opens the shop and the installed viewer can only be mounted and replaced
- **THEN** the shop does not open rather than opening with a model pane that reloads the whole model on every change

#### Scenario: A usable viewer is installed
- **WHEN** the maker opens the shop and the installed solid-node reports a usable viewer
- **THEN** the shop opens and the browser renders the functional model with that viewer

### Requirement: The build snapshot carries browser animation metadata
The `solid build` publication consumed by Floor SHALL include a versioned
animation cadence with `fps` and `frames` together with the root viewer tree.

#### Scenario: Floor opens an animated model
- **WHEN** `solid build` publishes a model whose operations include `$t`
- **THEN** `viewer.json` supplies the animation cadence required for Floor to animate that model without a project runtime

