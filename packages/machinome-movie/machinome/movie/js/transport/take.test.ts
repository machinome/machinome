// Layer 4: the take transport on a recording fake of the viewer's handle
// (the take-transport change; ADR-020). A machine transport refuses a viewer
// that gives no machine or another machine before it touches the viewer,
// and poses a bank by a restore and one camera call; a take transport seeks
// the fixture counter's take by the pose rule of src/take.mjs, so a mark
// poses its recorded bank; a loop transport seeks by the loop's time. The
// fake records what changes the viewer (restore, setView, setTime), never
// what only reads it. No DOM is used.
import {describe,expect,test} from 'vitest';
import {attachLoop,attachMachine,attachTake} from './take';
import type {Bank,ViewerInstance} from './viewer-handle';
import {bankAt,type TakeDocument} from '../src/take.mjs';
import counter from '../fixtures/documents/count.json';

const count=counter as unknown as TakeDocument;
const IDENTITY=count.take.identity;
type Call=[string,...unknown[]];
// A viewer of the given API whose machine, unless `identity` is null, has
// that identity; `method: false` is a viewer without machine() at all.
function fake({api=29,identity=IDENTITY as string|null,method=true}={}){
  const calls:Call[]=[];
  let bank:Bank={};
  let view={camera:[160,-260,140],target:[0,0,20],up:[0,0,1],fov:37};
  const vec=(a:number[])=>({toArray:()=>[...a]});
  const machine=identity===null?null:{
    identity:()=>identity,
    state:()=>({...bank}),
    restore:(snapshot:{identity:string;bank:Bank})=>{calls.push(['restore',snapshot]);bank={...snapshot.bank};},
  };
  const viewer={apiVersion:api,setVisible(){calls.push(['setVisible']);},navigation:()=>({}),
    setTime:(t:number)=>{calls.push(['setTime',t]);},
    setView:(v:{camera:number[];target:number[];up?:number[];fov?:number})=>{calls.push(['setView',v]);
      view={...view,camera:v.camera,target:v.target,...(v.up?{up:v.up}:{}),...(v.fov!==undefined?{fov:v.fov}:{})};},
    view:()=>({camera:vec(view.camera),target:vec(view.target),up:vec(view.up),fov:view.fov}),
    partOnScreen:()=>null,project:()=>null,highlight:()=>()=>{},
    ...(method?{machine:()=>machine}:{})} as unknown as ViewerInstance;
  return {viewer,calls,holds:()=>({...bank})};
}
const camera={camera:[400,-600,300] as [number,number,number],target:[0,0,50] as [number,number,number],
  up:[0,1,0] as [number,number,number],fov:30};

describe('a machine transport',()=>{
  test('refuses a viewer that gives no machine, by name, before touching it',()=>{
    for(const given of [fake({identity:null}),fake({api:28,method:false})]){
      expect(()=>attachMachine(given.viewer,IDENTITY)).toThrow(
        'the viewer gives no machine for this clocked document; a view on a take is posed through viewer.machine(), from Viewer API 29');
      expect(given.calls).toEqual([]);
    }
  });
  test('refuses another machine, naming both identities and take.identity, before touching it',()=>{
    const given=fake({identity:'another-machine'});
    expect(()=>attachMachine(given.viewer,IDENTITY)).toThrow(
      `the viewer's machine is another-machine, and the take was recorded on ${IDENTITY} (take.identity)`);
    expect(given.calls).toEqual([]);
  });
  test('refuses to attach without a take identity, by name',()=>{
    for(const identity of ['',undefined,null]){
      const given=fake();
      expect(()=>attachMachine(given.viewer,identity as unknown as string)).toThrow(/^no take identity was given \(take\.identity\)/);
      expect(given.calls).toEqual([]);
    }
  });
  test('poses a copy of the bank with the take\'s identity, then the camera given, with up and field of view',()=>{
    const {viewer,calls,holds}=fake(),machine=attachMachine(viewer,IDENTITY);
    expect(machine.identity).toBe(IDENTITY);
    expect(calls).toEqual([]);
    const bank={crank:1800,tens:0,units:5};
    machine.pose(bank,camera);
    expect(calls).toEqual([['restore',{identity:IDENTITY,bank}],['setView',camera]]);
    expect((calls[0][1] as {bank:Bank}).bank).not.toBe(bank);
    expect(holds()).toEqual(bank);
    expect(machine.bank()).toEqual(bank);
  });
  test('below Viewer API 28 the camera call carries the camera and the target alone',()=>{
    const {viewer,calls}=fake({api:21}),machine=attachMachine(viewer,IDENTITY);
    machine.pose({crank:360,tens:0,units:1},camera);
    expect(calls[1]).toEqual(['setView',{camera:camera.camera,target:camera.target}]);
  });
  test('without a camera, draws the viewer again with the view it reports, as arrays',()=>{
    const {viewer,calls}=fake(),machine=attachMachine(viewer,IDENTITY);
    machine.pose({crank:360,tens:0,units:1});
    expect(calls).toEqual([['restore',{identity:IDENTITY,bank:{crank:360,tens:0,units:1}}],
      ['setView',{camera:[160,-260,140],target:[0,0,20],up:[0,0,1],fov:37}]]);
    const old=fake({api:21}),below=attachMachine(old.viewer,IDENTITY);
    below.pose({crank:0,tens:0,units:0});
    expect(old.calls[1]).toEqual(['setView',{camera:[160,-260,140],target:[0,0,20]}]);
  });
});

