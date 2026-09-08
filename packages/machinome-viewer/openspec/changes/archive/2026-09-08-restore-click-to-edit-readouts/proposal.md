## Why

Making every driver readout a permanently visible browser number input added
spinner arrows and field chrome that overwhelm the compact control surface.
Exact entry remains useful, but it should not change the established passive
readout appearance until the maker chooses to edit it.

## What Changes

- Restore the passive numeric readout presentation beside bounded sliders.
- Activate a text editor only when the maker clicks or keyboard-activates the
  readout, with exact finite values committed by Enter or focus loss.
- Remove native number-input spinner arrows while preserving exact values that
  lie beyond the slider's visual range.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: Refine exact bounded-driver entry into a passive
  click-to-edit interaction without persistent input chrome.

## Impact

The widget's driver-row DOM, interaction tests, README, changelog, and viewer
package behavioral specification change. The host API and document schema do
not change.
