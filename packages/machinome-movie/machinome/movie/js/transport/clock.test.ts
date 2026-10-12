// Layer 4: the clocks (the take-transport change; ADR-020), driven by an
// injected time source and frame scheduler, and the audio clock by a fake
// element: no wall clock and no browser, so every verdict is a function of
// what the test gives.
import {describe,expect,test} from 'vitest';
import {audioClock,timerClock,type FrameScheduler} from './clock';

// A frame scheduler a test runs by hand: `run()` is one animation frame.
function scheduler(){
  let next=1;const pending=new Map<number,()=>void>();
  const frames:FrameScheduler&{pending():number;run():void}={
    request:callback=>{const handle=next++;pending.set(handle,callback);return handle;},
    cancel:handle=>{pending.delete(handle);},
    pending:()=>pending.size,
    run:()=>{const due=[...pending.values()];pending.clear();for(const callback of due)callback();},
  };
  return frames;
}
// A timer over a time source the test sets, in milliseconds.
function timer(duration=2){
  const source={ms:0},frames=scheduler(),seen:number[]=[];
  const clock=timerClock(duration,()=>source.ms,frames);
  clock.onFrame(t=>{seen.push(t);});
  const at=(ms:number)=>{source.ms=ms;frames.run();};
  return {clock,frames,seen,source,at};
}

describe('a timer clock',()=>{
  test('plays to its end, calling back once per animation frame, and stops at its duration exactly',()=>{
    const {clock,frames,seen,at}=timer();
    expect([clock.duration,clock.time(),clock.playing(),clock.rate()]).toEqual([2,0,false,1]);
    clock.play();
    expect(clock.playing()).toBe(true);
    at(500);at(1000);at(1500);at(2100);
    expect(seen).toEqual([.5,1,1.5,2]);
    expect([clock.playing(),clock.time(),frames.pending()]).toEqual([false,2,0]);
  });
  test('drops a slow frame rather than queueing it',()=>{
    const {clock,seen,at}=timer();
    clock.play();at(1200);
    expect(seen).toEqual([1.2]);
  });
  test('scales its time by its rate, continuously across a change, and refuses a rate that is not positive',()=>{
    const {clock,source,at}=timer(10);
    clock.play();at(500);
    clock.setRate(2);
    expect([clock.rate(),clock.time()]).toEqual([2,.5]);
    source.ms=1000;
    expect(clock.time()).toBe(1.5);
    for(const r of [0,-1,Number.NaN,Number.POSITIVE_INFINITY])
      expect(()=>clock.setRate(r)).toThrow(/^setRate: .* is not a positive rate$/);
    expect(clock.rate()).toBe(2);
  });
  test('a seek while paused calls back once on the next frame, with the latest time, and stays paused',()=>{
    const {clock,frames,seen}=timer();
    clock.seek(.75);clock.seek(1.25);
    expect(seen).toEqual([]);
    expect(frames.pending()).toBe(1);
    frames.run();
    expect(seen).toEqual([1.25]);
    expect([clock.playing(),clock.time(),frames.pending()]).toEqual([false,1.25,0]);
  });
  test('a seek while playing keeps it playing from the time sought',()=>{
    const {clock,source,seen,at}=timer();
    clock.play();at(500);
    clock.seek(1.5);
    expect(clock.time()).toBe(1.5);
    at(750);
    expect(seen).toEqual([.5,1.75]);
    expect(clock.playing()).toBe(true);
    source.ms=1250;
    expect(clock.time()).toBe(2);
  });
  test('clamps a seek to the clock, and refuses a time that is not a number of seconds',()=>{
    const {clock}=timer();
    clock.seek(-3);expect(clock.time()).toBe(0);
    clock.seek(9);expect(clock.time()).toBe(2);
    expect(()=>clock.seek(Number.NaN)).toThrow(/^seek: NaN is not a time in seconds$/);
  });
  test('a pause holds the time and cancels the next frame, unless a seek asked for it',()=>{
    const {clock,frames,source,seen,at}=timer();
    clock.play();at(500);
    clock.pause();
    expect([clock.playing(),clock.time(),frames.pending()]).toEqual([false,.5,0]);
    source.ms=900;
    expect(clock.time()).toBe(.5);
    clock.play();clock.seek(1);clock.pause();
    expect(frames.pending()).toBe(1);
    frames.run();
    expect(seen).toEqual([.5,1]);
  });
  test('played at its end, starts again from the beginning',()=>{
    const {clock,source,at}=timer();
    clock.play();at(2500);
    expect(clock.playing()).toBe(false);
    clock.play();
    expect([clock.playing(),clock.time()]).toEqual([true,0]);
    source.ms=3000;
    expect(clock.time()).toBe(.5);
  });
  test('stops calling back once its subscriber unsubscribes',()=>{
    const {clock,frames}=timer(),late:number[]=[];
    const off=clock.onFrame(t=>{late.push(t);});
    clock.seek(1);frames.run();
    off();
    clock.seek(1.5);frames.run();
    expect(late).toEqual([1]);
  });
  test('refuses a duration that is not a positive number of seconds',()=>{
    for(const d of [0,-2,Number.NaN,Number.POSITIVE_INFINITY])
      expect(()=>timerClock(d,()=>0,scheduler())).toThrow(/^timerClock: .* is not a positive duration in seconds$/);
  });
});

