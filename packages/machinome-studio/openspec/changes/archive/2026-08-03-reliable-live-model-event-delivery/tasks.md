## 1. Replayable Floor event delivery

- [x] 1.1 Add a sequence cursor to the Floor run stream that safely replays
  broker events after a run snapshot while retaining live delivery order.
- [x] 1.2 Connect the browser stream from its latest observed run event and
  apply replayed model-publication events through the existing update path.

## 2. Regression proof

- [x] 2.1 Write a red end-to-end test that publishes an assembly-to-fusion
  `viewer.json` during the snapshot-to-stream hand-off and proves the open
  canvas updates without navigation or a second mount.
- [x] 2.2 Run focused Floor lifecycle coverage and the complete shop validation
  suite against the paired sprint framework.
