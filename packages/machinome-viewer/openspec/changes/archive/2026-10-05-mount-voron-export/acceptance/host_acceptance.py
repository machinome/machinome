import ast
import asyncio
import hashlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import operator
import sys
from pathlib import Path
import threading
import time
import numpy as np
from molejo import Shape
from playwright.async_api import async_playwright

ROOT=Path('/mnt/data/machinome-projects/3D-Printers/Voron-2')
EXPORT=ROOT/'_build_resume_main_browser_export'
SCRATCH=Path(__file__).parent
document=json.loads((EXPORT/'manifest.json').read_text())
tree=ast.parse((ROOT/'simulation/viewer_pose.py').read_text())
class_ast=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Expressions')
# The project's generic Python helper used Python's floor-modulo. The
# published expression language is OpenSCAD: a native openscad echo probe
# independently confirms remainder with the dividend's sign. Adapt only
# this scratch oracle, preserving the original mismatch as evidence.
for node in ast.walk(class_ast):
    if isinstance(node,ast.Dict):
        for i,key in enumerate(node.keys):
            if isinstance(key,ast.Attribute) and isinstance(key.value,ast.Name) and key.value.id=='ast' and key.attr=='Mod':
                node.values[i]=ast.Attribute(value=ast.Name(id='math',ctx=ast.Load()),attr='fmod',ctx=ast.Load())
ast.fix_missing_locations(class_ast)
namespace=dict(ast=ast,math=math,operator=operator)
exec(compile(ast.Module(body=[class_ast],type_ignores=[]),'independent-project-expression-oracle','exec'),namespace)
Expressions=namespace['Expressions']
sys.setrecursionlimit(20000)
nodes={}
def index(node,path):
    nodes['/'.join(path)]=node
    for child in node.get('children',[]):index(child,path+[child['name']])
index(document['root'],[])
belts=[p for p,n in nodes.items() if 'flexible' in n and ('belt_a/' in p or 'belt_b/' in p or 'front_left_belt/' in p)]
rigids=['bed','gantry','gantry/crossbeam','gantry/crossbeam/head','drives/chain/link_0','drives/chain/link_15']
selected=rigids+belts

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path=='/_host':
            body=b'<!doctype html><html><style>html,body,#host{margin:0;width:100%;height:100%}</style><div id="host"></div><script src="/_diagnostic.js"></script></html>'
            self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        elif self.path=='/_diagnostic.js':
            body=(SCRATCH/'host-diagnostic.js').read_bytes();self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        else:super().do_GET()

def oracle(values):
    evaluate=Expressions(document);evaluate.values.update(values)
    world={}
    def visit(node,path,parent):
        matrix=np.eye(4)
        for op in node['operations']:
            step=np.eye(4)
            if op[0]=='t':step[:3,3]=[evaluate(v) for v in op[1]]
            else:
                angle=evaluate(op[1])*math.pi/180
                axis=np.array(op[2],dtype=float);axis/=np.linalg.norm(axis);x,y,z=axis
                skew=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
                step[:3,:3]=math.cos(angle)*np.eye(3)+(1-math.cos(angle))*np.outer(axis,axis)+math.sin(angle)*skew
            matrix=step@matrix
        world[path]=parent@matrix
        for child in node.get('children',[]):visit(child,path+'/'+child['name'] if path else child['name'],world[path])
    visit(document['root'],'',np.eye(4))
    flexible={}
    for path in belts:
        payload=nodes[path]['flexible'];params={k:evaluate(v) for k,v in payload['params'].items()}
        mesh=Shape.from_dict(payload['spec']).evaluate(**params)
        flexible[path]=(np.array(mesh.vertices,dtype=np.float32),np.array(mesh.faces,dtype=np.uint32))
    return world,flexible

