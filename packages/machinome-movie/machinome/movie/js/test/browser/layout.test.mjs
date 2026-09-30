// Layer 5 (serial; Chromium, the viewer double): the layout `check` measures
// (src/layout.mjs, ADR-009) is the layout a frame is drawn in. The probe poses
// each set of the fixture tour empty, on a page with a stub viewer, at the
// tour's 1280×720; the renderer's session poses a frame of each set at the
// same size, with its elements; every slot the probe trusts has the same box
// in both, and a picture placed in `plate` gets the box the probe measured
// for a picture there.
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {browserSession,sharedStage} from '../support/stage.mjs';
import {fixtureMovie} from '../support/fixture-movie.mjs';
import {loadEpisode} from '../../src/episode.mjs';
import {readMovie} from '../../src/movie.mjs';
import {buildFilmStage} from '../../src/stage-build.mjs';
import {filmShots} from '../../src/timeline.mjs';
import {measureLayouts,trusted} from '../../src/layout.mjs';

const same=(rect,box)=>[rect.x,rect.y,rect.width,rect.height].every((v,i)=>Math.abs(v-box[i])<=1e-6);

test('the boxes check measures for a set are the boxes a posed frame of that set reports',async t=>{
  const {file,viewer}=await fixtureMovie(t,'tour');
  const film=await loadEpisode(file),{doc}=await readMovie(file);
  const layouts=await measureLayouts(doc,await buildFilmStage(film),await sharedStage());
  assert.deepEqual([layouts.width,layouts.height],[1280,720]);
  assert.deepEqual(Object.keys(layouts.sets),['playbill','frame','playbill-split','split'],'every set the tour uses, once, in the order its shots first use them');
  // The title band is as tall as the title it holds: sized by what it holds,
  // so check leaves it to the live box.
  for(const kind of ['playbill','playbill-split'])
    assert.equal(layouts.sets[kind].find(s=>s.slot==='headline').fixed,false,`${kind}.headline`);
  for(const kind of ['playbill','frame','playbill-split','split'])
    for(const slot of layouts.sets[kind].filter(s=>s.slot!=='headline'))assert.ok(trusted(slot),`${kind}.${slot.slot} is trusted`);
  // One frame of each set, and the still's, posed at the output size.
  const middle=id=>{const {shot}=filmShots(film).find(s=>s.shot.id===id);return (shot.start+shot.end)/2;};
  const posed=await browserSession(film,viewer,film.output.width,[],async({pose})=>{
    const out={};
    for(const id of ['hook','question','holds','source','push','still'])out[id]=await pose(middle(id),{transition:null});
    return {result:out};
  });
  let compared=0;
  for(const [id,f] of Object.entries(posed.result)){
    for(const slot of layouts.sets[f.set].filter(trusted)){
      assert.ok(same(f.observed.slots[slot.slot],slot.box),`${f.set}.${slot.slot} in ${id}: posed ${JSON.stringify(f.observed.slots[slot.slot])}, measured ${slot.box}`);
      compared++;
    }
  }
  assert.equal(compared,3+3+1+2+2+3,'every trusted slot of every posed frame');
  const plate=layouts.sets.playbill.find(s=>s.slot==='plate');
  assert.ok(same(posed.result.still.observed.elements['tip.plate'].box,plate.picture),'the still is drawn in the box measured for a picture in plate');
  // What the headline would have been judged by: the question's title makes
  // its box, which the empty set does not have.
  const headline=posed.result.question.observed.slots.headline,empty=layouts.sets.playbill.find(s=>s.slot==='headline').box;
  assert.ok(headline.height>0&&!same(headline,empty),`headline with its title ${JSON.stringify(headline)}, empty ${empty}`);
});
