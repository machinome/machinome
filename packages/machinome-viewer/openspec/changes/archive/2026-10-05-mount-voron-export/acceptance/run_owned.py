import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
scratch=Path(__file__).parent
name=sys.argv[1]
started=time.monotonic()
with (scratch/f'{name}.log').open('w') as output:
    process=subprocess.Popen(sys.argv[2:],stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
    group=process.pid;peak=0
    try:
        while process.poll() is None and time.monotonic()-started<225:
            rows=subprocess.run(['ps','-eo','pgid,rss'],capture_output=True,text=True).stdout.splitlines()[1:]
            peak=max(peak,sum(int(row.split()[1]) for row in rows if row.split()[0]==str(group)))
            time.sleep(.2)
        if process.poll() is None:
            os.killpg(group,signal.SIGTERM)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(group,signal.SIGKILL);process.wait(timeout=5)
    finally:
        try:os.killpg(group,signal.SIGKILL)
        except ProcessLookupError:pass
rows=subprocess.run(['ps','-eo','pid,pgid,args'],capture_output=True,text=True).stdout.splitlines()[1:]
survivors=[row for row in rows if row.split()[1]==str(group)]
result=dict(command=sys.argv[2:],group=group,returncode=process.returncode,peak_group_rss_kib=peak,
    elapsed_seconds=time.monotonic()-started,survivors=survivors)
(scratch/f'{name}-cleanup.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
if process.returncode or survivors:raise SystemExit(1)
