// Layer 4: the stage's components under jsdom. Structure, not pixels: a set
// renders its slots and its chrome, an element draws its state, the registry
// refuses what it does not draw by name, and components hold no state
// between frames.
import {flushSync} from 'react-dom';
import {createRoot,type Root} from 'react-dom/client';
import {afterEach,beforeAll,describe,expect,test} from 'vitest';
import {Stage,type ReportSource,type StageContextValue} from './components';
import {Chrome,Slot,defineElement,defineSet,useMovie,useReport} from './index';
import {checkRegistry,registerSet} from './registry';
import {leaseViews,measureElement,reframeHost} from './runtime';
import {SHIPPED_SLOTS,markSource,registerShipped} from './shipped';
import type {ElementComponentProps,MovieInfo,ProjectElementState,SetComponentProps,StageConfig,StageFrame} from './types';

// The test's own movie types, as a generated movie.d.ts would declare them.
declare module './types' {
  interface MovieElements {card:{props:{items:string[]};actions:{action:'light';params:{item:string}}}}
}

const movie:MovieInfo={id:'tour',title:'Tour',series:'SERIES FROM THE DOCUMENT',
  style:{background:'#faf7ef',foreground:'#222222',accent:'#237c86',fontFamily:'DejaVu Sans, sans-serif',safeInsetFraction:.08}};

// A project's set with chrome, one without, and a project element that reports.
function Bill({movie,props}:SetComponentProps){
  return (
    <div className="bill">
      <Chrome><div className="bill-series">{String(props.series)}</div><div className="bill-title">{movie.title}</div></Chrome>
      <Slot name="stage"/><Slot name="aside" className="bill-aside"/>
    </div>
  );
}
function Bare(){return <><Slot name="left"/><Slot name="right"/></>;}
function Card({state}:ElementComponentProps<ProjectElementState<{items:string[]},{action:'light';params:{item:string}}>>){
  const lit=state.actions.find(a=>a.action==='light');
  useReport({lines:state.props.items.length,lit:lit?.params.item??null});
  const {title}=useMovie();
  return <ul data-movie={title}>{state.props.items.map(item=><li key={item} className={item===lit?.params.item?'lit':''}>{item}</li>)}</ul>;
}

beforeAll(()=>{
  registerShipped();
  defineSet({kind:'bill',slots:['stage','aside'],component:Bill});
  defineSet({kind:'bare',slots:['left','right'],component:Bare});
  defineElement({kind:'card',component:Card});
});

const config:Pick<StageConfig,'stage'|'media'>={
  stage:{sets:{bill:{slots:['aside','stage'],props:{series:'SERIES FROM THE DOCUMENT'}},bare:{slots:['left','right']},
    frame:{slots:['stage']},paper:{slots:[...SHIPPED_SLOTS.paper],props:{brand:'BRAND FROM PROPS',series:'SERIES FROM PROPS'}},
    'paper-split':{slots:[...SHIPPED_SLOTS['paper-split']]}},elements:['card','view','source','title','picture']},
  media:{stills:{plate:{width:800,height:600}},clips:{spin:{width:640,height:360}}},
};

let root:Root|null=null;
function mount(){
  document.body.innerHTML='<div id="stage-root"></div><div id="transition"></div><div id="chrome"></div>';
  const caught:unknown[]=[];
  root=createRoot(document.getElementById('stage-root') as HTMLElement,{onUncaughtError:e=>{caught.push(e);}});
  const draw=(frame:StageFrame)=>{
    const reports=new Map<string,ReportSource>(),errors:Error[]=[];
    const stage:StageContextValue={frame,config,chromeLayer:document.getElementById('chrome'),reports,fail:e=>{errors.push(e);}};
    caught.length=0;
    flushSync(()=>(root as Root).render(<Stage movie={movie} stage={stage}/>));
    return {reports,errors,caught:[...caught]};
  };
  return draw;
}
afterEach(()=>{root?.unmount();root=null;document.body.innerHTML='';});

