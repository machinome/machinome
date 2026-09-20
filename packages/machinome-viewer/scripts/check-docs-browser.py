"""Review the built manual and execute its documented embedding examples.

Run with a Python environment containing Playwright and installed Chromium.
Writes screenshots/report under _build/docs-review, never into doc sources.
"""

from contextlib import contextmanager
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
from urllib.parse import unquote, urljoin, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'docs/_build/html'
ARTIFACTS = ROOT / '_build/docs-review'
PAGES = sorted(str(path.relative_to(ROOT / 'docs').with_suffix('.html'))
               for path in (ROOT / 'docs').rglob('*.rst')
               if '_build' not in path.parts)


class Links(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links = set(), []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@contextmanager
def serve():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(HTML)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}/'
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def documented_script(page, section):
    text = (ROOT / 'docs/reference' / page).read_text().split(section, 1)[1]
    block = re.search(r'\.\. code-block:: javascript\n\n((?:   .*\n|\n)+)', text)
    assert block, (page, section)
    return '\n'.join(line[3:] if line.startswith('   ') else line
                     for line in block[1].splitlines())


def fixture_route(route):
    relative = urlsplit(route.request.url).path.split('/test-fixtures/', 1)[1]
    target = (ROOT / 'tests/fixtures' / unquote(relative)).resolve()
    assert target.is_relative_to(ROOT / 'tests/fixtures')
    route.fulfill(path=target)


def main():
    assert (HTML / 'index.html').is_file(), 'Build the manual first'
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    local_links = set()
    for name in PAGES:
        for href in Links(HTML / name).links:
            parsed = urlsplit(urljoin('https://manual.invalid/' + name, href))
            if parsed.netloc != 'manual.invalid' or parsed.query:
                continue
            target = HTML / unquote(parsed.path.lstrip('/'))
            if parsed.path.endswith('/'):
                target /= 'index.html'
            assert target.is_file(), (name, href)
            if parsed.fragment and target.suffix == '.html':
                assert unquote(parsed.fragment) in Links(target).ids, (name, href)
            local_links.add(parsed.geturl())

    errors, pages = [], []
    with serve() as base, sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('response', lambda response: errors.append(f'HTTP {response.status}: {response.url}')
                if response.status >= 400 else None)
        for width, height in [(1440, 1000), (390, 844)]:
            page.set_viewport_size({'width': width, 'height': height})
            for name in PAGES:
                response = page.goto(base + name)
                assert response.status == 200
                page.locator('h1').wait_for()
                layout = page.evaluate('''() => ({
                  width: document.documentElement.clientWidth,
                  scroll: document.documentElement.scrollWidth,
                  brokenImages: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src)
                })''')
                assert layout['scroll'] <= layout['width'], (name, width, layout)
                assert not layout['brokenImages'], (name, layout)
                pages.append({'page': name, 'width': width})
                if name in ['index.html', 'reference/mount.html', 'reference/layouts.html', 'reference/running.html']:
                    page.screenshot(path=str(ARTIFACTS / f'{width}-{name.replace("/", "-")}.png'), full_page=True)

            page.goto(base)
            page.get_by_role('button', name='Load interactive spinner').click()
            frame = page.frame_locator('.viewer-demo iframe')
            frame.locator('#time:not([disabled])').wait_for(timeout=30000)
            canvas = frame.locator('canvas')
            assert canvas.bounding_box()['width'] > 100
            frame.locator('#time').fill('0.25')
            assert frame.locator('#position').inner_text() == '0.25'
            frame.get_by_role('button', name='Assembly', exact=True).click()
            frame.get_by_role('tree', name='Assembly').wait_for()
            page.screenshot(path=str(ARTIFACTS / f'{width}-interactive.png'), full_page=True)

        page.goto(base)
        page.locator('.wy-nav-top i').click()
        page.locator('.wy-menu-vertical a[href="installation.html"]').click()
        assert page.url.endswith('installation.html')
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.goto(base + 'search.html?q=MachineHandle.move')
        page.locator('#search-results li').first.wait_for(timeout=15000)
        assert 'clocked' in page.locator('#search-results').inner_text().lower()
        page.screenshot(path=str(ARTIFACTS / 'search.png'), full_page=True)

        # Read the exact reference snippets, not a separately maintained example.
        page.route('**/test-fixtures/**', fixture_route)
        page.goto(base + 'examples/embed.html')
        page.locator('#time:not([disabled])').wait_for()
        run_code = documented_script('running.rst', 'Scripted example')
        clocked_code = documented_script('clocked.rst', 'Example: operate and restore')
        results = {}
        for fixture, script, tail in [
            ('pascaline', run_code, 'return {elapsed: run.elapsed(), outcomes};'),
            ('calculator', clocked_code, 'return {admitted: stroke.admitted, restored: JSON.stringify(machine.snapshot()) === JSON.stringify(saved)};'),
        ]:
            result = page.evaluate('''async ({fixture, script, tail}) => {
              const target = document.createElement('div');
              target.style.cssText = 'width:600px;height:450px';
              document.body.append(target);
              const viewer = await MachinomeViewer.mount(target, '/test-fixtures/' + fixture + '/viewer.json', {autoplay: false});
              try {
                const execute = new Function('viewer', 'return (async () => {' + script + '\\n' + tail + '})()');
                return await execute(viewer);
              } finally { viewer.dispose(); target.remove(); }
            }''', {'fixture': fixture, 'script': script, 'tail': tail})
            results[fixture] = result
        assert results['pascaline']['elapsed'] == 1
        assert results['pascaline']['outcomes'][0]['status'] == 'completed'
        assert results['calculator'] == {'admitted': 360, 'restored': True}
        assert not errors, errors
        browser.close()

    report = {'pages': len(PAGES), 'viewports': [1440, 390], 'local_links': len(local_links),
              'mobile_menu': 'passed', 'search': 'passed', 'interactive_example': 'passed',
              'reference_examples': results, 'browser_errors': errors}
    (ARTIFACTS / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
