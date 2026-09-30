// Narration belongs to a chapter, an ordered run of shots. In the resolved
// document (a movie, or a YAML episode with one chapter per shot) chapters
// hold their shots; these read them.
export const DEFAULT_SPEECH_OFFSET=.2;
export const chaptersOf=film=>film.chapters;
// Every shot of the film in order, with its chapter.
export const shotsOf=film=>film.chapters.flatMap(chapter=>chapter.shots.map(shot=>({chapter,shot})));
export function chapterOf(film,shotId){
  const chapter=film.chapters.find(c=>c.shots.some(s=>s.id===shotId));
  if(!chapter)throw new Error(`Shot ${shotId} belongs to no chapter`);
  return chapter;
}
export const narrationOf=(film,shotId)=>chapterOf(film,shotId).narration;
// The shot-local instant its chapter's take starts. For the chapter's first
// shot (every YAML shot) it is exactly the chapter's offset, bit for bit.
export function takeOffset(film,shot){
  const chapter=chapterOf(film,shot.id);
  return chapter.start===shot.start?chapter.speechOffset:chapter.start+chapter.speechOffset-shot.start;
}
