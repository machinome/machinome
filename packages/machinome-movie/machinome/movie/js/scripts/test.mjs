#!/usr/bin/env node
// `npm test [-- --cold] [vitest arguments]`: the suite under vitest.
// `--cold` ignores the test memo entirely (test/support/memo.mjs); it is
// carried to the tests as VIDEOMAKER_TEST_COLD=1, which is the same switch
// for any other vitest invocation. Vitest refuses options it does not know,
// so the switch is taken off the arguments here.
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2),cold=args.includes('--cold');
const vitest=join(dirname(createRequire(import.meta.url).resolve('vitest/package.json')),'vitest.mjs');
const env={...process.env,...(cold?{VIDEOMAKER_TEST_COLD:'1'}:{})};
const result=spawnSync(process.execPath,[vitest,'run',...args.filter(a=>a!=='--cold')],{cwd:root,env,stdio:'inherit'});
process.exit(result.status??1);
