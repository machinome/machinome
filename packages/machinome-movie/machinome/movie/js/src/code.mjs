import {readFile,realpath} from 'node:fs/promises';
import {resolve,dirname,relative,extname} from 'node:path';
import {execFileSync} from 'node:child_process';
import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import {hash} from './util.mjs';
import {contained} from './episode.mjs';
import {formatAtLeast,typedAt,tokenRange} from './timeline.mjs';
import {sourceBase} from './util.mjs';

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
    const file=await realpath(resolve(sourceBase(e),source.file));
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
  const modern=formatAtLeast(e,'machinome-video-draft/0.4');
  if(!modern&&shot.code.emphasis!==undefined)throw new Error(`Text animation needs format machinome-video-draft/0.4: shot ${shot.id}`);
  if(modern)for(const key of Object.keys(shot.code))need(['snippet','typing','emphasis'].includes(key),`Unknown code field: ${key} (shot ${shot.id})`);
  const snippet=e.sourceCode?.[shot.code.snippet];
  need(snippet,`Unknown code snippet: ${shot.code.snippet}`);
  const cues=shot.code.typing;
  need(Array.isArray(cues)&&cues.length>0,`Missing typing schedule: ${shot.id}`);
  let time=0,line=snippet.lines[0]-1;
  for(const [index,cue] of cues.entries()){
    if(modern)for(const key of Object.keys(cue))need(['from','to','throughLine'].includes(key),`Unknown typing cue field: ${key} (typing cue #${index} in shot ${shot.id})`);
    need(Number.isFinite(cue.from)&&Number.isFinite(cue.to)&&cue.from>=time&&cue.to>cue.from&&cue.to<=shot.end-shot.start&&Number.isInteger(cue.throughLine)&&cue.throughLine>line&&cue.throughLine<=snippet.lines[1],`Invalid typing cue: ${shot.id}`);
    time=cue.to;line=cue.throughLine;
  }
  need(line===snippet.lines[1],`Typing must complete the source excerpt: ${shot.id}`);
  if(shot.code.emphasis!==undefined){
    need(Array.isArray(shot.code.emphasis),`Emphasis must be a list: shot ${shot.id}`);
    for(const [index,cue] of shot.code.emphasis.entries()){
      const where=`emphasis cue #${index} in shot ${shot.id}`;
      need(cue&&typeof cue==='object'&&!Array.isArray(cue),`Invalid ${where}`);
      for(const key of Object.keys(cue))need(['line','phrase','words','hold'].includes(key),`Unknown emphasis field: ${key} (${where})`);
      need(Number.isInteger(cue.line)&&cue.line>=snippet.lines[0]&&cue.line<=snippet.lines[1],`Emphasis line outside snippet: ${where}`);
      const narration=shot.narration;
      need(typeof cue.phrase==='string'&&cue.phrase.length>0&&narration.includes(cue.phrase)&&
        narration.indexOf(cue.phrase)===narration.lastIndexOf(cue.phrase),`Missing or ambiguous emphasis phrase: ${where}`);
      need(Array.isArray(cue.words)&&cue.words.length>0&&new Set(cue.words).size===cue.words.length&&
        cue.words.every(w=>typeof w==='string'&&/^[A-Za-z_]\w*$/.test(w)),`Invalid emphasis words: ${where}`);
      need(Number.isFinite(cue.hold)&&cue.hold>=0,`Invalid emphasis hold: ${where}`);
      for(const word of cue.words){
        const occurrences=[...cue.phrase.matchAll(new RegExp(`\\b${word}\\b`,'g'))];
        need(occurrences.length===1,`Missing or ambiguous spoken token ${word}: ${where}`);
      }
    }
  }
}

export function validateCodeSource(e,shot){
  if(!shot.code?.emphasis?.length)return;
  const snippet=e.sourceCode[shot.code.snippet],lines=snippet.text.split('\n');
  for(const [index,cue] of shot.code.emphasis.entries()){
    const line=lines[cue.line-snippet.lines[0]],where=`emphasis cue #${index} in shot ${shot.id}`;
    need(typeof line==='string',`Emphasis line outside snippet: ${where}`);
    for(const word of cue.words)
      need([...line.matchAll(new RegExp(`\\b${word}\\b`,'g'))].length===1,
        `Missing or ambiguous source token ${word}: ${where}`);
  }
}

// A source panel's state at shot-local time (design D4): the typed text,
// continuing where its chapter's typing stopped, its highlighted markup, the
// cursor, and the tokens its active emphasis lights.
export function sourceState(film,chapter,shot,key,element,local){
  const snippet=film.excerpts?.[element.source];
  if(!snippet)throw new Error(`Source excerpt is not loaded: ${element.source} in shot ${shot.id}`);
  const count=typedAt(film,chapter,shot,key,local),total=Array.from(snippet.text).length;
  const text=Array.from(snippet.text).slice(0,count).join('');
  const emphasis=[];
  shot.cues.forEach(cue=>cue.actions.forEach(action=>{
    if(action.element!==key||action.action!=='emphasize')return;
    if(action.until===undefined||action.words.some(w=>w.at===undefined))throw new Error(`Word timing is not resolved: shot ${shot.id}`);
    for(const word of action.words)if(local>=word.at-1e-9&&local<action.until-1e-9)
      emphasis.push({token:word.token,...tokenRange(snippet,word.token,action.line)});
  }));
  emphasis.sort((a,b)=>a.start-b.start);
  return sourceLook(snippet,text,count<total&&Math.floor(local*2)%2===0,emphasis);
}
const sourceLook=(snippet,text,cursor,emphasis)=>({kind:'source',file:snippet.file,firstLine:snippet.lines[0],lastLine:snippet.lines[1],text,
  html:hljs.highlight(text,{language:'python',ignoreIllegals:true}).value,cursor,emphasis});
// A source panel wholly typed, as its state is once typing completes: the
// whole excerpt's markup, no cursor, nothing lit. What `check` measures the
// code's size on (ADR-017); it depends on no take.
export function wholeSource(excerpts,name){
  const snippet=excerpts?.[name];
  if(!snippet)throw new Error(`Source excerpt is not loaded: ${name}`);
  return sourceLook(snippet,snippet.text,false,[]);
}
