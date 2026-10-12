// One pose in flight, the latest time wins (the player-page change, design
// D6). A time requested while a pose runs replaces any requested before it,
// so a frame the stage cannot reach before the clock moves on is dropped,
// never queued; nothing here waits on the clock, so the narration never
// waits for a pose. The time just posed is not posed again unless forced.

export interface Poser {
  /** Asks for `t`; `force` poses it even when it is the time just posed. */
  request(t:number,options?:{force?:boolean}):void;
  /** Whether a pose runs or waits. */
  busy():boolean;
  /** Resolves once no pose runs and none waits. */
  idle():Promise<void>;
}

export function poser(pose:(t:number)=>Promise<void>,onError:(error:unknown)=>void=()=>{}):Poser{
  let running=false,wanted:{t:number;force:boolean}|null=null,posed:number|null=null,current:number|null=null;
  let waiters:(()=>void)[]=[];
  const settle=()=>{if(!running&&!wanted){const done=waiters;waiters=[];for(const resolve of done)resolve();}};
  async function run(){
    running=true;
    while(wanted){
      const {t,force}=wanted;wanted=null;
      if(!force&&t===posed)continue;
      current=t;
      try{await pose(t);}catch(error){onError(error);}
      posed=t;current=null;
    }
    running=false;
    settle();
  }
  return {
    request(t,{force=false}={}){
      if(!force&&!wanted&&(running?current===t:posed===t))return;
      wanted={t,force:force||(wanted?.t===t&&wanted.force)};
      if(!running)void run();
    },
    busy:()=>running||wanted!==null,
    idle:()=>running||wanted?new Promise<void>(resolve=>{waiters.push(resolve);}):Promise.resolve(),
  };
}
