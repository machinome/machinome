"""Compare paused initial-frame screenshot latency without changing run state."""

import argparse
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    assert not args.report.exists(), 'preserve earlier reports'
    build, bundle = args.build.resolve(), args.bundle.resolve()
    document = json.loads((build / 'manifest.json').read_text())
    report = {
        'validation': 'pending',
        'document_sha256': hashlib.sha256((build / 'manifest.json').read_bytes()).hexdigest(),
        'bundle_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
        'version': document['version'],
        'coordinates': len(document['program']['coordinates']),
        'coverage': 'paused initial-frame browser capture, no command or pointer',
        'errors': [],
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=[
            '--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'])
        try:
            page = browser.new_page(viewport={'width': 800, 'height': 600})
            page.set_default_timeout(180_000)
            page.on('pageerror', lambda error: report['errors'].append(str(error)))

            def serve(route):
                name = unquote(urlsplit(route.request.url).path).lstrip('/')
                if not name:
                    route.fulfill(content_type='text/html', body=(
                        '<html><body style="margin:0"><div id="view" '
                        'style="width:800px;height:600px"></div></body></html>'))
                    return
                asset = (build / name).resolve()
                if asset.is_relative_to(build) and asset.is_file():
                    route.fulfill(path=asset)
                else:
                    route.fulfill(status=404, body='Missing contained asset')

            page.route('http://capture-latency.test/**', serve)
            page.goto('http://capture-latency.test/')
            page.add_script_tag(path=str(bundle))
            started = time.perf_counter()
            report['mount'] = page.evaluate('''async () => {
                window.viewer = await MachinomeViewer.mount('#view','manifest.json',{
                    autoplay:false,run:{dt:.1},partControls:'none'});
                viewer.run().pause();
                return {api:MachinomeViewer.apiVersion,
                        tick:viewer.run().tick(),bank:viewer.run().state(),
                        canvas:!!document.querySelector('canvas')};
            }''')
            report['mount_seconds'] = time.perf_counter() - started
            report['frame_sample_ms'] = page.evaluate('''async () => {
                const start=performance.now();
                for(let i=0;i<20;i++) await new Promise(requestAnimationFrame);
                return performance.now()-start;
            }''')
            started = time.perf_counter()
            page.screenshot(path=str(args.report.with_suffix('.png')), timeout=180_000)
            report['screenshot_seconds'] = time.perf_counter()-started
            report['after_tick'] = page.evaluate('viewer.run().tick()')
            assert report['mount']['canvas'] and report['mount']['api'] == 25
            assert report['after_tick'] == report['mount']['tick'], 'paused run advanced'
            assert not report['errors'], report['errors']
            report['validation'] = 'passed'
        except Exception as error:
            report['failure'] = f'{type(error).__name__}: {error}'
            raise
        finally:
            browser.close()
            report['mount'].pop('bank', None) if 'mount' in report else None
            args.report.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
