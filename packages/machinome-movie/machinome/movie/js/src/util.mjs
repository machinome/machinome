import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import {dirname} from 'node:path';
import {spawn} from 'node:child_process';
// The directory a source's relative paths resolve against: a movie's root, or
// the directory of a YAML episode's production settings.
export const sourceBase=e=>e.paths.base??dirname(e.paths.production);
export const hash=value=>createHash('sha256').update(value).digest('hex');
export const fileHash=async path=>hash(await readFile(path));
export async function json(path,value){await mkdir(dirname(path),{recursive:true});await writeFile(path+'.tmp',JSON.stringify(value,null,2)+'\n');await rename(path+'.tmp',path);}
export function command(program,args,options={}) {
  return new Promise((resolve,reject)=>{
    const child=spawn(program,args,{stdio:['ignore','pipe','pipe'],...options});let output='',error='';
    child.stdout?.on('data',v=>output+=v);child.stderr?.on('data',v=>error=(error+v).slice(-16000));
    child.on('error',reject);child.on('close',code=>code===0?resolve(output):reject(new Error(`${program} exited ${code}: ${error}`)));
  });
}
export async function duration(path){return Number((await command('ffprobe',['-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',path])).trim());}
