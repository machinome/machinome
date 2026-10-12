// Pure: where the speech command looks for its key file, in order, for each
// shape of checkout it can run from. Throwaway Git repositories only; no key
// is read and no `.env` of this repository is named.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {join} from 'node:path';
import {keyFiles} from '../src/speech.mjs';
import {keyLayout} from './support/key-layouts.mjs';

test('a plain directory looks only in its own .env',async t=>{
  const {checkout}=await keyLayout(t,'plain');
  assert.deepEqual(keyFiles(checkout),[join(checkout,'.env')]);
});

test('a primary work tree looks only in its own .env',async t=>{
  const {checkout}=await keyLayout(t,'primary');
  assert.deepEqual(keyFiles(checkout),[join(checkout,'.env')]);
});

test('another work tree looks in its own .env, then in the primary work tree\'s',async t=>{
  const {checkout,primary}=await keyLayout(t,'worktree');
  assert.deepEqual(keyFiles(checkout),[join(checkout,'.env'),join(primary,'.env')]);
});

test('a copy inside another repository\'s work tree never looks in that repository',async t=>{
  const {checkout,primary}=await keyLayout(t,'inside');
  assert.deepEqual(keyFiles(checkout),[join(checkout,'.env')]);
  assert.ok(!keyFiles(checkout).includes(join(primary,'.env')));
});

test('a caller\'s GIT_DIR naming another repository is not followed',async t=>{
  const {checkout}=await keyLayout(t,'plain'),other=await keyLayout(t,'primary');
  const before=process.env.GIT_DIR;
  process.env.GIT_DIR=join(other.primary,'.git');
  t.onTestFinished(()=>{if(before===undefined)delete process.env.GIT_DIR;else process.env.GIT_DIR=before;});
  assert.deepEqual(keyFiles(checkout),[join(checkout,'.env')]);
});
