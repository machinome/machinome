import {readFile, realpath} from 'node:fs/promises';
import {resolve, dirname, relative, isAbsolute} from 'node:path';
import {execFileSync} from 'node:child_process';
import {parseDocument, visit, isAlias, isScalar, isMap} from 'yaml';
import {loadSourceCode,validateCode} from './code.mjs';

export function parseSource(source) {
  const doc = parseDocument(source, {version:'1.2', uniqueKeys:true});
  if (doc.errors.length || doc.warnings.length) throw new Error([...doc.errors,...doc.warnings].map(e=>e.message).join('\n'));
  visit(doc, (_, node) => {
    if (isAlias(node) || node?.anchor || node?.tag) throw new Error('YAML aliases, anchors and tags are not supported');
    if (isMap(node)) for (const pair of node.items) {
      if (!isScalar(pair.key) || typeof pair.key.value !== 'string' || pair.key.value === '<<')
        throw new Error('YAML keys must be unique strings; merge keys are not supported');
    }
  });
  return doc.toJS({maxAliasCount:0});
}
const need = (ok, message) => {if (!ok) throw new Error(message);};
const finite = n => typeof n === 'number' && Number.isFinite(n);
export function validateEpisode(e, manifest) {
  need(manifest.animation?.loop === e.model.expectedDurationSeconds, 'Model duration differs from production settings; recheck the exported simulation');
  need(e.model.timeMode === 'normalized-loop' && !manifest.program && !manifest.clocked, 'Only posed normalized-loop models are supported');
  need(finite(e.model.expectedDurationSeconds) && e.model.expectedDurationSeconds > 0, 'Invalid model duration');
  for (const k of ['width','height','fps']) need(Number.isInteger(e.output[k]) && e.output[k] > 0, `Invalid output ${k}`);
  need(e.output.width%2===0 && e.output.height%2===0, 'Video dimensions must be even');
  need(finite(e.output.durationSeconds) && e.output.durationSeconds > 0 && Number.isInteger(e.output.durationSeconds*e.output.fps), 'Video duration must be a whole number of frames');
  for (const [name,c] of Object.entries(e.cameras)) {
    for (const k of ['position','target','up']) need(Array.isArray(c[k]) && c[k].length===3 && c[k].every(finite), `Invalid ${name}.${k}`);
    need(c.position.some((v,i)=>v!==c.target[i]), `Camera ${name} coincides with target`);
    need(c.up.some(v=>v!==0) && finite(c.fov) && c.fov>0 && c.fov<180, `Invalid camera ${name}`);
  }
  let end=0;const ids=new Set();
  need(Array.isArray(e.shots) && e.shots.length>0,'No shots');
  for (const s of e.shots) {
    need(typeof s.id==='string' && /^[a-z0-9-]+$/.test(s.id) && !ids.has(s.id), 'Shot ids must be unique slugs');ids.add(s.id);
    need(s.start===end && finite(s.end) && s.end>s.start, `Shots must be contiguous: ${s.id}`);end=s.end;
    need(typeof s.narration==='string' && s.narration.trim() && typeof s.direction==='string', `Missing narration/direction: ${s.id}`);
    need(s.speechOffset===undefined||(finite(s.speechOffset)&&s.speechOffset>=0&&s.speechOffset<s.end-s.start),`Invalid speech offset: ${s.id}`);
    validateCode(e,s);
    need(finite(s.simulation.from) && finite(s.simulation.to) && s.simulation.from>=0 && s.simulation.to>=s.simulation.from && s.simulation.to<=e.model.expectedDurationSeconds,`Invalid simulation range: ${s.id}`);
    if(s.simulation.keyframes){
      const keys=s.simulation.keyframes;
      need(keys.length>=2&&keys[0].at===0&&keys[0].seconds===s.simulation.from&&keys.at(-1).at===s.end-s.start&&keys.at(-1).seconds===s.simulation.to,`Invalid model keyframe endpoints: ${s.id}`);
      for(let i=0;i<keys.length;i++)need(finite(keys[i].at)&&finite(keys[i].seconds)&&keys[i].seconds>=s.simulation.from&&keys[i].seconds<=s.simulation.to&&(i===0||(keys[i].at>keys[i-1].at&&keys[i].seconds>=keys[i-1].seconds)),`Invalid model keyframes: ${s.id}`);
    }
    need(Array.isArray(s.camera) && s.camera.length>0 && s.camera[0].at===0,`Missing initial camera: ${s.id}`);
    let at=-1;let prior;
    for (const key of s.camera) {
      const c=e.cameras[key.preset];need(c && finite(key.at) && key.at>at && key.at<=s.end-s.start,`Invalid camera key: ${s.id}`);at=key.at;
      if(prior)need(c.fov===prior.fov && JSON.stringify(c.up)===JSON.stringify(prior.up),'Changing FOV/up within a shot is not supported');prior=c;
    }
    for(const name of s.hiddenLayers)need(e.layers[name],`Unknown layer: ${name}`);
    for(const cue of s.overlays)need(finite(cue.from)&&finite(cue.to)&&cue.from>=0&&cue.to>cue.from&&cue.to<=s.end-s.start&&typeof cue.text==='string'&&['top','lower-third','center'].includes(cue.position),`Invalid overlay: ${s.id}`);
    for(const name of s.evidence)need(e.evidence[name],`Unknown evidence: ${name}`);
  }
  need(end===e.output.durationSeconds,'Shots must cover the video duration');
}
export async function loadEpisode(file) {
  const episodePath=await realpath(file), base=dirname(episodePath);
  const script=parseSource(await readFile(episodePath,'utf8'));
  need(script.format==='machinome-video-draft/0.2','Unsupported episode format');
  const productionPath=await realpath(resolve(base,script.production));
  const p=parseSource(await readFile(productionPath,'utf8'));
  const e={...p,...script};
  const manifestPath=await realpath(resolve(dirname(productionPath),p.model.manifest));
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  validateEpisode(e,manifest);
  const paths=new Set();
  function walk(n,path=[]) {paths.add(JSON.stringify(path));for(const child of n.children??[])walk(child,[...path,child.name]);}
  walk(manifest.root);
  for(const layer of Object.values(e.layers)) for(const path of layer) need(paths.has(JSON.stringify(path)),`Missing assembly path: ${path.join('/')}`);
  for(const path of Object.values(e.evidence)) await readFile(resolve(dirname(productionPath),path));
  const repository=execFileSync('git',['rev-parse','--show-toplevel'],{cwd:base,encoding:'utf8'}).trim();
  need(!relative(repository,base).startsWith('..'),'Episode must live inside its project repository');
  const sourceRevision=(await readFile(resolve(dirname(manifestPath),'source-revision.txt'),'utf8')).trim();
  need(e.model.sourceRevision===sourceRevision,'Pin model.sourceRevision to the export source-revision.txt before rendering');
  e.paths={episode:episodePath,production:productionPath,manifest:manifestPath,repository,build:resolve(base,'_build')};
  e.sourceCode=await loadSourceCode(e);
  return e;
}

export function contained(root,path) {
  const rel=relative(root,path);
  return !isAbsolute(rel) && rel!=='..' && !rel.startsWith('../');
}
