// The registry of set and element kinds. A project's module registers its
// kinds with defineSet and defineElement when the bundle loads; the runtime
// registers the shipped ones first. A kind registered twice is refused by
// name, and the runtime refuses at mount a document whose kinds or slots the
// registry does not match (checkRegistry).
import type {ComponentType} from 'react';
import type {ElementDefinition,SetDefinition,SlotsOf,StageConfig} from './types';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyComponent=ComponentType<any>;
export interface RegisteredSet {kind:string;slots:readonly string[];component:AnyComponent;shipped:boolean}
export interface RegisteredElement {kind:string;component:AnyComponent;shipped:boolean}

const sets=new Map<string,RegisteredSet>();
const elements=new Map<string,RegisteredElement>();

const named=(kind:unknown,what:string):string=>{
  if(typeof kind!=='string'||!/^[a-z][a-z0-9-]*$/.test(kind))
    throw new Error(`${what} kind ${JSON.stringify(kind)} is not a kind name (a lower-case letter, then lower-case letters, digits or hyphens)`);
  return kind;
};

export function registerSet(kind:string,slots:readonly string[],component:AnyComponent,shipped=false):void{
  named(kind,'Set');
  if(sets.has(kind))throw new Error(`Set kind ${kind} is registered twice`);
  if(!Array.isArray(slots)||!slots.length||slots.some(s=>typeof s!=='string'||!s))
    throw new Error(`Set kind ${kind} must declare its slots as a non-empty list of names`);
  if(new Set(slots).size!==slots.length)throw new Error(`Set kind ${kind} declares a slot twice`);
  if(typeof component!=='function'&&typeof component!=='object')throw new Error(`Set kind ${kind} has no component`);
  sets.set(kind,{kind,slots:[...slots],component,shipped});
}
export function registerElement(kind:string,component:AnyComponent,shipped=false):void{
  named(kind,'Element');
  if(elements.has(kind))throw new Error(`Element kind ${kind} is registered twice`);
  if(typeof component!=='function'&&typeof component!=='object')throw new Error(`Element kind ${kind} has no component`);
  elements.set(kind,{kind,component,shipped});
}

/** Registers a set kind: its slots (exactly the document's) and the component that lays them out. */
export function defineSet<const K extends string,const L extends readonly string[]>(
  definition:{kind:K;slots:L&SlotsOf<K,L>;component:SetDefinition<K,L>['component']}):void{
  registerSet(definition.kind,definition.slots as readonly string[],definition.component);
}
/** Registers an element kind and the component that draws its state. */
export function defineElement<const K extends string>(definition:ElementDefinition<K>):void{
  registerElement(definition.kind,definition.component);
}

export const setOf=(kind:string):RegisteredSet|undefined=>sets.get(kind);
export const elementOf=(kind:string):RegisteredElement|undefined=>elements.get(kind);
export const registeredSets=():string[]=>[...sets.keys()];
export const registeredElements=():string[]=>[...elements.keys()];

/** Refuses, naming the subject, a document the registry does not draw. */
export function checkRegistry(config:Pick<StageConfig,'stage'>):void{
  for(const [kind,declared] of Object.entries(config.stage?.sets??{})){
    const set=sets.get(kind);
    if(!set)throw new Error(`Set kind ${kind} is not registered by the stage modules (registered: ${registeredSets().join(', ')})`);
    const want=[...declared.slots].sort(),have=[...set.slots].sort();
    if(JSON.stringify(want)!==JSON.stringify(have))
      throw new Error(`Set kind ${kind} registers slots ${have.join(', ')} but the document declares ${want.join(', ')}`);
  }
  for(const kind of config.stage?.elements??[])
    if(!elements.has(kind))throw new Error(`Element kind ${kind} is not registered by the stage modules`);
}

/** Tests only: forget every registration. */
export function resetRegistry():void{sets.clear();elements.clear();}
