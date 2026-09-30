// Layer 3 (pure): the frame is a pure function of the resolved document and
// video time (design D4; docs/movie-document.md, "The frame"). Inline resolved
// fixtures only: no file, no DOM, no provider.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {frameAt,checkFilm,filmShots} from '../src/timeline.mjs';
import {ease} from '../src/easing.mjs';
import {DEFAULT_STYLE} from '../src/style.mjs';
import {outputShotUnits} from '../src/shot-cache.mjs';

const unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};
const close=(actual,expected,what='')=>{
  if(Array.isArray(expected))return expected.forEach((v,i)=>close(actual[i],v,`${what}[${i}]`));
  assert.ok(Math.abs(actual-expected)<1e-9,`${what} ${actual} is not ${expected}`);
};
const CAMERAS={a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},
  b:{position:[10,-10,0],target:[0,0,2],up:[0,0,1],fov:20},
  r:{position:[0,-10,0],target:[0,0,0],up:[1,0,1],fov:37},
  along:{position:[0,-10,0],target:[0,0,0],up:[0,1,0],fov:37}};
const TEXT='wheel.drives(saw)\nsaw.cuts(wheel)';
const shot=(id,until,more)=>({id,until,cues:[],...more});
// A resolved movie of two chapters and six shots, 12 s at 10 fps:
//   drive: one [0, 2) fadeIn, two [2, 4) cut, three [4, 5) dissolve;
//   tip:   rise [5, 8) wipe, rhythm [8, 10) slide right, closing [10, 12) fade and fadeOut.
function film(edit){
  const doc={format:'machinome-movie/0.2',resolved:true,id:'inline',title:'Inline',output:{width:320,height:180,fps:10},
    model:{expectedDurationSeconds:20},style:{accent:'#bf531f'},cameras:structuredClone(CAMERAS),
    layers:{frame:[['Frame']],load:[['Beam','Plank'],['Beam','Weight']]},
    sourceCode:{drive:{file:'m.py',lines:[10,11]}},stills:{plate:{}},clips:{reel:{}},
    stage:{modules:[],elements:{},sets:{}},
    chapters:[
      {id:'drive',narration:'x',speechOffset:.2,elements:{
        view:{kind:'view',camera:'a',hide:['frame']},code:{kind:'source',source:'drive'},
        card:{kind:'tally',props:{items:['A','B']}}},shots:[
        shot('one',2,{set:'split',places:{left:'code',right:'view',aside:'card'},model:{from:0,to:4},fadeIn:{duration:.5},cues:[
          {at:.5,actions:[{element:'view',action:'move',camera:'b',until:1.5}]},
          {at:0,actions:[{element:'code',action:'type',throughLine:10,over:1}]},
          {at:.5,until:1.5,actions:[{element:'card',action:'light',params:{item:'A'}}]},
          {at:1.2,actions:[{element:'code',action:'emphasize',words:[{spoken:'drives',token:'drives',at:1.2}],until:1.8}]}]}),
        shot('two',2,{set:'split',places:{left:'code',right:'view',aside:'card'},
          model:{keys:[{at:0,seconds:4},{at:1,seconds:4},{at:2,seconds:8,ease:'in'}]},cues:[
          {at:.5,actions:[{element:'code',action:'type',throughLine:11,over:1}]},
          {at:1.6,actions:[{element:'code',action:'emphasize',line:11,
            words:[{spoken:'saw',token:'saw',at:1.6},{spoken:'wheel',token:'wheel',at:1.8}],until:1.95}]},
          {at:1,until:2,actions:[{element:'card',action:'light',params:{item:'B'}}]}]}),
        shot('three',1,{set:'split',places:{left:'code',right:'view'},model:{from:8,to:9},
          transition:{kind:'dissolve',duration:.5,ease:'linear'}})]},
      {id:'tip',narration:'y',speechOffset:.2,elements:{
        close:{kind:'view',camera:'a'},heading:{kind:'title',text:'Rise and fall',subtitle:'One beam'},
        beat:{kind:'title',text:'Up. Down.'},plate:{kind:'picture',still:'plate'},
        reel:{kind:'picture',clip:'reel',inPoint:.5,fit:'cover'}},shots:[
        shot('rise',3,{set:'board',places:{stage:'close',headline:'heading',plate:'plate'},model:{from:4,to:6},
          transition:{kind:'wipe',duration:.4},cues:[
          {at:0,until:3,actions:[{element:'heading',action:'show',enter:{kind:'fade',duration:.4},leave:{kind:'fade',duration:.5,ease:'linear'}}]},
          {at:.5,until:2.5,actions:[
            {element:'close',action:'ring',part:['Beam'],enter:{kind:'draw',duration:.8,ease:'out'},leave:{kind:'fade',duration:.4}},
            {element:'close',action:'label',part:'load',text:'Load',offset:[.1,-.1],enter:{kind:'fade',duration:.4}},
            {element:'close',action:'highlight',parts:[['Beam']]}]},
          {at:1,until:3,actions:[
            {element:'close',action:'arrow',point:[0,0,1],place:[.2,.3],text:'Here'},
            {element:'close',action:'ring',part:['Stand'],leave:{kind:'fade',duration:.4}}]},
          {at:0,actions:[{element:'close',action:'move',camera:'r',until:2,ease:'linear'}]},
          {at:.5,until:3,actions:[{element:'plate',action:'show',enter:{kind:'fade',duration:.5},leave:{kind:'fade',duration:.5},
            view:[{at:.5,center:[.5,.5],zoom:1},{at:2.5,center:[.4,.4],zoom:2,ease:'linear'}]}]}]}),
        shot('rhythm',2,{set:'board',places:{stage:'close',headline:'beat',plate:'reel'},model:{from:6,to:6},
          transition:{kind:'slide',duration:.4,direction:'right'},cues:[
          {at:0,until:2,actions:[{element:'beat',action:'show',reveal:{timing:'spoken',onsets:[.3,.9]}}]},
          {at:.2,until:2,actions:[{element:'reel',action:'show'}]}]}),
        shot('closing',2,{set:'board',places:{stage:'close',headline:'heading',aside:'beat'},model:{from:6,to:7},
          transition:{kind:'fade',duration:.6},fadeOut:{duration:1},cues:[
          {at:0,until:2,actions:[{element:'beat',action:'show',reveal:{timing:'even',duration:1}}]},
          {at:0,until:1.5,actions:[{element:'close',action:'highlight',parts:['load'],others:'ghost',color:'#123456'}]}]})]}]};
  edit?.(doc);
  let clock=0;
  for(const chapter of doc.chapters){
    chapter.start=clock;
    for(const s of chapter.shots){s.start=clock;s.end=clock+s.until;clock=s.end;}
    chapter.end=clock;
  }
  doc.output.durationSeconds=clock;
  // What the load attaches: the excerpts' pinned text and the pictures' probes.
  doc.excerpts={drive:{file:'m.py',lines:[10,11],text:TEXT}};
  doc.pictureMedia={stills:{plate:{width:48,height:32}},
    clips:{reel:{end:3,timestamps:Array.from({length:13},(_,i)=>i/4)}}};
  return doc;
}
const state=(f,key)=>f.elements[`${f.chapterId}.${key}`];
const at=(movie,t,key)=>state(frameAt(movie,t),key);