const frameOf=(set:string,slots:Record<string,string>,elements:StageFrame['elements']):StageFrame=>
  ({time:1,chapterId:'c',shotId:'s1',set,slots,elements,transition:null});
const view={kind:'view' as const,time:.5,view:{camera:[0,-500,100] as [number,number,number],target:[0,0,50] as [number,number,number]},
  up:[0,0,1] as [number,number,number],fov:30,hidden:[],highlight:null,marks:[]};
const source={kind:'source' as const,file:'models/seesaw.py',firstLine:22,lastLine:24,
  text:"base = Block(name='Base')\nstand = Stand()",
  html:"base = <span class=\"hljs-title\">Block</span>(name=<span class=\"hljs-string\">'Base'</span>)\nstand = Stand()",
  cursor:true,emphasis:[{token:'Block',start:7,end:12},{token:'Stand',start:34,end:39}]};
const chrome=()=>document.getElementById('chrome') as HTMLElement;
const stageRoot=()=>document.getElementById('stage-root') as HTMLElement;
const element=(key:string)=>stageRoot().querySelector(`[data-element="${key}"]`) as HTMLElement;

describe('sets',()=>{
  test('a project set renders its slots, the placed element in its box, and its chrome in #chrome',()=>{
    const draw=mount();
    draw(frameOf('bill',{stage:'a.mill'},{'a.mill':view}));
    const slots=[...stageRoot().querySelectorAll<HTMLElement>('.vm-slot')].map(s=>s.dataset.slot);
    expect(slots).toEqual(['stage','aside']);
    expect(stageRoot().querySelector('.vm-set')?.getAttribute('data-set')).toBe('bill');
    const box=stageRoot().querySelector('.vm-slot-stage > .vm-element.vm-element-view');
    expect(box?.getAttribute('data-element')).toBe('a.mill');
    expect(stageRoot().querySelector('.vm-slot-aside')?.children.length).toBe(0);
    expect(stageRoot().querySelector('.vm-slot-aside')?.className).toBe('vm-slot vm-slot-aside bill-aside');
    expect(chrome().querySelector('.bill-series')?.textContent).toBe('SERIES FROM THE DOCUMENT');
    expect(chrome().querySelector('.bill-title')?.textContent).toBe('Tour');
    expect(stageRoot().querySelector('.bill-series')).toBeNull();
  });
  test('a set with no Chrome draws no chrome',()=>{
    const draw=mount();
    draw(frameOf('bare',{left:'a.code'},{'a.code':source}));
    expect(chrome().children.length).toBe(0);
    draw(frameOf('frame',{stage:'a.mill'},{'a.mill':view}));
    expect(chrome().children.length).toBe(0);
    expect(stageRoot().querySelector('.vm-slot-stage [data-element="a.mill"]')).not.toBeNull();
  });
  test('the paper sets draw their masthead from props only, and every indexed slot',()=>{
    const draw=mount();
    draw(frameOf('paper',{stage:'a.mill','top-2':'a.t'},{'a.mill':view,'a.t':{kind:'title',shown:true,text:'Hello',opacity:1}}));
    expect(chrome().querySelector('.vm-paper-brand')?.textContent).toBe('BRAND FROM PROPS');
    expect(chrome().querySelector('.vm-paper-series')?.textContent).toBe('SERIES FROM PROPS');
    const slots=[...stageRoot().querySelectorAll<HTMLElement>('.vm-slot')].map(s=>s.dataset.slot);
    expect([...slots].sort()).toEqual([...SHIPPED_SLOTS.paper].sort());
    expect(stageRoot().querySelector('.vm-slot-top-2 .vm-title')?.textContent).toBe('Hello');
    expect(stageRoot().querySelector('.vm-slot-top-2')?.classList.contains('vm-paper-top')).toBe(true);
    draw(frameOf('paper-split',{left:'a.code',right:'a.mill'},{'a.code':source,'a.mill':view}));
    expect(chrome().children.length).toBe(0);
    expect(stageRoot().querySelector('.vm-set-paper-split .vm-slot-left [data-element="a.code"]')).not.toBeNull();
  });
});