describe('a take transport',()=>{
  test('reads its length and its marks from the take document, and poses nothing when attached',()=>{
    const {viewer,calls}=fake(),take=attachTake(viewer,count);
    expect(take.kind).toBe('clocked');
    expect(take.duration).toBe(8);
    expect(take.marks).toEqual([{name:'one',time:2},{name:'nine',time:6},{name:'ten',time:8}]);
    expect(take.machine?.identity).toBe(IDENTITY);
    expect(take.time()).toBe(0);
    expect(calls).toEqual([]);
  });
  test('seeks each mark to the bank the take records there, by a restore and a redraw',()=>{
    const {viewer,calls,holds}=fake(),take=attachTake(viewer,count);
    for(const {name,time} of take.marks){
      calls.length=0;
      take.seek(time);
      expect(holds(),name).toEqual(count.take.banks[name]);
      expect(take.machine?.bank()).toEqual(count.take.banks[name]);
      expect(take.time()).toBe(time);
      expect(calls.map(c=>c[0])).toEqual(['restore','setView']);
    }
    take.seek(0);
    expect(holds()).toEqual(count.take.initial);
  });
  test('inside a step poses the bank the pose rule gives',()=>{
    const {viewer,holds}=fake(),take=attachTake(viewer,count);
    take.seek(3.5);
    expect(holds()).toEqual(bankAt(count,3.5));
    expect(holds()).not.toEqual(count.take.banks.one);
    expect(take.time()).toBe(3.5);
  });
  test('clamps a time outside the take to its start or its end',()=>{
    const {viewer,holds}=fake(),take=attachTake(viewer,count);
    take.seek(-1);
    expect([holds(),take.time()]).toEqual([count.take.initial,0]);
    take.seek(9);
    expect([holds(),take.time()]).toEqual([count.take.banks.ten,8]);
  });
  test('refuses a time that is not a number of seconds, by name, before touching the viewer',()=>{
    const {viewer,calls}=fake(),take=attachTake(viewer,count);
    for(const t of [Number.NaN,Number.POSITIVE_INFINITY,'2' as unknown as number])
      expect(()=>take.seek(t)).toThrow(/^seek: .* is not a take time in seconds$/);
    expect(calls).toEqual([]);
  });
  test('refuses a take that is not clocked, or a length that is not a positive number, naming the field',()=>{
    const {viewer,calls}=fake();
    expect(()=>attachTake(viewer,{...count,take:{...count.take,kind:'running'}} as unknown as TakeDocument))
      .toThrow(/take\.kind is "running"; a take transport poses a clocked take/);
    expect(()=>attachTake(viewer,{...count,model:{...count.model,expectedDurationSeconds:0}}))
      .toThrow(/model\.expectedDurationSeconds is 0; a take's length is a positive number of seconds/);
    expect(calls).toEqual([]);
  });
  test('refuses a viewer whose machine is not the take\'s',()=>{
    expect(()=>attachTake(fake({identity:'another-machine'}).viewer,count)).toThrow(/another-machine.*\(take\.identity\)/);
  });
});

describe('a loop transport',()=>{
  test('is the trivial take: one loop long, no marks, no machine',()=>{
    const {viewer,calls}=fake({api:28,identity:null}),loop=attachLoop(viewer);
    expect([loop.kind,loop.duration,loop.marks,loop.machine,loop.time()]).toEqual(['loop',1,[],null,0]);
    expect(calls).toEqual([]);
  });
  test('seeks by the viewer\'s loop time, clamped to the loop',()=>{
    const {viewer,calls}=fake({api:28,identity:null}),loop=attachLoop(viewer);
    loop.seek(.25);loop.seek(2);loop.seek(-1);
    expect(calls).toEqual([['setTime',.25],['setTime',1],['setTime',0]]);
    expect(loop.time()).toBe(0);
    expect(()=>loop.seek(Number.NaN)).toThrow(/^seek: NaN is not a loop time$/);
  });
});
