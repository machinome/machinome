// Decoded pixels of each flag variant's frames against the stage flags'
// frames (round 0 of a flags run), frame by frame: equal frames, differing
// pixels per frame, the largest level difference.
//   node compare-flags.mjs > raw/curta-flags-pixels.txt   (after a flags run)
import {readFileSync,readdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {decodePng} from '../../../../src/pixels.mjs';

const dir=resolve(dirname(fileURLToPath(import.meta.url)),'_build/curta/frames');
const reference='stage-0';
const files=readdirSync(resolve(dir,reference,'generation')).filter(f=>f.endsWith('.png')).sort();
for(const variant of readdirSync(dir).filter(v=>/-\d+$/.test(v)&&!v.startsWith('parallel')&&v!==reference).sort()){
  let same=0,n=0,differing=0,largest=0;
  for(const f of files){
    let b;try{b=decodePng(readFileSync(resolve(dir,variant,'generation',f))).rgb;}catch{continue;}
    const a=decodePng(readFileSync(resolve(dir,reference,'generation',f))).rgb;n++;
    if(a.equals(b)){same++;continue;}
    for(let i=0;i<a.length;i+=3){let m=0;for(let c=0;c<3;c++)m=Math.max(m,Math.abs(a[i+c]-b[i+c]));if(m){differing++;largest=Math.max(largest,m);}}
  }
  console.log(`${variant} against ${reference}: decoded pixels equal in ${same}/${n} frames; ${(differing/Math.max(1,n)).toFixed(0)} differing pixels per frame; largest level difference ${largest}`);
}
