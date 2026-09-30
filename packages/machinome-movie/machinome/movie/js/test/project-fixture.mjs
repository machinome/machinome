// The tiny fixture project the movie-document and YAML-identity tests share.
// Not a test file: it registers no tests. Its one commit is deterministic
// (fixed tree, author, committer and dates), so a document may pin the model
// revision literally. No test reads a project under the workspace's projects/.
import {mkdtemp,mkdir,writeFile,rm,readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {pcmWav} from '../src/speech.mjs';
import {hash} from '../src/util.mjs';

export const MODEL_SOURCE=[
  'class Mill:',
  '    def coupling(self, waterwheel, crankshaft):',
  '        waterwheel.drives(crankshaft)',
  '        return crankshaft',
  ''].join('\n');
export const MANIFEST={root:{name:'fixture',children:[{name:'Feed',children:[{name:'Pawl'}]}]},animation:{loop:20}};
const COMMIT_ENV={GIT_AUTHOR_NAME:'Fixture',GIT_AUTHOR_EMAIL:'fixture@example.invalid',GIT_AUTHOR_DATE:'2026-09-30T00:00:00Z',
  GIT_COMMITTER_NAME:'Fixture',GIT_COMMITTER_EMAIL:'fixture@example.invalid',GIT_COMMITTER_DATE:'2026-09-30T00:00:00Z'};

// A fresh project: models/fixture.py committed once, the export beside it.
export async function fixtureProject(t){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-project-'));
  t?.after(()=>process.env.KEEP_VIDEOMAKER_TEST?console.log('Review fixture: '+dir):rm(dir,{recursive:true,force:true}));
  const git=(...args)=>execFileSync('git',args,{cwd:dir,encoding:'utf8',env:{...process.env,...COMMIT_ENV}}).trim();
  git('init','-q');
  await mkdir(join(dir,'models'));
  await writeFile(join(dir,'models','fixture.py'),MODEL_SOURCE);
  git('add','models/fixture.py');
  git('-c','commit.gpgsign=false','commit','-qm','fixture model');
  const revision=git('rev-parse','HEAD');
  await mkdir(join(dir,'export','fixture'),{recursive:true});
  await writeFile(join(dir,'export','fixture','manifest.json'),JSON.stringify(MANIFEST));
  await writeFile(join(dir,'export','fixture','source-revision.txt'),revision+'\n');
  return {dir,revision};
}

// A synthetic alignment: every character, spaces included, lasts `step` seconds.
export function evenAlignment(text,step=.05,start=0){
  const characters=Array.from(text);
  return {characters,character_start_times_seconds:characters.map((_,i)=>+(start+i*step).toFixed(6)),
    character_end_times_seconds:characters.map((_,i)=>+(start+(i+1)*step).toFixed(6))};
}

// Installs one cached take the way the speech command stores it: a silent WAV
// of the record's duration and its sidecar record with the checksum.
export async function installTake(entry,{alignment,duration}){
  await mkdir(dirname(entry.file),{recursive:true});
  const bytes=pcmWav(Buffer.alloc(Math.round(duration*24000)*2),24000);
  await writeFile(entry.file,bytes);
  await writeFile(entry.meta,JSON.stringify({cache:entry.cache,format:entry.format,request:entry.request,
    alignment,sha256:hash(bytes),duration}));
  return entry.file;
}

export async function readJson(file){return JSON.parse(await readFile(file,'utf8'));}

// A format 0.4 YAML episode of three shots inside the fixture project, using
// what chapters touch: per-shot narration and speech offsets, a spoken reveal,
// source emphasis, a pronunciation alias, transitions and fades.
export async function yamlEpisode(dir,revision){
  const videos=join(dir,'videos','yaml-fixture');
  await mkdir(videos,{recursive:true});
  await writeFile(join(videos,'description.md'),'Fixture description.\n');
  await writeFile(join(videos,'episode.yaml'),`format: machinome-video-draft/0.4
id: yaml-fixture
title: YAML fixture
status: rehearsal
learningGoal: Pin the frames of a YAML episode.
production: production.yaml
shots:
  - id: hook
    start: 0
    end: 2.5
    speechOffset: 0.3
    narration: The wheel turns the shaft.
    direction: Look at the wheel.
    fadeIn: {duration: 0.5}
    simulation:
      from: 2
      to: 6
      keyframes:
        - {at: 0, seconds: 2}
        - {at: 1.2, seconds: 3, ease: out}
        - {at: 2.5, seconds: 6}
    camera:
      - {at: 0, preset: wide}
      - {at: 2, preset: near, ease: in-out}
    hiddenLayers: []
    overlays:
      - {from: 0, to: 2.5, text: The wheel turns, position: top, reveal: {timing: spoken}}
    evidence: [model]
  - id: coupling
    start: 2.5
    end: 5
    narration: The waterwheel drives the crankshaft.
    direction: Read the line.
    transition: {kind: dissolve, duration: 0.4}
    simulation: {from: 6, to: 9}
    camera:
      - {at: 0, preset: near}
    hiddenLayers: []
    overlays: []
    evidence: [model]
    code:
      snippet: coupling
      typing:
        - {from: 0, to: 0.3, throughLine: 3}
      emphasis:
        - {line: 3, phrase: The waterwheel drives the crankshaft., words: [waterwheel, drives, crankshaft], hold: 0.2}
  - id: closing
    start: 5
    end: 7
    narration: Watch Machinome again.
    direction: Hold on the pawl.
    fadeOut: {duration: 0.5}
    simulation: {from: 9, to: 11}
    camera:
      - {at: 0, preset: near}
      - {at: 2, preset: wide, ease: linear}
    hiddenLayers: []
    overlays: []
    evidence: []
    highlight:
      - {from: 0.5, to: 2, parts: [pawl], others: ghost}
`);
  await writeFile(join(videos,'production.yaml'),`output: {width: 320, height: 180, fps: 10, durationSeconds: 7}
model:
  manifest: ../../export/fixture/manifest.json
  expectedDurationSeconds: 20
  timeMode: normalized-loop
  sourceRevision: ${revision}
  readiness: Fixture export.
audio:
  provider: elevenlabs
  model: test-model
  voice: test-voice
  outputFormat: pcm_24000
  replacements: {Machinome: mah-SHEEN-ohm}
series: FIXTURE
style: {background: "#faf7ef", foreground: "#222222", accent: "#237c86", fontFamily: DejaVu Sans, safeInsetFraction: 0.08}
cameras:
  wide: {position: [0, -10, 4], target: [0, 0, 0], up: [0, 0, 1], fov: 37}
  near: {position: [2, -6, 2], target: [0, 0, 0], up: [0, 0, 1], fov: 37}
layers:
  pawl: [[Feed, Pawl]]
evidence:
  model: ../../models/fixture.py
sourceCode:
  coupling: {file: ../../models/fixture.py, lines: [3, 3]}
credits: {creator: Fixture}
release: {simulationUrl: null, sourceUrl: null, descriptionTemplate: description.md}
`);
  return join(videos,'episode.yaml');
}
