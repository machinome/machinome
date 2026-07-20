## 1. Framework dependency

- [ ] 1.1 Ratify and implement the linked solid-node public contract for one-shot conventional-model builds and development-time broker callbacks.
- [ ] 1.2 Verify the framework contract against a project whose root `__init__.py` exists and one whose model is missing.

## 2. Floor model boundary

- [ ] 2.1 Implement a floor adapter for the ratified framework build and development interfaces without importing project model Python.
- [ ] 2.2 Make the porter/shop-open flow build the conventional model before announcing an open browser location, with clean build-failure reporting.
- [ ] 2.3 Add broker storage and a locally validated callback endpoint that accepts only a successfully built model update.

## 3. Browser refresh

- [ ] 3.1 Serve the current functional-model state through the floor and render it in the artifact area.
- [ ] 3.2 Publish the model-change notification through the run SSE stream and reload the complete model state in the browser.
- [ ] 3.3 Preserve the last successful browser model when a subsequent development build fails.

## 4. Evidence

- [ ] 4.1 Add red-first floor tests for initial build, missing model, no in-process project import, and callback-driven refresh.
- [ ] 4.2 Add browser end-to-end evidence that a built model is inspectable and a machinist update refreshes it.
- [ ] 4.3 Run the relevant Python, frontend, and browser suites after the linked framework contract is available.
