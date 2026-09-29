// Fixtures of the 0.2 and 0.3 frame pins (workflow.test.mjs) and of their
// 0.4 copies (keyframes.test.mjs). Not a test file: it registers no tests.
export const base02=()=>({output:{width:1280,height:720,fps:30,durationSeconds:4},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  cameras:{a:{position:[0,0,10],target:[0,0,0],up:[0,1,0],fov:37},
    b:{position:[10,0,10],target:[0,0,0],up:[0,1,0],fov:37}},
  layers:{frame:[['Frame']]}, evidence:{},
  shots:[{id:'first',start:0,end:2,narration:'One.',direction:'Look.',
    simulation:{from:8,to:12,keyframes:[{at:0,seconds:8},{at:1.5,seconds:10},{at:2,seconds:12}]},camera:[{at:0,preset:'a'},{at:2,preset:'b'}],
    hiddenLayers:['frame'],overlays:[],evidence:[]},
    {id:'second',start:2,end:4,narration:'Two.',direction:'Look again.',
      simulation:{from:12,to:12},camera:[{at:0,preset:'b'}],hiddenLayers:[],overlays:[],evidence:[]}]});
export const order02=()=>({format:'machinome-video-draft/0.2',output:{width:1280,height:720,fps:30,durationSeconds:8.6},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  cameras:{a:{position:[0,0,10],target:[0,0,0],up:[0,1,0],fov:37}},layers:{},evidence:{},
  shots:[{id:'stroke',start:0,end:8.6,narration:'One.',direction:'Look.',
    simulation:{from:158.7,to:180.1,keyframes:[{at:0,seconds:158.7},{at:8.6,seconds:180.1}]},camera:[{at:0,preset:'a'}],
    hiddenLayers:[],overlays:[],evidence:[]}]});
const shot=(id,start,end,camera,extra={})=>({id,start,end,narration:'Words.',direction:'Look.',
  simulation:{from:8,to:8+end-start},camera,hiddenLayers:[],overlays:[],evidence:[],...extra});
export const lens03=(second='tight')=>({format:'machinome-video-draft/0.3',
  output:{width:1280,height:720,fps:30,durationSeconds:5},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  cameras:{wide:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},
    tight:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:20},
    rolled:{position:[0,-10,0],target:[0,0,0],up:[1,0,1],fov:37}},
  layers:{},evidence:{},
  shots:[shot('narrow',0,3,[{at:0,preset:'wide'},{at:2,preset:second}]),shot('hold',3,5,[{at:0,preset:second}])]});
export const cues03=()=>({format:'machinome-video-draft/0.3',
  output:{width:1280,height:720,fps:30,durationSeconds:2},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  style:{background:'#faf7ef',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08},
  cameras:{a:{position:[0,0,10],target:[0,0,0],up:[0,1,0],fov:37},b:{position:[4,0,10],target:[0,0,0],up:[0,1,0],fov:37}},
  layers:{pawls:[['Feed mechanism','Driving pawl'],['Feed mechanism','Holding pawl']]},evidence:{},
  shots:[shot('pawls',0,2,[{at:0,preset:'a'},{at:2,preset:'b'}],{
    annotations:[{from:.5,to:1.5,kind:'arrow',part:['Feed mechanism','Driving pawl'],place:[.18,.22],text:'Pulls one tooth'}],
    highlight:[{from:0,to:2,parts:['pawls'],others:'ghost'}]})]});
export const cuesManifest={animation:{loop:296},root:{name:'Mill',children:[
  {name:'Feed mechanism',children:[{name:'Driving pawl'},{name:'Holding pawl'}]}]}};
