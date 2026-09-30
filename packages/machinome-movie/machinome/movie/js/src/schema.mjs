// A validator for the JSON Schema keywords schema/machinome-movie-0.2.json
// uses, and no others (design D1 of the react-stage change). A test fails if
// the schema uses a keyword this file does not implement.
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

export const SCHEMA_FILE=fileURLToPath(new URL('../schema/machinome-movie-0.2.json',import.meta.url));
// Annotations (no effect on validity) and the keywords validate() implements.
export const SCHEMA_KEYWORDS=new Set(['$schema','$id','title','description','$defs','$ref','type','properties','required',
  'additionalProperties','propertyNames','items','anyOf','oneOf','enum','minItems','maxItems','minLength','pattern',
  'minimum','exclusiveMinimum']);
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
      else if(key==='anyOf'||key==='oneOf')value.forEach(walk);
      else if(key==='items'||key==='additionalProperties'||key==='propertyNames')walk(value);
    }
  })(schema);
  return used;
}

const TYPES={null:v=>v===null,boolean:v=>typeof v==='boolean',string:v=>typeof v==='string',
  number:v=>typeof v==='number'&&Number.isFinite(v),integer:v=>Number.isInteger(v),
  array:v=>Array.isArray(v),object:v=>v!==null&&typeof v==='object'&&!Array.isArray(v)};
// A place in the document in the words refusals use: the chapter and shot by
// id, then the field's path inside them (cues[1].actions[0].enter).
export function describePath(root,path){
  const words=[];let node=root,i=0;
  while(i<path.length){
    const key=path[i];
    if((key==='chapters'||key==='shots')&&Number.isInteger(path[i+1])){
      node=node?.[key]?.[path[i+1]];
      words.push(`${key==='chapters'?'chapter':'shot'} ${node?.id??`#${path[i+1]}`}`);
      i+=2;continue;
    }
    const rest=path.slice(i).map((p,j)=>Number.isInteger(p)?`[${p}]`:(j?`.${p}`:p)).join('');
    words.push(`field ${rest}`);break;
  }
  return words.join(', ')||'the top level';
}
const fail=message=>{throw new Error(message);};

// Throws the first violation, naming the field and where it is.
export function validateSchema(root,value){
  const where=path=>describePath(value,path);
  const resolveRef=ref=>{
    const match=/^#\/\$defs\/([^/]+)$/.exec(ref);
    if(!match||!root.$defs?.[match[1]])fail(`Unsupported schema reference: ${ref}`);
    return root.$defs[match[1]];
  };
  const errorOf=(schema,v,path)=>{try{check(schema,v,path);return null;}catch(error){return error;}};
  const titleOf=branch=>(branch.$ref?resolveRef(branch.$ref):branch).title??'another form';
  function check(schema,v,path){
    if(schema.$ref)return check(resolveRef(schema.$ref),v,path);
    if(schema.anyOf){
      if(schema.anyOf.some(branch=>!errorOf(branch,v,path)))return;
      fail(`Invalid movie document: ${where(path)} must be one of: ${schema.anyOf.map(titleOf).join(', ')}`);
    }
    if(schema.oneOf){
      const errors=schema.oneOf.map(branch=>errorOf(branch,v,path)),passed=errors.filter(e=>!e).length;
      if(passed>1)fail(`Invalid movie document: ${where(path)} matches more than one of: ${schema.oneOf.map(titleOf).join(', ')}`);
      if(passed===0){
        // Name the field: the error of the branch that got furthest (an object
        // of the right shape with one wrong field), else the branch titles.
        const deep=errors.find(e=>/^(Unknown field|Missing field)/.test(e.message)&&TYPES.object(v));
        const untitled=schema.oneOf.every(branch=>!(branch.$ref?resolveRef(branch.$ref):branch).title);
        if(untitled&&TYPES.object(v)){
          const field=Object.keys(v).find(name=>!schema.oneOf.some(branch=>{
            const b=branch.$ref?resolveRef(branch.$ref):branch;return b.properties&&Object.hasOwn(b.properties,name);}));
          if(field!==undefined)fail(`Unknown field: ${field} (${where(path)})`);
          if(deep)throw deep;
        }
        fail(`Invalid movie document: ${where(path)} must be one of: ${schema.oneOf.map(titleOf).join(', ')}`);
      }
    }
    if(schema.type){
      const types=[].concat(schema.type);
      if(!types.some(type=>TYPES[type](v)))fail(`Invalid movie document: ${where(path)} must be ${types.join(' or ')}`);
    }
    if(schema.enum&&!schema.enum.some(item=>item===v))fail(`Invalid movie document: ${where(path)} must be one of ${schema.enum.join(', ')}, not ${JSON.stringify(v)}`);
    if(typeof v==='string'){
      if(schema.minLength!==undefined&&Array.from(v).length<schema.minLength)fail(`Invalid movie document: ${where(path)} must not be empty`);
      if(schema.pattern!==undefined&&!new RegExp(schema.pattern,'u').test(v))fail(`Invalid movie document: ${where(path)} must match ${schema.pattern}, not ${JSON.stringify(v)}`);
    }
    if(TYPES.number(v)){
      if(schema.minimum!==undefined&&v<schema.minimum)fail(`Invalid movie document: ${where(path)} must be at least ${schema.minimum}`);
      if(schema.exclusiveMinimum!==undefined&&!(v>schema.exclusiveMinimum))fail(`Invalid movie document: ${where(path)} must be greater than ${schema.exclusiveMinimum}`);
    }
    if(Array.isArray(v)){
      if(schema.minItems!==undefined&&v.length<schema.minItems)fail(`Invalid movie document: ${where(path)} needs at least ${schema.minItems} item${schema.minItems===1?'':'s'}`);
      if(schema.maxItems!==undefined&&v.length>schema.maxItems)fail(`Invalid movie document: ${where(path)} takes at most ${schema.maxItems} item${schema.maxItems===1?'':'s'}`);
      if(schema.items)v.forEach((item,i)=>check(schema.items,item,[...path,i]));
    }
    if(TYPES.object(v)){
      for(const name of schema.required??[])if(!Object.hasOwn(v,name))fail(`Missing field: ${name} (${where(path)})`);
      for(const [name,item] of Object.entries(v)){
        if(schema.propertyNames)check(schema.propertyNames,name,[...path,name]);
        if(schema.properties&&Object.hasOwn(schema.properties,name))check(schema.properties[name],item,[...path,name]);
        else if(schema.additionalProperties===false)fail(`Unknown field: ${name} (${where(path)})`);
        else if(schema.additionalProperties&&typeof schema.additionalProperties==='object')check(schema.additionalProperties,item,[...path,name]);
      }
    }
  }
  check(root,value,[]);
}
