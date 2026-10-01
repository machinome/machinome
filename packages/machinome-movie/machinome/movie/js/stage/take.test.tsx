// Layer 4: a view on a clocked take, posed by its bank (the pose-a-take
// change, ADR-012). The runtime's pose of one view is a function of the view's
// state and the take's identity: a view carrying `bank` is restored on the
// viewer's machine, then its camera set, and its loop time never set; a view
// on a loop sets its time. A viewer without a machine, or with another, is
// refused naming the view. Stub viewers record what they are asked; no DOM.
import {describe,expect,test} from 'vitest';
import {poseView,viewMachine,type ViewerInstance} from './runtime';
import type {ViewState} from './types';

const IDENTITY='d46d4f1ee76199bce9aa9924e34a97020fd28bd3073939a2a85ec0eceb1111d6';
type Call=[string,...unknown[]];
// A stub viewer of the given API with, optionally, a machine of the given identity.
function stub(api:number,identity:string|null){
  const calls:Call[]=[];
  let bank:Record<string,number>={};
  const machine=identity===null?null:{
    identity:()=>identity,
    state:()=>({...bank}),
    restore:(snapshot:{identity:string;bank:Record<string,number>})=>{calls.push(['restore',snapshot]);bank={...snapshot.bank};},
  };
  const vec=(a:number[])=>({toArray:()=>[...a]});
  const viewer={apiVersion:api,setVisible(){},navigation:()=>({}),
    setTime:(t:number)=>{calls.push(['setTime',t]);},
    setView:(v:unknown)=>{calls.push(['setView',v]);},
    view:()=>({camera:vec([0,0,1]),target:vec([0,0,0])}),
    partOnScreen:()=>null,project:()=>null,highlight:()=>()=>{},
    machine:()=>machine} as unknown as ViewerInstance;
  return {viewer,calls};
}
const camera={view:{camera:[160,-260,140] as [number,number,number],target:[0,0,20] as [number,number,number]},
  up:[0,0,1] as [number,number,number],fov:37};
const onTake:ViewState={kind:'view',bank:{crank:1800,tens:0,units:5},...camera,hidden:[],highlight:null,marks:[]};
const onLoop:ViewState={kind:'view',time:.25,...camera,hidden:[],highlight:null,marks:[]};

describe('a view on a take',()=>{
  test('is restored to its bank with the take\'s identity, then its camera set, and no loop time is set',()=>{
    const {viewer,calls}=stub(29,IDENTITY);
    poseView(viewer,onTake,IDENTITY);
    expect(calls).toEqual([
      ['restore',{identity:IDENTITY,bank:{crank:1800,tens:0,units:5}}],
      ['setView',{camera:camera.view.camera,target:camera.view.target,up:camera.up,fov:camera.fov}]]);
    expect(viewer.machine?.()?.state()).toEqual(onTake.bank);
  });
  test('restores the whole bank given, a fresh copy each pose',()=>{
    const {viewer,calls}=stub(29,IDENTITY);
    poseView(viewer,onTake,IDENTITY);poseView(viewer,{...onTake,bank:{crank:360,tens:0,units:1}},IDENTITY);
    expect(calls.filter(c=>c[0]==='restore').map(c=>(c[1] as {bank:unknown}).bank)).toEqual([onTake.bank,{crank:360,tens:0,units:1}]);
  });
  test('a view on a loop sets its time, and touches no machine',()=>{
    const {viewer,calls}=stub(29,IDENTITY);
    poseView(viewer,onLoop,null);
    expect(calls.map(c=>c[0])).toEqual(['setTime','setView']);
    expect(calls[0]).toEqual(['setTime',.25]);
  });
  test('below API 28 the camera alone is set, as before',()=>{
    const {viewer,calls}=stub(21,null);
    poseView(viewer,onLoop,null);
    expect(calls[1]).toEqual(['setView',{camera:camera.view.camera,target:camera.view.target}]);
  });
});

describe('the machine of a view on a take',()=>{
  test('is the viewer\'s, when its identity is the take\'s',()=>{
    const {viewer}=stub(29,IDENTITY);
    expect(viewMachine(viewer,IDENTITY,'View counting.view in shot once').identity()).toBe(IDENTITY);
  });
  test('a viewer that gives no machine is refused naming the view and the shot',()=>{
    const {viewer}=stub(29,null);
    expect(()=>viewMachine(viewer,IDENTITY,'View counting.view in shot once'))
      .toThrow(/^View counting\.view in shot once: .*no machine/);
    const old={...stub(28,null).viewer,machine:undefined} as unknown as ViewerInstance;
    expect(()=>viewMachine(old,IDENTITY,'View counting.view in shot once')).toThrow(/View counting\.view in shot once: .*machine/);
  });
  test('another machine is refused naming both identities and take.identity',()=>{
    const {viewer}=stub(29,'another-machine');
    expect(()=>viewMachine(viewer,IDENTITY,'View counting.view in shot once'))
      .toThrow(new RegExp(`View counting\\.view in shot once: .*another-machine.*${IDENTITY}.*take\\.identity`));
  });
});
