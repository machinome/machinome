#!/usr/bin/env node
// Draws the fixture project's still, python/tests/fixtures/project/media/plate.png:
// a seesaw in flat, hard-edged shapes with no text (a stand, a tilted plank, a
// weight on its low end, the ground, a hill and a sun), so that pixel proofs
// have edges to compare.
//
// Its size is the tour's: the playbill's `plate` covers its `stage`, 68 % by
// 80 % of a 1280 by 720 film, 870.4 by 576 pixels, where a 3:2 picture fitted
// whole is 864 by 576 and so drawn at its own size. The `still` shot's zoom of
// 1.4 is then its peak enlargement, inside the allowance of 1.5 the fixture
// declares (`videos/takes.py`).
//
// Every coordinate is an integer, every pixel is sampled at its centre, and
// every test is additions and multiplications, so the same script draws the
// same pixels on every machine and the same bytes on every run.
// Usage: node scripts/draw-fixture-still.mjs
import {writeFile} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {encodeRgbPng} from '../src/pixels.mjs';

export const WIDTH=864,HEIGHT=576;
export const STILL=join(dirname(fileURLToPath(import.meta.url)),'..','python','tests','fixtures','project','media','plate.png');

const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
const circle=(cx,cy,r)=>(x,y)=>(x-cx)*(x-cx)+(y-cy)*(y-cy)<=r*r;
// A convex polygon: the point is on one side of every edge.
const polygon=(...points)=>(x,y)=>{
  let below=false,above=false;
  for(let i=0;i<points.length;i++){
    const [ax,ay]=points[i],[bx,by]=points[(i+1)%points.length];
    const side=(bx-ax)*(y-ay)-(by-ay)*(x-ax);
    if(side<0)below=true;else if(side>0)above=true;
  }
  return !(below&&above);
};
const band=(top,bottom)=>(x,y)=>y>=top&&y<bottom;

// Painted in order, each over the ones before it.
const SHAPES=[
  [circle(170,620,260),'#dcd2b6'],                          // a hill behind
  [circle(744,100,46),'#e3a73c'],                           // the sun
  [band(462,470),'#5a4830'],                                // the ground's edge
  [band(470,HEIGHT),'#c7b487'],                             // the ground
  [polygon([432,292],[512,462],[352,462]),'#56676f'],       // the stand
  [polygon([117,358],[741,202],[747,226],[123,382]),'#9b5c2f'], // the plank, low on the left
  [circle(180,301,40),'#237c86'],                           // the weight on its low end
  [circle(432,292,9),'#202020'],                            // the pivot
].map(([inside,colour])=>[inside,rgb(colour)]);
const PAPER=rgb('#f3eddc');

// The still's PNG bytes.
export function drawFixtureStill(){
  const pixels=Buffer.alloc(WIDTH*HEIGHT*3);
  for(let y=0;y<HEIGHT;y++)for(let x=0;x<WIDTH;x++){
    let colour=PAPER;
    for(const [inside,paint] of SHAPES)if(inside(x+.5,y+.5))colour=paint;
    pixels.set(colour,(y*WIDTH+x)*3);
  }
  return encodeRgbPng(WIDTH,HEIGHT,pixels);
}

if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  await writeFile(STILL,drawFixtureStill());
  console.log(`Wrote ${STILL} (${WIDTH}×${HEIGHT}).`);
}
