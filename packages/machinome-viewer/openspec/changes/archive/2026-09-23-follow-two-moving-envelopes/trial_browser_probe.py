"""Read-only hosted browser parity probe for a frozen Curta Follow trial export.

This uses the viewer's public mount and run surfaces. It does not claim pointer
coverage or that the originating project has adopted the trial.
"""

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--oracle', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    assert not args.report.exists(), 'preserve earlier reports'
    build = args.build.resolve()
    oracle = json.loads(args.oracle.read_text())
    document = json.loads((build / 'manifest.json').read_text())
    report = {
        'validation': 'pending', 'errors': [], 'stages': {},
        'coverage': 'real Chromium/WebGL hosted public run; dt=.1, no pointer',
        'document_version': document['version'],
        'coordinates': len(document['program']['coordinates']),
        'program_identity': document['program']['identity'],
        'asset_sha256': {name: digest(build / name) for name in (
            'manifest.json', 'machinome-viewer.js', 'index.html')},
        'oracle_sha256': digest(args.oracle),
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=[
            '--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'])
        try:
            page = browser.new_page(viewport={'width': 1440, 'height': 1000})
            page.set_default_timeout(300_000)
            page.on('pageerror', lambda error: report['errors'].append(str(error)))

            def serve(route):
                name = unquote(urlsplit(route.request.url).path).lstrip('/')
                if not name:
                    route.fulfill(content_type='text/html', body=(
                        '<html><body style="margin:0"><div id="view" '
                        'style="width:1440px;height:1000px"></div></body></html>'))
                    return
                asset = (build / name).resolve()
                if asset.is_relative_to(build) and asset.is_file():
                    route.fulfill(path=asset)
                else:
                    route.fulfill(status=404, body='Missing contained asset')

            page.route('http://follow-trial.test/**', serve)
            page.goto('http://follow-trial.test/')
            page.add_script_tag(path=str(build / 'machinome-viewer.js'))
            report['mount'] = page.evaluate('''async () => {
                window.curta = await MachinomeViewer.mount('#view', 'manifest.json', {
                    autoplay:false, run:{dt:.1}, partControls:'inline'
                });
                curta.run().pause();
                return {api: MachinomeViewer.apiVersion, dt:curta.run().dt(),
                        controls:curta.controls().length,
                        canvas:!!document.querySelector('canvas')};
            }''')

            def capture(stage, action):
                row = page.evaluate(action)
                report['stages'][stage] = row
                expected = oracle[stage]['bank']
                differences = {key: (row['bank'].get(key), value)
                               for key, value in expected.items()
                               if row['bank'].get(key) != value}
                assert len(row['bank']) == len(expected) == 214
                assert not differences, (stage, differences)
                if oracle[stage].get('status'):
                    assert row['status'] == oracle[stage]['status'], (stage, row)
                print(json.dumps({'stage': stage, 'status': row['status'],
                                  'crank': row['bank']['crank_rotation']}), flush=True)

            capture('rest', '''async () => ({status:'rest',bank:curta.run().state()})''')
            capture('lift', '''async () => {
                const status=(await curta.run().move('carriage_elevation',{to:6})).at(-1).status;
                window.saved=await curta.run().snapshot();
                return {status,bank:curta.run().state()};
            }''')
            capture('blocked', '''async () => {
                const run=curta.run(), command=run.move('crank_rotation',{to:90,duration:.5});
                await run.step(1);
                const status=(await command).at(-1).status;
                window.stopped=await run.snapshot();
                return {status,bank:run.state()};
            }''')
            capture('replay', '''async () => {
                const run=curta.run(); await run.restore(saved);
                const command=run.move('crank_rotation',{to:90,duration:.5});
                await run.step(1);
                const status=(await command).at(-1).status;
                const replay=JSON.stringify(await run.snapshot())===JSON.stringify(stopped);
                if(!replay) throw Error('Snapshot replay mismatch');
                return {status,bank:run.state(),replay};
            }''')
            capture('relief', '''async () => {
                const status=(await curta.run().move('carriage_elevation',{to:0})).at(-1).status;
                return {status,bank:curta.run().state()};
            }''')
            capture('after_relief', '''async () => {
                const run=curta.run(), command=run.move('crank_rotation',{to:90,duration:.5});
                await run.step(5);
                return {status:(await command).at(-1).status,bank:run.state()};
            }''')
            capture('outward', '''async () => {
                const run=curta.run(); await run.reset();
                const command=run.move('crank_rotation',{by:90,duration:.5});
                await run.step(5);
                return {status:(await command).at(-1).status,bank:run.state()};
            }''')
            capture('return', '''async () => {
                const run=curta.run(), command=run.move('crank_rotation',{to:360,duration:1.5});
                await run.step(15);
                return {status:(await command).at(-1).status,bank:run.state()};
            }''')
            assert report['mount'] == {
                'api': 25, 'dt': .1, 'controls': 25, 'canvas': True}
            assert report['stages']['blocked']['bank']['crank_rotation'] == .36119713971311285
            assert report['stages']['return']['bank'][
                'carriage.positioning.p_6mm_ball_419094.slide'] == report['stages']['outward']['bank'][
                'carriage.positioning.p_6mm_ball_419094.slide']
            assert not report['errors'], report['errors']
            page.screenshot(path=str(args.report.with_suffix('.png')), timeout=180_000)
            report['validation'] = 'passed'
        except Exception as error:
            report['failure'] = f'{type(error).__name__}: {error}'
            raise
        finally:
            browser.close()
            args.report.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