describe('elements',()=>{
  test('a source panel draws its header, markup, lit tokens and cursor',()=>{
    const draw=mount();
    const {errors}=draw(frameOf('bare',{left:'a.code'},{'a.code':source}));
    expect(errors).toEqual([]);
    const box=element('a.code');
    expect(box.querySelector('.vm-source-file')?.textContent).toBe('models/seesaw.py · L22–24');
    expect(box.querySelector('code')?.textContent).toBe(source.text);
    expect(box.querySelector('code .hljs-string')?.textContent).toBe("'Base'");
    const marks=[...box.querySelectorAll<HTMLElement>('mark.spoken')].map(m=>[m.dataset.token,m.textContent]);
    expect(marks).toEqual([['Block','Block'],['Stand','Stand']]);
    expect((box.querySelector('.vm-source-cursor') as HTMLElement).style.visibility).toBe('visible');
    const report=measureElement(box,source);
    expect(report).toMatchObject({kind:'source',text:source.text,emphasis:[{token:'Block',text:'Block'},{token:'Stand',text:'Stand'}],cursor:true});
    draw(frameOf('bare',{left:'a.code'},{'a.code':{...source,cursor:false,emphasis:[]}}));
    expect(box.querySelectorAll('mark').length).toBe(0);
    expect((element('a.code').querySelector('.vm-source-cursor') as HTMLElement).style.visibility).toBe('hidden');
  });
  test('a source panel refuses an emphasis range whose text is not its token, naming the token and element',()=>{
    const draw=mount();
    const {errors}=draw(frameOf('bare',{left:'a.code'},{'a.code':{...source,emphasis:[{token:'Stand',start:7,end:12}]}}));
    expect(errors.map(String).join()).toMatch(/a\.code.*s1.*Stand/);
    expect(()=>markSource(document.createElement('code'),{text:'x',emphasis:[{token:'x',start:0,end:1}]}))
      .toThrow(/differs from the typed text/);
  });
  test('a title draws its words, reveals as many as the state says, and fades by opacity',()=>{
    const draw=mount();
    const words=[{text:'Up.',word:true,start:0,end:3},{text:' ',word:false,start:3,end:4},{text:'Down.',word:true,start:4,end:9}];
    draw(frameOf('paper',{center:'a.beat'},{'a.beat':{kind:'title',shown:true,text:'Up. Down.',words,revealed:1,opacity:.4}}));
    const title=element('a.beat').querySelector('.vm-title') as HTMLElement;
    expect(title.textContent).toBe('Up. Down.');
    expect([...title.querySelectorAll<HTMLElement>('.vm-reveal-word')].map(w=>w.style.visibility)).toEqual(['','hidden']);
    expect(title.style.opacity).toBe('0.4');
    expect(measureElement(element('a.beat'),{kind:'title'})).toMatchObject({kind:'title',revealed:1});
    draw(frameOf('paper',{title:'a.t'},{'a.t':{kind:'title',shown:true,text:'SEESAW',subtitle:'One beam, one stand',opacity:1}}));
    expect(element('a.t').querySelector('.vm-title-subtitle')?.textContent).toBe('One beam, one stand');
    expect((element('a.t').querySelector('.vm-title') as HTMLElement).style.opacity).toBe('');
    expect(measureElement(element('a.t'),{kind:'title'})).toMatchObject({revealed:null});
    draw(frameOf('paper',{title:'a.t'},{'a.t':{kind:'title',shown:false,text:'SEESAW',opacity:0}}));
    expect(element('a.t').querySelector('.vm-title')).toBeNull();
    expect(measureElement(element('a.t'),{kind:'title'})).toEqual({kind:'title',text:null,revealed:null});
  });
  test('a picture draws a plate and its image, placed by CSS variables over its box',()=>{
    const draw=mount();
    draw(frameOf('paper',{plate:'a.plate'},{'a.plate':{kind:'picture',shown:true,media:'still',name:'plate',fit:'cover',opacity:1,
      view:{center:[.5,.42],zoom:1.4}}}));
    const box=element('a.plate');
    expect(box.classList.contains('vm-element-picture')).toBe(true);
    expect(box.querySelector('.vm-picture-plate')).not.toBeNull();
    const img=box.querySelector('img') as HTMLImageElement;
    expect(img.getAttribute('src')).toBe('/pictures/stills/plate');
    expect(img.dataset.fit).toBe('cover');
    expect(['--vm-picture-aspect','--vm-picture-zoom','--vm-picture-cx','--vm-picture-cy'].map(p=>img.style.getPropertyValue(p)))
      .toEqual([String(800/600),'1.4','0.5','0.42']);
    draw(frameOf('paper',{full:'a.clip'},{'a.clip':{kind:'picture',shown:true,media:'clip',name:'spin',fit:'contain',opacity:.5,
      view:{center:[.5,.5],zoom:1},frame:12,clipSeconds:.4}}));
    const clip=element('a.clip');
    expect(clip.querySelector('img')?.getAttribute('src')).toBe('/pictures/clips/spin/000012.png');
    expect((clip.querySelector('.vm-picture') as HTMLElement).style.opacity).toBe('0.5');
    expect(measureElement(clip,{kind:'picture',media:'clip'} as never)).toMatchObject({kind:'picture',shown:true,frame:12});
    draw(frameOf('paper',{full:'a.clip'},{'a.clip':{kind:'picture',shown:false,media:'clip',name:'spin',fit:'contain',opacity:0,
      view:{center:[.5,.5],zoom:1},frame:12}}));
    expect(element('a.clip').children.length).toBe(0);
  });
  test('a picture whose size the config does not give is refused naming the element',()=>{
    const draw=mount();
    const {caught}=draw(frameOf('paper',{plate:'a.p'},{'a.p':{kind:'picture',shown:true,media:'still',name:'missing',fit:'contain',opacity:1,
      view:{center:[.5,.5],zoom:1}}}));
    expect(String(caught[0])).toMatch(/a\.p.*s1.*still missing/);
  });
  test('a project element receives its state and reports through useReport',()=>{
    const draw=mount();
    const card={kind:'card',props:{items:['Balance','Tip']},actions:[{action:'light',params:{item:'Tip'},since:1.2,until:3.4,progress:.25}]};
    const {reports}=draw(frameOf('bill',{aside:'a.card'},{'a.card':card}));
    const box=element('a.card');
    expect(box.className).toBe('vm-element vm-element-card');
    expect([...box.querySelectorAll('li')].map(li=>[li.textContent,li.className])).toEqual([['Balance',''],['Tip','lit']]);
    expect(box.querySelector('ul')?.dataset.movie).toBe('Tour');
    expect(reports.get('a.card')).toEqual({lines:2,lit:'Tip'});
  });
});

