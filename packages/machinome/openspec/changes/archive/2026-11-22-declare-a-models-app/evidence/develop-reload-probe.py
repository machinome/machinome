# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Observe how the development page learns of a publication after a source edit.

Opens the development page, records every reload-socket frame and every fetch
of /build/viewer.json (with the model path the document names at that moment),
edits the model's Python, and records when viewer.json is rewritten on disk.
"""
import json, os, sys, time, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJ = Path(sys.argv[1])
SRC = PROJ / 'flat_project' / 'simple_cylinder.py'
DOC = PROJ / '_build' / 'viewer.json'
T0 = time.monotonic()
events = []

def log(kind, detail=''):
    events.append((round(time.monotonic() - T0, 2), kind, detail))
    print(f'{events[-1][0]:7.2f}  {kind:18s} {detail}', flush=True)

def doc_model():
    try:
        d = json.loads(DOC.read_text())
        return d['root'].get('model'), DOC.stat().st_mtime_ns
    except Exception as e:
        return repr(e), None

stop = False
def watch_disk():
    last = doc_model()[1]
    while not stop:
        m, ns = doc_model()
        if ns != last:
            log('DISK viewer.json', m)
            last = ns
        time.sleep(0.05)

threading.Thread(target=watch_disk, daemon=True).start()

with sync_playwright() as p:
    browser = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader',
                                      '--enable-unsafe-swiftshader'])
    page = browser.new_page()
    page.on('websocket', lambda ws: (log('WS open', ws.url),
                                     ws.on('framereceived', lambda f: log('WS recv', str(f)))))
    def on_response(r):
        if r.url.endswith('/build/viewer.json'):
            try:
                body = r.json()
                log('PAGE fetch doc', body['root'].get('model'))
            except Exception as e:
                log('PAGE fetch doc', repr(e))
        elif '/_build_error' in r.url:
            log('PAGE build_error', r.text()[:60])
    page.on('response', on_response)
    page.goto('http://localhost:8028/')
    page.wait_for_timeout(8000)
    log('--- EDIT 1', 'radius 1 -> 3')
    SRC.write_text(SRC.read_text().replace('radius=1,', 'radius=3,'))
    page.wait_for_timeout(25000)
    log('--- EDIT 2', 'height 10 -> 20')
    SRC.write_text(SRC.read_text().replace('height=10)', 'height=20)'))
    page.wait_for_timeout(25000)
    log('--- END')
    browser.close()
stop = True
