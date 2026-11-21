# Evidence: share one material per appearance

The applier's record (tasks 1.2 to 6.2, 7.1 and 8.1). Tasks 7.2, 8.2 and
8.3 are the reviewer's and are not recorded here. Paths are relative to
`packages/machinome-viewer/` unless they say otherwise; the widget is
`machinome/viewer/web/widget/`.

## 1.2 The bench

- Worktree `machinome/WTs/share-one-material-per-appearance`, branch
  `share-one-material-per-appearance`, HEAD `95e15739` ("plan: share one
  material per appearance"), its parent `e72d1ae7ee8e4ce2a4d9828eba48b70398b6d729`;
  `git status --short` empty before any write; `git diff --stat e72d1ae7
  HEAD` touched only the change directory, `workflow/warts.md` and the
  opening evidence, so the source at HEAD was the base source.
- `openspec validate share-one-material-per-appearance --strict`: "Change
  'share-one-material-per-appearance' is valid".
- three.js installed: 0.156.1.

## 2.2 Red on the base

`src/shared-materials.test.ts` run on the base source (the final form of
the file, run again against the four base source files restored
temporarily after the implementation, then the implementation restored
and compared byte for byte): 22 tests, 18 failed, 4 passed.

| Test | Base | Why |
|---|---|---|
| R1 | red: `expected 12 to be 5` | one material object per mesh, 12 of 12 |
| R2 | red: `expected 5 to be 1` | five changes of material along six drawn parts |
| R3 | red at step "hover tail" | the hovered part's own material's `emissive` written in place: `Color{b:0,g:0,r:0}` to `Color{b:0.1844749944900301,g:0.1844749944900301,r:0.1844749944900301}` |
| R4 | red: `expected +0 to be 9` | none of the new tree's nine meshes points at a material of the old tree |
| O1 | green | its constants were recorded here (below) |
| O2 | red: `holder.mesh is not a function` | the holder's new method is absent |
| P1, P2 (10 cases) | red: `this.holder.mesh is not a function` | the same |
| L1 | green | every part has its own material |
| L2 | red: `bench.holder.counts is not a function` | the reader is absent |
| L3 | red: `holder.counts is not a function` | the same |
| L4 | green | a part's own material is ghosted again |
| L5 | green | |

Each design-stated base fact used by a test was checked here: R1's 12, R2's
5, R3's first hover writing `emissive`, R4's nothing shared, and the
fresh-load order (a part, its two markings in declaration order, its child,
then the flexible part and the later parts: O1's "load" row below).

## O1: the constants, recorded on the base

Recorded by running O1 on the base source before any source change, with a
temporary line printing the records as JSON (removed after recording); the
printed records were pasted into `O1_EXPECTED` as one array of lines per
step, joined with `\n`, numbers as `String` printed them (`-0` would be
written `-0`; none occurs). The constants have not been regenerated. On the
implementation O1 passes against them unchanged (task 4.4 and every later
run).

The first twelve steps are design Decision 7's. Nine follow them (a
decision of the applier's, below): the replacements repeated under a
standing ghost and a hover, then a dim with a hover and a colour chosen
under it. The raw printed output, one block per step:

```text
21
load
  opaque: lamp bare body body#digits body#band body/knob spring plain tail
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

hover tail
  opaque: lamp bare body body#digits body#band body/knob spring plain tail
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

highlight body kept
  opaque: lamp bare body body#digits body#band body/knob spring plain tail
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

put back
  opaque: lamp bare body body#digits body#band body/knob spring plain tail
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

highlight body dimmed
  opaque: lamp bare body body#digits body#band body/knob spring plain tail
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,0.43415363616478553,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.274238227032548,0.2582686430685311,0.21602229684422222] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.01158666829780323,0.04650391254045119,0.11149137234002374] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.21133956859663927,0.020231900564327443,0.020231900564327443] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

put back
  opaque: lamp bare body body#digits body#band body/knob spring plain tail
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

highlight body ghosted
  opaque: body body#digits body#band body/knob
  transparent: lamp bare plain tail spring
  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false

hover plain, ghosted
  opaque: body body#digits body#band body/knob
  transparent: lamp bare plain tail spring
  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,1,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false

put back both
  opaque: lamp bare body body#digits body#band body/knob spring plain tail
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

flip the choice
  opaque: lamp bare body body#digits body#band body/knob spring plain tail
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

republish
  opaque: lamp body body#band body/knob spring plain tail extra extra/pin bare body#digits
  transparent: 
  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

artifactChanged body.stl
  opaque: lamp body#band body/knob spring plain tail extra extra/pin bare body#digits body
  transparent: 
  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

reload
  opaque: lamp bare body body#digits body#band body/knob spring plain tail extra extra/pin
  transparent: 
  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

highlight knob ghosted, hover tail
  opaque: body/knob
  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring
  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false

flip the choice back under it
  opaque: body/knob
  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring
  bare: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[0.5271151256969157,0.5271151256969157,0.5271151256969157] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  plain: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false

republish under it
  opaque: body/knob
  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring
  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  plain: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false

artifactChanged lamp.stl under it
  opaque: body/knob
  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring
  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  plain: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false

reload under it
  opaque: body/knob
  transparent: lamp bare body body#digits body#band plain tail extra/pin extra spring
  bare: MeshNormalMaterial color=none emissive=none transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[1,1,1] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.7835377915215659,0.7379104087672317,0.6172065624120635] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  plain: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=true opacity=0.15 depthWrite=false side=0 polygonOffset=false flatShading=false

highlight dimmed in its place, hover lamp
  opaque: lamp bare body body#digits body#band body/knob spring plain tail extra extra/pin
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.274238227032548,0.2582686430685311,0.21602229684422222] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshStandardMaterial color=[0.01158666829780323,0.04650391254045119,0.11149137234002374] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.21133956859663927,0.020231900564327443,0.020231900564327443] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

flip the choice under a dim
  opaque: lamp bare body body#digits body#band body/knob spring plain tail extra extra/pin
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[0.35,0.2428551164499914,0.0657372703015821] emissive=[0.1844749944900301,0.1844749944900301,0.1844749944900301] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshStandardMaterial color=[0.01158666829780323,0.04650391254045119,0.11149137234002374] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0.4019777798219466,0.4969329950515914,0.6038273388475408] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.21133956859663927,0.020231900564327443,0.020231900564327443] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false

put back both again
  opaque: lamp bare body body#digits body#band body/knob spring plain tail extra extra/pin
  transparent: 
  bare: MeshNormalMaterial color=none emissive=none transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body#band: MeshStandardMaterial color=[1,1,1] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body#digits: MeshStandardMaterial color=[0.005605391621829108,0.015996293361446288,0.033104766565152086] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=2 polygonOffset=true flatShading=false
  body/knob: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  body: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra/pin: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  extra: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  lamp: MeshStandardMaterial color=[1,0.6938717612856897,0.1878207722902346] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  plain: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
  spring: MeshStandardMaterial color=[0.033104766565152086,0.13286832154414627,0.31854677811435356] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=true
  tail: MeshStandardMaterial color=[0.6038273388475408,0.057805430183792694,0.057805430183792694] emissive=[0,0,0] transparent=false opacity=1 depthWrite=true side=0 polygonOffset=false flatShading=false
```

What the rows show on the base, as design Decision 3 states: after
"republish", `bare` (coloured from none: a replaced material) and
`body#digits` (a retained marking recoloured) move to the end, and the
replaced `tail` and the added `extra` keep the order they were made in
during preparation; after "artifactChanged body.stl", `body` moves to the
end; a reload restores document preorder; the chosen colour of `lamp`
keeps its place.

## 2.3 B1 on the base bundle

- Bundle built from the base source with `npm run build`:
  `a183cb1d3ae18e65bfc96a24a41bc5ebb1d30bef283430272bc9533abf1b9b6b`, kept
  under the widget's `.scratch/` during the work and deleted at the end.
- `tests/test_asset_load_order.py::AssetLoadOrderTest::test_coincident_plates_keep_the_shipped_order_through_overlays_and_a_chosen_colour`
  on it: **1 passed, 3 deselected in 1.14s**.
- Before that pass the first form of B1 failed on the base bundle at the
  dim: `AssertionError: 201 not less than 201 : the dimmed plate is not
  darker: (201, 30, 30)`. Cause, found by reading the canvas directly: the
  test called `page.evaluate("window.clear = viewer.highlight(...)")`, and
  Playwright invokes an expression that evaluates to a function, so the
  highlight's own put-back ran at once and no highlight stood. The two
  highlight calls were wrapped as `() => { window.clear = ...; }`, as
  `test_widget_e2e.py` writes them; no assertion changed. The kept
  highlight's frame equalities would have passed vacuously in the first
  form; the dim step's "darker" and the two `assembly()` colour checks are
  what show the overlays and the choice took effect.

## 3.2 and 4.4

- 3.2: `tsc --noEmit` clean. The file: 17 failed, 5 passed. P1, P2 and O2
  could not be green at 3.2 as the task expects: they need the kinds
  `RIGID`, `MARKING` and `FLEXIBLE`, which the design places in `tree.ts`
  and `flexible.ts` (task 4). L1, L2, L4 and L5 passed, but vacuously,
  since the tree did not yet make its meshes through the holder.
- 4.4: `tsc --noEmit` clean. First run: 20 passed, 2 failed, both test
  defects of mine, fixed in the test without touching an assertion's
  meaning: O2 gave its random render orders to its own items while
  three.js's list reads `object.renderOrder` (now set on the object), and
  L4 (below, "L4"). Then 22 of 22 green, O1 against the base constants.

## 5.1 Existing tests

Each file run alone after its change, green:

- `src/presentation.test.ts`: 18 passed.
- `src/color.test.ts`: 22 passed.
- `src/tree.test.ts`: 71 passed.

What changed (E1 to E3), assertion before and after:

- E1, `presentation.test.ts`: every mesh is made by the owner under test
  (`owner.mesh(geometry, RIGID, colour)`, or `RIGID` with no colour),
  created after the owner instead of before it. Two kinds declared in the
  test keep the bases the viewer's kinds cannot make: `glowing(0x010203)`
  for "tints ..." (was `standard(hub).emissive.setHex(0x010203)`),
  `glowing(0x050505)` for the six orders (was `setHex(0x050505)`), and
  `GLASS`, transparent at 0.5, for "ghosts the others ..." (was
  `standard(glass).transparent = true; opacity = 0.5`). In "ghosts the
  others ...", the three `version` assertions
  `expect(blade.material.version).toBeGreaterThan(versions[0])`,
  `expect(plain.material.version).toBeGreaterThan(versions[2])`,
  `expect(glass.material.version).toBe(versions[1])` and, after the
  put-back, `expect(blade.material.version).toBeGreaterThan(versions[0] + 1)`
  became: `blade` and `plain` point at materials other than their plain
  ones, `glass`'s points at one whose `transparent` is its plain
  material's, the three plain materials' `version`s are unchanged after
  the ghost and after the put-back, and after the put-back each mesh
  points at its plain material. Every other assertion is as it was.
- E2, `color.test.ts`: "resolves finite zero/nonzero ...":
  `expect(original.material).toBe(material)` became
  `expect(placeOf(original)).toBe(place)` and
  `expect(original.material).toBe(holders(powered ? ON : OFF))`, where
  `holders(colour)` makes a probe mesh of that colour through the tree's
  holder (the tree is now given an explicit holder), reads its material
  and releases it; mesh and geometry identity stand. "rebases every
  overlay ... preserving material identity" was retitled "... keeping each
  mesh's place"; its meshes are made with `owner.mesh(BoxGeometry, RIGID,
  OFF)`, `expect(target.material).toBe(material)` became
  `expect(placeOf(target)).toBe(place)`, and its disposal
  `target.material.dispose()` / `other.material.dispose()` became
  `owner.release(...)`; its colour assertions stand. "keeps an inherited
  flexible color ...": both `expect(spring.material).toBe(material)` became
  `expect(placeOf(spring)).toBe(place)` and the colour (`hex(...)` is
  `ON`); geometry identity stands. "judges a chosen color without showing
  it ..." holds as written.
- E3, `tree.test.ts`: the two fresh-load order tests keep every assertion
  and gain `placeOf(first) < placeOf(second)` and the order read through
  `drawOrderSort` (a reversed copy sorted by it equals the document order),
  for the sibling pair and for the model and its two markings. The three
  disposal tests, "leaves a decal's material alone ..." and "replaces the
  material of a retained marking ..." hold as written.

No test the design said holds as written failed.

## 5.2 Mutations

Each applied alone to the implementation (by a script under `.scratch/`),
`src/shared-materials.test.ts` run, the files restored from saved copies
and compared with `cmp` (all byte-equal after every mutation):

| Mutation | Red |
|---|---|
| M1, three.js's default opaque sort in the order helper | O1 (step 0, "load": `lamp plain bare tail ...`) |
| M2, `setBaseColor` takes a new place | O1 (step 9, "flip the choice") |
| M3, `recolor` keeps the place | O1 (step 10, "republish") |
| M4, a hover writes `emissive` into the shared material in place | R3 (at "hover tail"), O1, P1 |
| M5, `release` disposes the mesh's material whatever its counts | L1 (first step: a live mesh on a disposed material), R4, L2 |
| M6, appearances keyed by the colour string | R1 (`expected 8 to be 5`), P2 four spellings, P2 lamp |
| M7, ghosted variants released at zero pointers | L4 |
| M8, lit variants kept | L3 (`expected 3 to be less than or equal to 2`) |
| M9, a dimmed colour from the material the mesh points at, not from `P` | P1, P2 (the lamp under a dim; a colour chosen under a dim), O1 |
| M-W, `renderer.setOpaqueSort` removed, bundle rebuilt | B1 red at load: `30 not greater than 306.0 : the last red plate must show at load: (30, 30, 204)` (the blue plate shows) |

Two mutations were first applied in a form that did not do what they
name, and were applied again:

- M1, first form: `record`'s default argument set to `undefined`. Nothing
  went red, because `drawn`'s own default parameter then supplied
  `drawOrderSort` again. Second form: `drawn` sorts with
  `list.sort(undefined, null)`, three.js's default; O1 red.
- M4, first form: the hovered meshes' materials written with the hover
  grey AFTER the owner pointed them at their looks. Only P1 went red: the
  material written was then the hovered variant, which already carries the
  hover grey, so R3's sequence (a hover of one part, and of a colourless
  one) wrote no new value. Second form: the write BEFORE the owner points
  them, which writes the shared plain material in place; R3, O1 and P1 red.

M-W's bundle: `d9463e1552df1ab29fb150b6ec6b170e4b4b420bd2ca0005e0682bf7413ffcff`;
after the restore `viewer.ts` compared byte-equal and the bundle was built
again.

## 5.3 Other widget tests, singly, unmodified

`flexible.test.ts` 32 passed; `flexible-rebuild.test.ts` 18;
`parity-fixture.test.ts` 16; `document.test.ts` 65; `partControls.test.ts`
52; `partSurface.test.ts` 36; `inspector.test.ts` 22; `navigator.test.ts`
26; `flat-pass-parity.test.ts` 52. All green.

## 6.1 The gate

- Whole widget suite, first run: Test Files 4 failed | 71 passed | 1
  skipped (76); Tests 1 failed | 1928 passed | 2 skipped (1931). Three of
  the failed files were my byte copies of test files under the widget's
  `.scratch/`, which vitest collects (they fail at import from that
  directory); the failed test was P1, `Test timed out in 5000ms` under
  the suite's load (2.6 to 2.8 s alone). The copies were renamed out of
  the test pattern and P1 given a 60-second timeout.
- Whole widget suite, second run: **Test Files 71 passed | 1 skipped (72);
  Tests 1911 passed | 2 skipped (1913)**. The skips:
  `src/run/profile-installed-benchmark.test.ts` (`it.skipIf(!path)`,
  `CURTA_INSTALLED_PROFILE_DOCUMENT` unset) and one test of
  `src/run/profile-contact.test.ts` (`it.skipIf(!actualCurtaDocument)`,
  `CURTA_PROFILE_V13_DOCUMENT` unset). The cost gates of
  `src/run/cost.test.ts` passed.
- `tsc --noEmit`: clean.

## 6.2 Build and the Python suite

- Bundle built from the implementation with `npm run build`:
  `878801de6adcd3c4c273f779d72672dcaf99140e86f6fb5cbf0a2f4b32cc6f7b`
  (`machinome/viewer/web/widget/dist/machinome-viewer.js`, ignored).
- `python -m pytest tests -rs` on the bench's venv: **285 passed, 2
  skipped, 71 warnings in 283.48s**. All four tests of
  `tests/test_asset_load_order.py` passed, B1 among them, on the
  implementation bundle. The two skips: `tests/test_curta_drawing.py:375`
  and `:469`, "the Curta's own builds are not at
  .../WTs/projects/Calculators/Curta-Type-I-3x/_build" (a project build
  the bench does not have). The warnings are Pillow's deprecation of
  `Image.getdata` in `test_widget_e2e.py` and are not new.

## Deviations from the design, and decisions it left open

- **The holder's public surface as built** (`presentation.ts`):
  `MaterialPresentation` with `mesh(geometry, kind, color)`,
  `recolor(mesh, color)`, `setBaseColor(mesh, color)`, `release(mesh)`,
  `setHover(meshes)`, `setHighlight(state)`, `forget()`, `drop()`,
  `isGhosted(mesh)`, `dispose()` and `counts()`; and beside it the
  exported `MaterialKind` (`{ name, make(color) }`), `drawOrderSort`
  (the design's code, verbatim), `placeOf(object)`,
  `releaseMaterial(mesh)`, `HolderCounts` and a `RenderItem` interface
  declaring the six fields the comparator reads (three.js's own
  `RenderItem` type lives in an internal path of `@types/three`). `counts()`
  returns the held meshes, the held materials, and per appearance its kind,
  colour key, users, variants held other than the kept ghosted ones, and
  kept ones.
- **Variants are keyed by the values they carry**, within their
  appearance: a look's values (emissive, colour, `transparent`, `opacity`,
  `depthWrite`, by components under `Object.is`) equal to the plain
  material's point the mesh at the plain material, and two looks with
  equal values share one variant. This is the design's two sharing rules
  ("where a look's values equal P's", "where two looks' values are equal")
  taken literally; the look-to-material lookup is computed once per
  appearance and look within one presentation (a per-call memo), so
  nothing accumulates across highlight colours.
- **A plain material's values are read once**, when it is made, into the
  appearance (the shipped `record` of a base, done once); variants are
  computed from those, never from the material a mesh points at.
- **`setBaseColor` on a mesh whose colour value is none** keeps its
  appearance and presents it (the shipped `base.color?.set` set nothing
  there). Unreachable in the viewer: a rebase happens only between two
  colours.
- **`releaseMaterial` keeps the mesh's entry in the module `WeakMap`**
  after a release, so that a second disposal of the same mesh reaches the
  holder, which ignores it, rather than the path for a mesh no holder
  made, which disposes the material: `FlexibleShape.dispose` has no guard
  against being called twice, as `disposeMesh` has.
- **Release order inside one step:** the new material's count rises
  before the old one's falls, and a mesh that moves appearance takes its
  new appearance's user before leaving the old, so moving within one
  appearance never drops it to zero users.
- **`MARKING.make`** passes its colour value to `markingMaterial` as a
  `THREE.Color`; a marking's colour is never none.
- **O1 has nine steps after the design's twelve:** a ghost of a nested
  part with a hover standing; the choice flipped under it; a second
  republish under it (a part coloured, one put back to no colour, a
  marking recoloured, a flexible part's spec and a nested model replaced);
  `artifactChanged` and a reload under it; a dim of two paths with a
  hover; the choice flipped under the dim; both put back. They exercise
  the re-resolution of a standing highlight on new meshes and the
  transparent list, and were recorded on the base with the rest.
- **O1's bench** drives the tree as `viewer.ts` does: `forget` in a
  republish's `beforeCommit`, `forget` before `artifactChanged`, the new
  tree made and updated before `forget` and the old tree's disposal in a
  reload, and the standing highlight re-resolved after each as
  `presentHighlight` resolves it (lit: every mesh under the paths; others:
  every other mesh of the tree). The hover from "hover tail" stands until
  "put back both".
- **R3** runs O1's steps and compares every material seen against its
  snapshot after each step, property by property by name, so a failure
  names the property.
- **L1:** the failed `artifactChanged` is called on the tree directly,
  without the viewer's `forget` before it, so that the highlight stands
  through it as the step requires (the viewer forgets first and, on a
  failure, does not re-present). "A mesh released under a hover" is a
  republish removing one of two hovered parts of one colour with no
  `beforeCommit`, so the hover still stands when the part is released;
  in the viewer a republish forgets first, so this is reachable only
  through the tree.
- **L4's lit part has no colour.** With a coloured lit part the second
  ghost hands out a new lit variant for it: lit variants are released at
  the put-back (design Decision 4; L3 holds it), so the same object cannot
  come back. A colourless part lit is drawn with its plain material, so
  the second ghost hands out exactly the first's materials and makes none,
  as L4 states. **Finding:** design Decision 6, "A second ghost: reuses
  the kept ghosted variants; nothing is made or compiled", holds for the
  ghosted parts; the lit part, when its appearance has an emissive, has
  its lit variant made again (a clone, drawn with the plain material's
  program, so nothing compiles). No picture is affected.
- **P1's composition:** ten meshes cannot hold two of each of the eight
  appearances P1 draws from (rigid red in four spellings, rigid without
  colour, rigid `#336699`, marking white in three spellings, flexible
  `#336699`, flexible without colour, the declared emissive kind, the
  declared glass kind), so each sequence takes five of the eight, two
  meshes each, a spelling drawn per mesh; the test asserts that all eight
  were covered over the 200 sequences and that more than 7,000 steps were
  checked. Console warnings (an unreadable colour) are counted for the
  oracle and the holder separately at every construction, recolour and
  rebase, and the two counts must agree.
