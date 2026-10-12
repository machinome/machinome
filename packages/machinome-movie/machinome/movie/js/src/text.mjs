// The three counting rules of the movie document, as the Python side counts
// them (machinome/movie/text.py): a phrase in a narration, words in a
// phrase, a token in a source excerpt. Both character classes are ASCII.

// What a source token is: an identifier or a dotted path of identifiers.
export const TOKEN=/^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$/;
const escape=text=>text.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const bounded=text=>new RegExp(`(?<![A-Za-z0-9_])${escape(text)}(?![A-Za-z0-9_])`,'g');

// How many times `phrase` occurs in `text`, overlapping occurrences included.
export function countPhrase(text,phrase){
  let found=0,start=0;
  for(;;){start=text.indexOf(phrase,start);if(start<0)return found;found++;start++;}
}
// Where `words` occur in `phrase`, word-bounded: not preceded or followed by
// an ASCII letter, digit or underscore. A dot is a boundary.
export const boundedMatches=(text,words)=>[...text.matchAll(bounded(words))].map(m=>m.index);
export const countWords=(phrase,words)=>boundedMatches(phrase,words).length;
export const countToken=(text,token)=>boundedMatches(text,token).length;
// The text of `line` (a file line number) in an excerpt whose first line is
// `first`, or null when the line is outside it.
export function excerptLine(text,first,line){
  const lines=text.split('\n'),index=line-first;
  return index>=0&&index<lines.length?lines[index]:null;
}
// The document's kind of a JSON value, or null.
export function propKind(value){
  if(typeof value==='boolean')return 'boolean';
  if(typeof value==='number')return 'number';
  if(typeof value==='string')return 'string';
  if(Array.isArray(value))return 'list';
  if(value&&typeof value==='object')return 'object';
  return null;
}
// A narration as the narrator speaks it: every replacement applied.
export function spokenForm(text,replacements={}){
  let result=text;
  for(const [term,spoken] of Object.entries(replacements))result=result.replaceAll(term,spoken);
  return result;
}
