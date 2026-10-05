/* SPDX-License-Identifier: AGPL-3.0-or-later */
import * as THREE from 'three';
import { expect, it, vi } from 'vitest';
const { loadAsync } = vi.hoisted(() => ({ loadAsync: vi.fn() }));
vi.mock('three/examples/jsm/loaders/STLLoader.js', () => ({ STLLoader: class { loadAsync = loadAsync; } }));
import { WidgetTree } from './tree';
import type { ManifestNode } from './types';
import { admitGeometry, GeometryOwner } from './geometry-admission';
const leaf = (name: string): ManifestNode => ({name, type:'leaf',color:null,operations:[],model:`${name}.stl`});
const root = (prefix: string): ManifestNode => ({name:prefix,type:'assembly',color:null,operations:[],
  children:Array.from({length:8},(_,i)=>({...leaf(`${prefix}${i}`),markings:i===0?
    [{name:'mark',model:`${prefix}-mark.stl`,color:'#ffffff'}]:undefined}))});
it('bounds active distinct geometry groups across two roots and markings while every required job completes', async () => {
  const pending: (()=>void)[]=[];
  let active=0,peak=0,total=0;
  loadAsync.mockImplementation(()=>new Promise<THREE.BufferGeometry>(resolve=>{
    active++;peak=Math.max(peak,active);total++;
    pending.push(()=>{active--;resolve(new THREE.BoxGeometry());});
  }));
  const a=new WidgetTree(root('a'),'/'),b=new WidgetTree(root('b'),'/');
  const initially=total;
  // Drain in reverse batches, including jobs admitted after each settlement.
  while(pending.length){pending.splice(0).reverse().forEach(resolve=>resolve());
    for(let i=0;i<12;i++)await Promise.resolve();}
  await Promise.all([a.loaded,b.loaded]);
  a.dispose();b.dispose();
  console.info({initially,peak,total});
  expect(initially).toBe(4);expect(peak).toBeLessThanOrEqual(4);expect(total).toBe(18);
});

const flush = async () => { for(let i=0;i<15;i++)await Promise.resolve(); };
it('cancels queued jobs without requests and retains active capacity until real settlement', async () => {
  const owner = new GeometryOwner(),other = new GeometryOwner();
  const settle: (()=>void)[]=[];
  let started=0;
  const jobs=Array.from({length:7},(_,i)=>admitGeometry(`cancel-${i}`,owner,()=>{
    started++;return new Promise<void>(resolve=>settle.push(resolve));
  }));
  const all=Promise.allSettled(jobs);
  owner.cancel();
  let otherStarted=false;
  const survivor=admitGeometry('survivor',other,async()=>{otherStarted=true;});
  await flush();
  expect(started).toBe(4);expect(otherStarted).toBe(false);
  settle.shift()!();await flush();expect(otherStarted).toBe(true);
  settle.splice(0).forEach(resolve=>resolve());
  expect((await all).every(row=>row.status==='rejected')).toBe(true);
  await survivor;
});

it('removes cancelled queued URL eligibility so a later request cannot inherit abandoned FIFO priority', async () => {
  const activeOwner = new GeometryOwner(), cancelled = new GeometryOwner();
  const survivor = new GeometryOwner(), laterOwner = new GeometryOwner();
  const settle: (() => void)[] = [];
  const activeJobs = Array.from({ length: 4 }, (_, index) =>
    admitGeometry(`fifo-active-${index}`, activeOwner, () =>
      new Promise<void>(resolve => settle.push(resolve))));
  const starts: string[] = [];
  const abandoned = admitGeometry('fifo-X', cancelled, async () => { starts.push('abandoned'); });
  const abandonedResult = Promise.allSettled([abandoned]);
  const first = admitGeometry('fifo-Y', survivor, async () => { starts.push('Y'); });
  cancelled.cancel();
  const second = admitGeometry('fifo-X', laterOwner, async () => { starts.push('new X'); });
  settle.shift()!();
  await flush();
  settle.splice(0).forEach(resolve => resolve());
  await Promise.all([...activeJobs, first, second, abandonedResult]);
  expect(starts).toEqual(['Y', 'new X']);
});