async def main():
    started=time.monotonic();result=dict(status='not accepted',selected_paths=selected,belts=belts,
        manifest_sha256=hashlib.sha256((EXPORT/'manifest.json').read_bytes()).hexdigest(),
        diagnostic_bundle_sha256=hashlib.sha256((SCRATCH/'host-diagnostic.js').read_bytes()).hexdigest(),
        requests=[],errors=[],readings=[])
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(EXPORT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        async with async_playwright() as pw:
            browser=await pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader'])
            try:
                page=await browser.new_page(viewport=dict(width=1100,height=850))
                page.on('response',lambda r:result['requests'].append(dict(url=r.url,status=r.status)))
                page.on('pageerror',lambda e:result['errors'].append(str(e)))
                page.on('requestfailed',lambda r:result['errors'].append(dict(url=r.url,error=r.failure)))
                await page.goto(f'http://127.0.0.1:{server.server_port}/_host')
                mounted=await asyncio.wait_for(page.evaluate('''async () => {
                  const oldUpdate=HostProbe.WidgetTree.prototype.update;
                  HostProbe.WidgetTree.prototype.update=function(...args){if(!this.group.parent||this.group.parent.isScene)window.actualTree=this;return oldUpdate.apply(this,args)};
                  window.requestAnimationFrame=callback=>{window.frame=callback;return 99};
                  window.cancelAnimationFrame=()=>{};
                  const realNow=performance.now.bind(performance);window.clockOffset=0;
                  performance.now=()=>realNow()+window.clockOffset;
                  window.viewer=await HostProbe.mount('#host','/manifest.json',{autoplay:false,driverControls:'none',partControls:'none'});
                  window.frame(performance.now());
                  const count=n=>1+n.children.reduce((sum,c)=>sum+count(c),0);
                  const models=n=>(n.model?1:0)+n.children.reduce((sum,c)=>sum+models(c),0);
                  return {nodes:count(viewer.assembly()),models:models(viewer.assembly()),defaults:Object.fromEntries(Object.keys(viewer.drivers()).map(k=>[k,viewer.driver(k)]))};
                }'''),timeout=80)
                result['mounted']=mounted
                if mounted['nodes']!=1636 or mounted['models']!=1565:raise AssertionError('Incomplete full assembly')
                expected_defaults={k:v['default'] for k,v in document['drivers'].items()}
                if mounted['defaults']!=expected_defaults:raise AssertionError('Default readbacks changed')
                for pose in ['rest','Home','Center','Present','restored']:
                    if pose in document['instructions']:
                        await page.evaluate('''async name=>{const request=viewer.trigger(name);clockOffset+=30000;frame(performance.now());await request.done}''',pose)
                    elif pose=='restored':
                        await page.evaluate('''defaults=>{for(const [key,value] of Object.entries(defaults))viewer.setDriver(key,value);frame(performance.now())}''',expected_defaults)
                    reading=await page.evaluate('''paths=>{
                      actualTree.group.updateMatrixWorld(true);
                      const box=new HostProbe.THREE.Box3().setFromObject(actualTree.group);
                      return {drivers:Object.fromEntries(Object.keys(viewer.drivers()).map(k=>[k,viewer.driver(k)])),
                        bounds:{min:box.min.toArray(),max:box.max.toArray()},
                        nodes:paths.map(path=>{const node=actualTree.requirePath(path.split('/'));
                          const mesh=node.group.children.find(x=>x.isMesh);
                          const drivers=Object.fromEntries(Object.keys(viewer.drivers()).map(k=>[k,viewer.driver(k)]));
                          const params=node.flexible?HostProbe.withExpressions(()=>Object.fromEntries(node.flexible.params.map(([key,expr])=>[key,HostProbe.evalExpr(expr,{time:0,drivers,bindings:node.bindings.roots()})]))):null;
                          return {path,matrix:node.group.matrixWorld.toArray(),params,vertices:node.flexible?Array.from(mesh.geometry.attributes.position.array):null,faces:node.flexible?Array.from(mesh.geometry.index.array):null}})};
                    }''',selected)
                    expected=document['instructions'][pose]['targets'] if pose in document['instructions'] else expected_defaults
                    if reading['drivers']!=expected:raise AssertionError(f'{pose} readbacks changed')
                    if not np.isfinite(reading['bounds']['min']+reading['bounds']['max']).all():raise AssertionError('Nonfinite assembly bounds')
                    matrices,flex=oracle(expected)
                    differences=[]
                    for row in reading['nodes']:
                        actual=np.array(row['matrix']).reshape((4,4),order='F')
                        difference=float(np.max(np.abs(actual-matrices[row['path']])))
                        if difference>1e-8:raise AssertionError(f'Matrix differs: {row["path"]} {difference}')
                        if row['vertices'] is not None:
                            vertices=np.array(row.pop('vertices')).reshape((-1,3))
                            reference,faces=flex[row['path']]
                            if vertices.shape!=reference.shape:raise AssertionError('Flexible topology differs')
                            actual_faces=np.array(row.pop('faces'),dtype=np.uint32).reshape((-1,3))
                            if not np.array_equal(actual_faces,faces):raise AssertionError(f'Flexible indices differ: {row["path"]}')
                            delta=float(np.max(np.abs(vertices-reference)))
                            if delta>0.0001:
                                evaluate=Expressions(document);evaluate.values.update(expected)
                                params={k:evaluate(v) for k,v in nodes[row['path']]['flexible']['params'].items()}
                                result['flexible_failure']=dict(pose=pose,path=row['path'],delta=delta,actual_params=row['params'],reference_params=params,actual=vertices.tolist(),reference=reference.tolist())
                                raise AssertionError(f'Flexible vertices differ: {row["path"]} {delta}')
                            differences.append(dict(path=row['path'],matrix_difference=difference,vertex_difference=delta,vertices=len(vertices),faces=len(faces),indices_equal=True))
                        else:differences.append(dict(path=row['path'],matrix_difference=difference))
                    result['readings'].append(dict(pose=pose,drivers=reading['drivers'],bounds=reading['bounds'],comparisons=differences))
                    (SCRATCH/'host-acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
                    if pose in ('rest','Present'):
                        await page.screenshot(path=str(SCRATCH/f'host-{pose}.png'),timeout=60000)
                    if pose=='Present':
                        await page.evaluate("viewer.setVisible(['enclosure'],false);viewer.setView(viewer.view())")
                        await page.screenshot(path=str(SCRATCH/'host-Present-interior.png'),timeout=60000)
                        await page.evaluate("viewer.setVisible(['enclosure'],true)")
                    print('accepted pose',pose,flush=True)
                reloaded=await page.evaluate('''async()=>{
                  await viewer.reload();frame(performance.now());actualTree.group.updateMatrixWorld(true);
                  const count=n=>1+n.children.reduce((sum,c)=>sum+count(c),0);
                  const models=n=>(n.model?1:0)+n.children.reduce((sum,c)=>sum+models(c),0);
                  const box=new HostProbe.THREE.Box3().setFromObject(actualTree.group);
                  return {nodes:count(viewer.assembly()),models:models(viewer.assembly()),
                    defaults:Object.fromEntries(Object.keys(viewer.drivers()).map(k=>[k,viewer.driver(k)])),
                    bounds:{min:box.min.toArray(),max:box.max.toArray()}};
                }''')
                result['reload_reading']=reloaded
                if reloaded['nodes']!=1636 or reloaded['models']!=1565 or reloaded['defaults']!=expected_defaults:raise AssertionError('Reload did not restore full assembly/defaults')
                if not np.isfinite(reloaded['bounds']['min']+reloaded['bounds']['max']).all():raise AssertionError('Reload bounds nonfinite')
                result['reload_completed']=True
                await page.evaluate('viewer.dispose()')
                if result['errors'] or any(r['status']>=400 for r in result['requests']):raise AssertionError('Browser errors')
                result['status']='full actual host assembly, five poses, independent matrices/belts and reload accepted'
            finally:
                try:await asyncio.wait_for(browser.close(),timeout=5)
                except asyncio.TimeoutError:result['graceful_close_timed_out']=True
    except Exception as error:
        result['error']=f'{type(error).__name__}: {error}';raise
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)
        result['elapsed_seconds']=time.monotonic()-started
        (SCRATCH/'host-acceptance.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':asyncio.run(asyncio.wait_for(main(),timeout=210))
