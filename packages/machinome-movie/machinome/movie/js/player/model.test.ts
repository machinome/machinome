// Layer 4: the player's pure parts (the player-page change, design D3 to
// D9): snapping to the film's frames, the stage request and the join-as-cut
// rule, the surface an address names, the ruler's geometry and the time under
// a pointer, the readout and the reload decision. The outline is the
// counter's as a session at --width 640 serves it (test/live.test.mjs and the
// pipeline tests hold the server to it); the frames are written in the shape
// frameAt gives. No DOM is used.
import {describe,expect,test} from 'vitest';
import {joinWords,readoutOf,reloadAction,routeOf,rulerOf,snap,stageRequest,surfacesOf,timeAt,
  type Frame,type Outline} from './model';

export const COUNT:Outline={id:'count',title:'Count',output:{width:640,height:360,fps:10,duration:11.4},
  chapters:[{id:'counting',start:0,end:11.4}],
  shots:[{id:'once',chapter:'counting',start:0,end:3.2,set:'frame',join:null},
    {id:'nine',chapter:'counting',start:3.2,end:5.3,set:'frame',join:null},
    {id:'carry',chapter:'counting',start:5.3,end:11.4,set:'split',join:{kind:'dissolve',duration:0.5}}],
  cues:[{shot:'carry',id:'cues[0]',at:5.3,until:null},{shot:'carry',id:'cues[1]',at:7.1,until:null},{shot:'carry',id:'cues[2]',at:9.9,until:10.9}],
  marks:[{name:'one',shot:'nine',at:3.2},{name:'nine',shot:'carry',at:5.3}],
  takes:{take:{kind:'clocked',duration:8,marks:[{name:'one',time:2},{name:'nine',time:6},{name:'ten',time:8}],url:'/take.json'}},
  speech:{mix:false,captions:false},stage:{sha256:'a'.repeat(64)},viewer:{api:29},
  generation:{number:1,loadedAt:'2026-10-04T12:00:00.000Z'},refusal:null};
const MOVIE={kind:'movie'} as const,TAKE={kind:'take',key:'take'} as const;

const frame=(shotId:string,time:number,transition:Frame['transition']=null):Frame=>
  ({time,chapterId:'counting',shotId,set:'frame',slots:{stage:`counting.${shotId}`},elements:{[`counting.${shotId}`]:{kind:'view'}},transition});

describe('snapping',()=>{
  test('video time snaps to the film\'s frames, its last frame before the end',()=>{
    const grid={fps:10,duration:11.4,end:'exclusive'} as const;
    expect(snap(0,grid)).toEqual({index:0,time:0,count:114});
    expect(snap(3.24,grid)).toEqual({index:32,time:3.2,count:114});
    expect(snap(6.06,grid).index).toBe(61);
    expect(snap(-1,grid)).toEqual({index:0,time:0,count:114});
    expect(snap(11.4,grid)).toEqual({index:113,time:11.3,count:114});
    expect(snap(99,grid).index).toBe(113);
  });
  test('take time snaps to the same frames, the take\'s end included, never past it',()=>{
    expect(snap(8,{fps:10,duration:8,end:'inclusive'})).toEqual({index:80,time:8,count:81});
    expect(snap(9,{fps:10,duration:8,end:'inclusive'}).time).toBe(8);
    // A length off the grid: its last frame is the length itself.
    expect(snap(8.04,{fps:10,duration:8.05,end:'inclusive'})).toEqual({index:80,time:8,count:82});
    expect(snap(8.06,{fps:10,duration:8.05,end:'inclusive'})).toEqual({index:81,time:8.05,count:82});
  });
  test('a time that is not a number is refused, naming it',()=>{
    expect(()=>snap(Number.NaN,{fps:10,duration:1,end:'exclusive'})).toThrow(/not a time/);
  });
});

