"""One ordinary canonical build using the isolated, corrected WT runtime."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import fcntl
import json
import os
import signal
import subprocess
import time

from simulation.export_native_console import source_inputs

ROOT=Path('/mnt/data/machinome-projects/enigma-i')
OUT=Path(__file__).resolve().parent
WT=Path('/home/asa/devel/machinome/machinome/WTs/skip-equal-artifact-restamps')
EXPECTED_HEAD='60c6d8cb6193d67fecb410d0a1b0a8571938f37d'


def digest(path):return sha256(path.read_bytes()).hexdigest()
def head(path):return subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip()
def ticks(pid):return Path(f'/proc/{pid}/stat').read_text().split(') ',1)[1].split()[19]
def provenance(pid):return {'pid':pid,'start_ticks':ticks(pid),'mount_namespace':os.readlink(f'/proc/{pid}/ns/mnt')}


def assets(value,inputs):
    if isinstance(value,dict):
        if isinstance(value.get('file'),str) and 'sha256' in value:
            name=value['file']
            if digest(ROOT/name)!=value['sha256']:raise ValueError('Pinned asset changed: '+name)
            inputs[name]=value['sha256']
        for child in value.values():assets(child,inputs)
    elif isinstance(value,list):
        for child in value:assets(child,inputs)


def model_hashes():
    document=json.loads((ROOT/'_build/viewer.json').read_text())
    paths=set()
    def visit(node):
        if 'model' in node:paths.add(node['model'])
        for child in node.get('children',[]):visit(child)
    visit(document['root'])
    return {path:digest(ROOT/'_build'/path) for path in sorted(paths)}


def main():
    if Path.cwd().resolve()!=ROOT or head(ROOT)!=EXPECTED_HEAD:raise RuntimeError('Canonical main moved before caller check')
    if (OUT/'process.json').exists():raise RuntimeError('One actual caller command only; retained result exists')
    inputs=source_inputs(ROOT)
    from simulation.v_rest_lamp_lead import lead_input
    lead=lead_input()
    for item in [lead['baseline'],lead['function_basis'],*lead['endpoint_assets'].values()]:
        if digest(ROOT/item['file'])!=item['sha256']:raise ValueError(item['file'])
        inputs[item['file']]=item['sha256']
    for filename in ('parallel-electrical-row-lead-input-v1.json','parallel-electrical-rest-lamp-bank-input-v3.json'):
        assets(json.loads((ROOT/'sources'/filename).read_text()),inputs)
    inputs[str(Path(__file__).resolve().relative_to(ROOT))]=digest(Path(__file__))
    (OUT/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
    probe="""import hashlib,json,sys
from pathlib import Path
from importlib import metadata
import machinome.currency as c
import machinome._artifact as a
import machinome.core.pieces as p
import machinome.node.step as s
print(json.dumps({'python':sys.version,'executable':sys.executable,'packages':{n:metadata.version(n) for n in ('machinome','machinome-node-step','machinome-node-cadquery','machinome-engine-brep','machinome-engine-mesh','machinome-viewer','cadquery','molejo')},'currency':{'path':c.__file__,'sha256':hashlib.sha256(Path(c.__file__).read_bytes()).hexdigest()},'artifact':{'path':a.__file__,'sha256':hashlib.sha256(Path(a.__file__).read_bytes()).hexdigest()},'pieces':{'path':p.__file__,'sha256':hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest()},'step_path':s.__file__}))
"""
    runtime=json.loads(subprocess.check_output([str(WT/'.venv/bin/python'),'-B','-c',probe],cwd=ROOT,text=True))
    if not runtime['currency']['path'].startswith(str(WT)+os.sep):raise RuntimeError('WT core not selected')
    (OUT/'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n')
    before=model_hashes();(OUT/'models-before.json').write_text(json.dumps(before,indent=2)+'\n')
    command=[str(WT/'.venv/bin/machinome'),'build']
    status={'complete':False,'project_revision':EXPECTED_HEAD,'framework_planning_commit':head(WT),
        'parent':provenance(os.getpid()),'command':command,'cwd':str(ROOT),
        'build_root':str(ROOT/'_build'),'native_lock':'/tmp/enigma-native-secondary-20261107.lock',
        'reference':'simulation.candidate_machine:CandidateMachineInspection',
        'runtime':runtime,'queued_at':datetime.now(timezone.utc).isoformat(),
        'document_sha256_before':digest(ROOT/'_build/viewer.json'),'timeout_seconds':420,
        'no_manual_document_or_cache_edits':True,'original_guards_and_retry_unchanged':True,
        'instrumentation':'Source/runtime/hash receipt only; no sitecustomize, trace or behavior hook in caller command',
        'timed_out':False}
    def save():
        temporary=OUT/'process.json.tmp';temporary.write_text(json.dumps(status,indent=2)+'\n');temporary.replace(OUT/'process.json')
    save();print('queued',status['parent'],flush=True)
    with open(status['native_lock'],'a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if head(ROOT)!=EXPECTED_HEAD:raise RuntimeError('Main moved while waiting')
        changed=[name for name,value in inputs.items() if digest(ROOT/name)!=value]
        if changed:raise RuntimeError('Inputs moved while waiting: '+repr(changed))
        if digest(Path(runtime['currency']['path']))!=runtime['currency']['sha256']:raise RuntimeError('WT source moved')
        start=time.monotonic();status['started_at']=datetime.now(timezone.utc).isoformat();save()
        env=dict(os.environ);env.pop('SOLID_BUILD_DIR',None);env.pop('ENIGMA_ARTIFACT_TRACE',None);env['PYTHONPATH']='.'
        with (OUT/'build.log').open('w') as log:
            child=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            status['child']=provenance(child.pid);save()
            try:code=child.wait(timeout=420)
            except subprocess.TimeoutExpired:
                status['timed_out']=True;os.killpg(child.pid,signal.SIGTERM)
                try:code=child.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
        after=model_hashes();(OUT/'models-after.json').write_text(json.dumps(after,indent=2)+'\n')
        changed=[name for name,value in inputs.items() if digest(ROOT/name)!=value]
        status.update(complete=True,returncode=code,elapsed_seconds=time.monotonic()-start,
            finished_at=datetime.now(timezone.utc).isoformat(),project_revision_after=head(ROOT),
            inputs_unchanged=not changed,changed_inputs=changed,
            core_source_unchanged=digest(Path(runtime['currency']['path']))==runtime['currency']['sha256'],
            document_sha256_after=digest(ROOT/'_build/viewer.json'),models_unchanged=before==after,
            referenced_models_before=len(before),referenced_models_after=len(after),
            errors_json=(ROOT/'_build/errors.json').read_text() if (ROOT/'_build/errors.json').exists() else None,
            build_log_sha256=digest(OUT/'build.log'))
        save();print(json.dumps(status),flush=True)
        if changed or not status['core_source_unchanged']:raise RuntimeError('Caller input/source changed')
        return code


if __name__=='__main__':raise SystemExit(main())