describe('registry',()=>{
  test('refuses a set kind the document uses and no module registers, by name',()=>{
    expect(()=>checkRegistry({stage:{sets:{playbill:{slots:['stage']}}}})).toThrow(/Set kind playbill is not registered/);
  });
  test('refuses an element kind the document uses and no module registers, by name',()=>{
    expect(()=>checkRegistry({stage:{sets:{},elements:['view','tally']}})).toThrow(/Element kind tally is not registered/);
  });
  test('refuses a set whose registered slots differ from the document, by name',()=>{
    expect(()=>checkRegistry({stage:{sets:{bill:{slots:['stage','aside','plate']}}}})).toThrow(/Set kind bill registers slots aside, stage but the document declares aside, plate, stage/);
    expect(()=>checkRegistry({stage:{sets:{frame:{slots:['left']}}}})).toThrow(/Set kind frame/);
    expect(()=>checkRegistry(config)).not.toThrow();
  });
  test('refuses a kind registered twice, by name, a shipped kind included',()=>{
    expect(()=>defineSet({kind:'bill',slots:['stage','aside'],component:Bill})).toThrow('Set kind bill is registered twice');
    expect(()=>defineSet({kind:'frame',slots:['stage'],component:Bare})).toThrow('Set kind frame is registered twice');
    expect(()=>defineElement({kind:'card',component:Card})).toThrow('Element kind card is registered twice');
    expect(()=>defineElement({kind:'view',component:Card as never})).toThrow('Element kind view is registered twice');
    expect(()=>registerSet('Bad Kind',['a'],Bare)).toThrow(/"Bad Kind" is not a kind name/);
  });
  test('refuses, while drawing, a set kind not registered and an element kind not registered, by name',()=>{
    const draw=mount();
    expect(String(draw(frameOf('nowhere',{},{})).caught[0])).toMatch(/Set kind nowhere of shot s1 is not registered/);
    expect(String(draw(frameOf('bill',{stage:'a.x'},{'a.x':{kind:'gizmo',props:{},actions:[]}})).caught[0]))
      .toMatch(/Element kind gizmo of element a\.x is not registered/);
  });
});