test('a frame names its chapter, shot, set and slots, and holds every placed element complete',()=>{
  const movie=film(),f=frameAt(movie,1);
  assert.deepEqual(Object.keys(f),['time','chapterId','shotId','set','slots','elements','transition']);
  assert.equal(f.time,1);assert.equal(f.chapterId,'drive');assert.equal(f.shotId,'one');assert.equal(f.set,'split');
  assert.deepEqual(f.slots,{left:'drive.code',right:'drive.view',aside:'drive.card'});
  assert.deepEqual(Object.keys(f.elements).sort(),['drive.card','drive.code','drive.view']);
  assert.equal(f.transition,null);
  assert.deepEqual(Object.keys(frameAt(movie,5.5).elements).sort(),['tip.close','tip.heading','tip.plate']);
  assert.throws(()=>frameAt(movie,12),/Frame time 12 is outside the film/);
  assert.throws(()=>frameAt(movie,-.1),/outside the film/);
});

test('a view holds its camera, eases along a move by its curve (smooth by default) and continues across its chapter',()=>{
  const movie=film(),{a,b}=CAMERAS;
  // Before the move: the element's camera, exactly.
  assert.deepEqual(at(movie,.2,'view').view,{camera:a.position,target:a.target});
  assert.equal(at(movie,.2,'view').fov,37);
  // Along the move from 0.5 to 1.5, smooth by default.
  for(const local of [.5,.75,1,1.25]){
    const w=ease('smooth',(local-.5)/1),v=at(movie,local,'view');
    close(v.view.camera,a.position.map((x,i)=>x+(b.position[i]-x)*w),`camera at ${local}`);
    close(v.view.target,a.target.map((x,i)=>x+(b.target[i]-x)*w),`target at ${local}`);
    close(v.fov,37+(20-37)*w,`fov at ${local}`);
  }
  close(at(movie,.75,'view').view.camera[0],1.5625);
  // Held at its end, and where the next shots of the chapter start.
  for(const t of [1.5,1.9,2,3.9,4.2,4.9])assert.deepEqual(at(movie,t,'view').view,{camera:b.position,target:b.target},`at ${t}`);
  // The next chapter's view starts at its own camera.
  assert.deepEqual(at(movie,5,'close').view,{camera:a.position,target:a.target});
  // A linear move covers equal distances in equal times.
  const linear=film(d=>{d.chapters[0].shots[0].cues[0].actions[0].ease='linear';});
  const x=t=>at(linear,t,'view').view.camera[0];
  for(const t of [.6,.7,.8,.9,1,1.1])close(x(t+.1)-x(t),1,`step at ${t}`);
});

