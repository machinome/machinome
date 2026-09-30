// Word timing is derived from the exact cached take, never from reading speed.
import {ease} from './easing.mjs';
import {narrationOf,takeOffset} from './chapters.mjs';

const need=(ok,message)=>{if(!ok)throw new Error(message);};
const finite=n=>typeof n==='number'&&Number.isFinite(n);
const codePointIndex=(text,index)=>Array.from(text.slice(0,index)).length;
const normalize=word=>word.replace(/^\p{P}+|\p{P}+$/gu,'').toLocaleLowerCase();
const spokenForm=(text,replacements={})=>{
  let result=text;
  for(const [term,spoken] of Object.entries(replacements))result=result.replaceAll(term,spoken);
  return result;
};

export function splitWords(text){
  const parts=[];
  for(const match of text.matchAll(/\S+|\s+/gu))parts.push({text:match[0],word:!/^\s+$/u.test(match[0]),start:match.index,end:match.index+match[0].length});
  return parts;
}

export function validateSpokenPair({text,phrase=text,narration,replacements={},shotId='shot',index=0}){
  const where=`overlay #${index} in shot ${shotId}`;
  need(typeof phrase==='string'&&phrase.length>0&&typeof narration==='string',`Missing spoken phrase: ${where}`);
  const pos=narration.indexOf(phrase);
  need(pos>=0,`Spoken phrase is absent from narration: ${where} (${phrase})`);
  need(narration.indexOf(phrase,pos+1)<0,`Ambiguous spoken phrase in narration: ${where} (${phrase})`);
  const displayed=splitWords(text).filter(p=>p.word),written=splitWords(phrase).filter(p=>p.word);
  for(const part of displayed)need(normalize(part.text),`Punctuation-only word cannot be spoken: ${part.text} (${where})`);
  need(displayed.length===written.length,`Displayed and spoken phrase word counts differ: ${where}`);
  for(let i=0;i<written.length;i++){
    need(normalize(displayed[i].text)===normalize(written[i].text),
      `Displayed word ${displayed[i].text} differs from spoken ${written[i].text}: ${where}`);
  }
  const parts=splitWords(phrase),pieces=parts.map(p=>p.word?spokenForm(p.text,replacements):p.text);
  need(pieces.join('')===spokenForm(phrase,replacements),`A replacement spans two words of the spoken phrase: ${where}`);
  return {where,written,parts,pieces,spoken:pieces.join('')};
}

export function validateAlignment(alignment,where='speech'){
  const a=alignment,chars=a?.characters,starts=a?.character_start_times_seconds,ends=a?.character_end_times_seconds;
  need(Array.isArray(chars)&&chars.length>0&&Array.isArray(starts)&&Array.isArray(ends)&&
    starts.length===chars.length&&ends.length===chars.length,`Invalid alignment: ${where}`);
  for(let i=0;i<chars.length;i++)need(typeof chars[i]==='string'&&Array.from(chars[i]).length===1&&
    finite(starts[i])&&finite(ends[i])&&starts[i]>=0&&ends[i]>=starts[i]&&
    (i===0||(starts[i]>=starts[i-1]&&ends[i]>=ends[i-1])),`Invalid alignment timing: ${where}`);
  return {text:chars.join(''),starts,ends};
}

function occurrence(haystack,needle,where){
  const first=haystack.indexOf(needle);
  need(needle.length>0&&first>=0,`Missing spoken phrase in recorded speech: ${where} (${needle})`);
  need(haystack.indexOf(needle,first+1)<0,`Ambiguous spoken phrase in recorded speech: ${where} (${needle})`);
  return first;
}

