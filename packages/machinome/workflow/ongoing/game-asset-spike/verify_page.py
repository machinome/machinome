"""Spike helper: compare the page's JavaScript evaluation with Python at the Place pose.

usage: verify_page.py PAGE_URL VIEWER_JSON THOR.glb
"""
import json, os, struct, sys
import numpy as np
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(__file__))
from thor_glb import make_scope, rot

url, docpath, glb = sys.argv[1:4]
doc = json.load(open(docpath))
place = dict(art1=90, art2=60, art3=-80, art5=-40, art6=90)
drivers = {k: float(v['default']) for k, v in doc['drivers'].items()}
drivers.update(place)
py_scope = make_scope(doc, drivers)

with sync_playwright() as p:
    browser = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport=dict(width=900, height=700))
    page.goto(url + '?bg=ffffff&panel=0', wait_until='load')
    page.wait_for_function('window.spike && window.spike.ready', timeout=120000)
    page.evaluate('d => window.spike.setDrivers(d)', place)
    js_scope = page.evaluate('window.spike.scope()')
    worlds = {n: page.evaluate(f'window.spike.worldOf({n!r})') for n in ('output', 'art56', 'gripper_finger')}
    browser.close()

worst = max(abs(js_scope[k] - py_scope[k]) for k in js_scope if k != '_t')
print('scope names compared', len(js_scope) - 1, 'max |js - py|', worst)
for k in ('_b12', '_b13', '_b20', '_b24'):
    print(f'  {k}: js {js_scope[k]:.6f} py {py_scope[k]:.6f}')
print('page world matrix of "output" (metres, Y-up):', [round(x, 4) for x in worlds['output']])
