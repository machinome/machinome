// Narration belongs to a chapter, an ordered run of shots (movie-document D2).
// A YAML episode is one chapter per shot; an episode object without `chapters`
// (as unit tests build them) gets that mapping from its shots.
export const DEFAULT_SPEECH_OFFSET=.2;
const perShot=shot=>({id:shot.id,narration:shot.narration,speechOffset:shot.speechOffset??DEFAULT_SPEECH_OFFSET,
  start:shot.start,end:shot.end,shots:[shot.id]});
export const shotChapters=e=>e.shots.map(perShot);
export function chaptersOf(e){return e.chapters??shotChapters(e);}
export function chapterOf(e,shot){
  if(!e.chapters)return perShot(shot);
  const chapter=e.chapters.find(c=>c.shots.includes(shot.id));
  if(!chapter)throw new Error(`Shot ${shot.id} belongs to no chapter`);
  return chapter;
}
export const narrationOf=(e,shot)=>chapterOf(e,shot).narration;
// The shot-local instant its chapter's take starts. For the chapter's first
// shot (every YAML shot) it is exactly the chapter's offset, bit for bit.
export function takeOffset(e,shot){
  const chapter=chapterOf(e,shot);
  return chapter.start===shot.start?chapter.speechOffset:chapter.start+chapter.speechOffset-shot.start;
}
