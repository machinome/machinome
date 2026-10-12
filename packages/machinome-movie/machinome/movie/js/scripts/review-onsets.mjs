// Diagnostic only: signal preservation is not a listening/intelligibility verdict.
import {readFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
const [manifest,...targets]=process.argv.slice(2);
if(!manifest||!targets.length)throw new Error('Usage: node scripts/review-onsets.mjs AUDIO-MANIFEST MIX.wav [FINAL.mp4]');
const {records}=JSON.parse(await readFile(manifest,'utf8'));
const rate=16000;
function decode(file){const b=execFileSync('ffmpeg',['-v','error','-i',file,'-vn','-f','f32le','-ac','1','-ar',String(rate),'pipe:1'],{maxBuffer:256*1024*1024});return new Float32Array(b.buffer,b.byteOffset,b.length/4);}
const results=targets.map(file=>({file,signal:decode(file),onsets:[]}));
for(const record of records){
  const source=decode(record.file),offset=Math.round(record.offset*rate);
  const active=source.findIndex(v=>Math.abs(v)>.005);
  for(const target of results){
    let xy=0,xx=0,yy=0;
    for(let i=Math.max(active,0);i<Math.min(source.length,Math.max(active,0)+rate*.35);i++){
      const x=source[i],y=target.signal[offset+i]??0;xy+=x*y;xx+=x*x;yy+=y*y;
    }
    target.onsets.push({id:record.id,rawActiveAt:active/rate,offset:record.offset,correlation:xy/Math.sqrt(xx*yy),gain:Math.sqrt(yy/xx)});
  }
}
console.log(JSON.stringify({method:'First 350ms after raw signal crosses 0.005; mono 16kHz, original offset; no listening verdict',results:results.map(({signal,...r})=>r)},null,2));
