#!/usr/bin/env node
import {parseArgs} from 'node:util';
import {resolve,extname} from 'node:path';
import {loadEpisode} from '../src/episode.mjs';
import {speech} from '../src/speech.mjs';
import {generateMovieTakes} from '../src/movie.mjs';
import {validateWordFramesAtFps} from '../src/words.mjs';
import {prepareWordTimingForCommand} from '../src/command-timing.mjs';
import {preview,render,highlightLine} from '../src/render.mjs';
import {reviewManifest} from '../src/review-pack.mjs';
import {checkSource,commandOptions,summaryLine} from '../src/check.mjs';
import {live} from '../src/live.mjs';

try{
  const {positionals,values}=parseArgs({allowPositionals:true,options:{viewer:{type:'string'},width:{type:'string'},fps:{type:'string'},silent:{type:'boolean'},
    port:{type:'string'},poll:{type:'string'},open:{type:'boolean'},help:{type:'boolean'}}});
  const [command,source]=positionals;
  if(values.help||!source){console.log('videomaker check|speech|preview|render|build EPISODE.yaml|MOVIE.json [--viewer BUNDLE.js] [--width 960] [--fps 10] [--silent]\n'+
    'videomaker live EPISODE.yaml|MOVIE.json [--viewer BUNDLE.js] [--width 960] [--port 0] [--poll MS] [--open]\nvideomaker review MANIFEST.json');process.exit(source?0:1);}
  if(command==='review'){
    const result=await reviewManifest(source);
    console.log(`Review pack: ${result.generation}${result.reused?' (verified reuse)':''}`);
    process.exit(0);
  }
  if(!['check','speech','preview','render','build','live'].includes(command))throw new Error('Unknown command: '+command);
  // Each command takes its own options and no other's.
  const own=command==='live'?['viewer','width','port','poll','open']:['viewer','width','fps','silent'];
  for(const name of Object.keys(values))if(name!=='help'&&!own.includes(name))throw new Error(`The ${command} command takes no --${name}`);
  // live checks the film as check does, serves it at one address and reloads
  // it when its inputs change, until it is interrupted (src/live.mjs).
  if(command==='live'){
    const session=await live(source,{viewer:values.viewer,width:values.width?Number(values.width):undefined,
      port:values.port===undefined?0:Number(values.port),poll:values.poll===undefined?0:Number(values.poll),open:Boolean(values.open)});
    console.log(`Live: ${session.origin}/`);
    const stop=()=>session.close().then(()=>process.exit(0),error=>{console.error(error.message);process.exit(1);});
    process.once('SIGINT',stop);process.once('SIGTERM',stop);
  }else{
    // A movie document's takes need only its narration: speech generates them
    // before the anchors that depend on them are resolved (movie-document D4),
    // once every check of the load that needs no take has passed
    // (speech-loads-first).
    if(extname(source).toLowerCase()==='.json'&&(command==='speech'||command==='build'&&!values.silent))await generateMovieTakes(source);
    const numbers={width:values.width?Number(values.width):undefined,fps:values.fps?Number(values.fps):undefined};
    // check's body is checkSource (src/check.mjs), which live loads with too.
    if(command==='check'){
      await checkSource(source,{viewer:values.viewer,...numbers,silent:Boolean(values.silent)});
      process.exit(0);
    }
    const e=await loadEpisode(source);
    const options=commandOptions(e,{viewer:values.viewer,...numbers});
    console.log(summaryLine(e));
    await prepareWordTimingForCommand(e,{command,silent:Boolean(values.silent),fps:options.fps??e.output.fps});
    if(command==='speech'){await speech(e,{generate:true});process.exit(0);}
    if(command==='preview'){
      const report=await preview(e,options);
      // Where each highlight landed, by its parts (ADR-017).
      for(const h of report.highlightChecks??[])console.log(highlightLine(h));
      console.log('Storyboard: '+resolve(e.paths.build,'storyboard.jpg'));process.exit(0);
    }
    const audio=values.silent?null:await speech(e,{generate:command==='build'});
    if(command==='build'&&!values.silent)validateWordFramesAtFps(e,options.fps??e.output.fps);
    const output=await render(e,{...options,audio,label:values.silent?'silent-preview':'rehearsal'});
    console.log('Video: '+output);
  }
}catch(error){console.error(error.message);process.exitCode=1;}
