/* SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+ */
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

/** How a reading of one URL is made, copied for a further viewer, and
 * freed (OpenSpec `share-one-geometry-per-model-file`, design Decision 1).
 * The reading uses the kind of the load that opens it. */
export interface ReadingKind<T> {
  read(url: string): Promise<T>;
  copy(value: T): T;
  dispose(value: T): void;
}

/** One holder's hold on its viewer's geometry of one reading. `value`
 * must not be written; `release()` lets go, once, however often it is
 * called. */
export interface Share<T> {
  readonly value: T;
  release(): void;
}

/** One viewer's geometry of one reading and how many hold it. Disposed
 * exactly once: when nothing holds it and its reading has retired. A
 * disposed holding drops its value. */
interface Holding {
  readonly url: string;
  readonly viewer: object;
  value: unknown;
  holders: number;
  retired: boolean;
  dispose: ((value: unknown) => void) | undefined;
}

class HeldShare implements Share<unknown> {
  private released = false;
  constructor(private readonly holding: Holding) {}
  get value(): unknown { return this.holding.value; }
  release(): void {
    if (this.released) return;
    this.released = true;
    const holding = this.holding;
    holding.holders--;
    if (holding.holders === 0 && holding.retired) disposeHolding(holding);
  }
}

interface Job {
  owner: GeometryOwner;
  viewer: object;
  resolve: (share: Share<unknown>) => void;
  reject: (error: unknown) => void;
}
/** One reading: one admission group, one slot of the four, one request
 * and one parse. It is joinable until its request settles; it retires
 * when every subscriber that joined it has settled, and then keeps no
 * geometry. */
interface Group {
  url: string; jobs: Job[]; active: boolean; pending: number;
  kind: ReadingKind<unknown>;
  load: Promise<unknown> | undefined;
  // The parse, until it is taken by its first viewer or the reading
  // retires; never both.
  parsed: boolean; value: unknown; taken: boolean;
  holdings: Map<object, Holding>;
}
const groups = new Map<string, Group>();
const queue: Group[] = [];
let active = 0;
const BUDGET = 4;
// The holdings alive, for the census. Never read on a load's path.
const alive = new Set<Holding>();

function close(group: Group): void {
  // Once its request settles, a reading is no longer joinable. Never turn
  // completed requests into a persistent cache.
  if (groups.get(group.url) === group) groups.delete(group.url);
}
function disposeHolding(holding: Holding): void {
  const dispose = holding.dispose!;
  const value = holding.value;
  holding.value = undefined;
  holding.dispose = undefined;
  alive.delete(holding);
  dispose(value);
}
/** This viewer's share of the reading: the first viewer takes the parse,
 * each further one a copy of it. Called only in the reaction to the
 * reading's arrival, before any share of it can be released. */
function take(group: Group, viewer: object): Share<unknown> {
  let holding = group.holdings.get(viewer);
  if (holding === undefined) {
    const value = group.taken ? group.kind.copy(group.value) : group.value;
    group.taken = true;
    holding = { url: group.url, viewer, value, holders: 0, retired: false,
                dispose: group.kind.dispose };
    group.holdings.set(viewer, holding);
    alive.add(holding);
  }
  holding.holders++;
  return new HeldShare(holding);
}
/** Every subscriber has settled: no share of this reading will be taken
 * again. What no one holds is freed; the reading lets go of everything. */
function retire(group: Group): void {
  if (group.parsed && !group.taken) group.kind.dispose(group.value);
  group.value = undefined;
  group.parsed = false;
  group.load = undefined;
  for (const holding of group.holdings.values()) {
    holding.retired = true;
    if (holding.holders === 0) disposeHolding(holding);
  }
  group.holdings.clear();
}
function begin(group: Group): Promise<unknown> {
  let load: Promise<unknown>;
  try { load = group.kind.read(group.url); } catch (error) { load = Promise.reject(error); }
  group.load = load;
  // The first reaction to the request's settlement, before any
  // subscriber's: the reading closes here.
  load.then(value => { group.value = value; group.parsed = true; close(group); },
            () => close(group));
  return load;
}
function start(group: Group, job: Job): void {
  group.pending++;
  const load = group.load ?? begin(group);
  load.then(() => {
    if (job.owner.cancelled) job.reject(job.owner.cancellation);
    else {
      let share: Share<unknown>;
      try { share = take(group, job.viewer); } catch (error) { job.reject(error); return; }
      job.resolve(share);
    }
  }, error => { job.reject(error); }).finally(() => {
    group.pending--;
    if (group.pending === 0) { retire(group); active--; pump(); }
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

/** One reading per admission group (OpenSpec
 * `share-one-geometry-per-model-file`, design Decisions 1, 3 and 6): every
 * subscriber of a URL that asks while its reading is open -- queued, or
 * its request not yet settled -- joins it, and the reading sends one
 * request through `kind.read` and parses it once. Each subscriber gets a
 * share of its viewer's holding: the first viewer takes the parse, each
 * further viewer a copy. A subscriber whose owner was cancelled when the
 * reading arrives takes no share; what no one took is freed when the
 * reading retires. */
export function admitGeometry<T>(url: string, owner: GeometryOwner, viewer: object,
                                 kind: ReadingKind<T>): Promise<Share<T>> {
  if (owner.cancelled) return Promise.reject(owner.cancellation);
  return new Promise<Share<T>>((resolve, reject) => {
    const job: Job = { owner, viewer, resolve: resolve as (share: Share<unknown>) => void, reject };
    let group = groups.get(url);
    if (!group) {
      group = { url, jobs: [], active: false, pending: 0, kind: kind as ReadingKind<unknown>,
                load: undefined, parsed: false, value: undefined, taken: false,
                holdings: new Map() };
      groups.set(url, group); queue.push(group);
    }
    if (group.active) start(group, job); else group.jobs.push(job);
    pump();
  });
}

/** A holding alive, as the census lists it: for the tests. */
export interface CensusRow {
  url: string;
  viewer: object;
  holders: number;
  value: unknown;
}

/** Every holding alive, with its URL, viewer, holder count and value. For
 * the tests; nothing on a load's path reads it. */
export function geometryCensus(): CensusRow[] {
  return [...alive].map(({ url, viewer, holders, value }) => ({ url, viewer, holders, value }));
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