test('up is carried exactly between cameras that share it and mixed as unit directions when they differ',()=>{
  const movie=film();
  // a to b share up [0, 0, 1]: carried exactly, the same numbers.
  for(const t of [.2,.9,1.3])assert.deepEqual(at(movie,t,'view').up,[0,0,1]);
  // a to r (up [1, 0, 1]), linear over the rise's first 2 s.
  const ua=unit([0,0,1]),ub=unit([1,0,1]);
  for(const local of [0,.5,1,1.5,1.9]){
    const up=at(movie,5+local,'close').up,w=ease('linear',local/2);
    close(up,unit(ua.map((v,i)=>v+(ub[i]-v)*w)),`up at ${local}`);
    close(Math.hypot(...up),1,`unit at ${local}`);
  }
  // In the shot whose move changed it, the held up stays a unit vector; the
  // chapter's next shot, which does not change it, carries r's up exactly.
  assert.deepEqual(at(movie,7.5,'close').up,unit([1,0,1]));
  assert.deepEqual(at(movie,9,'close').up,[1,0,1]);
});

test('model time runs from and to, or along keys with their ease, over the export duration',()=>{
  const movie=film();
  close(at(movie,0,'view').time,0);close(at(movie,1,'view').time,2/20);close(at(movie,1.5,'view').time,3/20);
  // Keys: held from 0 to 1, then eased in to 8 at the shot's end.
  close(at(movie,2.5,'view').time,4/20);
  for(const local of [1,1.25,1.5,1.9])close(at(movie,2+local,'view').time,(4+4*ease('in',local-1))/20,`at ${local}`);
  // In a shot of another chapter, its own model.
  close(at(movie,6,'close').time,(4+2/3)/20);
  close(at(movie,9,'close').time,6/20);
});

test('hidden layers become paths; a view without hide hides nothing',()=>{
  const movie=film();
  assert.deepEqual(at(movie,1,'view').hidden,[['Frame']]);
  assert.deepEqual(at(movie,6,'close').hidden,[]);
});

test('a highlight is on from its at to its until; others default to keep and colour to the style accent',()=>{
  const movie=film();
  assert.equal(at(movie,5.4,'close').highlight,null);
  assert.deepEqual(at(movie,5.5,'close').highlight,{paths:[['Beam']],others:'keep',color:'#bf531f'});
  assert.equal(at(movie,7.5,'close').highlight,null,'until is exclusive');
  assert.deepEqual(at(movie,10.5,'close').highlight,{paths:[['Beam','Plank'],['Beam','Weight']],others:'ghost',color:'#123456'});
  // Without a style accent, the stage's default.
  const plain=film(d=>{d.style={};});
  assert.equal(at(plain,6,'close').highlight.color,DEFAULT_STYLE.accent);
});