describe('the stage request',()=>{
  test('a plain frame is posed without its transition',()=>{
    const f=frame('nine',4);
    const {request,shown,posed}=stageRequest(f);
    expect(request).toEqual({...f,transition:undefined});
    expect(Object.hasOwn(request,'transition')).toBe(false);
    expect([shown,posed]).toEqual([null,'nine']);
  });
  test('a reframe is posed live, with its progress and boxes, as the renderer poses it',()=>{
    const boxes={'opening.wide':[0,0,.5,1]};
    const f=frame('question',2.8,{field:'transition',kind:'reframe',shotId:'question',duration:0.8,ease:'smooth',outgoingShotId:'hook',
      start:2.4333333333333331,progress:.4,outgoing:null,boxes});
    const {request,shown,posed}=stageRequest(f);
    expect(request.transition).toEqual({kind:'reframe',progress:.4,boxes});
    expect(posed).toBe('question');
    expect(shown).toEqual({field:'transition',kind:'reframe',into:'question',duration:0.8,shown:'live'});
    expect(joinWords(shown)).toBe('reframe into question, 0.8 s: drawn live');
  });
  for(const kind of ['dissolve','wipe','slide'])
    test(`a ${kind} poses the outgoing frame before its midpoint and the incoming from it on`,()=>{
      const outgoing=frame('nine',5.5);
      const join=(time:number)=>frame('carry',time,{field:'transition',kind,shotId:'carry',duration:0.5,ease:'smooth',outgoingShotId:'nine',
        start:5.3,progress:(time-5.3)/0.5,outgoing:{...outgoing,time}});
      const before=stageRequest(join(5.5)),at=stageRequest(join(5.55)),after=stageRequest(join(5.6));
      expect(before.posed).toBe('nine');
      expect(before.request).toEqual({...outgoing,time:5.5,transition:undefined});
      expect(Object.hasOwn(before.request,'transition')).toBe(false);
      expect([at.posed,after.posed]).toEqual(['carry','carry']);
      expect(Object.hasOwn(after.request,'transition')).toBe(false);
      expect(after.shown).toEqual({field:'transition',kind,into:'carry',duration:0.5,shown:'cut'});
      expect(joinWords(before.shown)).toBe(`${kind} into carry, 0.5 s: shown as a cut at its midpoint`);
    });
  test('a fade between shots poses the outgoing picture through its first half, then the incoming',()=>{
    const outgoing=frame('nine',5.4);
    const first=stageRequest(frame('carry',5.4,{field:'transition',kind:'fade',shotId:'carry',duration:0.5,ease:'smooth',outgoingShotId:'nine',
      start:5.3,color:'#000000',plate:.6,picture:'outgoing',outgoing}));
    const second=stageRequest(frame('carry',5.6,{field:'transition',kind:'fade',shotId:'carry',duration:0.5,ease:'smooth',outgoingShotId:'nine',
      start:5.3,color:'#000000',plate:.4,picture:'incoming',outgoing:null}));
    expect([first.posed,second.posed]).toEqual(['nine','carry']);
    expect(joinWords(first.shown)).toBe('fade into carry, 0.5 s: shown as a cut at its midpoint');
  });
  test('a shot\'s fade in or out is posed without its plate, and said so',()=>{
    const f=frame('hook',0.5,{field:'fadeIn',kind:'fade',shotId:'hook',duration:1,ease:'smooth',color:'#faf7ef',plate:.5,picture:'incoming',outgoing:null});
    const {request,shown,posed}=stageRequest(f);
    expect(Object.hasOwn(request,'transition')).toBe(false);
    expect(posed).toBe('hook');
    expect(joinWords(shown)).toBe('fade in, 1 s: shown without its fade');
    const out=stageRequest(frame('invitation',18,{field:'fadeOut',kind:'fade',shotId:'invitation',duration:1.2,ease:'smooth',color:'#faf7ef',plate:.3,picture:'incoming',outgoing:null}));
    expect(joinWords(out.shown)).toBe('fade out, 1.2 s: shown without its fade');
  });
});

describe('the surface an address names',()=>{
  test('#movie, #take/<key>, and the movie by default, the address corrected',()=>{
    expect(routeOf('#movie',COUNT)).toEqual({surface:MOVIE,hash:'#movie',known:true});
    expect(routeOf('#take/take',COUNT)).toEqual({surface:TAKE,hash:'#take/take',known:true});
    for(const hash of ['','#','#take/loop','#nothing'])expect(routeOf(hash,COUNT)).toEqual({surface:MOVIE,hash:'#movie',known:false});
    expect(surfacesOf(COUNT)).toEqual([{hash:'#movie',label:'Movie',surface:MOVIE},{hash:'#take/take',label:'Take',surface:TAKE}]);
    const loop={...COUNT,takes:{loop:{kind:'loop' as const,duration:20,marks:[]}}};
    expect(surfacesOf(loop).map(s=>s.hash)).toEqual(['#movie','#take/loop']);
    expect(surfacesOf(loop)[1].label).toBe('Loop');
  });
});

