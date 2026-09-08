## Context

Bounded drivers gained exact entry through an always-visible native number
input. That control exposes browser spinner arrows and input chrome even while
the maker is only observing or dragging, replacing the compact fixed-width
readout the viewer previously used.

## Goals / Non-Goals

**Goals:**

- Make the resting readout visually identical to the passive fixed-width
  presentation.
- Preserve mouse and keyboard access to exact entry.
- Keep out-of-range driver values exact while the range input pins visually.

**Non-Goals:**

- Change driver units, conversion, range semantics, host APIs, or viewer API
  version.
- Add a general form-control framework.

## Decisions

Render a passive span and a hidden text input in the same readout container.
Activation swaps to the text input, selects its contents, and commit occurs on
Enter or blur; Escape cancels. A text input was chosen over styling a number
input because native spinner rendering varies by browser and is the unwanted
noise itself.

Keep the passive span as the only visible element outside editing and reuse
its prior fixed-width, right-aligned, tabular-number styling. This was chosen
over leaving a borderless input permanently visible because focus, selection,
and browser autofill affordances still alter the resting presentation.

Parse only non-empty finite numbers. External and ramp updates continue to
refresh the passive value but do not overwrite an active edit.

## Risks / Trade-offs

- [Blur can be caused by an incidental click] -> Commit valid text and revert
  invalid text deterministically.
- [A text input lacks native numeric validation] -> Validate finite numeric
  text before calling the existing conversion and driver update path.

## Migration Plan

Replace the permanent number input in the existing driver-row builder and
retain its state conversion functions. Rollback restores the previous input
element without affecting host contracts or saved documents.

## Open Questions

None.