- **E2, "resolves finite zero/nonzero ...":** "the material the holder's
  for the new colour" is read by a probe mesh made through the same holder
  and released, which required giving that test's tree an explicit
  holder.
- **B1** also asserts, after each `setDriver`, that the first plate's
  colour in `assembly()` is the chosen one, so a frame equality cannot
  pass because the choice did not happen.

## 8.1

One bullet added at the end of "Unreleased" in `CHANGELOG.md`.

## Reviewer's record: review of the implementation and task 7.2

Written by the repository agent, 21 November 2026, after the applier stopped.

### Review of the implementation

`src/presentation.ts` was read line by line against design Decisions 1 to
4, and the diffs of `src/tree.ts`, `src/flexible.ts` and `src/viewer.ts`
against task 4: the comparator is the design's code block; a look's values
are computed from the values of the plain material read once when it is
made; a place is given in `mesh()` and in `recolor()` and nowhere else; the
viewer makes one renderer and one scene, and a mesh is constructed at two
sites only, both through the holder. No difference from the design found.

**The constants of O1, again.** The test file was copied into a clean
checkout of the base (`e72d1ae7`, another bench of the repository), run
there and removed: O1 passes on the base with the recorded constants; R1 to
R4 fail there on their counts (12 for 5, 5 for 1, the write at "hover
tail", 0 for 9); L1, L4 and L5 pass; the rest fail at the absence of the
holder's methods. The constants are the base's.

**Faults of the reviewer's own.** Twenty, none of them from the design's
list, were planted one at a time in `src/presentation.ts`, `src/tree.ts`
or `src/flexible.ts`, with `src/shared-materials.test.ts`,
`src/presentation.test.ts`, `src/color.test.ts`, `src/tree.test.ts` and
`src/flexible.test.ts` run against each and the files restored and checked
by digest. The verdict script was first tried on an edit of a comment (no
test red) and on one fault known to be real.

| Fault planted | Result |
|---|---|
| a comment edited (the control) | passes, as it must |
| a recolour into the appearance the mesh already has keeps its place | passed: a gap, closed below |
| a chosen colour read afresh instead of set on the colour the mesh had | P1, P2 red |
| hovered wins over lit | P1, P2 and one test of `presentation.test.ts` red |
| a dim darkens the recorded plain colour itself | O1, P1, P2 and five other tests red |
| a ghost takes the ghost opacity whatever the plain one is | passed: a gap, closed below |
| a variant left by its last mesh is not disposed | L3 red |
| an appearance without meshes leaves its variants undisposed | L2, L3 red |
| the comparator ignores `renderOrder` | O2 red |
| a colour choice takes a new place | O1 and two tests of `color.test.ts` red |
| a retained marking that changes colour keeps its place | O1 red |
| a new highlight does not put back what the previous overlays touched | 16 tests red |
| a part both lit and among the others is treated as an other too | P1, P2 red |
| colours equal after rounding to eight bits share an appearance | passed: a gap, closed below |
| a mesh takes its place again when its model arrives | O1 and the two fresh-load tests of `tree.test.ts` red |
| a flexible part made by a republish gets a holder of its own | O1 red |
| disposing a rigid mesh does not release its material | L2 and three disposal tests of `tree.test.ts` red |
| disposing a flexible part does not release its material | L2 red |
| a released mesh stays counted in its appearance | L2 and three disposal tests red |
| a marking is made with the rigid kind | O1 and four marking tests red |
| appearances keyed by colour alone, across kinds | O1, P1, P2 red |

Seventeen were caught as the tests stood, none is equivalent, and three
showed gaps in the proof, not in the implementation:

- **A recolour into the same appearance.** When a republish both gives a
  colourless part a colour and replaces its model, the replacement mesh is
  reserved with the new colour and the commit then replaces its material
  again, because the part had none; the shipped code makes a new material
  there whatever the colour, so the mesh moves after everything made since
  it was reserved. O1's republishes never do both to one part. The
  reviewer added O3: two siblings re-modelled by one republish, the first
  also coloured, drawn second, first. O3 passes on the base and on the
  implementation, and is red with the fault planted again.
- **The ghost's opacity as the smaller of two.** No kind in the suite had
  a plain opacity below the ghost's 0.15, so `Math.min` was held by
  nothing. The reviewer added a kind declared by the test at opacity 0.1
  and a case of P2 on it; red with the fault planted again.
- **Colours keyed exactly.** Every colour in the suite was a hex colour or
  a name equal to one, and those survive rounding to eight bits. The
  reviewer added a case of P2 with `rgb(50%, 0%, 0%)` beside `#800000`,
  which print as the same hex and are not the same value: two appearances,
  each with its own colour; red with the fault planted again.

With the three added, all twenty faults turn a named test red.

The applier's finding about design Decision 6 stands: "a second ghost …
nothing is made" holds for the ghosted parts; the lit part's variant is
released at the put-back and made again, a clone on a program already
compiled. Measured below: a second ghost takes 22 to 27 ms, against 92 to
101 for the first.

Final gate with the three added cases: the widget suite 71 files passed and
1 skipped, 1,914 tests passed and 2 skipped (the two environment-gated
Curta profile tests), no failure; `tsc --noEmit` clean; the bundle rebuilt
with the SHA256 the applier recorded,
`878801de6adcd3c4c273f779d72672dcaf99140e86f6fb5cbf0a2f4b32cc6f7b`; the
Python suite on that bundle 285 passed and 2 skipped (the Curta's own
builds are not on this machine), B1 among the passed.

### 7.2 The Enigma I page

Method: `workflow/evidence/enigma-material-per-part-cost-2026-11-21.md`'s.
`enigma-i` at `081f4e6`, its `_build-page/`, headless Chromium
(Playwright) on a virtual machine with no GPU. The viewer was built
unminified from its unedited source with a scratch entry exposing the
renderer, the scene and the mounted handle: once from the base
(`e72d1ae7`) and once from this bench, each with molejo's `main`
(`363847a`) and with npm molejo 0.2.0. Each build ran in its own page
load. Times are script time, with WebGL draw calls counted and not
executed; pictures are really drawn by the software rasteriser at 998 by
868 and read back from the canvas in the task that drew them.

**The page declares no part controls** (`controls()` is empty), so a hover
cannot happen on it; hover is held by the widget's tests and by the
browser tests on fixtures that declare controls. The highlight was applied
through the mounted handle to `keyboard/front_row/keys-0` (eleven meshes,
in sight in the opening view; six lit variants are made for them).

**Pictures.** Forty per page load, the same scripted sequence in each: five
views at rest; the same five with a key held (a lamp lit by the colour the
model chooses); two after the release; the three highlights (others kept,
dimmed, ghosted) in two views, each followed by its put-back; under a dim
and under a ghost, a key pressed, the highlight put back, applied again and
put back again, and the key released; the flap opened and closed; a wheel
stepped and stepped back. A key press steps the machine, so pictures are
compared between page loads at the same step, and inside one page load
only against a picture taken in the same state.

| Compared, picture by picture | Pictures that differ, of 40 | Pixels |
|---|---|---|
| The base, two page loads (the control for no difference) | 0 | 0 |
| The base and this change | 0 | 0 |
| The base and this change built without `setOpaqueSort` (the control for a difference) | 24 | one pixel in each, by 1, 2 or 17 of 255 |

Read from the scene in seven of those states (at rest, a key held, each
highlight, a key held under a dim and under a ghost), base against this
change: every one of the 3,347 meshes carries a material of equal type,
colour, emissive colour, metalness, roughness, flat shading, side,
transparency, opacity, depth write and polygon offset; the opaque list and
the transparent list the renderer last drew are in the same order. Without
the sort the looks are equal and the opaque order is not.

Inside each page load, base and this change alike: every put-back gives
the picture taken before its highlight (six of six); a highlight applied
again over a held key gives the first one's picture and its put-back the
first put-back's (four of four); the flap closed and the wheel stepped
back give the picture before them. No page error and no console error or
warning in any run.

**Counts.**

| | Base | This change |
|---|---|---|
| Material objects among the 3,347 meshes, at rest | 3,347 | 79 |
| under a highlight (kept, dimmed, ghosted) | 3,347 | 85 |
| after the put-backs, and at the end of the sequence | 3,347 | 79 |
| after a reload (`reload()`, 26 to 32 s here) | 3,347 | 79 |
| Changes of material along the opaque order, at rest | 3,346 | 1,293 |

After the reload the picture is the one before it, and the base's.

**Times**, in milliseconds, lowest to highest of the measured rounds.

| | Base | This change |
|---|---|---|
| A frame in which nothing moves, 9 rounds in 3 page loads and 6 in 2 | 23.9 to 29.1 | 17.5 to 22.7 |
| of it, the renderer's `render` | 21.6 to 25.1 | 14.8 to 19.0 |
| A frame of a key press, molejo's `main`, 6 and 3 rounds of Press and Release | 55.8 to 62.8 | 49.7 to 53.8 |
| pictures in its two seconds | 30 to 35 | 35 to 39 |
| A frame of a key press, npm molejo, 3 rounds each | 81.0 to 92.3 | 71.7 to 79.7 |
| pictures in its two seconds | 21 to 25 | 25 to 28 |
| Highlight, others kept: the call with its draw | 23.0 to 29.6 | 19.9 to 23.0 |
| a still frame while it stands | 24.7 to 28.8 | 17.2 to 19.7 |
| the put-back with its draw | 22.4 to 33.2 | 15.7 to 19.0 |
| Highlight, others dimmed: the call | 28.0 to 37.9 | 19.1 to 24.4 |
| a still frame while it stands | 23.7 to 29.0 | 15.9 to 19.8 |
| the put-back | 24.0 to 31.9 | 15.4 to 19.5 |
| Highlight, others ghosted: the first call | 210.7 to 223.7 | 91.5 to 101.4 |
| the second call | 55.1 to 60.0 | 21.8 to 26.8 |
| a still frame while it stands | 28.5 to 32.0 | 18.5 to 23.5 |
| the put-back | 53.4 to 60.0 | 17.2 to 20.2 |

The build without the sort gave a still frame of 18.1 to 19.7 ms in one
page load, against 18.5 to 20.5 with it in the page load beside it: the
order kept costs at most a millisecond or two here, and one pixel in 24 of
40 pictures is what it buys.

**The design's expectations** ("What the Enigma should show"): no pixel
differs: met. 79 materials at rest: met; under a dimming highlight the
meshes point at 85, one per appearance among the others and six lit, and
the plain materials the holder still holds beside them are not visible to
this count. A still
frame near 19 to 22 ms: 17.5 to 22.7. A key press lower than shipped: by
6 to 9 ms with molejo's `main` and 9 to 13 with npm molejo. Each highlight
call below the shipped figure and a second ghost with no compile: met.

**Limits.** Script time on one virtual machine; no GPU was involved, what
a change of material costs a graphics card was not measured, and nothing
was measured on a maker's hardware. The pictures are forty of one document
at one size on a software rasteriser; they cannot show that no view of no
document differs, which is what the order's test, the parity proof and the
coincident plates are for. Not exercised on this page: a hover (it
declares no controls), a republish or `artifactChanged` (the page makes
none), two viewers. The Enigma document is a project's and is not in this
repository; its pictures cannot be committed here.

