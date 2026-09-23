"""Hosted public-handle parity of candidate bundle against frozen Curta export."""

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--oracle', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--no-screenshot', action='store_true')
    args = parser.parse_args()
    build = args.build.resolve()
    bundle = args.bundle.resolve()
    oracle = json.loads(args.oracle.read_text())
    report = {'validation': 'pending', 'manifest_sha256': sha(build / 'manifest.json'),
              'bundle_sha256': sha(bundle), 'oracle_sha256': sha(args.oracle),
              'stages': {}, 'errors': []}
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

            page.route('http://follow-prefix.test/**', serve)
            page.goto('http://follow-prefix.test/')
            page.add_script_tag(path=str(bundle))
            report['mount'] = page.evaluate('''async () => {
                window.curta = await MachinomeViewer.mount('#view', 'manifest.json', {
                    autoplay:false, run:{dt:.1}, partControls:'inline'
                });
                curta.run().pause();
                return {api:MachinomeViewer.apiVersion,dt:curta.run().dt(),
                    controls:curta.controls().length,canvas:!!document.querySelector('canvas')};
            }''')

            def stage(name, action):
                result = page.evaluate(action)
                expected = oracle[name]['bank']
                differences = {key: [result['bank'].get(key), value]
                               for key, value in expected.items()
                               if result['bank'].get(key) != value}
                assert len(result['bank']) == len(expected) == 214
                assert not differences, (name, differences)
                if oracle[name].get('status'):
                    assert result['status'] == oracle[name]['status']
                report['stages'][name] = {'status': result['status'],
                    'crank': result['bank']['crank_rotation'], 'differences': differences}
                print(json.dumps({'stage': name, **report['stages'][name]}), flush=True)

            stage('rest', "async () => ({status:'rest',bank:curta.run().state()})")
            stage('lift', '''async () => {
                const status=(await curta.run().move('carriage_elevation',{to:6})).at(-1).status;
                window.saved=await curta.run().snapshot();
                return {status,bank:curta.run().state()};
            }''')
            stage('blocked', '''async () => {
                const run=curta.run(), command=run.move('crank_rotation',{to:90,duration:.5});
                await run.step(1); window.stopped=await run.snapshot();
                return {status:(await command).at(-1).status,bank:run.state()};
            }''')
            stage('replay', '''async () => {
                const run=curta.run(); await run.restore(saved);
                const command=run.move('crank_rotation',{to:90,duration:.5});
                await run.step(1);
                if(JSON.stringify(await run.snapshot())!==JSON.stringify(stopped))
                    throw Error('Snapshot replay mismatch');
                return {status:(await command).at(-1).status,bank:run.state()};
            }''')
            stage('relief', '''async () => {
                const status=(await curta.run().move('carriage_elevation',{to:0})).at(-1).status;
                return {status,bank:curta.run().state()};
            }''')
            stage('after_relief', '''async () => {
                const run=curta.run(), command=run.move('crank_rotation',{to:90,duration:.5});
                await run.step(5);
                return {status:(await command).at(-1).status,bank:run.state()};
            }''')
            stage('outward', '''async () => {
                const run=curta.run(); await run.reset();
                const command=run.move('crank_rotation',{by:90,duration:.5});
                await run.step(5);
                return {status:(await command).at(-1).status,bank:run.state()};
            }''')
            stage('return', '''async () => {
                const run=curta.run(), command=run.move('crank_rotation',{to:360,duration:1.5});
                await run.step(15);
                return {status:(await command).at(-1).status,bank:run.state()};
            }''')
            assert report['mount'] == {'api': 25, 'dt': .1, 'controls': 25, 'canvas': True}
            assert not report['errors'], report['errors']
            if not args.no_screenshot:
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
