// The take transport (the take-transport change; ADR-020): the pose of a take
// on a mounted viewer, in a browser, outside the stage and through it. A
// machine transport poses a whole bank on the viewer's clocked machine; a
// take transport seeks a clocked take by the pose rule of src/take.mjs, the
// rule the frame uses, so a mark poses exactly its recorded bank; a loop
// transport seeks a posed loop by its normalized time. It knows the viewer's
// public handle and the take document, and nothing of the stage or the
// movie. Every call is synchronous: it returns once the viewer has drawn.
import {bankAt,type TakeDocument} from '../src/take.mjs';
import type {Bank,CameraView,ViewerInstance} from './viewer-handle';

export interface MachineTransport {
  /** The identity the take was recorded on, which every pose restores with. */
  readonly identity:string;
  /**
   * Restores the whole bank on the viewer's machine with the take's
   * identity, then sets the camera given (up and field of view from Viewer
   * API 28), or, given none, draws the viewer again with the view it
   * reports: one restore and one setView.
   */
  pose(bank:Bank,view?:CameraView):void;
  /** The bank the viewer's machine holds. */
  bank():Bank;
}
export interface TakeTransport {
  readonly kind:'clocked'|'loop';
  /** Clocked: the take's length in take seconds; loop: 1. */
  readonly duration:number;
  /** The marks in take-time order; a loop has none. */
  readonly marks:ReadonlyArray<{readonly name:string;readonly time:number}>;
  /** Poses the take at `t`, clamped to [0, duration]. */
  seek(t:number):void;
  /** The last time sought, clamped; 0 before any. */
  time():number;
  /** Clocked: the machine transport a seek poses through; loop: null. */
  readonly machine:MachineTransport|null;
}
export type {TakeDocument};

const clamp=(t:number,high:number)=>Math.min(high,Math.max(0,t));
const shown=(value:unknown)=>typeof value==='number'?String(value):JSON.stringify(value)??String(value);

/**
 * The machine transport of a viewer whose machine is the one a take was
 * recorded on. Refuses, before anything is restored, set or drawn, a missing
 * identity, a viewer that gives no machine and a machine of another identity.
 * The words are the stage's; the stage prefixes them with the view and the
 * shot.
 */
export function attachMachine(viewer:ViewerInstance,identity:string):MachineTransport{
  if(typeof identity!=='string'||!identity)
    throw new Error('no take identity was given (take.identity); a machine is posed with the identity its take was recorded on');
  const machine=typeof viewer.machine==='function'?viewer.machine():null;
  if(!machine)throw new Error('the viewer gives no machine for this clocked document; a view on a take is posed through viewer.machine(), from Viewer API 29');
  const own=machine.identity();
  if(own!==identity)throw new Error(`the viewer's machine is ${own}, and the take was recorded on ${identity} (take.identity)`);
  const lens=viewer.apiVersion>=28;
  return {
    identity,
    pose(bank,view){
      machine.restore({identity,bank:{...bank}});
      if(view){
        viewer.setView(lens?{camera:view.camera,target:view.target,up:view.up,fov:view.fov}:{camera:view.camera,target:view.target});
        return;
      }
      // The view the viewer holds, read back as arrays: setView is what draws
      // a restored bank under on-demand rendering (ADR-012).
      const own=viewer.view(),camera=own.camera.toArray() as CameraView['camera'],target=own.target.toArray() as CameraView['target'];
      viewer.setView(lens?{camera,target,up:own.up?.toArray() as CameraView['up'],fov:own.fov}:{camera,target});
    },
    bank:()=>machine.state(),
  };
}

/**
 * The transport of a clocked take on a viewer whose machine is the take's:
 * `doc` is what the pose rule reads, {model: {expectedDurationSeconds},
 * marks, take}. Attaching poses nothing.
 */
export function attachTake(viewer:ViewerInstance,doc:TakeDocument):TakeTransport{
  const kind=(doc.take as {kind?:unknown}|undefined)?.kind;
  if(kind!=='clocked')throw new Error(`attachTake: take.kind is ${shown(kind)}; a take transport poses a clocked take`);
  const duration=doc.model?.expectedDurationSeconds;
  if(typeof duration!=='number'||!Number.isFinite(duration)||duration<=0)
    throw new Error(`attachTake: model.expectedDurationSeconds is ${shown(duration)}; a take's length is a positive number of seconds`);
  const machine=attachMachine(viewer,doc.take.identity);
  // Take-time order; Array.prototype.sort is stable, so equal times keep the
  // document's order.
  const marks=Object.freeze(Object.entries(doc.marks??{}).map(([name,time])=>Object.freeze({name,time}))
    .sort((a,b)=>a.time-b.time));
  let last=0;
  return {
    kind:'clocked',duration,marks,machine,
    seek(t){
      if(typeof t!=='number'||!Number.isFinite(t))throw new Error(`seek: ${shown(t)} is not a take time in seconds`);
      const at=clamp(t,duration);
      machine.pose(bankAt(doc,at));
      last=at;
    },
    time:()=>last,
  };
}

/** The trivial take of a posed loop: one loop long, no marks, no machine; a seek sets the loop's time. */
export function attachLoop(viewer:ViewerInstance):TakeTransport{
  let last=0;
  return {
    kind:'loop',duration:1,marks:Object.freeze([]),machine:null,
    seek(t){
      if(typeof t!=='number'||!Number.isFinite(t))throw new Error(`seek: ${shown(t)} is not a loop time`);
      const at=clamp(t,1);
      viewer.setTime(at);
      last=at;
    },
    time:()=>last,
  };
}
