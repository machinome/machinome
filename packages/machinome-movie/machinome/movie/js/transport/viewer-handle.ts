// The viewer's public handle as Videomaker reaches it: what the stage and the
// take transport call on a mounted machinome-viewer instance (Viewer API 21;
// up and field of view through setView from 28; the clocked machine's handle
// from 29). Types only: no value and no import, so the take transport can be
// moved to another package with nothing of this repository behind it
// (ADR-020). The stage imports these types from here.

export type Vec3=[number,number,number];
export interface Rect {x:number;y:number;width:number;height:number}
/** A clocked machine's drivers and states by qualified id, in native units. */
export type Bank=Record<string,number>;
/** A vector as the viewer returns it from view(). */
export interface Vector {toArray():number[]}
/** A camera as setView takes it; up and field of view from Viewer API 28. */
export interface CameraView {camera:Vec3;target:Vec3;up?:Vec3;fov?:number}

/** The viewer's handle on a clocked machine (Viewer API 29, on-demand). */
export interface MachineHandle {
  identity():string;
  state():Bank;
  restore(snapshot:{identity:string;bank:Bank}):void;
}
export interface ViewerInstance {
  apiVersion:number;
  setVisible(path:string[],visible:boolean):void;
  navigation():unknown;
  machine?():MachineHandle|null;
  setTime(time:number):void;
  setView(view:CameraView):void;
  view():{camera:Vector;target:Vector;up?:Vector;fov?:number};
  partOnScreen(path:string[]):{rect:Rect}|null;
  project(point:Vec3):{x:number;y:number}|null;
  highlight(paths:string[][],settings:{color?:string;others?:string}):()=>void;
}
export interface ViewerFactory {mount(selector:string,url:string,options:Record<string,unknown>):Promise<ViewerInstance>}
