// Read-only renderer diagnosis for Leonardo's source-grid frame 10.
// Captures repeated poses inside one browser mount; writes evidence only.
import {mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {loadEpisode} from '../../src/episode.mjs';
import {prepareWordTimingForCommand} from '../../src/command-timing.mjs';
import {browserSession} from '../../src/render.mjs';

const [source,viewer,output]=process.argv.slice(2);
if(!source||!viewer||!output)throw new Error('Usage: node diagnose-frame10.mjs EPISODE VIEWER OUTPUT_DIR');
const e=await loadEpisode(source);
await prepareWordTimingForCommand(e,{command:'render',silent:true});
const dir=resolve(output);
await mkdir(dir,{recursive:true});
const poses=[1,1,1,0.5,1,1.1,1];
const observations=[];
const report=await browserSession(e,resolve(viewer),960,[],async({page,pose})=>{
  for(let i=0;i<poses.length;i++){
    const time=poses[i];
    await pose(time);
    const bytes=await page.screenshot();
    const file=resolve(dir,`${String(i).padStart(2,'0')}-${time.toFixed(1)}.png`);
    await writeFile(file,bytes);
    observations.push({index:i,time,file,sha256:createHash('sha256').update(bytes).digest('hex')});
  }
  return {observations};
});
const data={source,viewer,output:dir,browser:report.browser,viewerApi:report.viewerApi,framesChecked:report.framesChecked,observations};
await writeFile(resolve(dir,'report.json'),JSON.stringify(data,null,2)+'\n');
console.log(JSON.stringify(data,null,2));
