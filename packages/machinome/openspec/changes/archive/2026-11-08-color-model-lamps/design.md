## Context

Origin: Enigma's actual `LampGlass`, `simulation/declared_lamp_probe.py`, `simulation/tools/probe_declared_lamp.py`, `sources/declared-lamp-appearance-v1.json` and `docs/workstreams/declared-lamp-appearance.md` in `/mnt/data/machinome-projects/enigma-i`. The retained diagnostic ran in a linked integration worktree, not canonical main. Numeric observations 0/1/0 select `#e5dfce/#ffd978/#e5dfce`; both fixed-color controls build with the same physical piece identity `470fa6a540e1`, while the dynamic Python conditional raises `SymbolicTruthError` at publication. Its receipt pins logs and documents and explicitly calls this a capability finding, not a static-color conformance bug. Its historical 1,943-leaf input is not the newer ordinary 2,018-leaf model; do not conflate those packets.

Current alternatives were inspected, not ruled out from the conditional failure alone:

| Existing route | Observed contract/source | Why it does not deliver this requirement |
| --- | --- | --- |
| `node.color = '#RRGGBB'` | `node-model` Color declaration; `node/base.py:_colorize`; `core/serializer.py:serialize_node` publishes `node.color` | One static hex/None; no state predicate is published. Numeric assignment works but does not defer a Python branch. |
| `machinome.math` | Degree-based scalar operations and numeric compositions; no color/selection API | Scalar arithmetic cannot produce a supported symbolic six-digit hex value; coercing it with `str`, `hex` or Python truth would bake/refuse, not bind a color law. |
| Marking color / source CAD colors | Static hex on a distinct decal, STEP source color or authored CAD presentation; STL rendering uses node-level material | No model-state law on the existing glass; a new overlay/decal or duplicate lit body is the wrong physical consumer. |
| `ViewerHandle.highlight` / hover | Host overlay; viewer ADR-076 and `presentation.ts` give one material presentation owner | Requires host actions/JS, has independent lifetime and no circuit-bank/reset/replay authority. It is not a model declaration. |
| Rebuild or swap roots | A static document can republish another color | Rebuilds/replaces a document rather than having ordinary controls operate one retained model. |

The recommendation is deliberately color selection only. The source-backed lit control is a different hex under existing viewer lighting; no self-emission, optical brightness, illumination of neighboring parts, bloom or thermal/electrical model is claimed.

Ownership: core at `packages/machinome`; web viewer at `packages/machinome-viewer` with its own OpenSpec (ADR-188/194/196); API shop skill in `packages/machinome-studio/machinome/studio/shop-skills/machinome-api/SKILL.md` (ADR-193). The paired viewer planning record is `read-model-color-choice` in that product. Studio's contract synchronization is a completion dependency under its own process, with no new Studio behavior. The workspace's old separate-repository statements and core OpenSpec context's old monolithic paths/frontend symlinks conflict with accepted current monorepo records; they are not adopted or edited here. Use a worktree-owned locked environment after ratification, not a symlink to or mutation of the installed environment. No framework-local AGENTS/prompts were read as authority.

Standalone base: clean main `6f07b083d3e9a4194d5f982ce200ae9dc6ffe4b9`; branch/worktree `illuminate-model-lamps`, slot 14, intended eventual integration target main under recorded authority. The pilot’s active goal, “Finish the ongoing work in all branchs and merge everything to main”, advances this existing work through planning, apply, validation and local integration. The coordinating agent reviewed both complete plans; this is advance authorization plus agent review, not a human review of the finished text. The capture change is the immediate predecessor: capture predecessor integrated at the recorded base; planning and apply proceed through the clean-commit gate. Installed-environment changes, push and publication remain outside this cycle.

## Goals / Non-Goals

**Goals:** One source-backed color choice on each same glass; numeric/symbolic parity; ordinary build/export/Studio controls; reset, restore and replay select from the machine's standing state; physical/model/artifact identity unchanged; legacy static colors and non-choice documents unchanged.

**Non-Goals:** No circuit solver or new circuit result, new framework input controls, custom panel, host callbacks, model postprocessing, duplicate parts, general appearance/material API, interpolated RGB, opacity, textures or emission. No claim that the partial Enigma motion law becomes a complete operating law. No extraction/new distribution. No new public retained appearance state.

## Decisions

