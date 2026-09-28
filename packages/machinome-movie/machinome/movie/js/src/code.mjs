import {readFile,realpath} from 'node:fs/promises';
import {resolve,dirname,relative,extname} from 'node:path';
import {execFileSync} from 'node:child_process';
import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import {hash} from './util.mjs';
import {contained} from './episode.mjs';

hljs.registerLanguage('python',api=>{
  const grammar=python(api);
  // Highlight calls as well as definitions: small declarative excerpts often
  // contain no def/class keyword. Existing string/comment modes remain intact.
  grammar.contains.push({scope:'title.function',match:/\b[A-Za-z_]\w*(?=\s*\()/});
  return grammar;
});
const need=(ok,message)=>{if(!ok)throw new Error(message);};
export async function loadSourceCode(e){
  const snippets={};
  for(const [name,source] of Object.entries(e.sourceCode??{})){
    need(source&&typeof source.file==='string',`Missing Python source file: ${name}`);
    const file=await realpath(resolve(dirname(e.paths.production),source.file));
    need(contained(e.paths.repository,file)&&extname(file)==='.py',`Python source must be inside the project: ${name}`);
    const path=relative(e.paths.repository,file),bytes=await readFile(file);
    need(/^[a-f0-9]{40}$/.test(e.model.sourceRevision),'Source code needs a full pinned model revision');
    const pinned=execFileSync('git',['show',`${e.model.sourceRevision}:${path}`],{cwd:e.paths.repository,maxBuffer:10*1024*1024});
    need(bytes.equals(pinned),`Source differs from pinned model revision: ${path}`);
    const all=bytes.toString('utf8').replace(/\r\n/g,'\n').split('\n');if(all.at(-1)==='')all.pop();
    const range=source.lines;
    need(Array.isArray(range)&&range.length===2&&range.every(Number.isInteger)&&range[0]>=1&&range[1]>=range[0]&&range[1]<=all.length,`Invalid source line range: ${name}`);
    const selected=all.slice(range[0]-1,range[1]);
    const nonblank=selected.filter(line=>line.trim());
    need(nonblank.length>0,`Empty source excerpt: ${name}`);
    const indent=Math.min(...nonblank.map(line=>line.match(/^ */)[0].length));
    const text=selected.map(line=>line.slice(Math.min(indent,line.match(/^ */)[0].length))).join('\n');
    snippets[name]={file:path,lines:range,revision:e.model.sourceRevision,fileSha256:hash(bytes),excerptSha256:hash(text),dedent:indent,text};
  }
  return snippets;
}

export function validateCode(e,shot){
  if(!shot.code)return;
  const snippet=e.sourceCode?.[shot.code.snippet];
  need(snippet,`Unknown code snippet: ${shot.code.snippet}`);
  const cues=shot.code.typing;
  need(Array.isArray(cues)&&cues.length>0,`Missing typing schedule: ${shot.id}`);
  let time=0,line=snippet.lines[0]-1;
  for(const cue of cues){
    need(Number.isFinite(cue.from)&&Number.isFinite(cue.to)&&cue.from>=time&&cue.to>cue.from&&cue.to<=shot.end-shot.start&&Number.isInteger(cue.throughLine)&&cue.throughLine>line&&cue.throughLine<=snippet.lines[1],`Invalid typing cue: ${shot.id}`);
    time=cue.to;line=cue.throughLine;
  }
  need(line===snippet.lines[1],`Typing must complete the source excerpt: ${shot.id}`);
}

export function codeAt(e,shot,local){
  if(!shot.code)return null;
  const snippet=e.sourceCode[shot.code.snippet],lines=snippet.text.split('\n');
  let count=0,prior=0;
  for(const cue of shot.code.typing){
    const end=Array.from(lines.slice(0,cue.throughLine-snippet.lines[0]+1).join('\n')).length;
    if(local<cue.from)break;
    count=prior+Math.floor((end-prior)*Math.min(1,(local-cue.from)/(cue.to-cue.from)));
    if(local<cue.to)break;
    prior=end;
  }
  const text=Array.from(snippet.text).slice(0,count).join('');
  return {file:snippet.file,firstLine:snippet.lines[0],lastLine:snippet.lines[1],text,
    html:hljs.highlight(text,{language:'python',ignoreIllegals:true}).value,
    cursor:count<Array.from(snippet.text).length&&Math.floor(local*2)%2===0};
}
