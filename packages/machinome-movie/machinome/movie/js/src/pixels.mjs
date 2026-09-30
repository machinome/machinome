// Decoded captures for preview's pixel proofs. Playwright's screenshots are
// 8-bit, non-interlaced RGB or RGBA PNG; anything else is refused, not guessed.
import {inflateSync} from 'node:zlib';

const SIGNATURE=Buffer.from([137,80,78,71,13,10,26,10]);
export function decodePng(buffer){
  if(!buffer.subarray(0,8).equals(SIGNATURE))throw new Error('Capture is not a PNG');
  let pos=8,header=null;const data=[];
  while(pos<buffer.length){
    const length=buffer.readUInt32BE(pos),kind=buffer.toString('latin1',pos+4,pos+8),body=buffer.subarray(pos+8,pos+8+length);
    if(kind==='IHDR')header={width:body.readUInt32BE(0),height:body.readUInt32BE(4),depth:body[8],type:body[9],interlace:body[12]};
    else if(kind==='IDAT')data.push(body);
    else if(kind==='IEND')break;
    pos+=12+length;
  }
  if(!header||header.depth!==8||![2,6].includes(header.type)||header.interlace!==0)throw new Error('Unsupported PNG capture: expected 8-bit non-interlaced RGB or RGBA');
  const {width,height}=header,channels=header.type===6?4:3,stride=width*channels,raw=inflateSync(Buffer.concat(data));
  const rgb=Buffer.alloc(width*height*3);
  let prior=Buffer.alloc(stride),line=Buffer.alloc(stride);
  for(let y=0;y<height;y++){
    const at=y*(stride+1),filter=raw[at];
    for(let i=0;i<stride;i++){
      const a=i>=channels?line[i-channels]:0,b=prior[i],c=i>=channels?prior[i-channels]:0;let v=raw[at+1+i];
      if(filter===1)v+=a;else if(filter===2)v+=b;else if(filter===3)v+=(a+b)>>1;
      else if(filter===4){const p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);v+=pa<=pb&&pa<=pc?a:pb<=pc?b:c;}
      else if(filter!==0)throw new Error(`Unsupported PNG filter ${filter}`);
      line[i]=v&255;
    }
    for(let x=0;x<width;x++)for(let k=0;k<3;k++)rgb[(y*width+x)*3+k]=line[x*channels+k];
    [prior,line]=[line,prior];
  }
  return {width,height,rgb};
}
export const hexColor=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
// Pixels to leave out of a comparison: the film's chrome (whatever the set
// marks with Chrome, drawn above every transition and blend and reported by
// the stage), each rectangle widened by `margin` pixels so antialiased edges
// fall inside it. Every pixel proof leaves it out, and nothing else.
export function chromeMask(width,height,rects,margin=2){
  const mask=new Uint8Array(width*height);
  for(const r of rects){
    const x0=Math.max(0,Math.floor(r.x)-margin),x1=Math.min(width,Math.ceil(r.x+r.width)+margin);
    const y0=Math.max(0,Math.floor(r.y)-margin),y1=Math.min(height,Math.ceil(r.y+r.height)+margin);
    for(let y=y0;y<y1;y++)mask.fill(1,y*width+x0,y*width+x1);
  }
  return mask;
}
// The largest channel difference between an image and a prediction made per
// pixel by expect(x, y, k), skipping masked pixels.
export function largestDifference(image,expect,mask=null){
  const {width,height,rgb}=image;let largest=0;
  for(let y=0;y<height;y++)for(let x=0;x<width;x++){
    if(mask?.[y*width+x])continue;
    for(let k=0;k<3;k++){const d=Math.abs(rgb[(y*width+x)*3+k]-expect(x,y,k));if(d>largest)largest=d;}
  }
  return largest;
}
export const at=(image,x,y,k)=>image.rgb[(y*image.width+x)*3+k];
// The largest channel difference between two images within the 3×3
// neighbourhood of the point p (viewport pixels, rounded).
function aroundDifference(a,b,p){
  let largest=0;
  for(let y=Math.round(p.y)-1;y<=Math.round(p.y)+1;y++)for(let x=Math.round(p.x)-1;x<=Math.round(p.x)+1;x++){
    if(x<0||y<0||x>=a.width||y>=a.height)continue;
    for(let k=0;k<3;k++)largest=Math.max(largest,Math.abs(at(a,x,y,k)-at(b,x,y,k)));
  }
  return largest;
}
// Graphic-overlays proofs (design D8), on decoded captures of one instant: the
// mark as authored (composed), drawn without its entrance and exit (full), and
// not drawn (without). phase is enter-start, enter (the midpoint), enter-end,
// leave-start or leave (the midpoint); info names the check (`where`), the
// entrance kind, the frame's opacity, and the reported inside and outside
// stroke points and text box. Returns what the report records, or throws.
export function proveMark(phase,{composed,full,without},{where,entrance,opacity,inside,outside,text,chrome=[]}={}){
  const vacuous=full.rgb.equals(without.rgb),mask=chromeMask(composed.width,composed.height,chrome);
  const same=(a,b,extra=[])=>largestDifference(a,(x,y,k)=>at(b,x,y,k),extra.length?chromeMask(a.width,a.height,[...chrome,...extra]):mask);
  let largest;
  if(phase==='enter'&&entrance==='draw'){
    largest=aroundDifference(composed,without,outside);
    if(largest>2)throw new Error(`Annotation draw-on shows the rest of its stroke: ${where} (${largest} levels at the outside point)`);
    if(aroundDifference(full,without,outside)<=2)throw new Error(`Annotation draw-on proof shows nothing: the complete stroke does not reach the outside point: ${where}`);
    if(aroundDifference(composed,without,inside)<=2)throw new Error(`Annotation draw-on shows none of its stroke: ${where} (inside point)`);
  }else if(phase==='enter'||phase==='leave'){
    largest=largestDifference(composed,(x,y,k)=>(1-opacity)*at(without,x,y,k)+opacity*at(full,x,y,k),mask);
    if(largest>2)throw new Error(`Annotation fade does not blend as its easing predicts: ${where} (largest difference ${largest} levels)`);
  }else if(phase==='enter-start'&&entrance==='draw'&&text){
    // A draw-on arrow shows its words from the start, and nothing else of itself.
    largest=same(composed,without,[text]);
    if(largest>0)throw new Error(`Annotation draw-on does not start from its words alone: ${where} (largest difference ${largest} levels outside its text)`);
  }else if(phase==='enter-start'){
    largest=same(composed,without);
    if(largest>0)throw new Error(`Annotation entrance does not start from nothing: ${where} (largest difference ${largest} levels)`);
  }else if(phase==='enter-end'||phase==='leave-start'){
    largest=same(composed,full);
    if(largest>0)throw new Error(`${phase==='enter-end'?'Annotation entrance changes the mark it ends on':'Annotation exit does not start from the mark as drawn'}: ${where} (largest difference ${largest} levels)`);
  }else throw new Error(`Unknown mark proof: ${phase}`);
  return {largestDifference:largest,vacuous};
}
