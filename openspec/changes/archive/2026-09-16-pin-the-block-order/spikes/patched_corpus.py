import json, os, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from order import listing, compare
from tools.generate_running_corpus import run_machine
fixture = json.load(open(os.path.join(ROOT,'tests','running-corpus.json')))
for entry in fixture['machines']:
    with listing():
        try:
            ticks = run_machine({k: entry[k] for k in ('name','dt','steps','script')})
        except Exception as exc:
            print(f'{entry["name"]:16} dt={entry["dt"]:<5} RAISED {type(exc).__name__}: {exc}')
            continue
    bad = compare(entry['ticks'], ticks)
    print(f'{entry["name"]:16} dt={entry["dt"]:<5} '
          f'{"PASSES under listing order" if not bad else f"DIVERGES ({len(bad)})"}')
