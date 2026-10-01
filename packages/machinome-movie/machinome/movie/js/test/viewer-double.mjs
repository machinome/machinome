// The scripted MachinomeViewer double shared by the browser tests. Not a test
// file: it registers no tests.
// A configurable API 28 viewer double. Its canvas is one flat colour; a part's
// on-screen rect moves with model time, or with `machine` with the bank its
// clocked machine holds (below); project() is a pinhole camera. Every
// instance of a page records its calls in the one list window.viewerCalls, in
// order; window.viewerInstances lists each mount ({selector, calls}).
export function viewerDouble(options={}){
  const o={api:28,color:'#6f8fa8',...options};
  return `window.MachinomeViewer={async mount(selector,url,options){
    const o=${JSON.stringify(o)};
    // A machine names the input its part rects follow, one its bank holds.
    if(o.machine){const ids=Object.keys(o.machine.initial).join(', '),input=o.machine.follows?.input;
      if(input===undefined)throw new Error('the double\\'s machine follows no input; name one of '+ids+' in machine.follows');
      if(!Object.hasOwn(o.machine.initial,input))throw new Error('the double\\'s machine follows '+input+', which its bank does not hold ('+ids+')');}
    const canvas=document.createElement('canvas');canvas.style.background=o.color;
    const host=document.querySelector(selector);host.append(canvas);
    // lateCanvas: size the canvas from the host on the next animation frame,
    // after mount and after each resize, as the real viewer does (a number:
    // that many animation frames after the resize); stuckCanvas: as
    // lateCanvas, but a canvas never shrinks once sized; otherwise the canvas
    // fills its host at once.
    if(o.lateCanvas||o.stuckCanvas){
      canvas.style.width='1px';canvas.style.height='1px';
      const late=typeof o.lateCanvas==='number'?o.lateCanvas:1;
      const after=(n,fn)=>requestAnimationFrame(()=>n>1?after(n-1,fn):fn());
      const fit=()=>{const b=host.getBoundingClientRect(),c=canvas.getBoundingClientRect();
        const w=o.stuckCanvas?Math.max(b.width,c.width):b.width,h=o.stuckCanvas?Math.max(b.height,c.height):b.height;
        canvas.style.width=w+'px';canvas.style.height=h+'px';};
      after(late,fit);new ResizeObserver(()=>after(late,fit)).observe(host);
    }else{canvas.style.width='100%';canvas.style.height='100%';}
    let view={camera:options.view.camera,target:options.view.target,up:options.up,fov:options.fov},time=options.time??0,lit=null,drifted=0;
    const calls=window.viewerCalls??=[],own=[];
    (window.viewerInstances??=[]).push({selector,calls:own});
    const record=call=>{calls.push(call);own.push(call);};
    const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
    const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
    const norm=a=>{const l=Math.hypot(...a);return a.map(v=>v/l);};
    const vec=a=>({toArray:()=>[...a]});
    // machine: {identity, initial, requests, follows}: a clocked machine
    // whose move() answers from the requests (a take's steps, or a table a
    // test forges), found by the input, the to or by, and the origin the bank
    // holds. Its bank is drawn as an inset outline of the canvas, a colour of
    // the whole bank, so a pose change reaches the pixels and a highlight's
    // tint stays; follows: {input, range: [low, high]} places the part rects
    // at that input's fraction of its range where a loop's time places them
    // without a machine, so a mark follows its part from bank to bank.
    const m=o.machine;
    let bank=m?{...m.initial}:null;
    const paint=()=>{let h=7;for(const c of JSON.stringify(bank))h=(h*31+c.charCodeAt(0))%16777213;
      canvas.style.outline='12px solid rgb('+(h>>16&255)+','+(h>>8&255)+','+(h&255)+')';canvas.style.outlineOffset='-12px';};
    if(m)paint();
    const machine=!m?null:{
      identity:()=>m.identity,order:()=>Object.keys(m.initial),state:()=>({...bank}),
      snapshot:()=>({identity:m.identity,bank:{...bank}}),
      reset(){record(['reset']);bank={...m.initial};paint();},
      restore(s){record(['restore',s.bank]);
        if(s.identity!==m.identity)throw new Error('restore: '+s.identity+' is not the identity of this machine, '+m.identity);
        // skew: a machine that holds other values than those restored on it.
        bank={...s.bank,...(m.skew??{})};paint();},
      move(input,args){record(['move',input,args]);
        const r=m.requests.find(q=>q.input===input&&(args.to!==undefined?q.to===args.to:q.by===args.by)&&q.origin===bank[input]);
        if(!r)throw new Error('the double has no request for '+input+' '+JSON.stringify(args)+' from '+bank[input]);
        bank={...bank,[input]:r.end};for(const c of r.commits)Object.assign(bank,c.targets);paint();
        return {input,...(r.to!==undefined?{to:r.to}:{by:r.by}),origin:r.origin,end:r.end,admitted:r.admitted,
          commits:JSON.parse(JSON.stringify(r.commits)),stops:JSON.parse(JSON.stringify(r.stops??[]))};},
      // Drawing an instruction needs the frame loop, which on-demand rendering does not run.
      trigger(name){if(options.renderMode==='on-demand')throw new Error('trigger('+name+') needs the frame loop; on-demand rendering refuses it');
        throw new Error('the double draws no instruction');},
    };
    return {apiVersion:o.api,setVisible(){},navigation(){return {};},machine(){return machine;},
      setTime(t){if(o.recordTime)record(['setTime',t]);time=t;
        if(o.timeColor)canvas.style.background='rgb('+Math.round(255*t)+',96,160)';},
      setView(v){record(['setView',v]);if(!v.camera.every(Number.isFinite))throw new Error('invalid camera');
        // drift: a viewer whose picture depends on how often it was posed (a control for replay proofs).
        if(o.drift){drifted=(drifted+37)%256;canvas.style.background='rgb('+drifted+',96,160)';}
        view={...view,camera:v.camera,target:v.target};
        if(!o.ignoreFov){if(v.up)view.up=v.up;if(v.fov!==undefined)view.fov=v.fov;}},
      view(){return {camera:vec(view.camera),target:vec(view.target),up:vec(view.up),fov:view.fov};},
      partOnScreen(path){
        // Known parts: Feed/Pawl, or the listed paths ('*' for any); each
        // path sits at its own height, the pawl's at the middle.
        const name=path.join('/'),known=o.parts??['Feed/Pawl'];
        if(known!=='*'&&!known.includes(name))throw new Error('Unknown assembly path: '+name);
        if(o.vanishAfter!==undefined&&time>o.vanishAfter)return null;
        const b0=canvas.getBoundingClientRect();
        // Where along its row: the loop's time, or the followed input's
        // fraction of its range in the bank the machine holds.
        const f=m?.follows,at=m?(bank[f.input]-f.range[0])/(f.range[1]-f.range[0]):time;
        let h=0;for(const c of name)h=(h*31+c.charCodeAt(0))%997;
        const b=name==='Feed/Pawl'?b0:{left:b0.left,top:b0.top+b0.height*((h%7)-3)*.06,width:b0.width,height:b0.height};
        // rectSize: the same centre, another size (off by default).
        if(o.rectSize){const [w,h]=o.rectSize;return {rect:{x:b.left+b.width*(.35+.3*at)+12-w/2,y:b.top+b.height*.5-h/2,width:w,height:h},point:null};}
        return {rect:{x:b.left+b.width*(.35+.3*at),y:b.top+b.height*.5-10,width:24,height:20},point:null};
      },
      project(p){
        const f=norm(sub(view.target,view.camera)),r=norm(cross(f,view.up)),u=cross(r,f),d=sub(p,view.camera),z=dot(d,f);
        if(z<=0)return null;const b=canvas.getBoundingClientRect(),k=(b.height/2)/Math.tan(view.fov*Math.PI/360);
        return {x:b.left+b.width/2+dot(d,r)/z*k,y:b.top+b.height/2-dot(d,u)/z*k};
      },
      highlight(paths,settings){
        if(lit)throw new Error('A highlight is already standing');
        record(['highlight',paths,settings]);if(!o.inertHighlight)canvas.style.background=o.tintHighlight?'color-mix(in srgb, '+settings.color+' 40%, white)':settings.color;
        const token=lit={};
        return ()=>{if(lit!==token)throw new Error('restore called twice');record(['restore']);lit=null;if(!o.brokenRestore)canvas.style.background=o.color;};
      }};
  }};`;
}