describe('viewer lease',()=>{
  // leaseViews(instances, placed): for each placed view, the index of the
  // instance it is drawn on, or -1 when one must mount (ADR-007).
  const free=(lens:string|null=null)=>({key:null,lens});
  const held=(key:string,lens:string|null=null)=>({key,lens});
  const at=(key:string,lens='L')=>({key,lens});
  test('a placed view keeps its instance; a view without one takes the lowest free; one mounts only when none is free',()=>{
    expect(leaseViews([held('a')],[at('a')])).toEqual([0]);
    expect(leaseViews([held('x'),free(),held('y')],[at('b')])).toEqual([0]);
    expect(leaseViews([held('b'),held('a')],[at('a'),at('b')])).toEqual([1,0]);
    expect(leaseViews([held('a')],[at('a'),at('b')])).toEqual([0,-1]);
    expect(leaseViews([held('a')],[at('b')])).toEqual([0]);
    expect(leaseViews([],[at('a')])).toEqual([-1]);
    expect(leaseViews([held('a'),held('b')],[])).toEqual([]);
  });
  test('below API 28 an instance is leased only to the lens it mounted with',()=>{
    expect(leaseViews([free('37')],[at('b','42')])).toEqual([-1]);
    expect(leaseViews([free('42'),free('37')],[at('b','37')])).toEqual([1]);
    expect(leaseViews([held('a','37')],[at('a','37'),at('b','37')])).toEqual([0,-1]);
    expect(leaseViews([free(null)],[at('b','42')])).toEqual([0]);
  });
  test('no sequence of frames mounts more instances than one frame places views, and a placed view keeps its instance',()=>{
    const frames:{key:string;lens:string}[][]=[[at('A')],[at('B')],[at('A'),at('B')],[]];
    const sequences=(n:number):number[][]=>n===0?[[]]:sequences(n-1).flatMap(s=>frames.map((_,i)=>[...s,i]));
    let checked=0;
    for(const sequence of sequences(5)){
      const instances:{key:string|null;lens:string|null}[]=[];
      let most=0,before:Record<string,number>={};
      for(const i of sequence){
        const placed=frames[i],chosen=leaseViews(instances,placed);
        const given=chosen.map((c,n)=>c>=0?c:instances.push({key:placed[n].key,lens:null})-1);
        expect(new Set(given).size).toBe(placed.length);
        instances.forEach((instance,n)=>{instance.key=placed[given.indexOf(n)]?.key??null;});
        for(const [n,{key}] of placed.entries())if(key in before)expect(given[n]).toBe(before[key]);
        before=Object.fromEntries(placed.map(({key},n)=>[key,given[n]]));
        most=Math.max(most,placed.length);
        expect(instances.length).toBeLessThanOrEqual(most);
        checked++;
      }
    }
    expect(checked).toBe(4**5*5);
  });
});

