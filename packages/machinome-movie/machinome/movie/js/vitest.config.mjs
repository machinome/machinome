// The Node suite under one runner (AGENTS.md, "Testing policy"; ADR-003).
// Pure tests run first and in parallel; slow tests (anything that launches
// Chromium, runs FFmpeg or writes a build directory) run after them, one file
// at a time in one worker that shares its module graph, so one Chromium
// (launched by the global setup) and one asset server serve every browser
// test of the project. The viewer layer (layer 6, ADR-008) runs last, one file
// at a time in a worker of its own, on the same Chromium, gated on the bundle
// VIDEOMAKER_VIEWER_BUNDLE selects. Slow tests are memoized
// (test/support/memo.mjs); `npm test -- --cold` ignores the memo.
import {defineConfig} from 'vitest/config';

// A file is slow when it launches Chromium, runs FFmpeg or writes a build
// directory: the browser tests (layer 5) under test/browser/ and the pipeline
// tests (layer 8) under test/pipeline/. The viewer layer's tests, under
// test/viewer/, are slow too, and their own project. The pure project is
// everything else under test/.
export const SLOW=['test/browser/**/*.test.mjs','test/pipeline/**/*.test.mjs'];
export const VIEWER=['test/viewer/**/*.test.mjs'];
const serial={fileParallelism:false,isolate:false,
  globalSetup:['./test/support/toolchain.mjs'],setupFiles:['./test/support/one-browser.mjs'],
  testTimeout:600_000,hookTimeout:600_000};

export default defineConfig({
  test:{
    reporters:['default','./test/support/memo-reporter.mjs'],
    projects:[
      {test:{name:'pure',include:['test/**/*.test.mjs'],exclude:[...SLOW,...VIEWER],
        sequence:{groupOrder:0},testTimeout:30_000}},
      // Layer 4: the stage's components and the take transport under jsdom,
      // and tsc over stage/ and transport/.
      {test:{name:'stage',include:['stage/**/*.test.tsx','transport/**/*.test.ts'],environment:'jsdom',
        sequence:{groupOrder:0},testTimeout:60_000}},
      {test:{name:'slow',include:SLOW,sequence:{groupOrder:1},...serial}},
      // Layer 6: the real viewer, over the fixture project's real export.
      {test:{name:'viewer',include:VIEWER,sequence:{groupOrder:2},...serial}},
    ],
  },
});