1. **One helper assigned to the existing attribute.** Proposed spelling:

   ```python
   from machinome.color import color_when

   def simulate(self):
       self.glass.color = color_when(
           self.energized > 0.5,
           on='#ffd978', off='#e5dfce')
   ```

   `color_when(condition, *, on, off)` validates both required colors as `#RRGGBB`. For a numeric finite bool/real condition it returns the selected existing string: zero selects off, nonzero selects on. For a supported framework symbolic scalar it returns a small immutable internal choice holding the graph and two strings; it never asks Python for a symbolic truth. Non-numeric/non-symbolic or non-finite numeric conditions fail by name. Conditions remain ordinary model formulas; no callable callback or new expression function is published. Declarative parameter-formula color objects and nested color choices are not introduced; callers use the helper where resolved numeric or motion values are available.

   A new `Appearance` declaration or mutator family would introduce lifecycle and namespace surface the glass does not need. Arbitrary RGB expressions/continuous interpolation would require color-space and channel-domain choices unsupported by this finding. A raw expression string in `color` would ambiguously compete with existing hex strings and encourage constructing expressions by hand.

2. **Keep the physical boundary.** Color/choice is presentation data, not a construction parameter, solid, driver, port or retained state. It does not key geometry, cause model remeshing per request, change part inventory/identity or affect contracts over exact solids/meshes. Existing static hex/None, nearest-ancestor inheritance, explicit child overrides and independent fixed marking colors stay intact. The choice extends a node's existing whole-node color semantics; it does not gain a separate geometry branch. Both colors are required, so release/power-off is authored explicitly rather than retaining whichever color was set last.

3. **Use the existing symbolic document path.** Serialize `color` as either its legacy string/null or exactly `{when: <scalar expression>, on: '#RRGGBB', off: '#RRGGBB'}`. Add `color.when` to the existing expression-slot/binding compiler so reuse stays bounded and aliases have the same qualified driver/state/coordinate/time scope as pose. Numeric snapshots can publish the selected static hex; live ordinary build/export must preserve the condition. All producers use the same serializer rather than patching a delivered document. Core colorization recognizes the choice before `.lstrip`; symbolic OpenSCAD presentation can express each selected RGB channel with existing scalar graph arithmetic over `(condition != 0)`, with no new public RGB/ternary language. This is color presentation, not emitted light.

   Successful and failed symbolic publication must restore the caller's numeric drivers/states, node colors and pose. Numeric `Sim` reset/restore/replay must recompute the same selected strings with no appearance history. Source inspection shows current publication restores state maps then re-renders; tests must pin color restoration too, including a failure after an earlier body's color was assigned. Add bounded restoration of appearance values only if replay alone is insufficient; do not snapshot arbitrary user object dictionaries.

4. **Explicit version gate, preserving execution modes.** A document containing any symbolic color choice selects version **14**, dominating the current posed/clocked/running ladder. A document containing no such value keeps its current version and bytes; `color_when(True/False, ...)` is just a static hex. Version 14 does not imply a running machine: `program` means running, `clocked` means clocked, neither means posed; both remain invalid. This matters because current viewer and capture paths infer a program from `version >= 5` except 8. The paired reader must handle version 14 by content while retaining the existing version-1–13 checks/refusals. Older readers must refuse 14 before rendering rather than silently showing the off color. The companion viewer advertises API **30**, documents 1–14. No release version/publication is implied by those proposed source changes.

5. **Viewer base appearance follows admission, not a second state machine.** The viewer companion resolves the chosen hex from its current posed/banked scope, with dependency closure for bindings and inherited choices. It prepares candidate colors with placement admission before publishing any material base; an invalid evaluated condition must not leave earlier bodies recolored or commit a clocked bank/events. Native and browser truth semantics are finite zero/nonzero. Materials/geometry retain identity as far as the existing ownership rules permit; no STL refetch/replacement is used to simulate a color change.

   Viewer ADR-076's `MaterialPresentation` must remain the one owner of base/hover/highlight composition. Rebase a standing material's declared color through that owner, then derive overlays from the new base. Clearing a highlight after a lamp changes must reveal its new current color, not the old recorded base. `assembly().color` remains a resolved string/null, not a new wire object; current host interfaces keep their types.

## Risks / Trade-offs

- Version 14 crosses the old mode-by-number assumption → explicit posed/clocked/running fixtures, capture classification checks and old-reader refusal tests, not a broad execution-model redesign.
- Native publication may leak symbolic/temporary color assignments → round-trip state/color tests on both success and deliberate failure before choosing the smallest restoration fix.
- Overlay restoration can resurrect an old lamp color → overlap hover/highlight and admitted state changes in a real browser; rebase through the existing single owner.
- A new feature could accidentally claim physical lighting → teach only the source-backed two-color visual choice and keep emission/optical units absent.
- A whole Enigma build/capture is costly → source-owned minimal rigid fixtures prove the feature first, then inspect the existing 26 actual glasses using retained assets in an isolated project worktree. Never replace canonical publication with an explicit diagnostic root.

## Validation Plan

