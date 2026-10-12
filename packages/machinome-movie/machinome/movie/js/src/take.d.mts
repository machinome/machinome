// The types of src/take.mjs, the pose rule of a clocked take, for the
// TypeScript that imports it: the take transport (transport/take.ts). The
// module itself is plain JavaScript, read by Node and bundled by esbuild;
// this file is read only by `tsc`. Every export of the module is declared
// here, and test/transport-boundary.test.mjs holds the two to each other.

/** A clocked machine's drivers and states by qualified id, in native units. */
export type Bank=Record<string,number>;
/** What a commit of a step wrote, at the fraction of the step's path it fired. */
export interface TakeCommit {fraction:number;value:number;targets:Bank;relations?:string[]}
/** A step of a take: the request the framework returned, verbatim (docs/movie-document.md, "The take"). */
export interface TakeStep {
  id:string;
  at:number;
  duration:number;
  input:string;
  to?:number;
  by?:number;
  origin:number;
  end:number;
  admitted:number;
  commits:TakeCommit[];
  stops:unknown[];
}
/** A document's `take` block. */
export interface ClockedTake {
  kind:'clocked';
  identity:string;
  initial:Bank;
  steps:TakeStep[];
  banks:Record<string,Bank>;
}
/**
 * What a take is read from: a movie document that films a clocked take, or
 * its resolution. The marks' take times are the document's `marks`; the
 * take's length is `model.expectedDurationSeconds`, read and never added
 * (ADR-016).
 */
export interface TakeDocument {
  model:{expectedDurationSeconds:number};
  marks?:Record<string,number>;
  take:ClockedTake;
}

export function takeTimes(steps:readonly {duration:number}[]):{starts:number[];length:number};
export function stepEnds(doc:TakeDocument):number[];
export function replayTake(take:ClockedTake):{before:Bank[];after:Bank[]};
export function markSteps(doc:TakeDocument):Record<string,number>;
export function checkTakeBanks(doc:TakeDocument):void;
export function bankAt(doc:TakeDocument,seconds:number):Bank;
export function markAt(doc:TakeDocument,seconds:number):string|null;
export function takeLine(doc:TakeDocument):string;
