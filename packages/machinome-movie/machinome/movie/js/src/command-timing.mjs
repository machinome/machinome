import {resolveWordTiming,validateWordFramesAtFps} from './words.mjs';
import {readSpeechTake} from './speech.mjs';

// The only provider route is speech/build with narration. All other commands,
// including a silent build, read the exact cached take before opening a page.
export async function prepareWordTimingForCommand(e,{command,silent=false,fps=e.output.fps},read=readSpeechTake){
  if(command==='speech'||command==='build'&&!silent)return;
  await resolveWordTiming(e,shot=>read(e,shot));
  if(command==='render'||command==='build'&&silent)validateWordFramesAtFps(e,fps);
}
