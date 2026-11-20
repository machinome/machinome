# Enigma I: which rebuilt flexible parts actually change

A viewer-side measurement on a committed mechanical project's own page,
taken to size the second finding of `workflow/warts.md`'s "Enigma I
(2026-11-20…)" section before a change is cut from it. No project or
framework source is copied here; the page is an ignored build artifact of
the project.

## Pinned inputs

- Project `enigma-i` at `081f4e6`, `_build-page/`, manifest SHA256
  `a8769deec38e3fbf0dca2b826ef4b7779d29d2137ad7977e2f34ed9d58326fc0`: 426
  flexible parts among 3,347 meshes.
- Viewer source at `69cf7a3f` (`keep-a-live-model-parsed` integrated), built
  unminified from the widget's own entry with a handle on the scene.
- Headless Chromium through Playwright on an AMD Ryzen 9 5900X virtual
  machine, no GPU. Every WebGL draw call is counted and not executed, so the
  times are script only.

## Method

Between animation frames a tracker reads, for every mesh, the `version` of
its position attribute; a rise is a refill (`FlexibleShape.evaluate` sets
`needsUpdate`). For every refilled mesh it also sums a weighted sample of the
position array (every seventh float) and compares the sum with that mesh's
previous one; a different sum is a part whose vertex data changed. A part
whose data changed in a way the sample cannot see would be counted as
unchanged; none of the conclusions below rests on a single part. Each
instruction is its own button, pressed by `element.click()`. Single run.

## Result

| Instruction (declared seconds) | Parts refilled per frame | Parts whose data changed, whole instruction | Triangles refilled | Triangles in the parts that changed | Script per refilling frame, ms | Press task, ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Press (2) | 86 | 9 | 8,470,912 | 2,328,800 | 334 | 678 |
| Release (2) | 86 | 8 | 8,470,912 | 2,205,872 | 305 | 606 |
| Key B (0), a different key | 86 | 0 | 8,470,912 | 0 | (one frame) | 313 |
| Right wheel on (0.4) | 86 | 0 | 8,470,912 | 0 | 183 | 670 |
| Right wheel back (0.4) | 86 | 0 | 8,470,912 | 0 | 175 | 642 |

The nine parts a Press changes have 670,512, 670,512, 236,208, 236,208,
236,208, 153,648, 122,928, 1,288 and 1,288 triangles. In a median frame of
the Press seven of the 86 refilled parts received different data.

For comparison, from the archived
`openspec/changes/archive/2026-11-20-keep-a-live-model-parsed/evidence.md`:
an instruction that refills nothing costs 47 to 56 ms in its press task and
27 to 30 ms per changing frame (the flap and the hood), and selecting the key
already selected costs 41 to 52 ms.

## What it shows

A wheel step and a key selection rebuild 86 flexible parts, 8.47 million
triangles, of which none changes. A key press rebuilds the same 86 of which
nine change, 27 % of the triangles.

## Not measured

What the frame would cost with the unchanged parts skipped; any GPU's frame
time; the cost of evaluating the parameters alone, without the refill.