export function spokenOnsets(input){
  const {text,phrase=text,narration,alignment,replacements={},offset=0,from=0,to=Infinity,
    shotStart=0,fps=30,shotId='shot',index=0}=input;
  const pair=validateSpokenPair({text,phrase,narration,replacements,shotId,index});
  const a=validateAlignment(alignment,pair.where),at=occurrence(a.text,pair.spoken,pair.where);
  let position=0,prior=-Infinity;
  const onsets=[];
  for(let i=0;i<pair.parts.length;i++){
    const part=pair.parts[i],piece=pair.pieces[i];
    if(part.word){
      const first=/[\p{L}\p{N}]/u.exec(piece);
      need(first,`No spoken letter or digit for ${part.text}: ${pair.where}`);
      const char=codePointIndex(a.text,at+position+first.index),onset=offset+a.starts[char];
      need(onset>prior,`Word onsets must increase in alignment: ${pair.where} (${part.text})`);
      need(onset>from-1/fps+1e-9,`Word ${part.text} is spoken a frame or more before its cue: ${pair.where}`);
      const visible=shotStart+Math.max(from,onset),frame=Math.ceil(visible*fps-1e-9)/fps;
      need(frame<shotStart+to-1e-9,`Word ${part.text} appears on no global output frame before its cue ends: ${pair.where}`);
      onsets.push(onset);prior=onset;
    }
    position+=piece.length;
  }
  return onsets;
}

export function evenCount(count,local,from,duration,name='linear'){
  if(local<from)return 0;
  return Math.min(count,Math.floor(count*ease(name,(local-from)/duration))+1);
}

export function fadeOpacity(cue,local){
  const first=cue.enter?ease(cue.enter.ease??'smooth',(local-cue.from)/cue.enter.duration):1;
  const last=cue.leave?1-ease(cue.leave.ease??'smooth',(local-(cue.to-cue.leave.duration))/cue.leave.duration):1;
  return Math.min(first,last);
}

export function resolveEmphasis({source,firstLine,line,phrase,words,alignment,offset=0,hold=0,narration,replacements={},
  shotId='shot',shotDuration=Infinity}){
  const where=`emphasis in shot ${shotId}`;
  need(typeof phrase==='string'&&phrase.length>0&&typeof narration==='string',`Missing phrase: ${where}`);
  const inWriting=narration.indexOf(phrase);
  need(inWriting>=0&&narration.indexOf(phrase,inWriting+1)<0,`Missing or ambiguous phrase in narration: ${where}`);
  const spoken=spokenForm(phrase,replacements);
  const a=validateAlignment(alignment,where),at=occurrence(a.text,spoken,where);
  const lines=source.split('\n'),target=lines[line-firstLine];
  need(Number.isInteger(line)&&typeof target==='string',`Missing source token line ${line}: ${where}`);
  need(Array.isArray(words)&&words.length>0&&new Set(words).size===words.length,`Emphasis words must be distinct: ${where}`);
  need(finite(hold)&&hold>=0,`Invalid emphasis hold: ${where}`);
  const lineStart=lines.slice(0,line-firstLine).reduce((n,s)=>n+s.length+1,0);
  const clear=offset+a.ends[codePointIndex(a.text,at+spoken.length)-1]+hold;
  need(clear<=shotDuration+1e-9,`Emphasis clears after shot ${shotId} ends`);
  const cues=words.map(word=>{
    need(/^[A-Za-z_]\w*$/.test(word),`Invalid source identifier ${word}: ${where}`);
    const sourceMatches=[...target.matchAll(new RegExp(`\\b${word}\\b`,'g'))];
    need(sourceMatches.length===1,`Missing or ambiguous source token: ${word} (${where})`);
    const spokenMatches=[...spoken.matchAll(new RegExp(`\\b${word}\\b`,'g'))];
    need(spokenMatches.length===1,`Missing or ambiguous spoken token: ${word} (${where})`);
    const start=lineStart+sourceMatches[0].index,spokenStart=at+spokenMatches[0].index;
    const char=codePointIndex(a.text,spokenStart),endChar=codePointIndex(a.text,spokenStart+word.length)-1;
    return {word,line,start,end:start+word.length,from:offset+a.starts[char],wordEnd:offset+a.ends[endChar],to:clear};
  });
  for(let i=1;i<cues.length;i++)need(cues[i].from>cues[i-1].from,`Words must follow narration order: ${where}`);
  return cues;
}

