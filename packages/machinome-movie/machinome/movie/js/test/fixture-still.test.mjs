// Layer 9 (pure): the fixture project's still is the drawing
// scripts/draw-fixture-still.mjs makes, byte for byte the same every run, and
// the tour's template puts it over its stage as a film puts a drawing, at an
// enlargement inside the allowance the fixture declares.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {drawFixtureStill,STILL,WIDTH,HEIGHT} from '../scripts/draw-fixture-still.mjs';
import {decodePng} from '../src/pixels.mjs';

const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const project=join(root,'..','..','..','tests','fixtures','project');

test('the fixture still is drawn to the same bytes on every run, in flat shapes',()=>{
  const once=drawFixtureStill(),again=drawFixtureStill();
  assert.ok(once.equals(again),'two drawings differ');
  const {width,height,rgb}=decodePng(once);
  assert.deepEqual([width,height],[WIDTH,HEIGHT]);
  const colours=new Set();
  for(let i=0;i<rgb.length;i+=3)colours.add(rgb.readUIntBE(i,3));
  assert.equal(colours.size,9,'the paper and the eight shapes, each one flat colour with a hard edge');
});

test('the committed still is the drawing',async()=>{
  const committed=decodePng(await readFile(STILL)),drawn=decodePng(drawFixtureStill());
  assert.deepEqual([committed.width,committed.height],[drawn.width,drawn.height],
    'media/plate.png is not the drawing; run node scripts/draw-fixture-still.mjs');
  assert.ok(committed.rgb.equals(drawn.rgb),'media/plate.png is not the drawing; run node scripts/draw-fixture-still.mjs');
});

// A rule's left, top, width and height, in fractions of the frame, from its
// per-cent insets and size (a right or bottom inset counts from the far side).
function box(css,rule){
  const body=new RegExp(`\\.${rule}\\s*\\{([^}]*)\\}`).exec(css)?.[1];
  assert.ok(body,`stage.css has no rule .${rule}`);
  const read=side=>{const v=new RegExp(`(?:^|[;\\s])${side}:\\s*([\\d.]+)%`).exec(body)?.[1];return v===undefined?null:Number(v)/100;};
  const [width,height]=[read('width'),read('height')];
  assert.ok(width!==null&&height!==null,`.${rule} has no width and height in per cent`);
  const left=read('left')??1-read('right')-width,top=read('top')??1-read('bottom')-height;
  assert.ok(Number.isFinite(left)&&Number.isFinite(top),`.${rule} has no inset in per cent`);
  return [left,top,width,height].map(v=>+v.toFixed(6));
}

test('the tour puts its still over the stage, drawn whole inside its allowance at the peak zoom',async()=>{
  const css=await readFile(join(project,'videos','tour','stage.css'),'utf8');
  assert.deepEqual(box(css,'playbill-plate'),box(css,'playbill-stage'),'the plate covers the stage');
  const tour=JSON.parse(await readFile(join(root,'fixtures','documents','tour.json'),'utf8'));
  const [,,w,h]=box(css,'playbill-plate'),{width:W,height:H}=tour.output;
  const shot=tour.chapters.flatMap(c=>c.shots).find(s=>s.id==='still');
  const show=shot.cues.flatMap(c=>c.actions).find(a=>a.action==='show');
  const element=tour.chapters.find(c=>c.shots.includes(shot)).elements[show.element];
  assert.deepEqual([element.still,element.fit],['plate','contain']);
  const fitted=Math.min(w*W/WIDTH,h*H/HEIGHT),peak=fitted*Math.max(...show.view.map(k=>k.zoom));
  assert.ok(Math.abs(fitted-1)<1e-9,`fitted whole, the still is drawn at its own size, not ${fitted}×`);
  assert.ok(peak<=tour.stills.plate.upscale,`peak enlargement ${peak} exceeds the allowance ${tour.stills.plate.upscale}`);
});
