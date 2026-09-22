## Context

`ExactLeafNode.shape()` first reads a current BREP. When the BREP is stale, it currently tries `self.model` before calling `render()`. That attribute stores SCAD presentation after `assemble()`, including `_ArtifactImport` for a native leaf. The Curta `CounterOperatingFixtureTest` reaches this state during an exact fusion and OCCT receives the SCAD object.

## Goals / Non-Goals

**Goals:** Return native local geometry for a stale exact leaf after assembly; keep current BREP reuse; prove the real Curta fixture and an isolated lifecycle regression.

**Non-Goals:** Change artifact currency, SCAD presentation, exact fusion rules, or any viewer contract.

## Decisions

- On a current BREP, continue returning `cached_shape()` without rendering. On a stale BREP, call the adapter's `render()`, validate the native result, and convert it with `shape_from_rendered()`. Do not use `self.model`: it is presentation state, not a native-geometry cache.
- Test both stale and current BREP paths. The stale test first assembles a leaf, then makes only its BREP stale inside a test-owned temporary build directory and asks for its native shape through an exact fusion. The current test proves no render is needed.
- Run the originating `CounterOperatingFixtureTest` against this worktree while preserving the project's existing build cache. The fix is accepted only if the measured candidate comparison completes.

## Risks / Trade-offs

- A stale BREP can cause a second native render after an earlier assembly. That cost is limited to invalid artifacts and is required to avoid returning stale geometry.
- The project's runtime graph may contain another unrelated error after the `_ArtifactImport` failure is removed. Report the next failure separately rather than widening this correction without evidence.
