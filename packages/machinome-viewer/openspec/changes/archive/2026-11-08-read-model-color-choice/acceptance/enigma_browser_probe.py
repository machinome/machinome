"""Unchanged ordinary Enigma export, official inspector, public driver operations."""
import argparse
import base64
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import sys
from threading import Thread
import time
from urllib.parse import unquote, urlsplit

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGE = b'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:100%;height:100%}#host{width:100%;height:100%}
</style></head><body><div id="host"></div><script src="/viewer.js"></script></body></html>'''


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--oracle', type=Path)
    parser.add_argument('--document', type=Path)
    parser.add_argument('--mode', choices=['baseline', 'candidate'], default='candidate')
    parser.add_argument('--resume-row', type=int)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(HERE)
    if args.mode == 'baseline':
        oracle = {'document': str(args.document),
                  'document_sha256': 'f6ffa7958cf787d2d5b06f246a11d380ef4b3851f8585756a653650629ddbf6a',
                  'viewer_bundle_sha256': '2b4836154d730a0bb4c48e0226f87e03acf5ebb8ebe1015fdda4a79ad3ada90d',
                  'glass_sites': []}
    else:
        assert digest(args.oracle) == '157e4303f774867121414f0a9dbd9698edf3517e7118ea6a54f19e9561ddfd80'
        oracle = json.loads(args.oracle.read_text())
    document_path = Path(oracle['document'])
    build = document_path.parent
    assert digest(document_path) == oracle['document_sha256']
    assert digest(args.bundle) == oracle['viewer_bundle_sha256']
    if args.mode == 'candidate':
        assert digest(Path(oracle['geometry_review'])) == oracle['geometry_review_sha256']
    document = json.loads(document_path.read_text())
    assert document['version'] == (4 if args.mode == 'baseline' else 14)
    assert not document.get('clocked') and not document.get('program')
    sites = oracle['glass_sites']
    if args.mode == 'candidate':
        assert len(sites) == 26 and len({s['path'] for s in sites}) == 26
    nodes = {}

    def walk(node, path=()):
        nodes['.'.join(path)] = node
        for child in node.get('children', []):
            walk(child, (*path, child['name']))
    walk(document['root'])
    assets = {n['model'] for n in nodes.values() if n.get('model')}
    pins = {name: {'sha256': digest((build / name).resolve()),
                   'bytes': (build / name).stat().st_size} for name in sorted(assets)}
    for site in sites:
        assert nodes[site['path']].get('model')
    inputs = {'mode': args.mode, 'oracle_path': str(args.oracle), 'oracle_sha256': digest(args.oracle) if args.oracle else None,
              'document': str(document_path), 'document_sha256': digest(document_path),
              'document_bytes': document_path.stat().st_size, 'bundle': str(args.bundle),
              'bundle_sha256': digest(args.bundle), 'geometry_review_sha256': oracle.get('geometry_review_sha256'),
              'geometry_review': json.loads(Path(oracle['geometry_review']).read_text()) if oracle.get('geometry_review') else None,
              'assets': pins, 'nodes': len(nodes), 'bindings': len(document.get('bindings', [])),
              'glass_model_identity': {s['path']: {k: nodes[s['path']].get(k) for k in ('model', 'piece')} for s in sites},
              'python': sys.version}
    inputs['probe_source_sha256'] = {}
    for name in ('enigma_browser_probe.py', 'enigma_owned_browser.py'):
        shutil.copy2(HERE/name, output/name)
        inputs['probe_source_sha256'][name] = digest(output/name)
    project = build.parent
    inputs['project_source_sha256'] = {str(path.relative_to(project)): digest(path)
        for path in sorted((project/'simulation').glob('*.py'))}
    (output / 'inputs.json').write_text(json.dumps(inputs, indent=2) + '\n')
    if args.oracle:
        (output / 'oracle.json').write_bytes(args.oracle.read_bytes())

    def save(name, value):
        (output / name).write_text(json.dumps(value, indent=2) + '\n')

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            path = unquote(urlsplit(self.path).path)
            if path == '/':
                self.send_response(200); self.send_header('Content-Type', 'text/html')
                self.end_headers(); self.wfile.write(PAGE); return
            if path == '/favicon.ico':
                self.send_response(204); self.end_headers(); return
            return super().do_GET()

        def translate_path(self, request):
            path = unquote(urlsplit(request).path)
            if path == '/viewer.js':
                return str(args.bundle)
            target = (build / path.removeprefix('/build/')).resolve() if path.startswith('/build/') else build / '__missing__'
            return str(target if target.is_relative_to(build.resolve()) else build / '__missing__')

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(build)))
    thread = Thread(target=server.serve_forever, daemon=True); thread.start()
    errors, failed, http_errors, requests, completed = [], [], [], [], []
    states, screenshots = [], {}
    started = time.monotonic()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
            try:
                context = browser.new_context(viewport={'width': 1400, 'height': 1000}, device_scale_factor=1)
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('requestfailed', lambda request: failed.append({'url': request.url, 'error': request.failure}))
                page.on('response', lambda response: http_errors.append({'url': response.url, 'status': response.status}) if response.status >= 400 else None)
                page.on('request', lambda request: requests.append(request.url) if '.stl' in request.url else None)
                def finished(request):
                    if '.stl' in request.url:
                        completed.append(request.url)
                        save('network-progress.json', {'started':len(requests),'completed':len(completed),
                             'errors':failed,'http_errors':http_errors,'seconds':time.monotonic()-started})
                page.on('requestfinished', finished)
                page.goto(f'http://127.0.0.1:{server.server_port}/')
                mount = page.evaluate('''async continuation=>{
                  const started=performance.now();
                  window.inspector=await MachinomeViewer.mountInspector('#host','/build/viewer.json',{
                    animation:'inline',autoplay:false,sidebar:'collapsed'});
                  window.viewer=inspector.viewer;
                  const mounted=performance.now();
                  if(continuation)viewer.setRoot(['lamps']);
                  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
                  return {api:viewer.apiVersion,mount_ms:mounted-started,next_frame_ms:performance.now()-mounted,
                    driver_ids:Object.keys(viewer.drivers()),view:viewer.view(),run:viewer.run(),machine:viewer.machine()};
                }''', args.resume_row is not None)
                assert mount['api'] == 30 and mount['run'] is None and mount['machine'] is None
                save('mount.json', mount)
                print('mounted', json.dumps(mount), flush=True)
                dom = page.evaluate('''()=>({url:location.href,title:document.title,
                  canvas_count:document.querySelectorAll('canvas').length,
                  inspector_count:document.querySelectorAll('.machinome-inspector').length,
                  drivers:[...document.querySelectorAll('.driver-control input')].map(input=>({
                    label:input.getAttribute('aria-label'),type:input.type,value:input.value})),
                  navigator_rows:document.querySelectorAll('[role=treeitem]').length,
                  body_text:document.body.innerText.slice(0,3000)})''')
                save('normal-dom.json', dom)

                def readback(name):
                    result = page.evaluate('''()=>{
                      const start=performance.now();viewer.setView(viewer.view());
                      const drawn=performance.now();
                      const png=document.querySelector('canvas').toDataURL('image/png');
                      return {png,draw_ms:drawn-start,read_ms:performance.now()-drawn};
                    }''')
                    raw = base64.b64decode(result.pop('png').split(',',1)[1])
                    target = output / (name + '.png'); target.write_bytes(raw)
                    import io
                    image = Image.open(io.BytesIO(raw)).convert('RGB')
                    colors = image.getcolors(image.width*image.height)
                    dominant = max(count for count,_color in colors)
                    result.update({'path':str(target),'sha256':digest(target),
                                   'bytes':len(raw),'size':image.size,
                                   'non_dominant_pixels':image.width*image.height-dominant})
                    assert result['non_dominant_pixels'] > 1000, result
                    save(name+'-readback.json',result)
                    return target

                if args.resume_row is None:
                    readback('full-root-default')
                if args.mode == 'baseline':
                    save('lifecycle.json', {'mount':mount,'model_requests':len(requests),
                         'completed_model_requests':len(completed),'errors':errors,'failed_requests':failed,
                         'http_errors':http_errors,'seconds':time.monotonic()-started,'browser':browser.version})
                    assert not errors and not failed and not http_errors
                    assert len(completed)==len(requests)
                    assert digest(document_path)==oracle['document_sha256']
                    page.evaluate('inspector.dispose()')
                    context.close()
                    print('baseline-complete',len(completed),'model requests',flush=True)
                    return
                page.evaluate("viewer.setRoot(['lamps'])")
                canvas = page.locator('canvas')
                canvas_box = canvas.bounding_box()
                baseline_requests = len(requests)
                baseline_inventory = page.evaluate('''()=>{
                  const rows=[];const visit=n=>{rows.push([n.path,n.model]);n.children.forEach(visit)};
                  visit(viewer.assembly());return rows;
                }''')
                paths = [s['path'].split('.') for s in sites]
                page.evaluate('''paths=>{
                  window.glassPaths=paths;
                  window.readColors=()=>{const root=viewer.assembly();return glassPaths.map(path=>{
                    let node=root;for(const name of path)node=node.children.find(c=>c.name===name);
                    return node.color;
                  })};
                }''', paths)
                defaults = {name: value['default'] for name, value in document['drivers'].items()}

                def apply(bank):
                    return page.evaluate('''async bank=>{
                      const start=performance.now(),changed=[];
                      for(const [id,value]of Object.entries(bank))if(viewer.driver(id)!==value){
                        const at=performance.now();viewer.setDriver(id,value);
                        changed.push({id,value,control_ms:performance.now()-at});
                      }
                      const admitted=performance.now();
                      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
                      return {changed,control_total_ms:admitted-start,next_frame_ms:performance.now()-admitted,
                        total_ms:performance.now()-start,colors:readColors(),
                        drivers:Object.fromEntries(Object.keys(viewer.drivers()).map(id=>[id,viewer.driver(id)]))};
                    }''', bank)

                def shot(name):
                    if args.resume_row is not None:
                        return
                    target = readback(name)
                    screenshots[name] = str(target)

                initial = apply(defaults)
                shot('focused-default-dark')
                first_lit = None
                first_lit = oracle['rows'][0]
                for index, row in enumerate(oracle['rows'][args.resume_row or 0:], start=args.resume_row or 0):
                    result = apply(row['drivers'])
                    assert result['colors'] == row['expected_colors_by_path'], (row['case'], result['colors'], row['expected_colors_by_path'])
                    assert result['drivers'] == row['drivers'], (row['case'], result['drivers'])
                    assert len(requests) == baseline_requests, (row['case'], 'asset refetch')
                    states.append({'case': row['case'], 'oracle_row_index':index,
                                   'complete_input_bank_supplied':len(row['drivers'])==len(document['drivers']),
                                   'expected_vector': row['expected_vector_by_path'],
                                   'expected_colors': row['expected_colors_by_path'], **result})
                    if index == 0:
                        shot('first-held-lit'); first_lit = row
                    elif index == 1:
                        shot('first-released-dark')
                    save('states.json', states)
                    print('state', row['case'], result['total_ms'], flush=True)
                if args.resume_row is not None:
                    final_inventory = page.evaluate('''()=>{
                      const rows=[];const visit=n=>{rows.push([n.path,n.model]);n.children.forEach(visit)};
                      visit(viewer.assembly());return rows;
                    }''')
                    assert final_inventory == baseline_inventory and len(requests)==baseline_requests
                    assert not errors and not failed and not http_errors
                    save('lifecycle.json',{'continuation_start_row':args.resume_row,
                         'completed_cases':[r['case'] for r in states],
                         'complete_first_input_bank':states[0]['drivers'],
                         'same_public_body_inventory':True,'model_requests_at_mount':baseline_requests,
                         'model_requests_after_states':len(requests),'completed_model_requests':len(completed),
                         'browser':browser.version,'errors':errors,'failed_requests':failed,
                         'http_errors':http_errors,'seconds':time.monotonic()-started,
                         'readbacks_executed':0,'screen_queries_executed':0})
                    assert digest(document_path)==oracle['document_sha256']
                    assert all(digest(build/name)==pin['sha256'] for name,pin in pins.items())
                    assert page.evaluate('inspector.dispose();document.querySelectorAll("canvas").length')==0
                    context.close()
                    print('continuation-complete',len(states),'oracle states',flush=True)
                    return
                reset = apply(defaults)
                assert reset['colors'] == initial['colors']
                shot('reset-default-dark')
                # Explicit public-driver save/restore/replay for this posed model.
                restored = apply(first_lit['drivers'])
                assert restored['colors'] == first_lit['expected_colors_by_path']
                shot('restored-first-held-lit')
                apply(defaults)
                replay = apply(first_lit['drivers'])
                assert replay['colors'] == restored['colors']
                shot('replayed-first-held-lit')
                # All representative images above precede bounded screen queries.
                selected = first_lit['expected_vector_by_path'].index(1)
                point_queries = []
                for index in (selected, (selected + 1) % len(paths)):
                    at = time.monotonic()
                    value = page.evaluate('path=>viewer.partOnScreen(path)', paths[index])
                    point_queries.append({'path': sites[index]['path'], 'screen': value, 'seconds': time.monotonic() - at})
                final_inventory = page.evaluate('''()=>{
                  const rows=[];const visit=n=>{rows.push([n.path,n.model]);n.children.forEach(visit)};
                  visit(viewer.assembly());return rows;
                }''')
                assert final_inventory == baseline_inventory and len(requests) == baseline_requests
                save('lifecycle.json', {'initial': initial, 'reset': reset, 'restored': restored, 'replayed': replay,
                      'canvas_box': canvas_box, 'queries': point_queries, 'same_public_body_inventory': True,
                      'model_requests_at_mount': baseline_requests, 'model_requests_after_states': len(requests),
                      'completed_model_requests':len(completed),
                      'requests': requests, 'browser': browser.version, 'errors': errors, 'failed_requests': failed,
                      'http_errors': http_errors, 'seconds': time.monotonic() - started})
                assert not errors and not failed and not http_errors
                # Crop the previously captured images at a public screen rectangle.
                screen = point_queries[0]['screen']
                assert screen and screen['point'] is not None, point_queries[0]
                rect = screen['rect']
                bounds = [round(rect['x'] - canvas_box['x']), round(rect['y'] - canvas_box['y']),
                          round(rect['x'] + rect['width'] - canvas_box['x']),
                          round(rect['y'] + rect['height'] - canvas_box['y'])]
                dark = Image.open(screenshots['focused-default-dark']).convert('RGB')
                lit = Image.open(screenshots['first-held-lit']).convert('RGB')
                released = Image.open(screenshots['first-released-dark']).convert('RGB')
                bounds = (max(0,bounds[0]),max(0,bounds[1]),min(dark.width,bounds[2]),min(dark.height,bounds[3]))
                difference = ImageChops.difference(dark.crop(bounds), lit.crop(bounds))
                changed = sum(max(pixel)>4 for pixel in difference.getdata())
                assert changed > 5, ('no visible selected-glass color difference', bounds, changed)
                for name, image in [('glass-dark',dark),('glass-lit',lit),('glass-released',released)]:
                    image.crop(bounds).save(output/(name+'.png'))
                save('pixels.json', {'representative_glass': sites[selected], 'bounds': bounds,
                     'changed_pixels_above_4': changed, 'dark_lit_bounds': difference.getbbox(),
                     'dark_released_equal': dark.crop(bounds).tobytes()==released.crop(bounds).tobytes(),
                     'screenshots': {Path(value).name:digest(Path(value)) for value in screenshots.values()}})
                assert digest(document_path) == oracle['document_sha256']
                assert all(digest(build / name) == pin['sha256'] for name,pin in pins.items())
                print('complete', len(states), 'oracle states', flush=True)
                inspector_closed = page.evaluate('inspector.dispose();document.querySelectorAll("canvas").length')
                assert inspector_closed == 0
                context.close()
            finally:
                browser.close()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


if __name__ == '__main__':
    main()
