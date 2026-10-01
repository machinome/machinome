#!/usr/bin/env node
import {parseArgs} from 'node:util';
import {resolve,dirname,extname,basename} from 'node:path';
import {readFile} from 'node:fs/promises';
import {loadEpisode,confirmViewerApi,filmSubject,PAPER_STAGE} from '../src/episode.mjs';
import {filmShots,shotActions,joinShows} from '../src/timeline.mjs';
import {buildFilmStage} from '../src/stage-build.mjs';
import {speech,cachedTake} from '../src/speech.mjs';
import {chaptersOf,chapterTakeLines} from '../src/chapters.mjs';
import {generateMovieTakes} from '../src/movie.mjs';
import {validateWordFramesAtFps} from '../src/words.mjs';
import {prepareWordTimingForCommand} from '../src/command-timing.mjs';
import {preview,render,readTrees} from '../src/render.mjs';
import {clipCadence,loadPictures} from '../src/pictures.mjs';
import {picturesShown,measureLayouts,layoutLines,checkEnlargements,checkPictureViews,
  reframesOf,reframeBoxes,reframeLines} from '../src/layout.mjs';
import {reviewManifest} from '../src/review-pack.mjs';
import {takeLine} from '../src/take.mjs';

try{
  const {positionals,values}=parseArgs({allowPositionals:true,options:{viewer:{type:'string'},width:{type:'string'},fps:{type:'string'},silent:{type:'boolean'},help:{type:'boolean'}}});
  const [command,source]=positionals;
  if(values.help||!source){console.log('videomaker check|speech|preview|render|build EPISODE.yaml|MOVIE.json [--viewer BUNDLE.js] [--width 960] [--fps 10] [--silent]\nvideomaker review MANIFEST.json');process.exit(source?0:1);}
  if(command==='review'){
    const result=await reviewManifest(source);
    console.log(`Review pack: ${result.generation}${result.reused?' (verified reuse)':''}`);
    process.exit(0);
  }
  if(!['check','speech','preview','render','build'].includes(command))throw new Error('Unknown command: '+command);
  // A movie document's takes need only its narration: speech generates them
  // before the anchors that depend on them are resolved (movie-document D4).
  if(extname(source).toLowerCase()==='.json'&&(command==='speech'||command==='build'&&!values.silent))await generateMovieTakes(source);
  // check bundles and type-checks a document's stage before anything that
  // needs a take, so a template that does not match the declarations is
  // refused before speech is bought.
  // A document that shows a picture or comes in by a reframe has its sets'
  // layout measured next, in a headless page served the bundle
  // (src/layout.mjs, ADR-009, ADR-010), and a picture enlarged beyond its
  // allowance in its slot's box, or a reframe through a slot sized by what it
  // holds, is refused before any take is read. A document without either,
  // and a YAML episode, whose paper sets' boxes are known, open no browser.
  let early=null,layouts=null,enlargements=null;
  if(command==='check'&&extname(source).toLowerCase()==='.json'){
    const {readMovie}=await import('../src/movie.mjs');
    const {doc,documentPath,base,build}=await readMovie(source);
    const {execFileSync}=await import('node:child_process');
    const repository=execFileSync('git',['rev-parse','--show-toplevel'],{cwd:base,encoding:'utf8'}).trim();
    early=await buildFilmStage({stage:doc.stage,paths:{base,build,repository,episode:documentPath}});
    // A reframe moves its views between slots' measured boxes (ADR-010): the
    // layout is measured for it too, and a slot sized by what it holds is
    // refused before any take.
    const pictures=picturesShown(doc).length>0,reframes=reframesOf(doc).length>0;
    if(pictures||reframes){
      const media=pictures?await loadPictures({source:'movie',stills:doc.stills,clips:doc.clips,paths:{repository,base}}):null;
      layouts=await measureLayouts(doc,early);
      reframeBoxes(doc,layouts);
      if(pictures)enlargements=checkEnlargements(doc,media,layouts);
    }
  }
  const e=await loadEpisode(source);
  const options={viewer:resolve(values.viewer??resolve(dirname(e.paths.manifest),'machinome-viewer.js')),
    width:values.width?Number(values.width):undefined,fps:values.fps?Number(values.fps):undefined};
  if(options.width!==undefined&&(!Number.isInteger(options.width)||options.width<320||options.width%2))throw new Error('Width must be an even integer >= 320');
  if(options.fps!==undefined&&(!Number.isInteger(options.fps)||options.fps<1||options.fps>120))throw new Error('FPS must be an integer from 1 to 120');
  console.log(`${e.title}: ${e.chapters.length} chapters, ${filmShots(e).length} shots, ${e.output.durationSeconds}s; model ${e.model.expectedDurationSeconds}s`);
  // Where the length comes from: each chapter's cached take and its tail
  // (read from the cache only; check never generates speech).
  if(command==='check'){
    const takes=await Promise.all(chaptersOf(e).map((_,i)=>cachedTake(e,i)));
    for(const line of chapterTakeLines(e,takes.map(take=>take?.record)))console.log(line);
    // A clocked take: its steps, marks and length, and the replay its load
    // checked against the recorded banks (ADR-012).
    if(e.model.timeMode==='take')console.log(takeLine(e));
  }
  await prepareWordTimingForCommand(e,{command,silent:Boolean(values.silent),fps:options.fps??e.output.fps});
  if(command==='check'){
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
    if(layouts)for(const line of [...layoutLines(layouts),...reframeLines(e,layouts)])console.log(line);
    const shots=filmShots(e),fps=e.output.fps;
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
        const globalStart=shot.start+cue.at,phase=Math.max(0,Math.ceil(globalStart*fps-1e-9)/fps-globalStart),start=element.inPoint??0;
        const continuation=Math.abs(cue.until-(shot.end-shot.start))<1e-9?joinShows(shots[i+1]?.shot.transition):0;
        const cadence=clipCadence(probe.timestamps,start,start+cue.until-cue.at+continuation,fps,phase);
        console.log(`  source ${probe.averageRate.toFixed(3)} fps into film ${fps} fps: `+
          `${cadence.dropped} dropped, ${cadence.repeated} repeated; audio not played`);
      }
    }
    // The trees a render would name the heads of, and whether they are dirty
    // now (ADR-015): the project's and this checkout's.
    await readTrees(e,'check');
    process.exit(0);
  }
  if(command==='speech'){await speech(e,{generate:true});process.exit(0);}
  if(command==='preview'){await preview(e,options);console.log('Storyboard: '+resolve(e.paths.build,'storyboard.jpg'));process.exit(0);}
  const audio=values.silent?null:await speech(e,{generate:command==='build'});
  if(command==='build'&&!values.silent)validateWordFramesAtFps(e,options.fps??e.output.fps);
  const output=await render(e,{...options,audio,label:values.silent?'silent-preview':'rehearsal'});
  console.log('Video: '+output);
}catch(error){console.error(error.message);process.exitCode=1;}
