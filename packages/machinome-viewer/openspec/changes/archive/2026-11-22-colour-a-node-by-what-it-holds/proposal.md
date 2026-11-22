## Why

The pilot, 22 November 2026: "I want to improve the model tree navigation in the viewer. if everything inside an internal node has the same color, that node should display that color."

The originating project is Enigma I (`projects/enigma-i`, at `68dc6be`; its built document `_build/viewer.json`, version 14, SHA256 `563a2fdc4107a88847af5dd04dee59d1697ff7d15a92a19d2af280414f57e7d7`). Measured on that document by reading it (a scratch script, not kept): 4,173 nodes, of which 878 have children and 3,295 have none. Not one of the 878 declares a colour, and not one inherits one, so the assembly snapshot reports `color: null` for every one of them, at every pose (every conditional colour in the document sits on a node without children), and every group row of the navigator shows the neutral chip. A maker walking that tree gets no colour cue from any row that has children. Yet 302 of the 878 hold parts that all carry one and the same colour declaration (for example `keyboard/guide/n8_Anti_Twist_Device_Group_1`, 16 children, every part beneath it `#a0a0a0`), 3 hold only parts with no colour, and 573 hold parts of different declarations. 754 nodes, all without children, carry a conditional colour `{when, on, off}`; read at their `off` choice, 607 of the 878 hold parts of one colour. Of the 3,295 nodes without children, 2,868 carry a model file, 426 are flexible parts, and one (`operation`, a child of the root) carries neither.

What the project does with the result: the maker reading the Enigma I in the Studio's Model panel, or in the export page's sidebar, sees at a glance which subassemblies are one material (the grey guide groups, the black keys) before expanding them.

## What Changes

- The navigator's row decision (`navtree.ts`, `navigatorRows`) gives each row the colour it shows. A row without children shows its node's effective colour, as today. A row with children shows the one colour every part it holds shows, when they all show the same colour; otherwise it shows what it shows today (its node's effective colour, else the neutral fill). A node's parts are every node without children beneath it, presented or not, hidden or not, each at its own effective colour, and the node itself when the snapshot says it carries a model of its own. A part with no colour keeps its group from sharing one. The colours are compared as the strings the snapshot reports.
- The colours a group holds are found in one pass over the snapshot per call of `navigatorRows`, before the rows are walked, so the cost is one visit per node per redraw, not one walk per row.
- `chipState` and `navigator.ts` are unchanged in behaviour: the chip is filled with the row's colour when the node is shown, neutral when the row has no colour to show, empty when hidden; the checked state and the accessible name do not read colour. Two comments change to say what the row's colour now is.
- The assembly snapshot (`ViewerHandle.assembly()`, `AssemblyNode.color`) is unchanged: a node's `color` stays its own effective inherited colour. No option, CSS custom property, exported name or API is added. Viewer API stays 30; the document versions read stay 1 to 14.
- Tests, red on the base where the behaviour is new: `src/navtree.test.ts`, `src/navigator.test.ts`; a guard in `src/tree.test.ts` that the snapshot keeps reporting a group's own colour.
- Records: one CHANGELOG bullet under "Unreleased"; two findings in `workflow/warts.md` (a chip whose colour the machine chooses shows the choice of the last assembly change, not of the pose; `AssemblyNode.model` is `false` for a flexible part, where the manual calls it "a boolean indicating geometry"). No ADR.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-assembly-navigation`: three requirements.
  - "The package mounts an assembly navigator into any host element" says each row shows "its effective inherited colour when the node has one". That sentence is replaced by the rule above; five scenarios are added. The scenario "A navigator shows a nested coloured assembly" keeps its name and its WHEN; its THEN, which said every row shows the colour its node inherits, gains the exception the rule makes, because as written it would contradict the rule for a subassembly whose parts all override its colour. Every other word and scenario is restated unchanged.
  - "A maker moves the viewer from the navigator" says the chip is filled with "the node's effective colour" and is neutral "when a shown node has no effective colour". Both become the colour the row shows. The scenarios "A maker reads visibility off the rows" and "A colourless node is shown" keep their names; their wording moves from the node's effective colour to the colour its row shows, because as written the second would contradict the Enigma case itself (a group with no effective colour that now shows its parts' colour). One scenario is added. Every other word and scenario is restated unchanged.
  - "A viewer host can inspect the rendered assembly" is restated word for word, with one scenario added: a host reading a group whose parts share one colour is still given the group's own effective colour.

## Impact

- Source: `packages/machinome-viewer/machinome/viewer/web/widget/src/navtree.ts` (the pass, `NavigatorRow.color`'s meaning, the header comment), `src/navigator.ts` (one comment). Nothing in `tree.ts`, `viewer.ts`, `assembly.ts`, `inspector.ts` or `widget.ts` changes.
- Tests: `src/navtree.test.ts`, `src/navigator.test.ts`, `src/tree.test.ts`.
- Interfaces: viewer API stays 30 (`machinomeViewerApi` in the widget's `package.json`) and the document versions stay 1 to 14 (`machinomeDocumentVersions`). The snapshot's fields and their meaning do not change. The navigator's class names, custom properties and options do not change; `--machinome-nav-node-color` carries the row's colour as before, which for a row with children may now be its parts' colour.
- Hosts: the Studio mounts this navigator (`machinome-studio/floor/frontend/src/main.tsx:305-306`) and reads no `AssemblyNode.color` (its `machinome-viewer.d.ts` declares the type; no source reads the field), so its Model panel gains the rule with no Studio change. The export page and the inspector mount the same navigator.
- Manual: no page of the manual states which colour a row or its chip shows (`packages/machinome/docs/howto/browser-viewer.rst`, "Inspect the assembly"; `packages/machinome/docs/reference/viewer/layouts.rst`, "Navigator variables", which says only that `--machinome-nav-node-color` is per-row data the component writes). No page changes.
- Records: CHANGELOG bullet; `workflow/warts.md` entries; `evidence.md`.

Standalone viewer cycle in the framework worktree `machinome/WTs/colour-a-node-by-what-it-holds`, branch `colour-a-node-by-what-it-holds`, based on framework `main` at `6ee00abc221872a959d3e0dbf714e8314b0e67ec`. Integration into `main`, pushing and publication remain the pilot's.

Authority: the pilot asked for the change on 22 November 2026 in the words quoted above and directed "use opus subagents for propose and apply", with the adversarial review of the proposal and of the implementation delegated to the repository agent. That is advance authorization for proposal and apply, not a human review of this text.

Review (repository agent, 22 November 2026): the proposal's citations were checked against the base (`types.ts:77-79`, `serializer.py:1003-1008`, the five notify sites of `viewer.ts`, `navigator.ts:248`, `:423`, `:443`, the Studio reading no node colour) and hold; the delta was diffed against the baseline, and differs from it only in the sentences and the three scenario bodies named under "Modified Capabilities". Accepted as written. Two things are reversible choices the pilot has not seen and may overturn after looking at the page: a group that declares one colour while all its parts show another shows the parts' colour, and a hidden part still counts. Findings W1 and W2 are recorded, not taken up.
