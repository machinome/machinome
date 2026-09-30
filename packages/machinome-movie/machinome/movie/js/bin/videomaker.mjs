#!/usr/bin/env node
import {parseArgs} from 'node:util';
import {resolve,dirname,extname} from 'node:path';
import {readFile} from 'node:fs/promises';
import {loadEpisode,requiredViewerApi,confirmViewerApi} from '../src/episode.mjs';
import {speech} from '../src/speech.mjs';
import {generateMovieTakes} from '../src/movie.mjs';
import {validateWordFramesAtFps} from '../src/words.mjs';
import {prepareWordTimingForCommand} from '../src/command-timing.mjs';
import {preview,render} from '../src/render.mjs';
import {pictureReports,clipCadenceForCue} from '../src/pictures.mjs';
import {reviewManifest} from '../src/review-pack.mjs';

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
  const e=await loadEpisode(source);
  const options={viewer:resolve(values.viewer??resolve(dirname(e.paths.manifest),'machinome-viewer.js')),
    width:values.width?Number(values.width):undefined,fps:values.fps?Number(values.fps):undefined};
  if(options.width!==undefined&&(!Number.isInteger(options.width)||options.width<320||options.width%2))throw new Error('Width must be an even integer >= 320');
  if(options.fps!==undefined&&(!Number.isInteger(options.fps)||options.fps<1||options.fps>120))throw new Error('FPS must be an integer from 1 to 120');
  console.log(`${e.title}: ${e.shots.length} shots, ${e.output.durationSeconds}s; model ${e.model.expectedDurationSeconds}s`);
  await prepareWordTimingForCommand(e,{command,silent:Boolean(values.silent),fps:options.fps??e.output.fps});
  if(command==='check'){
    // check has no browser; preview and render confirm the running viewer's apiVersion instead.
    const required=requiredViewerApi(e);
    if(required.api>21){
      const declared=confirmViewerApi(required,await readFile(options.viewer,'utf8').catch(()=>null));
      console.log(`Viewer API ${required.api} required for ${required.reasons.join(', ')}; ${options.viewer} declares API ${declared}`);
    }
    for(const report of pictureReports(e)){
      console.log(`Picture ${report.shotId} #${report.index} (${report.kind} ${report.name}): `+
        (report.peak===null?'vector, no enlargement limit':`peak ${report.peak.toFixed(2)}×; allowance ${report.allowance}×`));
      if(report.kind==='clip'){
        const shot=e.shots.find(s=>s.id===report.shotId),cue=shot.pictures[report.index],media=e.pictureMedia.clips[report.name];
        const cadence=clipCadenceForCue(e,shot,cue,media);
        console.log(`  source ${media.averageRate.toFixed(3)} fps into film ${e.output.fps} fps: `+
          `${cadence.dropped} dropped, ${cadence.repeated} repeated; audio not played`);
      }
    }
    process.exit(0);
  }
  if(command==='speech'){await speech(e,{generate:true});process.exit(0);}
  if(command==='preview'){await preview(e,options);console.log('Storyboard: '+resolve(e.paths.build,'storyboard.jpg'));process.exit(0);}
  const audio=values.silent?null:await speech(e,{generate:command==='build'});
  if(command==='build'&&!values.silent)validateWordFramesAtFps(e,options.fps??e.output.fps);
  const output=await render(e,{...options,audio,label:values.silent?'silent-preview':'rehearsal'});
  console.log('Video: '+output);
}catch(error){console.error(error.message);process.exitCode=1;}
