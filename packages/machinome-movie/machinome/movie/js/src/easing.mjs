// The easing vocabulary of every keyed value in an episode: five named curves
// that start at exactly 0, end at exactly 1, never decrease and never overshoot.
export const EASINGS=['linear','smooth','in','out','in-out'];
const CURVES={
  linear:u=>u,
  // The camera smoothstep, in its original operation order.
  smooth:u=>u*u*(3-2*u),
  in:u=>u*u*u,
  out:u=>{const v=1-u;return 1-v*v*v;},
  'in-out':u=>{if(u<.5)return 4*u*u*u;const v=1-u;return 1-4*v*v*v;},
};
// Each curve's slope at its end, in units of the segment's average rate: how
// fast a keyed value is still travelling when it reaches its later key.
const END_SLOPES={linear:1,smooth:0,in:3,out:0,'in-out':0};
export function endSlope(name){
  if(typeof name!=='string'||!Object.hasOwn(END_SLOPES,name))throw new Error(unknownEasing(name));
  return END_SLOPES[name];
}
export function unknownEasing(name){
  return `Unknown easing: ${name}; use linear, smooth, in, out or in-out`;
}
export function ease(name,u){
  if(typeof name!=='string'||!Object.hasOwn(CURVES,name))throw new Error(unknownEasing(name));
  return CURVES[name](Math.min(1,Math.max(0,u)));
}
// keys: [{at, value, ease?}] with `at` strictly increasing and values all finite
// numbers or all finite vectors of one length. A key's ease names the curve of
// the segment that ends at it; a key without one takes `fallback`. Before the
// first key and from the last key on, the end value holds.
export function keyedValue(keys,t,fallback){
  if(t<keys[0].at)return keys[0].value;
  const i=keys.findIndex((k,j)=>j+1<keys.length&&t>=k.at&&t<keys[j+1].at);
  if(i<0)return keys.at(-1).value;
  const a=keys[i],b=keys[i+1],name=b.ease??fallback;
  // Linear keeps the model-time expression and order (multiply, then divide),
  // so every existing model second keeps its bits.
  if(name==='linear'){
    const mix=(v,w)=>v+(w-v)*(t-a.at)/(b.at-a.at);
    return Array.isArray(a.value)?a.value.map((v,k)=>mix(v,b.value[k])):mix(a.value,b.value);
  }
  const w=ease(name,(t-a.at)/(b.at-a.at));
  // The camera expression, clamped so an eased segment never leaves its keys.
  const mix=(v,x)=>Math.min(Math.max(v,x),Math.max(Math.min(v,x),v+(x-v)*w));
  return Array.isArray(a.value)?a.value.map((v,k)=>mix(v,b.value[k])):mix(a.value,b.value);
}
