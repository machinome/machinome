"""Read-only predecessor bundle against the unchanged standard producer fixture."""
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import sys
import tempfile
from threading import Thread
from playwright.sync_api import sync_playwright

bundle, fixture, output = map(Path, sys.argv[1:])
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    shutil.copy2(bundle, root / 'viewer.js')
    shutil.copytree(fixture, root / 'fixture')
    (root / 'index.html').write_text('<div id="host" style="width:800px;height:600px"></div><script src="viewer.js"></script>')
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=directory))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=['--no-sandbox', '--use-angle=swiftshader'])
            try:
                page = browser.new_page()
                assets = []
                page.on('request', lambda request: assets.append(request.url)
                        if request.url.endswith('.stl') else None)
                page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
                result = page.evaluate('''async()=>{
                  let error=null;try{await MachinomeViewer.mount('#host','fixture/manifest.json',{})}
                  catch(e){error=e.message}
                  return {api:MachinomeViewer.apiVersion,error,canvases:document.querySelectorAll('canvas').length};
                }''')
                result['model_requests'] = assets
                result['chromium_version'] = browser.version
            finally:
                browser.close()
    finally:
        server.shutdown(); server.server_close(); thread.join()
receipt = {'bundle_sha256': sha256(bundle.read_bytes()).hexdigest(),
           'document_sha256': sha256((fixture / 'manifest.json').read_bytes()).hexdigest(),
           'result': result}
output.write_text(json.dumps(receipt, indent=2) + '\n')
assert result['api'] == 29 and 'document version 14' in result['error'], receipt
assert result['model_requests'] == [], receipt