export const activeEmphasis=(cues,time)=>cues.filter(c=>time>=c.from-1e-9&&time<c.to-1e-9);

// The CLI may render at a different fps from the episode's declared grid.
// A valid check at 30 fps does not imply all words are filmed at 10 fps.
export function validateWordFramesAtFps(e,fps){
  for(const shot of e.shots)for(const [index,cue] of (shot.overlays??[]).entries()){
    if(!cue.reveal)continue;
    const words=splitWords(cue.text).filter(p=>p.word);let shown=0;
    const onsets=cue.reveal.timing==='spoken'?e.wordTiming?.[shot.id]?.overlays?.[index]?.onsets:null;
    if(cue.reveal.timing==='spoken'&&!onsets)throw new Error(`Word timing is not resolved: shot ${shot.id}`);
    for(let frame=Math.ceil((shot.start+cue.from)*fps-1e-9);
      frame/fps<shot.start+cue.to-1e-9&&frame/fps<shot.end-1e-9;frame++){
      const local=frame/fps-shot.start;
      const count=onsets?onsets.filter(t=>local>=Math.max(cue.from,t)-1e-9).length
        :evenCount(words.length,local,cue.from,cue.reveal.duration,cue.reveal.ease??'linear');
      shown=Math.max(shown,count);
    }
    need(shown>=words.length,
      `Word ${words.at(-1).text} appears on no ${fps} fps output frame: overlay #${index} in shot ${shot.id}`);
  }
}

function typedCount(snippet,typing,time){
  const lines=snippet.text.split('\n');let count=0,prior=0;
  for(const cue of typing){
    const end=Array.from(lines.slice(0,cue.throughLine-snippet.lines[0]+1).join('\n')).length;
    if(time<cue.from)break;
    count=prior+Math.floor((end-prior)*Math.min(1,(time-cue.from)/(cue.to-cue.from)));
    if(time<cue.to)break;
    prior=end;
  }
  return count;
}

// Resolve only shots with measured cues, from the exact cached take that speech
// uses. The resulting numbers are immutable inputs to frameAt, not page state.
export async function resolveWordTiming(e,read){
  const timing={};
  for(const shot of e.shots){
    const spoken=(shot.overlays??[]).flatMap((cue,index)=>cue.reveal?.timing==='spoken'?[{cue,index}]:[]);
    const emphases=shot.code?.emphasis??[];
    if(!spoken.length&&!emphases.length)continue;
    const take=await read(shot),entry={sha256:take.sha256,overlays:{},emphasis:[]};
    // The shot's chapter take, starting at this shot-local instant (movie-document D2).
    const offset=takeOffset(e,shot),narration=narrationOf(e,shot),shotDuration=shot.end-shot.start;
    for(const {cue,index} of spoken){
      entry.overlays[index]={onsets:spokenOnsets({text:cue.text,phrase:cue.reveal.phrase??cue.text,
        narration,replacements:e.audio?.replacements??{},alignment:take.alignment,
        offset,from:cue.from,to:cue.to,shotStart:shot.start,fps:e.output.fps,shotId:shot.id,index})};
    }
    if(emphases.length){
      const snippet=e.sourceCode[shot.code.snippet];
      for(const [index,cue] of emphases.entries()){
        const cues=resolveEmphasis({source:snippet.text,firstLine:snippet.lines[0],...cue,
          alignment:take.alignment,offset,narration,shotId:shot.id,shotDuration,
          replacements:e.audio?.replacements??{}});
        for(const word of cues){
          const typed=typedCount(snippet,shot.code.typing,word.from);
          need(codePointIndex(snippet.text,word.end)<=typed,`Source word ${word.word} is not yet typed at its onset: shot ${shot.id}`);
        }
        const first=cues[0]?.from,last=cues[0]?.to;
        for(const prior of entry.emphasis)need(first>=prior.to||last<=prior.from,`Emphasis cues overlap in shot ${shot.id}`);
        entry.emphasis.push({index,from:first,to:last,cues});
      }
    }
    timing[shot.id]=entry;
  }
  e.wordTiming=timing;
  return timing;
}
