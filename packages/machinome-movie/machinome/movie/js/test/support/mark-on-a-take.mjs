// The proof that a mark on a part a take moves follows the part from one bank
// to another (the double-poses-a-bank change), on the fixture movie `count`.
// The browser layer calls it with the viewer double, whose machine moves its
// part rectangles with its bank, and the viewer layer with the selected
// bundle, so both layers make one assertion. Not a test file: it registers no
// tests.
import assert from 'node:assert/strict';
import {browserSession} from './stage.mjs';
import {frameAt,filmShots} from '../../src/timeline.mjs';

const VIEW='counting.view',WIDTH=640;
// A ring on the units drum, as the timeline draws a ring cue at rest.
export const UNITS_RING={id:'units-ring',kind:'ring',target:{paths:[['units_drum']]},padding:.01,opacity:1,drawn:1};

// Poses `count` at the take's start (the initial bank), at the mark one (the
// start of shot nine) and at the start again, the ring added to the view's
// own state each time, on `viewer` (a double's file or a bundle's path), and
// asserts that the ring moved with the bank and came back exactly.
export async function assertMarkFollowsTheBank(film,viewer){
  const start=0,one=filmShots(film).find(s=>s.shot.id==='nine').shot.start;
  const [a,b]=[frameAt(film,start),frameAt(film,one)];
  // Both frames place the view in one set with one camera, so a difference
  // in the ring's place is the bank's.
  assert.equal(a.set,b.set,'the take\'s start and the mark one are filmed on one set');
  assert.deepEqual([a.elements[VIEW].view,a.elements[VIEW].fov],[b.elements[VIEW].view,b.elements[VIEW].fov],'with one camera');
  assert.deepEqual(a.elements[VIEW].bank,film.take.initial);
  assert.deepEqual(b.elements[VIEW].bank,film.take.banks.one);
  assert.notEqual(a.elements[VIEW].bank.units,b.elements[VIEW].bank.units,'the units drum turns between them');
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    const grab=async t=>{
      const state=frameAt(film,t).elements[VIEW];
      const f=await pose(t,{transition:null,elements:{[VIEW]:{...state,marks:[...state.marks,UNITS_RING]}}});
      const view=f.observed.elements[VIEW];
      return {png:await page.screenshot(),bank:view.bank,box:view.box,ring:view.marks.find(m=>m.id===UNITS_RING.id)??null};
    };
    const first=await grab(start),mark=await grab(one),again=await grab(start);
    return {result:{first,mark,again}};
  });
  const {first,mark,again}=seen.result;
  assert.deepEqual([first.bank,mark.bank,again.bank],[film.take.initial,film.take.banks.one,film.take.initial],'each pose holds its frame\'s bank');
  assert.deepEqual(mark.box,first.box,'the view has one box at both instants');
  assert.ok(first.ring?.rect&&mark.ring?.rect,'the ring reached the picture at both instants');
  const where=r=>`rect ${JSON.stringify(r.rect)}, anchor ${JSON.stringify(r.anchor)}`;
  assert.notDeepEqual(mark.ring.rect,first.ring.rect,
    `the ring on units_drum moves with the bank: at the take's start ${where(first.ring)}, at the mark one ${where(mark.ring)}`);
  assert.notDeepEqual(mark.ring.anchor,first.ring.anchor,'its anchor moves with it');
  assert.deepEqual([again.ring.rect,again.ring.anchor],[first.ring.rect,first.ring.anchor],
    'the take\'s start posed after the mark one places the ring as its first pose did');
  assert.ok(first.png.equals(again.png),'the take\'s start is drawn identically, its ring included, after the mark one');
  assert.ok(!first.png.equals(mark.png),'two banks are two pictures');
}
