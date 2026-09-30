// Browser presentation only. All mechanics stay inside the public viewer.
(async()=>{
  const cfg=await (await fetch('/config.json')).json();
  const style=cfg.style;
  document.body.style.background=style.background;
  document.documentElement.style.setProperty('--film-background',style.background);
  document.body.style.color=style.foreground;
  document.body.style.fontFamily=style.fontFamily;
  document.querySelector('#brand').style.color=style.accent;
  document.querySelector('#progress').style.background=style.accent;
  document.querySelector('#series').textContent=cfg.series;
  document.body.classList.toggle('with-code',Boolean(cfg.initial.code));
  const viewer=await MachinomeViewer.mount('#stage','/model/manifest.json',{
    renderMode:'on-demand',
    animation:'external',autoplay:false,driverControls:'none',partControls:'none',
    time:cfg.initial.time,view:cfg.initial.view,up:cfg.initial.up,fov:cfg.initial.fov,
  });
  if(viewer.apiVersion<21||typeof viewer.setView!=='function')throw new Error('Viewer API 21 with setView is required');
  // Refuse on mount rather than render a film with its new cues missing.
  if(viewer.apiVersion<cfg.requiredViewerApi.api)throw new Error(cfg.viewerRefusal.replace('{declared}',String(viewer.apiVersion)));
  await document.fonts.ready;
  let hidden=[],applied=null,restore=null;
  const layer=document.querySelector('#annotations'),svgNS='http://www.w3.org/2000/svg';
  const plain=r=>({x:r.x,y:r.y,width:r.width,height:r.height});
  const union=(a,b)=>{const x=Math.min(a.x,b.x),y=Math.min(a.y,b.y);
    return {x,y,width:Math.max(a.x+a.width,b.x+b.width)-x,height:Math.max(a.y+a.height,b.y+b.height)-y};};
  // The anchor of a part is the centre of its on-screen rect (the union for a
  // multi-path layer); of a world point, its projection. Viewport CSS pixels.
  function resolve(target){
    if(target.point){const p=viewer.project(target.point);return {anchor:p?{x:p.x,y:p.y}:null,rect:null};}
    let rect=null;
    for(const path of target.paths){const on=viewer.partOnScreen(path);if(on)rect=rect?union(rect,on.rect):plain(on.rect);}
    return {anchor:rect?{x:rect.x+rect.width/2,y:rect.y+rect.height/2}:null,rect};
  }
  // Rebuilt from nothing every frame, after the viewer is posed; reading never renders.
  function drawAnnotations(frame){
    layer.replaceChildren();
    const cues=frame.annotations??[];if(!cues.length)return [];
    const origin=layer.getBoundingClientRect(),W=window.innerWidth,H=window.innerHeight;
    const svg=document.createElementNS(svgNS,'svg');svg.setAttribute('width',W);svg.setAttribute('height',H);layer.append(svg);
    const shape=(name,attributes,parent=svg)=>{const el=document.createElementNS(svgNS,name);for(const [k,v] of Object.entries(attributes))el.setAttribute(k,v);parent.append(el);return el;};
    const local=p=>({x:p.x-origin.left,y:p.y-origin.top});
    const drawn=[];
    for(const cue of cues){
      let found;
      try{found=resolve(cue.target);}catch(error){throw new Error(`Viewer refused annotation #${cue.index} in shot ${frame.shotId}: ${error.message}`);}
      const entry={index:cue.index,kind:cue.kind,anchor:found.anchor,rect:found.rect,text:null,tail:null};drawn.push(entry);
      if(!entry.anchor)continue;
      const inset=cue.safeInset,safe={x:W*inset,y:H*inset,width:W*(1-2*inset),height:H*(1-2*inset)};
      // At rest use the exact old drawing path, including text rasterization.
      const animated=cue.opacity!==undefined&&(cue.opacity<1||cue.drawn<1);
      const strokes=animated?shape('g',{opacity:cue.opacity}):svg;
      if(cue.opacity!==undefined){entry.opacity=cue.opacity;entry.drawn=cue.drawn;}
      if(cue.kind==='ring'){
        const {x,y,width,height}=entry.rect,P=cue.padding*safe.width;
        const cx=x+width/2,cy=y+height/2,rx=Math.SQRT2*(width/2+P),ry=Math.SQRT2*(height/2+P);
        entry.ring={cx,cy,rx,ry};
        const top=local({x:cx,y:cy-ry}),bottom=local({x:cx,y:cy+ry});
        const path=shape('path',{d:`M ${top.x} ${top.y} A ${rx} ${ry} 0 0 1 ${bottom.x} ${bottom.y} A ${rx} ${ry} 0 0 1 ${top.x} ${top.y}`,
          fill:'none',stroke:style.accent,'stroke-width':W*.0024},strokes);
        if(cue.drawn!==undefined&&cue.drawn<1){
          path.setAttribute('pathLength','1');path.setAttribute('stroke-dasharray',`${cue.drawn} 1`);
          path.setAttribute('stroke-linecap','butt');
          if(cue.drawn>0){
            const length=path.getTotalLength(),inside=path.getPointAtLength(cue.drawn*length/2),outside=path.getPointAtLength((1+cue.drawn)*length/2);
            entry.inside={x:inside.x+origin.left,y:inside.y+origin.top};
            entry.outside={x:outside.x+origin.left,y:outside.y+origin.top};
          }
        }
        continue;
      }
      const centre=cue.kind==='arrow'?{x:safe.x+cue.place[0]*safe.width,y:safe.y+cue.place[1]*safe.height}
        :{x:entry.anchor.x+cue.offset[0]*safe.width,y:entry.anchor.y+cue.offset[1]*safe.height};
      if(cue.text!==undefined){
        const el=document.createElement('div');el.className='annotation-text';el.textContent=cue.text;layer.append(el);
        const size=el.getBoundingClientRect(),at=local({x:centre.x-size.width/2,y:centre.y-size.height/2});
        el.style.left=`${at.x}px`;el.style.top=`${at.y}px`;entry.text=plain(el.getBoundingClientRect());
        if(animated)el.style.opacity=String(cue.opacity);
      }
      if(cue.kind!=='arrow')continue;
      // The shaft leaves the text box at the edge nearest the tip; the tip touches the part.
      const tip=entry.anchor,dx=tip.x-centre.x,dy=tip.y-centre.y;
      const k=entry.text?Math.min(1,dx?entry.text.width/2/Math.abs(dx):Infinity,dy?entry.text.height/2/Math.abs(dy):Infinity):0;
      const tail=entry.tail={x:centre.x+dx*k,y:centre.y+dy*k};
      const length=Math.hypot(tip.x-tail.x,tip.y-tail.y),u=length?{x:(tip.x-tail.x)/length,y:(tip.y-tail.y)/length}:{x:0,y:1};
      const head=W*.012,half=head*.7,base={x:tip.x-u.x*head,y:tip.y-u.y*head};
      const a=local(tail),b=local(base),t=local(tip);
      if(cue.drawn!==undefined&&cue.drawn<1){
        const f=cue.drawn,edge={x:a.x+u.x*length*f,y:a.y+u.y*length*f},normal={x:-u.y,y:u.x},span=2*Math.hypot(W,H);
        const clip=shape('clipPath',{id:`mark-${cue.index}`});
        shape('polygon',{points:[[a.x+normal.x*span,a.y+normal.y*span],[edge.x+normal.x*span,edge.y+normal.y*span],
          [edge.x-normal.x*span,edge.y-normal.y*span],[a.x-normal.x*span,a.y-normal.y*span]].map(p=>p.join(',')).join(' ')},clip);
        strokes.setAttribute('clip-path',`url(#mark-${cue.index})`);
        if(f>0){entry.inside={x:tail.x+u.x*length*f/2,y:tail.y+u.y*length*f/2};
          entry.outside={x:tail.x+u.x*length*(1+f)/2,y:tail.y+u.y*length*(1+f)/2};}
      }
      if(length>head)shape('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:style.accent,'stroke-width':W*.0024},strokes);
      shape('polygon',{fill:style.accent,points:[[t.x,t.y],[b.x-u.y*half,b.y+u.x*half],[b.x+u.y*half,b.y-u.x*half]].map(p=>p.join(',')).join(' ')},strokes);
    }
    return drawn;
  }
  // A fresh pose ends with the whole page repainted. Chromium re-rasterizes only
  // what changed, and the antialiased edge of text just outside the changed area
  // keeps what an earlier pose left there, so without this a pose's pixels could
  // depend on the poses before it. Transitions and their proofs pose fresh;
  // every other frame is posed exactly as before.
  const frames=()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  async function repaint(){
    const background=document.body.style.background;
    document.body.style.background='#010203';await frames();
    document.body.style.background=background;await frames();
  }
  // The transition layer: above the picture (stage, annotations, overlays, code
  // panel), below the film's masthead and progress rule. A transition frame is
  // drawn in it entirely from captures of this page at the same instant, each an
  // image at its own pixel size and a whole-pixel offset, optionally translucent
  // and optionally cut to the columns [from, to), with a colour plate over them.
  // The live stage is hidden meanwhile: a visible WebGL canvas beneath the layer
  // would make Chromium composite the masthead separately and draw its text
  // without subpixel antialiasing, so it would not match the plain frames.
  const transition=document.querySelector('#transition'),viewport=document.querySelector('#viewport');
  function clearComposition(){
    transition.replaceChildren();
    document.body.classList.remove('in-transition');
    document.body.classList.remove('in-mark-blend');
    viewport.style.visibility='';
  }
  // Same-instant raster blend for faded marks. Chromium switches HTML glyphs
  // from subpixel to grayscale antialiasing under CSS opacity; blending captures
  // of the plain mark preserves the plain pixels and the authored opacity.
  async function composeMarkBlend(pictures){
    clearComposition();document.body.classList.add('in-mark-blend');
    const W=window.innerWidth,H=window.innerHeight,canvas=document.createElement('canvas');
    canvas.width=W;canvas.height=H;canvas.style.width=`${W}px`;canvas.style.height=`${H}px`;
    const ctx=canvas.getContext('2d',{willReadFrequently:true}),sum=new Float64Array(W*H*4);
    for(const {src,weight} of pictures){
      const img=new Image();img.src=src;await img.decode();ctx.clearRect(0,0,W,H);ctx.drawImage(img,0,0);
      const rgba=ctx.getImageData(0,0,W,H).data;
      for(let i=0;i<rgba.length;i++)sum[i]+=rgba[i]*weight;
    }
    const output=ctx.createImageData(W,H);
    for(let i=0;i<sum.length;i++)output.data[i]=Math.round(sum[i]);
    ctx.putImageData(output,0,0);transition.append(canvas);
    return {chrome:chrome()};
  }
  async function compose(request){
    clearComposition();
    document.body.classList.add('in-transition');
    document.body.classList.toggle('picture-only',Boolean(request.pictureOnly));
    viewport.style.visibility='hidden';
    for(const image of request.images){
      const img=new Image();img.src=image.src;await img.decode();
      const [from,to]=image.columns??[0,window.innerWidth];
      const box=document.createElement('div');
      Object.assign(box.style,{left:`${from}px`,width:`${to-from}px`,height:'100%',overflow:'hidden'});
      Object.assign(img.style,{position:'absolute',left:`${image.x-from}px`,top:'0'});
      if(image.opacity!==undefined)box.style.opacity=String(image.opacity);
      box.append(img);transition.append(box);
    }
    if(request.plate){
      const plate=document.createElement('div');
      Object.assign(plate.style,{left:'0',width:'100%',height:'100%',background:request.plate.color,opacity:String(request.plate.opacity)});
      transition.append(plate);
    }
    await repaint();
  }
  const rect=selector=>plain(document.querySelector(selector).getBoundingClientRect());
  const chrome=()=>['#brand','#series','#rule'].map(rect);
  window.film={viewer,apiVersion:viewer.apiVersion,
    // Preview's lens check: viewport positions of world points for the current pose.
    project:points=>points.map(p=>viewer.project(p)),
    // Draws a transition frame over the posed page; see compose.
    async compose(request){await compose(request);return {chrome:chrome()};},
    async composeMarkBlend(pictures){return composeMarkBlend(pictures);},
    async setFrame(frame){
    // Every frame starts from an empty transition layer and a visible stage.
    clearComposition();
    // Picture-only captures leave out the film's own chrome (design D6).
    document.body.classList.toggle('picture-only',Boolean(frame.pictureOnly));
    const split=Boolean(frame.code);
    if(document.body.classList.contains('with-code')!==split){
      document.body.classList.toggle('with-code',split);
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
    }
    // Highlight state follows the request, never the order frames are posed in:
    // restore a standing cue that differs, apply visibility, then the new cue.
    const wanted=frame.highlight?JSON.stringify(frame.highlight):null;
    if(wanted!==applied&&restore){const put=restore;restore=null;applied=null;put();}
    if(JSON.stringify(hidden)!==JSON.stringify(frame.hidden)){
      for(const path of hidden)viewer.setVisible(path,true);
      for(const path of frame.hidden)viewer.setVisible(path,false);
      hidden=frame.hidden;
    }
    if(wanted!==applied){
      const {paths,others,color}=frame.highlight;
      try{restore=viewer.highlight(paths,{color,others});}
      catch(error){throw new Error(`Viewer refused the highlight in shot ${frame.shotId}: ${error.message}`);}
      applied=wanted;
    }
    viewer.setTime(frame.time);
    // Validates, updates and renders synchronously. From API 28 up and field of
    // view are set on every frame; below it the call is exactly as before.
    if(viewer.apiVersion>=28)viewer.setView({camera:frame.view.camera,target:frame.view.target,up:frame.up,fov:frame.fov});
    else viewer.setView(frame.view);
    const overlays=document.querySelector('#overlays');overlays.replaceChildren();
    for(const cue of frame.overlays){const el=document.createElement('div');el.className='overlay '+cue.position;el.textContent=cue.text;overlays.append(el);}
    document.querySelector('#source-file').textContent=frame.code?`${frame.code.file} · L${frame.code.firstLine}–${frame.code.lastLine}`:'';
    // Markup is escaped by the server-side Python highlighter; source is never executed.
    document.querySelector('#source-code').innerHTML=frame.code?.html??'';
    document.querySelector('#source-cursor').style.visibility=frame.code?.cursor?'visible':'hidden';
    document.querySelector('#progress').style.width=`${frame.progress*100}%`;
    const annotations=drawAnnotations(frame);
    if(frame.fresh)await repaint();
    const view=viewer.view();
    return {camera:view.camera.toArray(),target:view.target.toArray(),navigation:viewer.navigation(),
      annotations,stage:plain(document.querySelector('#stage').getBoundingClientRect()),
      frame:{width:window.innerWidth,height:window.innerHeight},
      chrome:chrome(),
      ...(viewer.apiVersion>=28?{up:view.up.toArray(),fov:Number(view.fov)}:{})};
  }};
})().catch(error=>{window.filmError=String(error);});
