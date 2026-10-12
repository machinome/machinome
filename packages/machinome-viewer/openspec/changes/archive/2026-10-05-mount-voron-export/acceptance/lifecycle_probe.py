import asyncio
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import sys
from playwright.async_api import async_playwright

SCRATCH=Path(__file__).parent
FIXTURE=Path('/home/asa/devel/machinome/machinome-viewer/WTs/mount-voron-export/tests/fixtures/pascaline')
async def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(FIXTURE)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        async with async_playwright() as pw:
            browser=await pw.chromium.launch(args=['--use-angle=swiftshader','--enable-unsafe-swiftshader'])
            try:
                page=await browser.new_page(viewport={'width':640,'height':480})
                await page.route('**/_host',lambda route:route.fulfill(body='<html><div id="host" style="width:640px;height:480px"></div><script src="/_probe.js"></script></html>',content_type='text/html'))
                mode='red' if '--red' in sys.argv else 'diagnostic'
                await page.route('**/_probe.js',lambda route:route.fulfill(path=str(SCRATCH/f'lifecycle-{mode}.js')))
                await page.goto(f'http://127.0.0.1:{server.server_port}/_host')
                result=await page.evaluate('''async()=>{
                  const originalStart=LifecycleProbe.RunRuntime.start;
                  const originalDispose=LifecycleProbe.RunRuntime.prototype.dispose;
                  const originalUpdate=LifecycleProbe.WidgetTree.prototype.update;
                  let starts=0,disposals=0,disposed=false,postDisposeUpdates=0;
                  LifecycleProbe.RunRuntime.prototype.dispose=function(){disposals++;return originalDispose.call(this)};
                  LifecycleProbe.WidgetTree.prototype.update=function(...args){if(disposed)postDisposeUpdates++;return originalUpdate.apply(this,args)};
                  LifecycleProbe.RunRuntime.start=function(document,options){
                    starts++;
                    const runtime=originalStart(document,{...options,workerFactory:()=>{throw Error('controlled in-thread test')}});
                    if(starts>1){const actualReady=runtime.ready;
                      Object.defineProperty(runtime,'ready',{value:new Promise((resolve,reject)=>{
                        actualReady.then(()=>{window.releaseReady=resolve;window.readyBlocked=true},reject);
                      })});}
                    return runtime;
                  };
                  window.viewer=await LifecycleProbe.mount('#host','/viewer.json',{autoplay:false,driverControls:'none',partControls:'none'});
                  const reload=viewer.reload();
                  while(!window.readyBlocked)await new Promise(resolve=>setTimeout(resolve,5));
                  disposed=true;viewer.dispose();window.releaseReady();await reload;
                  return {starts,disposals,postDisposeUpdates,remainingCanvas:document.querySelectorAll('canvas').length};
                }''')
                (SCRATCH/f'lifecycle-{mode}-probe.json').write_text(json.dumps(result,indent=2)+'\n')
                print(json.dumps(result),flush=True)
                assert result==dict(starts=2,disposals=2,postDisposeUpdates=0,remainingCanvas=0),result
            finally:await browser.close()
    finally:server.shutdown();server.server_close();thread.join(timeout=2)
asyncio.run(asyncio.wait_for(main(),timeout=90))