describe('reframe',()=>{
  // A frame of a reframe (ADR-010): the incoming set drawn as for any frame,
  // every element but the moving views at the progress as opacity, and the
  // moving view's host over the frame's box (the runtime's reframeHost).
  const card={kind:'card',props:{items:['Balance','Tip']},actions:[]};
  const reframe=(progress:number)=>({...frameOf('bill',{stage:'a.mill',aside:'a.card'},{'a.mill':view,'a.card':card}),
    transition:{kind:'reframe',progress,boxes:{'a.mill':[.25,.1,.5,.8]}}});
  test('every element but the moving views is drawn at the progress as opacity, and none at its end or without one',()=>{
    const draw=mount();
    draw(reframe(.4));
    expect(element('a.card').style.opacity).toBe('0.4');
    expect(element('a.mill').style.opacity).toBe('');
    draw(reframe(0));
    expect(element('a.card').style.opacity).toBe('0');
    // React leaves an emptied style attribute behind; the runtime removes it
    // after each commit, so the page's content is the frame's alone.
    draw(reframe(1));
    expect(element('a.card').style.opacity).toBe('');
    draw(frameOf('bill',{stage:'a.mill',aside:'a.card'},{'a.mill':view,'a.card':card}));
    expect(element('a.card').style.opacity).toBe('');
    // The slots keep the boxes the set gives them.
    expect(stageRoot().querySelector('.vm-slot-stage')?.getAttribute('style')).toBeNull();
  });
  test('the moving host\'s inline box is the frame\'s, in pixels of the page, to the layout\'s 1/64 pixel, relative to its element',()=>{
    const page={width:1280,height:720},inSlot={x:640,y:72,width:512,height:576};
    expect(reframeHost(inSlot,page,[.25,.1,.5,.8])).toEqual({left:'-320px',top:'0px',width:'640px',height:'576px',right:'auto',bottom:'auto'});
    // 0.27 of 1280 is 345.6, which the layout holds as 22118/64 pixels.
    expect(reframeHost({x:0,y:0,width:1,height:1},page,[.27,.17,.56,.74]))
      .toEqual({left:`${22118/64}px`,top:`${7834/64}px`,width:`${45875/64}px`,height:`${34099/64}px`,right:'auto',bottom:'auto'});
    expect(reframeHost(inSlot,page,null)).toEqual({left:'',top:'',width:'',height:'',right:'',bottom:''});
    const host=document.createElement('div');
    Object.assign(host.style,reframeHost(inSlot,page,[.25,.1,.5,.8]));
    expect([host.style.left,host.style.width,host.style.right]).toEqual(['-320px','640px','auto']);
    Object.assign(host.style,reframeHost(inSlot,page,null));
    expect(host.getAttribute('style')).toBe('');
  });
});

describe('purity',()=>{
  test('drawing frame A, then B, then A gives identical DOM',()=>{
    const draw=mount();
    const card={kind:'card',props:{items:['Balance','Tip']},actions:[]};
    const A=frameOf('bill',{stage:'a.code',aside:'a.card'},{'a.code':source,'a.card':card});
    const B=frameOf('paper',{stage:'a.mill',title:'a.t',plate:'a.p'},{'a.mill':view,'a.t':{kind:'title',shown:true,text:'SEESAW',opacity:.5},
      'a.p':{kind:'picture',shown:true,media:'still',name:'plate',fit:'contain',opacity:1,view:{center:[.5,.5],zoom:1}}});
    const snapshot=()=>stageRoot().innerHTML+'|'+chrome().innerHTML;
    draw(A);const a=snapshot();
    draw(B);const b=snapshot();
    draw(A);
    expect(snapshot()).toBe(a);
    expect(b).not.toBe(a);
    draw(B);
    expect(snapshot()).toBe(b);
  });
});
