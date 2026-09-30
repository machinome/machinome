import {test} from 'vitest';
import assert from 'node:assert/strict';
import {EASINGS,ease,keyedValue} from '../src/easing.mjs';

const grid=n=>Array.from({length:n+1},(_,i)=>i/n);

test('five named curves with exact values, ends and clamping',()=>{
  assert.deepEqual(EASINGS,['linear','smooth','in','out','in-out']);
  assert.equal(ease('smooth',.25),.15625);
  assert.equal(ease('in',.5),.125);
  assert.equal(ease('out',.5),.875);
  assert.equal(ease('in-out',.25),.0625);
  assert.equal(ease('in-out',.5),.5);
  assert.equal(ease('in-out',.75),.9375);
  assert.equal(ease('linear',.3),.3);
  for(const name of EASINGS){
    assert.equal(ease(name,0),0,name);assert.equal(ease(name,1),1,name);
    assert.equal(ease(name,-.2),0,name);assert.equal(ease(name,1.3),1,name);
  }
});

test('smooth is the camera smoothstep to the last bit',()=>{
  for(const u of grid(1000))assert.ok(Object.is(ease('smooth',u),u*u*(3-2*u)),`u = ${u}`);
});

test('every curve is non-decreasing within [0, 1]; out mirrors in; smooth and in-out are symmetric',()=>{
  const us=grid(100000);
  for(const name of EASINGS){
    let prior=-Infinity;
    for(const u of us){const v=ease(name,u);assert.ok(v>=prior&&v>=0&&v<=1,`${name} at ${u}: ${v}`);prior=v;}
  }
  for(const u of us){
    assert.ok(Math.abs(ease('out',u)-(1-ease('in',1-u)))<=1e-15,`out at ${u}`);
    for(const name of ['smooth','in-out'])assert.ok(Math.abs(ease(name,1-u)+ease(name,u)-1)<=1e-15,`${name} at ${u}`);
  }
});

test('any other easing name is refused, naming the five',()=>{
  for(const name of ['bounce','spring','hold','ease-out','Smooth',null,1])
    assert.throws(()=>ease(name,.5),/Unknown easing: .*use linear, smooth, in, out or in-out/,String(name));
});

test('keyedValue holds the ends, meets keys exactly and eases the segment by its ending key',()=>{
  const keys=[{at:1,value:10},{at:2,value:20,ease:'in'},{at:4,value:30}];
  assert.equal(keyedValue(keys,0,'linear'),10);
  assert.equal(keyedValue(keys,1,'linear'),10);
  assert.equal(keyedValue(keys,2,'linear'),20);
  assert.equal(keyedValue(keys,4,'linear'),30);
  assert.equal(keyedValue(keys,9,'linear'),30);
  assert.equal(keyedValue(keys,1.5,'linear'),10+10*ease('in',.5),'the segment ending at an in key');
  assert.equal(keyedValue(keys,3,'linear'),25,'no ease on the ending key: the fallback');
  assert.equal(keyedValue(keys,3,'out'),20+10*ease('out',.5));
  const vectors=[{at:0,value:[0,10,-4]},{at:2,value:[4,10,8],ease:'out'}];
  assert.deepEqual(keyedValue(vectors,1,'smooth'),[0+4*.875,10,-4+12*.875]);
  assert.deepEqual(keyedValue(vectors,-1,'smooth'),[0,10,-4]);
  assert.deepEqual(keyedValue(vectors,2,'smooth'),[4,10,8]);
  assert.deepEqual(keyedValue([{at:0,value:[1,2]},{at:1,value:[3,6]}],.25,'linear'),[1.5,3]);
});

test('linear keeps the model-time order: multiply before divide, left to right',()=>{
  const keys=[{at:0,value:158.7},{at:8.6,value:180.1}];
  const a=158.7,b=180.1,A=0,B=8.6,t=8;
  assert.ok(Object.is(keyedValue(keys,t,'linear'),a+(b-a)*(t-A)/(B-A)));
  assert.equal(keyedValue(keys,t,'linear'),178.60697674418606);
  assert.notEqual(a+(b-a)*((t-A)/(B-A)),178.60697674418606,'the divide-first order differs here');
});

test('an eased segment never passes its later key (the clamp)',()=>{
  for(const [a,b] of [[461,466.8],[453,461],[158.7,180.1],[0.1,0.3]]){
    const keys=[{at:0,value:a},{at:6.899,value:b,ease:'out'}];
    for(let i=0;i<100000;i++){
      const t=6.899*i/100000,v=keyedValue(keys,t,'linear');
      assert.ok(v>=a&&v<=b,`${a}->${b} at ${t}: ${v}`);
    }
    for(let t=6.899;t>6.899-1e-11;t-=Number.EPSILON*4){const v=keyedValue(keys,t,'linear');assert.ok(v<=b,`${v} > ${b}`);}
    const falling=[{at:0,value:b},{at:1,value:a,ease:'out'}];
    for(const u of grid(10000)){const v=keyedValue(falling,u,'linear');assert.ok(v>=a&&v<=b,`falling at ${u}: ${v}`);}
  }
});
