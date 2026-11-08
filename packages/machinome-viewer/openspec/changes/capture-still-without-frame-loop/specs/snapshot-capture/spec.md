## ADDED Requirements

### Requirement: Eligible stills are captured without a continuing viewer frame loop

For a valid staged posed document without instructions, and for a valid staged clocked document, the capture SHALL use the viewer's existing on-demand rendering mode with external animation, autoplay disabled, no driver controls and no part controls. It SHALL photograph the requested animation instant and the same declared initial or standing pose required by the existing snapshot contract, without issuing a simulation request or starting an animation-frame render loop.

After mount and final viewport/layout settlement, the capture SHALL explicitly draw the viewer's current public view before announcing that the page is ready to photograph. That redraw SHALL preserve camera, target, up, field of view, bank and requested animation instant. The resulting PNG SHALL retain the existing model, markings, transparency and requested dimensions.

A staged running program or a posed document with instructions SHALL retain the existing continuous-mode capture path and its existing rest-state, instant and error behavior. Mode selection SHALL NOT strip program or instruction data, alter model geometry, hide model parts, weaken document validation, or change the caller's supplied option object. Existing malformed-document and unsupported-instant refusals SHALL remain refusals.

#### Scenario: A posed model is photographed at an explicit instant

- **WHEN** a valid posed document without instructions is captured at a requested animation instant
- **THEN** the capture draws that instant without a continuing viewer render loop and produces the same model content, markings, camera and alpha behavior required by the existing contract

#### Scenario: A clocked model is photographed at its initial bank

- **WHEN** a valid clocked document is captured, including one declaring instructions, at a permitted animation instant
- **THEN** the capture draws on demand with the bank at its declared initial values, makes no request, and honors the requested animation instant

#### Scenario: Layout settles after the initial mount

- **WHEN** an eligible capture's viewport settles after the viewer's initial draw
- **THEN** readiness follows an explicit draw of the current public view and the photograph contains the correctly framed model at the requested dimensions rather than a cleared or stale canvas

#### Scenario: A running program keeps its supported capture path

- **WHEN** a staged running program is captured at time zero
- **THEN** capture uses the existing continuous-mode path and photographs the rest state without advancing the run

#### Scenario: A posed document declares instructions

- **WHEN** a valid posed document with instructions is captured
- **THEN** capture uses the existing supported continuous-mode path and retains the instruction data without playing an instruction

#### Scenario: Mode selection does not repair a malformed document

- **WHEN** a malformed staged document or an unsupported running-program instant is supplied
- **THEN** capture preserves the existing refusal, starts no simulation request, and does not change document data or caller options to obtain an image
