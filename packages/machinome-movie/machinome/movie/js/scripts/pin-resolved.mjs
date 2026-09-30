#!/usr/bin/env node
// Writes fixtures/resolved/<name>.json from fixtures/documents/<name>.json and
// fixtures/takes/<name>/, for a person to review before committing: the Node
// suite pins the file, so it must be checked by hand, never regenerated to
// make a failing test pass. Usage: node scripts/pin-resolved.mjs NAME...
import {readFile,writeFile,mkdir,access} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {resolveMovie} from '../src/movie.mjs';

const fixtures=join(dirname(fileURLToPath(import.meta.url)),'..','fixtures');
const json=async file=>JSON.parse(await readFile(file,'utf8'));
try{
  const names=process.argv.slice(2);
  if(!names.length)throw new Error('Usage: node scripts/pin-resolved.mjs NAME...');
  for(const name of names){
    const doc=await json(join(fixtures,'documents',`${name}.json`)),takes={};
    for(const chapter of doc.chapters){
      const file=join(fixtures,'takes',name,`${chapter.id}.json`);
      if(await access(file).then(()=>true,()=>false))takes[chapter.id]=await json(file);
    }
    const out=join(fixtures,'resolved',`${name}.json`);
    await mkdir(dirname(out),{recursive:true});
    await writeFile(out,JSON.stringify(resolveMovie(doc,takes),null,2)+'\n');
    console.log(`Wrote ${out}; review it before committing.`);
  }
}catch(error){console.error(error.message);process.exitCode=1;}
