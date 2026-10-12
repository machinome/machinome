## 1. Browser acceptance coverage

- [x] 1.1 Replace the exact workspace-ratio assertion with coverage that both desktop workspace areas remain visible and usable.
- [x] 1.2 Extend browser coverage to require the compact chat controls, removal of visible foreman-specific chrome, and transcript auto-scroll after a live foreman message.

## 2. Chat workspace implementation

- [x] 2.1 Allocate equal desktop workspace rows to artifact inspection and chat while preserving the narrow-window layout.
- [x] 2.2 Restructure the conversation markup and styling into a compact, independently scrollable participant-attributed chat transcript with a message field and `Send` control.
- [x] 2.3 Scroll the transcript to the newest foreman message after it is rendered, without scrolling the broader workspace.

## 3. Verification

- [x] 3.1 Run the focused browser lifecycle coverage and the full relevant test suite.
- [x] 3.2 Build the frontend and inspect the resulting workspace/chat presentation for visual regressions.

## 4. Keyboard composer refinement

- [x] 4.1 Add browser coverage for Enter sending and Ctrl+Enter inserting a newline without sending.
- [x] 4.2 Implement the specified keyboard behavior while preserving the `Send` button submission path.
- [x] 4.3 Build the frontend and run the focused composer coverage.
