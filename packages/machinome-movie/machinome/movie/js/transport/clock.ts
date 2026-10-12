// The clocks a transport is driven by (the take-transport change; ADR-020): a
// timer, for a take watched by itself or a film without narration, and the
// narration's audio element, for a film with its mix. A clock calls back once
// per animation frame while it plays, with its time then, and once on the
// animation frame after a seek; a slow frame is dropped, never queued. No UI.
// The frame scheduler is injectable, so a clock is proved without a browser.

export interface Clock {
  readonly duration:number;
  play():void;
  pause():void;
  playing():boolean;
  /** Clamps to [0, duration]; leaves the clock playing or paused. */
  seek(t:number):void;
  time():number;
  rate():number;
  /** Positive and finite. */
  setRate(r:number):void;
  /** Per animation frame while playing, and once after a seek; returns the unsubscribe. */
  onFrame(callback:(t:number)=>void):()=>void;
}
/** Animation frames: by default the browser's requestAnimationFrame. */
export interface FrameScheduler {
  request(callback:()=>void):number;
  cancel(handle:number):void;
}
/** What the audio clock uses of an audio element (an HTMLAudioElement is one). */
export type ClockAudio=Pick<HTMLMediaElement,'currentTime'|'paused'|'ended'|'playbackRate'|'play'|'pause'>;

const animationFrames=():FrameScheduler=>({
  request:callback=>requestAnimationFrame(()=>callback()),
  cancel:handle=>cancelAnimationFrame(handle),
});
const shown=(value:unknown)=>typeof value==='number'?String(value):JSON.stringify(value)??String(value);
const positive=(value:unknown)=>typeof value==='number'&&Number.isFinite(value)&&value>0;
function needDuration(name:string,duration:number){
  if(!positive(duration))throw new Error(`${name}: ${shown(duration)} is not a positive duration in seconds`);
}
function needRate(r:number){
  if(!positive(r))throw new Error(`setRate: ${shown(r)} is not a positive rate`);
}
function needTime(t:number){
  if(typeof t!=='number'||!Number.isFinite(t))throw new Error(`seek: ${shown(t)} is not a time in seconds`);
}

// The callbacks and the one animation frame a clock asks for at a time. A
// seek's frame survives a pause; the frame of a play does not.
function frameLoop(frames:FrameScheduler,time:()=>number,playing:()=>boolean){
  const callbacks=new Set<(t:number)=>void>();
  let handle:number|null=null,sought=false;
  function tick(){
    handle=null;sought=false;
    const t=time();
    for(const callback of [...callbacks])callback(t);
    if(playing())ask();
  }
  function ask(){if(handle===null)handle=frames.request(tick);}
  return {
    ask,
    seek(){sought=true;ask();},
    pause(){if(handle!==null&&!sought){frames.cancel(handle);handle=null;}},
    subscribe(callback:(t:number)=>void){callbacks.add(callback);return ()=>{callbacks.delete(callback);};},
  };
}

/**
 * A clock of `duration` seconds over a time source in milliseconds (by
 * default performance.now()). It stops at its duration exactly; played
 * again there, it starts from 0, as a media element does once ended.
 */
export function timerClock(duration:number,now:()=>number=()=>performance.now(),frames:FrameScheduler=animationFrames()):Clock{
  needDuration('timerClock',duration);
  // The time at the last play, seek or change of rate, and the source's
  // milliseconds then while playing (null while paused).
  let base=0,since:number|null=null,speed=1;
  function time(){
    if(since===null)return base;
    const t=base+(now()-since)/1000*speed;
    if(t<duration)return t;
    base=duration;since=null;
    return base;
  }
  const playing=()=>{time();return since!==null;};
  const loop=frameLoop(frames,time,playing);
  return {
    duration,time,playing,
    play(){
      if(playing())return;
      if(base>=duration)base=0;
      since=now();loop.ask();
    },
    pause(){
      if(since!==null){base=time();since=null;}
      loop.pause();
    },
    seek(t){
      needTime(t);
      base=Math.min(duration,Math.max(0,t));
      if(since!==null)since=now();
      loop.seek();
    },
    rate:()=>speed,
    setRate(r){
      needRate(r);
      if(playing()){base=time();since=now();}
      speed=r;
    },
    onFrame:callback=>loop.subscribe(callback),
  };
}

/**
 * A clock whose time is an audio element's playback position, clamped to
 * `duration`: play, pause, seek and rate drive the element. On reaching its
 * duration it pauses the element; played again there, it starts from 0.
 */
export function audioClock(audio:ClockAudio,duration:number,frames:FrameScheduler=animationFrames()):Clock{
  needDuration('audioClock',duration);
  const time=()=>Math.min(duration,Math.max(0,audio.currentTime));
  function playing(){
    if(!audio.paused&&audio.currentTime>=duration)audio.pause();
    return !audio.paused&&!audio.ended;
  }
  const loop=frameLoop(frames,time,playing);
  return {
    duration,time,playing,
    play(){
      if(audio.ended||audio.currentTime>=duration)audio.currentTime=0;
      // A refusal of the browser's autoplay policy rejects this promise and
      // leaves the element paused; it reaches the page's console.
      void audio.play();
      loop.ask();
    },
    pause(){audio.pause();loop.pause();},
    seek(t){
      needTime(t);
      audio.currentTime=Math.min(duration,Math.max(0,t));
      loop.seek();
    },
    rate:()=>audio.playbackRate,
    setRate(r){needRate(r);audio.playbackRate=r;},
    onFrame:callback=>loop.subscribe(callback),
  };
}
