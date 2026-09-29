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
    const shape=(name,attributes)=>{const el=document.createElementNS(svgNS,name);for(const [k,v] of Object.entries(attributes))el.setAttribute(k,v);svg.append(el);};
    const local=p=>({x:p.x-origin.left,y:p.y-origin.top});
    const drawn=[];
    for(const cue of cues){
      let found;
      try{found=resolve(cue.target);}catch(error){throw new Error(`Viewer refused annotation #${cue.index} in shot ${frame.shotId}: ${error.message}`);}
      const entry={index:cue.index,kind:cue.kind,anchor:found.anchor,rect:found.rect,text:null,tail:null};drawn.push(entry);
      if(!entry.anchor)continue;
      const inset=cue.safeInset,safe={x:W*inset,y:H*inset,width:W*(1-2*inset),height:H*(1-2*inset)};
      const centre=cue.kind==='arrow'?{x:safe.x+cue.place[0]*safe.width,y:safe.y+cue.place[1]*safe.height}
        :{x:entry.anchor.x+cue.offset[0]*safe.width,y:entry.anchor.y+cue.offset[1]*safe.height};
      if(cue.text!==undefined){
        const el=document.createElement('div');el.className='annotation-text';el.textContent=cue.text;layer.append(el);
        const size=el.getBoundingClientRect(),at=local({x:centre.x-size.width/2,y:centre.y-size.height/2});
        el.style.left=`${at.x}px`;el.style.top=`${at.y}px`;entry.text=plain(el.getBoundingClientRect());
      }
      if(cue.kind!=='arrow')continue;
      // The shaft leaves the text box at the edge nearest the tip; the tip touches the part.
      const tip=entry.anchor,dx=tip.x-centre.x,dy=tip.y-centre.y;
      const k=entry.text?Math.min(1,dx?entry.text.width/2/Math.abs(dx):Infinity,dy?entry.text.height/2/Math.abs(dy):Infinity):0;
      const tail=entry.tail={x:centre.x+dx*k,y:centre.y+dy*k};
      const length=Math.hypot(tip.x-tail.x,tip.y-tail.y),u=length?{x:(tip.x-tail.x)/length,y:(tip.y-tail.y)/length}:{x:0,y:1};
      const head=W*.012,half=head*.7,base={x:tip.x-u.x*head,y:tip.y-u.y*head};
      const a=local(tail),b=local(base),t=local(tip);
      if(length>head)shape('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:style.accent,'stroke-width':W*.0024});
      shape('polygon',{fill:style.accent,points:[[t.x,t.y],[b.x-u.y*half,b.y+u.x*half],[b.x+u.y*half,b.y-u.x*half]].map(p=>p.join(',')).join(' ')});
    }
    return drawn;
  }
  window.film={viewer,apiVersion:viewer.apiVersion,async setFrame(frame){
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
    viewer.setView(frame.view); // Validates, updates and renders synchronously.
    const overlays=document.querySelector('#overlays');overlays.replaceChildren();
    for(const cue of frame.overlays){const el=document.createElement('div');el.className='overlay '+cue.position;el.textContent=cue.text;overlays.append(el);}
    document.querySelector('#source-file').textContent=frame.code?`${frame.code.file} · L${frame.code.firstLine}–${frame.code.lastLine}`:'';
    // Markup is escaped by the server-side Python highlighter; source is never executed.
    document.querySelector('#source-code').innerHTML=frame.code?.html??'';
    document.querySelector('#source-cursor').style.visibility=frame.code?.cursor?'visible':'hidden';
    document.querySelector('#progress').style.width=`${frame.progress*100}%`;
    const annotations=drawAnnotations(frame);
    const view=viewer.view();
    return {camera:view.camera.toArray(),target:view.target.toArray(),navigation:viewer.navigation(),
      annotations,stage:plain(document.querySelector('#stage').getBoundingClientRect()),
      frame:{width:window.innerWidth,height:window.innerHeight}};
  }};
})().catch(error=>{window.filmError=String(error);});
