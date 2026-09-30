// A validator for the JSON Schema keywords schema/machinome-movie-0.1.json
// uses, and no others (design D9 of the movie-document change). A test fails
// if the schema uses a keyword this file does not implement.
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

export const SCHEMA_FILE=fileURLToPath(new URL('../schema/machinome-movie-0.1.json',import.meta.url));
// Annotations (no effect on validity) and the keywords validate() implements.
export const SCHEMA_KEYWORDS=new Set(['$schema','$id','title','description','$defs','$ref','type','properties','required',
  'additionalProperties','items','anyOf','minItems','minLength','pattern']);
export const MOVIE_SCHEMA=JSON.parse(readFileSync(SCHEMA_FILE,'utf8'));
export async function loadMovieSchema(){return MOVIE_SCHEMA;}

// Every keyword the schema uses, walking subschemas (not property names).
export function schemaKeywords(schema){
  const used=new Set();
  (function walk(node){
    if(!node||typeof node!=='object'||Array.isArray(node))return;
    for(const [key,value] of Object.entries(node)){
      used.add(key);
      if(key==='properties'||key==='$defs')for(const sub of Object.values(value))walk(sub);
      else if(key==='anyOf')value.forEach(walk);
      else if(key==='items'||key==='additionalProperties')walk(value);
    }
  })(schema);
  return used;
}

const TYPES={null:v=>v===null,boolean:v=>typeof v==='boolean',string:v=>typeof v==='string',
  number:v=>typeof v==='number'&&Number.isFinite(v),integer:v=>Number.isInteger(v),
  array:v=>Array.isArray(v),object:v=>v!==null&&typeof v==='object'&&!Array.isArray(v)};
const where=path=>path.length?path.join('/'):'/';
const fail=message=>{throw new Error(message);};

// Throws the first violation, naming the field and its slash-separated path.
export function validateSchema(root,value){
  const resolveRef=ref=>{
    const match=/^#\/\$defs\/([^/]+)$/.exec(ref);
    if(!match||!root.$defs?.[match[1]])fail(`Unsupported schema reference: ${ref}`);
    return root.$defs[match[1]];
  };
  const matches=(schema,v,path)=>{try{check(schema,v,path);return true;}catch{return false;}};
  function check(schema,v,path){
    if(schema.$ref)return check(resolveRef(schema.$ref),v,path);
    if(schema.anyOf){
      if(schema.anyOf.some(branch=>matches(branch,v,path)))return;
      const titles=schema.anyOf.map(branch=>(branch.$ref?resolveRef(branch.$ref):branch).title??'another form');
      fail(`Invalid movie document: ${where(path)} must be one of: ${titles.join(', ')}`);
    }
    if(schema.type){
      const types=[].concat(schema.type);
      if(!types.some(type=>TYPES[type](v)))fail(`Invalid movie document: ${where(path)} must be ${types.join(' or ')}`);
    }
    if(typeof v==='string'){
      if(schema.minLength!==undefined&&Array.from(v).length<schema.minLength)fail(`Invalid movie document: ${where(path)} must not be empty`);
      if(schema.pattern!==undefined&&!new RegExp(schema.pattern,'u').test(v))fail(`Invalid movie document: ${where(path)} must match ${schema.pattern}`);
    }
    if(Array.isArray(v)){
      if(schema.minItems!==undefined&&v.length<schema.minItems)fail(`Invalid movie document: ${where(path)} needs at least ${schema.minItems} item${schema.minItems===1?'':'s'}`);
      if(schema.items)v.forEach((item,i)=>check(schema.items,item,[...path,i]));
    }
    if(TYPES.object(v)){
      for(const name of schema.required??[])if(!Object.hasOwn(v,name))fail(`Missing field: ${name} (${where(path)})`);
      for(const [name,item] of Object.entries(v)){
        if(schema.properties&&Object.hasOwn(schema.properties,name))check(schema.properties[name],item,[...path,name]);
        else if(schema.additionalProperties===false)fail(`Unknown field: ${name} (${where(path)})`);
        else if(schema.additionalProperties&&typeof schema.additionalProperties==='object')check(schema.additionalProperties,item,[...path,name]);
      }
    }
  }
  check(root,value,[]);
}
