// Marks on a view: rings, labels and arrows, rebuilt from nothing every frame
// in the view's mark layer after its viewer is posed; reading the viewer never
// renders. The drawing is the earlier film page's (its drawAnnotations), except
// that `place`, `offset` and a ring's `padding` are fractions of the view
// element's box, since a set may put the view anywhere.
import type {MarkState,Rect,Vec3} from './types';

export interface MarkViewer {
  partOnScreen(path:string[]):{rect:Rect}|null;
  project(point:Vec3):{x:number;y:number}|null;
}
export interface MarkReport {
  id:string;
  kind:MarkState['kind'];
  anchor:{x:number;y:number}|null;
  rect:Rect|null;
  ring?:{cx:number;cy:number;rx:number;ry:number};
  text:Rect|null;
  tail:{x:number;y:number}|null;
  inside?:{x:number;y:number};
  outside?:{x:number;y:number};
  opacity:number;
  drawn:number;
}

const svgNS='http://www.w3.org/2000/svg';
export const plain=(r:{x:number;y:number;width:number;height:number}):Rect=>({x:r.x,y:r.y,width:r.width,height:r.height});
const union=(a:Rect,b:Rect):Rect=>{const x=Math.min(a.x,b.x),y=Math.min(a.y,b.y);
  return {x,y,width:Math.max(a.x+a.width,b.x+b.width)-x,height:Math.max(a.y+a.height,b.y+b.height)-y};};

// The anchor of a part is the centre of its on-screen rect (the union for
// several paths); of a world point, its projection. Client pixels.
function resolve(viewer:MarkViewer,target:MarkState['target']):{anchor:{x:number;y:number}|null;rect:Rect|null}{
  if('point' in target){const p=viewer.project(target.point);return {anchor:p?{x:p.x,y:p.y}:null,rect:null};}
  let rect:Rect|null=null;
  for(const path of target.paths){const on=viewer.partOnScreen(path);if(on)rect=rect?union(rect,on.rect):plain(on.rect);}
  return {anchor:rect?{x:rect.x+rect.width/2,y:rect.y+rect.height/2}:null,rect};
}

/**
 * Draws `marks` into `layer` (emptied first) over the view element whose box
 * is `box` (client pixels) and returns what was drawn, in client pixels.
 * `uid` keeps clip-path ids distinct between views; `where` names the view and
 * shot in a refusal.
 */
