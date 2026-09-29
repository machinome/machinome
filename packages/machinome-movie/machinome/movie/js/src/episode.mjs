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
export const FORMATS=['machinome-video-draft/0.2','machinome-video-draft/0.3'];
const V03=FORMATS[1];
// Episodes without a format field are the unit-test shape of a 0.2 episode.
const formatOf=e=>e.format??FORMATS[0];
export function assemblyPaths(root) {
  const paths=new Set();
  (function walk(n,path=[]){paths.add(JSON.stringify(path));for(const child of n.children??[])walk(child,[...path,child.name]);})(root);
  return paths;
}
const within=(outer,inner)=>outer.length<=inner.length&&outer.every((name,i)=>name===inner[i]);
const isPath=p=>Array.isArray(p)&&p.length>0&&p.every(n=>typeof n==='string'&&n.length>0);
// A part target is a production layer name or one root-relative assembly path.
function targetPaths(e,s,part,known,where){
  if(typeof part==='string'){need(e.layers?.[part],`Unknown layer: ${part} (${where} in shot ${s.id})`);return e.layers[part];}
  need(isPath(part),`Invalid part: expected a layer name or an assembly path (${where} in shot ${s.id})`);
  need(known(part),`Missing assembly path: ${part.join('/')} (${where} in shot ${s.id})`);
  return [part];
}
function hiddenPaths(e,s){return (s.hiddenLayers??[]).flatMap(name=>e.layers?.[name]??[]);}
const pair=(v,lo,hi)=>Array.isArray(v)&&v.length===2&&v.every(n=>finite(n)&&n>=lo&&n<=hi);
const ANNOTATION_FIELDS=new Set(['from','to','kind','part','point','text','place','offset']);
function validateAnnotations(e,s,known){
  if(s.annotations===undefined)return;
  need(formatOf(e)===V03,`Annotations need format machinome-video-draft/0.3: shot ${s.id}`);
  need(Array.isArray(s.annotations),`Annotations must be a list: shot ${s.id}`);
  const inset=e.style?.safeInsetFraction;
  need(finite(inset)&&inset>=0&&inset<.5,`Annotations need a declared style.safeInsetFraction in [0, 0.5): shot ${s.id}`);
  const duration=s.end-s.start,hidden=hiddenPaths(e,s);
  s.annotations.forEach((a,i)=>{
    const where=`annotation #${i}`,bad=why=>`Invalid ${where} in shot ${s.id}: ${why}`;
    need(a&&typeof a==='object'&&!Array.isArray(a),bad('expected a mapping'));
    for(const key of Object.keys(a))need(ANNOTATION_FIELDS.has(key),`Unknown annotation field: ${key} (${where} in shot ${s.id})`);
    need(['arrow','label'].includes(a.kind),bad('kind must be arrow or label'));
    need(finite(a.from)&&finite(a.to)&&a.from>=0&&a.from<a.to&&a.to<=duration,bad('times must satisfy 0 <= from < to <= shot duration'));
    need((a.part===undefined)!==(a.point===undefined),bad('give exactly one of part or point'));
    if(a.point!==undefined)need(Array.isArray(a.point)&&a.point.length===3&&a.point.every(finite),bad('point must be three finite numbers'));
    else for(const path of targetPaths(e,s,a.part,known,where))
      need(!hidden.some(h=>within(h,path)),`Annotated part is hidden in shot ${s.id}: ${path.join('/')} (${where})`);
    need(a.text===undefined||(typeof a.text==='string'&&a.text.trim().length>0),bad('text must be non-empty words'));
    if(a.kind==='arrow'){
      need(a.offset===undefined,bad('offset belongs to a label; an arrow takes place'));
      need(pair(a.place,0,1),bad('an arrow needs place: [x, y] within the safe area, each in [0, 1]'));
    }else{
      need(a.place===undefined,bad('place belongs to an arrow; a label takes offset'));
      need(typeof a.text==='string'&&a.text.trim().length>0,bad('a label needs text'));
      need(a.offset===undefined||pair(a.offset,-1,1),bad('offset must be [dx, dy], each in [-1, 1]'));
    }
  });
}
// The lowest Viewer API an episode can be produced with, and why.
export function requiredViewerApi(e) {
  const reasons=[];
  for(const s of e.shots??[]){
    if(s.annotations?.length)reasons.push(`annotations (shot ${s.id})`);
  }
  return {api:reasons.length?28:21,reasons};
}
export function viewerApiRefusal(required,declared) {
  return `This episode needs Viewer API ${required.api} for ${required.reasons.join(', ')}; the selected viewer declares API ${declared}. Select a newer machinome-viewer bundle with --viewer.`;
}
// check has no browser: it reads the "viewer API <n>" banner of the selected bundle.
export function viewerApiFromBanner(text) {
  const match=/\bviewer API (\d+)\b/.exec(String(text).slice(0,4096));
  return match?Number(match[1]):null;
}
export function confirmViewerApi(required,bundleText) {
  if(required.api<=21)return null;
  const declared=bundleText==null?null:viewerApiFromBanner(bundleText);
  need(declared!==null,`Cannot confirm the viewer API: this episode needs Viewer API ${required.api} for ${required.reasons.join(', ')}, and the selected bundle is missing or declares no "viewer API" banner. Select a machinome-viewer bundle with --viewer.`);
  need(declared>=required.api,viewerApiRefusal(required,declared));
  return declared;
}
export function validateEpisode(e, manifest) {
  need(FORMATS.includes(formatOf(e)),'Unsupported episode format');
  const paths=manifest.root?assemblyPaths(manifest.root):null;
  const known=path=>!paths||paths.has(JSON.stringify(path));
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
    validateAnnotations(e,s,known);
  }
  need(end===e.output.durationSeconds,'Shots must cover the video duration');
}
export async function loadEpisode(file) {
  const episodePath=await realpath(file), base=dirname(episodePath);
  const script=parseSource(await readFile(episodePath,'utf8'));
  need(FORMATS.includes(script.format),'Unsupported episode format');
  const productionPath=await realpath(resolve(base,script.production));
  const p=parseSource(await readFile(productionPath,'utf8'));
  const e={...p,...script};
  const manifestPath=await realpath(resolve(dirname(productionPath),p.model.manifest));
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  validateEpisode(e,manifest);
  const paths=assemblyPaths(manifest.root);
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
