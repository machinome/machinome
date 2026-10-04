// The check command (README, "check"; the live-server change, design D1):
// loads a YAML episode or a movie document, bundles its stage, measures its
// layout when it shows a picture or comes in by a reframe, resolves it
// against the cached takes and prints what it found, in the order `check`
// has always printed it. `live` loads every generation through it, so the
// lines a live session prints are the command's.
import {resolve,dirname,extname,basename} from 'node:path';
import {readFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {loadEpisode,confirmViewerApi,filmSubject,PAPER_STAGE} from './episode.mjs';
import {filmShots,shotActions,joinShows} from './timeline.mjs';
import {buildFilmStage} from './stage-build.mjs';
import {cachedTake} from './speech.mjs';
import {chaptersOf,chapterTakeLines} from './chapters.mjs';
import {readMovie} from './movie.mjs';
import {prepareWordTimingForCommand} from './command-timing.mjs';
import {readTrees} from './render.mjs';
import {clipCadence,loadPictures} from './pictures.mjs';
import {loadSourceCode} from './code.mjs';
import {picturesShown,measureLayouts,layoutLines,checkEnlargements,checkPictureViews,
  reframesOf,reframeBoxes,reframeLines,textLines,showsText,TEXT_NOT_MEASURED} from './layout.mjs';
import {takeLine} from './take.mjs';

// What every command takes of its options once the film is loaded: the
// viewer bundle (the given path, or the one beside the export's manifest),
// the width and the frame rate, each refused when it cannot be rendered.
export function commandOptions(e,{viewer,width,fps}={}){
  const options={viewer:resolve(viewer??resolve(dirname(e.paths.manifest),'machinome-viewer.js')),width,fps};
  if(options.width!==undefined&&(!Number.isInteger(options.width)||options.width<320||options.width%2))throw new Error('Width must be an even integer >= 320');
  if(options.fps!==undefined&&(!Number.isInteger(options.fps)||options.fps<1||options.fps>120))throw new Error('FPS must be an integer from 1 to 120');
  return options;
}
// The line every command prints once the film is loaded.
export const summaryLine=e=>`${e.title}: ${e.chapters.length} chapters, ${filmShots(e).length} shots, ${e.output.durationSeconds}s; model ${e.model.expectedDurationSeconds}s`;

// Checks the source and prints check's lines; returns the loaded film, the
// stage bundle and the measured layout (null when nothing was measured).
export async function checkSource(source,{viewer,width,fps,silent=false}={}){
  // check bundles and type-checks a document's stage before anything that
  // needs a take, so a template that does not match the declarations is
  // refused before speech is bought.
  // A document that shows a picture or comes in by a reframe has its sets'
  // layout measured next, in a headless page served the bundle
  // (src/layout.mjs, ADR-009, ADR-010), and a picture enlarged beyond its
  // allowance in its slot's box, or a reframe through a slot sized by what it
  // holds, is refused before any take is read. A document without either,
  // and a YAML episode, whose paper sets' boxes are known, open no browser.
  // The same probe measures the text each shot shows, wholly shown, from the
  // pinned excerpts (ADR-017); a document it does not measure says so.
  let early=null,layouts=null,enlargements=null,textUnmeasured=false;
  if(extname(source).toLowerCase()==='.json'){
    const {doc,documentPath,base,build}=await readMovie(source);
    const repository=execFileSync('git',['rev-parse','--show-toplevel'],{cwd:base,encoding:'utf8'}).trim();
    early=await buildFilmStage({stage:doc.stage,paths:{base,build,repository,episode:documentPath}});
    // A reframe moves its views between slots' measured boxes (ADR-010): the
    // layout is measured for it too, and a slot sized by what it holds is
    // refused before any take.
    const pictures=picturesShown(doc).length>0,reframes=reframesOf(doc).length>0;
    textUnmeasured=!pictures&&!reframes&&showsText(doc);
    if(pictures||reframes){
      const media=pictures?await loadPictures({source:'movie',stills:doc.stills,clips:doc.clips,paths:{repository,base}}):null;
      const excerpts=await loadSourceCode({sourceCode:doc.sourceCode,model:doc.model,paths:{base,repository}});
      layouts=await measureLayouts(doc,early,{excerpts});
      reframeBoxes(doc,layouts);
      if(pictures)enlargements=checkEnlargements(doc,media,layouts);
    }
  }
  const e=await loadEpisode(source);
  const options=commandOptions(e,{viewer,width,fps});
  console.log(summaryLine(e));
  // Where the length comes from: each chapter's cached take and its tail
  // (read from the cache only; check never generates speech).
  const takes=await Promise.all(chaptersOf(e).map((_,i)=>cachedTake(e,i)));
  for(const line of chapterTakeLines(e,takes.map(take=>take?.record)))console.log(line);
  // A clocked take: its steps, marks and length, and the replay its load
  // checked against the recorded banks (ADR-012).
  if(e.model.timeMode==='take')console.log(takeLine(e));
  // Each shot whose continuation through its outgoing join crosses a mark,
  // in film order, as resolution recorded it on the shot's model time: a
  // report, not a refusal (check-the-continuation, ADR-014).
  for(const {shot} of filmShots(e))if(shot.model?.crossing)console.log(shot.model.crossing.report);
  await prepareWordTimingForCommand(e,{command:'check',silent:Boolean(silent),fps:options.fps??e.output.fps});
  // The reframes' boxes, from the measured layout, before any frame is posed.
  if(layouts&&reframesOf(e).length)e.reframes=reframeBoxes(e,layouts);
  // A view that leaves its picture, in the measured box, at a frame the
  // takes have now placed.
  if(layouts)checkPictureViews(e,layouts);
  // check mounts no viewer (the layout page gets a stub): it reads the
  // bundle's banner; preview and render confirm the running viewer's apiVersion instead.
  const required=e.viewerApi;
  if(required.api>21){
    const declared=confirmViewerApi(required,await readFile(options.viewer,'utf8').catch(()=>null),filmSubject(e));
    console.log(`Viewer API ${required.api} required for ${required.reasons.join(', ')}; ${options.viewer} declares API ${declared}`);
  }
  // The stage bundle: bundled and type-checked before any speech is bought.
  const bundle=early??await buildFilmStage(e);
  const modules=e.stage.modules.length?e.stage.modules.join(', '):'the runtime alone';
  // Both hashes: a stylesheet change leaves the script's bytes as they were.
  console.log(`Stage: ${bundle.reused?'reused':'bundled'} ${bundle.js} (sha256 ${bundle.sha256.slice(0,12)}) and ${basename(bundle.css)} (sha256 ${bundle.cssSha256.slice(0,12)}) from ${modules}; `+
    (bundle.typechecked?'types checked':e.stage.modules.length?'no TypeScript module, types not checked':'no module to type-check'));
  if(layouts)for(const line of [...layoutLines(layouts),...reframeLines(e,layouts),...textLines(layouts)])console.log(line);
  if(textUnmeasured)console.log(TEXT_NOT_MEASURED);
  const shots=filmShots(e),rate=e.output.fps;
  for(const [i,{chapter,shot}] of shots.entries())for(const {cue,action} of shotActions(shot)){
    const element=chapter.elements[action.element];
    if(element?.kind!=='picture'||action.action!=='show')continue;
    const media=element.still!==undefined?'still':'clip',name=element[media],probe=e.pictureMedia[`${media}s`][name];
    // A document's picture was measured in its slot's box, before the
    // takes; a YAML episode's is in a paper set, whose boxes are known.
    const measured=enlargements?.get(`${shot.id}/${chapter.id}.${action.element}`);
    const slot=Object.keys(shot.places).find(s=>shot.places[s]===action.element),known=PAPER_STAGE[shot.set];
    const box=!known?null:/^full(-\d+)?$/.test(slot)?[0,0,1,1]:known;
    let text;
    if(measured!==undefined)text=measured;
    else if(probe.format==='svg')text='vector, no enlargement limit';
    else if(!box)text=`allowance ${probe.upscale}×; enlargement checked against its slot's box at preview and render`;
    else{
      const zoom=Math.max(1,...(action.view??[]).map(v=>v.zoom)),w=box[2]*e.output.width,h=box[3]*e.output.height;
      const peak=((element.fit??'contain')==='cover'?Math.max:Math.min)(w/probe.width,h/probe.height)*zoom;
      text=`peak ${peak.toFixed(2)}×; allowance ${probe.upscale}×`;
    }
    console.log(`Picture ${shot.id} ${chapter.id}.${action.element} (${media} ${name}): ${text}`);
    if(media==='clip'){
      const globalStart=shot.start+cue.at,phase=Math.max(0,Math.ceil(globalStart*rate-1e-9)/rate-globalStart),start=element.inPoint??0;
      const continuation=Math.abs(cue.until-(shot.end-shot.start))<1e-9?joinShows(shots[i+1]?.shot.transition):0;
      const cadence=clipCadence(probe.timestamps,start,start+cue.until-cue.at+continuation,rate,phase);
      console.log(`  source ${probe.averageRate.toFixed(3)} fps into film ${rate} fps: `+
        `${cadence.dropped} dropped, ${cadence.repeated} repeated; audio not played`);
    }
  }
  // The trees a render would name the heads of, and whether they are dirty
  // now (ADR-015): the project's and this checkout's; then the revision the
  // export was made from and whether the project was dirty then (ADR-019).
  await readTrees(e,'check');
  return {film:e,bundle,layouts};
}