test('marks carry their target, their own fields, and opacity and drawn through fades and draw-ons',()=>{
  const movie=film(),marks=local=>at(movie,5+local,'close').marks;
  const byId=(local,id)=>marks(local).find(m=>m.id===id);
  assert.deepEqual(marks(.4),[]);
  assert.deepEqual(marks(.5).map(m=>m.id),['cues[1].actions[0]','cues[1].actions[1]']);
  // The ring draws on, out-eased, at full opacity; the label fades in, smooth.
  assert.deepEqual(byId(.5,'cues[1].actions[0]'),{id:'cues[1].actions[0]',kind:'ring',target:{paths:[['Beam']]},padding:.01,opacity:1,drawn:0});
  close(byId(.9,'cues[1].actions[0]').drawn,ease('out',.5));close(byId(.9,'cues[1].actions[0]').drawn,.875);
  for(const local of [1.3,2])assert.equal(byId(local,'cues[1].actions[0]').drawn,1);
  assert.deepEqual(byId(.5,'cues[1].actions[1]'),{id:'cues[1].actions[1]',kind:'label',target:{paths:[['Beam','Plank'],['Beam','Weight']]},
    text:'Load',offset:[.1,-.1],opacity:0,drawn:1});
  close(byId(.7,'cues[1].actions[1]').opacity,ease('smooth',.5));
  assert.equal(byId(.9,'cues[1].actions[1]').opacity,1);
  // The ring fades out over its last 0.4 s; gone at its until.
  close(byId(2.3,'cues[1].actions[0]').opacity,1-ease('smooth',.5));
  assert.equal(byId(2.5,'cues[1].actions[0]'),undefined);
  // A mark with neither: full opacity, drawn; a point target; an arrow's place.
  assert.deepEqual(byId(1.5,'cues[2].actions[0]'),{id:'cues[2].actions[0]',kind:'arrow',target:{point:[0,0,1]},text:'Here',place:[.2,.3],opacity:1,drawn:1});
});

test('a source panel types where its chapter stopped, blinks its cursor by shot-local time, and holds a completed excerpt',()=>{
  const movie=film(),code=t=>at(movie,t,'code');
  const firstLine=TEXT.split('\n')[0];
  assert.deepEqual(code(0),{kind:'source',file:'m.py',firstLine:10,lastLine:11,text:'',html:'',cursor:true,emphasis:[]});
  assert.equal(code(.5).text,firstLine.slice(0,Math.floor(17*.5)));
  assert.equal(code(1).text,firstLine);
  // The second shot continues from the first's 17 characters, not from nothing.
  assert.equal(code(2.2).text,firstLine,'before its typing starts');
  assert.equal(code(3).text,TEXT.slice(0,17+Math.floor(16*.5)));
  assert.equal(code(3.5).text,TEXT);
  // Blinking on shot-local halves of a second while typing is incomplete.
  assert.equal(code(.2).cursor,true);assert.equal(code(.6).cursor,false);assert.equal(code(1.1).cursor,true);
  assert.equal(code(2.2).cursor,true);assert.equal(code(2.6).cursor,false);
  // Complete: no cursor, whatever the time; the next shot places it again, untyped.
  assert.equal(code(3.6).cursor,false);
  assert.deepEqual(code(4.2),{...code(3.6),emphasis:[]});
  assert.equal(code(4.2).text,TEXT);assert.equal(code(4.2).cursor,false);
  assert.ok(code(4.2).html.includes('<span'),'highlighted markup of the typed text');
});

test('emphasis lights each token from its word\'s onset to the action\'s until, on its line or in the whole excerpt',()=>{
  const movie=film(),lit=t=>at(movie,t,'code').emphasis;
  assert.deepEqual(lit(1.1),[]);
  // Whole excerpt: the only bounded "drives".
  assert.deepEqual(lit(1.2),[{token:'drives',start:6,end:12}]);
  assert.equal(TEXT.slice(6,12),'drives');
  assert.deepEqual(lit(1.8),[],'until is exclusive');
  // On line 11: "saw" bounded by the dot, not the "saw" of line 10; then "wheel" of line 11.
  assert.deepEqual(lit(3.5),[]);
  assert.deepEqual(lit(3.6),[{token:'saw',start:18,end:21}]);
  assert.deepEqual(lit(3.8),[{token:'saw',start:18,end:21},{token:'wheel',start:27,end:32}]);
  assert.equal(TEXT.slice(18,21),'saw');assert.equal(TEXT.slice(27,32),'wheel');
  assert.deepEqual(lit(3.95),[]);
  // An emphasis without resolved word times is refused, naming the shot.
  const raw=film(d=>{delete d.chapters[0].shots[1].cues[1].actions[0].words[0].at;});
  assert.throws(()=>frameAt(raw,3),/Word timing is not resolved: shot two/);
});