describe('the ruler',()=>{
  test('the counter\'s ruler: a band, three segments, a hatched dissolve, three ticks, two flags',()=>{
    const r=rulerOf(COUNT,MOVIE);
    expect(r.duration).toBe(11.4);
    expect(r.bands).toEqual([{id:'counting',from:0,to:1}]);
    expect(r.segments.map(s=>[s.id,s.start,+s.from.toFixed(6),+s.to.toFixed(6)])).toEqual([['once',0,0,0.280702],['nine',3.2,0.280702,0.464912],['carry',5.3,0.464912,1]]);
    expect(r.joins.map(j=>[j.shot,j.kind,+j.from.toFixed(6),+j.to.toFixed(6)])).toEqual([['carry','dissolve',0.464912,0.508772]]);
    expect(r.ticks.map(t=>[t.id,t.at])).toEqual([['cues[0]',5.3],['cues[1]',7.1],['cues[2]',9.9]]);
    expect(r.flags.map(f=>[f.name,f.at])).toEqual([['one',3.2],['nine',5.3]]);
  });
  test('the take\'s ruler has its marks only, in take seconds',()=>{
    const r=rulerOf(COUNT,TAKE);
    expect([r.duration,r.bands,r.segments,r.joins,r.ticks]).toEqual([8,[],[],[],[]]);
    expect(r.flags.map(f=>[f.name,f.at,f.x])).toEqual([['one',2,.25],['nine',6,.75],['ten',8,1]]);
  });
  test('the time under a pointer is its fraction of the ruler, clamped',()=>{
    const r=rulerOf(COUNT,MOVIE);
    expect(timeAt(0.5,r)).toBeCloseTo(5.7,9);
    expect([timeAt(-0.2,r),timeAt(1.3,r)]).toEqual([0,11.4]);
  });
});

describe('the readout',()=>{
  test('at the mark one: the time, the frame, the shot, the chapter and the mark',()=>{
    const r=readoutOf({outline:COUNT,surface:MOVIE,time:3.2,shown:null,captions:null});
    expect(r).toEqual({time:'3.20 s',frame:32,count:114,shot:'nine',chapter:'counting',mark:'one',join:null,caption:null});
  });
  test('inside the dissolve, the join; with captions, the one that holds the time',()=>{
    const shown={field:'transition',kind:'dissolve',into:'carry',duration:0.5,shown:'cut'} as const;
    const captions=[{text:'One turn.',start:1,end:2.5},{text:'Nine.',start:5,end:6}];
    const r=readoutOf({outline:COUNT,surface:MOVIE,time:5.4,shown,captions});
    expect([r.shot,r.mark,r.join,r.caption]).toEqual(['carry',null,'dissolve into carry, 0.5 s: shown as a cut at its midpoint','Nine.']);
    expect(readoutOf({outline:COUNT,surface:MOVIE,time:2,shown:null,captions}).caption).toBe('One turn.');
    expect(readoutOf({outline:COUNT,surface:MOVIE,time:2.5,shown:null,captions}).caption).toBeNull();
  });
  test('on the take surface: the time posed, its nearest frame and the mark, no shot or chapter',()=>{
    const r=readoutOf({outline:COUNT,surface:TAKE,time:6,shown:null,captions:null});
    expect(r).toEqual({time:'6.00 s',frame:60,count:81,shot:null,chapter:null,mark:'nine',join:null,caption:null});
    expect(readoutOf({outline:COUNT,surface:TAKE,time:6.06,shown:null,captions:null}).mark).toBeNull();
  });
});

describe('the reload decision',()=>{
  const held={number:2,stageSha256:'a'.repeat(64)};
  const event=(number:number,stageSha256:string,exportChanged:boolean)=>({number,loadedAt:'',stageSha256,exportChanged});
  test('the generation held does nothing',()=>{
    expect(reloadAction('movie',held,event(2,'a'.repeat(64),false))).toBe('none');
    expect(reloadAction('take',held,event(1,'b'.repeat(64),true))).toBe('none');
  });
  test('the movie surface keeps its stage page while its hash and the export hold, and reloads it otherwise',()=>{
    expect(reloadAction('movie',held,event(3,'a'.repeat(64),false))).toBe('pose-again');
    expect(reloadAction('movie',held,event(3,'b'.repeat(64),false))).toBe('reload-stage');
    expect(reloadAction('movie',held,event(3,'a'.repeat(64),true))).toBe('reload-stage');
  });
  test('the take surface remounts only when the export changed',()=>{
    expect(reloadAction('take',held,event(3,'b'.repeat(64),false))).toBe('reattach');
    expect(reloadAction('take',held,event(3,'a'.repeat(64),true))).toBe('remount');
  });
  test('a generation skipped is a change',()=>{
    expect(reloadAction('movie',held,event(4,'a'.repeat(64),false))).toBe('reload-stage');
    expect(reloadAction('take',held,event(4,'a'.repeat(64),false))).toBe('remount');
  });
});