Red-first after ratification: helper numeric truth/finite/hex validation; real symbolic standard build of an authored minimal glass fixture; shared predicates in bindings; native publication success/failure restores colors and state; color-only operation leaves mesh bytes/model paths/piece inventory and physical assertions unchanged; all legacy static documents byte-identical. A posed, clocked and running choice fixture must select the right runtime at v14 and old consumers refuse it. Add reset/restore/replay and failed-request atomicity checks with two bodies, a moved earlier sibling and an event crossed before the final invalid appearance condition.

Browser proof consumes the unedited standard document and official bundle through ordinary controls/handles. Capture dark/lit/dark pixels on the same mesh; assert geometry/material ownership, no asset fetch on a color-only update, binding-scoped independent-driver recovery, overlay removal showing current state, and reloading the same document at defaults. Native expected colors are the two source constants, not values read back from the implementation under test. Then use the actual Enigma glass and a 26-output electrical-observation sequence to prove one correct glass selection, release/power-loss clearing, reset/restore/replay equivalence and unchanged body identities. The project owns the electrical oracle and final ordinary root; this feature does not manufacture that oracle or substitute controls.

Run core/publication/expression-sharing tests; viewer focused/full unit tests, typecheck and real browser acceptance; strict manual build and targeted docs tests under `write-the-manual`; supported OpenSpec validation for both records. No required browser skip counts as acceptance. Record current source changes as unreleased with the exact API/document requirement; no uploads or installed-environment changes as a validation side effect.

## Open Questions / Ratification

The pilot’s active completion-and-merge goal supplies advance authority for both owned records and the named Studio API-contract synchronization dependency. The coordinating agent reviewed the complete plans and selected the helper spelling, wire object and version/API choices above within that scope; no human review of the finished text is claimed. The capture predecessor is integrated and the base is updated and verified. Implementation begins after both records validate and the planning-only commit is clean. No self-emission decision remains in scope.

Planning validation (2026-11-07): supported `openspec status` reports 4/4 planning artifacts complete and `openspec validate color-model-lamps --strict` passes from this owning package root. This is artifact validation only; no implementation, new runtime tests, dependency installation, planning commit or integration has occurred.


## Coordinated review (2026-11-08)

The coordinating agent reviewed both complete plans under the pilot’s active
completion-and-merge goal. The selected scope remains the exact helper, wire
form, format 14/API 30, same-body semantics and named Studio contract sync.
The dedicated core/viewer workers rechecked source boundaries and existing
material ownership. The capture cycle is the immediate predecessor, integrated as
`6f07b083d3e9a4194d5f982ce200ae9dc6ffe4b9`; the existing branch fast-forwarded
to this exact clean main HEAD before the planning commit.
No implementation or environment change is included in this review.

Native restoration review found `drive_tree` is currently called before the
publication context manager enters its `try/finally`. The red proof must
fail during that actual symbolic traversal after the first color assignment,
not merely raise inside the yielded context. If confirmed, bring that call
inside the existing restoration boundary; retain the existing numeric replay
and only add a bounded color snapshot if the measured failure requires it.
No unrelated exception or object-state framework is authorized.

Current Enigma main at `1dd1e48ed1e604bf15c972c94e9eff42d094b3a7` declares
`simulation.candidate_machine:CandidateMachineInspection`, with a static
`lamp_snapshot()` and actual glass paths supplied by `lamp_glass_paths()`.
The final project proof must consume the project electrical owner’s oracle
and supported ordinary-root declarations in an isolated project worktree;
the framework cannot call a diagnostic root or the static bank itself the
completed electrical consumer. The recorded 2,023-part document is distinct
from the older capability-finding packet above.

Project integration boundary update: the pilot’s coordinating agent authorized
the project owner to expose one `supply_connected` inspection Driver, default
off, forwarding the circuit’s existing powered input. This is project-owned
assembly integration, not a new framework control, a historical selector or a
battery-lid inference. The framework helper still accepts resolved numeric or
symbolic scalars; it does not silently read unbound relation outputs. The
project owner must prove a supported ordinary presentation lifecycle before
actual-project acceptance.


Base/authority gate (2026-11-08): the coordinating agent verified clean main
`6f07b083d3e9a4194d5f982ce200ae9dc6ffe4b9` after the capture cycle’s complete
local integration and authorized refreshing this existing cycle to that base.
The managed worktree fast-forwarded from its historical base without dropping
planning material. Both planning records are reviewed under the pilot’s
advance completion/local-integration authority and the Studio contract-sync
dependency is expressly included. The two-record planning-only commit is the
remaining gate before apply; the pilot-controlled installed environment is
not a validation target. Push, publication and contact remain unauthorized.
