// How the spike's camera was chosen: mount the clocked export, read the
// viewer's own framing and where the crank and the result register stand on
// screen, and photograph candidate cameras.
//
//   node camera.mjs <bundle> <export dir> <out dir> '<json list of {camera,target,up?,fov?}>'
import {mkdir,writeFile} from 'node:fs/promises';
import {launch,serve,openPage,mountClocked as mount,join,twoFrames} from './harness.mjs';

const [bundle,exported,out,candidates='[]']=process.argv.slice(2);
await mkdir(out,{recursive:true});
const {browser,close}=await launch(),server=await serve(bundle,{model:exported});
try{
  const {page,errors}=await openPage(browser,server.origin,960,540);
  console.log('mount',await mount(page,'model',{time:0}));
  const read=await page.evaluate(()=>{
    const v=window.viewer.view(),arr=x=>x&&[x.x,x.y,x.z];
    const on=p=>window.viewer.partOnScreen(p);
    return {view:{camera:arr(v.camera),target:arr(v.target),up:arr(v.up),fov:v.fov},
      crank:on(['main_drive','crank']),result:on(['carriage','registers','result_register']),
      whole:on([]),selectors:on(['input_selectors','selectors'])};
  });
  console.log(JSON.stringify(read,null,1));
  await page.screenshot({path:join(out,'default.png')});
  for(const [i,view] of JSON.parse(candidates).entries()){
    const seen=await page.evaluate(async([view,wait])=>{window.viewer.setView(view);await eval(wait);
      return {crank:window.viewer.partOnScreen(['main_drive','crank']),
        result:window.viewer.partOnScreen(['carriage','registers','result_register'])};},[view,twoFrames]);
    await page.screenshot({path:join(out,`candidate-${i}.png`)});
    console.log(i,JSON.stringify(view),JSON.stringify(seen));
  }
  if(errors.length)console.log('page errors',errors);
}finally{await close();await server.close();}
