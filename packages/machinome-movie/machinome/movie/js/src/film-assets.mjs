// What a film's stage page is served, and the handler that serves it (the
// live-server change, design D2): the renderer's sessions and a live session
// serve the same files the same way. Moved from src/render.mjs unchanged.
//
//   filmFiles(film, viewer, bundle) -> {paths, hashes}
//     paths   Map of URL path to file: the viewer bundle (/viewer.js), the
//             export's manifest (/model/manifest.json) and the files the
//             viewer reads from it (src/export.mjs), the stage bundle
//             (/stage.js, /stage.css), the page (/), each still
//             (/pictures/stills/<name>) and each extracted clip frame
//             (/pictures/clips/<name>/<n>.png)
//     hashes  the SHA-256 of every file but the clip frames, by URL, and
//             each clip's extraction key under /pictures/clips/<name>; the
//             shot cache's key reads them
//   clipUses(film) -> [{name, inPoint, span}]: the clip spans the film shows
//   filmAssets({paths, config, onError}) -> (req, res) handler
import {readFile} from 'node:fs/promises';
import {resolve,dirname,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {filmShots,shotActions,joinShows} from './timeline.mjs';
import {fileHash} from './util.mjs';
import {exportFiles} from './export.mjs';

const here=dirname(fileURLToPath(import.meta.url));
// The stage page: three empty layers, the stylesheet, the viewer, the stage.
export const FILM_PAGE=resolve(here,'film.html');
const near=(a,b)=>Math.abs(a-b)<1e-9;

export async function filmFiles(film,viewer,bundle) {
  const paths=new Map([['/viewer.js',resolve(viewer)],['/model/manifest.json',film.paths.manifest],
    ['/stage.js',bundle.js],['/stage.css',bundle.css],['/',FILM_PAGE],
    ...await exportFiles(film.paths.manifest)]);
  for(const [name,media] of Object.entries(film.pictureMedia?.stills??{}))
    paths.set(`/pictures/stills/${name}`,media.file);
  for(const [name,media] of Object.entries(film.pictureMedia?.clips??{}))
    for(const n of media.extraction?.frames??[])
      paths.set(`/pictures/clips/${name}/${String(n).padStart(6,'0')}.png`,
        resolve(media.extraction.dir,`${String(n).padStart(6,'0')}.png`));
  const hashes={};for(const [url,file]of paths){
    if(url.startsWith('/pictures/clips/'))continue;
    hashes[url]=await fileHash(file);
  }
  for(const [name,media] of Object.entries(film.pictureMedia?.clips??{}))
    if(media.extraction)hashes[`/pictures/clips/${name}`]=media.extraction.key;
  return {paths,hashes};
}

// The clip spans a film shows: each picture's cue, and the continuation a
// transition shows past its shot's end.
export function clipUses(film){
  const shots=filmShots(film);
  return shots.flatMap(({chapter,shot},i)=>shotActions(shot).flatMap(({cue,action})=>{
    const element=chapter.elements[action.element];
    if(element?.kind!=='picture'||element.clip===undefined)return [];
    const continuation=near(cue.until,shot.end-shot.start)?joinShows(shots[i+1]?.shot.transition):0;
    return [{name:element.clip,inPoint:element.inPoint??0,span:cue.until-cue.at+continuation}];
  }));
}

const TYPES={'.js':'text/javascript','.css':'text/css','.html':'text/html','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'};
// The handler: the stage config at /config.json, no favicon, every path of
// the map with its type; a failure answers 500 and is reported to onError.
export function filmAssets({paths,config,onError=()=>{}}){
  return async(req,res)=>{
    try{
      const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
      if(path==='/config.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(config));return;}
      if(path==='/favicon.ico'){res.writeHead(204);res.end();return;}
      const file=paths.get(path);if(!file){res.writeHead(404);res.end('Not found');return;}
      res.setHeader('Content-Type',TYPES[extname(file)]??'application/octet-stream');
      res.end(await readFile(file));
    }catch(error){onError(error);res.writeHead(500);res.end('Asset error');}
  };
}
