// Word timing is derived from the exact cached take, never from reading speed.
import {ease} from './easing.mjs';
import {takeOffset,shotsOf} from './chapters.mjs';
import {boundedMatches,spokenForm as spokenText} from './text.mjs';

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

export function validateSpokenPair({text,phrase=text,narration,replacements={},shotId='shot',index=0,where=`overlay #${index} in shot ${shotId}`}){
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
    shotStart=0,fps=30,shotId='shot',index=0,where}=input;
  const pair=validateSpokenPair({text,phrase,narration,replacements,shotId,index,where});
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

// A movie's emphasis (design D2.2): each spoken part's onset in the chapter's
// take, and the instant the phrase's last character ends plus the hold, in
// shot-local seconds from `offset` (where the take starts in the shot).
export function emphasisTiming({phrase,words,alignment,replacements={},offset=0,hold=0,where='emphasis'}){
  const a=alignment.text!==undefined?alignment:validateAlignment(alignment,where);
  const spoken=spokenText(phrase,replacements),at=occurrence(a.text,spoken,where);
  const onsets=words.map((word,index)=>{
    const form=spokenText(word,replacements),found=boundedMatches(spoken,form);
    need(found.length===1,`${where}, words[${index}].spoken: the spoken words '${word}' are ${found.length?'ambiguous in':'absent from'} the recorded phrase '${spoken}'`);
    const letter=/[\p{L}\p{N}]/u.exec(form);
    need(letter,`${where}, words[${index}].spoken: no spoken letter or digit in '${word}'`);
    return offset+a.starts[codePointIndex(a.text,at+found[0]+letter.index)];
  });
  const clear=offset+a.ends[codePointIndex(a.text,at+spoken.length)-1]+hold;
  return {onsets,clear};
}

// The CLI may render at a different fps from the film's declared grid. A
// valid check at 30 fps does not imply every revealed word is filmed at 10.
export function validateWordFramesAtFps(film,fps){
  for(const {shot} of shotsOf(film))shot.cues.forEach((cue,i)=>cue.actions.forEach((action,j)=>{
    const reveal=action.reveal;if(!reveal)return;
    const where=action.overlay!==undefined?`overlay #${action.overlay} in shot ${shot.id}`:`shot ${shot.id}, cues[${i}].actions[${j}]`;
    const title=film.chapters.find(c=>c.shots.includes(shot)).elements[action.element];
    const words=splitWords(title.text).filter(p=>p.word);let shown=0;
    if(reveal.timing==='spoken'&&!reveal.onsets)throw new Error(`Word timing is not resolved: shot ${shot.id}`);
    for(let frame=Math.ceil((shot.start+cue.at)*fps-1e-9);
      frame/fps<shot.start+cue.until-1e-9&&frame/fps<shot.end-1e-9;frame++){
      const local=frame/fps-shot.start;
      const count=reveal.timing==='spoken'?reveal.onsets.filter(t=>local>=Math.max(cue.at,t)-1e-9).length
        :evenCount(words.length,local,cue.at,reveal.duration,reveal.ease??'linear');
      shown=Math.max(shown,count);
    }
    need(shown>=words.length,`Word ${words.at(-1).text} appears on no ${fps} fps output frame: ${where}`);
  }));
}

// How many characters of an excerpt's text a panel has typed at shot-local
// `time`, from the typing actions [{at, over, throughLine}] of its chapter so
// far (each starts where the one before stopped).
export function typedCount(text,firstLine,typings,time){
  const lines=text.split('\n');let count=0,prior=0;
  for(const cue of typings){
    const end=Array.from(lines.slice(0,cue.throughLine-firstLine+1).join('\n')).length;
    if(time<cue.at)break;
    count=prior+Math.floor((end-prior)*Math.min(1,(time-cue.at)/cue.over));
    if(time<cue.at+cue.over)break;
    prior=end;
  }
  return count;
}

// A YAML film's measured timing (spoken reveals and emphasis), from the exact
// cached take that speech uses; a movie's is resolved with it (design D3).
// Records which take each measured shot read; the numbers are immutable inputs
// to frameAt, not page state.
export async function resolveWordTiming(film,read){
  const timing={};
  for(const {chapter,shot} of shotsOf(film)){
    const measured=shot.cues.flatMap(cue=>cue.actions.filter(a=>a.action==='emphasize'||a.reveal?.timing==='spoken').map(a=>({cue,action:a})));
    if(!measured.length)continue;
    const take=await read(shot);
    timing[shot.id]={sha256:take.sha256};
    if(film.source==='movie')continue;
    const offset=takeOffset(film,shot),duration=shot.end-shot.start,replacements=film.audio?.replacements??{};
    const emphases=[];
    for(const {cue,action} of measured){
      if(action.action==='emphasize'){
        const element=chapter.elements[action.element],snippet=film.excerpts[element.source];
        const cues=resolveEmphasis({source:snippet.text,firstLine:snippet.lines[0],line:action.line,phrase:action.phrase,
          words:action.words.map(w=>w.token),alignment:take.alignment,offset,hold:action.hold??0,narration:chapter.narration,
          shotId:shot.id,shotDuration:duration,replacements});
        const typings=shot.cues.flatMap(c=>c.actions.filter(a=>a.action==='type'&&a.element===action.element).map(a=>({...a,at:c.at})));
        for(const word of cues)
          need(codePointIndex(snippet.text,word.end)<=typedCount(snippet.text,snippet.lines[0],typings,word.from),`Source word ${word.word} is not yet typed at its onset: shot ${shot.id}`);
        const first=cues[0].from,last=cues[0].to;
        for(const prior of emphases)need(first>=prior.to||last<=prior.from,`Emphasis cues overlap in shot ${shot.id}`);
        emphases.push({from:first,to:last});
        cues.forEach((word,k)=>{action.words[k].at=word.from;});
        action.until=last;cue.at=first;
      }else{
        const title=chapter.elements[action.element];
        action.reveal.onsets=spokenOnsets({text:title.text,phrase:action.reveal.phrase??title.text,narration:chapter.narration,
          replacements,alignment:take.alignment,offset,from:cue.at,to:cue.until,shotStart:shot.start,fps:film.output.fps,
          shotId:shot.id,index:action.overlay});
      }
    }
  }
  film.wordTiming=timing;
  return timing;
}