test('a title is placed shown or not, fades in and out, and reveals words as spoken or evenly',()=>{
  const movie=film(),heading=t=>at(movie,t,'heading');
  assert.deepEqual(heading(5),{kind:'title',shown:true,text:'Rise and fall',subtitle:'One beam',opacity:0});
  close(heading(5.2).opacity,ease('smooth',.5));
  assert.equal(heading(6).opacity,1);
  close(heading(7.75).opacity,.5,'linear exit midpoint');
  // Placed and not shown.
  assert.deepEqual(heading(11),{kind:'title',shown:false,text:'Rise and fall',subtitle:'One beam',opacity:0});
  // Spoken: words appear at their onsets, never before the cue.
  const beat=t=>at(movie,t,'beat');
  assert.deepEqual(beat(8.2).words.filter(p=>p.word).map(p=>p.text),['Up.','Down.']);
  assert.equal(beat(8.2).words.map(p=>p.text).join(''),'Up. Down.');
  assert.deepEqual([8,8.29,8.3,8.8,8.9,9.5].map(t=>beat(t).revealed),[0,0,1,1,2,2]);
  assert.equal(beat(8.5).opacity,1);assert.equal(beat(8.5).subtitle,undefined);
  // Even: the first word at the cue, then by eased progress over its duration.
  assert.deepEqual([10,10.4,10.5,10.9,11.5].map(t=>beat(t).revealed),[1,1,2,2,2]);
  const raw=film(d=>{delete d.chapters[1].shots[1].cues[0].actions[0].reveal.onsets;});
  assert.throws(()=>frameAt(raw,8.5),/Word timing is not resolved: shot rhythm/);
});

test('a picture shows its still through its view keys, a clip its frame by timestamp, and is placed unshown outside its cue',()=>{
  const movie=film(),plate=t=>at(movie,t,'plate'),reel=t=>at(movie,t,'reel');
  assert.deepEqual(plate(5.2),{kind:'picture',shown:false,media:'still',name:'plate',fit:'contain',opacity:0});
  assert.deepEqual(plate(5.5),{kind:'picture',shown:true,media:'still',name:'plate',fit:'contain',opacity:0,view:{center:[.5,.5],zoom:1}});
  close(plate(5.75).opacity,ease('smooth',.5));
  // Zoom geometric, the centre by the zoom's own weight, linear between keys.
  const mid=plate(6.5).view,z=Math.SQRT2,k=(1-1/z)/(1-1/2);
  close(mid.zoom,z);close(mid.center,[.5-.1*k,.5-.1*k]);
  assert.deepEqual(plate(7.6).view,{center:[.4,.4],zoom:2});
  close(plate(7.75).opacity,1-ease('smooth',.5));
  // A clip: its frame at inPoint plus the time since its cue, by the probe's timestamps.
  assert.deepEqual(reel(8.1),{kind:'picture',shown:false,media:'clip',name:'reel',fit:'cover',opacity:0});
  const {clipSeconds,...shown}=reel(9.2);
  assert.deepEqual(shown,{kind:'picture',shown:true,media:'clip',name:'reel',fit:'cover',opacity:1,
    view:{center:[.5,.5],zoom:1},frame:6});
  close(clipSeconds,.5+1);
  assert.equal(reel(8.2).frame,2);assert.equal(reel(8.2).clipSeconds,.5);
  const unprobed=film();unprobed.pictureMedia={stills:{},clips:{}};
  assert.throws(()=>frameAt(unprobed,9),/Picture media is not resolved: reel in shot rhythm/);
});