export function drawMarks(layer:HTMLElement,box:Rect,marks:MarkState[],viewer:MarkViewer,
  {accent,uid,where}:{accent:string;uid:string;where:string}):MarkReport[]{
  layer.replaceChildren();
  if(!marks.length)return [];
  const origin=layer.getBoundingClientRect(),W=window.innerWidth,H=window.innerHeight;
  const svg=document.createElementNS(svgNS,'svg');
  svg.setAttribute('width',String(W));svg.setAttribute('height',String(H));layer.append(svg);
  const shape=(name:string,attributes:Record<string,string|number>,parent:Element=svg):SVGElement=>{
    const el=document.createElementNS(svgNS,name);
    for(const [k,v] of Object.entries(attributes))el.setAttribute(k,String(v));
    parent.append(el);return el;
  };
  const local=(p:{x:number;y:number})=>({x:p.x-origin.left,y:p.y-origin.top});
  const stroke=W*.0024,reports:MarkReport[]=[];
  for(const [index,mark] of marks.entries()){
    let found;
    try{found=resolve(viewer,mark.target);}
    catch(error){throw new Error(`Viewer refused mark ${mark.id} of ${where}: ${(error as Error).message}`);}
    const entry:MarkReport={id:mark.id,kind:mark.kind,anchor:found.anchor,rect:found.rect,text:null,tail:null,
      opacity:mark.opacity,drawn:mark.drawn};
    reports.push(entry);
    if(!entry.anchor)continue;
    // At rest the plain drawing path, including text rasterization.
    const animated=mark.opacity<1||mark.drawn<1;
    const strokes=animated?shape('g',{opacity:mark.opacity}):svg;
    if(mark.kind==='ring'){
      const {x,y,width,height}=entry.rect as Rect,P=(mark.padding??0)*box.width;
      const cx=x+width/2,cy=y+height/2,rx=Math.SQRT2*(width/2+P),ry=Math.SQRT2*(height/2+P);
      entry.ring={cx,cy,rx,ry};
      const top=local({x:cx,y:cy-ry}),bottom=local({x:cx,y:cy+ry});
      const path=shape('path',{d:`M ${top.x} ${top.y} A ${rx} ${ry} 0 0 1 ${bottom.x} ${bottom.y} A ${rx} ${ry} 0 0 1 ${top.x} ${top.y}`,
        fill:'none',stroke:accent,'stroke-width':stroke},strokes) as SVGPathElement;
      if(mark.drawn<1){
        path.setAttribute('pathLength','1');path.setAttribute('stroke-dasharray',`${mark.drawn} 1`);
        path.setAttribute('stroke-linecap','butt');
        if(mark.drawn>0&&typeof path.getTotalLength==='function'){
          const length=path.getTotalLength(),inside=path.getPointAtLength(mark.drawn*length/2),
            outside=path.getPointAtLength((1+mark.drawn)*length/2);
          entry.inside={x:inside.x+origin.left,y:inside.y+origin.top};
          entry.outside={x:outside.x+origin.left,y:outside.y+origin.top};
        }
      }
      continue;
    }
    const place=mark.place??[0,0],offset=mark.offset??[0,0];
    const centre=mark.kind==='arrow'?{x:box.x+place[0]*box.width,y:box.y+place[1]*box.height}
      :{x:entry.anchor.x+offset[0]*box.width,y:entry.anchor.y+offset[1]*box.height};
    if(mark.text!==undefined){
      const el=document.createElement('div');el.className='vm-mark-text';el.textContent=mark.text;layer.append(el);
      const size=el.getBoundingClientRect(),at=local({x:centre.x-size.width/2,y:centre.y-size.height/2});
      el.style.left=`${at.x}px`;el.style.top=`${at.y}px`;entry.text=plain(el.getBoundingClientRect());
      if(animated)el.style.opacity=String(mark.opacity);
    }
    if(mark.kind!=='arrow')continue;
    // The shaft leaves the text box at the edge nearest the tip; the tip touches the part.
    const tip=entry.anchor,dx=tip.x-centre.x,dy=tip.y-centre.y;
    const k=entry.text?Math.min(1,dx?entry.text.width/2/Math.abs(dx):Infinity,dy?entry.text.height/2/Math.abs(dy):Infinity):0;
    const tail=entry.tail={x:centre.x+dx*k,y:centre.y+dy*k};
    const length=Math.hypot(tip.x-tail.x,tip.y-tail.y),u=length?{x:(tip.x-tail.x)/length,y:(tip.y-tail.y)/length}:{x:0,y:1};
    const head=W*.012,half=head*.7,base={x:tip.x-u.x*head,y:tip.y-u.y*head};
    const a=local(tail),b=local(base),t=local(tip);
    if(mark.drawn<1){
      const f=mark.drawn,edge={x:a.x+u.x*length*f,y:a.y+u.y*length*f},normal={x:-u.y,y:u.x},span=2*Math.hypot(W,H);
      const id=`vm-mark-${uid}-${index}`,clip=shape('clipPath',{id});
      shape('polygon',{points:[[a.x+normal.x*span,a.y+normal.y*span],[edge.x+normal.x*span,edge.y+normal.y*span],
        [edge.x-normal.x*span,edge.y-normal.y*span],[a.x-normal.x*span,a.y-normal.y*span]].map(p=>p.join(',')).join(' ')},clip);
      strokes.setAttribute('clip-path',`url(#${id})`);
      if(f>0){entry.inside={x:tail.x+u.x*length*f/2,y:tail.y+u.y*length*f/2};
        entry.outside={x:tail.x+u.x*length*(1+f)/2,y:tail.y+u.y*length*(1+f)/2};}
    }
    if(length>head)shape('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:accent,'stroke-width':stroke},strokes);
    shape('polygon',{fill:accent,points:[[t.x,t.y],[b.x-u.y*half,b.y+u.x*half],[b.x+u.y*half,b.y-u.x*half]].map(p=>p.join(',')).join(' ')},strokes);
  }
  return reports;
}
