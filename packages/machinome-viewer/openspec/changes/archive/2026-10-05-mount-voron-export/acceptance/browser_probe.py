import argparse
import asyncio
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

EXPORT = Path('/mnt/data/machinome-projects/3D-Printers/Voron-2/_build_resume_main_browser_export')
SCRATCH = Path(__file__).parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def worker(args):
    from playwright.async_api import async_playwright
    started = time.monotonic()
    result = dict(mode=args.mode, export=str(EXPORT), manifest_sha256=sha(EXPORT/'manifest.json'),
        page_sha256=sha(EXPORT/'index.html'), original_bundle_sha256=sha(EXPORT/'machinome-viewer.js'),
        supplied_bundle=str(args.bundle) if args.bundle else None,
        supplied_bundle_sha256=sha(Path(args.bundle)) if args.bundle else None,
        requests=[], responses=[], failed_requests=[], page_errors=[], console=[])
    output = SCRATCH/f'{args.mode}.json'
    def save():
        result['elapsed_seconds'] = time.monotonic()-started
        output.write_text(json.dumps(result, indent=2)+'\n')
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(EXPORT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    async def observe():
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True, args=['--use-gl=angle',
                '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
            result['browser_version'] = browser.version
            try:
                page = await browser.new_page(viewport=dict(width=1400, height=1100), service_workers='block')
                pending=set()
                result['peak_pending_models']=0
                def requested(request):
                    result['requests'].append(request.url)
                    if '/models/' in request.url:
                        pending.add(request.url)
                        result['peak_pending_models']=max(result['peak_pending_models'],len(pending))
                page.on('request', requested)
                page.on('requestfinished',lambda request: pending.discard(request.url))
                def response(row):
                    result['responses'].append(dict(url=row.url,status=row.status,seconds=time.monotonic()-started))
                    if len(result['responses'])<=4 or len(result['responses'])%100==0:
                        save(); print('response',len(result['responses']),row.status,row.url,flush=True)
                page.on('response', response)
                page.on('requestfailed', lambda request: result['failed_requests'].append(dict(url=request.url,error=request.failure)))
                page.on('pageerror', lambda error: result['page_errors'].append(str(error)))
                page.on('console', lambda message: result['console'].append(dict(type=message.type,text=message.text)))
                if args.bundle:
                    await page.route('**/machinome-viewer.js', lambda route: route.fulfill(path=args.bundle,content_type='application/javascript'))
                result['url']=f'http://127.0.0.1:{server.server_port}/'
                save()
                await page.goto(result['url'], wait_until='commit',timeout=15000)
                # The portable page remains byte-for-byte original. This probe
                # observes readiness, never treats a canvas alone as completion.
                await asyncio.sleep(20)
                result['body_text']=await asyncio.wait_for(page.locator('body').inner_text(timeout=15000),timeout=20)
                result['canvas_count']=await page.locator('canvas').count()
                await page.screenshot(path=str(SCRATCH/f'{args.mode}-rest.png'),timeout=90000)
                result['screenshot']=str(SCRATCH/f'{args.mode}-rest.png')
                result['status']='responsive portable page; further mount evidence required'
                if args.mode.startswith('queued'):
                    if result['failed_requests'] or result['page_errors'] or any(r['status']>=400 for r in result['responses']):
                        raise RuntimeError('Browser resource/page errors prevent mount acceptance')
                    if result['canvas_count'] != 1 or 'machinome-viewer:' in result['body_text']:
                        raise RuntimeError('Absent mounted portable printer')
                    if sum('/models/' in r['url'] for r in result['responses']) != 1565:
                        raise RuntimeError('Incomplete full printer resources')
                    result['status']='complete resources and portable canvas; host bounds/pose gate remains'
            finally:
                try: await asyncio.wait_for(browser.close(),timeout=5)
                except asyncio.TimeoutError: result['graceful_close_timed_out']=True
    try:
        asyncio.run(asyncio.wait_for(observe(),timeout=205))
    except Exception as error:
        result['probe_error']=f'{type(error).__name__}: {error}'
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2);save()
    print(json.dumps({key:result[key] for key in ('mode','elapsed_seconds','probe_error') if key in result}),flush=True)
    if args.mode.startswith('queued') and result.get('probe_error'):raise SystemExit(1)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('mode');parser.add_argument('--bundle');parser.add_argument('--worker',action='store_true')
    args=parser.parse_args()
    if args.worker: worker(args);return
    log=SCRATCH/f'{args.mode}.log'
    command=[sys.executable,__file__,args.mode,'--worker']
    if args.bundle:command+=['--bundle',args.bundle]
    with log.open('w') as stream:
        process=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        group=process.pid
        try:
            process.wait(timeout=220)
        except subprocess.TimeoutExpired:
            os.killpg(group,signal.SIGTERM)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(group,signal.SIGKILL);process.wait(timeout=5)
        finally:
            try:os.killpg(group,signal.SIGKILL)
            except ProcessLookupError:pass
    remaining=subprocess.run(['ps','-eo','pid,pgid,args'],capture_output=True,text=True).stdout
    survivors=[line for line in remaining.splitlines()[1:] if line.split()[1]==str(group)]
    (SCRATCH/f'{args.mode}-cleanup.json').write_text(json.dumps(dict(group=group,returncode=process.returncode,survivors=survivors),indent=2)+'\n')
    print(dict(log=str(log),group=group,returncode=process.returncode,survivors=survivors),flush=True)
    if survivors:raise SystemExit(2)
    if process.returncode:raise SystemExit(1)

if __name__=='__main__':main()