test('a project element carries its props and its active actions with since, until and progress',()=>{
  const movie=film(),card=t=>at(movie,t,'card');
  assert.deepEqual(card(.4),{kind:'tally',props:{items:['A','B']},actions:[]});
  assert.deepEqual(card(.5),{kind:'tally',props:{items:['A','B']},actions:[{action:'light',params:{item:'A'},since:.5,until:1.5,progress:0}]});
  close(card(1).actions[0].progress,.5);
  assert.deepEqual(card(1.5).actions,[],'until is exclusive');
  assert.deepEqual(card(3.5).actions,[{action:'light',params:{item:'B'},since:1,until:2,progress:.5}]);
});

test('an outgoing shot continues: model at its end rate, camera held, actions that ran to the end stay, leaving marks and pictures have left',()=>{
  const movie=film();
  // Two into three, a linear dissolve: "in" ends at three times its average rate (4 per second), so 12 per second.
  for(const u of [0,.1,.25,.4]){
    const x=frameAt(movie,4+u).transition,out=x.outgoing;
    assert.equal(x.outgoingShotId,'two');assert.equal(out.shotId,'two');assert.equal(out.transition,null);
    close(state(out,'view').time,(8+12*u)/20,`model at ${u}`);
    assert.deepEqual(state(out,'view').view,{camera:CAMERAS.b.position,target:CAMERAS.b.target});
    assert.equal(state(out,'code').text,TEXT);assert.equal(state(out,'code').cursor,false);
    // The emphasis ended before the cut; the tally light that ran to the end stays, complete.
    assert.deepEqual(state(out,'code').emphasis,[]);
    assert.deepEqual(state(out,'card').actions,[{action:'light',params:{item:'B'},since:1,until:2,progress:1}]);
  }
  // Rise into rhythm, a slide: the arrow without a leave stays at full strength,
  // the ring with a leave has left, the ended highlight is gone, the picture with a leave has left.
  const out=frameAt(movie,8.2).transition.outgoing,close$=state(out,'close');
  assert.equal(out.shotId,'rise');
  assert.deepEqual(close$.marks.map(m=>[m.id,m.opacity,m.drawn]),[['cues[2].actions[0]',1,1]]);
  assert.equal(close$.highlight,null);
  assert.equal(state(out,'plate').opacity,0);
  assert.deepEqual(close$.view,{camera:CAMERAS.r.position,target:CAMERAS.r.target});
  assert.deepEqual(close$.up,unit([1,0,1]));
  close(close$.time,(6+2/3*.2)/20,'linear end rate');
  // Rhythm into closing, a fade: the clip without a leave runs on through its continuation.
  const reel=state(frameAt(movie,10.1).transition.outgoing,'reel');
  assert.equal(reel.shown,true);assert.equal(reel.opacity,1);close(reel.clipSeconds,.5+1.9);assert.equal(reel.frame,9);
});

test('transitions: a dissolve eased, a wipe or slide with its direction, a fade through its plate, and the film\'s head and tail',()=>{
  const movie=film(),x=t=>frameAt(movie,t).transition;
  // fadeIn: exactly the colour on the first frame, gone at its end.
  assert.deepEqual(x(0),{field:'fadeIn',kind:'fade',shotId:'one',duration:.5,ease:'smooth',color:DEFAULT_STYLE.background,
    plate:1,picture:'incoming',outgoing:null});
  close(x(.25).plate,1-ease('smooth',.5));
  assert.equal(x(.5),null);assert.equal(x(2),null,'a cut has no transition');
  // Dissolve, linear.
  const dissolve=x(4.25);
  assert.equal(dissolve.kind,'dissolve');assert.equal(dissolve.field,'transition');assert.equal(dissolve.shotId,'three');
  assert.equal(dissolve.outgoingShotId,'two');assert.equal(dissolve.start,4);assert.equal(dissolve.duration,.5);
  close(dissolve.progress,.5);assert.equal(dissolve.direction,undefined);
  assert.equal(x(4).progress,0,'the first frame is the outgoing picture alone');
  assert.equal(x(4.5),null);
  // Wipe, smooth by default, left by default.
  assert.equal(x(5.1).kind,'wipe');assert.equal(x(5.1).direction,'left');close(x(5.1).progress,ease('smooth',.25));
  assert.equal(x(5.1).ease,'smooth');
  // Slide, right.
  assert.equal(x(8.1).kind,'slide');assert.equal(x(8.1).direction,'right');
  // Fade between shots: the outgoing picture under a rising plate, then the incoming under a falling one.
  assert.equal(x(10).plate,0);assert.equal(x(10).picture,'outgoing');assert.equal(x(10).outgoing.shotId,'rhythm');
  assert.equal(x(10).color,DEFAULT_STYLE.background);
  close(x(10.15).plate,ease('smooth',.5));assert.equal(x(10.15).picture,'outgoing');
  assert.equal(x(10.3).plate,1);assert.equal(x(10.3).picture,'incoming');assert.equal(x(10.3).outgoing,null);
  close(x(10.45).plate,1-ease('smooth',.5));
  assert.equal(x(10.6),null);
  // fadeOut: nothing at its start, exactly the colour on the film's last frame.
  assert.equal(x(11).field,'fadeOut');assert.equal(x(11).plate,0);assert.equal(x(11).picture,'incoming');
  assert.equal(x(11.9).plate,1);assert.equal(x(11.9).color,DEFAULT_STYLE.background);
  const black=film(d=>{d.chapters[1].shots[2].fadeOut.color='#000000';});
  assert.equal(frameAt(black,11.9).transition.color,'#000000');assert.equal(frameAt(black,11.9).transition.plate,1);
});

