/* SPDX-License-Identifier: AGPL-3.0-or-later */
// Bundle/page admission only. Scene resources belong to the caller's owner.
export class GeometryOwner {
  cancelled = false;
  readonly cancellation = new Error('Geometry load owner was disposed');
  private cleanup = new Set<() => void>();
  own(cleanup: () => void): () => void {
    if (this.cancelled) cleanup(); else this.cleanup.add(cleanup);
    return () => { this.cleanup.delete(cleanup); };
  }
  cancel(): void {
    if (this.cancelled) return;
    this.cancelled = true;
    for (const cleanup of this.cleanup) cleanup();
    this.cleanup.clear();
    for (const group of queue) {
      group.jobs = group.jobs.filter(job => {
        if (job.owner !== this) return true;
        job.reject(this.cancellation); return false;
      });
      // A later subscriber is a new request, not a revival of this
      // abandoned group's FIFO position. pump may keep the tombstone.
      if (!group.jobs.length) close(group);
    }
    pump();
  }
}

interface Job {
  owner: GeometryOwner;
  start: () => Promise<unknown>;
  resolve: (value: unknown) => void;
  reject: (error: unknown) => void;
  abandon: (value: unknown) => void;
}
interface Group { url: string; jobs: Job[]; active: boolean; pending: number }
const groups = new Map<string, Group>();
const queue: Group[] = [];
let active = 0;
const BUDGET = 4;

function close(group: Group): void {
  // Once ANY subscriber settles, the network callback group is no longer
  // safely joinable. Never turn completed requests into a persistent cache.
  if (groups.get(group.url) === group) groups.delete(group.url);
}
function start(group: Group, job: Job): void {
  group.pending++;
  let promise: Promise<unknown>;
  try { promise = job.start(); } catch (error) { promise = Promise.reject(error); }
  promise.then(value => {
    close(group);
    if (job.owner.cancelled) {
      job.abandon(value);
      job.reject(job.owner.cancellation);
    }
    else job.resolve(value);
  }, error => { close(group); job.reject(error); }).finally(() => {
    group.pending--;
    if (group.pending === 0) { active--; pump(); }
  });
}
function pump(): void {
  while (active < BUDGET && queue.length) {
    const group = queue.shift()!;
    if (!group.jobs.length) { close(group); continue; }
    group.active = true; active++;
    const jobs = group.jobs; group.jobs = [];
    for (const job of jobs) start(group, job);
  }
}

/** Each subscriber starts its OWN STLLoader parse against the overlapping
 * three.js FileLoader request, retaining independent mutable geometry. */
export function admitGeometry<T>(url: string, owner: GeometryOwner,
                                 startLoad: () => Promise<T>,
                                 abandon: (value: T) => void = () => undefined): Promise<T> {
  if (owner.cancelled) return Promise.reject(owner.cancellation);
  return new Promise<T>((resolve, reject) => {
    const job: Job = { owner, start: startLoad,
      resolve: value => resolve(value as T), reject,
      abandon: value => abandon(value as T) };
    let group = groups.get(url);
    if (!group) {
      group = { url, jobs: [], active: false, pending: 0 };
      groups.set(url, group); queue.push(group);
    }
    if (group.active) start(group, job); else group.jobs.push(job);
    pump();
  });
}

/** A failed preparation cancels only its new work; commit hands resources
 * to the tree. Dispose callbacks are idempotent and also cover late results. */
export class GeometryBatch {
  private owners = new Set<GeometryOwner>();
  private cleanup = new Set<() => void>();
  owner(): GeometryOwner { const owner = new GeometryOwner(); this.owners.add(owner); return owner; }
  own(cleanup: () => void): void { this.cleanup.add(cleanup); }
  cancel(): void {
    for (const owner of this.owners) owner.cancel();
    for (const cleanup of this.cleanup) cleanup();
    this.cleanup.clear();
  }
}
