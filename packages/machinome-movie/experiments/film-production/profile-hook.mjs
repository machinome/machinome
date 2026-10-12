// Copied only into an ignored, private instrumentation tree by profile-compositing.mjs.
// Durations are monotonic milliseconds. Browser subphases are nested in Node
// await intervals and must never be summed with their enclosing call.
import {performance} from 'node:perf_hooks';

const now=()=>performance.now();
export const profile={
  frames:[],current:null,stages:[],counts:{},
  reset(){this.frames=[];this.current=null;this.stages=[];this.counts={};},
  count(name,n=1){
    this.counts[name]=(this.counts[name]??0)+n;
    if(this.current)this.current.calls[name]=(this.current.calls[name]??0)+n;
  },
  add(name,ms){
    if(this.current)this.current.nodeMs[name]=(this.current.nodeMs[name]??0)+ms;
    else this.stages.push({name,ms});
  },
  async measure(name,work){const start=now();try{return await work();}finally{this.add(name,now()-start);}},
  startFrame(frame){
    if(this.current)throw Error('Profiler frame overlap');
    const request=frame.request,partial=(request.annotations??[]).filter(a=>a.opacity>0&&a.opacity<1).length;
    this.current={index:frame.index,time:frame.time,shotId:request.shotId,partialFades:partial,
      transition:request.transition?.kind??null,picture:request.picture?.kind??null,
      nodeMs:{},pageMs:{},calls:{},startedMonotonicMs:now()};
  },
  pageTimes(observed){
    if(!this.current||!observed?.__profile)return;
    if(observed.__profile.repaintWait!==undefined)this.count('repaint');
    for(const [name,ms] of Object.entries(observed.__profile))
      this.current.pageMs[name]=(this.current.pageMs[name]??0)+ms;
  },
  pageResult(result){
    if(!this.current||!result?.__profile)return;
    for(const [name,ms] of Object.entries(result.__profile))
      this.current.pageMs[name]=(this.current.pageMs[name]??0)+ms;
  },
  async screenshot(page,kind){
    const start=now();const bytes=await page.screenshot();
    this.add(`${kind}ScreenshotCaptureEncodeTransfer`,now()-start);
    if(this.current&&kind==='final')this.current.finalScreenshotMonotonicMs=now();
    this.count(`${kind}Screenshot`);return bytes;
  },
  endFrame(){
    if(!this.current)throw Error('Profiler end without frame');
    this.current.endedMonotonicMs=now();
    this.current.totalMs=this.current.endedMonotonicMs-this.current.startedMonotonicMs;
    this.frames.push(this.current);this.current=null;
  },
};
