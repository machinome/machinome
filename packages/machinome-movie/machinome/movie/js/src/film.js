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
  const viewer=await MachinomeViewer.mount('#stage','/model/manifest.json',{
    renderMode:'on-demand',
    animation:'external',autoplay:false,driverControls:'none',partControls:'none',
    time:cfg.initial.time,view:cfg.initial.view,up:cfg.initial.up,fov:cfg.initial.fov,
  });
  if(viewer.apiVersion<21||typeof viewer.setView!=='function')throw new Error('Viewer API 21 with setView is required');
  await document.fonts.ready;
  let hidden=[];
  window.film={viewer,apiVersion:viewer.apiVersion,setFrame(frame){
    if(JSON.stringify(hidden)!==JSON.stringify(frame.hidden)){
      for(const path of hidden)viewer.setVisible(path,true);
      for(const path of frame.hidden)viewer.setVisible(path,false);
      hidden=frame.hidden;
    }
    viewer.setTime(frame.time);
    viewer.setView(frame.view); // Validates, updates and renders synchronously.
    const overlays=document.querySelector('#overlays');overlays.replaceChildren();
    for(const cue of frame.overlays){const el=document.createElement('div');el.className='overlay '+cue.position;el.textContent=cue.text;overlays.append(el);}
    document.querySelector('#caption span').textContent=frame.caption;
    document.querySelector('#caption').hidden=!frame.caption;
    document.querySelector('#progress').style.width=`${frame.progress*100}%`;
    const view=viewer.view();
    return {camera:view.camera.toArray(),target:view.target.toArray(),navigation:viewer.navigation()};
  }};
})().catch(error=>{window.filmError=String(error);});
