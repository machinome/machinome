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
// Pixels to leave out of a comparison: the film's chrome (masthead and progress
// rule, drawn above every transition), each rectangle widened by `margin` pixels
// so antialiased edges fall inside it.
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