test('the same instant resolves twice to the same frame, whatever was asked before',()=>{
  const movie=film(),grid=Array.from({length:120},(_,i)=>i/10);
  const first=grid.map(t=>frameAt(movie,t));
  // Backwards, on a copy with no derived state yet.
  const copy=structuredClone(movie);
  for(const t of [...grid].reverse())assert.deepEqual(frameAt(copy,t),first[grid.indexOf(t)],`at ${t}`);
  // A, then B, then A.
  for(const [a,b] of [[1,10.1],[4.2,8.2],[11.9,0]])
    assert.deepEqual(frameAt(movie,a),(frameAt(movie,b),frameAt(movie,a)));
  for(const t of grid)assert.deepEqual(frameAt(movie,t),first[grid.indexOf(t)]);
});

test('no frame, outgoing frame or frame record carries a film-wide progress',()=>{
  const movie=film();
  for(const {index,request} of outputShotUnits(movie,10).units.flatMap(u=>u.frames)){
    assert.equal(Object.hasOwn(request,'progress'),false,`frame ${index}`);
    if(request.transition?.outgoing)assert.equal(Object.hasOwn(request.transition.outgoing,'progress'),false,`outgoing ${index}`);
  }
  for(const record of outputShotUnits(movie,10).units.flatMap(u=>u.frames))
    assert.deepEqual(Object.keys(record),['index','time','request']);
  assert.deepEqual(filmShots(movie).map(({shot})=>shot.id),['one','two','three','rise','rhythm','closing']);
});

test('checkFilm refuses by name a token not typed when spoken, a clip too short and an up along the view direction',()=>{
  assert.doesNotThrow(()=>checkFilm(film()));
  // "saw" of line 11 spoken at 0.6 s of shot two, before typing reaches it.
  const early=film(d=>{d.chapters[0].shots[1].cues[1].actions[0].words[0].at=.6;});
  assert.throws(()=>checkFilm(early),error=>['chapter drive','shot two','cues[1].actions[0]','words[0].token',"'saw'",'not yet typed'].every(w=>error.message.includes(w)),'untyped token');
  // The reel needs 0.5 + 1.8 s and half the 0.6 s fade after it: 2.6 s.
  const short=film();short.pictureMedia.clips.reel.end=2.5;
  assert.throws(()=>checkFilm(short),error=>['chapter tip','shot rhythm','cues[1].actions[0]','clip reel','2.60'].every(w=>error.message.includes(w)),'short clip');
  const enough=film();enough.pictureMedia.clips.reel.end=2.6;
  assert.doesNotThrow(()=>checkFilm(enough));
  // A move to a camera whose up lies along its view direction: refused at the
  // first output frame within half a degree of it, where the move ends.
  const along=film(d=>{d.chapters[1].shots[0].cues[3].actions[0].camera='along';});
  assert.throws(()=>checkFilm(along),/^Error: Camera up lies along the view direction in shot rise \(places\.stage\) at 7\.00 s$/);
});
