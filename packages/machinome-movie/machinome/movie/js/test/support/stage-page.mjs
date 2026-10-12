// The stage page booted with a given config, for the refusals the stage makes
// at mount: the movie's bundle (built as the renderer builds it), the page,
// the viewer, the model and the stills served by the run's one asset server to its one
// Chromium, with `/config.json` as the test writes it. Not a test file: it
// registers no tests.
import {readFile} from 'node:fs/promises';
import {extname,join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {sharedStage} from './stage.mjs';
import {buildFilmStage} from '../../src/stage-build.mjs';
import {stageConfig} from '../../src/render.mjs';

const PAGE=join(dirname(fileURLToPath(import.meta.url)),'..','..','src','film.html');
const TYPES={'.js':'text/javascript','.css':'text/css','.html':'text/html','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'};

// Boots the page and returns what it reports: `error` (window.filmError) or
// null when window.film is ready; `edit(config)` changes the config first.
export async function bootStage(film,{viewer,edit=config=>config,width=640}){
  const {browser,assets}=await sharedStage();
  const bundle=await buildFilmStage(film);
  const config=edit(structuredClone(stageConfig(film)));
  const files=new Map([['/',PAGE],['/stage.js',bundle.js],['/stage.css',bundle.css],['/viewer.js',viewer],
    ['/model/manifest.json',film.paths.manifest],
    ...Object.entries(film.pictureMedia?.stills??{}).map(([name,media])=>[`/pictures/stills/${encodeURIComponent(name)}`,media.file])]);
  const release=assets.mount(async(req,res)=>{
    const path=new URL(req.url,'http://localhost').pathname;
    if(path==='/config.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(config));return;}
    const file=files.get(path);
    if(!file){res.writeHead(404);res.end();return;}
    res.setHeader('Content-Type',TYPES[extname(file)]??'application/octet-stream');res.end(await readFile(file));
  });
  const page=await browser.newPage({viewport:{width,height:Math.round(width*9/16)}});
  try{
    await page.goto(`${assets.origin}/`);
    await page.waitForFunction(()=>window.film||window.filmError,{},{timeout:60000});
    return {error:await page.evaluate(()=>window.filmError??null),ready:await page.evaluate(()=>Boolean(window.film))};
  }finally{await page.close();release();}
}
