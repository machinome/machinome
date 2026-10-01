// Evidence of the flaky-pixel-proofs investigation (30 September 2026), not
// part of the suite: does Chromium draw the same scaled image the same way in
// every page? Opens PAGES fresh pages of one headless Chromium launched with
// the renderer's flags, draws the PNG at WIDTH x HEIGHT CSS pixels on a plain
// page of 320 x 180, decodes it, repaints the whole page as the stage does,
// screenshots it twice, and prints a short hash per page and the number of
// distinct renderings. MODE `sized` gives the <img> its size before its source
// is set, as the stage's picture element does; `late` sets the source, decodes
// and only then sizes it, as the old film page's drawPicture() did. Extra
// arguments are passed to Chromium.
//
//   node workflow/ongoing/fix-warts-campaign/flaky-pixel-proofs/two-renderings.mjs \
//     python/tests/fixtures/project/media/plate.png 12 300 200 late
//   ... 12 300 200 sized
//   ... 12 300 200 late --disable-gpu-rasterization
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {createServer} from 'node:http';
const root=new URL('../../../../',import.meta.url);
const {chromium}=await import(new URL('node_modules/playwright/index.mjs',root));
const {CHROMIUM_ARGS}=await import(new URL('src/render.mjs',root));
const [file,pages='12',width='300',height='200',mode='late',...extra]=process.argv.slice(2);
if(!file||!['sized','late'].includes(mode))throw new Error('usage: two-renderings.mjs <png> [pages] [width] [height] [sized|late] [chromium args...]');
const bytes=await readFile(file);
const html=`<!doctype html><html><body style="margin:0;background:#faf7ef">
<img id=img alt="" style="position:absolute;left:0;top:0;max-width:none"></body></html>`;
const server=createServer((req,res)=>{
  if(req.url==='/plate.png'){res.setHeader('Content-Type','image/png');res.end(bytes);}
  else{res.setHeader('Content-Type','text/html');res.setHeader('Connection','close');res.end(html);}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,args:[...CHROMIUM_ARGS,...extra]});
const sha=b=>createHash('sha256').update(b).digest('hex').slice(0,6),counts=new Map(),order=[];
for(let n=0;n<Number(pages);n++){
  const page=await browser.newPage({viewport:{width:320,height:180},deviceScaleFactor:1});
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.evaluate(async([width,height,mode])=>{
    const frames=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    const img=document.getElementById('img'),size=()=>Object.assign(img.style,{width:`${width}px`,height:`${height}px`});
    if(mode==='sized')size();
    img.src='/plate.png';await img.decode();
    if(mode==='late')size();
    const b=document.body.style.background;document.body.style.background='#010203';await frames();
    document.body.style.background=b;await frames();
  },[width,height,mode]);
  const a=sha(await page.screenshot()),b=sha(await page.screenshot());
  order.push(a===b?a:`${a}|${b}`);for(const h of new Set([a,b]))counts.set(h,(counts.get(h)??0)+1);
  await page.close();
}
await browser.close();server.close();
console.log(order.join(' '));
console.log(`${counts.size} distinct rendering${counts.size===1?'':'s'} in ${pages} pages:`,JSON.stringify(Object.fromEntries(counts)));
