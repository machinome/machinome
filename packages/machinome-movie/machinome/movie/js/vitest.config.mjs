// The Node suite under one runner (AGENTS.md, "Testing policy"; ADR-003).
// Two projects: pure tests run first and in parallel; slow tests (anything
// that launches Chromium, runs FFmpeg or writes a build directory) run after
// them, one file at a time in one worker that shares its module graph, so one
// Chromium (launched by the global setup) and one asset server serve every
// browser test of the run. Slow tests are memoized (test/support/memo.mjs);
// `npm test -- --cold` ignores the memo.
import {defineConfig} from 'vitest/config';

// A file is slow when it launches Chromium, runs FFmpeg or writes a build
// directory. The pure project is everything else under test/.
export const SLOW=[
  'test/browser-seam.test.mjs',
  'test/incremental-rendering.test.mjs',
  'test/movie-pipeline.test.mjs',
  'test/pictures.test.mjs',
  'test/render.test.mjs',
  'test/review-pack.test.mjs',
  'test/source-only-browser.test.mjs',
  'test/source-scenes.test.mjs',
  'test/speech.test.mjs',
];

export default defineConfig({
  test:{
    reporters:['default','./test/support/memo-reporter.mjs'],
    projects:[
      {test:{name:'pure',include:['test/**/*.test.mjs'],exclude:SLOW,
        sequence:{groupOrder:0},testTimeout:30_000}},
      {test:{name:'slow',include:SLOW,sequence:{groupOrder:1},
        fileParallelism:false,isolate:false,
        globalSetup:['./test/support/toolchain.mjs'],setupFiles:['./test/support/one-browser.mjs'],
        testTimeout:600_000,hookTimeout:600_000}},
    ],
  },
});
