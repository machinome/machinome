"""Spike helper: screenshot the asset page at named poses with headless Chromium.

usage: capture.py PAGE_URL OUT_DIR
"""
import sys, time
from playwright.sync_api import sync_playwright

POSES = {
    'home': {},
    'park': dict(art2=80, art3=-135, art5=80, grip=0),
    'place': dict(art1=90, art2=60, art3=-80, art5=-40, art6=90),
    'art6': dict(art6=90),
    'art1': dict(art1=90),
}

url, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    browser = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport=dict(width=900, height=700), device_scale_factor=1)
    errors = []
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(url + '?bg=ffffff&panel=0&cam=viewer', wait_until='load')
    page.wait_for_function('window.spike && window.spike.ready', timeout=120000)
    for name, drivers in POSES.items():
        page.evaluate('d => window.spike.setDrivers(d)', drivers)
        frames = page.evaluate('window.spike.frames')
        page.wait_for_function(f'window.spike.frames > {frames + 3}', timeout=30000)
        page.locator('#view canvas').screenshot(path=f'{out}/asset-{name}.png')
        print('captured', name)
    # play one clip and screenshot halfway through
    page.evaluate("window.spike.play('Park')")
    time.sleep(2.5)
    page.locator('#view canvas').screenshot(path=f'{out}/asset-park-clip-midway.png')
    print('captured park clip midway')
    print('status:', page.locator('#status').inner_text())
    print('facts:', page.locator('#facts').inner_text().replace('\n', ' | '))
    print('console errors:', errors)
    browser.close()
