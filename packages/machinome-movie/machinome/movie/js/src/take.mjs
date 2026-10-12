// A clocked take, pure (docs/movie-document.md, "The take"; the pose-a-take
// change, design D2 and D3; ADR-012). The document carries what the
// framework's simulation returned for each step; this module only copies it:
// the replay of the steps from the initial bank, the check that the recorded
// banks are that replay at every mark, and the bank at any take time. No I/O,
// no clock, no solving: nothing here decides what the machine does.
const need=(ok,message)=>{if(!ok)throw new Error(message);};
const shown=value=>value===undefined?'nothing':JSON.stringify(value);

// Take time is the exact sum of the durations as written (ADR-016): a
// duration is the decimal its shortest form writes (String(), the digits
// Python's repr gives), n·10^e with n a BigInt; the sum of decimals is a
// decimal, written as the double nearest it (Number() of the decimal, as
// Python's float() of the fraction). No take time is added in floats.
const decimal=seconds=>{
  const [,digits,fraction='',exponent='0']=/^(-?\d+)(?:\.(\d+))?(?:e([+-]\d+))?$/.exec(String(seconds));
  return {n:BigInt(digits+fraction),e:Number(exponent)-fraction.length};
};
const plus=(a,b)=>{const e=Math.min(a.e,b.e),at=d=>d.n*10n**BigInt(d.e-e);return {n:at(a)+at(b),e};};
const written=d=>Number(`${d.n}e${d.e}`);

// The take seconds each step starts at, and the take's length: the exact sums
// of the durations before it, as the document must write them.
export function takeTimes(steps){
  let total={n:0n,e:0};const starts=[];
  for(const step of steps){starts.push(written(total));total=plus(total,decimal(step.duration));}
  return {starts,length:written(total)};
}

// The take seconds each step ends at, as the document writes them (and the
// check has held them to the exact sums): the next step's at, and for the
// last step the take's length. Read, never added again.
export function stepEnds(doc){
  const steps=doc.take.steps;
  return steps.map((_,i)=>i+1<steps.length?steps[i+1].at:doc.model.expectedDurationSeconds);
}

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
// neither 0 nor a step's written end, exactly, is refused, naming it.
export function markSteps(doc){
  const ends=stepEnds(doc),follows={};
  for(const [name,seconds] of Object.entries(doc.marks??{})){
    if(seconds===0){follows[name]=-1;continue;}
    const index=ends.indexOf(seconds);
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
// after the step before it, is posed on the bank that step ended with. A
// step's end is the one the document writes (stepEnds), so the take seconds
// of a mark are that step's end exactly (ADR-016).
export function bankAt(doc,seconds){
  const take=doc.take;
  if(seconds<=0)return {...take.initial};
  const {before,after}=replayOf(take),steps=take.steps,ends=stepEnds(doc);
  const i=ends.findIndex(end=>seconds<=end);
  if(i<0)return {...after.at(-1)};
  if(seconds===ends[i])return {...after[i]};
  const step=steps[i],f=Math.max(0,Math.min(1,(seconds-step.at)/step.duration));
  if(f>=1)return {...after[i]};
  const bank={...before[i],[step.input]:step.origin+f*(step.end-step.origin)};
  for(const commit of step.commits)if(commit.fraction<=f)Object.assign(bank,commit.targets);
  return bank;
}

// The mark at take time `seconds` exactly, or null: a take time a hair off a
// mark is posed inside a step, not on the mark's recorded bank.
export function markAt(doc,seconds){
  const found=Object.entries(doc.marks??{}).find(([,at])=>at===seconds);
  return found?found[0]:null;
}

// What check prints for a take document, once its checks have passed: the
// marks and the length as the document writes them.
export function takeLine(doc){
  const take=doc.take,length=doc.model.expectedDurationSeconds;
  const marks=Object.entries(doc.marks??{}).sort((a,b)=>a[1]-b[1]).map(([name,at])=>`${name} ${at} s`);
  return `Take: ${take.steps.length} step${take.steps.length===1?'':'s'}, marks ${marks.join(', ')||'none'}, ${length} s long; the replay of its steps gives the recorded bank at every mark`;
}