it('releases failures, preserves their original error and closes duplicate groups after actual settlement', async () => {
  const a=new GeometryOwner(),b=new GeometryOwner();
  let fail!: (e:Error)=>void,resolve!:()=>void;
  const error=new Error('original parse failure');
  const failed=admitGeometry('same',a,()=>new Promise<void>((_,reject)=>{fail=reject;}));
  const joined=admitGeometry('same',b,()=>new Promise<void>(yes=>{resolve=yes;}));
  const result=Promise.allSettled([failed,joined]);
  a.cancel(); fail(error); await flush();
  // A completed callback group must no longer be joined while another
  // subscriber's parser is still finishing. The fresh load stays independent.
  let fresh=0;
  const later=admitGeometry('same',b,async()=>{fresh++;return 3;});
  expect(await later).toBe(3);expect(fresh).toBe(1);
  resolve();
  const rows=await result;
  expect(rows[0]).toEqual({status:'rejected',reason:error});
  expect(rows[1].status).toBe('fulfilled');
});

it('disposes active late geometry and never attaches it to a disposed tree', async () => {
  let resolve!:(g:THREE.BufferGeometry)=>void;
  loadAsync.mockImplementationOnce(()=>new Promise<THREE.BufferGeometry>(yes=>{resolve=yes;}));
  const tree=new WidgetTree(leaf('late'),'/');
  const loaded=Promise.allSettled([tree.loaded]);
  tree.dispose();tree.dispose();
  const geometry=new THREE.BoxGeometry(),dispose=vi.spyOn(geometry,'dispose');
  resolve(geometry);await loaded;
  expect(dispose).toHaveBeenCalledTimes(1);expect(tree.group.children).toHaveLength(0);
});

it.each([0,1,2,3,4])('disposes a returned result exactly once when cancelled after %i microtasks', async steps => {
  let resolve!:(g:THREE.BufferGeometry)=>void;
  loadAsync.mockImplementationOnce(()=>new Promise<THREE.BufferGeometry>(yes=>{resolve=yes;}));
  const tree=new WidgetTree(leaf(`microtask-${steps}`),'/');
  const loaded=Promise.allSettled([tree.loaded]);
  const geometry=new THREE.BoxGeometry(),dispose=vi.spyOn(geometry,'dispose');
  resolve(geometry);
  for(let i=0;i<steps;i++)await Promise.resolve();
  tree.dispose();await loaded;
  expect(dispose).toHaveBeenCalledTimes(1);
  expect(tree.group.children.filter(x=>x.isMesh && !x.geometry)).toHaveLength(0);
});

it('retains last-good geometry when a multi-part artifact or reconcile preparation fails', async () => {
  loadAsync.mockImplementation(async()=>new THREE.BoxGeometry());
  const tree=new WidgetTree({name:'root',type:'assembly',color:null,operations:[],
    children:[leaf('one'),leaf('two')]},'/');
  await tree.loaded;
  const previous=tree.children.map(child=>child.group.children[0]);
  const prepared=new THREE.BoxGeometry(),dispose=vi.spyOn(prepared,'dispose');
  loadAsync.mockResolvedValueOnce(prepared).mockRejectedValueOnce(Error('replacement failed'));
  await expect(tree.reconcile({name:'root',type:'assembly',color:null,operations:[],children:[
    {...leaf('one'),mtime:2},{...leaf('two'),mtime:2}]},'/')).rejects.toThrow('replacement failed');
  expect(tree.children.map(child=>child.group.children[0])).toEqual(previous);
  expect(dispose).toHaveBeenCalledTimes(1);
  tree.dispose();
});

it.each([3, 4, 5, 10])('does not commit prepared shared-path models or markings after disposal at microtask %i', async steps => {
  loadAsync.mockImplementation(async () => new THREE.BoxGeometry());
  const tree = new WidgetTree({ ...leaf('artifact-and-marking'), model: 'shared.stl',
    markings: [{ name: 'mark', model: 'shared.stl', color: '#ffffff' }] }, '/');
  await tree.loaded;
  const markingGroup = tree.group.children.find(child => !child.isMesh)!;
  const pending: (() => void)[] = [];
  loadAsync.mockImplementation(() => new Promise<THREE.BufferGeometry>(resolve => {
    pending.push(() => resolve(new THREE.BoxGeometry()));
  }));
  const result = Promise.allSettled([tree.artifactChanged('shared.stl', '/')]);
  expect(pending).toHaveLength(2);
  pending.forEach(resolve => resolve());
  for (let step = 0; step < steps; step++) await Promise.resolve();
  tree.dispose();
  const partAdd = vi.spyOn(tree.group, 'add'), markingAdd = vi.spyOn(markingGroup, 'add');
  await result;
  expect(partAdd).not.toHaveBeenCalled();
  expect(markingAdd).not.toHaveBeenCalled();
});
