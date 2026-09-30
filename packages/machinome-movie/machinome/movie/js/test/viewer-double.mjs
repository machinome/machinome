// The scripted MachinomeViewer double shared by the browser tests. Not a test
// file: it registers no tests.
// A configurable API 28 viewer double. Its canvas is one flat colour; a part's
// on-screen rect moves with model time; project() is a pinhole camera. Every
// instance of a page records its calls in the one list window.viewerCalls, in
// order; window.viewerInstances lists each mount ({selector, calls}).
export function viewerDouble(options={}){
  const o={api:28,color:'#6f8fa8',...options};
  return `window.MachinomeViewer={async mount(selector,url,options){
    const o=${JSON.stringify(o)};
    const canvas=document.createElement('canvas');canvas.style.width='100%';canvas.style.height='100%';canvas.style.background=o.color;
    document.querySelector(selector).append(canvas);
    let view={camera:options.view.camera,target:options.view.target,up:options.up,fov:options.fov},time=options.time??0,lit=null,drifted=0;
    const calls=window.viewerCalls??=[],own=[];
    (window.viewerInstances??=[]).push({selector,calls:own});
    const record=call=>{calls.push(call);own.push(call);};
    const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
    const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
    const norm=a=>{const l=Math.hypot(...a);return a.map(v=>v/l);};
    const vec=a=>({toArray:()=>[...a]});
    return {apiVersion:o.api,setVisible(){},navigation(){return {};},
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
        let h=0;for(const c of name)h=(h*31+c.charCodeAt(0))%997;
        const b=name==='Feed/Pawl'?b0:{left:b0.left,top:b0.top+b0.height*((h%7)-3)*.06,width:b0.width,height:b0.height};
        // rectSize: the same centre, another size (off by default).
        if(o.rectSize){const [w,h]=o.rectSize;return {rect:{x:b.left+b.width*(.35+.3*time)+12-w/2,y:b.top+b.height*.5-h/2,width:w,height:h},point:null};}
        return {rect:{x:b.left+b.width*(.35+.3*time),y:b.top+b.height*.5-10,width:24,height:20},point:null};
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