// A fake audio element: what an HTMLMediaElement does that the clock uses.
function element(){
  const el={currentTime:0,paused:true,ended:false,playbackRate:1,plays:0,
    play(){el.paused=false;el.ended=false;el.plays++;return Promise.resolve();},
    pause(){el.paused=true;}};
  return el;
}
describe('an audio clock',()=>{
  test('is the element\'s position, and plays, pauses, seeks and changes rate by driving the element',()=>{
    const el=element(),clock=audioClock(el,10,scheduler());
    expect([clock.duration,clock.time(),clock.playing(),clock.rate()]).toEqual([10,0,false,1]);
    clock.play();
    expect([el.paused,el.plays,clock.playing()]).toEqual([false,1,true]);
    clock.seek(3);
    expect([el.currentTime,clock.time(),clock.playing()]).toEqual([3,3,true]);
    clock.setRate(1.5);
    expect([el.playbackRate,clock.rate()]).toEqual([1.5,1.5]);
    clock.pause();
    expect([el.paused,clock.playing()]).toEqual([true,false]);
    clock.seek(12);
    expect([el.currentTime,clock.time()]).toEqual([10,10]);
    el.currentTime=12;
    expect(clock.time()).toBe(10);
    expect(()=>clock.setRate(0)).toThrow(/^setRate: 0 is not a positive rate$/);
    expect(()=>audioClock(element(),0,scheduler())).toThrow(/^audioClock: 0 is not a positive duration in seconds$/);
  });
  test('calls back per frame while the element plays, and once after a seek',()=>{
    const el=element(),frames=scheduler(),clock=audioClock(el,10,frames),seen:number[]=[];
    clock.onFrame(t=>{seen.push(t);});
    clock.play();
    el.currentTime=1;frames.run();
    el.currentTime=1.5;frames.run();
    clock.pause();
    expect(frames.pending()).toBe(0);
    clock.seek(4);clock.seek(4.5);
    frames.run();
    expect(seen).toEqual([1,1.5,4.5]);
    expect(frames.pending()).toBe(0);
  });
  test('stops at its duration: pauses the element and calls back with the duration; played again, starts from 0',()=>{
    const el=element(),frames=scheduler(),clock=audioClock(el,10,frames),seen:number[]=[];
    clock.onFrame(t=>{seen.push(t);});
    clock.play();
    el.currentTime=10.2;frames.run();
    expect([seen,el.paused,clock.playing(),frames.pending()]).toEqual([[10],true,false,0]);
    clock.play();
    expect([el.currentTime,el.paused]).toEqual([0,false]);
    el.paused=true;el.ended=true;el.currentTime=9.5;
    clock.play();
    expect(el.currentTime).toBe(0);
  });
});
