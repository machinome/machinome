// Layer 4: one pose in flight, the latest time wins (the player-page change,
// design D6), on a pose whose completion the test controls. No DOM, no clock.
import {describe,expect,test} from 'vitest';
import {poser} from './poser';

// A pose that records each time it is asked and finishes when told.
function controlled(){
  const asked:number[]=[],pending:(()=>void)[]=[];
  const pose=(t:number)=>{asked.push(t);return new Promise<void>(resolve=>{pending.push(resolve);});};
  const finish=async()=>{pending.shift()?.();await new Promise(r=>setTimeout(r,0));};
  return {asked,pose,finish};
}

describe('the poser',()=>{
  test('one pose runs at a time, and of the times requested meanwhile only the latest is posed after it',async()=>{
    const {asked,pose,finish}=controlled(),p=poser(pose);
    p.request(1);
    p.request(2);p.request(3);p.request(4);
    expect(asked).toEqual([1]);
    expect(p.busy()).toBe(true);
    await finish();
    expect(asked).toEqual([1,4]);
    await finish();
    expect(p.busy()).toBe(false);
    expect(asked).toEqual([1,4]);
  });
  test('the time just posed is not posed again unless forced',async()=>{
    const {asked,pose,finish}=controlled(),p=poser(pose);
    p.request(5);await finish();
    p.request(5);
    expect(asked).toEqual([5]);
    p.request(5,{force:true});
    expect(asked).toEqual([5,5]);
    await finish();
    p.request(6);p.request(5);
    await finish();
    // 6 ran; 5 was requested after it, and differs from the time just posed.
    expect(asked).toEqual([5,5,6,5]);
    await finish();
  });
  test('idle resolves once nothing runs and nothing waits; an error is reported and the poser goes on',async()=>{
    const errors:unknown[]=[];
    let fail=true;
    const asked:number[]=[];
    const p=poser(async t=>{asked.push(t);if(fail){fail=false;throw new Error('the stage refused');}},error=>errors.push(error));
    p.request(1);p.request(2);
    await p.idle();
    expect(asked).toEqual([1,2]);
    expect(errors.map(e=>(e as Error).message)).toEqual(['the stage refused']);
    expect(p.busy()).toBe(false);
    await p.idle();
  });
});
