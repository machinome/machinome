// A clocked take, pure (docs/movie-document.md, "The take"; the pose-a-take
// change, design D2 and D3; ADR-012). The document carries what the
// framework's simulation returned for each step; this module only copies it:
// the replay of the steps from the initial bank, the check that the recorded
// banks are that replay at every mark, and the bank at any take time. No I/O,
// no clock, no solving: nothing here decides what the machine does.
const need=(ok,message)=>{if(!ok)throw new Error(message);};
// Seconds within which a take's sums agree (the Python side's TOLERANCE).
export const TOLERANCE=1e-9;
const shown=value=>value===undefined?'nothing':JSON.stringify(value);

// The bank before and after each step: a step ends with its input at `end`
// and the targets of every commit written, in path order. Fresh objects in
// the initial bank's order.
export function replayTake(take){
  const before=[],after=[];
  let bank={...take.initial};
  for(const step of take.steps){
    before.push({...bank});
    bank={...bank,[step.input]:step.end};
    for(const commit of step.commits)Object.assign(bank,commit.targets);
    after.push({...bank});
  }
  return {before,after};
}
// Banks are cached by the take object, computed once per film.
const replays=new WeakMap();
const replayOf=take=>{let r=replays.get(take);if(!r){r=replayTake(take);replays.set(take,r);}return r;};

// The step each mark follows: -1 for the initial bank, at 0. A mark that is
// neither 0 nor a step's end is refused, naming it.
export function markSteps(doc){
  const take=doc.take,follows={};
  for(const [name,seconds] of Object.entries(doc.marks??{})){
    if(Math.abs(seconds)<=TOLERANCE){follows[name]=-1;continue;}
    const index=take.steps.findIndex(step=>Math.abs(step.at+step.duration-seconds)<=TOLERANCE);
    need(index>=0,`marks.${name}: ${seconds} s is neither 0 nor the end of a step; a mark of a take is the instant after the step before it`);
    follows[name]=index;
  }
  return follows;
}

// The recorded bank at every mark must be the replay's, id by id, exactly;
// otherwise the document is refused naming take.banks.<mark>, the mark and
// the first id (in sorted order) that differs.
export function checkTakeBanks(doc){
  const take=doc.take,follows=markSteps(doc),banks=take.banks;
  for(const name of Object.keys(follows))
    need(Object.hasOwn(banks,name),`take.banks: the bank of the mark ${name} is missing; every mark of a take has its recorded bank`);
  for(const name of Object.keys(banks))
    need(Object.hasOwn(follows,name),`take.banks: ${name} is not one of the marks (${Object.keys(follows).join(', ')||'none'})`);
  const {after}=replayTake(take);
  for(const [name,index] of Object.entries(follows)){
    const expected=index<0?take.initial:after[index],recorded=banks[name];
    for(const id of [...new Set([...Object.keys(expected),...Object.keys(recorded)])].sort()){
      need(Object.is(expected[id],recorded[id]),
        `take.banks.${name}: the bank recorded at the mark ${name} differs from the replay of the steps at ${id}: recorded ${shown(recorded[id])}, replayed ${shown(expected[id])}`);
    }
  }
}

// The bank at take time `seconds` (design D3): the initial bank at or before
// 0; inside the step with at < t ≤ at + duration, f = (t − at) / duration,
// the bank before it with its input at origin + f·(end − origin), exactly
// end at f = 1, and every commit whose fraction ≤ f written; past the last
// step, the bank it ended with. A step owns its end, so a mark, the instant
// after the step before it, is posed on the bank that step ended with.
export function bankAt(take,seconds){
  if(seconds<=0)return {...take.initial};
  const {before,after}=replayOf(take),steps=take.steps;
  const i=steps.findIndex(step=>seconds<=step.at+step.duration);
  if(i<0)return {...after.at(-1)};
  const step=steps[i],f=Math.max(0,Math.min(1,(seconds-step.at)/step.duration));
  if(f>=1)return {...after[i]};
  const bank={...before[i],[step.input]:step.origin+f*(step.end-step.origin)};
  for(const commit of step.commits)if(commit.fraction<=f)Object.assign(bank,commit.targets);
  return bank;
}

// The mark at take time `seconds`, or null.
export function markAt(doc,seconds){
  const found=Object.entries(doc.marks??{}).find(([,at])=>Math.abs(at-seconds)<=TOLERANCE);
  return found?found[0]:null;
}

// What check prints for a take document, once its checks have passed.
export function takeLine(doc){
  const take=doc.take,last=take.steps.at(-1),length=last.at+last.duration;
  const marks=Object.entries(doc.marks??{}).sort((a,b)=>a[1]-b[1]).map(([name,at])=>`${name} ${at} s`);
  return `Take: ${take.steps.length} step${take.steps.length===1?'':'s'}, marks ${marks.join(', ')||'none'}, ${length} s long; the replay of its steps gives the recorded bank at every mark`;
}
