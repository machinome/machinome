(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const l of document.querySelectorAll('link[rel="modulepreload"]'))r(l);new MutationObserver(l=>{for(const u of l)if(u.type==="childList")for(const f of u.addedNodes)f.tagName==="LINK"&&f.rel==="modulepreload"&&r(f)}).observe(document,{childList:!0,subtree:!0});function i(l){const u={};return l.integrity&&(u.integrity=l.integrity),l.referrerPolicy&&(u.referrerPolicy=l.referrerPolicy),l.crossOrigin==="use-credentials"?u.credentials="include":l.crossOrigin==="anonymous"?u.credentials="omit":u.credentials="same-origin",u}function r(l){if(l.ep)return;l.ep=!0;const u=i(l);fetch(l.href,u)}})();var fh={exports:{}},Xo={};var k_;function ty(){if(k_)return Xo;k_=1;var s=Symbol.for("react.transitional.element"),t=Symbol.for("react.fragment");function i(r,l,u){var f=null;if(u!==void 0&&(f=""+u),l.key!==void 0&&(f=""+l.key),"key"in l){u={};for(var p in l)p!=="key"&&(u[p]=l[p])}else u=l;return l=u.ref,{$$typeof:s,type:r,key:f,ref:l!==void 0?l:null,props:u}}return Xo.Fragment=t,Xo.jsx=i,Xo.jsxs=i,Xo}var X_;function ey(){return X_||(X_=1,fh.exports=ty()),fh.exports}var ve=ey(),hh={exports:{}},ae={};var W_;function ny(){if(W_)return ae;W_=1;var s=Symbol.for("react.transitional.element"),t=Symbol.for("react.portal"),i=Symbol.for("react.fragment"),r=Symbol.for("react.strict_mode"),l=Symbol.for("react.profiler"),u=Symbol.for("react.consumer"),f=Symbol.for("react.context"),p=Symbol.for("react.forward_ref"),m=Symbol.for("react.suspense"),d=Symbol.for("react.memo"),g=Symbol.for("react.lazy"),v=Symbol.for("react.activity"),_=Symbol.iterator;function M(L){return L===null||typeof L!="object"?null:(L=_&&L[_]||L["@@iterator"],typeof L=="function"?L:null)}var T={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},w=Object.assign,E={};function S(L,K,Mt){this.props=L,this.context=K,this.refs=E,this.updater=Mt||T}S.prototype.isReactComponent={},S.prototype.setState=function(L,K){if(typeof L!="object"&&typeof L!="function"&&L!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,L,K,"setState")},S.prototype.forceUpdate=function(L){this.updater.enqueueForceUpdate(this,L,"forceUpdate")};function F(){}F.prototype=S.prototype;function z(L,K,Mt){this.props=L,this.context=K,this.refs=E,this.updater=Mt||T}var C=z.prototype=new F;C.constructor=z,w(C,S.prototype),C.isPureReactComponent=!0;var N=Array.isArray;function D(){}var O={H:null,A:null,T:null,S:null},b=Object.prototype.hasOwnProperty;function P(L,K,Mt){var Rt=Mt.ref;return{$$typeof:s,type:L,key:K,ref:Rt!==void 0?Rt:null,props:Mt}}function q(L,K){return P(L.type,K,L.props)}function G(L){return typeof L=="object"&&L!==null&&L.$$typeof===s}function Z(L){var K={"=":"=0",":":"=2"};return"$"+L.replace(/[=:]/g,function(Mt){return K[Mt]})}var ht=/\/+/g;function mt(L,K){return typeof L=="object"&&L!==null&&L.key!=null?Z(""+L.key):K.toString(36)}function J(L){switch(L.status){case"fulfilled":return L.value;case"rejected":throw L.reason;default:switch(typeof L.status=="string"?L.then(D,D):(L.status="pending",L.then(function(K){L.status==="pending"&&(L.status="fulfilled",L.value=K)},function(K){L.status==="pending"&&(L.status="rejected",L.reason=K)})),L.status){case"fulfilled":return L.value;case"rejected":throw L.reason}}throw L}function I(L,K,Mt,Rt,Pt){var at=typeof L;(at==="undefined"||at==="boolean")&&(L=null);var xt=!1;if(L===null)xt=!0;else switch(at){case"bigint":case"string":case"number":xt=!0;break;case"object":switch(L.$$typeof){case s:case t:xt=!0;break;case g:return xt=L._init,I(xt(L._payload),K,Mt,Rt,Pt)}}if(xt)return Pt=Pt(L),xt=Rt===""?"."+mt(L,0):Rt,N(Pt)?(Mt="",xt!=null&&(Mt=xt.replace(ht,"$&/")+"/"),I(Pt,K,Mt,"",function(ee){return ee})):Pt!=null&&(G(Pt)&&(Pt=q(Pt,Mt+(Pt.key==null||L&&L.key===Pt.key?"":(""+Pt.key).replace(ht,"$&/")+"/")+xt)),K.push(Pt)),1;xt=0;var yt=Rt===""?".":Rt+":";if(N(L))for(var Bt=0;Bt<L.length;Bt++)Rt=L[Bt],at=yt+mt(Rt,Bt),xt+=I(Rt,K,Mt,at,Pt);else if(Bt=M(L),typeof Bt=="function")for(L=Bt.call(L),Bt=0;!(Rt=L.next()).done;)Rt=Rt.value,at=yt+mt(Rt,Bt++),xt+=I(Rt,K,Mt,at,Pt);else if(at==="object"){if(typeof L.then=="function")return I(J(L),K,Mt,Rt,Pt);throw K=String(L),Error("Objects are not valid as a React child (found: "+(K==="[object Object]"?"object with keys {"+Object.keys(L).join(", ")+"}":K)+"). If you meant to render a collection of children, use an array instead.")}return xt}function H(L,K,Mt){if(L==null)return L;var Rt=[],Pt=0;return I(L,Rt,"","",function(at){return K.call(Mt,at,Pt++)}),Rt}function j(L){if(L._status===-1){var K=L._result;K=K(),K.then(function(Mt){(L._status===0||L._status===-1)&&(L._status=1,L._result=Mt)},function(Mt){(L._status===0||L._status===-1)&&(L._status=2,L._result=Mt)}),L._status===-1&&(L._status=0,L._result=K)}if(L._status===1)return L._result.default;throw L._result}var gt=typeof reportError=="function"?reportError:function(L){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var K=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof L=="object"&&L!==null&&typeof L.message=="string"?String(L.message):String(L),error:L});if(!window.dispatchEvent(K))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",L);return}console.error(L)},Et={map:H,forEach:function(L,K,Mt){H(L,function(){K.apply(this,arguments)},Mt)},count:function(L){var K=0;return H(L,function(){K++}),K},toArray:function(L){return H(L,function(K){return K})||[]},only:function(L){if(!G(L))throw Error("React.Children.only expected to receive a single React element child.");return L}};return ae.Activity=v,ae.Children=Et,ae.Component=S,ae.Fragment=i,ae.Profiler=l,ae.PureComponent=z,ae.StrictMode=r,ae.Suspense=m,ae.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=O,ae.__COMPILER_RUNTIME={__proto__:null,c:function(L){return O.H.useMemoCache(L)}},ae.cache=function(L){return function(){return L.apply(null,arguments)}},ae.cacheSignal=function(){return null},ae.cloneElement=function(L,K,Mt){if(L==null)throw Error("The argument must be a React element, but you passed "+L+".");var Rt=w({},L.props),Pt=L.key;if(K!=null)for(at in K.key!==void 0&&(Pt=""+K.key),K)!b.call(K,at)||at==="key"||at==="__self"||at==="__source"||at==="ref"&&K.ref===void 0||(Rt[at]=K[at]);var at=arguments.length-2;if(at===1)Rt.children=Mt;else if(1<at){for(var xt=Array(at),yt=0;yt<at;yt++)xt[yt]=arguments[yt+2];Rt.children=xt}return P(L.type,Pt,Rt)},ae.createContext=function(L){return L={$$typeof:f,_currentValue:L,_currentValue2:L,_threadCount:0,Provider:null,Consumer:null},L.Provider=L,L.Consumer={$$typeof:u,_context:L},L},ae.createElement=function(L,K,Mt){var Rt,Pt={},at=null;if(K!=null)for(Rt in K.key!==void 0&&(at=""+K.key),K)b.call(K,Rt)&&Rt!=="key"&&Rt!=="__self"&&Rt!=="__source"&&(Pt[Rt]=K[Rt]);var xt=arguments.length-2;if(xt===1)Pt.children=Mt;else if(1<xt){for(var yt=Array(xt),Bt=0;Bt<xt;Bt++)yt[Bt]=arguments[Bt+2];Pt.children=yt}if(L&&L.defaultProps)for(Rt in xt=L.defaultProps,xt)Pt[Rt]===void 0&&(Pt[Rt]=xt[Rt]);return P(L,at,Pt)},ae.createRef=function(){return{current:null}},ae.forwardRef=function(L){return{$$typeof:p,render:L}},ae.isValidElement=G,ae.lazy=function(L){return{$$typeof:g,_payload:{_status:-1,_result:L},_init:j}},ae.memo=function(L,K){return{$$typeof:d,type:L,compare:K===void 0?null:K}},ae.startTransition=function(L){var K=O.T,Mt={};O.T=Mt;try{var Rt=L(),Pt=O.S;Pt!==null&&Pt(Mt,Rt),typeof Rt=="object"&&Rt!==null&&typeof Rt.then=="function"&&Rt.then(D,gt)}catch(at){gt(at)}finally{K!==null&&Mt.types!==null&&(K.types=Mt.types),O.T=K}},ae.unstable_useCacheRefresh=function(){return O.H.useCacheRefresh()},ae.use=function(L){return O.H.use(L)},ae.useActionState=function(L,K,Mt){return O.H.useActionState(L,K,Mt)},ae.useCallback=function(L,K){return O.H.useCallback(L,K)},ae.useContext=function(L){return O.H.useContext(L)},ae.useDebugValue=function(){},ae.useDeferredValue=function(L,K){return O.H.useDeferredValue(L,K)},ae.useEffect=function(L,K){return O.H.useEffect(L,K)},ae.useEffectEvent=function(L){return O.H.useEffectEvent(L)},ae.useId=function(){return O.H.useId()},ae.useImperativeHandle=function(L,K,Mt){return O.H.useImperativeHandle(L,K,Mt)},ae.useInsertionEffect=function(L,K){return O.H.useInsertionEffect(L,K)},ae.useLayoutEffect=function(L,K){return O.H.useLayoutEffect(L,K)},ae.useMemo=function(L,K){return O.H.useMemo(L,K)},ae.useOptimistic=function(L,K){return O.H.useOptimistic(L,K)},ae.useReducer=function(L,K,Mt){return O.H.useReducer(L,K,Mt)},ae.useRef=function(L){return O.H.useRef(L)},ae.useState=function(L){return O.H.useState(L)},ae.useSyncExternalStore=function(L,K,Mt){return O.H.useSyncExternalStore(L,K,Mt)},ae.useTransition=function(){return O.H.useTransition()},ae.version="19.2.7",ae}var q_;function kd(){return q_||(q_=1,hh.exports=ny()),hh.exports}var Bn=kd(),dh={exports:{}},Wo={},ph={exports:{}},mh={};var Y_;function iy(){return Y_||(Y_=1,(function(s){function t(I,H){var j=I.length;I.push(H);t:for(;0<j;){var gt=j-1>>>1,Et=I[gt];if(0<l(Et,H))I[gt]=H,I[j]=Et,j=gt;else break t}}function i(I){return I.length===0?null:I[0]}function r(I){if(I.length===0)return null;var H=I[0],j=I.pop();if(j!==H){I[0]=j;t:for(var gt=0,Et=I.length,L=Et>>>1;gt<L;){var K=2*(gt+1)-1,Mt=I[K],Rt=K+1,Pt=I[Rt];if(0>l(Mt,j))Rt<Et&&0>l(Pt,Mt)?(I[gt]=Pt,I[Rt]=j,gt=Rt):(I[gt]=Mt,I[K]=j,gt=K);else if(Rt<Et&&0>l(Pt,j))I[gt]=Pt,I[Rt]=j,gt=Rt;else break t}}return H}function l(I,H){var j=I.sortIndex-H.sortIndex;return j!==0?j:I.id-H.id}if(s.unstable_now=void 0,typeof performance=="object"&&typeof performance.now=="function"){var u=performance;s.unstable_now=function(){return u.now()}}else{var f=Date,p=f.now();s.unstable_now=function(){return f.now()-p}}var m=[],d=[],g=1,v=null,_=3,M=!1,T=!1,w=!1,E=!1,S=typeof setTimeout=="function"?setTimeout:null,F=typeof clearTimeout=="function"?clearTimeout:null,z=typeof setImmediate<"u"?setImmediate:null;function C(I){for(var H=i(d);H!==null;){if(H.callback===null)r(d);else if(H.startTime<=I)r(d),H.sortIndex=H.expirationTime,t(m,H);else break;H=i(d)}}function N(I){if(w=!1,C(I),!T)if(i(m)!==null)T=!0,D||(D=!0,Z());else{var H=i(d);H!==null&&J(N,H.startTime-I)}}var D=!1,O=-1,b=5,P=-1;function q(){return E?!0:!(s.unstable_now()-P<b)}function G(){if(E=!1,D){var I=s.unstable_now();P=I;var H=!0;try{t:{T=!1,w&&(w=!1,F(O),O=-1),M=!0;var j=_;try{e:{for(C(I),v=i(m);v!==null&&!(v.expirationTime>I&&q());){var gt=v.callback;if(typeof gt=="function"){v.callback=null,_=v.priorityLevel;var Et=gt(v.expirationTime<=I);if(I=s.unstable_now(),typeof Et=="function"){v.callback=Et,C(I),H=!0;break e}v===i(m)&&r(m),C(I)}else r(m);v=i(m)}if(v!==null)H=!0;else{var L=i(d);L!==null&&J(N,L.startTime-I),H=!1}}break t}finally{v=null,_=j,M=!1}H=void 0}}finally{H?Z():D=!1}}}var Z;if(typeof z=="function")Z=function(){z(G)};else if(typeof MessageChannel<"u"){var ht=new MessageChannel,mt=ht.port2;ht.port1.onmessage=G,Z=function(){mt.postMessage(null)}}else Z=function(){S(G,0)};function J(I,H){O=S(function(){I(s.unstable_now())},H)}s.unstable_IdlePriority=5,s.unstable_ImmediatePriority=1,s.unstable_LowPriority=4,s.unstable_NormalPriority=3,s.unstable_Profiling=null,s.unstable_UserBlockingPriority=2,s.unstable_cancelCallback=function(I){I.callback=null},s.unstable_forceFrameRate=function(I){0>I||125<I?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):b=0<I?Math.floor(1e3/I):5},s.unstable_getCurrentPriorityLevel=function(){return _},s.unstable_next=function(I){switch(_){case 1:case 2:case 3:var H=3;break;default:H=_}var j=_;_=H;try{return I()}finally{_=j}},s.unstable_requestPaint=function(){E=!0},s.unstable_runWithPriority=function(I,H){switch(I){case 1:case 2:case 3:case 4:case 5:break;default:I=3}var j=_;_=I;try{return H()}finally{_=j}},s.unstable_scheduleCallback=function(I,H,j){var gt=s.unstable_now();switch(typeof j=="object"&&j!==null?(j=j.delay,j=typeof j=="number"&&0<j?gt+j:gt):j=gt,I){case 1:var Et=-1;break;case 2:Et=250;break;case 5:Et=1073741823;break;case 4:Et=1e4;break;default:Et=5e3}return Et=j+Et,I={id:g++,callback:H,priorityLevel:I,startTime:j,expirationTime:Et,sortIndex:-1},j>gt?(I.sortIndex=j,t(d,I),i(m)===null&&I===i(d)&&(w?(F(O),O=-1):w=!0,J(N,j-gt))):(I.sortIndex=Et,t(m,I),T||M||(T=!0,D||(D=!0,Z()))),I},s.unstable_shouldYield=q,s.unstable_wrapCallback=function(I){var H=_;return function(){var j=_;_=H;try{return I.apply(this,arguments)}finally{_=j}}}})(mh)),mh}var Z_;function ay(){return Z_||(Z_=1,ph.exports=iy()),ph.exports}var gh={exports:{}},Nn={};var K_;function ry(){if(K_)return Nn;K_=1;var s=kd();function t(m){var d="https://react.dev/errors/"+m;if(1<arguments.length){d+="?args[]="+encodeURIComponent(arguments[1]);for(var g=2;g<arguments.length;g++)d+="&args[]="+encodeURIComponent(arguments[g])}return"Minified React error #"+m+"; visit "+d+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function i(){}var r={d:{f:i,r:function(){throw Error(t(522))},D:i,C:i,L:i,m:i,X:i,S:i,M:i},p:0,findDOMNode:null},l=Symbol.for("react.portal");function u(m,d,g){var v=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:l,key:v==null?null:""+v,children:m,containerInfo:d,implementation:g}}var f=s.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function p(m,d){if(m==="font")return"";if(typeof d=="string")return d==="use-credentials"?d:""}return Nn.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=r,Nn.createPortal=function(m,d){var g=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!d||d.nodeType!==1&&d.nodeType!==9&&d.nodeType!==11)throw Error(t(299));return u(m,d,null,g)},Nn.flushSync=function(m){var d=f.T,g=r.p;try{if(f.T=null,r.p=2,m)return m()}finally{f.T=d,r.p=g,r.d.f()}},Nn.preconnect=function(m,d){typeof m=="string"&&(d?(d=d.crossOrigin,d=typeof d=="string"?d==="use-credentials"?d:"":void 0):d=null,r.d.C(m,d))},Nn.prefetchDNS=function(m){typeof m=="string"&&r.d.D(m)},Nn.preinit=function(m,d){if(typeof m=="string"&&d&&typeof d.as=="string"){var g=d.as,v=p(g,d.crossOrigin),_=typeof d.integrity=="string"?d.integrity:void 0,M=typeof d.fetchPriority=="string"?d.fetchPriority:void 0;g==="style"?r.d.S(m,typeof d.precedence=="string"?d.precedence:void 0,{crossOrigin:v,integrity:_,fetchPriority:M}):g==="script"&&r.d.X(m,{crossOrigin:v,integrity:_,fetchPriority:M,nonce:typeof d.nonce=="string"?d.nonce:void 0})}},Nn.preinitModule=function(m,d){if(typeof m=="string")if(typeof d=="object"&&d!==null){if(d.as==null||d.as==="script"){var g=p(d.as,d.crossOrigin);r.d.M(m,{crossOrigin:g,integrity:typeof d.integrity=="string"?d.integrity:void 0,nonce:typeof d.nonce=="string"?d.nonce:void 0})}}else d==null&&r.d.M(m)},Nn.preload=function(m,d){if(typeof m=="string"&&typeof d=="object"&&d!==null&&typeof d.as=="string"){var g=d.as,v=p(g,d.crossOrigin);r.d.L(m,g,{crossOrigin:v,integrity:typeof d.integrity=="string"?d.integrity:void 0,nonce:typeof d.nonce=="string"?d.nonce:void 0,type:typeof d.type=="string"?d.type:void 0,fetchPriority:typeof d.fetchPriority=="string"?d.fetchPriority:void 0,referrerPolicy:typeof d.referrerPolicy=="string"?d.referrerPolicy:void 0,imageSrcSet:typeof d.imageSrcSet=="string"?d.imageSrcSet:void 0,imageSizes:typeof d.imageSizes=="string"?d.imageSizes:void 0,media:typeof d.media=="string"?d.media:void 0})}},Nn.preloadModule=function(m,d){if(typeof m=="string")if(d){var g=p(d.as,d.crossOrigin);r.d.m(m,{as:typeof d.as=="string"&&d.as!=="script"?d.as:void 0,crossOrigin:g,integrity:typeof d.integrity=="string"?d.integrity:void 0})}else r.d.m(m)},Nn.requestFormReset=function(m){r.d.r(m)},Nn.unstable_batchedUpdates=function(m,d){return m(d)},Nn.useFormState=function(m,d,g){return f.H.useFormState(m,d,g)},Nn.useFormStatus=function(){return f.H.useHostTransitionStatus()},Nn.version="19.2.7",Nn}var Q_;function sy(){if(Q_)return gh.exports;Q_=1;function s(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(s)}catch(t){console.error(t)}}return s(),gh.exports=ry(),gh.exports}var J_;function oy(){if(J_)return Wo;J_=1;var s=ay(),t=kd(),i=sy();function r(e){var n="https://react.dev/errors/"+e;if(1<arguments.length){n+="?args[]="+encodeURIComponent(arguments[1]);for(var a=2;a<arguments.length;a++)n+="&args[]="+encodeURIComponent(arguments[a])}return"Minified React error #"+e+"; visit "+n+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}function l(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function u(e){var n=e,a=e;if(e.alternate)for(;n.return;)n=n.return;else{e=n;do n=e,(n.flags&4098)!==0&&(a=n.return),e=n.return;while(e)}return n.tag===3?a:null}function f(e){if(e.tag===13){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function p(e){if(e.tag===31){var n=e.memoizedState;if(n===null&&(e=e.alternate,e!==null&&(n=e.memoizedState)),n!==null)return n.dehydrated}return null}function m(e){if(u(e)!==e)throw Error(r(188))}function d(e){var n=e.alternate;if(!n){if(n=u(e),n===null)throw Error(r(188));return n!==e?null:e}for(var a=e,o=n;;){var c=a.return;if(c===null)break;var h=c.alternate;if(h===null){if(o=c.return,o!==null){a=o;continue}break}if(c.child===h.child){for(h=c.child;h;){if(h===a)return m(c),e;if(h===o)return m(c),n;h=h.sibling}throw Error(r(188))}if(a.return!==o.return)a=c,o=h;else{for(var x=!1,R=c.child;R;){if(R===a){x=!0,a=c,o=h;break}if(R===o){x=!0,o=c,a=h;break}R=R.sibling}if(!x){for(R=h.child;R;){if(R===a){x=!0,a=h,o=c;break}if(R===o){x=!0,o=h,a=c;break}R=R.sibling}if(!x)throw Error(r(189))}}if(a.alternate!==o)throw Error(r(190))}if(a.tag!==3)throw Error(r(188));return a.stateNode.current===a?e:n}function g(e){var n=e.tag;if(n===5||n===26||n===27||n===6)return e;for(e=e.child;e!==null;){if(n=g(e),n!==null)return n;e=e.sibling}return null}var v=Object.assign,_=Symbol.for("react.element"),M=Symbol.for("react.transitional.element"),T=Symbol.for("react.portal"),w=Symbol.for("react.fragment"),E=Symbol.for("react.strict_mode"),S=Symbol.for("react.profiler"),F=Symbol.for("react.consumer"),z=Symbol.for("react.context"),C=Symbol.for("react.forward_ref"),N=Symbol.for("react.suspense"),D=Symbol.for("react.suspense_list"),O=Symbol.for("react.memo"),b=Symbol.for("react.lazy"),P=Symbol.for("react.activity"),q=Symbol.for("react.memo_cache_sentinel"),G=Symbol.iterator;function Z(e){return e===null||typeof e!="object"?null:(e=G&&e[G]||e["@@iterator"],typeof e=="function"?e:null)}var ht=Symbol.for("react.client.reference");function mt(e){if(e==null)return null;if(typeof e=="function")return e.$$typeof===ht?null:e.displayName||e.name||null;if(typeof e=="string")return e;switch(e){case w:return"Fragment";case S:return"Profiler";case E:return"StrictMode";case N:return"Suspense";case D:return"SuspenseList";case P:return"Activity"}if(typeof e=="object")switch(e.$$typeof){case T:return"Portal";case z:return e.displayName||"Context";case F:return(e._context.displayName||"Context")+".Consumer";case C:var n=e.render;return e=e.displayName,e||(e=n.displayName||n.name||"",e=e!==""?"ForwardRef("+e+")":"ForwardRef"),e;case O:return n=e.displayName||null,n!==null?n:mt(e.type)||"Memo";case b:n=e._payload,e=e._init;try{return mt(e(n))}catch{}}return null}var J=Array.isArray,I=t.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,H=i.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,j={pending:!1,data:null,method:null,action:null},gt=[],Et=-1;function L(e){return{current:e}}function K(e){0>Et||(e.current=gt[Et],gt[Et]=null,Et--)}function Mt(e,n){Et++,gt[Et]=e.current,e.current=n}var Rt=L(null),Pt=L(null),at=L(null),xt=L(null);function yt(e,n){switch(Mt(at,n),Mt(Pt,e),Mt(Rt,null),n.nodeType){case 9:case 11:e=(e=n.documentElement)&&(e=e.namespaceURI)?h_(e):0;break;default:if(e=n.tagName,n=n.namespaceURI)n=h_(n),e=d_(n,e);else switch(e){case"svg":e=1;break;case"math":e=2;break;default:e=0}}K(Rt),Mt(Rt,e)}function Bt(){K(Rt),K(Pt),K(at)}function ee(e){e.memoizedState!==null&&Mt(xt,e);var n=Rt.current,a=d_(n,e.type);n!==a&&(Mt(Pt,e),Mt(Rt,a))}function Kt(e){Pt.current===e&&(K(Rt),K(Pt)),xt.current===e&&(K(xt),Ho._currentValue=j)}var qe,ce;function Se(e){if(qe===void 0)try{throw Error()}catch(a){var n=a.stack.trim().match(/\n( *(at )?)/);qe=n&&n[1]||"",ce=-1<a.stack.indexOf(`
    at`)?" (<anonymous>)":-1<a.stack.indexOf("@")?"@unknown:0:0":""}return`
`+qe+e+ce}var ye=!1;function fe(e,n){if(!e||ye)return"";ye=!0;var a=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var o={DetermineComponentFrameRoot:function(){try{if(n){var vt=function(){throw Error()};if(Object.defineProperty(vt.prototype,"props",{set:function(){throw Error()}}),typeof Reflect=="object"&&Reflect.construct){try{Reflect.construct(vt,[])}catch(lt){var ot=lt}Reflect.construct(e,[],vt)}else{try{vt.call()}catch(lt){ot=lt}e.call(vt.prototype)}}else{try{throw Error()}catch(lt){ot=lt}(vt=e())&&typeof vt.catch=="function"&&vt.catch(function(){})}}catch(lt){if(lt&&ot&&typeof lt.stack=="string")return[lt.stack,ot.stack]}return[null,null]}};o.DetermineComponentFrameRoot.displayName="DetermineComponentFrameRoot";var c=Object.getOwnPropertyDescriptor(o.DetermineComponentFrameRoot,"name");c&&c.configurable&&Object.defineProperty(o.DetermineComponentFrameRoot,"name",{value:"DetermineComponentFrameRoot"});var h=o.DetermineComponentFrameRoot(),x=h[0],R=h[1];if(x&&R){var B=x.split(`
`),et=R.split(`
`);for(c=o=0;o<B.length&&!B[o].includes("DetermineComponentFrameRoot");)o++;for(;c<et.length&&!et[c].includes("DetermineComponentFrameRoot");)c++;if(o===B.length||c===et.length)for(o=B.length-1,c=et.length-1;1<=o&&0<=c&&B[o]!==et[c];)c--;for(;1<=o&&0<=c;o--,c--)if(B[o]!==et[c]){if(o!==1||c!==1)do if(o--,c--,0>c||B[o]!==et[c]){var dt=`
`+B[o].replace(" at new "," at ");return e.displayName&&dt.includes("<anonymous>")&&(dt=dt.replace("<anonymous>",e.displayName)),dt}while(1<=o&&0<=c);break}}}finally{ye=!1,Error.prepareStackTrace=a}return(a=e?e.displayName||e.name:"")?Se(a):""}function en(e,n){switch(e.tag){case 26:case 27:case 5:return Se(e.type);case 16:return Se("Lazy");case 13:return e.child!==n&&n!==null?Se("Suspense Fallback"):Se("Suspense");case 19:return Se("SuspenseList");case 0:case 15:return fe(e.type,!1);case 11:return fe(e.type.render,!1);case 1:return fe(e.type,!0);case 31:return Se("Activity");default:return""}}function nn(e){try{var n="",a=null;do n+=en(e,a),a=e,e=e.return;while(e);return n}catch(o){return`
Error generating stack: `+o.message+`
`+o.stack}}var an=Object.prototype.hasOwnProperty,ln=s.unstable_scheduleCallback,We=s.unstable_cancelCallback,rn=s.unstable_shouldYield,W=s.unstable_requestPaint,ze=s.unstable_now,Ce=s.unstable_getCurrentPriorityLevel,U=s.unstable_ImmediatePriority,y=s.unstable_UserBlockingPriority,Q=s.unstable_NormalPriority,rt=s.unstable_LowPriority,ct=s.unstable_IdlePriority,bt=s.log,wt=s.unstable_setDisableYieldValue,ut=null,ft=null;function At(e){if(typeof bt=="function"&&wt(e),ft&&typeof ft.setStrictMode=="function")try{ft.setStrictMode(ut,e)}catch{}}var Ft=Math.clz32?Math.clz32:Zt,Lt=Math.log,Dt=Math.LN2;function Zt(e){return e>>>=0,e===0?32:31-(Lt(e)/Dt|0)|0}var Qt=256,ne=262144,k=4194304;function Tt(e){var n=e&42;if(n!==0)return n;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:return e&261888;case 262144:case 524288:case 1048576:case 2097152:return e&3932160;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function pt(e,n,a){var o=e.pendingLanes;if(o===0)return 0;var c=0,h=e.suspendedLanes,x=e.pingedLanes;e=e.warmLanes;var R=o&134217727;return R!==0?(o=R&~h,o!==0?c=Tt(o):(x&=R,x!==0?c=Tt(x):a||(a=R&~e,a!==0&&(c=Tt(a))))):(R=o&~h,R!==0?c=Tt(R):x!==0?c=Tt(x):a||(a=o&~e,a!==0&&(c=Tt(a)))),c===0?0:n!==0&&n!==c&&(n&h)===0&&(h=c&-c,a=n&-n,h>=a||h===32&&(a&4194048)!==0)?n:c}function Ct(e,n){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&n)===0}function It(e,n){switch(e){case 1:case 2:case 4:case 8:case 64:return n+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return n+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function St(){var e=k;return k<<=1,(k&62914560)===0&&(k=4194304),e}function Wt(e){for(var n=[],a=0;31>a;a++)n.push(e);return n}function Gt(e,n){e.pendingLanes|=n,n!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function Ke(e,n,a,o,c,h){var x=e.pendingLanes;e.pendingLanes=a,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=a,e.entangledLanes&=a,e.errorRecoveryDisabledLanes&=a,e.shellSuspendCounter=0;var R=e.entanglements,B=e.expirationTimes,et=e.hiddenUpdates;for(a=x&~a;0<a;){var dt=31-Ft(a),vt=1<<dt;R[dt]=0,B[dt]=-1;var ot=et[dt];if(ot!==null)for(et[dt]=null,dt=0;dt<ot.length;dt++){var lt=ot[dt];lt!==null&&(lt.lane&=-536870913)}a&=~vt}o!==0&&Ue(e,o,0),h!==0&&c===0&&e.tag!==0&&(e.suspendedLanes|=h&~(x&~n))}function Ue(e,n,a){e.pendingLanes|=n,e.suspendedLanes&=~n;var o=31-Ft(n);e.entangledLanes|=n,e.entanglements[o]=e.entanglements[o]|1073741824|a&261930}function Jn(e,n){var a=e.entangledLanes|=n;for(e=e.entanglements;a;){var o=31-Ft(a),c=1<<o;c&n|e[o]&n&&(e[o]|=n),a&=~c}}function jn(e,n){var a=n&-n;return a=(a&42)!==0?1:$s(a),(a&(e.suspendedLanes|n))!==0?0:a}function $s(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function to(e){return e&=-e,2<e?8<e?(e&134217727)!==0?32:268435456:8:2}function eo(){var e=H.p;return e!==0?e:(e=window.event,e===void 0?32:I_(e.type))}function Kr(e,n){var a=H.p;try{return H.p=e,n()}finally{H.p=a}}var Ii=Math.random().toString(36).slice(2),fn="__reactFiber$"+Ii,Tn="__reactProps$"+Ii,Gn="__reactContainer$"+Ii,mr="__reactEvents$"+Ii,ll="__reactListeners$"+Ii,ul="__reactHandles$"+Ii,gr="__reactResources$"+Ii,wa="__reactMarker$"+Ii;function Da(e){delete e[fn],delete e[Tn],delete e[mr],delete e[ll],delete e[ul]}function ji(e){var n=e[fn];if(n)return n;for(var a=e.parentNode;a;){if(n=a[Gn]||a[fn]){if(a=n.alternate,n.child!==null||a!==null&&a.child!==null)for(e=S_(e);e!==null;){if(a=e[fn])return a;e=S_(e)}return n}e=a,a=e.parentNode}return null}function $i(e){if(e=e[fn]||e[Gn]){var n=e.tag;if(n===5||n===6||n===13||n===31||n===26||n===27||n===3)return e}return null}function _r(e){var n=e.tag;if(n===5||n===26||n===27||n===6)return e.stateNode;throw Error(r(33))}function Ua(e){var n=e[gr];return n||(n=e[gr]={hoistableStyles:new Map,hoistableScripts:new Map}),n}function hn(e){e[wa]=!0}var cl=new Set,A={};function X(e,n){st(e,n),st(e+"Capture",n)}function st(e,n){for(A[e]=n,e=0;e<n.length;e++)cl.add(n[e])}var nt=RegExp("^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$"),it={},Nt={};function Ht(e){return an.call(Nt,e)?!0:an.call(it,e)?!1:nt.test(e)?Nt[e]=!0:(it[e]=!0,!1)}function Ut(e,n,a){if(Ht(n))if(a===null)e.removeAttribute(n);else{switch(typeof a){case"undefined":case"function":case"symbol":e.removeAttribute(n);return;case"boolean":var o=n.toLowerCase().slice(0,5);if(o!=="data-"&&o!=="aria-"){e.removeAttribute(n);return}}e.setAttribute(n,""+a)}}function kt(e,n,a){if(a===null)e.removeAttribute(n);else{switch(typeof a){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(n);return}e.setAttribute(n,""+a)}}function Vt(e,n,a,o){if(o===null)e.removeAttribute(a);else{switch(typeof o){case"undefined":case"function":case"symbol":case"boolean":e.removeAttribute(a);return}e.setAttributeNS(n,a,""+o)}}function Jt(e){switch(typeof e){case"bigint":case"boolean":case"number":case"string":case"undefined":return e;case"object":return e;default:return""}}function se(e){var n=e.type;return(e=e.nodeName)&&e.toLowerCase()==="input"&&(n==="checkbox"||n==="radio")}function Yt(e,n,a){var o=Object.getOwnPropertyDescriptor(e.constructor.prototype,n);if(!e.hasOwnProperty(n)&&typeof o<"u"&&typeof o.get=="function"&&typeof o.set=="function"){var c=o.get,h=o.set;return Object.defineProperty(e,n,{configurable:!0,get:function(){return c.call(this)},set:function(x){a=""+x,h.call(this,x)}}),Object.defineProperty(e,n,{enumerable:o.enumerable}),{getValue:function(){return a},setValue:function(x){a=""+x},stopTracking:function(){e._valueTracker=null,delete e[n]}}}}function Te(e){if(!e._valueTracker){var n=se(e)?"checked":"value";e._valueTracker=Yt(e,n,""+e[n])}}function Qe(e){if(!e)return!1;var n=e._valueTracker;if(!n)return!0;var a=n.getValue(),o="";return e&&(o=se(e)?e.checked?"true":"false":e.value),e=o,e!==a?(n.setValue(e),!0):!1}function ke(e){if(e=e||(typeof document<"u"?document:void 0),typeof e>"u")return null;try{return e.activeElement||e.body}catch{return e.body}}var Le=/[\n"\\]/g;function Ne(e){return e.replace(Le,function(n){return"\\"+n.charCodeAt(0).toString(16)+" "})}function zt(e,n,a,o,c,h,x,R){e.name="",x!=null&&typeof x!="function"&&typeof x!="symbol"&&typeof x!="boolean"?e.type=x:e.removeAttribute("type"),n!=null?x==="number"?(n===0&&e.value===""||e.value!=n)&&(e.value=""+Jt(n)):e.value!==""+Jt(n)&&(e.value=""+Jt(n)):x!=="submit"&&x!=="reset"||e.removeAttribute("value"),n!=null?he(e,x,Jt(n)):a!=null?he(e,x,Jt(a)):o!=null&&e.removeAttribute("value"),c==null&&h!=null&&(e.defaultChecked=!!h),c!=null&&(e.checked=c&&typeof c!="function"&&typeof c!="symbol"),R!=null&&typeof R!="function"&&typeof R!="symbol"&&typeof R!="boolean"?e.name=""+Jt(R):e.removeAttribute("name")}function Ln(e,n,a,o,c,h,x,R){if(h!=null&&typeof h!="function"&&typeof h!="symbol"&&typeof h!="boolean"&&(e.type=h),n!=null||a!=null){if(!(h!=="submit"&&h!=="reset"||n!=null)){Te(e);return}a=a!=null?""+Jt(a):"",n=n!=null?""+Jt(n):a,R||n===e.value||(e.value=n),e.defaultValue=n}o=o??c,o=typeof o!="function"&&typeof o!="symbol"&&!!o,e.checked=R?e.checked:!!o,e.defaultChecked=!!o,x!=null&&typeof x!="function"&&typeof x!="symbol"&&typeof x!="boolean"&&(e.name=x),Te(e)}function he(e,n,a){n==="number"&&ke(e.ownerDocument)===e||e.defaultValue===""+a||(e.defaultValue=""+a)}function vn(e,n,a,o){if(e=e.options,n){n={};for(var c=0;c<a.length;c++)n["$"+a[c]]=!0;for(a=0;a<e.length;a++)c=n.hasOwnProperty("$"+e[a].value),e[a].selected!==c&&(e[a].selected=c),c&&o&&(e[a].defaultSelected=!0)}else{for(a=""+Jt(a),n=null,c=0;c<e.length;c++){if(e[c].value===a){e[c].selected=!0,o&&(e[c].defaultSelected=!0);return}n!==null||e[c].disabled||(n=e[c])}n!==null&&(n.selected=!0)}}function $n(e,n,a){if(n!=null&&(n=""+Jt(n),n!==e.value&&(e.value=n),a==null)){e.defaultValue!==n&&(e.defaultValue=n);return}e.defaultValue=a!=null?""+Jt(a):""}function bi(e,n,a,o){if(n==null){if(o!=null){if(a!=null)throw Error(r(92));if(J(o)){if(1<o.length)throw Error(r(93));o=o[0]}a=o}a==null&&(a=""),n=a}a=Jt(n),e.defaultValue=a,o=e.textContent,o===a&&o!==""&&o!==null&&(e.value=o),Te(e)}function ti(e,n){if(n){var a=e.firstChild;if(a&&a===e.lastChild&&a.nodeType===3){a.nodeValue=n;return}}e.textContent=n}var Oe=new Set("animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp".split(" "));function Je(e,n,a){var o=n.indexOf("--")===0;a==null||typeof a=="boolean"||a===""?o?e.setProperty(n,""):n==="float"?e.cssFloat="":e[n]="":o?e.setProperty(n,a):typeof a!="number"||a===0||Oe.has(n)?n==="float"?e.cssFloat=a:e[n]=(""+a).trim():e[n]=a+"px"}function Ti(e,n,a){if(n!=null&&typeof n!="object")throw Error(r(62));if(e=e.style,a!=null){for(var o in a)!a.hasOwnProperty(o)||n!=null&&n.hasOwnProperty(o)||(o.indexOf("--")===0?e.setProperty(o,""):o==="float"?e.cssFloat="":e[o]="");for(var c in n)o=n[c],n.hasOwnProperty(c)&&a[c]!==o&&Je(e,c,o)}else for(var h in n)n.hasOwnProperty(h)&&Je(e,h,n[h])}function De(e){if(e.indexOf("-")===-1)return!1;switch(e){case"annotation-xml":case"color-profile":case"font-face":case"font-face-src":case"font-face-uri":case"font-face-format":case"font-face-name":case"missing-glyph":return!1;default:return!0}}var Fi=new Map([["acceptCharset","accept-charset"],["htmlFor","for"],["httpEquiv","http-equiv"],["crossOrigin","crossorigin"],["accentHeight","accent-height"],["alignmentBaseline","alignment-baseline"],["arabicForm","arabic-form"],["baselineShift","baseline-shift"],["capHeight","cap-height"],["clipPath","clip-path"],["clipRule","clip-rule"],["colorInterpolation","color-interpolation"],["colorInterpolationFilters","color-interpolation-filters"],["colorProfile","color-profile"],["colorRendering","color-rendering"],["dominantBaseline","dominant-baseline"],["enableBackground","enable-background"],["fillOpacity","fill-opacity"],["fillRule","fill-rule"],["floodColor","flood-color"],["floodOpacity","flood-opacity"],["fontFamily","font-family"],["fontSize","font-size"],["fontSizeAdjust","font-size-adjust"],["fontStretch","font-stretch"],["fontStyle","font-style"],["fontVariant","font-variant"],["fontWeight","font-weight"],["glyphName","glyph-name"],["glyphOrientationHorizontal","glyph-orientation-horizontal"],["glyphOrientationVertical","glyph-orientation-vertical"],["horizAdvX","horiz-adv-x"],["horizOriginX","horiz-origin-x"],["imageRendering","image-rendering"],["letterSpacing","letter-spacing"],["lightingColor","lighting-color"],["markerEnd","marker-end"],["markerMid","marker-mid"],["markerStart","marker-start"],["overlinePosition","overline-position"],["overlineThickness","overline-thickness"],["paintOrder","paint-order"],["panose-1","panose-1"],["pointerEvents","pointer-events"],["renderingIntent","rendering-intent"],["shapeRendering","shape-rendering"],["stopColor","stop-color"],["stopOpacity","stop-opacity"],["strikethroughPosition","strikethrough-position"],["strikethroughThickness","strikethrough-thickness"],["strokeDasharray","stroke-dasharray"],["strokeDashoffset","stroke-dashoffset"],["strokeLinecap","stroke-linecap"],["strokeLinejoin","stroke-linejoin"],["strokeMiterlimit","stroke-miterlimit"],["strokeOpacity","stroke-opacity"],["strokeWidth","stroke-width"],["textAnchor","text-anchor"],["textDecoration","text-decoration"],["textRendering","text-rendering"],["transformOrigin","transform-origin"],["underlinePosition","underline-position"],["underlineThickness","underline-thickness"],["unicodeBidi","unicode-bidi"],["unicodeRange","unicode-range"],["unitsPerEm","units-per-em"],["vAlphabetic","v-alphabetic"],["vHanging","v-hanging"],["vIdeographic","v-ideographic"],["vMathematical","v-mathematical"],["vectorEffect","vector-effect"],["vertAdvY","vert-adv-y"],["vertOriginX","vert-origin-x"],["vertOriginY","vert-origin-y"],["wordSpacing","word-spacing"],["writingMode","writing-mode"],["xmlnsXlink","xmlns:xlink"],["xHeight","x-height"]]),La=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function vr(e){return La.test(""+e)?"javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')":e}function ta(){}var oc=null;function lc(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var Qr=null,Jr=null;function fp(e){var n=$i(e);if(n&&(e=n.stateNode)){var a=e[Tn]||null;t:switch(e=n.stateNode,n.type){case"input":if(zt(e,a.value,a.defaultValue,a.defaultValue,a.checked,a.defaultChecked,a.type,a.name),n=a.name,a.type==="radio"&&n!=null){for(a=e;a.parentNode;)a=a.parentNode;for(a=a.querySelectorAll('input[name="'+Ne(""+n)+'"][type="radio"]'),n=0;n<a.length;n++){var o=a[n];if(o!==e&&o.form===e.form){var c=o[Tn]||null;if(!c)throw Error(r(90));zt(o,c.value,c.defaultValue,c.defaultValue,c.checked,c.defaultChecked,c.type,c.name)}}for(n=0;n<a.length;n++)o=a[n],o.form===e.form&&Qe(o)}break t;case"textarea":$n(e,a.value,a.defaultValue);break t;case"select":n=a.value,n!=null&&vn(e,!!a.multiple,n,!1)}}}var uc=!1;function hp(e,n,a){if(uc)return e(n,a);uc=!0;try{var o=e(n);return o}finally{if(uc=!1,(Qr!==null||Jr!==null)&&(Jl(),Qr&&(n=Qr,e=Jr,Jr=Qr=null,fp(n),e)))for(n=0;n<e.length;n++)fp(e[n])}}function no(e,n){var a=e.stateNode;if(a===null)return null;var o=a[Tn]||null;if(o===null)return null;a=o[n];t:switch(n){case"onClick":case"onClickCapture":case"onDoubleClick":case"onDoubleClickCapture":case"onMouseDown":case"onMouseDownCapture":case"onMouseMove":case"onMouseMoveCapture":case"onMouseUp":case"onMouseUpCapture":case"onMouseEnter":(o=!o.disabled)||(e=e.type,o=!(e==="button"||e==="input"||e==="select"||e==="textarea")),e=!o;break t;default:e=!1}if(e)return null;if(a&&typeof a!="function")throw Error(r(231,n,typeof a));return a}var ea=!(typeof window>"u"||typeof window.document>"u"||typeof window.document.createElement>"u"),cc=!1;if(ea)try{var io={};Object.defineProperty(io,"passive",{get:function(){cc=!0}}),window.addEventListener("test",io,io),window.removeEventListener("test",io,io)}catch{cc=!1}var Na=null,fc=null,fl=null;function dp(){if(fl)return fl;var e,n=fc,a=n.length,o,c="value"in Na?Na.value:Na.textContent,h=c.length;for(e=0;e<a&&n[e]===c[e];e++);var x=a-e;for(o=1;o<=x&&n[a-o]===c[h-o];o++);return fl=c.slice(e,1<o?1-o:void 0)}function hl(e){var n=e.keyCode;return"charCode"in e?(e=e.charCode,e===0&&n===13&&(e=13)):e=n,e===10&&(e=13),32<=e||e===13?e:0}function dl(){return!0}function pp(){return!1}function Vn(e){function n(a,o,c,h,x){this._reactName=a,this._targetInst=c,this.type=o,this.nativeEvent=h,this.target=x,this.currentTarget=null;for(var R in e)e.hasOwnProperty(R)&&(a=e[R],this[R]=a?a(h):h[R]);return this.isDefaultPrevented=(h.defaultPrevented!=null?h.defaultPrevented:h.returnValue===!1)?dl:pp,this.isPropagationStopped=pp,this}return v(n.prototype,{preventDefault:function(){this.defaultPrevented=!0;var a=this.nativeEvent;a&&(a.preventDefault?a.preventDefault():typeof a.returnValue!="unknown"&&(a.returnValue=!1),this.isDefaultPrevented=dl)},stopPropagation:function(){var a=this.nativeEvent;a&&(a.stopPropagation?a.stopPropagation():typeof a.cancelBubble!="unknown"&&(a.cancelBubble=!0),this.isPropagationStopped=dl)},persist:function(){},isPersistent:dl}),n}var xr={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},pl=Vn(xr),ao=v({},xr,{view:0,detail:0}),jv=Vn(ao),hc,dc,ro,ml=v({},ao,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:mc,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return"movementX"in e?e.movementX:(e!==ro&&(ro&&e.type==="mousemove"?(hc=e.screenX-ro.screenX,dc=e.screenY-ro.screenY):dc=hc=0,ro=e),hc)},movementY:function(e){return"movementY"in e?e.movementY:dc}}),mp=Vn(ml),$v=v({},ml,{dataTransfer:0}),tx=Vn($v),ex=v({},ao,{relatedTarget:0}),pc=Vn(ex),nx=v({},xr,{animationName:0,elapsedTime:0,pseudoElement:0}),ix=Vn(nx),ax=v({},xr,{clipboardData:function(e){return"clipboardData"in e?e.clipboardData:window.clipboardData}}),rx=Vn(ax),sx=v({},xr,{data:0}),gp=Vn(sx),ox={Esc:"Escape",Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},lx={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},ux={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function cx(e){var n=this.nativeEvent;return n.getModifierState?n.getModifierState(e):(e=ux[e])?!!n[e]:!1}function mc(){return cx}var fx=v({},ao,{key:function(e){if(e.key){var n=ox[e.key]||e.key;if(n!=="Unidentified")return n}return e.type==="keypress"?(e=hl(e),e===13?"Enter":String.fromCharCode(e)):e.type==="keydown"||e.type==="keyup"?lx[e.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:mc,charCode:function(e){return e.type==="keypress"?hl(e):0},keyCode:function(e){return e.type==="keydown"||e.type==="keyup"?e.keyCode:0},which:function(e){return e.type==="keypress"?hl(e):e.type==="keydown"||e.type==="keyup"?e.keyCode:0}}),hx=Vn(fx),dx=v({},ml,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),_p=Vn(dx),px=v({},ao,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:mc}),mx=Vn(px),gx=v({},xr,{propertyName:0,elapsedTime:0,pseudoElement:0}),_x=Vn(gx),vx=v({},ml,{deltaX:function(e){return"deltaX"in e?e.deltaX:"wheelDeltaX"in e?-e.wheelDeltaX:0},deltaY:function(e){return"deltaY"in e?e.deltaY:"wheelDeltaY"in e?-e.wheelDeltaY:"wheelDelta"in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0}),xx=Vn(vx),Sx=v({},xr,{newState:0,oldState:0}),yx=Vn(Sx),Mx=[9,13,27,32],gc=ea&&"CompositionEvent"in window,so=null;ea&&"documentMode"in document&&(so=document.documentMode);var Ex=ea&&"TextEvent"in window&&!so,vp=ea&&(!gc||so&&8<so&&11>=so),xp=" ",Sp=!1;function yp(e,n){switch(e){case"keyup":return Mx.indexOf(n.keyCode)!==-1;case"keydown":return n.keyCode!==229;case"keypress":case"mousedown":case"focusout":return!0;default:return!1}}function Mp(e){return e=e.detail,typeof e=="object"&&"data"in e?e.data:null}var jr=!1;function bx(e,n){switch(e){case"compositionend":return Mp(n);case"keypress":return n.which!==32?null:(Sp=!0,xp);case"textInput":return e=n.data,e===xp&&Sp?null:e;default:return null}}function Tx(e,n){if(jr)return e==="compositionend"||!gc&&yp(e,n)?(e=dp(),fl=fc=Na=null,jr=!1,e):null;switch(e){case"paste":return null;case"keypress":if(!(n.ctrlKey||n.altKey||n.metaKey)||n.ctrlKey&&n.altKey){if(n.char&&1<n.char.length)return n.char;if(n.which)return String.fromCharCode(n.which)}return null;case"compositionend":return vp&&n.locale!=="ko"?null:n.data;default:return null}}var Ax={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function Ep(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n==="input"?!!Ax[e.type]:n==="textarea"}function bp(e,n,a,o){Qr?Jr?Jr.push(o):Jr=[o]:Qr=o,n=au(n,"onChange"),0<n.length&&(a=new pl("onChange","change",null,a,o),e.push({event:a,listeners:n}))}var oo=null,lo=null;function Rx(e){s_(e,0)}function gl(e){var n=_r(e);if(Qe(n))return e}function Tp(e,n){if(e==="change")return n}var Ap=!1;if(ea){var _c;if(ea){var vc="oninput"in document;if(!vc){var Rp=document.createElement("div");Rp.setAttribute("oninput","return;"),vc=typeof Rp.oninput=="function"}_c=vc}else _c=!1;Ap=_c&&(!document.documentMode||9<document.documentMode)}function Cp(){oo&&(oo.detachEvent("onpropertychange",wp),lo=oo=null)}function wp(e){if(e.propertyName==="value"&&gl(lo)){var n=[];bp(n,lo,e,lc(e)),hp(Rx,n)}}function Cx(e,n,a){e==="focusin"?(Cp(),oo=n,lo=a,oo.attachEvent("onpropertychange",wp)):e==="focusout"&&Cp()}function wx(e){if(e==="selectionchange"||e==="keyup"||e==="keydown")return gl(lo)}function Dx(e,n){if(e==="click")return gl(n)}function Ux(e,n){if(e==="input"||e==="change")return gl(n)}function Lx(e,n){return e===n&&(e!==0||1/e===1/n)||e!==e&&n!==n}var ei=typeof Object.is=="function"?Object.is:Lx;function uo(e,n){if(ei(e,n))return!0;if(typeof e!="object"||e===null||typeof n!="object"||n===null)return!1;var a=Object.keys(e),o=Object.keys(n);if(a.length!==o.length)return!1;for(o=0;o<a.length;o++){var c=a[o];if(!an.call(n,c)||!ei(e[c],n[c]))return!1}return!0}function Dp(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function Up(e,n){var a=Dp(e);e=0;for(var o;a;){if(a.nodeType===3){if(o=e+a.textContent.length,e<=n&&o>=n)return{node:a,offset:n-e};e=o}t:{for(;a;){if(a.nextSibling){a=a.nextSibling;break t}a=a.parentNode}a=void 0}a=Dp(a)}}function Lp(e,n){return e&&n?e===n?!0:e&&e.nodeType===3?!1:n&&n.nodeType===3?Lp(e,n.parentNode):"contains"in e?e.contains(n):e.compareDocumentPosition?!!(e.compareDocumentPosition(n)&16):!1:!1}function Np(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var n=ke(e.document);n instanceof e.HTMLIFrameElement;){try{var a=typeof n.contentWindow.location.href=="string"}catch{a=!1}if(a)e=n.contentWindow;else break;n=ke(e.document)}return n}function xc(e){var n=e&&e.nodeName&&e.nodeName.toLowerCase();return n&&(n==="input"&&(e.type==="text"||e.type==="search"||e.type==="tel"||e.type==="url"||e.type==="password")||n==="textarea"||e.contentEditable==="true")}var Nx=ea&&"documentMode"in document&&11>=document.documentMode,$r=null,Sc=null,co=null,yc=!1;function Op(e,n,a){var o=a.window===a?a.document:a.nodeType===9?a:a.ownerDocument;yc||$r==null||$r!==ke(o)||(o=$r,"selectionStart"in o&&xc(o)?o={start:o.selectionStart,end:o.selectionEnd}:(o=(o.ownerDocument&&o.ownerDocument.defaultView||window).getSelection(),o={anchorNode:o.anchorNode,anchorOffset:o.anchorOffset,focusNode:o.focusNode,focusOffset:o.focusOffset}),co&&uo(co,o)||(co=o,o=au(Sc,"onSelect"),0<o.length&&(n=new pl("onSelect","select",null,n,a),e.push({event:n,listeners:o}),n.target=$r)))}function Sr(e,n){var a={};return a[e.toLowerCase()]=n.toLowerCase(),a["Webkit"+e]="webkit"+n,a["Moz"+e]="moz"+n,a}var ts={animationend:Sr("Animation","AnimationEnd"),animationiteration:Sr("Animation","AnimationIteration"),animationstart:Sr("Animation","AnimationStart"),transitionrun:Sr("Transition","TransitionRun"),transitionstart:Sr("Transition","TransitionStart"),transitioncancel:Sr("Transition","TransitionCancel"),transitionend:Sr("Transition","TransitionEnd")},Mc={},Pp={};ea&&(Pp=document.createElement("div").style,"AnimationEvent"in window||(delete ts.animationend.animation,delete ts.animationiteration.animation,delete ts.animationstart.animation),"TransitionEvent"in window||delete ts.transitionend.transition);function yr(e){if(Mc[e])return Mc[e];if(!ts[e])return e;var n=ts[e],a;for(a in n)if(n.hasOwnProperty(a)&&a in Pp)return Mc[e]=n[a];return e}var Ip=yr("animationend"),Fp=yr("animationiteration"),zp=yr("animationstart"),Ox=yr("transitionrun"),Px=yr("transitionstart"),Ix=yr("transitioncancel"),Bp=yr("transitionend"),Hp=new Map,Ec="abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");Ec.push("scrollEnd");function Ai(e,n){Hp.set(e,n),X(n,[e])}var _l=typeof reportError=="function"?reportError:function(e){if(typeof window=="object"&&typeof window.ErrorEvent=="function"){var n=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof e=="object"&&e!==null&&typeof e.message=="string"?String(e.message):String(e),error:e});if(!window.dispatchEvent(n))return}else if(typeof process=="object"&&typeof process.emit=="function"){process.emit("uncaughtException",e);return}console.error(e)},di=[],es=0,bc=0;function vl(){for(var e=es,n=bc=es=0;n<e;){var a=di[n];di[n++]=null;var o=di[n];di[n++]=null;var c=di[n];di[n++]=null;var h=di[n];if(di[n++]=null,o!==null&&c!==null){var x=o.pending;x===null?c.next=c:(c.next=x.next,x.next=c),o.pending=c}h!==0&&Gp(a,c,h)}}function xl(e,n,a,o){di[es++]=e,di[es++]=n,di[es++]=a,di[es++]=o,bc|=o,e.lanes|=o,e=e.alternate,e!==null&&(e.lanes|=o)}function Tc(e,n,a,o){return xl(e,n,a,o),Sl(e)}function Mr(e,n){return xl(e,null,null,n),Sl(e)}function Gp(e,n,a){e.lanes|=a;var o=e.alternate;o!==null&&(o.lanes|=a);for(var c=!1,h=e.return;h!==null;)h.childLanes|=a,o=h.alternate,o!==null&&(o.childLanes|=a),h.tag===22&&(e=h.stateNode,e===null||e._visibility&1||(c=!0)),e=h,h=h.return;return e.tag===3?(h=e.stateNode,c&&n!==null&&(c=31-Ft(a),e=h.hiddenUpdates,o=e[c],o===null?e[c]=[n]:o.push(n),n.lane=a|536870912),h):null}function Sl(e){if(50<No)throw No=0,Pf=null,Error(r(185));for(var n=e.return;n!==null;)e=n,n=e.return;return e.tag===3?e.stateNode:null}var ns={};function Fx(e,n,a,o){this.tag=e,this.key=a,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=n,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=o,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function ni(e,n,a,o){return new Fx(e,n,a,o)}function Ac(e){return e=e.prototype,!(!e||!e.isReactComponent)}function na(e,n){var a=e.alternate;return a===null?(a=ni(e.tag,n,e.key,e.mode),a.elementType=e.elementType,a.type=e.type,a.stateNode=e.stateNode,a.alternate=e,e.alternate=a):(a.pendingProps=n,a.type=e.type,a.flags=0,a.subtreeFlags=0,a.deletions=null),a.flags=e.flags&65011712,a.childLanes=e.childLanes,a.lanes=e.lanes,a.child=e.child,a.memoizedProps=e.memoizedProps,a.memoizedState=e.memoizedState,a.updateQueue=e.updateQueue,n=e.dependencies,a.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext},a.sibling=e.sibling,a.index=e.index,a.ref=e.ref,a.refCleanup=e.refCleanup,a}function Vp(e,n){e.flags&=65011714;var a=e.alternate;return a===null?(e.childLanes=0,e.lanes=n,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=a.childLanes,e.lanes=a.lanes,e.child=a.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=a.memoizedProps,e.memoizedState=a.memoizedState,e.updateQueue=a.updateQueue,e.type=a.type,n=a.dependencies,e.dependencies=n===null?null:{lanes:n.lanes,firstContext:n.firstContext}),e}function yl(e,n,a,o,c,h){var x=0;if(o=e,typeof e=="function")Ac(e)&&(x=1);else if(typeof e=="string")x=VS(e,a,Rt.current)?26:e==="html"||e==="head"||e==="body"?27:5;else t:switch(e){case P:return e=ni(31,a,n,c),e.elementType=P,e.lanes=h,e;case w:return Er(a.children,c,h,n);case E:x=8,c|=24;break;case S:return e=ni(12,a,n,c|2),e.elementType=S,e.lanes=h,e;case N:return e=ni(13,a,n,c),e.elementType=N,e.lanes=h,e;case D:return e=ni(19,a,n,c),e.elementType=D,e.lanes=h,e;default:if(typeof e=="object"&&e!==null)switch(e.$$typeof){case z:x=10;break t;case F:x=9;break t;case C:x=11;break t;case O:x=14;break t;case b:x=16,o=null;break t}x=29,a=Error(r(130,e===null?"null":typeof e,"")),o=null}return n=ni(x,a,n,c),n.elementType=e,n.type=o,n.lanes=h,n}function Er(e,n,a,o){return e=ni(7,e,o,n),e.lanes=a,e}function Rc(e,n,a){return e=ni(6,e,null,n),e.lanes=a,e}function kp(e){var n=ni(18,null,null,0);return n.stateNode=e,n}function Cc(e,n,a){return n=ni(4,e.children!==null?e.children:[],e.key,n),n.lanes=a,n.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},n}var Xp=new WeakMap;function pi(e,n){if(typeof e=="object"&&e!==null){var a=Xp.get(e);return a!==void 0?a:(n={value:e,source:n,stack:nn(n)},Xp.set(e,n),n)}return{value:e,source:n,stack:nn(n)}}var is=[],as=0,Ml=null,fo=0,mi=[],gi=0,Oa=null,zi=1,Bi="";function ia(e,n){is[as++]=fo,is[as++]=Ml,Ml=e,fo=n}function Wp(e,n,a){mi[gi++]=zi,mi[gi++]=Bi,mi[gi++]=Oa,Oa=e;var o=zi;e=Bi;var c=32-Ft(o)-1;o&=~(1<<c),a+=1;var h=32-Ft(n)+c;if(30<h){var x=c-c%5;h=(o&(1<<x)-1).toString(32),o>>=x,c-=x,zi=1<<32-Ft(n)+c|a<<c|o,Bi=h+e}else zi=1<<h|a<<c|o,Bi=e}function wc(e){e.return!==null&&(ia(e,1),Wp(e,1,0))}function Dc(e){for(;e===Ml;)Ml=is[--as],is[as]=null,fo=is[--as],is[as]=null;for(;e===Oa;)Oa=mi[--gi],mi[gi]=null,Bi=mi[--gi],mi[gi]=null,zi=mi[--gi],mi[gi]=null}function qp(e,n){mi[gi++]=zi,mi[gi++]=Bi,mi[gi++]=Oa,zi=n.id,Bi=n.overflow,Oa=e}var An=null,Ye=null,Me=!1,Pa=null,_i=!1,Uc=Error(r(519));function Ia(e){var n=Error(r(418,1<arguments.length&&arguments[1]!==void 0&&arguments[1]?"text":"HTML",""));throw ho(pi(n,e)),Uc}function Yp(e){var n=e.stateNode,a=e.type,o=e.memoizedProps;switch(n[fn]=e,n[Tn]=o,a){case"dialog":pe("cancel",n),pe("close",n);break;case"iframe":case"object":case"embed":pe("load",n);break;case"video":case"audio":for(a=0;a<Po.length;a++)pe(Po[a],n);break;case"source":pe("error",n);break;case"img":case"image":case"link":pe("error",n),pe("load",n);break;case"details":pe("toggle",n);break;case"input":pe("invalid",n),Ln(n,o.value,o.defaultValue,o.checked,o.defaultChecked,o.type,o.name,!0);break;case"select":pe("invalid",n);break;case"textarea":pe("invalid",n),bi(n,o.value,o.defaultValue,o.children)}a=o.children,typeof a!="string"&&typeof a!="number"&&typeof a!="bigint"||n.textContent===""+a||o.suppressHydrationWarning===!0||c_(n.textContent,a)?(o.popover!=null&&(pe("beforetoggle",n),pe("toggle",n)),o.onScroll!=null&&pe("scroll",n),o.onScrollEnd!=null&&pe("scrollend",n),o.onClick!=null&&(n.onclick=ta),n=!0):n=!1,n||Ia(e,!0)}function Zp(e){for(An=e.return;An;)switch(An.tag){case 5:case 31:case 13:_i=!1;return;case 27:case 3:_i=!0;return;default:An=An.return}}function rs(e){if(e!==An)return!1;if(!Me)return Zp(e),Me=!0,!1;var n=e.tag,a;if((a=n!==3&&n!==27)&&((a=n===5)&&(a=e.type,a=!(a!=="form"&&a!=="button")||Qf(e.type,e.memoizedProps)),a=!a),a&&Ye&&Ia(e),Zp(e),n===13){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(r(317));Ye=x_(e)}else if(n===31){if(e=e.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(r(317));Ye=x_(e)}else n===27?(n=Ye,Qa(e.type)?(e=eh,eh=null,Ye=e):Ye=n):Ye=An?xi(e.stateNode.nextSibling):null;return!0}function br(){Ye=An=null,Me=!1}function Lc(){var e=Pa;return e!==null&&(qn===null?qn=e:qn.push.apply(qn,e),Pa=null),e}function ho(e){Pa===null?Pa=[e]:Pa.push(e)}var Nc=L(null),Tr=null,aa=null;function Fa(e,n,a){Mt(Nc,n._currentValue),n._currentValue=a}function ra(e){e._currentValue=Nc.current,K(Nc)}function Oc(e,n,a){for(;e!==null;){var o=e.alternate;if((e.childLanes&n)!==n?(e.childLanes|=n,o!==null&&(o.childLanes|=n)):o!==null&&(o.childLanes&n)!==n&&(o.childLanes|=n),e===a)break;e=e.return}}function Pc(e,n,a,o){var c=e.child;for(c!==null&&(c.return=e);c!==null;){var h=c.dependencies;if(h!==null){var x=c.child;h=h.firstContext;t:for(;h!==null;){var R=h;h=c;for(var B=0;B<n.length;B++)if(R.context===n[B]){h.lanes|=a,R=h.alternate,R!==null&&(R.lanes|=a),Oc(h.return,a,e),o||(x=null);break t}h=R.next}}else if(c.tag===18){if(x=c.return,x===null)throw Error(r(341));x.lanes|=a,h=x.alternate,h!==null&&(h.lanes|=a),Oc(x,a,e),x=null}else x=c.child;if(x!==null)x.return=c;else for(x=c;x!==null;){if(x===e){x=null;break}if(c=x.sibling,c!==null){c.return=x.return,x=c;break}x=x.return}c=x}}function ss(e,n,a,o){e=null;for(var c=n,h=!1;c!==null;){if(!h){if((c.flags&524288)!==0)h=!0;else if((c.flags&262144)!==0)break}if(c.tag===10){var x=c.alternate;if(x===null)throw Error(r(387));if(x=x.memoizedProps,x!==null){var R=c.type;ei(c.pendingProps.value,x.value)||(e!==null?e.push(R):e=[R])}}else if(c===xt.current){if(x=c.alternate,x===null)throw Error(r(387));x.memoizedState.memoizedState!==c.memoizedState.memoizedState&&(e!==null?e.push(Ho):e=[Ho])}c=c.return}e!==null&&Pc(n,e,a,o),n.flags|=262144}function El(e){for(e=e.firstContext;e!==null;){if(!ei(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function Ar(e){Tr=e,aa=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function Rn(e){return Kp(Tr,e)}function bl(e,n){return Tr===null&&Ar(e),Kp(e,n)}function Kp(e,n){var a=n._currentValue;if(n={context:n,memoizedValue:a,next:null},aa===null){if(e===null)throw Error(r(308));aa=n,e.dependencies={lanes:0,firstContext:n},e.flags|=524288}else aa=aa.next=n;return a}var zx=typeof AbortController<"u"?AbortController:function(){var e=[],n=this.signal={aborted:!1,addEventListener:function(a,o){e.push(o)}};this.abort=function(){n.aborted=!0,e.forEach(function(a){return a()})}},Bx=s.unstable_scheduleCallback,Hx=s.unstable_NormalPriority,dn={$$typeof:z,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function Ic(){return{controller:new zx,data:new Map,refCount:0}}function po(e){e.refCount--,e.refCount===0&&Bx(Hx,function(){e.controller.abort()})}var mo=null,Fc=0,os=0,ls=null;function Gx(e,n){if(mo===null){var a=mo=[];Fc=0,os=Gf(),ls={status:"pending",value:void 0,then:function(o){a.push(o)}}}return Fc++,n.then(Qp,Qp),n}function Qp(){if(--Fc===0&&mo!==null){ls!==null&&(ls.status="fulfilled");var e=mo;mo=null,os=0,ls=null;for(var n=0;n<e.length;n++)(0,e[n])()}}function Vx(e,n){var a=[],o={status:"pending",value:null,reason:null,then:function(c){a.push(c)}};return e.then(function(){o.status="fulfilled",o.value=n;for(var c=0;c<a.length;c++)(0,a[c])(n)},function(c){for(o.status="rejected",o.reason=c,c=0;c<a.length;c++)(0,a[c])(void 0)}),o}var Jp=I.S;I.S=function(e,n){Og=ze(),typeof n=="object"&&n!==null&&typeof n.then=="function"&&Gx(e,n),Jp!==null&&Jp(e,n)};var Rr=L(null);function zc(){var e=Rr.current;return e!==null?e:Xe.pooledCache}function Tl(e,n){n===null?Mt(Rr,Rr.current):Mt(Rr,n.pool)}function jp(){var e=zc();return e===null?null:{parent:dn._currentValue,pool:e}}var us=Error(r(460)),Bc=Error(r(474)),Al=Error(r(542)),Rl={then:function(){}};function $p(e){return e=e.status,e==="fulfilled"||e==="rejected"}function tm(e,n,a){switch(a=e[a],a===void 0?e.push(n):a!==n&&(n.then(ta,ta),n=a),n.status){case"fulfilled":return n.value;case"rejected":throw e=n.reason,nm(e),e;default:if(typeof n.status=="string")n.then(ta,ta);else{if(e=Xe,e!==null&&100<e.shellSuspendCounter)throw Error(r(482));e=n,e.status="pending",e.then(function(o){if(n.status==="pending"){var c=n;c.status="fulfilled",c.value=o}},function(o){if(n.status==="pending"){var c=n;c.status="rejected",c.reason=o}})}switch(n.status){case"fulfilled":return n.value;case"rejected":throw e=n.reason,nm(e),e}throw wr=n,us}}function Cr(e){try{var n=e._init;return n(e._payload)}catch(a){throw a!==null&&typeof a=="object"&&typeof a.then=="function"?(wr=a,us):a}}var wr=null;function em(){if(wr===null)throw Error(r(459));var e=wr;return wr=null,e}function nm(e){if(e===us||e===Al)throw Error(r(483))}var cs=null,go=0;function Cl(e){var n=go;return go+=1,cs===null&&(cs=[]),tm(cs,e,n)}function _o(e,n){n=n.props.ref,e.ref=n!==void 0?n:null}function wl(e,n){throw n.$$typeof===_?Error(r(525)):(e=Object.prototype.toString.call(n),Error(r(31,e==="[object Object]"?"object with keys {"+Object.keys(n).join(", ")+"}":e)))}function im(e){function n(Y,V){if(e){var tt=Y.deletions;tt===null?(Y.deletions=[V],Y.flags|=16):tt.push(V)}}function a(Y,V){if(!e)return null;for(;V!==null;)n(Y,V),V=V.sibling;return null}function o(Y){for(var V=new Map;Y!==null;)Y.key!==null?V.set(Y.key,Y):V.set(Y.index,Y),Y=Y.sibling;return V}function c(Y,V){return Y=na(Y,V),Y.index=0,Y.sibling=null,Y}function h(Y,V,tt){return Y.index=tt,e?(tt=Y.alternate,tt!==null?(tt=tt.index,tt<V?(Y.flags|=67108866,V):tt):(Y.flags|=67108866,V)):(Y.flags|=1048576,V)}function x(Y){return e&&Y.alternate===null&&(Y.flags|=67108866),Y}function R(Y,V,tt,_t){return V===null||V.tag!==6?(V=Rc(tt,Y.mode,_t),V.return=Y,V):(V=c(V,tt),V.return=Y,V)}function B(Y,V,tt,_t){var jt=tt.type;return jt===w?dt(Y,V,tt.props.children,_t,tt.key):V!==null&&(V.elementType===jt||typeof jt=="object"&&jt!==null&&jt.$$typeof===b&&Cr(jt)===V.type)?(V=c(V,tt.props),_o(V,tt),V.return=Y,V):(V=yl(tt.type,tt.key,tt.props,null,Y.mode,_t),_o(V,tt),V.return=Y,V)}function et(Y,V,tt,_t){return V===null||V.tag!==4||V.stateNode.containerInfo!==tt.containerInfo||V.stateNode.implementation!==tt.implementation?(V=Cc(tt,Y.mode,_t),V.return=Y,V):(V=c(V,tt.children||[]),V.return=Y,V)}function dt(Y,V,tt,_t,jt){return V===null||V.tag!==7?(V=Er(tt,Y.mode,_t,jt),V.return=Y,V):(V=c(V,tt),V.return=Y,V)}function vt(Y,V,tt){if(typeof V=="string"&&V!==""||typeof V=="number"||typeof V=="bigint")return V=Rc(""+V,Y.mode,tt),V.return=Y,V;if(typeof V=="object"&&V!==null){switch(V.$$typeof){case M:return tt=yl(V.type,V.key,V.props,null,Y.mode,tt),_o(tt,V),tt.return=Y,tt;case T:return V=Cc(V,Y.mode,tt),V.return=Y,V;case b:return V=Cr(V),vt(Y,V,tt)}if(J(V)||Z(V))return V=Er(V,Y.mode,tt,null),V.return=Y,V;if(typeof V.then=="function")return vt(Y,Cl(V),tt);if(V.$$typeof===z)return vt(Y,bl(Y,V),tt);wl(Y,V)}return null}function ot(Y,V,tt,_t){var jt=V!==null?V.key:null;if(typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint")return jt!==null?null:R(Y,V,""+tt,_t);if(typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case M:return tt.key===jt?B(Y,V,tt,_t):null;case T:return tt.key===jt?et(Y,V,tt,_t):null;case b:return tt=Cr(tt),ot(Y,V,tt,_t)}if(J(tt)||Z(tt))return jt!==null?null:dt(Y,V,tt,_t,null);if(typeof tt.then=="function")return ot(Y,V,Cl(tt),_t);if(tt.$$typeof===z)return ot(Y,V,bl(Y,tt),_t);wl(Y,tt)}return null}function lt(Y,V,tt,_t,jt){if(typeof _t=="string"&&_t!==""||typeof _t=="number"||typeof _t=="bigint")return Y=Y.get(tt)||null,R(V,Y,""+_t,jt);if(typeof _t=="object"&&_t!==null){switch(_t.$$typeof){case M:return Y=Y.get(_t.key===null?tt:_t.key)||null,B(V,Y,_t,jt);case T:return Y=Y.get(_t.key===null?tt:_t.key)||null,et(V,Y,_t,jt);case b:return _t=Cr(_t),lt(Y,V,tt,_t,jt)}if(J(_t)||Z(_t))return Y=Y.get(tt)||null,dt(V,Y,_t,jt,null);if(typeof _t.then=="function")return lt(Y,V,tt,Cl(_t),jt);if(_t.$$typeof===z)return lt(Y,V,tt,bl(V,_t),jt);wl(V,_t)}return null}function Xt(Y,V,tt,_t){for(var jt=null,Ae=null,qt=V,le=V=0,_e=null;qt!==null&&le<tt.length;le++){qt.index>le?(_e=qt,qt=null):_e=qt.sibling;var Re=ot(Y,qt,tt[le],_t);if(Re===null){qt===null&&(qt=_e);break}e&&qt&&Re.alternate===null&&n(Y,qt),V=h(Re,V,le),Ae===null?jt=Re:Ae.sibling=Re,Ae=Re,qt=_e}if(le===tt.length)return a(Y,qt),Me&&ia(Y,le),jt;if(qt===null){for(;le<tt.length;le++)qt=vt(Y,tt[le],_t),qt!==null&&(V=h(qt,V,le),Ae===null?jt=qt:Ae.sibling=qt,Ae=qt);return Me&&ia(Y,le),jt}for(qt=o(qt);le<tt.length;le++)_e=lt(qt,Y,le,tt[le],_t),_e!==null&&(e&&_e.alternate!==null&&qt.delete(_e.key===null?le:_e.key),V=h(_e,V,le),Ae===null?jt=_e:Ae.sibling=_e,Ae=_e);return e&&qt.forEach(function(er){return n(Y,er)}),Me&&ia(Y,le),jt}function $t(Y,V,tt,_t){if(tt==null)throw Error(r(151));for(var jt=null,Ae=null,qt=V,le=V=0,_e=null,Re=tt.next();qt!==null&&!Re.done;le++,Re=tt.next()){qt.index>le?(_e=qt,qt=null):_e=qt.sibling;var er=ot(Y,qt,Re.value,_t);if(er===null){qt===null&&(qt=_e);break}e&&qt&&er.alternate===null&&n(Y,qt),V=h(er,V,le),Ae===null?jt=er:Ae.sibling=er,Ae=er,qt=_e}if(Re.done)return a(Y,qt),Me&&ia(Y,le),jt;if(qt===null){for(;!Re.done;le++,Re=tt.next())Re=vt(Y,Re.value,_t),Re!==null&&(V=h(Re,V,le),Ae===null?jt=Re:Ae.sibling=Re,Ae=Re);return Me&&ia(Y,le),jt}for(qt=o(qt);!Re.done;le++,Re=tt.next())Re=lt(qt,Y,le,Re.value,_t),Re!==null&&(e&&Re.alternate!==null&&qt.delete(Re.key===null?le:Re.key),V=h(Re,V,le),Ae===null?jt=Re:Ae.sibling=Re,Ae=Re);return e&&qt.forEach(function($S){return n(Y,$S)}),Me&&ia(Y,le),jt}function Ge(Y,V,tt,_t){if(typeof tt=="object"&&tt!==null&&tt.type===w&&tt.key===null&&(tt=tt.props.children),typeof tt=="object"&&tt!==null){switch(tt.$$typeof){case M:t:{for(var jt=tt.key;V!==null;){if(V.key===jt){if(jt=tt.type,jt===w){if(V.tag===7){a(Y,V.sibling),_t=c(V,tt.props.children),_t.return=Y,Y=_t;break t}}else if(V.elementType===jt||typeof jt=="object"&&jt!==null&&jt.$$typeof===b&&Cr(jt)===V.type){a(Y,V.sibling),_t=c(V,tt.props),_o(_t,tt),_t.return=Y,Y=_t;break t}a(Y,V);break}else n(Y,V);V=V.sibling}tt.type===w?(_t=Er(tt.props.children,Y.mode,_t,tt.key),_t.return=Y,Y=_t):(_t=yl(tt.type,tt.key,tt.props,null,Y.mode,_t),_o(_t,tt),_t.return=Y,Y=_t)}return x(Y);case T:t:{for(jt=tt.key;V!==null;){if(V.key===jt)if(V.tag===4&&V.stateNode.containerInfo===tt.containerInfo&&V.stateNode.implementation===tt.implementation){a(Y,V.sibling),_t=c(V,tt.children||[]),_t.return=Y,Y=_t;break t}else{a(Y,V);break}else n(Y,V);V=V.sibling}_t=Cc(tt,Y.mode,_t),_t.return=Y,Y=_t}return x(Y);case b:return tt=Cr(tt),Ge(Y,V,tt,_t)}if(J(tt))return Xt(Y,V,tt,_t);if(Z(tt)){if(jt=Z(tt),typeof jt!="function")throw Error(r(150));return tt=jt.call(tt),$t(Y,V,tt,_t)}if(typeof tt.then=="function")return Ge(Y,V,Cl(tt),_t);if(tt.$$typeof===z)return Ge(Y,V,bl(Y,tt),_t);wl(Y,tt)}return typeof tt=="string"&&tt!==""||typeof tt=="number"||typeof tt=="bigint"?(tt=""+tt,V!==null&&V.tag===6?(a(Y,V.sibling),_t=c(V,tt),_t.return=Y,Y=_t):(a(Y,V),_t=Rc(tt,Y.mode,_t),_t.return=Y,Y=_t),x(Y)):a(Y,V)}return function(Y,V,tt,_t){try{go=0;var jt=Ge(Y,V,tt,_t);return cs=null,jt}catch(qt){if(qt===us||qt===Al)throw qt;var Ae=ni(29,qt,null,Y.mode);return Ae.lanes=_t,Ae.return=Y,Ae}}}var Dr=im(!0),am=im(!1),za=!1;function Hc(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function Gc(e,n){e=e.updateQueue,n.updateQueue===e&&(n.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function Ba(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function Ha(e,n,a){var o=e.updateQueue;if(o===null)return null;if(o=o.shared,(we&2)!==0){var c=o.pending;return c===null?n.next=n:(n.next=c.next,c.next=n),o.pending=n,n=Sl(e),Gp(e,null,a),n}return xl(e,o,n,a),Sl(e)}function vo(e,n,a){if(n=n.updateQueue,n!==null&&(n=n.shared,(a&4194048)!==0)){var o=n.lanes;o&=e.pendingLanes,a|=o,n.lanes=a,Jn(e,a)}}function Vc(e,n){var a=e.updateQueue,o=e.alternate;if(o!==null&&(o=o.updateQueue,a===o)){var c=null,h=null;if(a=a.firstBaseUpdate,a!==null){do{var x={lane:a.lane,tag:a.tag,payload:a.payload,callback:null,next:null};h===null?c=h=x:h=h.next=x,a=a.next}while(a!==null);h===null?c=h=n:h=h.next=n}else c=h=n;a={baseState:o.baseState,firstBaseUpdate:c,lastBaseUpdate:h,shared:o.shared,callbacks:o.callbacks},e.updateQueue=a;return}e=a.lastBaseUpdate,e===null?a.firstBaseUpdate=n:e.next=n,a.lastBaseUpdate=n}var kc=!1;function xo(){if(kc){var e=ls;if(e!==null)throw e}}function So(e,n,a,o){kc=!1;var c=e.updateQueue;za=!1;var h=c.firstBaseUpdate,x=c.lastBaseUpdate,R=c.shared.pending;if(R!==null){c.shared.pending=null;var B=R,et=B.next;B.next=null,x===null?h=et:x.next=et,x=B;var dt=e.alternate;dt!==null&&(dt=dt.updateQueue,R=dt.lastBaseUpdate,R!==x&&(R===null?dt.firstBaseUpdate=et:R.next=et,dt.lastBaseUpdate=B))}if(h!==null){var vt=c.baseState;x=0,dt=et=B=null,R=h;do{var ot=R.lane&-536870913,lt=ot!==R.lane;if(lt?(ge&ot)===ot:(o&ot)===ot){ot!==0&&ot===os&&(kc=!0),dt!==null&&(dt=dt.next={lane:0,tag:R.tag,payload:R.payload,callback:null,next:null});t:{var Xt=e,$t=R;ot=n;var Ge=a;switch($t.tag){case 1:if(Xt=$t.payload,typeof Xt=="function"){vt=Xt.call(Ge,vt,ot);break t}vt=Xt;break t;case 3:Xt.flags=Xt.flags&-65537|128;case 0:if(Xt=$t.payload,ot=typeof Xt=="function"?Xt.call(Ge,vt,ot):Xt,ot==null)break t;vt=v({},vt,ot);break t;case 2:za=!0}}ot=R.callback,ot!==null&&(e.flags|=64,lt&&(e.flags|=8192),lt=c.callbacks,lt===null?c.callbacks=[ot]:lt.push(ot))}else lt={lane:ot,tag:R.tag,payload:R.payload,callback:R.callback,next:null},dt===null?(et=dt=lt,B=vt):dt=dt.next=lt,x|=ot;if(R=R.next,R===null){if(R=c.shared.pending,R===null)break;lt=R,R=lt.next,lt.next=null,c.lastBaseUpdate=lt,c.shared.pending=null}}while(!0);dt===null&&(B=vt),c.baseState=B,c.firstBaseUpdate=et,c.lastBaseUpdate=dt,h===null&&(c.shared.lanes=0),Wa|=x,e.lanes=x,e.memoizedState=vt}}function rm(e,n){if(typeof e!="function")throw Error(r(191,e));e.call(n)}function sm(e,n){var a=e.callbacks;if(a!==null)for(e.callbacks=null,e=0;e<a.length;e++)rm(a[e],n)}var fs=L(null),Dl=L(0);function om(e,n){e=pa,Mt(Dl,e),Mt(fs,n),pa=e|n.baseLanes}function Xc(){Mt(Dl,pa),Mt(fs,fs.current)}function Wc(){pa=Dl.current,K(fs),K(Dl)}var ii=L(null),vi=null;function Ga(e){var n=e.alternate;Mt(un,un.current&1),Mt(ii,e),vi===null&&(n===null||fs.current!==null||n.memoizedState!==null)&&(vi=e)}function qc(e){Mt(un,un.current),Mt(ii,e),vi===null&&(vi=e)}function lm(e){e.tag===22?(Mt(un,un.current),Mt(ii,e),vi===null&&(vi=e)):Va()}function Va(){Mt(un,un.current),Mt(ii,ii.current)}function ai(e){K(ii),vi===e&&(vi=null),K(un)}var un=L(0);function Ul(e){for(var n=e;n!==null;){if(n.tag===13){var a=n.memoizedState;if(a!==null&&(a=a.dehydrated,a===null||$f(a)||th(a)))return n}else if(n.tag===19&&(n.memoizedProps.revealOrder==="forwards"||n.memoizedProps.revealOrder==="backwards"||n.memoizedProps.revealOrder==="unstable_legacy-backwards"||n.memoizedProps.revealOrder==="together")){if((n.flags&128)!==0)return n}else if(n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return null;n=n.return}n.sibling.return=n.return,n=n.sibling}return null}var sa=0,oe=null,Be=null,pn=null,Ll=!1,hs=!1,Ur=!1,Nl=0,yo=0,ds=null,kx=0;function sn(){throw Error(r(321))}function Yc(e,n){if(n===null)return!1;for(var a=0;a<n.length&&a<e.length;a++)if(!ei(e[a],n[a]))return!1;return!0}function Zc(e,n,a,o,c,h){return sa=h,oe=n,n.memoizedState=null,n.updateQueue=null,n.lanes=0,I.H=e===null||e.memoizedState===null?Wm:cf,Ur=!1,h=a(o,c),Ur=!1,hs&&(h=cm(n,a,o,c)),um(e),h}function um(e){I.H=bo;var n=Be!==null&&Be.next!==null;if(sa=0,pn=Be=oe=null,Ll=!1,yo=0,ds=null,n)throw Error(r(300));e===null||mn||(e=e.dependencies,e!==null&&El(e)&&(mn=!0))}function cm(e,n,a,o){oe=e;var c=0;do{if(hs&&(ds=null),yo=0,hs=!1,25<=c)throw Error(r(301));if(c+=1,pn=Be=null,e.updateQueue!=null){var h=e.updateQueue;h.lastEffect=null,h.events=null,h.stores=null,h.memoCache!=null&&(h.memoCache.index=0)}I.H=qm,h=n(a,o)}while(hs);return h}function Xx(){var e=I.H,n=e.useState()[0];return n=typeof n.then=="function"?Mo(n):n,e=e.useState()[0],(Be!==null?Be.memoizedState:null)!==e&&(oe.flags|=1024),n}function Kc(){var e=Nl!==0;return Nl=0,e}function Qc(e,n,a){n.updateQueue=e.updateQueue,n.flags&=-2053,e.lanes&=~a}function Jc(e){if(Ll){for(e=e.memoizedState;e!==null;){var n=e.queue;n!==null&&(n.pending=null),e=e.next}Ll=!1}sa=0,pn=Be=oe=null,hs=!1,yo=Nl=0,ds=null}function Fn(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return pn===null?oe.memoizedState=pn=e:pn=pn.next=e,pn}function cn(){if(Be===null){var e=oe.alternate;e=e!==null?e.memoizedState:null}else e=Be.next;var n=pn===null?oe.memoizedState:pn.next;if(n!==null)pn=n,Be=e;else{if(e===null)throw oe.alternate===null?Error(r(467)):Error(r(310));Be=e,e={memoizedState:Be.memoizedState,baseState:Be.baseState,baseQueue:Be.baseQueue,queue:Be.queue,next:null},pn===null?oe.memoizedState=pn=e:pn=pn.next=e}return pn}function Ol(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function Mo(e){var n=yo;return yo+=1,ds===null&&(ds=[]),e=tm(ds,e,n),n=oe,(pn===null?n.memoizedState:pn.next)===null&&(n=n.alternate,I.H=n===null||n.memoizedState===null?Wm:cf),e}function Pl(e){if(e!==null&&typeof e=="object"){if(typeof e.then=="function")return Mo(e);if(e.$$typeof===z)return Rn(e)}throw Error(r(438,String(e)))}function jc(e){var n=null,a=oe.updateQueue;if(a!==null&&(n=a.memoCache),n==null){var o=oe.alternate;o!==null&&(o=o.updateQueue,o!==null&&(o=o.memoCache,o!=null&&(n={data:o.data.map(function(c){return c.slice()}),index:0})))}if(n==null&&(n={data:[],index:0}),a===null&&(a=Ol(),oe.updateQueue=a),a.memoCache=n,a=n.data[n.index],a===void 0)for(a=n.data[n.index]=Array(e),o=0;o<e;o++)a[o]=q;return n.index++,a}function oa(e,n){return typeof n=="function"?n(e):n}function Il(e){var n=cn();return $c(n,Be,e)}function $c(e,n,a){var o=e.queue;if(o===null)throw Error(r(311));o.lastRenderedReducer=a;var c=e.baseQueue,h=o.pending;if(h!==null){if(c!==null){var x=c.next;c.next=h.next,h.next=x}n.baseQueue=c=h,o.pending=null}if(h=e.baseState,c===null)e.memoizedState=h;else{n=c.next;var R=x=null,B=null,et=n,dt=!1;do{var vt=et.lane&-536870913;if(vt!==et.lane?(ge&vt)===vt:(sa&vt)===vt){var ot=et.revertLane;if(ot===0)B!==null&&(B=B.next={lane:0,revertLane:0,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null}),vt===os&&(dt=!0);else if((sa&ot)===ot){et=et.next,ot===os&&(dt=!0);continue}else vt={lane:0,revertLane:et.revertLane,gesture:null,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},B===null?(R=B=vt,x=h):B=B.next=vt,oe.lanes|=ot,Wa|=ot;vt=et.action,Ur&&a(h,vt),h=et.hasEagerState?et.eagerState:a(h,vt)}else ot={lane:vt,revertLane:et.revertLane,gesture:et.gesture,action:et.action,hasEagerState:et.hasEagerState,eagerState:et.eagerState,next:null},B===null?(R=B=ot,x=h):B=B.next=ot,oe.lanes|=vt,Wa|=vt;et=et.next}while(et!==null&&et!==n);if(B===null?x=h:B.next=R,!ei(h,e.memoizedState)&&(mn=!0,dt&&(a=ls,a!==null)))throw a;e.memoizedState=h,e.baseState=x,e.baseQueue=B,o.lastRenderedState=h}return c===null&&(o.lanes=0),[e.memoizedState,o.dispatch]}function tf(e){var n=cn(),a=n.queue;if(a===null)throw Error(r(311));a.lastRenderedReducer=e;var o=a.dispatch,c=a.pending,h=n.memoizedState;if(c!==null){a.pending=null;var x=c=c.next;do h=e(h,x.action),x=x.next;while(x!==c);ei(h,n.memoizedState)||(mn=!0),n.memoizedState=h,n.baseQueue===null&&(n.baseState=h),a.lastRenderedState=h}return[h,o]}function fm(e,n,a){var o=oe,c=cn(),h=Me;if(h){if(a===void 0)throw Error(r(407));a=a()}else a=n();var x=!ei((Be||c).memoizedState,a);if(x&&(c.memoizedState=a,mn=!0),c=c.queue,af(pm.bind(null,o,c,e),[e]),c.getSnapshot!==n||x||pn!==null&&pn.memoizedState.tag&1){if(o.flags|=2048,ps(9,{destroy:void 0},dm.bind(null,o,c,a,n),null),Xe===null)throw Error(r(349));h||(sa&127)!==0||hm(o,n,a)}return a}function hm(e,n,a){e.flags|=16384,e={getSnapshot:n,value:a},n=oe.updateQueue,n===null?(n=Ol(),oe.updateQueue=n,n.stores=[e]):(a=n.stores,a===null?n.stores=[e]:a.push(e))}function dm(e,n,a,o){n.value=a,n.getSnapshot=o,mm(n)&&gm(e)}function pm(e,n,a){return a(function(){mm(n)&&gm(e)})}function mm(e){var n=e.getSnapshot;e=e.value;try{var a=n();return!ei(e,a)}catch{return!0}}function gm(e){var n=Mr(e,2);n!==null&&Yn(n,e,2)}function ef(e){var n=Fn();if(typeof e=="function"){var a=e;if(e=a(),Ur){At(!0);try{a()}finally{At(!1)}}}return n.memoizedState=n.baseState=e,n.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:oa,lastRenderedState:e},n}function _m(e,n,a,o){return e.baseState=a,$c(e,Be,typeof o=="function"?o:oa)}function Wx(e,n,a,o,c){if(Bl(e))throw Error(r(485));if(e=n.action,e!==null){var h={payload:c,action:e,next:null,isTransition:!0,status:"pending",value:null,reason:null,listeners:[],then:function(x){h.listeners.push(x)}};I.T!==null?a(!0):h.isTransition=!1,o(h),a=n.pending,a===null?(h.next=n.pending=h,vm(n,h)):(h.next=a.next,n.pending=a.next=h)}}function vm(e,n){var a=n.action,o=n.payload,c=e.state;if(n.isTransition){var h=I.T,x={};I.T=x;try{var R=a(c,o),B=I.S;B!==null&&B(x,R),xm(e,n,R)}catch(et){nf(e,n,et)}finally{h!==null&&x.types!==null&&(h.types=x.types),I.T=h}}else try{h=a(c,o),xm(e,n,h)}catch(et){nf(e,n,et)}}function xm(e,n,a){a!==null&&typeof a=="object"&&typeof a.then=="function"?a.then(function(o){Sm(e,n,o)},function(o){return nf(e,n,o)}):Sm(e,n,a)}function Sm(e,n,a){n.status="fulfilled",n.value=a,ym(n),e.state=a,n=e.pending,n!==null&&(a=n.next,a===n?e.pending=null:(a=a.next,n.next=a,vm(e,a)))}function nf(e,n,a){var o=e.pending;if(e.pending=null,o!==null){o=o.next;do n.status="rejected",n.reason=a,ym(n),n=n.next;while(n!==o)}e.action=null}function ym(e){e=e.listeners;for(var n=0;n<e.length;n++)(0,e[n])()}function Mm(e,n){return n}function Em(e,n){if(Me){var a=Xe.formState;if(a!==null){t:{var o=oe;if(Me){if(Ye){e:{for(var c=Ye,h=_i;c.nodeType!==8;){if(!h){c=null;break e}if(c=xi(c.nextSibling),c===null){c=null;break e}}h=c.data,c=h==="F!"||h==="F"?c:null}if(c){Ye=xi(c.nextSibling),o=c.data==="F!";break t}}Ia(o)}o=!1}o&&(n=a[0])}}return a=Fn(),a.memoizedState=a.baseState=n,o={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Mm,lastRenderedState:n},a.queue=o,a=Vm.bind(null,oe,o),o.dispatch=a,o=ef(!1),h=uf.bind(null,oe,!1,o.queue),o=Fn(),c={state:n,dispatch:null,action:e,pending:null},o.queue=c,a=Wx.bind(null,oe,c,h,a),c.dispatch=a,o.memoizedState=e,[n,a,!1]}function bm(e){var n=cn();return Tm(n,Be,e)}function Tm(e,n,a){if(n=$c(e,n,Mm)[0],e=Il(oa)[0],typeof n=="object"&&n!==null&&typeof n.then=="function")try{var o=Mo(n)}catch(x){throw x===us?Al:x}else o=n;n=cn();var c=n.queue,h=c.dispatch;return a!==n.memoizedState&&(oe.flags|=2048,ps(9,{destroy:void 0},qx.bind(null,c,a),null)),[o,h,e]}function qx(e,n){e.action=n}function Am(e){var n=cn(),a=Be;if(a!==null)return Tm(n,a,e);cn(),n=n.memoizedState,a=cn();var o=a.queue.dispatch;return a.memoizedState=e,[n,o,!1]}function ps(e,n,a,o){return e={tag:e,create:a,deps:o,inst:n,next:null},n=oe.updateQueue,n===null&&(n=Ol(),oe.updateQueue=n),a=n.lastEffect,a===null?n.lastEffect=e.next=e:(o=a.next,a.next=e,e.next=o,n.lastEffect=e),e}function Rm(){return cn().memoizedState}function Fl(e,n,a,o){var c=Fn();oe.flags|=e,c.memoizedState=ps(1|n,{destroy:void 0},a,o===void 0?null:o)}function zl(e,n,a,o){var c=cn();o=o===void 0?null:o;var h=c.memoizedState.inst;Be!==null&&o!==null&&Yc(o,Be.memoizedState.deps)?c.memoizedState=ps(n,h,a,o):(oe.flags|=e,c.memoizedState=ps(1|n,h,a,o))}function Cm(e,n){Fl(8390656,8,e,n)}function af(e,n){zl(2048,8,e,n)}function Yx(e){oe.flags|=4;var n=oe.updateQueue;if(n===null)n=Ol(),oe.updateQueue=n,n.events=[e];else{var a=n.events;a===null?n.events=[e]:a.push(e)}}function wm(e){var n=cn().memoizedState;return Yx({ref:n,nextImpl:e}),function(){if((we&2)!==0)throw Error(r(440));return n.impl.apply(void 0,arguments)}}function Dm(e,n){return zl(4,2,e,n)}function Um(e,n){return zl(4,4,e,n)}function Lm(e,n){if(typeof n=="function"){e=e();var a=n(e);return function(){typeof a=="function"?a():n(null)}}if(n!=null)return e=e(),n.current=e,function(){n.current=null}}function Nm(e,n,a){a=a!=null?a.concat([e]):null,zl(4,4,Lm.bind(null,n,e),a)}function rf(){}function Om(e,n){var a=cn();n=n===void 0?null:n;var o=a.memoizedState;return n!==null&&Yc(n,o[1])?o[0]:(a.memoizedState=[e,n],e)}function Pm(e,n){var a=cn();n=n===void 0?null:n;var o=a.memoizedState;if(n!==null&&Yc(n,o[1]))return o[0];if(o=e(),Ur){At(!0);try{e()}finally{At(!1)}}return a.memoizedState=[o,n],o}function sf(e,n,a){return a===void 0||(sa&1073741824)!==0&&(ge&261930)===0?e.memoizedState=n:(e.memoizedState=a,e=Ig(),oe.lanes|=e,Wa|=e,a)}function Im(e,n,a,o){return ei(a,n)?a:fs.current!==null?(e=sf(e,a,o),ei(e,n)||(mn=!0),e):(sa&42)===0||(sa&1073741824)!==0&&(ge&261930)===0?(mn=!0,e.memoizedState=a):(e=Ig(),oe.lanes|=e,Wa|=e,n)}function Fm(e,n,a,o,c){var h=H.p;H.p=h!==0&&8>h?h:8;var x=I.T,R={};I.T=R,uf(e,!1,n,a);try{var B=c(),et=I.S;if(et!==null&&et(R,B),B!==null&&typeof B=="object"&&typeof B.then=="function"){var dt=Vx(B,o);Eo(e,n,dt,oi(e))}else Eo(e,n,o,oi(e))}catch(vt){Eo(e,n,{then:function(){},status:"rejected",reason:vt},oi())}finally{H.p=h,x!==null&&R.types!==null&&(x.types=R.types),I.T=x}}function Zx(){}function of(e,n,a,o){if(e.tag!==5)throw Error(r(476));var c=zm(e).queue;Fm(e,c,n,j,a===null?Zx:function(){return Bm(e),a(o)})}function zm(e){var n=e.memoizedState;if(n!==null)return n;n={memoizedState:j,baseState:j,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:oa,lastRenderedState:j},next:null};var a={};return n.next={memoizedState:a,baseState:a,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:oa,lastRenderedState:a},next:null},e.memoizedState=n,e=e.alternate,e!==null&&(e.memoizedState=n),n}function Bm(e){var n=zm(e);n.next===null&&(n=e.alternate.memoizedState),Eo(e,n.next.queue,{},oi())}function lf(){return Rn(Ho)}function Hm(){return cn().memoizedState}function Gm(){return cn().memoizedState}function Kx(e){for(var n=e.return;n!==null;){switch(n.tag){case 24:case 3:var a=oi();e=Ba(a);var o=Ha(n,e,a);o!==null&&(Yn(o,n,a),vo(o,n,a)),n={cache:Ic()},e.payload=n;return}n=n.return}}function Qx(e,n,a){var o=oi();a={lane:o,revertLane:0,gesture:null,action:a,hasEagerState:!1,eagerState:null,next:null},Bl(e)?km(n,a):(a=Tc(e,n,a,o),a!==null&&(Yn(a,e,o),Xm(a,n,o)))}function Vm(e,n,a){var o=oi();Eo(e,n,a,o)}function Eo(e,n,a,o){var c={lane:o,revertLane:0,gesture:null,action:a,hasEagerState:!1,eagerState:null,next:null};if(Bl(e))km(n,c);else{var h=e.alternate;if(e.lanes===0&&(h===null||h.lanes===0)&&(h=n.lastRenderedReducer,h!==null))try{var x=n.lastRenderedState,R=h(x,a);if(c.hasEagerState=!0,c.eagerState=R,ei(R,x))return xl(e,n,c,0),Xe===null&&vl(),!1}catch{}if(a=Tc(e,n,c,o),a!==null)return Yn(a,e,o),Xm(a,n,o),!0}return!1}function uf(e,n,a,o){if(o={lane:2,revertLane:Gf(),gesture:null,action:o,hasEagerState:!1,eagerState:null,next:null},Bl(e)){if(n)throw Error(r(479))}else n=Tc(e,a,o,2),n!==null&&Yn(n,e,2)}function Bl(e){var n=e.alternate;return e===oe||n!==null&&n===oe}function km(e,n){hs=Ll=!0;var a=e.pending;a===null?n.next=n:(n.next=a.next,a.next=n),e.pending=n}function Xm(e,n,a){if((a&4194048)!==0){var o=n.lanes;o&=e.pendingLanes,a|=o,n.lanes=a,Jn(e,a)}}var bo={readContext:Rn,use:Pl,useCallback:sn,useContext:sn,useEffect:sn,useImperativeHandle:sn,useLayoutEffect:sn,useInsertionEffect:sn,useMemo:sn,useReducer:sn,useRef:sn,useState:sn,useDebugValue:sn,useDeferredValue:sn,useTransition:sn,useSyncExternalStore:sn,useId:sn,useHostTransitionStatus:sn,useFormState:sn,useActionState:sn,useOptimistic:sn,useMemoCache:sn,useCacheRefresh:sn};bo.useEffectEvent=sn;var Wm={readContext:Rn,use:Pl,useCallback:function(e,n){return Fn().memoizedState=[e,n===void 0?null:n],e},useContext:Rn,useEffect:Cm,useImperativeHandle:function(e,n,a){a=a!=null?a.concat([e]):null,Fl(4194308,4,Lm.bind(null,n,e),a)},useLayoutEffect:function(e,n){return Fl(4194308,4,e,n)},useInsertionEffect:function(e,n){Fl(4,2,e,n)},useMemo:function(e,n){var a=Fn();n=n===void 0?null:n;var o=e();if(Ur){At(!0);try{e()}finally{At(!1)}}return a.memoizedState=[o,n],o},useReducer:function(e,n,a){var o=Fn();if(a!==void 0){var c=a(n);if(Ur){At(!0);try{a(n)}finally{At(!1)}}}else c=n;return o.memoizedState=o.baseState=c,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:c},o.queue=e,e=e.dispatch=Qx.bind(null,oe,e),[o.memoizedState,e]},useRef:function(e){var n=Fn();return e={current:e},n.memoizedState=e},useState:function(e){e=ef(e);var n=e.queue,a=Vm.bind(null,oe,n);return n.dispatch=a,[e.memoizedState,a]},useDebugValue:rf,useDeferredValue:function(e,n){var a=Fn();return sf(a,e,n)},useTransition:function(){var e=ef(!1);return e=Fm.bind(null,oe,e.queue,!0,!1),Fn().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,n,a){var o=oe,c=Fn();if(Me){if(a===void 0)throw Error(r(407));a=a()}else{if(a=n(),Xe===null)throw Error(r(349));(ge&127)!==0||hm(o,n,a)}c.memoizedState=a;var h={value:a,getSnapshot:n};return c.queue=h,Cm(pm.bind(null,o,h,e),[e]),o.flags|=2048,ps(9,{destroy:void 0},dm.bind(null,o,h,a,n),null),a},useId:function(){var e=Fn(),n=Xe.identifierPrefix;if(Me){var a=Bi,o=zi;a=(o&~(1<<32-Ft(o)-1)).toString(32)+a,n="_"+n+"R_"+a,a=Nl++,0<a&&(n+="H"+a.toString(32)),n+="_"}else a=kx++,n="_"+n+"r_"+a.toString(32)+"_";return e.memoizedState=n},useHostTransitionStatus:lf,useFormState:Em,useActionState:Em,useOptimistic:function(e){var n=Fn();n.memoizedState=n.baseState=e;var a={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return n.queue=a,n=uf.bind(null,oe,!0,a),a.dispatch=n,[e,n]},useMemoCache:jc,useCacheRefresh:function(){return Fn().memoizedState=Kx.bind(null,oe)},useEffectEvent:function(e){var n=Fn(),a={impl:e};return n.memoizedState=a,function(){if((we&2)!==0)throw Error(r(440));return a.impl.apply(void 0,arguments)}}},cf={readContext:Rn,use:Pl,useCallback:Om,useContext:Rn,useEffect:af,useImperativeHandle:Nm,useInsertionEffect:Dm,useLayoutEffect:Um,useMemo:Pm,useReducer:Il,useRef:Rm,useState:function(){return Il(oa)},useDebugValue:rf,useDeferredValue:function(e,n){var a=cn();return Im(a,Be.memoizedState,e,n)},useTransition:function(){var e=Il(oa)[0],n=cn().memoizedState;return[typeof e=="boolean"?e:Mo(e),n]},useSyncExternalStore:fm,useId:Hm,useHostTransitionStatus:lf,useFormState:bm,useActionState:bm,useOptimistic:function(e,n){var a=cn();return _m(a,Be,e,n)},useMemoCache:jc,useCacheRefresh:Gm};cf.useEffectEvent=wm;var qm={readContext:Rn,use:Pl,useCallback:Om,useContext:Rn,useEffect:af,useImperativeHandle:Nm,useInsertionEffect:Dm,useLayoutEffect:Um,useMemo:Pm,useReducer:tf,useRef:Rm,useState:function(){return tf(oa)},useDebugValue:rf,useDeferredValue:function(e,n){var a=cn();return Be===null?sf(a,e,n):Im(a,Be.memoizedState,e,n)},useTransition:function(){var e=tf(oa)[0],n=cn().memoizedState;return[typeof e=="boolean"?e:Mo(e),n]},useSyncExternalStore:fm,useId:Hm,useHostTransitionStatus:lf,useFormState:Am,useActionState:Am,useOptimistic:function(e,n){var a=cn();return Be!==null?_m(a,Be,e,n):(a.baseState=e,[e,a.queue.dispatch])},useMemoCache:jc,useCacheRefresh:Gm};qm.useEffectEvent=wm;function ff(e,n,a,o){n=e.memoizedState,a=a(o,n),a=a==null?n:v({},n,a),e.memoizedState=a,e.lanes===0&&(e.updateQueue.baseState=a)}var hf={enqueueSetState:function(e,n,a){e=e._reactInternals;var o=oi(),c=Ba(o);c.payload=n,a!=null&&(c.callback=a),n=Ha(e,c,o),n!==null&&(Yn(n,e,o),vo(n,e,o))},enqueueReplaceState:function(e,n,a){e=e._reactInternals;var o=oi(),c=Ba(o);c.tag=1,c.payload=n,a!=null&&(c.callback=a),n=Ha(e,c,o),n!==null&&(Yn(n,e,o),vo(n,e,o))},enqueueForceUpdate:function(e,n){e=e._reactInternals;var a=oi(),o=Ba(a);o.tag=2,n!=null&&(o.callback=n),n=Ha(e,o,a),n!==null&&(Yn(n,e,a),vo(n,e,a))}};function Ym(e,n,a,o,c,h,x){return e=e.stateNode,typeof e.shouldComponentUpdate=="function"?e.shouldComponentUpdate(o,h,x):n.prototype&&n.prototype.isPureReactComponent?!uo(a,o)||!uo(c,h):!0}function Zm(e,n,a,o){e=n.state,typeof n.componentWillReceiveProps=="function"&&n.componentWillReceiveProps(a,o),typeof n.UNSAFE_componentWillReceiveProps=="function"&&n.UNSAFE_componentWillReceiveProps(a,o),n.state!==e&&hf.enqueueReplaceState(n,n.state,null)}function Lr(e,n){var a=n;if("ref"in n){a={};for(var o in n)o!=="ref"&&(a[o]=n[o])}if(e=e.defaultProps){a===n&&(a=v({},a));for(var c in e)a[c]===void 0&&(a[c]=e[c])}return a}function Km(e){_l(e)}function Qm(e){console.error(e)}function Jm(e){_l(e)}function Hl(e,n){try{var a=e.onUncaughtError;a(n.value,{componentStack:n.stack})}catch(o){setTimeout(function(){throw o})}}function jm(e,n,a){try{var o=e.onCaughtError;o(a.value,{componentStack:a.stack,errorBoundary:n.tag===1?n.stateNode:null})}catch(c){setTimeout(function(){throw c})}}function df(e,n,a){return a=Ba(a),a.tag=3,a.payload={element:null},a.callback=function(){Hl(e,n)},a}function $m(e){return e=Ba(e),e.tag=3,e}function tg(e,n,a,o){var c=a.type.getDerivedStateFromError;if(typeof c=="function"){var h=o.value;e.payload=function(){return c(h)},e.callback=function(){jm(n,a,o)}}var x=a.stateNode;x!==null&&typeof x.componentDidCatch=="function"&&(e.callback=function(){jm(n,a,o),typeof c!="function"&&(qa===null?qa=new Set([this]):qa.add(this));var R=o.stack;this.componentDidCatch(o.value,{componentStack:R!==null?R:""})})}function Jx(e,n,a,o,c){if(a.flags|=32768,o!==null&&typeof o=="object"&&typeof o.then=="function"){if(n=a.alternate,n!==null&&ss(n,a,c,!0),a=ii.current,a!==null){switch(a.tag){case 31:case 13:return vi===null?jl():a.alternate===null&&on===0&&(on=3),a.flags&=-257,a.flags|=65536,a.lanes=c,o===Rl?a.flags|=16384:(n=a.updateQueue,n===null?a.updateQueue=new Set([o]):n.add(o),zf(e,o,c)),!1;case 22:return a.flags|=65536,o===Rl?a.flags|=16384:(n=a.updateQueue,n===null?(n={transitions:null,markerInstances:null,retryQueue:new Set([o])},a.updateQueue=n):(a=n.retryQueue,a===null?n.retryQueue=new Set([o]):a.add(o)),zf(e,o,c)),!1}throw Error(r(435,a.tag))}return zf(e,o,c),jl(),!1}if(Me)return n=ii.current,n!==null?((n.flags&65536)===0&&(n.flags|=256),n.flags|=65536,n.lanes=c,o!==Uc&&(e=Error(r(422),{cause:o}),ho(pi(e,a)))):(o!==Uc&&(n=Error(r(423),{cause:o}),ho(pi(n,a))),e=e.current.alternate,e.flags|=65536,c&=-c,e.lanes|=c,o=pi(o,a),c=df(e.stateNode,o,c),Vc(e,c),on!==4&&(on=2)),!1;var h=Error(r(520),{cause:o});if(h=pi(h,a),Lo===null?Lo=[h]:Lo.push(h),on!==4&&(on=2),n===null)return!0;o=pi(o,a),a=n;do{switch(a.tag){case 3:return a.flags|=65536,e=c&-c,a.lanes|=e,e=df(a.stateNode,o,e),Vc(a,e),!1;case 1:if(n=a.type,h=a.stateNode,(a.flags&128)===0&&(typeof n.getDerivedStateFromError=="function"||h!==null&&typeof h.componentDidCatch=="function"&&(qa===null||!qa.has(h))))return a.flags|=65536,c&=-c,a.lanes|=c,c=$m(c),tg(c,e,a,o),Vc(a,c),!1}a=a.return}while(a!==null);return!1}var pf=Error(r(461)),mn=!1;function Cn(e,n,a,o){n.child=e===null?am(n,null,a,o):Dr(n,e.child,a,o)}function eg(e,n,a,o,c){a=a.render;var h=n.ref;if("ref"in o){var x={};for(var R in o)R!=="ref"&&(x[R]=o[R])}else x=o;return Ar(n),o=Zc(e,n,a,x,h,c),R=Kc(),e!==null&&!mn?(Qc(e,n,c),la(e,n,c)):(Me&&R&&wc(n),n.flags|=1,Cn(e,n,o,c),n.child)}function ng(e,n,a,o,c){if(e===null){var h=a.type;return typeof h=="function"&&!Ac(h)&&h.defaultProps===void 0&&a.compare===null?(n.tag=15,n.type=h,ig(e,n,h,o,c)):(e=yl(a.type,null,o,n,n.mode,c),e.ref=n.ref,e.return=n,n.child=e)}if(h=e.child,!Mf(e,c)){var x=h.memoizedProps;if(a=a.compare,a=a!==null?a:uo,a(x,o)&&e.ref===n.ref)return la(e,n,c)}return n.flags|=1,e=na(h,o),e.ref=n.ref,e.return=n,n.child=e}function ig(e,n,a,o,c){if(e!==null){var h=e.memoizedProps;if(uo(h,o)&&e.ref===n.ref)if(mn=!1,n.pendingProps=o=h,Mf(e,c))(e.flags&131072)!==0&&(mn=!0);else return n.lanes=e.lanes,la(e,n,c)}return mf(e,n,a,o,c)}function ag(e,n,a,o){var c=o.children,h=e!==null?e.memoizedState:null;if(e===null&&n.stateNode===null&&(n.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),o.mode==="hidden"){if((n.flags&128)!==0){if(h=h!==null?h.baseLanes|a:a,e!==null){for(o=n.child=e.child,c=0;o!==null;)c=c|o.lanes|o.childLanes,o=o.sibling;o=c&~h}else o=0,n.child=null;return rg(e,n,h,a,o)}if((a&536870912)!==0)n.memoizedState={baseLanes:0,cachePool:null},e!==null&&Tl(n,h!==null?h.cachePool:null),h!==null?om(n,h):Xc(),lm(n);else return o=n.lanes=536870912,rg(e,n,h!==null?h.baseLanes|a:a,a,o)}else h!==null?(Tl(n,h.cachePool),om(n,h),Va(),n.memoizedState=null):(e!==null&&Tl(n,null),Xc(),Va());return Cn(e,n,c,a),n.child}function To(e,n){return e!==null&&e.tag===22||n.stateNode!==null||(n.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),n.sibling}function rg(e,n,a,o,c){var h=zc();return h=h===null?null:{parent:dn._currentValue,pool:h},n.memoizedState={baseLanes:a,cachePool:h},e!==null&&Tl(n,null),Xc(),lm(n),e!==null&&ss(e,n,o,!0),n.childLanes=c,null}function Gl(e,n){return n=kl({mode:n.mode,children:n.children},e.mode),n.ref=e.ref,e.child=n,n.return=e,n}function sg(e,n,a){return Dr(n,e.child,null,a),e=Gl(n,n.pendingProps),e.flags|=2,ai(n),n.memoizedState=null,e}function jx(e,n,a){var o=n.pendingProps,c=(n.flags&128)!==0;if(n.flags&=-129,e===null){if(Me){if(o.mode==="hidden")return e=Gl(n,o),n.lanes=536870912,To(null,e);if(qc(n),(e=Ye)?(e=v_(e,_i),e=e!==null&&e.data==="&"?e:null,e!==null&&(n.memoizedState={dehydrated:e,treeContext:Oa!==null?{id:zi,overflow:Bi}:null,retryLane:536870912,hydrationErrors:null},a=kp(e),a.return=n,n.child=a,An=n,Ye=null)):e=null,e===null)throw Ia(n);return n.lanes=536870912,null}return Gl(n,o)}var h=e.memoizedState;if(h!==null){var x=h.dehydrated;if(qc(n),c)if(n.flags&256)n.flags&=-257,n=sg(e,n,a);else if(n.memoizedState!==null)n.child=e.child,n.flags|=128,n=null;else throw Error(r(558));else if(mn||ss(e,n,a,!1),c=(a&e.childLanes)!==0,mn||c){if(o=Xe,o!==null&&(x=jn(o,a),x!==0&&x!==h.retryLane))throw h.retryLane=x,Mr(e,x),Yn(o,e,x),pf;jl(),n=sg(e,n,a)}else e=h.treeContext,Ye=xi(x.nextSibling),An=n,Me=!0,Pa=null,_i=!1,e!==null&&qp(n,e),n=Gl(n,o),n.flags|=4096;return n}return e=na(e.child,{mode:o.mode,children:o.children}),e.ref=n.ref,n.child=e,e.return=n,e}function Vl(e,n){var a=n.ref;if(a===null)e!==null&&e.ref!==null&&(n.flags|=4194816);else{if(typeof a!="function"&&typeof a!="object")throw Error(r(284));(e===null||e.ref!==a)&&(n.flags|=4194816)}}function mf(e,n,a,o,c){return Ar(n),a=Zc(e,n,a,o,void 0,c),o=Kc(),e!==null&&!mn?(Qc(e,n,c),la(e,n,c)):(Me&&o&&wc(n),n.flags|=1,Cn(e,n,a,c),n.child)}function og(e,n,a,o,c,h){return Ar(n),n.updateQueue=null,a=cm(n,o,a,c),um(e),o=Kc(),e!==null&&!mn?(Qc(e,n,h),la(e,n,h)):(Me&&o&&wc(n),n.flags|=1,Cn(e,n,a,h),n.child)}function lg(e,n,a,o,c){if(Ar(n),n.stateNode===null){var h=ns,x=a.contextType;typeof x=="object"&&x!==null&&(h=Rn(x)),h=new a(o,h),n.memoizedState=h.state!==null&&h.state!==void 0?h.state:null,h.updater=hf,n.stateNode=h,h._reactInternals=n,h=n.stateNode,h.props=o,h.state=n.memoizedState,h.refs={},Hc(n),x=a.contextType,h.context=typeof x=="object"&&x!==null?Rn(x):ns,h.state=n.memoizedState,x=a.getDerivedStateFromProps,typeof x=="function"&&(ff(n,a,x,o),h.state=n.memoizedState),typeof a.getDerivedStateFromProps=="function"||typeof h.getSnapshotBeforeUpdate=="function"||typeof h.UNSAFE_componentWillMount!="function"&&typeof h.componentWillMount!="function"||(x=h.state,typeof h.componentWillMount=="function"&&h.componentWillMount(),typeof h.UNSAFE_componentWillMount=="function"&&h.UNSAFE_componentWillMount(),x!==h.state&&hf.enqueueReplaceState(h,h.state,null),So(n,o,h,c),xo(),h.state=n.memoizedState),typeof h.componentDidMount=="function"&&(n.flags|=4194308),o=!0}else if(e===null){h=n.stateNode;var R=n.memoizedProps,B=Lr(a,R);h.props=B;var et=h.context,dt=a.contextType;x=ns,typeof dt=="object"&&dt!==null&&(x=Rn(dt));var vt=a.getDerivedStateFromProps;dt=typeof vt=="function"||typeof h.getSnapshotBeforeUpdate=="function",R=n.pendingProps!==R,dt||typeof h.UNSAFE_componentWillReceiveProps!="function"&&typeof h.componentWillReceiveProps!="function"||(R||et!==x)&&Zm(n,h,o,x),za=!1;var ot=n.memoizedState;h.state=ot,So(n,o,h,c),xo(),et=n.memoizedState,R||ot!==et||za?(typeof vt=="function"&&(ff(n,a,vt,o),et=n.memoizedState),(B=za||Ym(n,a,B,o,ot,et,x))?(dt||typeof h.UNSAFE_componentWillMount!="function"&&typeof h.componentWillMount!="function"||(typeof h.componentWillMount=="function"&&h.componentWillMount(),typeof h.UNSAFE_componentWillMount=="function"&&h.UNSAFE_componentWillMount()),typeof h.componentDidMount=="function"&&(n.flags|=4194308)):(typeof h.componentDidMount=="function"&&(n.flags|=4194308),n.memoizedProps=o,n.memoizedState=et),h.props=o,h.state=et,h.context=x,o=B):(typeof h.componentDidMount=="function"&&(n.flags|=4194308),o=!1)}else{h=n.stateNode,Gc(e,n),x=n.memoizedProps,dt=Lr(a,x),h.props=dt,vt=n.pendingProps,ot=h.context,et=a.contextType,B=ns,typeof et=="object"&&et!==null&&(B=Rn(et)),R=a.getDerivedStateFromProps,(et=typeof R=="function"||typeof h.getSnapshotBeforeUpdate=="function")||typeof h.UNSAFE_componentWillReceiveProps!="function"&&typeof h.componentWillReceiveProps!="function"||(x!==vt||ot!==B)&&Zm(n,h,o,B),za=!1,ot=n.memoizedState,h.state=ot,So(n,o,h,c),xo();var lt=n.memoizedState;x!==vt||ot!==lt||za||e!==null&&e.dependencies!==null&&El(e.dependencies)?(typeof R=="function"&&(ff(n,a,R,o),lt=n.memoizedState),(dt=za||Ym(n,a,dt,o,ot,lt,B)||e!==null&&e.dependencies!==null&&El(e.dependencies))?(et||typeof h.UNSAFE_componentWillUpdate!="function"&&typeof h.componentWillUpdate!="function"||(typeof h.componentWillUpdate=="function"&&h.componentWillUpdate(o,lt,B),typeof h.UNSAFE_componentWillUpdate=="function"&&h.UNSAFE_componentWillUpdate(o,lt,B)),typeof h.componentDidUpdate=="function"&&(n.flags|=4),typeof h.getSnapshotBeforeUpdate=="function"&&(n.flags|=1024)):(typeof h.componentDidUpdate!="function"||x===e.memoizedProps&&ot===e.memoizedState||(n.flags|=4),typeof h.getSnapshotBeforeUpdate!="function"||x===e.memoizedProps&&ot===e.memoizedState||(n.flags|=1024),n.memoizedProps=o,n.memoizedState=lt),h.props=o,h.state=lt,h.context=B,o=dt):(typeof h.componentDidUpdate!="function"||x===e.memoizedProps&&ot===e.memoizedState||(n.flags|=4),typeof h.getSnapshotBeforeUpdate!="function"||x===e.memoizedProps&&ot===e.memoizedState||(n.flags|=1024),o=!1)}return h=o,Vl(e,n),o=(n.flags&128)!==0,h||o?(h=n.stateNode,a=o&&typeof a.getDerivedStateFromError!="function"?null:h.render(),n.flags|=1,e!==null&&o?(n.child=Dr(n,e.child,null,c),n.child=Dr(n,null,a,c)):Cn(e,n,a,c),n.memoizedState=h.state,e=n.child):e=la(e,n,c),e}function ug(e,n,a,o){return br(),n.flags|=256,Cn(e,n,a,o),n.child}var gf={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function _f(e){return{baseLanes:e,cachePool:jp()}}function vf(e,n,a){return e=e!==null?e.childLanes&~a:0,n&&(e|=si),e}function cg(e,n,a){var o=n.pendingProps,c=!1,h=(n.flags&128)!==0,x;if((x=h)||(x=e!==null&&e.memoizedState===null?!1:(un.current&2)!==0),x&&(c=!0,n.flags&=-129),x=(n.flags&32)!==0,n.flags&=-33,e===null){if(Me){if(c?Ga(n):Va(),(e=Ye)?(e=v_(e,_i),e=e!==null&&e.data!=="&"?e:null,e!==null&&(n.memoizedState={dehydrated:e,treeContext:Oa!==null?{id:zi,overflow:Bi}:null,retryLane:536870912,hydrationErrors:null},a=kp(e),a.return=n,n.child=a,An=n,Ye=null)):e=null,e===null)throw Ia(n);return th(e)?n.lanes=32:n.lanes=536870912,null}var R=o.children;return o=o.fallback,c?(Va(),c=n.mode,R=kl({mode:"hidden",children:R},c),o=Er(o,c,a,null),R.return=n,o.return=n,R.sibling=o,n.child=R,o=n.child,o.memoizedState=_f(a),o.childLanes=vf(e,x,a),n.memoizedState=gf,To(null,o)):(Ga(n),xf(n,R))}var B=e.memoizedState;if(B!==null&&(R=B.dehydrated,R!==null)){if(h)n.flags&256?(Ga(n),n.flags&=-257,n=Sf(e,n,a)):n.memoizedState!==null?(Va(),n.child=e.child,n.flags|=128,n=null):(Va(),R=o.fallback,c=n.mode,o=kl({mode:"visible",children:o.children},c),R=Er(R,c,a,null),R.flags|=2,o.return=n,R.return=n,o.sibling=R,n.child=o,Dr(n,e.child,null,a),o=n.child,o.memoizedState=_f(a),o.childLanes=vf(e,x,a),n.memoizedState=gf,n=To(null,o));else if(Ga(n),th(R)){if(x=R.nextSibling&&R.nextSibling.dataset,x)var et=x.dgst;x=et,o=Error(r(419)),o.stack="",o.digest=x,ho({value:o,source:null,stack:null}),n=Sf(e,n,a)}else if(mn||ss(e,n,a,!1),x=(a&e.childLanes)!==0,mn||x){if(x=Xe,x!==null&&(o=jn(x,a),o!==0&&o!==B.retryLane))throw B.retryLane=o,Mr(e,o),Yn(x,e,o),pf;$f(R)||jl(),n=Sf(e,n,a)}else $f(R)?(n.flags|=192,n.child=e.child,n=null):(e=B.treeContext,Ye=xi(R.nextSibling),An=n,Me=!0,Pa=null,_i=!1,e!==null&&qp(n,e),n=xf(n,o.children),n.flags|=4096);return n}return c?(Va(),R=o.fallback,c=n.mode,B=e.child,et=B.sibling,o=na(B,{mode:"hidden",children:o.children}),o.subtreeFlags=B.subtreeFlags&65011712,et!==null?R=na(et,R):(R=Er(R,c,a,null),R.flags|=2),R.return=n,o.return=n,o.sibling=R,n.child=o,To(null,o),o=n.child,R=e.child.memoizedState,R===null?R=_f(a):(c=R.cachePool,c!==null?(B=dn._currentValue,c=c.parent!==B?{parent:B,pool:B}:c):c=jp(),R={baseLanes:R.baseLanes|a,cachePool:c}),o.memoizedState=R,o.childLanes=vf(e,x,a),n.memoizedState=gf,To(e.child,o)):(Ga(n),a=e.child,e=a.sibling,a=na(a,{mode:"visible",children:o.children}),a.return=n,a.sibling=null,e!==null&&(x=n.deletions,x===null?(n.deletions=[e],n.flags|=16):x.push(e)),n.child=a,n.memoizedState=null,a)}function xf(e,n){return n=kl({mode:"visible",children:n},e.mode),n.return=e,e.child=n}function kl(e,n){return e=ni(22,e,null,n),e.lanes=0,e}function Sf(e,n,a){return Dr(n,e.child,null,a),e=xf(n,n.pendingProps.children),e.flags|=2,n.memoizedState=null,e}function fg(e,n,a){e.lanes|=n;var o=e.alternate;o!==null&&(o.lanes|=n),Oc(e.return,n,a)}function yf(e,n,a,o,c,h){var x=e.memoizedState;x===null?e.memoizedState={isBackwards:n,rendering:null,renderingStartTime:0,last:o,tail:a,tailMode:c,treeForkCount:h}:(x.isBackwards=n,x.rendering=null,x.renderingStartTime=0,x.last=o,x.tail=a,x.tailMode=c,x.treeForkCount=h)}function hg(e,n,a){var o=n.pendingProps,c=o.revealOrder,h=o.tail;o=o.children;var x=un.current,R=(x&2)!==0;if(R?(x=x&1|2,n.flags|=128):x&=1,Mt(un,x),Cn(e,n,o,a),o=Me?fo:0,!R&&e!==null&&(e.flags&128)!==0)t:for(e=n.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&fg(e,a,n);else if(e.tag===19)fg(e,a,n);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===n)break t;for(;e.sibling===null;){if(e.return===null||e.return===n)break t;e=e.return}e.sibling.return=e.return,e=e.sibling}switch(c){case"forwards":for(a=n.child,c=null;a!==null;)e=a.alternate,e!==null&&Ul(e)===null&&(c=a),a=a.sibling;a=c,a===null?(c=n.child,n.child=null):(c=a.sibling,a.sibling=null),yf(n,!1,c,a,h,o);break;case"backwards":case"unstable_legacy-backwards":for(a=null,c=n.child,n.child=null;c!==null;){if(e=c.alternate,e!==null&&Ul(e)===null){n.child=c;break}e=c.sibling,c.sibling=a,a=c,c=e}yf(n,!0,a,null,h,o);break;case"together":yf(n,!1,null,null,void 0,o);break;default:n.memoizedState=null}return n.child}function la(e,n,a){if(e!==null&&(n.dependencies=e.dependencies),Wa|=n.lanes,(a&n.childLanes)===0)if(e!==null){if(ss(e,n,a,!1),(a&n.childLanes)===0)return null}else return null;if(e!==null&&n.child!==e.child)throw Error(r(153));if(n.child!==null){for(e=n.child,a=na(e,e.pendingProps),n.child=a,a.return=n;e.sibling!==null;)e=e.sibling,a=a.sibling=na(e,e.pendingProps),a.return=n;a.sibling=null}return n.child}function Mf(e,n){return(e.lanes&n)!==0?!0:(e=e.dependencies,!!(e!==null&&El(e)))}function $x(e,n,a){switch(n.tag){case 3:yt(n,n.stateNode.containerInfo),Fa(n,dn,e.memoizedState.cache),br();break;case 27:case 5:ee(n);break;case 4:yt(n,n.stateNode.containerInfo);break;case 10:Fa(n,n.type,n.memoizedProps.value);break;case 31:if(n.memoizedState!==null)return n.flags|=128,qc(n),null;break;case 13:var o=n.memoizedState;if(o!==null)return o.dehydrated!==null?(Ga(n),n.flags|=128,null):(a&n.child.childLanes)!==0?cg(e,n,a):(Ga(n),e=la(e,n,a),e!==null?e.sibling:null);Ga(n);break;case 19:var c=(e.flags&128)!==0;if(o=(a&n.childLanes)!==0,o||(ss(e,n,a,!1),o=(a&n.childLanes)!==0),c){if(o)return hg(e,n,a);n.flags|=128}if(c=n.memoizedState,c!==null&&(c.rendering=null,c.tail=null,c.lastEffect=null),Mt(un,un.current),o)break;return null;case 22:return n.lanes=0,ag(e,n,a,n.pendingProps);case 24:Fa(n,dn,e.memoizedState.cache)}return la(e,n,a)}function dg(e,n,a){if(e!==null)if(e.memoizedProps!==n.pendingProps)mn=!0;else{if(!Mf(e,a)&&(n.flags&128)===0)return mn=!1,$x(e,n,a);mn=(e.flags&131072)!==0}else mn=!1,Me&&(n.flags&1048576)!==0&&Wp(n,fo,n.index);switch(n.lanes=0,n.tag){case 16:t:{var o=n.pendingProps;if(e=Cr(n.elementType),n.type=e,typeof e=="function")Ac(e)?(o=Lr(e,o),n.tag=1,n=lg(null,n,e,o,a)):(n.tag=0,n=mf(null,n,e,o,a));else{if(e!=null){var c=e.$$typeof;if(c===C){n.tag=11,n=eg(null,n,e,o,a);break t}else if(c===O){n.tag=14,n=ng(null,n,e,o,a);break t}}throw n=mt(e)||e,Error(r(306,n,""))}}return n;case 0:return mf(e,n,n.type,n.pendingProps,a);case 1:return o=n.type,c=Lr(o,n.pendingProps),lg(e,n,o,c,a);case 3:t:{if(yt(n,n.stateNode.containerInfo),e===null)throw Error(r(387));o=n.pendingProps;var h=n.memoizedState;c=h.element,Gc(e,n),So(n,o,null,a);var x=n.memoizedState;if(o=x.cache,Fa(n,dn,o),o!==h.cache&&Pc(n,[dn],a,!0),xo(),o=x.element,h.isDehydrated)if(h={element:o,isDehydrated:!1,cache:x.cache},n.updateQueue.baseState=h,n.memoizedState=h,n.flags&256){n=ug(e,n,o,a);break t}else if(o!==c){c=pi(Error(r(424)),n),ho(c),n=ug(e,n,o,a);break t}else for(e=n.stateNode.containerInfo,e.nodeType===9?e=e.body:e=e.nodeName==="HTML"?e.ownerDocument.body:e,Ye=xi(e.firstChild),An=n,Me=!0,Pa=null,_i=!0,a=am(n,null,o,a),n.child=a;a;)a.flags=a.flags&-3|4096,a=a.sibling;else{if(br(),o===c){n=la(e,n,a);break t}Cn(e,n,o,a)}n=n.child}return n;case 26:return Vl(e,n),e===null?(a=b_(n.type,null,n.pendingProps,null))?n.memoizedState=a:Me||(a=n.type,e=n.pendingProps,o=ru(at.current).createElement(a),o[fn]=n,o[Tn]=e,wn(o,a,e),hn(o),n.stateNode=o):n.memoizedState=b_(n.type,e.memoizedProps,n.pendingProps,e.memoizedState),null;case 27:return ee(n),e===null&&Me&&(o=n.stateNode=y_(n.type,n.pendingProps,at.current),An=n,_i=!0,c=Ye,Qa(n.type)?(eh=c,Ye=xi(o.firstChild)):Ye=c),Cn(e,n,n.pendingProps.children,a),Vl(e,n),e===null&&(n.flags|=4194304),n.child;case 5:return e===null&&Me&&((c=o=Ye)&&(o=wS(o,n.type,n.pendingProps,_i),o!==null?(n.stateNode=o,An=n,Ye=xi(o.firstChild),_i=!1,c=!0):c=!1),c||Ia(n)),ee(n),c=n.type,h=n.pendingProps,x=e!==null?e.memoizedProps:null,o=h.children,Qf(c,h)?o=null:x!==null&&Qf(c,x)&&(n.flags|=32),n.memoizedState!==null&&(c=Zc(e,n,Xx,null,null,a),Ho._currentValue=c),Vl(e,n),Cn(e,n,o,a),n.child;case 6:return e===null&&Me&&((e=a=Ye)&&(a=DS(a,n.pendingProps,_i),a!==null?(n.stateNode=a,An=n,Ye=null,e=!0):e=!1),e||Ia(n)),null;case 13:return cg(e,n,a);case 4:return yt(n,n.stateNode.containerInfo),o=n.pendingProps,e===null?n.child=Dr(n,null,o,a):Cn(e,n,o,a),n.child;case 11:return eg(e,n,n.type,n.pendingProps,a);case 7:return Cn(e,n,n.pendingProps,a),n.child;case 8:return Cn(e,n,n.pendingProps.children,a),n.child;case 12:return Cn(e,n,n.pendingProps.children,a),n.child;case 10:return o=n.pendingProps,Fa(n,n.type,o.value),Cn(e,n,o.children,a),n.child;case 9:return c=n.type._context,o=n.pendingProps.children,Ar(n),c=Rn(c),o=o(c),n.flags|=1,Cn(e,n,o,a),n.child;case 14:return ng(e,n,n.type,n.pendingProps,a);case 15:return ig(e,n,n.type,n.pendingProps,a);case 19:return hg(e,n,a);case 31:return jx(e,n,a);case 22:return ag(e,n,a,n.pendingProps);case 24:return Ar(n),o=Rn(dn),e===null?(c=zc(),c===null&&(c=Xe,h=Ic(),c.pooledCache=h,h.refCount++,h!==null&&(c.pooledCacheLanes|=a),c=h),n.memoizedState={parent:o,cache:c},Hc(n),Fa(n,dn,c)):((e.lanes&a)!==0&&(Gc(e,n),So(n,null,null,a),xo()),c=e.memoizedState,h=n.memoizedState,c.parent!==o?(c={parent:o,cache:o},n.memoizedState=c,n.lanes===0&&(n.memoizedState=n.updateQueue.baseState=c),Fa(n,dn,o)):(o=h.cache,Fa(n,dn,o),o!==c.cache&&Pc(n,[dn],a,!0))),Cn(e,n,n.pendingProps.children,a),n.child;case 29:throw n.pendingProps}throw Error(r(156,n.tag))}function ua(e){e.flags|=4}function Ef(e,n,a,o,c){if((n=(e.mode&32)!==0)&&(n=!1),n){if(e.flags|=16777216,(c&335544128)===c)if(e.stateNode.complete)e.flags|=8192;else if(Hg())e.flags|=8192;else throw wr=Rl,Bc}else e.flags&=-16777217}function pg(e,n){if(n.type!=="stylesheet"||(n.state.loading&4)!==0)e.flags&=-16777217;else if(e.flags|=16777216,!w_(n))if(Hg())e.flags|=8192;else throw wr=Rl,Bc}function Xl(e,n){n!==null&&(e.flags|=4),e.flags&16384&&(n=e.tag!==22?St():536870912,e.lanes|=n,vs|=n)}function Ao(e,n){if(!Me)switch(e.tailMode){case"hidden":n=e.tail;for(var a=null;n!==null;)n.alternate!==null&&(a=n),n=n.sibling;a===null?e.tail=null:a.sibling=null;break;case"collapsed":a=e.tail;for(var o=null;a!==null;)a.alternate!==null&&(o=a),a=a.sibling;o===null?n||e.tail===null?e.tail=null:e.tail.sibling=null:o.sibling=null}}function Ze(e){var n=e.alternate!==null&&e.alternate.child===e.child,a=0,o=0;if(n)for(var c=e.child;c!==null;)a|=c.lanes|c.childLanes,o|=c.subtreeFlags&65011712,o|=c.flags&65011712,c.return=e,c=c.sibling;else for(c=e.child;c!==null;)a|=c.lanes|c.childLanes,o|=c.subtreeFlags,o|=c.flags,c.return=e,c=c.sibling;return e.subtreeFlags|=o,e.childLanes=a,n}function tS(e,n,a){var o=n.pendingProps;switch(Dc(n),n.tag){case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return Ze(n),null;case 1:return Ze(n),null;case 3:return a=n.stateNode,o=null,e!==null&&(o=e.memoizedState.cache),n.memoizedState.cache!==o&&(n.flags|=2048),ra(dn),Bt(),a.pendingContext&&(a.context=a.pendingContext,a.pendingContext=null),(e===null||e.child===null)&&(rs(n)?ua(n):e===null||e.memoizedState.isDehydrated&&(n.flags&256)===0||(n.flags|=1024,Lc())),Ze(n),null;case 26:var c=n.type,h=n.memoizedState;return e===null?(ua(n),h!==null?(Ze(n),pg(n,h)):(Ze(n),Ef(n,c,null,o,a))):h?h!==e.memoizedState?(ua(n),Ze(n),pg(n,h)):(Ze(n),n.flags&=-16777217):(e=e.memoizedProps,e!==o&&ua(n),Ze(n),Ef(n,c,e,o,a)),null;case 27:if(Kt(n),a=at.current,c=n.type,e!==null&&n.stateNode!=null)e.memoizedProps!==o&&ua(n);else{if(!o){if(n.stateNode===null)throw Error(r(166));return Ze(n),null}e=Rt.current,rs(n)?Yp(n):(e=y_(c,o,a),n.stateNode=e,ua(n))}return Ze(n),null;case 5:if(Kt(n),c=n.type,e!==null&&n.stateNode!=null)e.memoizedProps!==o&&ua(n);else{if(!o){if(n.stateNode===null)throw Error(r(166));return Ze(n),null}if(h=Rt.current,rs(n))Yp(n);else{var x=ru(at.current);switch(h){case 1:h=x.createElementNS("http://www.w3.org/2000/svg",c);break;case 2:h=x.createElementNS("http://www.w3.org/1998/Math/MathML",c);break;default:switch(c){case"svg":h=x.createElementNS("http://www.w3.org/2000/svg",c);break;case"math":h=x.createElementNS("http://www.w3.org/1998/Math/MathML",c);break;case"script":h=x.createElement("div"),h.innerHTML="<script><\/script>",h=h.removeChild(h.firstChild);break;case"select":h=typeof o.is=="string"?x.createElement("select",{is:o.is}):x.createElement("select"),o.multiple?h.multiple=!0:o.size&&(h.size=o.size);break;default:h=typeof o.is=="string"?x.createElement(c,{is:o.is}):x.createElement(c)}}h[fn]=n,h[Tn]=o;t:for(x=n.child;x!==null;){if(x.tag===5||x.tag===6)h.appendChild(x.stateNode);else if(x.tag!==4&&x.tag!==27&&x.child!==null){x.child.return=x,x=x.child;continue}if(x===n)break t;for(;x.sibling===null;){if(x.return===null||x.return===n)break t;x=x.return}x.sibling.return=x.return,x=x.sibling}n.stateNode=h;t:switch(wn(h,c,o),c){case"button":case"input":case"select":case"textarea":o=!!o.autoFocus;break t;case"img":o=!0;break t;default:o=!1}o&&ua(n)}}return Ze(n),Ef(n,n.type,e===null?null:e.memoizedProps,n.pendingProps,a),null;case 6:if(e&&n.stateNode!=null)e.memoizedProps!==o&&ua(n);else{if(typeof o!="string"&&n.stateNode===null)throw Error(r(166));if(e=at.current,rs(n)){if(e=n.stateNode,a=n.memoizedProps,o=null,c=An,c!==null)switch(c.tag){case 27:case 5:o=c.memoizedProps}e[fn]=n,e=!!(e.nodeValue===a||o!==null&&o.suppressHydrationWarning===!0||c_(e.nodeValue,a)),e||Ia(n,!0)}else e=ru(e).createTextNode(o),e[fn]=n,n.stateNode=e}return Ze(n),null;case 31:if(a=n.memoizedState,e===null||e.memoizedState!==null){if(o=rs(n),a!==null){if(e===null){if(!o)throw Error(r(318));if(e=n.memoizedState,e=e!==null?e.dehydrated:null,!e)throw Error(r(557));e[fn]=n}else br(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;Ze(n),e=!1}else a=Lc(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=a),e=!0;if(!e)return n.flags&256?(ai(n),n):(ai(n),null);if((n.flags&128)!==0)throw Error(r(558))}return Ze(n),null;case 13:if(o=n.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(c=rs(n),o!==null&&o.dehydrated!==null){if(e===null){if(!c)throw Error(r(318));if(c=n.memoizedState,c=c!==null?c.dehydrated:null,!c)throw Error(r(317));c[fn]=n}else br(),(n.flags&128)===0&&(n.memoizedState=null),n.flags|=4;Ze(n),c=!1}else c=Lc(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=c),c=!0;if(!c)return n.flags&256?(ai(n),n):(ai(n),null)}return ai(n),(n.flags&128)!==0?(n.lanes=a,n):(a=o!==null,e=e!==null&&e.memoizedState!==null,a&&(o=n.child,c=null,o.alternate!==null&&o.alternate.memoizedState!==null&&o.alternate.memoizedState.cachePool!==null&&(c=o.alternate.memoizedState.cachePool.pool),h=null,o.memoizedState!==null&&o.memoizedState.cachePool!==null&&(h=o.memoizedState.cachePool.pool),h!==c&&(o.flags|=2048)),a!==e&&a&&(n.child.flags|=8192),Xl(n,n.updateQueue),Ze(n),null);case 4:return Bt(),e===null&&Wf(n.stateNode.containerInfo),Ze(n),null;case 10:return ra(n.type),Ze(n),null;case 19:if(K(un),o=n.memoizedState,o===null)return Ze(n),null;if(c=(n.flags&128)!==0,h=o.rendering,h===null)if(c)Ao(o,!1);else{if(on!==0||e!==null&&(e.flags&128)!==0)for(e=n.child;e!==null;){if(h=Ul(e),h!==null){for(n.flags|=128,Ao(o,!1),e=h.updateQueue,n.updateQueue=e,Xl(n,e),n.subtreeFlags=0,e=a,a=n.child;a!==null;)Vp(a,e),a=a.sibling;return Mt(un,un.current&1|2),Me&&ia(n,o.treeForkCount),n.child}e=e.sibling}o.tail!==null&&ze()>Kl&&(n.flags|=128,c=!0,Ao(o,!1),n.lanes=4194304)}else{if(!c)if(e=Ul(h),e!==null){if(n.flags|=128,c=!0,e=e.updateQueue,n.updateQueue=e,Xl(n,e),Ao(o,!0),o.tail===null&&o.tailMode==="hidden"&&!h.alternate&&!Me)return Ze(n),null}else 2*ze()-o.renderingStartTime>Kl&&a!==536870912&&(n.flags|=128,c=!0,Ao(o,!1),n.lanes=4194304);o.isBackwards?(h.sibling=n.child,n.child=h):(e=o.last,e!==null?e.sibling=h:n.child=h,o.last=h)}return o.tail!==null?(e=o.tail,o.rendering=e,o.tail=e.sibling,o.renderingStartTime=ze(),e.sibling=null,a=un.current,Mt(un,c?a&1|2:a&1),Me&&ia(n,o.treeForkCount),e):(Ze(n),null);case 22:case 23:return ai(n),Wc(),o=n.memoizedState!==null,e!==null?e.memoizedState!==null!==o&&(n.flags|=8192):o&&(n.flags|=8192),o?(a&536870912)!==0&&(n.flags&128)===0&&(Ze(n),n.subtreeFlags&6&&(n.flags|=8192)):Ze(n),a=n.updateQueue,a!==null&&Xl(n,a.retryQueue),a=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(a=e.memoizedState.cachePool.pool),o=null,n.memoizedState!==null&&n.memoizedState.cachePool!==null&&(o=n.memoizedState.cachePool.pool),o!==a&&(n.flags|=2048),e!==null&&K(Rr),null;case 24:return a=null,e!==null&&(a=e.memoizedState.cache),n.memoizedState.cache!==a&&(n.flags|=2048),ra(dn),Ze(n),null;case 25:return null;case 30:return null}throw Error(r(156,n.tag))}function eS(e,n){switch(Dc(n),n.tag){case 1:return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 3:return ra(dn),Bt(),e=n.flags,(e&65536)!==0&&(e&128)===0?(n.flags=e&-65537|128,n):null;case 26:case 27:case 5:return Kt(n),null;case 31:if(n.memoizedState!==null){if(ai(n),n.alternate===null)throw Error(r(340));br()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 13:if(ai(n),e=n.memoizedState,e!==null&&e.dehydrated!==null){if(n.alternate===null)throw Error(r(340));br()}return e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 19:return K(un),null;case 4:return Bt(),null;case 10:return ra(n.type),null;case 22:case 23:return ai(n),Wc(),e!==null&&K(Rr),e=n.flags,e&65536?(n.flags=e&-65537|128,n):null;case 24:return ra(dn),null;case 25:return null;default:return null}}function mg(e,n){switch(Dc(n),n.tag){case 3:ra(dn),Bt();break;case 26:case 27:case 5:Kt(n);break;case 4:Bt();break;case 31:n.memoizedState!==null&&ai(n);break;case 13:ai(n);break;case 19:K(un);break;case 10:ra(n.type);break;case 22:case 23:ai(n),Wc(),e!==null&&K(Rr);break;case 24:ra(dn)}}function Ro(e,n){try{var a=n.updateQueue,o=a!==null?a.lastEffect:null;if(o!==null){var c=o.next;a=c;do{if((a.tag&e)===e){o=void 0;var h=a.create,x=a.inst;o=h(),x.destroy=o}a=a.next}while(a!==c)}}catch(R){Ie(n,n.return,R)}}function ka(e,n,a){try{var o=n.updateQueue,c=o!==null?o.lastEffect:null;if(c!==null){var h=c.next;o=h;do{if((o.tag&e)===e){var x=o.inst,R=x.destroy;if(R!==void 0){x.destroy=void 0,c=n;var B=a,et=R;try{et()}catch(dt){Ie(c,B,dt)}}}o=o.next}while(o!==h)}}catch(dt){Ie(n,n.return,dt)}}function gg(e){var n=e.updateQueue;if(n!==null){var a=e.stateNode;try{sm(n,a)}catch(o){Ie(e,e.return,o)}}}function _g(e,n,a){a.props=Lr(e.type,e.memoizedProps),a.state=e.memoizedState;try{a.componentWillUnmount()}catch(o){Ie(e,n,o)}}function Co(e,n){try{var a=e.ref;if(a!==null){switch(e.tag){case 26:case 27:case 5:var o=e.stateNode;break;case 30:o=e.stateNode;break;default:o=e.stateNode}typeof a=="function"?e.refCleanup=a(o):a.current=o}}catch(c){Ie(e,n,c)}}function Hi(e,n){var a=e.ref,o=e.refCleanup;if(a!==null)if(typeof o=="function")try{o()}catch(c){Ie(e,n,c)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof a=="function")try{a(null)}catch(c){Ie(e,n,c)}else a.current=null}function vg(e){var n=e.type,a=e.memoizedProps,o=e.stateNode;try{t:switch(n){case"button":case"input":case"select":case"textarea":a.autoFocus&&o.focus();break t;case"img":a.src?o.src=a.src:a.srcSet&&(o.srcset=a.srcSet)}}catch(c){Ie(e,e.return,c)}}function bf(e,n,a){try{var o=e.stateNode;ES(o,e.type,a,n),o[Tn]=n}catch(c){Ie(e,e.return,c)}}function xg(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&Qa(e.type)||e.tag===4}function Tf(e){t:for(;;){for(;e.sibling===null;){if(e.return===null||xg(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&Qa(e.type)||e.flags&2||e.child===null||e.tag===4)continue t;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function Af(e,n,a){var o=e.tag;if(o===5||o===6)e=e.stateNode,n?(a.nodeType===9?a.body:a.nodeName==="HTML"?a.ownerDocument.body:a).insertBefore(e,n):(n=a.nodeType===9?a.body:a.nodeName==="HTML"?a.ownerDocument.body:a,n.appendChild(e),a=a._reactRootContainer,a!=null||n.onclick!==null||(n.onclick=ta));else if(o!==4&&(o===27&&Qa(e.type)&&(a=e.stateNode,n=null),e=e.child,e!==null))for(Af(e,n,a),e=e.sibling;e!==null;)Af(e,n,a),e=e.sibling}function Wl(e,n,a){var o=e.tag;if(o===5||o===6)e=e.stateNode,n?a.insertBefore(e,n):a.appendChild(e);else if(o!==4&&(o===27&&Qa(e.type)&&(a=e.stateNode),e=e.child,e!==null))for(Wl(e,n,a),e=e.sibling;e!==null;)Wl(e,n,a),e=e.sibling}function Sg(e){var n=e.stateNode,a=e.memoizedProps;try{for(var o=e.type,c=n.attributes;c.length;)n.removeAttributeNode(c[0]);wn(n,o,a),n[fn]=e,n[Tn]=a}catch(h){Ie(e,e.return,h)}}var ca=!1,gn=!1,Rf=!1,yg=typeof WeakSet=="function"?WeakSet:Set,En=null;function nS(e,n){if(e=e.containerInfo,Zf=hu,e=Np(e),xc(e)){if("selectionStart"in e)var a={start:e.selectionStart,end:e.selectionEnd};else t:{a=(a=e.ownerDocument)&&a.defaultView||window;var o=a.getSelection&&a.getSelection();if(o&&o.rangeCount!==0){a=o.anchorNode;var c=o.anchorOffset,h=o.focusNode;o=o.focusOffset;try{a.nodeType,h.nodeType}catch{a=null;break t}var x=0,R=-1,B=-1,et=0,dt=0,vt=e,ot=null;e:for(;;){for(var lt;vt!==a||c!==0&&vt.nodeType!==3||(R=x+c),vt!==h||o!==0&&vt.nodeType!==3||(B=x+o),vt.nodeType===3&&(x+=vt.nodeValue.length),(lt=vt.firstChild)!==null;)ot=vt,vt=lt;for(;;){if(vt===e)break e;if(ot===a&&++et===c&&(R=x),ot===h&&++dt===o&&(B=x),(lt=vt.nextSibling)!==null)break;vt=ot,ot=vt.parentNode}vt=lt}a=R===-1||B===-1?null:{start:R,end:B}}else a=null}a=a||{start:0,end:0}}else a=null;for(Kf={focusedElem:e,selectionRange:a},hu=!1,En=n;En!==null;)if(n=En,e=n.child,(n.subtreeFlags&1028)!==0&&e!==null)e.return=n,En=e;else for(;En!==null;){switch(n=En,h=n.alternate,e=n.flags,n.tag){case 0:if((e&4)!==0&&(e=n.updateQueue,e=e!==null?e.events:null,e!==null))for(a=0;a<e.length;a++)c=e[a],c.ref.impl=c.nextImpl;break;case 11:case 15:break;case 1:if((e&1024)!==0&&h!==null){e=void 0,a=n,c=h.memoizedProps,h=h.memoizedState,o=a.stateNode;try{var Xt=Lr(a.type,c);e=o.getSnapshotBeforeUpdate(Xt,h),o.__reactInternalSnapshotBeforeUpdate=e}catch($t){Ie(a,a.return,$t)}}break;case 3:if((e&1024)!==0){if(e=n.stateNode.containerInfo,a=e.nodeType,a===9)jf(e);else if(a===1)switch(e.nodeName){case"HEAD":case"HTML":case"BODY":jf(e);break;default:e.textContent=""}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if((e&1024)!==0)throw Error(r(163))}if(e=n.sibling,e!==null){e.return=n.return,En=e;break}En=n.return}}function Mg(e,n,a){var o=a.flags;switch(a.tag){case 0:case 11:case 15:ha(e,a),o&4&&Ro(5,a);break;case 1:if(ha(e,a),o&4)if(e=a.stateNode,n===null)try{e.componentDidMount()}catch(x){Ie(a,a.return,x)}else{var c=Lr(a.type,n.memoizedProps);n=n.memoizedState;try{e.componentDidUpdate(c,n,e.__reactInternalSnapshotBeforeUpdate)}catch(x){Ie(a,a.return,x)}}o&64&&gg(a),o&512&&Co(a,a.return);break;case 3:if(ha(e,a),o&64&&(e=a.updateQueue,e!==null)){if(n=null,a.child!==null)switch(a.child.tag){case 27:case 5:n=a.child.stateNode;break;case 1:n=a.child.stateNode}try{sm(e,n)}catch(x){Ie(a,a.return,x)}}break;case 27:n===null&&o&4&&Sg(a);case 26:case 5:ha(e,a),n===null&&o&4&&vg(a),o&512&&Co(a,a.return);break;case 12:ha(e,a);break;case 31:ha(e,a),o&4&&Tg(e,a);break;case 13:ha(e,a),o&4&&Ag(e,a),o&64&&(e=a.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(a=fS.bind(null,a),US(e,a))));break;case 22:if(o=a.memoizedState!==null||ca,!o){n=n!==null&&n.memoizedState!==null||gn,c=ca;var h=gn;ca=o,(gn=n)&&!h?da(e,a,(a.subtreeFlags&8772)!==0):ha(e,a),ca=c,gn=h}break;case 30:break;default:ha(e,a)}}function Eg(e){var n=e.alternate;n!==null&&(e.alternate=null,Eg(n)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(n=e.stateNode,n!==null&&Da(n)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var je=null,kn=!1;function fa(e,n,a){for(a=a.child;a!==null;)bg(e,n,a),a=a.sibling}function bg(e,n,a){if(ft&&typeof ft.onCommitFiberUnmount=="function")try{ft.onCommitFiberUnmount(ut,a)}catch{}switch(a.tag){case 26:gn||Hi(a,n),fa(e,n,a),a.memoizedState?a.memoizedState.count--:a.stateNode&&(a=a.stateNode,a.parentNode.removeChild(a));break;case 27:gn||Hi(a,n);var o=je,c=kn;Qa(a.type)&&(je=a.stateNode,kn=!1),fa(e,n,a),Fo(a.stateNode),je=o,kn=c;break;case 5:gn||Hi(a,n);case 6:if(o=je,c=kn,je=null,fa(e,n,a),je=o,kn=c,je!==null)if(kn)try{(je.nodeType===9?je.body:je.nodeName==="HTML"?je.ownerDocument.body:je).removeChild(a.stateNode)}catch(h){Ie(a,n,h)}else try{je.removeChild(a.stateNode)}catch(h){Ie(a,n,h)}break;case 18:je!==null&&(kn?(e=je,g_(e.nodeType===9?e.body:e.nodeName==="HTML"?e.ownerDocument.body:e,a.stateNode),As(e)):g_(je,a.stateNode));break;case 4:o=je,c=kn,je=a.stateNode.containerInfo,kn=!0,fa(e,n,a),je=o,kn=c;break;case 0:case 11:case 14:case 15:ka(2,a,n),gn||ka(4,a,n),fa(e,n,a);break;case 1:gn||(Hi(a,n),o=a.stateNode,typeof o.componentWillUnmount=="function"&&_g(a,n,o)),fa(e,n,a);break;case 21:fa(e,n,a);break;case 22:gn=(o=gn)||a.memoizedState!==null,fa(e,n,a),gn=o;break;default:fa(e,n,a)}}function Tg(e,n){if(n.memoizedState===null&&(e=n.alternate,e!==null&&(e=e.memoizedState,e!==null))){e=e.dehydrated;try{As(e)}catch(a){Ie(n,n.return,a)}}}function Ag(e,n){if(n.memoizedState===null&&(e=n.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{As(e)}catch(a){Ie(n,n.return,a)}}function iS(e){switch(e.tag){case 31:case 13:case 19:var n=e.stateNode;return n===null&&(n=e.stateNode=new yg),n;case 22:return e=e.stateNode,n=e._retryCache,n===null&&(n=e._retryCache=new yg),n;default:throw Error(r(435,e.tag))}}function ql(e,n){var a=iS(e);n.forEach(function(o){if(!a.has(o)){a.add(o);var c=hS.bind(null,e,o);o.then(c,c)}})}function Xn(e,n){var a=n.deletions;if(a!==null)for(var o=0;o<a.length;o++){var c=a[o],h=e,x=n,R=x;t:for(;R!==null;){switch(R.tag){case 27:if(Qa(R.type)){je=R.stateNode,kn=!1;break t}break;case 5:je=R.stateNode,kn=!1;break t;case 3:case 4:je=R.stateNode.containerInfo,kn=!0;break t}R=R.return}if(je===null)throw Error(r(160));bg(h,x,c),je=null,kn=!1,h=c.alternate,h!==null&&(h.return=null),c.return=null}if(n.subtreeFlags&13886)for(n=n.child;n!==null;)Rg(n,e),n=n.sibling}var Ri=null;function Rg(e,n){var a=e.alternate,o=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:Xn(n,e),Wn(e),o&4&&(ka(3,e,e.return),Ro(3,e),ka(5,e,e.return));break;case 1:Xn(n,e),Wn(e),o&512&&(gn||a===null||Hi(a,a.return)),o&64&&ca&&(e=e.updateQueue,e!==null&&(o=e.callbacks,o!==null&&(a=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=a===null?o:a.concat(o))));break;case 26:var c=Ri;if(Xn(n,e),Wn(e),o&512&&(gn||a===null||Hi(a,a.return)),o&4){var h=a!==null?a.memoizedState:null;if(o=e.memoizedState,a===null)if(o===null)if(e.stateNode===null){t:{o=e.type,a=e.memoizedProps,c=c.ownerDocument||c;e:switch(o){case"title":h=c.getElementsByTagName("title")[0],(!h||h[wa]||h[fn]||h.namespaceURI==="http://www.w3.org/2000/svg"||h.hasAttribute("itemprop"))&&(h=c.createElement(o),c.head.insertBefore(h,c.querySelector("head > title"))),wn(h,o,a),h[fn]=e,hn(h),o=h;break t;case"link":var x=R_("link","href",c).get(o+(a.href||""));if(x){for(var R=0;R<x.length;R++)if(h=x[R],h.getAttribute("href")===(a.href==null||a.href===""?null:a.href)&&h.getAttribute("rel")===(a.rel==null?null:a.rel)&&h.getAttribute("title")===(a.title==null?null:a.title)&&h.getAttribute("crossorigin")===(a.crossOrigin==null?null:a.crossOrigin)){x.splice(R,1);break e}}h=c.createElement(o),wn(h,o,a),c.head.appendChild(h);break;case"meta":if(x=R_("meta","content",c).get(o+(a.content||""))){for(R=0;R<x.length;R++)if(h=x[R],h.getAttribute("content")===(a.content==null?null:""+a.content)&&h.getAttribute("name")===(a.name==null?null:a.name)&&h.getAttribute("property")===(a.property==null?null:a.property)&&h.getAttribute("http-equiv")===(a.httpEquiv==null?null:a.httpEquiv)&&h.getAttribute("charset")===(a.charSet==null?null:a.charSet)){x.splice(R,1);break e}}h=c.createElement(o),wn(h,o,a),c.head.appendChild(h);break;default:throw Error(r(468,o))}h[fn]=e,hn(h),o=h}e.stateNode=o}else C_(c,e.type,e.stateNode);else e.stateNode=A_(c,o,e.memoizedProps);else h!==o?(h===null?a.stateNode!==null&&(a=a.stateNode,a.parentNode.removeChild(a)):h.count--,o===null?C_(c,e.type,e.stateNode):A_(c,o,e.memoizedProps)):o===null&&e.stateNode!==null&&bf(e,e.memoizedProps,a.memoizedProps)}break;case 27:Xn(n,e),Wn(e),o&512&&(gn||a===null||Hi(a,a.return)),a!==null&&o&4&&bf(e,e.memoizedProps,a.memoizedProps);break;case 5:if(Xn(n,e),Wn(e),o&512&&(gn||a===null||Hi(a,a.return)),e.flags&32){c=e.stateNode;try{ti(c,"")}catch(Xt){Ie(e,e.return,Xt)}}o&4&&e.stateNode!=null&&(c=e.memoizedProps,bf(e,c,a!==null?a.memoizedProps:c)),o&1024&&(Rf=!0);break;case 6:if(Xn(n,e),Wn(e),o&4){if(e.stateNode===null)throw Error(r(162));o=e.memoizedProps,a=e.stateNode;try{a.nodeValue=o}catch(Xt){Ie(e,e.return,Xt)}}break;case 3:if(lu=null,c=Ri,Ri=su(n.containerInfo),Xn(n,e),Ri=c,Wn(e),o&4&&a!==null&&a.memoizedState.isDehydrated)try{As(n.containerInfo)}catch(Xt){Ie(e,e.return,Xt)}Rf&&(Rf=!1,Cg(e));break;case 4:o=Ri,Ri=su(e.stateNode.containerInfo),Xn(n,e),Wn(e),Ri=o;break;case 12:Xn(n,e),Wn(e);break;case 31:Xn(n,e),Wn(e),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,ql(e,o)));break;case 13:Xn(n,e),Wn(e),e.child.flags&8192&&e.memoizedState!==null!=(a!==null&&a.memoizedState!==null)&&(Zl=ze()),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,ql(e,o)));break;case 22:c=e.memoizedState!==null;var B=a!==null&&a.memoizedState!==null,et=ca,dt=gn;if(ca=et||c,gn=dt||B,Xn(n,e),gn=dt,ca=et,Wn(e),o&8192)t:for(n=e.stateNode,n._visibility=c?n._visibility&-2:n._visibility|1,c&&(a===null||B||ca||gn||Nr(e)),a=null,n=e;;){if(n.tag===5||n.tag===26){if(a===null){B=a=n;try{if(h=B.stateNode,c)x=h.style,typeof x.setProperty=="function"?x.setProperty("display","none","important"):x.display="none";else{R=B.stateNode;var vt=B.memoizedProps.style,ot=vt!=null&&vt.hasOwnProperty("display")?vt.display:null;R.style.display=ot==null||typeof ot=="boolean"?"":(""+ot).trim()}}catch(Xt){Ie(B,B.return,Xt)}}}else if(n.tag===6){if(a===null){B=n;try{B.stateNode.nodeValue=c?"":B.memoizedProps}catch(Xt){Ie(B,B.return,Xt)}}}else if(n.tag===18){if(a===null){B=n;try{var lt=B.stateNode;c?__(lt,!0):__(B.stateNode,!1)}catch(Xt){Ie(B,B.return,Xt)}}}else if((n.tag!==22&&n.tag!==23||n.memoizedState===null||n===e)&&n.child!==null){n.child.return=n,n=n.child;continue}if(n===e)break t;for(;n.sibling===null;){if(n.return===null||n.return===e)break t;a===n&&(a=null),n=n.return}a===n&&(a=null),n.sibling.return=n.return,n=n.sibling}o&4&&(o=e.updateQueue,o!==null&&(a=o.retryQueue,a!==null&&(o.retryQueue=null,ql(e,a))));break;case 19:Xn(n,e),Wn(e),o&4&&(o=e.updateQueue,o!==null&&(e.updateQueue=null,ql(e,o)));break;case 30:break;case 21:break;default:Xn(n,e),Wn(e)}}function Wn(e){var n=e.flags;if(n&2){try{for(var a,o=e.return;o!==null;){if(xg(o)){a=o;break}o=o.return}if(a==null)throw Error(r(160));switch(a.tag){case 27:var c=a.stateNode,h=Tf(e);Wl(e,h,c);break;case 5:var x=a.stateNode;a.flags&32&&(ti(x,""),a.flags&=-33);var R=Tf(e);Wl(e,R,x);break;case 3:case 4:var B=a.stateNode.containerInfo,et=Tf(e);Af(e,et,B);break;default:throw Error(r(161))}}catch(dt){Ie(e,e.return,dt)}e.flags&=-3}n&4096&&(e.flags&=-4097)}function Cg(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var n=e;Cg(n),n.tag===5&&n.flags&1024&&n.stateNode.reset(),e=e.sibling}}function ha(e,n){if(n.subtreeFlags&8772)for(n=n.child;n!==null;)Mg(e,n.alternate,n),n=n.sibling}function Nr(e){for(e=e.child;e!==null;){var n=e;switch(n.tag){case 0:case 11:case 14:case 15:ka(4,n,n.return),Nr(n);break;case 1:Hi(n,n.return);var a=n.stateNode;typeof a.componentWillUnmount=="function"&&_g(n,n.return,a),Nr(n);break;case 27:Fo(n.stateNode);case 26:case 5:Hi(n,n.return),Nr(n);break;case 22:n.memoizedState===null&&Nr(n);break;case 30:Nr(n);break;default:Nr(n)}e=e.sibling}}function da(e,n,a){for(a=a&&(n.subtreeFlags&8772)!==0,n=n.child;n!==null;){var o=n.alternate,c=e,h=n,x=h.flags;switch(h.tag){case 0:case 11:case 15:da(c,h,a),Ro(4,h);break;case 1:if(da(c,h,a),o=h,c=o.stateNode,typeof c.componentDidMount=="function")try{c.componentDidMount()}catch(et){Ie(o,o.return,et)}if(o=h,c=o.updateQueue,c!==null){var R=o.stateNode;try{var B=c.shared.hiddenCallbacks;if(B!==null)for(c.shared.hiddenCallbacks=null,c=0;c<B.length;c++)rm(B[c],R)}catch(et){Ie(o,o.return,et)}}a&&x&64&&gg(h),Co(h,h.return);break;case 27:Sg(h);case 26:case 5:da(c,h,a),a&&o===null&&x&4&&vg(h),Co(h,h.return);break;case 12:da(c,h,a);break;case 31:da(c,h,a),a&&x&4&&Tg(c,h);break;case 13:da(c,h,a),a&&x&4&&Ag(c,h);break;case 22:h.memoizedState===null&&da(c,h,a),Co(h,h.return);break;case 30:break;default:da(c,h,a)}n=n.sibling}}function Cf(e,n){var a=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(a=e.memoizedState.cachePool.pool),e=null,n.memoizedState!==null&&n.memoizedState.cachePool!==null&&(e=n.memoizedState.cachePool.pool),e!==a&&(e!=null&&e.refCount++,a!=null&&po(a))}function wf(e,n){e=null,n.alternate!==null&&(e=n.alternate.memoizedState.cache),n=n.memoizedState.cache,n!==e&&(n.refCount++,e!=null&&po(e))}function Ci(e,n,a,o){if(n.subtreeFlags&10256)for(n=n.child;n!==null;)wg(e,n,a,o),n=n.sibling}function wg(e,n,a,o){var c=n.flags;switch(n.tag){case 0:case 11:case 15:Ci(e,n,a,o),c&2048&&Ro(9,n);break;case 1:Ci(e,n,a,o);break;case 3:Ci(e,n,a,o),c&2048&&(e=null,n.alternate!==null&&(e=n.alternate.memoizedState.cache),n=n.memoizedState.cache,n!==e&&(n.refCount++,e!=null&&po(e)));break;case 12:if(c&2048){Ci(e,n,a,o),e=n.stateNode;try{var h=n.memoizedProps,x=h.id,R=h.onPostCommit;typeof R=="function"&&R(x,n.alternate===null?"mount":"update",e.passiveEffectDuration,-0)}catch(B){Ie(n,n.return,B)}}else Ci(e,n,a,o);break;case 31:Ci(e,n,a,o);break;case 13:Ci(e,n,a,o);break;case 23:break;case 22:h=n.stateNode,x=n.alternate,n.memoizedState!==null?h._visibility&2?Ci(e,n,a,o):wo(e,n):h._visibility&2?Ci(e,n,a,o):(h._visibility|=2,ms(e,n,a,o,(n.subtreeFlags&10256)!==0||!1)),c&2048&&Cf(x,n);break;case 24:Ci(e,n,a,o),c&2048&&wf(n.alternate,n);break;default:Ci(e,n,a,o)}}function ms(e,n,a,o,c){for(c=c&&((n.subtreeFlags&10256)!==0||!1),n=n.child;n!==null;){var h=e,x=n,R=a,B=o,et=x.flags;switch(x.tag){case 0:case 11:case 15:ms(h,x,R,B,c),Ro(8,x);break;case 23:break;case 22:var dt=x.stateNode;x.memoizedState!==null?dt._visibility&2?ms(h,x,R,B,c):wo(h,x):(dt._visibility|=2,ms(h,x,R,B,c)),c&&et&2048&&Cf(x.alternate,x);break;case 24:ms(h,x,R,B,c),c&&et&2048&&wf(x.alternate,x);break;default:ms(h,x,R,B,c)}n=n.sibling}}function wo(e,n){if(n.subtreeFlags&10256)for(n=n.child;n!==null;){var a=e,o=n,c=o.flags;switch(o.tag){case 22:wo(a,o),c&2048&&Cf(o.alternate,o);break;case 24:wo(a,o),c&2048&&wf(o.alternate,o);break;default:wo(a,o)}n=n.sibling}}var Do=8192;function gs(e,n,a){if(e.subtreeFlags&Do)for(e=e.child;e!==null;)Dg(e,n,a),e=e.sibling}function Dg(e,n,a){switch(e.tag){case 26:gs(e,n,a),e.flags&Do&&e.memoizedState!==null&&kS(a,Ri,e.memoizedState,e.memoizedProps);break;case 5:gs(e,n,a);break;case 3:case 4:var o=Ri;Ri=su(e.stateNode.containerInfo),gs(e,n,a),Ri=o;break;case 22:e.memoizedState===null&&(o=e.alternate,o!==null&&o.memoizedState!==null?(o=Do,Do=16777216,gs(e,n,a),Do=o):gs(e,n,a));break;default:gs(e,n,a)}}function Ug(e){var n=e.alternate;if(n!==null&&(e=n.child,e!==null)){n.child=null;do n=e.sibling,e.sibling=null,e=n;while(e!==null)}}function Uo(e){var n=e.deletions;if((e.flags&16)!==0){if(n!==null)for(var a=0;a<n.length;a++){var o=n[a];En=o,Ng(o,e)}Ug(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)Lg(e),e=e.sibling}function Lg(e){switch(e.tag){case 0:case 11:case 15:Uo(e),e.flags&2048&&ka(9,e,e.return);break;case 3:Uo(e);break;case 12:Uo(e);break;case 22:var n=e.stateNode;e.memoizedState!==null&&n._visibility&2&&(e.return===null||e.return.tag!==13)?(n._visibility&=-3,Yl(e)):Uo(e);break;default:Uo(e)}}function Yl(e){var n=e.deletions;if((e.flags&16)!==0){if(n!==null)for(var a=0;a<n.length;a++){var o=n[a];En=o,Ng(o,e)}Ug(e)}for(e=e.child;e!==null;){switch(n=e,n.tag){case 0:case 11:case 15:ka(8,n,n.return),Yl(n);break;case 22:a=n.stateNode,a._visibility&2&&(a._visibility&=-3,Yl(n));break;default:Yl(n)}e=e.sibling}}function Ng(e,n){for(;En!==null;){var a=En;switch(a.tag){case 0:case 11:case 15:ka(8,a,n);break;case 23:case 22:if(a.memoizedState!==null&&a.memoizedState.cachePool!==null){var o=a.memoizedState.cachePool.pool;o!=null&&o.refCount++}break;case 24:po(a.memoizedState.cache)}if(o=a.child,o!==null)o.return=a,En=o;else t:for(a=e;En!==null;){o=En;var c=o.sibling,h=o.return;if(Eg(o),o===a){En=null;break t}if(c!==null){c.return=h,En=c;break t}En=h}}}var aS={getCacheForType:function(e){var n=Rn(dn),a=n.data.get(e);return a===void 0&&(a=e(),n.data.set(e,a)),a},cacheSignal:function(){return Rn(dn).controller.signal}},rS=typeof WeakMap=="function"?WeakMap:Map,we=0,Xe=null,de=null,ge=0,Pe=0,ri=null,Xa=!1,_s=!1,Df=!1,pa=0,on=0,Wa=0,Or=0,Uf=0,si=0,vs=0,Lo=null,qn=null,Lf=!1,Zl=0,Og=0,Kl=1/0,Ql=null,qa=null,xn=0,Ya=null,xs=null,ma=0,Nf=0,Of=null,Pg=null,No=0,Pf=null;function oi(){return(we&2)!==0&&ge!==0?ge&-ge:I.T!==null?Gf():eo()}function Ig(){if(si===0)if((ge&536870912)===0||Me){var e=ne;ne<<=1,(ne&3932160)===0&&(ne=262144),si=e}else si=536870912;return e=ii.current,e!==null&&(e.flags|=32),si}function Yn(e,n,a){(e===Xe&&(Pe===2||Pe===9)||e.cancelPendingCommit!==null)&&(Ss(e,0),Za(e,ge,si,!1)),Gt(e,a),((we&2)===0||e!==Xe)&&(e===Xe&&((we&2)===0&&(Or|=a),on===4&&Za(e,ge,si,!1)),Gi(e))}function Fg(e,n,a){if((we&6)!==0)throw Error(r(327));var o=!a&&(n&127)===0&&(n&e.expiredLanes)===0||Ct(e,n),c=o?lS(e,n):Ff(e,n,!0),h=o;do{if(c===0){_s&&!o&&Za(e,n,0,!1);break}else{if(a=e.current.alternate,h&&!sS(a)){c=Ff(e,n,!1),h=!1;continue}if(c===2){if(h=n,e.errorRecoveryDisabledLanes&h)var x=0;else x=e.pendingLanes&-536870913,x=x!==0?x:x&536870912?536870912:0;if(x!==0){n=x;t:{var R=e;c=Lo;var B=R.current.memoizedState.isDehydrated;if(B&&(Ss(R,x).flags|=256),x=Ff(R,x,!1),x!==2){if(Df&&!B){R.errorRecoveryDisabledLanes|=h,Or|=h,c=4;break t}h=qn,qn=c,h!==null&&(qn===null?qn=h:qn.push.apply(qn,h))}c=x}if(h=!1,c!==2)continue}}if(c===1){Ss(e,0),Za(e,n,0,!0);break}t:{switch(o=e,h=c,h){case 0:case 1:throw Error(r(345));case 4:if((n&4194048)!==n)break;case 6:Za(o,n,si,!Xa);break t;case 2:qn=null;break;case 3:case 5:break;default:throw Error(r(329))}if((n&62914560)===n&&(c=Zl+300-ze(),10<c)){if(Za(o,n,si,!Xa),pt(o,0,!0)!==0)break t;ma=n,o.timeoutHandle=p_(zg.bind(null,o,a,qn,Ql,Lf,n,si,Or,vs,Xa,h,"Throttled",-0,0),c);break t}zg(o,a,qn,Ql,Lf,n,si,Or,vs,Xa,h,null,-0,0)}}break}while(!0);Gi(e)}function zg(e,n,a,o,c,h,x,R,B,et,dt,vt,ot,lt){if(e.timeoutHandle=-1,vt=n.subtreeFlags,vt&8192||(vt&16785408)===16785408){vt={stylesheets:null,count:0,imgCount:0,imgBytes:0,suspenseyImages:[],waitingForImages:!0,waitingForViewTransition:!1,unsuspend:ta},Dg(n,h,vt);var Xt=(h&62914560)===h?Zl-ze():(h&4194048)===h?Og-ze():0;if(Xt=XS(vt,Xt),Xt!==null){ma=h,e.cancelPendingCommit=Xt(qg.bind(null,e,n,h,a,o,c,x,R,B,dt,vt,null,ot,lt)),Za(e,h,x,!et);return}}qg(e,n,h,a,o,c,x,R,B)}function sS(e){for(var n=e;;){var a=n.tag;if((a===0||a===11||a===15)&&n.flags&16384&&(a=n.updateQueue,a!==null&&(a=a.stores,a!==null)))for(var o=0;o<a.length;o++){var c=a[o],h=c.getSnapshot;c=c.value;try{if(!ei(h(),c))return!1}catch{return!1}}if(a=n.child,n.subtreeFlags&16384&&a!==null)a.return=n,n=a;else{if(n===e)break;for(;n.sibling===null;){if(n.return===null||n.return===e)return!0;n=n.return}n.sibling.return=n.return,n=n.sibling}}return!0}function Za(e,n,a,o){n&=~Uf,n&=~Or,e.suspendedLanes|=n,e.pingedLanes&=~n,o&&(e.warmLanes|=n),o=e.expirationTimes;for(var c=n;0<c;){var h=31-Ft(c),x=1<<h;o[h]=-1,c&=~x}a!==0&&Ue(e,a,n)}function Jl(){return(we&6)===0?(Oo(0),!1):!0}function If(){if(de!==null){if(Pe===0)var e=de.return;else e=de,aa=Tr=null,Jc(e),cs=null,go=0,e=de;for(;e!==null;)mg(e.alternate,e),e=e.return;de=null}}function Ss(e,n){var a=e.timeoutHandle;a!==-1&&(e.timeoutHandle=-1,AS(a)),a=e.cancelPendingCommit,a!==null&&(e.cancelPendingCommit=null,a()),ma=0,If(),Xe=e,de=a=na(e.current,null),ge=n,Pe=0,ri=null,Xa=!1,_s=Ct(e,n),Df=!1,vs=si=Uf=Or=Wa=on=0,qn=Lo=null,Lf=!1,(n&8)!==0&&(n|=n&32);var o=e.entangledLanes;if(o!==0)for(e=e.entanglements,o&=n;0<o;){var c=31-Ft(o),h=1<<c;n|=e[c],o&=~h}return pa=n,vl(),a}function Bg(e,n){oe=null,I.H=bo,n===us||n===Al?(n=em(),Pe=3):n===Bc?(n=em(),Pe=4):Pe=n===pf?8:n!==null&&typeof n=="object"&&typeof n.then=="function"?6:1,ri=n,de===null&&(on=1,Hl(e,pi(n,e.current)))}function Hg(){var e=ii.current;return e===null?!0:(ge&4194048)===ge?vi===null:(ge&62914560)===ge||(ge&536870912)!==0?e===vi:!1}function Gg(){var e=I.H;return I.H=bo,e===null?bo:e}function Vg(){var e=I.A;return I.A=aS,e}function jl(){on=4,Xa||(ge&4194048)!==ge&&ii.current!==null||(_s=!0),(Wa&134217727)===0&&(Or&134217727)===0||Xe===null||Za(Xe,ge,si,!1)}function Ff(e,n,a){var o=we;we|=2;var c=Gg(),h=Vg();(Xe!==e||ge!==n)&&(Ql=null,Ss(e,n)),n=!1;var x=on;t:do try{if(Pe!==0&&de!==null){var R=de,B=ri;switch(Pe){case 8:If(),x=6;break t;case 3:case 2:case 9:case 6:ii.current===null&&(n=!0);var et=Pe;if(Pe=0,ri=null,ys(e,R,B,et),a&&_s){x=0;break t}break;default:et=Pe,Pe=0,ri=null,ys(e,R,B,et)}}oS(),x=on;break}catch(dt){Bg(e,dt)}while(!0);return n&&e.shellSuspendCounter++,aa=Tr=null,we=o,I.H=c,I.A=h,de===null&&(Xe=null,ge=0,vl()),x}function oS(){for(;de!==null;)kg(de)}function lS(e,n){var a=we;we|=2;var o=Gg(),c=Vg();Xe!==e||ge!==n?(Ql=null,Kl=ze()+500,Ss(e,n)):_s=Ct(e,n);t:do try{if(Pe!==0&&de!==null){n=de;var h=ri;e:switch(Pe){case 1:Pe=0,ri=null,ys(e,n,h,1);break;case 2:case 9:if($p(h)){Pe=0,ri=null,Xg(n);break}n=function(){Pe!==2&&Pe!==9||Xe!==e||(Pe=7),Gi(e)},h.then(n,n);break t;case 3:Pe=7;break t;case 4:Pe=5;break t;case 7:$p(h)?(Pe=0,ri=null,Xg(n)):(Pe=0,ri=null,ys(e,n,h,7));break;case 5:var x=null;switch(de.tag){case 26:x=de.memoizedState;case 5:case 27:var R=de;if(x?w_(x):R.stateNode.complete){Pe=0,ri=null;var B=R.sibling;if(B!==null)de=B;else{var et=R.return;et!==null?(de=et,$l(et)):de=null}break e}}Pe=0,ri=null,ys(e,n,h,5);break;case 6:Pe=0,ri=null,ys(e,n,h,6);break;case 8:If(),on=6;break t;default:throw Error(r(462))}}uS();break}catch(dt){Bg(e,dt)}while(!0);return aa=Tr=null,I.H=o,I.A=c,we=a,de!==null?0:(Xe=null,ge=0,vl(),on)}function uS(){for(;de!==null&&!rn();)kg(de)}function kg(e){var n=dg(e.alternate,e,pa);e.memoizedProps=e.pendingProps,n===null?$l(e):de=n}function Xg(e){var n=e,a=n.alternate;switch(n.tag){case 15:case 0:n=og(a,n,n.pendingProps,n.type,void 0,ge);break;case 11:n=og(a,n,n.pendingProps,n.type.render,n.ref,ge);break;case 5:Jc(n);default:mg(a,n),n=de=Vp(n,pa),n=dg(a,n,pa)}e.memoizedProps=e.pendingProps,n===null?$l(e):de=n}function ys(e,n,a,o){aa=Tr=null,Jc(n),cs=null,go=0;var c=n.return;try{if(Jx(e,c,n,a,ge)){on=1,Hl(e,pi(a,e.current)),de=null;return}}catch(h){if(c!==null)throw de=c,h;on=1,Hl(e,pi(a,e.current)),de=null;return}n.flags&32768?(Me||o===1?e=!0:_s||(ge&536870912)!==0?e=!1:(Xa=e=!0,(o===2||o===9||o===3||o===6)&&(o=ii.current,o!==null&&o.tag===13&&(o.flags|=16384))),Wg(n,e)):$l(n)}function $l(e){var n=e;do{if((n.flags&32768)!==0){Wg(n,Xa);return}e=n.return;var a=tS(n.alternate,n,pa);if(a!==null){de=a;return}if(n=n.sibling,n!==null){de=n;return}de=n=e}while(n!==null);on===0&&(on=5)}function Wg(e,n){do{var a=eS(e.alternate,e);if(a!==null){a.flags&=32767,de=a;return}if(a=e.return,a!==null&&(a.flags|=32768,a.subtreeFlags=0,a.deletions=null),!n&&(e=e.sibling,e!==null)){de=e;return}de=e=a}while(e!==null);on=6,de=null}function qg(e,n,a,o,c,h,x,R,B){e.cancelPendingCommit=null;do tu();while(xn!==0);if((we&6)!==0)throw Error(r(327));if(n!==null){if(n===e.current)throw Error(r(177));if(h=n.lanes|n.childLanes,h|=bc,Ke(e,a,h,x,R,B),e===Xe&&(de=Xe=null,ge=0),xs=n,Ya=e,ma=a,Nf=h,Of=c,Pg=o,(n.subtreeFlags&10256)!==0||(n.flags&10256)!==0?(e.callbackNode=null,e.callbackPriority=0,dS(Q,function(){return Jg(),null})):(e.callbackNode=null,e.callbackPriority=0),o=(n.flags&13878)!==0,(n.subtreeFlags&13878)!==0||o){o=I.T,I.T=null,c=H.p,H.p=2,x=we,we|=4;try{nS(e,n,a)}finally{we=x,H.p=c,I.T=o}}xn=1,Yg(),Zg(),Kg()}}function Yg(){if(xn===1){xn=0;var e=Ya,n=xs,a=(n.flags&13878)!==0;if((n.subtreeFlags&13878)!==0||a){a=I.T,I.T=null;var o=H.p;H.p=2;var c=we;we|=4;try{Rg(n,e);var h=Kf,x=Np(e.containerInfo),R=h.focusedElem,B=h.selectionRange;if(x!==R&&R&&R.ownerDocument&&Lp(R.ownerDocument.documentElement,R)){if(B!==null&&xc(R)){var et=B.start,dt=B.end;if(dt===void 0&&(dt=et),"selectionStart"in R)R.selectionStart=et,R.selectionEnd=Math.min(dt,R.value.length);else{var vt=R.ownerDocument||document,ot=vt&&vt.defaultView||window;if(ot.getSelection){var lt=ot.getSelection(),Xt=R.textContent.length,$t=Math.min(B.start,Xt),Ge=B.end===void 0?$t:Math.min(B.end,Xt);!lt.extend&&$t>Ge&&(x=Ge,Ge=$t,$t=x);var Y=Up(R,$t),V=Up(R,Ge);if(Y&&V&&(lt.rangeCount!==1||lt.anchorNode!==Y.node||lt.anchorOffset!==Y.offset||lt.focusNode!==V.node||lt.focusOffset!==V.offset)){var tt=vt.createRange();tt.setStart(Y.node,Y.offset),lt.removeAllRanges(),$t>Ge?(lt.addRange(tt),lt.extend(V.node,V.offset)):(tt.setEnd(V.node,V.offset),lt.addRange(tt))}}}}for(vt=[],lt=R;lt=lt.parentNode;)lt.nodeType===1&&vt.push({element:lt,left:lt.scrollLeft,top:lt.scrollTop});for(typeof R.focus=="function"&&R.focus(),R=0;R<vt.length;R++){var _t=vt[R];_t.element.scrollLeft=_t.left,_t.element.scrollTop=_t.top}}hu=!!Zf,Kf=Zf=null}finally{we=c,H.p=o,I.T=a}}e.current=n,xn=2}}function Zg(){if(xn===2){xn=0;var e=Ya,n=xs,a=(n.flags&8772)!==0;if((n.subtreeFlags&8772)!==0||a){a=I.T,I.T=null;var o=H.p;H.p=2;var c=we;we|=4;try{Mg(e,n.alternate,n)}finally{we=c,H.p=o,I.T=a}}xn=3}}function Kg(){if(xn===4||xn===3){xn=0,W();var e=Ya,n=xs,a=ma,o=Pg;(n.subtreeFlags&10256)!==0||(n.flags&10256)!==0?xn=5:(xn=0,xs=Ya=null,Qg(e,e.pendingLanes));var c=e.pendingLanes;if(c===0&&(qa=null),to(a),n=n.stateNode,ft&&typeof ft.onCommitFiberRoot=="function")try{ft.onCommitFiberRoot(ut,n,void 0,(n.current.flags&128)===128)}catch{}if(o!==null){n=I.T,c=H.p,H.p=2,I.T=null;try{for(var h=e.onRecoverableError,x=0;x<o.length;x++){var R=o[x];h(R.value,{componentStack:R.stack})}}finally{I.T=n,H.p=c}}(ma&3)!==0&&tu(),Gi(e),c=e.pendingLanes,(a&261930)!==0&&(c&42)!==0?e===Pf?No++:(No=0,Pf=e):No=0,Oo(0)}}function Qg(e,n){(e.pooledCacheLanes&=n)===0&&(n=e.pooledCache,n!=null&&(e.pooledCache=null,po(n)))}function tu(){return Yg(),Zg(),Kg(),Jg()}function Jg(){if(xn!==5)return!1;var e=Ya,n=Nf;Nf=0;var a=to(ma),o=I.T,c=H.p;try{H.p=32>a?32:a,I.T=null,a=Of,Of=null;var h=Ya,x=ma;if(xn=0,xs=Ya=null,ma=0,(we&6)!==0)throw Error(r(331));var R=we;if(we|=4,Lg(h.current),wg(h,h.current,x,a),we=R,Oo(0,!1),ft&&typeof ft.onPostCommitFiberRoot=="function")try{ft.onPostCommitFiberRoot(ut,h)}catch{}return!0}finally{H.p=c,I.T=o,Qg(e,n)}}function jg(e,n,a){n=pi(a,n),n=df(e.stateNode,n,2),e=Ha(e,n,2),e!==null&&(Gt(e,2),Gi(e))}function Ie(e,n,a){if(e.tag===3)jg(e,e,a);else for(;n!==null;){if(n.tag===3){jg(n,e,a);break}else if(n.tag===1){var o=n.stateNode;if(typeof n.type.getDerivedStateFromError=="function"||typeof o.componentDidCatch=="function"&&(qa===null||!qa.has(o))){e=pi(a,e),a=$m(2),o=Ha(n,a,2),o!==null&&(tg(a,o,n,e),Gt(o,2),Gi(o));break}}n=n.return}}function zf(e,n,a){var o=e.pingCache;if(o===null){o=e.pingCache=new rS;var c=new Set;o.set(n,c)}else c=o.get(n),c===void 0&&(c=new Set,o.set(n,c));c.has(a)||(Df=!0,c.add(a),e=cS.bind(null,e,n,a),n.then(e,e))}function cS(e,n,a){var o=e.pingCache;o!==null&&o.delete(n),e.pingedLanes|=e.suspendedLanes&a,e.warmLanes&=~a,Xe===e&&(ge&a)===a&&(on===4||on===3&&(ge&62914560)===ge&&300>ze()-Zl?(we&2)===0&&Ss(e,0):Uf|=a,vs===ge&&(vs=0)),Gi(e)}function $g(e,n){n===0&&(n=St()),e=Mr(e,n),e!==null&&(Gt(e,n),Gi(e))}function fS(e){var n=e.memoizedState,a=0;n!==null&&(a=n.retryLane),$g(e,a)}function hS(e,n){var a=0;switch(e.tag){case 31:case 13:var o=e.stateNode,c=e.memoizedState;c!==null&&(a=c.retryLane);break;case 19:o=e.stateNode;break;case 22:o=e.stateNode._retryCache;break;default:throw Error(r(314))}o!==null&&o.delete(n),$g(e,a)}function dS(e,n){return ln(e,n)}var eu=null,Ms=null,Bf=!1,nu=!1,Hf=!1,Ka=0;function Gi(e){e!==Ms&&e.next===null&&(Ms===null?eu=Ms=e:Ms=Ms.next=e),nu=!0,Bf||(Bf=!0,mS())}function Oo(e,n){if(!Hf&&nu){Hf=!0;do for(var a=!1,o=eu;o!==null;){if(e!==0){var c=o.pendingLanes;if(c===0)var h=0;else{var x=o.suspendedLanes,R=o.pingedLanes;h=(1<<31-Ft(42|e)+1)-1,h&=c&~(x&~R),h=h&201326741?h&201326741|1:h?h|2:0}h!==0&&(a=!0,i_(o,h))}else h=ge,h=pt(o,o===Xe?h:0,o.cancelPendingCommit!==null||o.timeoutHandle!==-1),(h&3)===0||Ct(o,h)||(a=!0,i_(o,h));o=o.next}while(a);Hf=!1}}function pS(){t_()}function t_(){nu=Bf=!1;var e=0;Ka!==0&&TS()&&(e=Ka);for(var n=ze(),a=null,o=eu;o!==null;){var c=o.next,h=e_(o,n);h===0?(o.next=null,a===null?eu=c:a.next=c,c===null&&(Ms=a)):(a=o,(e!==0||(h&3)!==0)&&(nu=!0)),o=c}xn!==0&&xn!==5||Oo(e),Ka!==0&&(Ka=0)}function e_(e,n){for(var a=e.suspendedLanes,o=e.pingedLanes,c=e.expirationTimes,h=e.pendingLanes&-62914561;0<h;){var x=31-Ft(h),R=1<<x,B=c[x];B===-1?((R&a)===0||(R&o)!==0)&&(c[x]=It(R,n)):B<=n&&(e.expiredLanes|=R),h&=~R}if(n=Xe,a=ge,a=pt(e,e===n?a:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),o=e.callbackNode,a===0||e===n&&(Pe===2||Pe===9)||e.cancelPendingCommit!==null)return o!==null&&o!==null&&We(o),e.callbackNode=null,e.callbackPriority=0;if((a&3)===0||Ct(e,a)){if(n=a&-a,n===e.callbackPriority)return n;switch(o!==null&&We(o),to(a)){case 2:case 8:a=y;break;case 32:a=Q;break;case 268435456:a=ct;break;default:a=Q}return o=n_.bind(null,e),a=ln(a,o),e.callbackPriority=n,e.callbackNode=a,n}return o!==null&&o!==null&&We(o),e.callbackPriority=2,e.callbackNode=null,2}function n_(e,n){if(xn!==0&&xn!==5)return e.callbackNode=null,e.callbackPriority=0,null;var a=e.callbackNode;if(tu()&&e.callbackNode!==a)return null;var o=ge;return o=pt(e,e===Xe?o:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),o===0?null:(Fg(e,o,n),e_(e,ze()),e.callbackNode!=null&&e.callbackNode===a?n_.bind(null,e):null)}function i_(e,n){if(tu())return null;Fg(e,n,!0)}function mS(){RS(function(){(we&6)!==0?ln(U,pS):t_()})}function Gf(){if(Ka===0){var e=os;e===0&&(e=Qt,Qt<<=1,(Qt&261888)===0&&(Qt=256)),Ka=e}return Ka}function a_(e){return e==null||typeof e=="symbol"||typeof e=="boolean"?null:typeof e=="function"?e:vr(""+e)}function r_(e,n){var a=n.ownerDocument.createElement("input");return a.name=n.name,a.value=n.value,e.id&&a.setAttribute("form",e.id),n.parentNode.insertBefore(a,n),e=new FormData(e),a.parentNode.removeChild(a),e}function gS(e,n,a,o,c){if(n==="submit"&&a&&a.stateNode===c){var h=a_((c[Tn]||null).action),x=o.submitter;x&&(n=(n=x[Tn]||null)?a_(n.formAction):x.getAttribute("formAction"),n!==null&&(h=n,x=null));var R=new pl("action","action",null,o,c);e.push({event:R,listeners:[{instance:null,listener:function(){if(o.defaultPrevented){if(Ka!==0){var B=x?r_(c,x):new FormData(c);of(a,{pending:!0,data:B,method:c.method,action:h},null,B)}}else typeof h=="function"&&(R.preventDefault(),B=x?r_(c,x):new FormData(c),of(a,{pending:!0,data:B,method:c.method,action:h},h,B))},currentTarget:c}]})}}for(var Vf=0;Vf<Ec.length;Vf++){var kf=Ec[Vf],_S=kf.toLowerCase(),vS=kf[0].toUpperCase()+kf.slice(1);Ai(_S,"on"+vS)}Ai(Ip,"onAnimationEnd"),Ai(Fp,"onAnimationIteration"),Ai(zp,"onAnimationStart"),Ai("dblclick","onDoubleClick"),Ai("focusin","onFocus"),Ai("focusout","onBlur"),Ai(Ox,"onTransitionRun"),Ai(Px,"onTransitionStart"),Ai(Ix,"onTransitionCancel"),Ai(Bp,"onTransitionEnd"),st("onMouseEnter",["mouseout","mouseover"]),st("onMouseLeave",["mouseout","mouseover"]),st("onPointerEnter",["pointerout","pointerover"]),st("onPointerLeave",["pointerout","pointerover"]),X("onChange","change click focusin focusout input keydown keyup selectionchange".split(" ")),X("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")),X("onBeforeInput",["compositionend","keypress","textInput","paste"]),X("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" ")),X("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" ")),X("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var Po="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),xS=new Set("beforetoggle cancel close invalid load scroll scrollend toggle".split(" ").concat(Po));function s_(e,n){n=(n&4)!==0;for(var a=0;a<e.length;a++){var o=e[a],c=o.event;o=o.listeners;t:{var h=void 0;if(n)for(var x=o.length-1;0<=x;x--){var R=o[x],B=R.instance,et=R.currentTarget;if(R=R.listener,B!==h&&c.isPropagationStopped())break t;h=R,c.currentTarget=et;try{h(c)}catch(dt){_l(dt)}c.currentTarget=null,h=B}else for(x=0;x<o.length;x++){if(R=o[x],B=R.instance,et=R.currentTarget,R=R.listener,B!==h&&c.isPropagationStopped())break t;h=R,c.currentTarget=et;try{h(c)}catch(dt){_l(dt)}c.currentTarget=null,h=B}}}}function pe(e,n){var a=n[mr];a===void 0&&(a=n[mr]=new Set);var o=e+"__bubble";a.has(o)||(o_(n,e,2,!1),a.add(o))}function Xf(e,n,a){var o=0;n&&(o|=4),o_(a,e,o,n)}var iu="_reactListening"+Math.random().toString(36).slice(2);function Wf(e){if(!e[iu]){e[iu]=!0,cl.forEach(function(a){a!=="selectionchange"&&(xS.has(a)||Xf(a,!1,e),Xf(a,!0,e))});var n=e.nodeType===9?e:e.ownerDocument;n===null||n[iu]||(n[iu]=!0,Xf("selectionchange",!1,n))}}function o_(e,n,a,o){switch(I_(n)){case 2:var c=YS;break;case 8:c=ZS;break;default:c=sh}a=c.bind(null,n,a,e),c=void 0,!cc||n!=="touchstart"&&n!=="touchmove"&&n!=="wheel"||(c=!0),o?c!==void 0?e.addEventListener(n,a,{capture:!0,passive:c}):e.addEventListener(n,a,!0):c!==void 0?e.addEventListener(n,a,{passive:c}):e.addEventListener(n,a,!1)}function qf(e,n,a,o,c){var h=o;if((n&1)===0&&(n&2)===0&&o!==null)t:for(;;){if(o===null)return;var x=o.tag;if(x===3||x===4){var R=o.stateNode.containerInfo;if(R===c)break;if(x===4)for(x=o.return;x!==null;){var B=x.tag;if((B===3||B===4)&&x.stateNode.containerInfo===c)return;x=x.return}for(;R!==null;){if(x=ji(R),x===null)return;if(B=x.tag,B===5||B===6||B===26||B===27){o=h=x;continue t}R=R.parentNode}}o=o.return}hp(function(){var et=h,dt=lc(a),vt=[];t:{var ot=Hp.get(e);if(ot!==void 0){var lt=pl,Xt=e;switch(e){case"keypress":if(hl(a)===0)break t;case"keydown":case"keyup":lt=hx;break;case"focusin":Xt="focus",lt=pc;break;case"focusout":Xt="blur",lt=pc;break;case"beforeblur":case"afterblur":lt=pc;break;case"click":if(a.button===2)break t;case"auxclick":case"dblclick":case"mousedown":case"mousemove":case"mouseup":case"mouseout":case"mouseover":case"contextmenu":lt=mp;break;case"drag":case"dragend":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"dragstart":case"drop":lt=tx;break;case"touchcancel":case"touchend":case"touchmove":case"touchstart":lt=mx;break;case Ip:case Fp:case zp:lt=ix;break;case Bp:lt=_x;break;case"scroll":case"scrollend":lt=jv;break;case"wheel":lt=xx;break;case"copy":case"cut":case"paste":lt=rx;break;case"gotpointercapture":case"lostpointercapture":case"pointercancel":case"pointerdown":case"pointermove":case"pointerout":case"pointerover":case"pointerup":lt=_p;break;case"toggle":case"beforetoggle":lt=yx}var $t=(n&4)!==0,Ge=!$t&&(e==="scroll"||e==="scrollend"),Y=$t?ot!==null?ot+"Capture":null:ot;$t=[];for(var V=et,tt;V!==null;){var _t=V;if(tt=_t.stateNode,_t=_t.tag,_t!==5&&_t!==26&&_t!==27||tt===null||Y===null||(_t=no(V,Y),_t!=null&&$t.push(Io(V,_t,tt))),Ge)break;V=V.return}0<$t.length&&(ot=new lt(ot,Xt,null,a,dt),vt.push({event:ot,listeners:$t}))}}if((n&7)===0){t:{if(ot=e==="mouseover"||e==="pointerover",lt=e==="mouseout"||e==="pointerout",ot&&a!==oc&&(Xt=a.relatedTarget||a.fromElement)&&(ji(Xt)||Xt[Gn]))break t;if((lt||ot)&&(ot=dt.window===dt?dt:(ot=dt.ownerDocument)?ot.defaultView||ot.parentWindow:window,lt?(Xt=a.relatedTarget||a.toElement,lt=et,Xt=Xt?ji(Xt):null,Xt!==null&&(Ge=u(Xt),$t=Xt.tag,Xt!==Ge||$t!==5&&$t!==27&&$t!==6)&&(Xt=null)):(lt=null,Xt=et),lt!==Xt)){if($t=mp,_t="onMouseLeave",Y="onMouseEnter",V="mouse",(e==="pointerout"||e==="pointerover")&&($t=_p,_t="onPointerLeave",Y="onPointerEnter",V="pointer"),Ge=lt==null?ot:_r(lt),tt=Xt==null?ot:_r(Xt),ot=new $t(_t,V+"leave",lt,a,dt),ot.target=Ge,ot.relatedTarget=tt,_t=null,ji(dt)===et&&($t=new $t(Y,V+"enter",Xt,a,dt),$t.target=tt,$t.relatedTarget=Ge,_t=$t),Ge=_t,lt&&Xt)e:{for($t=SS,Y=lt,V=Xt,tt=0,_t=Y;_t;_t=$t(_t))tt++;_t=0;for(var jt=V;jt;jt=$t(jt))_t++;for(;0<tt-_t;)Y=$t(Y),tt--;for(;0<_t-tt;)V=$t(V),_t--;for(;tt--;){if(Y===V||V!==null&&Y===V.alternate){$t=Y;break e}Y=$t(Y),V=$t(V)}$t=null}else $t=null;lt!==null&&l_(vt,ot,lt,$t,!1),Xt!==null&&Ge!==null&&l_(vt,Ge,Xt,$t,!0)}}t:{if(ot=et?_r(et):window,lt=ot.nodeName&&ot.nodeName.toLowerCase(),lt==="select"||lt==="input"&&ot.type==="file")var Ae=Tp;else if(Ep(ot))if(Ap)Ae=Ux;else{Ae=wx;var qt=Cx}else lt=ot.nodeName,!lt||lt.toLowerCase()!=="input"||ot.type!=="checkbox"&&ot.type!=="radio"?et&&De(et.elementType)&&(Ae=Tp):Ae=Dx;if(Ae&&(Ae=Ae(e,et))){bp(vt,Ae,a,dt);break t}qt&&qt(e,ot,et),e==="focusout"&&et&&ot.type==="number"&&et.memoizedProps.value!=null&&he(ot,"number",ot.value)}switch(qt=et?_r(et):window,e){case"focusin":(Ep(qt)||qt.contentEditable==="true")&&($r=qt,Sc=et,co=null);break;case"focusout":co=Sc=$r=null;break;case"mousedown":yc=!0;break;case"contextmenu":case"mouseup":case"dragend":yc=!1,Op(vt,a,dt);break;case"selectionchange":if(Nx)break;case"keydown":case"keyup":Op(vt,a,dt)}var le;if(gc)t:{switch(e){case"compositionstart":var _e="onCompositionStart";break t;case"compositionend":_e="onCompositionEnd";break t;case"compositionupdate":_e="onCompositionUpdate";break t}_e=void 0}else jr?yp(e,a)&&(_e="onCompositionEnd"):e==="keydown"&&a.keyCode===229&&(_e="onCompositionStart");_e&&(vp&&a.locale!=="ko"&&(jr||_e!=="onCompositionStart"?_e==="onCompositionEnd"&&jr&&(le=dp()):(Na=dt,fc="value"in Na?Na.value:Na.textContent,jr=!0)),qt=au(et,_e),0<qt.length&&(_e=new gp(_e,e,null,a,dt),vt.push({event:_e,listeners:qt}),le?_e.data=le:(le=Mp(a),le!==null&&(_e.data=le)))),(le=Ex?bx(e,a):Tx(e,a))&&(_e=au(et,"onBeforeInput"),0<_e.length&&(qt=new gp("onBeforeInput","beforeinput",null,a,dt),vt.push({event:qt,listeners:_e}),qt.data=le)),gS(vt,e,et,a,dt)}s_(vt,n)})}function Io(e,n,a){return{instance:e,listener:n,currentTarget:a}}function au(e,n){for(var a=n+"Capture",o=[];e!==null;){var c=e,h=c.stateNode;if(c=c.tag,c!==5&&c!==26&&c!==27||h===null||(c=no(e,a),c!=null&&o.unshift(Io(e,c,h)),c=no(e,n),c!=null&&o.push(Io(e,c,h))),e.tag===3)return o;e=e.return}return[]}function SS(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function l_(e,n,a,o,c){for(var h=n._reactName,x=[];a!==null&&a!==o;){var R=a,B=R.alternate,et=R.stateNode;if(R=R.tag,B!==null&&B===o)break;R!==5&&R!==26&&R!==27||et===null||(B=et,c?(et=no(a,h),et!=null&&x.unshift(Io(a,et,B))):c||(et=no(a,h),et!=null&&x.push(Io(a,et,B)))),a=a.return}x.length!==0&&e.push({event:n,listeners:x})}var yS=/\r\n?/g,MS=/\u0000|\uFFFD/g;function u_(e){return(typeof e=="string"?e:""+e).replace(yS,`
`).replace(MS,"")}function c_(e,n){return n=u_(n),u_(e)===n}function He(e,n,a,o,c,h){switch(a){case"children":typeof o=="string"?n==="body"||n==="textarea"&&o===""||ti(e,o):(typeof o=="number"||typeof o=="bigint")&&n!=="body"&&ti(e,""+o);break;case"className":kt(e,"class",o);break;case"tabIndex":kt(e,"tabindex",o);break;case"dir":case"role":case"viewBox":case"width":case"height":kt(e,a,o);break;case"style":Ti(e,o,h);break;case"data":if(n!=="object"){kt(e,"data",o);break}case"src":case"href":if(o===""&&(n!=="a"||a!=="href")){e.removeAttribute(a);break}if(o==null||typeof o=="function"||typeof o=="symbol"||typeof o=="boolean"){e.removeAttribute(a);break}o=vr(""+o),e.setAttribute(a,o);break;case"action":case"formAction":if(typeof o=="function"){e.setAttribute(a,"javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')");break}else typeof h=="function"&&(a==="formAction"?(n!=="input"&&He(e,n,"name",c.name,c,null),He(e,n,"formEncType",c.formEncType,c,null),He(e,n,"formMethod",c.formMethod,c,null),He(e,n,"formTarget",c.formTarget,c,null)):(He(e,n,"encType",c.encType,c,null),He(e,n,"method",c.method,c,null),He(e,n,"target",c.target,c,null)));if(o==null||typeof o=="symbol"||typeof o=="boolean"){e.removeAttribute(a);break}o=vr(""+o),e.setAttribute(a,o);break;case"onClick":o!=null&&(e.onclick=ta);break;case"onScroll":o!=null&&pe("scroll",e);break;case"onScrollEnd":o!=null&&pe("scrollend",e);break;case"dangerouslySetInnerHTML":if(o!=null){if(typeof o!="object"||!("__html"in o))throw Error(r(61));if(a=o.__html,a!=null){if(c.children!=null)throw Error(r(60));e.innerHTML=a}}break;case"multiple":e.multiple=o&&typeof o!="function"&&typeof o!="symbol";break;case"muted":e.muted=o&&typeof o!="function"&&typeof o!="symbol";break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"defaultValue":case"defaultChecked":case"innerHTML":case"ref":break;case"autoFocus":break;case"xlinkHref":if(o==null||typeof o=="function"||typeof o=="boolean"||typeof o=="symbol"){e.removeAttribute("xlink:href");break}a=vr(""+o),e.setAttributeNS("http://www.w3.org/1999/xlink","xlink:href",a);break;case"contentEditable":case"spellCheck":case"draggable":case"value":case"autoReverse":case"externalResourcesRequired":case"focusable":case"preserveAlpha":o!=null&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(a,""+o):e.removeAttribute(a);break;case"inert":case"allowFullScreen":case"async":case"autoPlay":case"controls":case"default":case"defer":case"disabled":case"disablePictureInPicture":case"disableRemotePlayback":case"formNoValidate":case"hidden":case"loop":case"noModule":case"noValidate":case"open":case"playsInline":case"readOnly":case"required":case"reversed":case"scoped":case"seamless":case"itemScope":o&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(a,""):e.removeAttribute(a);break;case"capture":case"download":o===!0?e.setAttribute(a,""):o!==!1&&o!=null&&typeof o!="function"&&typeof o!="symbol"?e.setAttribute(a,o):e.removeAttribute(a);break;case"cols":case"rows":case"size":case"span":o!=null&&typeof o!="function"&&typeof o!="symbol"&&!isNaN(o)&&1<=o?e.setAttribute(a,o):e.removeAttribute(a);break;case"rowSpan":case"start":o==null||typeof o=="function"||typeof o=="symbol"||isNaN(o)?e.removeAttribute(a):e.setAttribute(a,o);break;case"popover":pe("beforetoggle",e),pe("toggle",e),Ut(e,"popover",o);break;case"xlinkActuate":Vt(e,"http://www.w3.org/1999/xlink","xlink:actuate",o);break;case"xlinkArcrole":Vt(e,"http://www.w3.org/1999/xlink","xlink:arcrole",o);break;case"xlinkRole":Vt(e,"http://www.w3.org/1999/xlink","xlink:role",o);break;case"xlinkShow":Vt(e,"http://www.w3.org/1999/xlink","xlink:show",o);break;case"xlinkTitle":Vt(e,"http://www.w3.org/1999/xlink","xlink:title",o);break;case"xlinkType":Vt(e,"http://www.w3.org/1999/xlink","xlink:type",o);break;case"xmlBase":Vt(e,"http://www.w3.org/XML/1998/namespace","xml:base",o);break;case"xmlLang":Vt(e,"http://www.w3.org/XML/1998/namespace","xml:lang",o);break;case"xmlSpace":Vt(e,"http://www.w3.org/XML/1998/namespace","xml:space",o);break;case"is":Ut(e,"is",o);break;case"innerText":case"textContent":break;default:(!(2<a.length)||a[0]!=="o"&&a[0]!=="O"||a[1]!=="n"&&a[1]!=="N")&&(a=Fi.get(a)||a,Ut(e,a,o))}}function Yf(e,n,a,o,c,h){switch(a){case"style":Ti(e,o,h);break;case"dangerouslySetInnerHTML":if(o!=null){if(typeof o!="object"||!("__html"in o))throw Error(r(61));if(a=o.__html,a!=null){if(c.children!=null)throw Error(r(60));e.innerHTML=a}}break;case"children":typeof o=="string"?ti(e,o):(typeof o=="number"||typeof o=="bigint")&&ti(e,""+o);break;case"onScroll":o!=null&&pe("scroll",e);break;case"onScrollEnd":o!=null&&pe("scrollend",e);break;case"onClick":o!=null&&(e.onclick=ta);break;case"suppressContentEditableWarning":case"suppressHydrationWarning":case"innerHTML":case"ref":break;case"innerText":case"textContent":break;default:if(!A.hasOwnProperty(a))t:{if(a[0]==="o"&&a[1]==="n"&&(c=a.endsWith("Capture"),n=a.slice(2,c?a.length-7:void 0),h=e[Tn]||null,h=h!=null?h[a]:null,typeof h=="function"&&e.removeEventListener(n,h,c),typeof o=="function")){typeof h!="function"&&h!==null&&(a in e?e[a]=null:e.hasAttribute(a)&&e.removeAttribute(a)),e.addEventListener(n,o,c);break t}a in e?e[a]=o:o===!0?e.setAttribute(a,""):Ut(e,a,o)}}}function wn(e,n,a){switch(n){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"img":pe("error",e),pe("load",e);var o=!1,c=!1,h;for(h in a)if(a.hasOwnProperty(h)){var x=a[h];if(x!=null)switch(h){case"src":o=!0;break;case"srcSet":c=!0;break;case"children":case"dangerouslySetInnerHTML":throw Error(r(137,n));default:He(e,n,h,x,a,null)}}c&&He(e,n,"srcSet",a.srcSet,a,null),o&&He(e,n,"src",a.src,a,null);return;case"input":pe("invalid",e);var R=h=x=c=null,B=null,et=null;for(o in a)if(a.hasOwnProperty(o)){var dt=a[o];if(dt!=null)switch(o){case"name":c=dt;break;case"type":x=dt;break;case"checked":B=dt;break;case"defaultChecked":et=dt;break;case"value":h=dt;break;case"defaultValue":R=dt;break;case"children":case"dangerouslySetInnerHTML":if(dt!=null)throw Error(r(137,n));break;default:He(e,n,o,dt,a,null)}}Ln(e,h,R,B,et,x,c,!1);return;case"select":pe("invalid",e),o=x=h=null;for(c in a)if(a.hasOwnProperty(c)&&(R=a[c],R!=null))switch(c){case"value":h=R;break;case"defaultValue":x=R;break;case"multiple":o=R;default:He(e,n,c,R,a,null)}n=h,a=x,e.multiple=!!o,n!=null?vn(e,!!o,n,!1):a!=null&&vn(e,!!o,a,!0);return;case"textarea":pe("invalid",e),h=c=o=null;for(x in a)if(a.hasOwnProperty(x)&&(R=a[x],R!=null))switch(x){case"value":o=R;break;case"defaultValue":c=R;break;case"children":h=R;break;case"dangerouslySetInnerHTML":if(R!=null)throw Error(r(91));break;default:He(e,n,x,R,a,null)}bi(e,o,c,h);return;case"option":for(B in a)a.hasOwnProperty(B)&&(o=a[B],o!=null)&&(B==="selected"?e.selected=o&&typeof o!="function"&&typeof o!="symbol":He(e,n,B,o,a,null));return;case"dialog":pe("beforetoggle",e),pe("toggle",e),pe("cancel",e),pe("close",e);break;case"iframe":case"object":pe("load",e);break;case"video":case"audio":for(o=0;o<Po.length;o++)pe(Po[o],e);break;case"image":pe("error",e),pe("load",e);break;case"details":pe("toggle",e);break;case"embed":case"source":case"link":pe("error",e),pe("load",e);case"area":case"base":case"br":case"col":case"hr":case"keygen":case"meta":case"param":case"track":case"wbr":case"menuitem":for(et in a)if(a.hasOwnProperty(et)&&(o=a[et],o!=null))switch(et){case"children":case"dangerouslySetInnerHTML":throw Error(r(137,n));default:He(e,n,et,o,a,null)}return;default:if(De(n)){for(dt in a)a.hasOwnProperty(dt)&&(o=a[dt],o!==void 0&&Yf(e,n,dt,o,a,void 0));return}}for(R in a)a.hasOwnProperty(R)&&(o=a[R],o!=null&&He(e,n,R,o,a,null))}function ES(e,n,a,o){switch(n){case"div":case"span":case"svg":case"path":case"a":case"g":case"p":case"li":break;case"input":var c=null,h=null,x=null,R=null,B=null,et=null,dt=null;for(lt in a){var vt=a[lt];if(a.hasOwnProperty(lt)&&vt!=null)switch(lt){case"checked":break;case"value":break;case"defaultValue":B=vt;default:o.hasOwnProperty(lt)||He(e,n,lt,null,o,vt)}}for(var ot in o){var lt=o[ot];if(vt=a[ot],o.hasOwnProperty(ot)&&(lt!=null||vt!=null))switch(ot){case"type":h=lt;break;case"name":c=lt;break;case"checked":et=lt;break;case"defaultChecked":dt=lt;break;case"value":x=lt;break;case"defaultValue":R=lt;break;case"children":case"dangerouslySetInnerHTML":if(lt!=null)throw Error(r(137,n));break;default:lt!==vt&&He(e,n,ot,lt,o,vt)}}zt(e,x,R,B,et,dt,h,c);return;case"select":lt=x=R=ot=null;for(h in a)if(B=a[h],a.hasOwnProperty(h)&&B!=null)switch(h){case"value":break;case"multiple":lt=B;default:o.hasOwnProperty(h)||He(e,n,h,null,o,B)}for(c in o)if(h=o[c],B=a[c],o.hasOwnProperty(c)&&(h!=null||B!=null))switch(c){case"value":ot=h;break;case"defaultValue":R=h;break;case"multiple":x=h;default:h!==B&&He(e,n,c,h,o,B)}n=R,a=x,o=lt,ot!=null?vn(e,!!a,ot,!1):!!o!=!!a&&(n!=null?vn(e,!!a,n,!0):vn(e,!!a,a?[]:"",!1));return;case"textarea":lt=ot=null;for(R in a)if(c=a[R],a.hasOwnProperty(R)&&c!=null&&!o.hasOwnProperty(R))switch(R){case"value":break;case"children":break;default:He(e,n,R,null,o,c)}for(x in o)if(c=o[x],h=a[x],o.hasOwnProperty(x)&&(c!=null||h!=null))switch(x){case"value":ot=c;break;case"defaultValue":lt=c;break;case"children":break;case"dangerouslySetInnerHTML":if(c!=null)throw Error(r(91));break;default:c!==h&&He(e,n,x,c,o,h)}$n(e,ot,lt);return;case"option":for(var Xt in a)ot=a[Xt],a.hasOwnProperty(Xt)&&ot!=null&&!o.hasOwnProperty(Xt)&&(Xt==="selected"?e.selected=!1:He(e,n,Xt,null,o,ot));for(B in o)ot=o[B],lt=a[B],o.hasOwnProperty(B)&&ot!==lt&&(ot!=null||lt!=null)&&(B==="selected"?e.selected=ot&&typeof ot!="function"&&typeof ot!="symbol":He(e,n,B,ot,o,lt));return;case"img":case"link":case"area":case"base":case"br":case"col":case"embed":case"hr":case"keygen":case"meta":case"param":case"source":case"track":case"wbr":case"menuitem":for(var $t in a)ot=a[$t],a.hasOwnProperty($t)&&ot!=null&&!o.hasOwnProperty($t)&&He(e,n,$t,null,o,ot);for(et in o)if(ot=o[et],lt=a[et],o.hasOwnProperty(et)&&ot!==lt&&(ot!=null||lt!=null))switch(et){case"children":case"dangerouslySetInnerHTML":if(ot!=null)throw Error(r(137,n));break;default:He(e,n,et,ot,o,lt)}return;default:if(De(n)){for(var Ge in a)ot=a[Ge],a.hasOwnProperty(Ge)&&ot!==void 0&&!o.hasOwnProperty(Ge)&&Yf(e,n,Ge,void 0,o,ot);for(dt in o)ot=o[dt],lt=a[dt],!o.hasOwnProperty(dt)||ot===lt||ot===void 0&&lt===void 0||Yf(e,n,dt,ot,o,lt);return}}for(var Y in a)ot=a[Y],a.hasOwnProperty(Y)&&ot!=null&&!o.hasOwnProperty(Y)&&He(e,n,Y,null,o,ot);for(vt in o)ot=o[vt],lt=a[vt],!o.hasOwnProperty(vt)||ot===lt||ot==null&&lt==null||He(e,n,vt,ot,o,lt)}function f_(e){switch(e){case"css":case"script":case"font":case"img":case"image":case"input":case"link":return!0;default:return!1}}function bS(){if(typeof performance.getEntriesByType=="function"){for(var e=0,n=0,a=performance.getEntriesByType("resource"),o=0;o<a.length;o++){var c=a[o],h=c.transferSize,x=c.initiatorType,R=c.duration;if(h&&R&&f_(x)){for(x=0,R=c.responseEnd,o+=1;o<a.length;o++){var B=a[o],et=B.startTime;if(et>R)break;var dt=B.transferSize,vt=B.initiatorType;dt&&f_(vt)&&(B=B.responseEnd,x+=dt*(B<R?1:(R-et)/(B-et)))}if(--o,n+=8*(h+x)/(c.duration/1e3),e++,10<e)break}}if(0<e)return n/e/1e6}return navigator.connection&&(e=navigator.connection.downlink,typeof e=="number")?e:5}var Zf=null,Kf=null;function ru(e){return e.nodeType===9?e:e.ownerDocument}function h_(e){switch(e){case"http://www.w3.org/2000/svg":return 1;case"http://www.w3.org/1998/Math/MathML":return 2;default:return 0}}function d_(e,n){if(e===0)switch(n){case"svg":return 1;case"math":return 2;default:return 0}return e===1&&n==="foreignObject"?0:e}function Qf(e,n){return e==="textarea"||e==="noscript"||typeof n.children=="string"||typeof n.children=="number"||typeof n.children=="bigint"||typeof n.dangerouslySetInnerHTML=="object"&&n.dangerouslySetInnerHTML!==null&&n.dangerouslySetInnerHTML.__html!=null}var Jf=null;function TS(){var e=window.event;return e&&e.type==="popstate"?e===Jf?!1:(Jf=e,!0):(Jf=null,!1)}var p_=typeof setTimeout=="function"?setTimeout:void 0,AS=typeof clearTimeout=="function"?clearTimeout:void 0,m_=typeof Promise=="function"?Promise:void 0,RS=typeof queueMicrotask=="function"?queueMicrotask:typeof m_<"u"?function(e){return m_.resolve(null).then(e).catch(CS)}:p_;function CS(e){setTimeout(function(){throw e})}function Qa(e){return e==="head"}function g_(e,n){var a=n,o=0;do{var c=a.nextSibling;if(e.removeChild(a),c&&c.nodeType===8)if(a=c.data,a==="/$"||a==="/&"){if(o===0){e.removeChild(c),As(n);return}o--}else if(a==="$"||a==="$?"||a==="$~"||a==="$!"||a==="&")o++;else if(a==="html")Fo(e.ownerDocument.documentElement);else if(a==="head"){a=e.ownerDocument.head,Fo(a);for(var h=a.firstChild;h;){var x=h.nextSibling,R=h.nodeName;h[wa]||R==="SCRIPT"||R==="STYLE"||R==="LINK"&&h.rel.toLowerCase()==="stylesheet"||a.removeChild(h),h=x}}else a==="body"&&Fo(e.ownerDocument.body);a=c}while(a);As(n)}function __(e,n){var a=e;e=0;do{var o=a.nextSibling;if(a.nodeType===1?n?(a._stashedDisplay=a.style.display,a.style.display="none"):(a.style.display=a._stashedDisplay||"",a.getAttribute("style")===""&&a.removeAttribute("style")):a.nodeType===3&&(n?(a._stashedText=a.nodeValue,a.nodeValue=""):a.nodeValue=a._stashedText||""),o&&o.nodeType===8)if(a=o.data,a==="/$"){if(e===0)break;e--}else a!=="$"&&a!=="$?"&&a!=="$~"&&a!=="$!"||e++;a=o}while(a)}function jf(e){var n=e.firstChild;for(n&&n.nodeType===10&&(n=n.nextSibling);n;){var a=n;switch(n=n.nextSibling,a.nodeName){case"HTML":case"HEAD":case"BODY":jf(a),Da(a);continue;case"SCRIPT":case"STYLE":continue;case"LINK":if(a.rel.toLowerCase()==="stylesheet")continue}e.removeChild(a)}}function wS(e,n,a,o){for(;e.nodeType===1;){var c=a;if(e.nodeName.toLowerCase()!==n.toLowerCase()){if(!o&&(e.nodeName!=="INPUT"||e.type!=="hidden"))break}else if(o){if(!e[wa])switch(n){case"meta":if(!e.hasAttribute("itemprop"))break;return e;case"link":if(h=e.getAttribute("rel"),h==="stylesheet"&&e.hasAttribute("data-precedence"))break;if(h!==c.rel||e.getAttribute("href")!==(c.href==null||c.href===""?null:c.href)||e.getAttribute("crossorigin")!==(c.crossOrigin==null?null:c.crossOrigin)||e.getAttribute("title")!==(c.title==null?null:c.title))break;return e;case"style":if(e.hasAttribute("data-precedence"))break;return e;case"script":if(h=e.getAttribute("src"),(h!==(c.src==null?null:c.src)||e.getAttribute("type")!==(c.type==null?null:c.type)||e.getAttribute("crossorigin")!==(c.crossOrigin==null?null:c.crossOrigin))&&h&&e.hasAttribute("async")&&!e.hasAttribute("itemprop"))break;return e;default:return e}}else if(n==="input"&&e.type==="hidden"){var h=c.name==null?null:""+c.name;if(c.type==="hidden"&&e.getAttribute("name")===h)return e}else return e;if(e=xi(e.nextSibling),e===null)break}return null}function DS(e,n,a){if(n==="")return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!a||(e=xi(e.nextSibling),e===null))return null;return e}function v_(e,n){for(;e.nodeType!==8;)if((e.nodeType!==1||e.nodeName!=="INPUT"||e.type!=="hidden")&&!n||(e=xi(e.nextSibling),e===null))return null;return e}function $f(e){return e.data==="$?"||e.data==="$~"}function th(e){return e.data==="$!"||e.data==="$?"&&e.ownerDocument.readyState!=="loading"}function US(e,n){var a=e.ownerDocument;if(e.data==="$~")e._reactRetry=n;else if(e.data!=="$?"||a.readyState!=="loading")n();else{var o=function(){n(),a.removeEventListener("DOMContentLoaded",o)};a.addEventListener("DOMContentLoaded",o),e._reactRetry=o}}function xi(e){for(;e!=null;e=e.nextSibling){var n=e.nodeType;if(n===1||n===3)break;if(n===8){if(n=e.data,n==="$"||n==="$!"||n==="$?"||n==="$~"||n==="&"||n==="F!"||n==="F")break;if(n==="/$"||n==="/&")return null}}return e}var eh=null;function x_(e){e=e.nextSibling;for(var n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="/$"||a==="/&"){if(n===0)return xi(e.nextSibling);n--}else a!=="$"&&a!=="$!"&&a!=="$?"&&a!=="$~"&&a!=="&"||n++}e=e.nextSibling}return null}function S_(e){e=e.previousSibling;for(var n=0;e;){if(e.nodeType===8){var a=e.data;if(a==="$"||a==="$!"||a==="$?"||a==="$~"||a==="&"){if(n===0)return e;n--}else a!=="/$"&&a!=="/&"||n++}e=e.previousSibling}return null}function y_(e,n,a){switch(n=ru(a),e){case"html":if(e=n.documentElement,!e)throw Error(r(452));return e;case"head":if(e=n.head,!e)throw Error(r(453));return e;case"body":if(e=n.body,!e)throw Error(r(454));return e;default:throw Error(r(451))}}function Fo(e){for(var n=e.attributes;n.length;)e.removeAttributeNode(n[0]);Da(e)}var Si=new Map,M_=new Set;function su(e){return typeof e.getRootNode=="function"?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var ga=H.d;H.d={f:LS,r:NS,D:OS,C:PS,L:IS,m:FS,X:BS,S:zS,M:HS};function LS(){var e=ga.f(),n=Jl();return e||n}function NS(e){var n=$i(e);n!==null&&n.tag===5&&n.type==="form"?Bm(n):ga.r(e)}var Es=typeof document>"u"?null:document;function E_(e,n,a){var o=Es;if(o&&typeof n=="string"&&n){var c=Ne(n);c='link[rel="'+e+'"][href="'+c+'"]',typeof a=="string"&&(c+='[crossorigin="'+a+'"]'),M_.has(c)||(M_.add(c),e={rel:e,crossOrigin:a,href:n},o.querySelector(c)===null&&(n=o.createElement("link"),wn(n,"link",e),hn(n),o.head.appendChild(n)))}}function OS(e){ga.D(e),E_("dns-prefetch",e,null)}function PS(e,n){ga.C(e,n),E_("preconnect",e,n)}function IS(e,n,a){ga.L(e,n,a);var o=Es;if(o&&e&&n){var c='link[rel="preload"][as="'+Ne(n)+'"]';n==="image"&&a&&a.imageSrcSet?(c+='[imagesrcset="'+Ne(a.imageSrcSet)+'"]',typeof a.imageSizes=="string"&&(c+='[imagesizes="'+Ne(a.imageSizes)+'"]')):c+='[href="'+Ne(e)+'"]';var h=c;switch(n){case"style":h=bs(e);break;case"script":h=Ts(e)}Si.has(h)||(e=v({rel:"preload",href:n==="image"&&a&&a.imageSrcSet?void 0:e,as:n},a),Si.set(h,e),o.querySelector(c)!==null||n==="style"&&o.querySelector(zo(h))||n==="script"&&o.querySelector(Bo(h))||(n=o.createElement("link"),wn(n,"link",e),hn(n),o.head.appendChild(n)))}}function FS(e,n){ga.m(e,n);var a=Es;if(a&&e){var o=n&&typeof n.as=="string"?n.as:"script",c='link[rel="modulepreload"][as="'+Ne(o)+'"][href="'+Ne(e)+'"]',h=c;switch(o){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":h=Ts(e)}if(!Si.has(h)&&(e=v({rel:"modulepreload",href:e},n),Si.set(h,e),a.querySelector(c)===null)){switch(o){case"audioworklet":case"paintworklet":case"serviceworker":case"sharedworker":case"worker":case"script":if(a.querySelector(Bo(h)))return}o=a.createElement("link"),wn(o,"link",e),hn(o),a.head.appendChild(o)}}}function zS(e,n,a){ga.S(e,n,a);var o=Es;if(o&&e){var c=Ua(o).hoistableStyles,h=bs(e);n=n||"default";var x=c.get(h);if(!x){var R={loading:0,preload:null};if(x=o.querySelector(zo(h)))R.loading=5;else{e=v({rel:"stylesheet",href:e,"data-precedence":n},a),(a=Si.get(h))&&nh(e,a);var B=x=o.createElement("link");hn(B),wn(B,"link",e),B._p=new Promise(function(et,dt){B.onload=et,B.onerror=dt}),B.addEventListener("load",function(){R.loading|=1}),B.addEventListener("error",function(){R.loading|=2}),R.loading|=4,ou(x,n,o)}x={type:"stylesheet",instance:x,count:1,state:R},c.set(h,x)}}}function BS(e,n){ga.X(e,n);var a=Es;if(a&&e){var o=Ua(a).hoistableScripts,c=Ts(e),h=o.get(c);h||(h=a.querySelector(Bo(c)),h||(e=v({src:e,async:!0},n),(n=Si.get(c))&&ih(e,n),h=a.createElement("script"),hn(h),wn(h,"link",e),a.head.appendChild(h)),h={type:"script",instance:h,count:1,state:null},o.set(c,h))}}function HS(e,n){ga.M(e,n);var a=Es;if(a&&e){var o=Ua(a).hoistableScripts,c=Ts(e),h=o.get(c);h||(h=a.querySelector(Bo(c)),h||(e=v({src:e,async:!0,type:"module"},n),(n=Si.get(c))&&ih(e,n),h=a.createElement("script"),hn(h),wn(h,"link",e),a.head.appendChild(h)),h={type:"script",instance:h,count:1,state:null},o.set(c,h))}}function b_(e,n,a,o){var c=(c=at.current)?su(c):null;if(!c)throw Error(r(446));switch(e){case"meta":case"title":return null;case"style":return typeof a.precedence=="string"&&typeof a.href=="string"?(n=bs(a.href),a=Ua(c).hoistableStyles,o=a.get(n),o||(o={type:"style",instance:null,count:0,state:null},a.set(n,o)),o):{type:"void",instance:null,count:0,state:null};case"link":if(a.rel==="stylesheet"&&typeof a.href=="string"&&typeof a.precedence=="string"){e=bs(a.href);var h=Ua(c).hoistableStyles,x=h.get(e);if(x||(c=c.ownerDocument||c,x={type:"stylesheet",instance:null,count:0,state:{loading:0,preload:null}},h.set(e,x),(h=c.querySelector(zo(e)))&&!h._p&&(x.instance=h,x.state.loading=5),Si.has(e)||(a={rel:"preload",as:"style",href:a.href,crossOrigin:a.crossOrigin,integrity:a.integrity,media:a.media,hrefLang:a.hrefLang,referrerPolicy:a.referrerPolicy},Si.set(e,a),h||GS(c,e,a,x.state))),n&&o===null)throw Error(r(528,""));return x}if(n&&o!==null)throw Error(r(529,""));return null;case"script":return n=a.async,a=a.src,typeof a=="string"&&n&&typeof n!="function"&&typeof n!="symbol"?(n=Ts(a),a=Ua(c).hoistableScripts,o=a.get(n),o||(o={type:"script",instance:null,count:0,state:null},a.set(n,o)),o):{type:"void",instance:null,count:0,state:null};default:throw Error(r(444,e))}}function bs(e){return'href="'+Ne(e)+'"'}function zo(e){return'link[rel="stylesheet"]['+e+"]"}function T_(e){return v({},e,{"data-precedence":e.precedence,precedence:null})}function GS(e,n,a,o){e.querySelector('link[rel="preload"][as="style"]['+n+"]")?o.loading=1:(n=e.createElement("link"),o.preload=n,n.addEventListener("load",function(){return o.loading|=1}),n.addEventListener("error",function(){return o.loading|=2}),wn(n,"link",a),hn(n),e.head.appendChild(n))}function Ts(e){return'[src="'+Ne(e)+'"]'}function Bo(e){return"script[async]"+e}function A_(e,n,a){if(n.count++,n.instance===null)switch(n.type){case"style":var o=e.querySelector('style[data-href~="'+Ne(a.href)+'"]');if(o)return n.instance=o,hn(o),o;var c=v({},a,{"data-href":a.href,"data-precedence":a.precedence,href:null,precedence:null});return o=(e.ownerDocument||e).createElement("style"),hn(o),wn(o,"style",c),ou(o,a.precedence,e),n.instance=o;case"stylesheet":c=bs(a.href);var h=e.querySelector(zo(c));if(h)return n.state.loading|=4,n.instance=h,hn(h),h;o=T_(a),(c=Si.get(c))&&nh(o,c),h=(e.ownerDocument||e).createElement("link"),hn(h);var x=h;return x._p=new Promise(function(R,B){x.onload=R,x.onerror=B}),wn(h,"link",o),n.state.loading|=4,ou(h,a.precedence,e),n.instance=h;case"script":return h=Ts(a.src),(c=e.querySelector(Bo(h)))?(n.instance=c,hn(c),c):(o=a,(c=Si.get(h))&&(o=v({},a),ih(o,c)),e=e.ownerDocument||e,c=e.createElement("script"),hn(c),wn(c,"link",o),e.head.appendChild(c),n.instance=c);case"void":return null;default:throw Error(r(443,n.type))}else n.type==="stylesheet"&&(n.state.loading&4)===0&&(o=n.instance,n.state.loading|=4,ou(o,a.precedence,e));return n.instance}function ou(e,n,a){for(var o=a.querySelectorAll('link[rel="stylesheet"][data-precedence],style[data-precedence]'),c=o.length?o[o.length-1]:null,h=c,x=0;x<o.length;x++){var R=o[x];if(R.dataset.precedence===n)h=R;else if(h!==c)break}h?h.parentNode.insertBefore(e,h.nextSibling):(n=a.nodeType===9?a.head:a,n.insertBefore(e,n.firstChild))}function nh(e,n){e.crossOrigin==null&&(e.crossOrigin=n.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=n.referrerPolicy),e.title==null&&(e.title=n.title)}function ih(e,n){e.crossOrigin==null&&(e.crossOrigin=n.crossOrigin),e.referrerPolicy==null&&(e.referrerPolicy=n.referrerPolicy),e.integrity==null&&(e.integrity=n.integrity)}var lu=null;function R_(e,n,a){if(lu===null){var o=new Map,c=lu=new Map;c.set(a,o)}else c=lu,o=c.get(a),o||(o=new Map,c.set(a,o));if(o.has(e))return o;for(o.set(e,null),a=a.getElementsByTagName(e),c=0;c<a.length;c++){var h=a[c];if(!(h[wa]||h[fn]||e==="link"&&h.getAttribute("rel")==="stylesheet")&&h.namespaceURI!=="http://www.w3.org/2000/svg"){var x=h.getAttribute(n)||"";x=e+x;var R=o.get(x);R?R.push(h):o.set(x,[h])}}return o}function C_(e,n,a){e=e.ownerDocument||e,e.head.insertBefore(a,n==="title"?e.querySelector("head > title"):null)}function VS(e,n,a){if(a===1||n.itemProp!=null)return!1;switch(e){case"meta":case"title":return!0;case"style":if(typeof n.precedence!="string"||typeof n.href!="string"||n.href==="")break;return!0;case"link":if(typeof n.rel!="string"||typeof n.href!="string"||n.href===""||n.onLoad||n.onError)break;return n.rel==="stylesheet"?(e=n.disabled,typeof n.precedence=="string"&&e==null):!0;case"script":if(n.async&&typeof n.async!="function"&&typeof n.async!="symbol"&&!n.onLoad&&!n.onError&&n.src&&typeof n.src=="string")return!0}return!1}function w_(e){return!(e.type==="stylesheet"&&(e.state.loading&3)===0)}function kS(e,n,a,o){if(a.type==="stylesheet"&&(typeof o.media!="string"||matchMedia(o.media).matches!==!1)&&(a.state.loading&4)===0){if(a.instance===null){var c=bs(o.href),h=n.querySelector(zo(c));if(h){n=h._p,n!==null&&typeof n=="object"&&typeof n.then=="function"&&(e.count++,e=uu.bind(e),n.then(e,e)),a.state.loading|=4,a.instance=h,hn(h);return}h=n.ownerDocument||n,o=T_(o),(c=Si.get(c))&&nh(o,c),h=h.createElement("link"),hn(h);var x=h;x._p=new Promise(function(R,B){x.onload=R,x.onerror=B}),wn(h,"link",o),a.instance=h}e.stylesheets===null&&(e.stylesheets=new Map),e.stylesheets.set(a,n),(n=a.state.preload)&&(a.state.loading&3)===0&&(e.count++,a=uu.bind(e),n.addEventListener("load",a),n.addEventListener("error",a))}}var ah=0;function XS(e,n){return e.stylesheets&&e.count===0&&fu(e,e.stylesheets),0<e.count||0<e.imgCount?function(a){var o=setTimeout(function(){if(e.stylesheets&&fu(e,e.stylesheets),e.unsuspend){var h=e.unsuspend;e.unsuspend=null,h()}},6e4+n);0<e.imgBytes&&ah===0&&(ah=62500*bS());var c=setTimeout(function(){if(e.waitingForImages=!1,e.count===0&&(e.stylesheets&&fu(e,e.stylesheets),e.unsuspend)){var h=e.unsuspend;e.unsuspend=null,h()}},(e.imgBytes>ah?50:800)+n);return e.unsuspend=a,function(){e.unsuspend=null,clearTimeout(o),clearTimeout(c)}}:null}function uu(){if(this.count--,this.count===0&&(this.imgCount===0||!this.waitingForImages)){if(this.stylesheets)fu(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var cu=null;function fu(e,n){e.stylesheets=null,e.unsuspend!==null&&(e.count++,cu=new Map,n.forEach(WS,e),cu=null,uu.call(e))}function WS(e,n){if(!(n.state.loading&4)){var a=cu.get(e);if(a)var o=a.get(null);else{a=new Map,cu.set(e,a);for(var c=e.querySelectorAll("link[data-precedence],style[data-precedence]"),h=0;h<c.length;h++){var x=c[h];(x.nodeName==="LINK"||x.getAttribute("media")!=="not all")&&(a.set(x.dataset.precedence,x),o=x)}o&&a.set(null,o)}c=n.instance,x=c.getAttribute("data-precedence"),h=a.get(x)||o,h===o&&a.set(null,c),a.set(x,c),this.count++,o=uu.bind(this),c.addEventListener("load",o),c.addEventListener("error",o),h?h.parentNode.insertBefore(c,h.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(c,e.firstChild)),n.state.loading|=4}}var Ho={$$typeof:z,Provider:null,Consumer:null,_currentValue:j,_currentValue2:j,_threadCount:0};function qS(e,n,a,o,c,h,x,R,B){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=Wt(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=Wt(0),this.hiddenUpdates=Wt(null),this.identifierPrefix=o,this.onUncaughtError=c,this.onCaughtError=h,this.onRecoverableError=x,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=B,this.incompleteTransitions=new Map}function D_(e,n,a,o,c,h,x,R,B,et,dt,vt){return e=new qS(e,n,a,x,B,et,dt,vt,R),n=1,h===!0&&(n|=24),h=ni(3,null,null,n),e.current=h,h.stateNode=e,n=Ic(),n.refCount++,e.pooledCache=n,n.refCount++,h.memoizedState={element:o,isDehydrated:a,cache:n},Hc(h),e}function U_(e){return e?(e=ns,e):ns}function L_(e,n,a,o,c,h){c=U_(c),o.context===null?o.context=c:o.pendingContext=c,o=Ba(n),o.payload={element:a},h=h===void 0?null:h,h!==null&&(o.callback=h),a=Ha(e,o,n),a!==null&&(Yn(a,e,n),vo(a,e,n))}function N_(e,n){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var a=e.retryLane;e.retryLane=a!==0&&a<n?a:n}}function rh(e,n){N_(e,n),(e=e.alternate)&&N_(e,n)}function O_(e){if(e.tag===13||e.tag===31){var n=Mr(e,67108864);n!==null&&Yn(n,e,67108864),rh(e,67108864)}}function P_(e){if(e.tag===13||e.tag===31){var n=oi();n=$s(n);var a=Mr(e,n);a!==null&&Yn(a,e,n),rh(e,n)}}var hu=!0;function YS(e,n,a,o){var c=I.T;I.T=null;var h=H.p;try{H.p=2,sh(e,n,a,o)}finally{H.p=h,I.T=c}}function ZS(e,n,a,o){var c=I.T;I.T=null;var h=H.p;try{H.p=8,sh(e,n,a,o)}finally{H.p=h,I.T=c}}function sh(e,n,a,o){if(hu){var c=oh(o);if(c===null)qf(e,n,o,du,a),F_(e,o);else if(QS(c,e,n,a,o))o.stopPropagation();else if(F_(e,o),n&4&&-1<KS.indexOf(e)){for(;c!==null;){var h=$i(c);if(h!==null)switch(h.tag){case 3:if(h=h.stateNode,h.current.memoizedState.isDehydrated){var x=Tt(h.pendingLanes);if(x!==0){var R=h;for(R.pendingLanes|=2,R.entangledLanes|=2;x;){var B=1<<31-Ft(x);R.entanglements[1]|=B,x&=~B}Gi(h),(we&6)===0&&(Kl=ze()+500,Oo(0))}}break;case 31:case 13:R=Mr(h,2),R!==null&&Yn(R,h,2),Jl(),rh(h,2)}if(h=oh(o),h===null&&qf(e,n,o,du,a),h===c)break;c=h}c!==null&&o.stopPropagation()}else qf(e,n,o,null,a)}}function oh(e){return e=lc(e),lh(e)}var du=null;function lh(e){if(du=null,e=ji(e),e!==null){var n=u(e);if(n===null)e=null;else{var a=n.tag;if(a===13){if(e=f(n),e!==null)return e;e=null}else if(a===31){if(e=p(n),e!==null)return e;e=null}else if(a===3){if(n.stateNode.current.memoizedState.isDehydrated)return n.tag===3?n.stateNode.containerInfo:null;e=null}else n!==e&&(e=null)}}return du=e,null}function I_(e){switch(e){case"beforetoggle":case"cancel":case"click":case"close":case"contextmenu":case"copy":case"cut":case"auxclick":case"dblclick":case"dragend":case"dragstart":case"drop":case"focusin":case"focusout":case"input":case"invalid":case"keydown":case"keypress":case"keyup":case"mousedown":case"mouseup":case"paste":case"pause":case"play":case"pointercancel":case"pointerdown":case"pointerup":case"ratechange":case"reset":case"resize":case"seeked":case"submit":case"toggle":case"touchcancel":case"touchend":case"touchstart":case"volumechange":case"change":case"selectionchange":case"textInput":case"compositionstart":case"compositionend":case"compositionupdate":case"beforeblur":case"afterblur":case"beforeinput":case"blur":case"fullscreenchange":case"focus":case"hashchange":case"popstate":case"select":case"selectstart":return 2;case"drag":case"dragenter":case"dragexit":case"dragleave":case"dragover":case"mousemove":case"mouseout":case"mouseover":case"pointermove":case"pointerout":case"pointerover":case"scroll":case"touchmove":case"wheel":case"mouseenter":case"mouseleave":case"pointerenter":case"pointerleave":return 8;case"message":switch(Ce()){case U:return 2;case y:return 8;case Q:case rt:return 32;case ct:return 268435456;default:return 32}default:return 32}}var uh=!1,Ja=null,ja=null,$a=null,Go=new Map,Vo=new Map,tr=[],KS="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset".split(" ");function F_(e,n){switch(e){case"focusin":case"focusout":Ja=null;break;case"dragenter":case"dragleave":ja=null;break;case"mouseover":case"mouseout":$a=null;break;case"pointerover":case"pointerout":Go.delete(n.pointerId);break;case"gotpointercapture":case"lostpointercapture":Vo.delete(n.pointerId)}}function ko(e,n,a,o,c,h){return e===null||e.nativeEvent!==h?(e={blockedOn:n,domEventName:a,eventSystemFlags:o,nativeEvent:h,targetContainers:[c]},n!==null&&(n=$i(n),n!==null&&O_(n)),e):(e.eventSystemFlags|=o,n=e.targetContainers,c!==null&&n.indexOf(c)===-1&&n.push(c),e)}function QS(e,n,a,o,c){switch(n){case"focusin":return Ja=ko(Ja,e,n,a,o,c),!0;case"dragenter":return ja=ko(ja,e,n,a,o,c),!0;case"mouseover":return $a=ko($a,e,n,a,o,c),!0;case"pointerover":var h=c.pointerId;return Go.set(h,ko(Go.get(h)||null,e,n,a,o,c)),!0;case"gotpointercapture":return h=c.pointerId,Vo.set(h,ko(Vo.get(h)||null,e,n,a,o,c)),!0}return!1}function z_(e){var n=ji(e.target);if(n!==null){var a=u(n);if(a!==null){if(n=a.tag,n===13){if(n=f(a),n!==null){e.blockedOn=n,Kr(e.priority,function(){P_(a)});return}}else if(n===31){if(n=p(a),n!==null){e.blockedOn=n,Kr(e.priority,function(){P_(a)});return}}else if(n===3&&a.stateNode.current.memoizedState.isDehydrated){e.blockedOn=a.tag===3?a.stateNode.containerInfo:null;return}}}e.blockedOn=null}function pu(e){if(e.blockedOn!==null)return!1;for(var n=e.targetContainers;0<n.length;){var a=oh(e.nativeEvent);if(a===null){a=e.nativeEvent;var o=new a.constructor(a.type,a);oc=o,a.target.dispatchEvent(o),oc=null}else return n=$i(a),n!==null&&O_(n),e.blockedOn=a,!1;n.shift()}return!0}function B_(e,n,a){pu(e)&&a.delete(n)}function JS(){uh=!1,Ja!==null&&pu(Ja)&&(Ja=null),ja!==null&&pu(ja)&&(ja=null),$a!==null&&pu($a)&&($a=null),Go.forEach(B_),Vo.forEach(B_)}function mu(e,n){e.blockedOn===n&&(e.blockedOn=null,uh||(uh=!0,s.unstable_scheduleCallback(s.unstable_NormalPriority,JS)))}var gu=null;function H_(e){gu!==e&&(gu=e,s.unstable_scheduleCallback(s.unstable_NormalPriority,function(){gu===e&&(gu=null);for(var n=0;n<e.length;n+=3){var a=e[n],o=e[n+1],c=e[n+2];if(typeof o!="function"){if(lh(o||a)===null)continue;break}var h=$i(a);h!==null&&(e.splice(n,3),n-=3,of(h,{pending:!0,data:c,method:a.method,action:o},o,c))}}))}function As(e){function n(B){return mu(B,e)}Ja!==null&&mu(Ja,e),ja!==null&&mu(ja,e),$a!==null&&mu($a,e),Go.forEach(n),Vo.forEach(n);for(var a=0;a<tr.length;a++){var o=tr[a];o.blockedOn===e&&(o.blockedOn=null)}for(;0<tr.length&&(a=tr[0],a.blockedOn===null);)z_(a),a.blockedOn===null&&tr.shift();if(a=(e.ownerDocument||e).$$reactFormReplay,a!=null)for(o=0;o<a.length;o+=3){var c=a[o],h=a[o+1],x=c[Tn]||null;if(typeof h=="function")x||H_(a);else if(x){var R=null;if(h&&h.hasAttribute("formAction")){if(c=h,x=h[Tn]||null)R=x.formAction;else if(lh(c)!==null)continue}else R=x.action;typeof R=="function"?a[o+1]=R:(a.splice(o,3),o-=3),H_(a)}}}function G_(){function e(h){h.canIntercept&&h.info==="react-transition"&&h.intercept({handler:function(){return new Promise(function(x){return c=x})},focusReset:"manual",scroll:"manual"})}function n(){c!==null&&(c(),c=null),o||setTimeout(a,20)}function a(){if(!o&&!navigation.transition){var h=navigation.currentEntry;h&&h.url!=null&&navigation.navigate(h.url,{state:h.getState(),info:"react-transition",history:"replace"})}}if(typeof navigation=="object"){var o=!1,c=null;return navigation.addEventListener("navigate",e),navigation.addEventListener("navigatesuccess",n),navigation.addEventListener("navigateerror",n),setTimeout(a,100),function(){o=!0,navigation.removeEventListener("navigate",e),navigation.removeEventListener("navigatesuccess",n),navigation.removeEventListener("navigateerror",n),c!==null&&(c(),c=null)}}}function ch(e){this._internalRoot=e}_u.prototype.render=ch.prototype.render=function(e){var n=this._internalRoot;if(n===null)throw Error(r(409));var a=n.current,o=oi();L_(a,o,e,n,null,null)},_u.prototype.unmount=ch.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var n=e.containerInfo;L_(e.current,2,null,e,null,null),Jl(),n[Gn]=null}};function _u(e){this._internalRoot=e}_u.prototype.unstable_scheduleHydration=function(e){if(e){var n=eo();e={blockedOn:null,target:e,priority:n};for(var a=0;a<tr.length&&n!==0&&n<tr[a].priority;a++);tr.splice(a,0,e),a===0&&z_(e)}};var V_=t.version;if(V_!=="19.2.7")throw Error(r(527,V_,"19.2.7"));H.findDOMNode=function(e){var n=e._reactInternals;if(n===void 0)throw typeof e.render=="function"?Error(r(188)):(e=Object.keys(e).join(","),Error(r(268,e)));return e=d(n),e=e!==null?g(e):null,e=e===null?null:e.stateNode,e};var jS={bundleType:0,version:"19.2.7",rendererPackageName:"react-dom",currentDispatcherRef:I,reconcilerVersion:"19.2.7"};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"){var vu=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!vu.isDisabled&&vu.supportsFiber)try{ut=vu.inject(jS),ft=vu}catch{}}return Wo.createRoot=function(e,n){if(!l(e))throw Error(r(299));var a=!1,o="",c=Km,h=Qm,x=Jm;return n!=null&&(n.unstable_strictMode===!0&&(a=!0),n.identifierPrefix!==void 0&&(o=n.identifierPrefix),n.onUncaughtError!==void 0&&(c=n.onUncaughtError),n.onCaughtError!==void 0&&(h=n.onCaughtError),n.onRecoverableError!==void 0&&(x=n.onRecoverableError)),n=D_(e,1,!1,null,null,a,o,null,c,h,x,G_),e[Gn]=n.current,Wf(e),new ch(n)},Wo.hydrateRoot=function(e,n,a){if(!l(e))throw Error(r(299));var o=!1,c="",h=Km,x=Qm,R=Jm,B=null;return a!=null&&(a.unstable_strictMode===!0&&(o=!0),a.identifierPrefix!==void 0&&(c=a.identifierPrefix),a.onUncaughtError!==void 0&&(h=a.onUncaughtError),a.onCaughtError!==void 0&&(x=a.onCaughtError),a.onRecoverableError!==void 0&&(R=a.onRecoverableError),a.formState!==void 0&&(B=a.formState)),n=D_(e,1,!0,n,a??null,o,c,B,h,x,R,G_),n.context=U_(null),a=n.current,o=oi(),o=$s(o),c=Ba(o),c.callback=null,Ha(a,c,o),a=o,n.current.lanes=a,Gt(n,a),Gi(n),e[Gn]=n.current,Wf(e),new _u(n)},Wo.version="19.2.7",Wo}var j_;function ly(){if(j_)return dh.exports;j_=1;function s(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>"u"||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!="function"))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(s)}catch(t){console.error(t)}}return s(),dh.exports=oy(),dh.exports}var uy=ly();const Xd="185",Vs={ROTATE:0,DOLLY:1,PAN:2},Gs={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},cy=0,$_=1,fy=2,Vu=1,hy=2,tl=3,fr=0,Qn=1,Ea=2,Ta=0,ks=1,t0=2,e0=3,n0=4,dy=5,kr=100,py=101,my=102,gy=103,_y=104,vy=200,xy=201,Sy=202,yy=203,jh=204,$h=205,My=206,Ey=207,by=208,Ty=209,Ay=210,Ry=211,Cy=212,wy=213,Dy=214,td=0,ed=1,nd=2,qs=3,id=4,ad=5,rd=6,sd=7,hv=0,Uy=1,Ly=2,Yi=0,dv=1,pv=2,mv=3,gv=4,_v=5,vv=6,xv=7,Sv=300,Yr=301,Ys=302,_h=303,vh=304,nc=306,od=1e3,ba=1001,ld=1002,Dn=1003,Ny=1004,xu=1005,In=1006,xh=1007,Wr=1008,fi=1009,yv=1010,Mv=1011,il=1012,Wd=1013,Ki=1014,Wi=1015,Ra=1016,qd=1017,Yd=1018,al=1020,Ev=35902,bv=35899,Tv=1021,Av=1022,Ni=1023,Ca=1026,qr=1027,Rv=1028,Zd=1029,Zr=1030,Kd=1031,Qd=1033,ku=33776,Xu=33777,Wu=33778,qu=33779,ud=35840,cd=35841,fd=35842,hd=35843,dd=36196,pd=37492,md=37496,gd=37488,_d=37489,Ku=37490,vd=37491,xd=37808,Sd=37809,yd=37810,Md=37811,Ed=37812,bd=37813,Td=37814,Ad=37815,Rd=37816,Cd=37817,wd=37818,Dd=37819,Ud=37820,Ld=37821,Nd=36492,Od=36494,Pd=36495,Id=36283,Fd=36284,Qu=36285,zd=36286,Oy=3200,Ju=0,Py=1,ur="",ci="srgb",ju="srgb-linear",$u="linear",Fe="srgb",Rs=7680,i0=519,Iy=512,Fy=513,zy=514,Jd=515,By=516,Hy=517,jd=518,Gy=519,a0=35044,r0="300 es",qi=2e3,rl=2001;function Vy(s){for(let t=s.length-1;t>=0;--t)if(s[t]>=65535)return!0;return!1}function tc(s){return document.createElementNS("http://www.w3.org/1999/xhtml",s)}function ky(){const s=tc("canvas");return s.style.display="block",s}const s0={};function o0(...s){const t="THREE."+s.shift();console.log(t,...s)}function Cv(s){const t=s[0];if(typeof t=="string"&&t.startsWith("TSL:")){const i=s[1];i&&i.isStackTrace?s[0]+=" "+i.getLocation():s[1]='Stack trace not available. Enable "THREE.Node.captureStackTrace" to capture stack traces.'}return s}function te(...s){s=Cv(s);const t="THREE."+s.shift();{const i=s[0];i&&i.isStackTrace?console.warn(i.getError(t)):console.warn(t,...s)}}function be(...s){s=Cv(s);const t="THREE."+s.shift();{const i=s[0];i&&i.isStackTrace?console.error(i.getError(t)):console.error(t,...s)}}function Xs(...s){const t=s.join(" ");t in s0||(s0[t]=!0,te(...s))}function Xy(s,t,i){return new Promise(function(r,l){function u(){switch(s.clientWaitSync(t,s.SYNC_FLUSH_COMMANDS_BIT,0)){case s.WAIT_FAILED:l();break;case s.TIMEOUT_EXPIRED:setTimeout(u,i);break;default:r()}}setTimeout(u,i)})}const Wy={[td]:ed,[nd]:rd,[id]:sd,[qs]:ad,[ed]:td,[rd]:nd,[sd]:id,[ad]:qs};class pr{addEventListener(t,i){this._listeners===void 0&&(this._listeners={});const r=this._listeners;r[t]===void 0&&(r[t]=[]),r[t].indexOf(i)===-1&&r[t].push(i)}hasEventListener(t,i){const r=this._listeners;return r===void 0?!1:r[t]!==void 0&&r[t].indexOf(i)!==-1}removeEventListener(t,i){const r=this._listeners;if(r===void 0)return;const l=r[t];if(l!==void 0){const u=l.indexOf(i);u!==-1&&l.splice(u,1)}}dispatchEvent(t){const i=this._listeners;if(i===void 0)return;const r=i[t.type];if(r!==void 0){t.target=this;const l=r.slice(0);for(let u=0,f=l.length;u<f;u++)l[u].call(this,t);t.target=null}}}const On=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"],Yu=Math.PI/180,Bd=180/Math.PI;function sl(){const s=Math.random()*4294967295|0,t=Math.random()*4294967295|0,i=Math.random()*4294967295|0,r=Math.random()*4294967295|0;return(On[s&255]+On[s>>8&255]+On[s>>16&255]+On[s>>24&255]+"-"+On[t&255]+On[t>>8&255]+"-"+On[t>>16&15|64]+On[t>>24&255]+"-"+On[i&63|128]+On[i>>8&255]+"-"+On[i>>16&255]+On[i>>24&255]+On[r&255]+On[r>>8&255]+On[r>>16&255]+On[r>>24&255]).toLowerCase()}function me(s,t,i){return Math.max(t,Math.min(i,s))}function qy(s,t){return(s%t+t)%t}function Sh(s,t,i){return(1-i)*s+i*t}function qo(s,t){switch(t.constructor){case Float32Array:return s;case Uint32Array:return s/4294967295;case Uint16Array:return s/65535;case Uint8Array:return s/255;case Int32Array:return Math.max(s/2147483647,-1);case Int16Array:return Math.max(s/32767,-1);case Int8Array:return Math.max(s/127,-1);default:throw new Error("THREE.MathUtils: Invalid component type.")}}function Zn(s,t){switch(t.constructor){case Float32Array:return s;case Uint32Array:return Math.round(s*4294967295);case Uint16Array:return Math.round(s*65535);case Uint8Array:return Math.round(s*255);case Int32Array:return Math.round(s*2147483647);case Int16Array:return Math.round(s*32767);case Int8Array:return Math.round(s*127);default:throw new Error("THREE.MathUtils: Invalid component type.")}}const Yy={DEG2RAD:Yu},sp=class sp{constructor(t=0,i=0){this.x=t,this.y=i}get width(){return this.x}set width(t){this.x=t}get height(){return this.y}set height(t){this.y=t}set(t,i){return this.x=t,this.y=i,this}setScalar(t){return this.x=t,this.y=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setComponent(t,i){switch(t){case 0:this.x=i;break;case 1:this.y=i;break;default:throw new Error("THREE.Vector2: index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;default:throw new Error("THREE.Vector2: index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y)}copy(t){return this.x=t.x,this.y=t.y,this}add(t){return this.x+=t.x,this.y+=t.y,this}addScalar(t){return this.x+=t,this.y+=t,this}addVectors(t,i){return this.x=t.x+i.x,this.y=t.y+i.y,this}addScaledVector(t,i){return this.x+=t.x*i,this.y+=t.y*i,this}sub(t){return this.x-=t.x,this.y-=t.y,this}subScalar(t){return this.x-=t,this.y-=t,this}subVectors(t,i){return this.x=t.x-i.x,this.y=t.y-i.y,this}multiply(t){return this.x*=t.x,this.y*=t.y,this}multiplyScalar(t){return this.x*=t,this.y*=t,this}divide(t){return this.x/=t.x,this.y/=t.y,this}divideScalar(t){return this.multiplyScalar(1/t)}applyMatrix3(t){const i=this.x,r=this.y,l=t.elements;return this.x=l[0]*i+l[3]*r+l[6],this.y=l[1]*i+l[4]*r+l[7],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this}clamp(t,i){return this.x=me(this.x,t.x,i.x),this.y=me(this.y,t.y,i.y),this}clampScalar(t,i){return this.x=me(this.x,t,i),this.y=me(this.y,t,i),this}clampLength(t,i){const r=this.length();return this.divideScalar(r||1).multiplyScalar(me(r,t,i))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(t){return this.x*t.x+this.y*t.y}cross(t){return this.x*t.y-this.y*t.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(t){const i=Math.sqrt(this.lengthSq()*t.lengthSq());if(i===0)return Math.PI/2;const r=this.dot(t)/i;return Math.acos(me(r,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const i=this.x-t.x,r=this.y-t.y;return i*i+r*r}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,i){return this.x+=(t.x-this.x)*i,this.y+=(t.y-this.y)*i,this}lerpVectors(t,i,r){return this.x=t.x+(i.x-t.x)*r,this.y=t.y+(i.y-t.y)*r,this}equals(t){return t.x===this.x&&t.y===this.y}fromArray(t,i=0){return this.x=t[i],this.y=t[i+1],this}toArray(t=[],i=0){return t[i]=this.x,t[i+1]=this.y,t}fromBufferAttribute(t,i){return this.x=t.getX(i),this.y=t.getY(i),this}rotateAround(t,i){const r=Math.cos(i),l=Math.sin(i),u=this.x-t.x,f=this.y-t.y;return this.x=u*r-f*l+t.x,this.y=u*l+f*r+t.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}};sp.prototype.isVector2=!0;let ie=sp;class hr{constructor(t=0,i=0,r=0,l=1){this.isQuaternion=!0,this._x=t,this._y=i,this._z=r,this._w=l}static slerpFlat(t,i,r,l,u,f,p){let m=r[l+0],d=r[l+1],g=r[l+2],v=r[l+3],_=u[f+0],M=u[f+1],T=u[f+2],w=u[f+3];if(v!==w||m!==_||d!==M||g!==T){let E=m*_+d*M+g*T+v*w;E<0&&(_=-_,M=-M,T=-T,w=-w,E=-E);let S=1-p;if(E<.9995){const F=Math.acos(E),z=Math.sin(F);S=Math.sin(S*F)/z,p=Math.sin(p*F)/z,m=m*S+_*p,d=d*S+M*p,g=g*S+T*p,v=v*S+w*p}else{m=m*S+_*p,d=d*S+M*p,g=g*S+T*p,v=v*S+w*p;const F=1/Math.sqrt(m*m+d*d+g*g+v*v);m*=F,d*=F,g*=F,v*=F}}t[i]=m,t[i+1]=d,t[i+2]=g,t[i+3]=v}static multiplyQuaternionsFlat(t,i,r,l,u,f){const p=r[l],m=r[l+1],d=r[l+2],g=r[l+3],v=u[f],_=u[f+1],M=u[f+2],T=u[f+3];return t[i]=p*T+g*v+m*M-d*_,t[i+1]=m*T+g*_+d*v-p*M,t[i+2]=d*T+g*M+p*_-m*v,t[i+3]=g*T-p*v-m*_-d*M,t}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get w(){return this._w}set w(t){this._w=t,this._onChangeCallback()}set(t,i,r,l){return this._x=t,this._y=i,this._z=r,this._w=l,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(t){return this._x=t.x,this._y=t.y,this._z=t.z,this._w=t.w,this._onChangeCallback(),this}setFromEuler(t,i=!0){const r=t._x,l=t._y,u=t._z,f=t._order,p=Math.cos,m=Math.sin,d=p(r/2),g=p(l/2),v=p(u/2),_=m(r/2),M=m(l/2),T=m(u/2);switch(f){case"XYZ":this._x=_*g*v+d*M*T,this._y=d*M*v-_*g*T,this._z=d*g*T+_*M*v,this._w=d*g*v-_*M*T;break;case"YXZ":this._x=_*g*v+d*M*T,this._y=d*M*v-_*g*T,this._z=d*g*T-_*M*v,this._w=d*g*v+_*M*T;break;case"ZXY":this._x=_*g*v-d*M*T,this._y=d*M*v+_*g*T,this._z=d*g*T+_*M*v,this._w=d*g*v-_*M*T;break;case"ZYX":this._x=_*g*v-d*M*T,this._y=d*M*v+_*g*T,this._z=d*g*T-_*M*v,this._w=d*g*v+_*M*T;break;case"YZX":this._x=_*g*v+d*M*T,this._y=d*M*v+_*g*T,this._z=d*g*T-_*M*v,this._w=d*g*v-_*M*T;break;case"XZY":this._x=_*g*v-d*M*T,this._y=d*M*v-_*g*T,this._z=d*g*T+_*M*v,this._w=d*g*v+_*M*T;break;default:te("Quaternion: .setFromEuler() encountered an unknown order: "+f)}return i===!0&&this._onChangeCallback(),this}setFromAxisAngle(t,i){const r=i/2,l=Math.sin(r);return this._x=t.x*l,this._y=t.y*l,this._z=t.z*l,this._w=Math.cos(r),this._onChangeCallback(),this}setFromRotationMatrix(t){const i=t.elements,r=i[0],l=i[4],u=i[8],f=i[1],p=i[5],m=i[9],d=i[2],g=i[6],v=i[10],_=r+p+v;if(_>0){const M=.5/Math.sqrt(_+1);this._w=.25/M,this._x=(g-m)*M,this._y=(u-d)*M,this._z=(f-l)*M}else if(r>p&&r>v){const M=2*Math.sqrt(1+r-p-v);this._w=(g-m)/M,this._x=.25*M,this._y=(l+f)/M,this._z=(u+d)/M}else if(p>v){const M=2*Math.sqrt(1+p-r-v);this._w=(u-d)/M,this._x=(l+f)/M,this._y=.25*M,this._z=(m+g)/M}else{const M=2*Math.sqrt(1+v-r-p);this._w=(f-l)/M,this._x=(u+d)/M,this._y=(m+g)/M,this._z=.25*M}return this._onChangeCallback(),this}setFromUnitVectors(t,i){let r=t.dot(i)+1;return r<1e-8?(r=0,Math.abs(t.x)>Math.abs(t.z)?(this._x=-t.y,this._y=t.x,this._z=0,this._w=r):(this._x=0,this._y=-t.z,this._z=t.y,this._w=r)):(this._x=t.y*i.z-t.z*i.y,this._y=t.z*i.x-t.x*i.z,this._z=t.x*i.y-t.y*i.x,this._w=r),this.normalize()}angleTo(t){return 2*Math.acos(Math.abs(me(this.dot(t),-1,1)))}rotateTowards(t,i){const r=this.angleTo(t);if(r===0)return this;const l=Math.min(1,i/r);return this.slerp(t,l),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(t){return this._x*t._x+this._y*t._y+this._z*t._z+this._w*t._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let t=this.length();return t===0?(this._x=0,this._y=0,this._z=0,this._w=1):(t=1/t,this._x=this._x*t,this._y=this._y*t,this._z=this._z*t,this._w=this._w*t),this._onChangeCallback(),this}multiply(t){return this.multiplyQuaternions(this,t)}premultiply(t){return this.multiplyQuaternions(t,this)}multiplyQuaternions(t,i){const r=t._x,l=t._y,u=t._z,f=t._w,p=i._x,m=i._y,d=i._z,g=i._w;return this._x=r*g+f*p+l*d-u*m,this._y=l*g+f*m+u*p-r*d,this._z=u*g+f*d+r*m-l*p,this._w=f*g-r*p-l*m-u*d,this._onChangeCallback(),this}slerp(t,i){let r=t._x,l=t._y,u=t._z,f=t._w,p=this.dot(t);p<0&&(r=-r,l=-l,u=-u,f=-f,p=-p);let m=1-i;if(p<.9995){const d=Math.acos(p),g=Math.sin(d);m=Math.sin(m*d)/g,i=Math.sin(i*d)/g,this._x=this._x*m+r*i,this._y=this._y*m+l*i,this._z=this._z*m+u*i,this._w=this._w*m+f*i,this._onChangeCallback()}else this._x=this._x*m+r*i,this._y=this._y*m+l*i,this._z=this._z*m+u*i,this._w=this._w*m+f*i,this.normalize();return this}slerpQuaternions(t,i,r){return this.copy(t).slerp(i,r)}random(){const t=2*Math.PI*Math.random(),i=2*Math.PI*Math.random(),r=Math.random(),l=Math.sqrt(1-r),u=Math.sqrt(r);return this.set(l*Math.sin(t),l*Math.cos(t),u*Math.sin(i),u*Math.cos(i))}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._w===this._w}fromArray(t,i=0){return this._x=t[i],this._y=t[i+1],this._z=t[i+2],this._w=t[i+3],this._onChangeCallback(),this}toArray(t=[],i=0){return t[i]=this._x,t[i+1]=this._y,t[i+2]=this._z,t[i+3]=this._w,t}fromBufferAttribute(t,i){return this._x=t.getX(i),this._y=t.getY(i),this._z=t.getZ(i),this._w=t.getW(i),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}const op=class op{constructor(t=0,i=0,r=0){this.x=t,this.y=i,this.z=r}set(t,i,r){return r===void 0&&(r=this.z),this.x=t,this.y=i,this.z=r,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setComponent(t,i){switch(t){case 0:this.x=i;break;case 1:this.y=i;break;case 2:this.z=i;break;default:throw new Error("THREE.Vector3: index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("THREE.Vector3: index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this}addVectors(t,i){return this.x=t.x+i.x,this.y=t.y+i.y,this.z=t.z+i.z,this}addScaledVector(t,i){return this.x+=t.x*i,this.y+=t.y*i,this.z+=t.z*i,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this}subVectors(t,i){return this.x=t.x-i.x,this.y=t.y-i.y,this.z=t.z-i.z,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this}multiplyVectors(t,i){return this.x=t.x*i.x,this.y=t.y*i.y,this.z=t.z*i.z,this}applyEuler(t){return this.applyQuaternion(l0.setFromEuler(t))}applyAxisAngle(t,i){return this.applyQuaternion(l0.setFromAxisAngle(t,i))}applyMatrix3(t){const i=this.x,r=this.y,l=this.z,u=t.elements;return this.x=u[0]*i+u[3]*r+u[6]*l,this.y=u[1]*i+u[4]*r+u[7]*l,this.z=u[2]*i+u[5]*r+u[8]*l,this}applyNormalMatrix(t){return this.applyMatrix3(t).normalize()}applyMatrix4(t){const i=this.x,r=this.y,l=this.z,u=t.elements,f=1/(u[3]*i+u[7]*r+u[11]*l+u[15]);return this.x=(u[0]*i+u[4]*r+u[8]*l+u[12])*f,this.y=(u[1]*i+u[5]*r+u[9]*l+u[13])*f,this.z=(u[2]*i+u[6]*r+u[10]*l+u[14])*f,this}applyQuaternion(t){const i=this.x,r=this.y,l=this.z,u=t.x,f=t.y,p=t.z,m=t.w,d=2*(f*l-p*r),g=2*(p*i-u*l),v=2*(u*r-f*i);return this.x=i+m*d+f*v-p*g,this.y=r+m*g+p*d-u*v,this.z=l+m*v+u*g-f*d,this}project(t){return this.applyMatrix4(t.matrixWorldInverse).applyMatrix4(t.projectionMatrix)}unproject(t){return this.applyMatrix4(t.projectionMatrixInverse).applyMatrix4(t.matrixWorld)}transformDirection(t){const i=this.x,r=this.y,l=this.z,u=t.elements;return this.x=u[0]*i+u[4]*r+u[8]*l,this.y=u[1]*i+u[5]*r+u[9]*l,this.z=u[2]*i+u[6]*r+u[10]*l,this.normalize()}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this}divideScalar(t){return this.multiplyScalar(1/t)}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this}clamp(t,i){return this.x=me(this.x,t.x,i.x),this.y=me(this.y,t.y,i.y),this.z=me(this.z,t.z,i.z),this}clampScalar(t,i){return this.x=me(this.x,t,i),this.y=me(this.y,t,i),this.z=me(this.z,t,i),this}clampLength(t,i){const r=this.length();return this.divideScalar(r||1).multiplyScalar(me(r,t,i))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,i){return this.x+=(t.x-this.x)*i,this.y+=(t.y-this.y)*i,this.z+=(t.z-this.z)*i,this}lerpVectors(t,i,r){return this.x=t.x+(i.x-t.x)*r,this.y=t.y+(i.y-t.y)*r,this.z=t.z+(i.z-t.z)*r,this}cross(t){return this.crossVectors(this,t)}crossVectors(t,i){const r=t.x,l=t.y,u=t.z,f=i.x,p=i.y,m=i.z;return this.x=l*m-u*p,this.y=u*f-r*m,this.z=r*p-l*f,this}projectOnVector(t){const i=t.lengthSq();if(i===0)return this.set(0,0,0);const r=t.dot(this)/i;return this.copy(t).multiplyScalar(r)}projectOnPlane(t){return yh.copy(this).projectOnVector(t),this.sub(yh)}reflect(t){return this.sub(yh.copy(t).multiplyScalar(2*this.dot(t)))}angleTo(t){const i=Math.sqrt(this.lengthSq()*t.lengthSq());if(i===0)return Math.PI/2;const r=this.dot(t)/i;return Math.acos(me(r,-1,1))}distanceTo(t){return Math.sqrt(this.distanceToSquared(t))}distanceToSquared(t){const i=this.x-t.x,r=this.y-t.y,l=this.z-t.z;return i*i+r*r+l*l}manhattanDistanceTo(t){return Math.abs(this.x-t.x)+Math.abs(this.y-t.y)+Math.abs(this.z-t.z)}setFromSpherical(t){return this.setFromSphericalCoords(t.radius,t.phi,t.theta)}setFromSphericalCoords(t,i,r){const l=Math.sin(i)*t;return this.x=l*Math.sin(r),this.y=Math.cos(i)*t,this.z=l*Math.cos(r),this}setFromCylindrical(t){return this.setFromCylindricalCoords(t.radius,t.theta,t.y)}setFromCylindricalCoords(t,i,r){return this.x=t*Math.sin(i),this.y=r,this.z=t*Math.cos(i),this}setFromMatrixPosition(t){const i=t.elements;return this.x=i[12],this.y=i[13],this.z=i[14],this}setFromMatrixScale(t){const i=this.setFromMatrixColumn(t,0).length(),r=this.setFromMatrixColumn(t,1).length(),l=this.setFromMatrixColumn(t,2).length();return this.x=i,this.y=r,this.z=l,this}setFromMatrixColumn(t,i){return this.fromArray(t.elements,i*4)}setFromMatrix3Column(t,i){return this.fromArray(t.elements,i*3)}setFromEuler(t){return this.x=t._x,this.y=t._y,this.z=t._z,this}setFromColor(t){return this.x=t.r,this.y=t.g,this.z=t.b,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z}fromArray(t,i=0){return this.x=t[i],this.y=t[i+1],this.z=t[i+2],this}toArray(t=[],i=0){return t[i]=this.x,t[i+1]=this.y,t[i+2]=this.z,t}fromBufferAttribute(t,i){return this.x=t.getX(i),this.y=t.getY(i),this.z=t.getZ(i),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const t=Math.random()*Math.PI*2,i=Math.random()*2-1,r=Math.sqrt(1-i*i);return this.x=r*Math.cos(t),this.y=i,this.z=r*Math.sin(t),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}};op.prototype.isVector3=!0;let $=op;const yh=new $,l0=new hr,lp=class lp{constructor(t,i,r,l,u,f,p,m,d){this.elements=[1,0,0,0,1,0,0,0,1],t!==void 0&&this.set(t,i,r,l,u,f,p,m,d)}set(t,i,r,l,u,f,p,m,d){const g=this.elements;return g[0]=t,g[1]=l,g[2]=p,g[3]=i,g[4]=u,g[5]=m,g[6]=r,g[7]=f,g[8]=d,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(t){const i=this.elements,r=t.elements;return i[0]=r[0],i[1]=r[1],i[2]=r[2],i[3]=r[3],i[4]=r[4],i[5]=r[5],i[6]=r[6],i[7]=r[7],i[8]=r[8],this}extractBasis(t,i,r){return t.setFromMatrix3Column(this,0),i.setFromMatrix3Column(this,1),r.setFromMatrix3Column(this,2),this}setFromMatrix4(t){const i=t.elements;return this.set(i[0],i[4],i[8],i[1],i[5],i[9],i[2],i[6],i[10]),this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,i){const r=t.elements,l=i.elements,u=this.elements,f=r[0],p=r[3],m=r[6],d=r[1],g=r[4],v=r[7],_=r[2],M=r[5],T=r[8],w=l[0],E=l[3],S=l[6],F=l[1],z=l[4],C=l[7],N=l[2],D=l[5],O=l[8];return u[0]=f*w+p*F+m*N,u[3]=f*E+p*z+m*D,u[6]=f*S+p*C+m*O,u[1]=d*w+g*F+v*N,u[4]=d*E+g*z+v*D,u[7]=d*S+g*C+v*O,u[2]=_*w+M*F+T*N,u[5]=_*E+M*z+T*D,u[8]=_*S+M*C+T*O,this}multiplyScalar(t){const i=this.elements;return i[0]*=t,i[3]*=t,i[6]*=t,i[1]*=t,i[4]*=t,i[7]*=t,i[2]*=t,i[5]*=t,i[8]*=t,this}determinant(){const t=this.elements,i=t[0],r=t[1],l=t[2],u=t[3],f=t[4],p=t[5],m=t[6],d=t[7],g=t[8];return i*f*g-i*p*d-r*u*g+r*p*m+l*u*d-l*f*m}invert(){const t=this.elements,i=t[0],r=t[1],l=t[2],u=t[3],f=t[4],p=t[5],m=t[6],d=t[7],g=t[8],v=g*f-p*d,_=p*m-g*u,M=d*u-f*m,T=i*v+r*_+l*M;if(T===0)return this.set(0,0,0,0,0,0,0,0,0);const w=1/T;return t[0]=v*w,t[1]=(l*d-g*r)*w,t[2]=(p*r-l*f)*w,t[3]=_*w,t[4]=(g*i-l*m)*w,t[5]=(l*u-p*i)*w,t[6]=M*w,t[7]=(r*m-d*i)*w,t[8]=(f*i-r*u)*w,this}transpose(){let t;const i=this.elements;return t=i[1],i[1]=i[3],i[3]=t,t=i[2],i[2]=i[6],i[6]=t,t=i[5],i[5]=i[7],i[7]=t,this}getNormalMatrix(t){return this.setFromMatrix4(t).invert().transpose()}transposeIntoArray(t){const i=this.elements;return t[0]=i[0],t[1]=i[3],t[2]=i[6],t[3]=i[1],t[4]=i[4],t[5]=i[7],t[6]=i[2],t[7]=i[5],t[8]=i[8],this}setUvTransform(t,i,r,l,u,f,p){const m=Math.cos(u),d=Math.sin(u);return this.set(r*m,r*d,-r*(m*f+d*p)+f+t,-l*d,l*m,-l*(-d*f+m*p)+p+i,0,0,1),this}scale(t,i){return Xs("Matrix3: .scale() is deprecated. Use .makeScale() instead."),this.premultiply(Mh.makeScale(t,i)),this}rotate(t){return Xs("Matrix3: .rotate() is deprecated. Use .makeRotation() instead."),this.premultiply(Mh.makeRotation(-t)),this}translate(t,i){return Xs("Matrix3: .translate() is deprecated. Use .makeTranslation() instead."),this.premultiply(Mh.makeTranslation(t,i)),this}makeTranslation(t,i){return t.isVector2?this.set(1,0,t.x,0,1,t.y,0,0,1):this.set(1,0,t,0,1,i,0,0,1),this}makeRotation(t){const i=Math.cos(t),r=Math.sin(t);return this.set(i,-r,0,r,i,0,0,0,1),this}makeScale(t,i){return this.set(t,0,0,0,i,0,0,0,1),this}equals(t){const i=this.elements,r=t.elements;for(let l=0;l<9;l++)if(i[l]!==r[l])return!1;return!0}fromArray(t,i=0){for(let r=0;r<9;r++)this.elements[r]=t[r+i];return this}toArray(t=[],i=0){const r=this.elements;return t[i]=r[0],t[i+1]=r[1],t[i+2]=r[2],t[i+3]=r[3],t[i+4]=r[4],t[i+5]=r[5],t[i+6]=r[6],t[i+7]=r[7],t[i+8]=r[8],t}clone(){return new this.constructor().fromArray(this.elements)}};lp.prototype.isMatrix3=!0;let re=lp;const Mh=new re,u0=new re().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),c0=new re().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);function Zy(){const s={enabled:!0,workingColorSpace:ju,spaces:{},convert:function(l,u,f){return this.enabled===!1||u===f||!u||!f||(this.spaces[u].transfer===Fe&&(l.r=Aa(l.r),l.g=Aa(l.g),l.b=Aa(l.b)),this.spaces[u].primaries!==this.spaces[f].primaries&&(l.applyMatrix3(this.spaces[u].toXYZ),l.applyMatrix3(this.spaces[f].fromXYZ)),this.spaces[f].transfer===Fe&&(l.r=Ws(l.r),l.g=Ws(l.g),l.b=Ws(l.b))),l},workingToColorSpace:function(l,u){return this.convert(l,this.workingColorSpace,u)},colorSpaceToWorking:function(l,u){return this.convert(l,u,this.workingColorSpace)},getPrimaries:function(l){return this.spaces[l].primaries},getTransfer:function(l){return l===ur?$u:this.spaces[l].transfer},getToneMappingMode:function(l){return this.spaces[l].outputColorSpaceConfig.toneMappingMode||"standard"},getLuminanceCoefficients:function(l,u=this.workingColorSpace){return l.fromArray(this.spaces[u].luminanceCoefficients)},define:function(l){Object.assign(this.spaces,l)},_getMatrix:function(l,u,f){return l.copy(this.spaces[u].toXYZ).multiply(this.spaces[f].fromXYZ)},_getDrawingBufferColorSpace:function(l){return this.spaces[l].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(l=this.workingColorSpace){return this.spaces[l].workingColorSpaceConfig.unpackColorSpace},fromWorkingColorSpace:function(l,u){return Xs("ColorManagement: .fromWorkingColorSpace() has been renamed to .workingToColorSpace()."),s.workingToColorSpace(l,u)},toWorkingColorSpace:function(l,u){return Xs("ColorManagement: .toWorkingColorSpace() has been renamed to .colorSpaceToWorking()."),s.colorSpaceToWorking(l,u)}},t=[.64,.33,.3,.6,.15,.06],i=[.2126,.7152,.0722],r=[.3127,.329];return s.define({[ju]:{primaries:t,whitePoint:r,transfer:$u,toXYZ:u0,fromXYZ:c0,luminanceCoefficients:i,workingColorSpaceConfig:{unpackColorSpace:ci},outputColorSpaceConfig:{drawingBufferColorSpace:ci}},[ci]:{primaries:t,whitePoint:r,transfer:Fe,toXYZ:u0,fromXYZ:c0,luminanceCoefficients:i,outputColorSpaceConfig:{drawingBufferColorSpace:ci}}}),s}const Ee=Zy();function Aa(s){return s<.04045?s*.0773993808:Math.pow(s*.9478672986+.0521327014,2.4)}function Ws(s){return s<.0031308?s*12.92:1.055*Math.pow(s,.41666)-.055}let Cs;class Ky{static getDataURL(t,i="image/png"){if(/^data:/i.test(t.src)||typeof HTMLCanvasElement>"u")return t.src;let r;if(t instanceof HTMLCanvasElement)r=t;else{Cs===void 0&&(Cs=tc("canvas")),Cs.width=t.width,Cs.height=t.height;const l=Cs.getContext("2d");t instanceof ImageData?l.putImageData(t,0,0):l.drawImage(t,0,0,t.width,t.height),r=Cs}return r.toDataURL(i)}static sRGBToLinear(t){if(typeof HTMLImageElement<"u"&&t instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&t instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&t instanceof ImageBitmap){const i=tc("canvas");i.width=t.width,i.height=t.height;const r=i.getContext("2d");r.drawImage(t,0,0,t.width,t.height);const l=r.getImageData(0,0,t.width,t.height),u=l.data;for(let f=0;f<u.length;f++)u[f]=Aa(u[f]/255)*255;return r.putImageData(l,0,0),i}else if(t.data){const i=t.data.slice(0);for(let r=0;r<i.length;r++)i instanceof Uint8Array||i instanceof Uint8ClampedArray?i[r]=Math.floor(Aa(i[r]/255)*255):i[r]=Aa(i[r]);return{data:i,width:t.width,height:t.height}}else return te("ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),t}}let Qy=0;class $d{constructor(t=null){this.isSource=!0,Object.defineProperty(this,"id",{value:Qy++}),this.uuid=sl(),this.data=t,this.dataReady=!0,this.version=0}getSize(t){const i=this.data;return typeof HTMLVideoElement<"u"&&i instanceof HTMLVideoElement?t.set(i.videoWidth,i.videoHeight,0):typeof VideoFrame<"u"&&i instanceof VideoFrame?t.set(i.displayWidth,i.displayHeight,0):i!==null?t.set(i.width,i.height,i.depth||0):t.set(0,0,0),t}set needsUpdate(t){t===!0&&this.version++}toJSON(t){const i=t===void 0||typeof t=="string";if(!i&&t.images[this.uuid]!==void 0)return t.images[this.uuid];const r={uuid:this.uuid,url:""},l=this.data;if(l!==null){let u;if(Array.isArray(l)){u=[];for(let f=0,p=l.length;f<p;f++)l[f].isDataTexture?u.push(Eh(l[f].image)):u.push(Eh(l[f]))}else u=Eh(l);r.url=u}return i||(t.images[this.uuid]=r),r}}function Eh(s){return typeof HTMLImageElement<"u"&&s instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&s instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&s instanceof ImageBitmap?Ky.getDataURL(s):s.data?{data:Array.from(s.data),width:s.width,height:s.height,type:s.data.constructor.name}:(te("Texture: Unable to serialize Texture."),{})}let Jy=0;const bh=new $;class Hn extends pr{constructor(t=Hn.DEFAULT_IMAGE,i=Hn.DEFAULT_MAPPING,r=ba,l=ba,u=In,f=Wr,p=Ni,m=fi,d=Hn.DEFAULT_ANISOTROPY,g=ur){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Jy++}),this.uuid=sl(),this.name="",this.source=new $d(t),this.mipmaps=[],this.mapping=i,this.channel=0,this.wrapS=r,this.wrapT=l,this.magFilter=u,this.minFilter=f,this.anisotropy=d,this.format=p,this.internalFormat=null,this.type=m,this.offset=new ie(0,0),this.repeat=new ie(1,1),this.center=new ie(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new re,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=g,this.userData={},this.updateRanges=[],this.version=0,this.onUpdate=null,this.renderTarget=null,this.isRenderTargetTexture=!1,this.isArrayTexture=!!(t&&t.depth&&t.depth>1),this.pmremVersion=0,this.normalized=!1}get width(){return this.source.getSize(bh).x}get height(){return this.source.getSize(bh).y}get depth(){return this.source.getSize(bh).z}get image(){return this.source.data}set image(t){this.source.data=t}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}addUpdateRange(t,i){this.updateRanges.push({start:t,count:i})}clearUpdateRanges(){this.updateRanges.length=0}clone(){return new this.constructor().copy(this)}copy(t){return this.name=t.name,this.source=t.source,this.mipmaps=t.mipmaps.slice(0),this.mapping=t.mapping,this.channel=t.channel,this.wrapS=t.wrapS,this.wrapT=t.wrapT,this.magFilter=t.magFilter,this.minFilter=t.minFilter,this.anisotropy=t.anisotropy,this.format=t.format,this.internalFormat=t.internalFormat,this.type=t.type,this.normalized=t.normalized,this.offset.copy(t.offset),this.repeat.copy(t.repeat),this.center.copy(t.center),this.rotation=t.rotation,this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrix.copy(t.matrix),this.generateMipmaps=t.generateMipmaps,this.premultiplyAlpha=t.premultiplyAlpha,this.flipY=t.flipY,this.unpackAlignment=t.unpackAlignment,this.colorSpace=t.colorSpace,this.renderTarget=t.renderTarget,this.isRenderTargetTexture=t.isRenderTargetTexture,this.isArrayTexture=t.isArrayTexture,this.userData=JSON.parse(JSON.stringify(t.userData)),this.needsUpdate=!0,this}setValues(t){for(const i in t){const r=t[i];if(r===void 0){te(`Texture.setValues(): parameter '${i}' has value of undefined.`);continue}const l=this[i];if(l===void 0){te(`Texture.setValues(): property '${i}' does not exist.`);continue}l&&r&&l.isVector2&&r.isVector2||l&&r&&l.isVector3&&r.isVector3||l&&r&&l.isMatrix3&&r.isMatrix3?l.copy(r):this[i]=r}}toJSON(t){const i=t===void 0||typeof t=="string";if(!i&&t.textures[this.uuid]!==void 0)return t.textures[this.uuid];const r={metadata:{version:4.7,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(t).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,normalized:this.normalized,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(r.userData=this.userData),i||(t.textures[this.uuid]=r),r}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(t){if(this.mapping!==Sv)return t;if(t.applyMatrix3(this.matrix),t.x<0||t.x>1)switch(this.wrapS){case od:t.x=t.x-Math.floor(t.x);break;case ba:t.x=t.x<0?0:1;break;case ld:Math.abs(Math.floor(t.x)%2)===1?t.x=Math.ceil(t.x)-t.x:t.x=t.x-Math.floor(t.x);break}if(t.y<0||t.y>1)switch(this.wrapT){case od:t.y=t.y-Math.floor(t.y);break;case ba:t.y=t.y<0?0:1;break;case ld:Math.abs(Math.floor(t.y)%2)===1?t.y=Math.ceil(t.y)-t.y:t.y=t.y-Math.floor(t.y);break}return this.flipY&&(t.y=1-t.y),t}set needsUpdate(t){t===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(t){t===!0&&this.pmremVersion++}}Hn.DEFAULT_IMAGE=null;Hn.DEFAULT_MAPPING=Sv;Hn.DEFAULT_ANISOTROPY=1;const up=class up{constructor(t=0,i=0,r=0,l=1){this.x=t,this.y=i,this.z=r,this.w=l}get width(){return this.z}set width(t){this.z=t}get height(){return this.w}set height(t){this.w=t}set(t,i,r,l){return this.x=t,this.y=i,this.z=r,this.w=l,this}setScalar(t){return this.x=t,this.y=t,this.z=t,this.w=t,this}setX(t){return this.x=t,this}setY(t){return this.y=t,this}setZ(t){return this.z=t,this}setW(t){return this.w=t,this}setComponent(t,i){switch(t){case 0:this.x=i;break;case 1:this.y=i;break;case 2:this.z=i;break;case 3:this.w=i;break;default:throw new Error("THREE.Vector4: index is out of range: "+t)}return this}getComponent(t){switch(t){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("THREE.Vector4: index is out of range: "+t)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(t){return this.x=t.x,this.y=t.y,this.z=t.z,this.w=t.w!==void 0?t.w:1,this}add(t){return this.x+=t.x,this.y+=t.y,this.z+=t.z,this.w+=t.w,this}addScalar(t){return this.x+=t,this.y+=t,this.z+=t,this.w+=t,this}addVectors(t,i){return this.x=t.x+i.x,this.y=t.y+i.y,this.z=t.z+i.z,this.w=t.w+i.w,this}addScaledVector(t,i){return this.x+=t.x*i,this.y+=t.y*i,this.z+=t.z*i,this.w+=t.w*i,this}sub(t){return this.x-=t.x,this.y-=t.y,this.z-=t.z,this.w-=t.w,this}subScalar(t){return this.x-=t,this.y-=t,this.z-=t,this.w-=t,this}subVectors(t,i){return this.x=t.x-i.x,this.y=t.y-i.y,this.z=t.z-i.z,this.w=t.w-i.w,this}multiply(t){return this.x*=t.x,this.y*=t.y,this.z*=t.z,this.w*=t.w,this}multiplyScalar(t){return this.x*=t,this.y*=t,this.z*=t,this.w*=t,this}applyMatrix4(t){const i=this.x,r=this.y,l=this.z,u=this.w,f=t.elements;return this.x=f[0]*i+f[4]*r+f[8]*l+f[12]*u,this.y=f[1]*i+f[5]*r+f[9]*l+f[13]*u,this.z=f[2]*i+f[6]*r+f[10]*l+f[14]*u,this.w=f[3]*i+f[7]*r+f[11]*l+f[15]*u,this}divide(t){return this.x/=t.x,this.y/=t.y,this.z/=t.z,this.w/=t.w,this}divideScalar(t){return this.multiplyScalar(1/t)}setAxisAngleFromQuaternion(t){this.w=2*Math.acos(t.w);const i=Math.sqrt(1-t.w*t.w);return i<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=t.x/i,this.y=t.y/i,this.z=t.z/i),this}setAxisAngleFromRotationMatrix(t){let i,r,l,u;const m=t.elements,d=m[0],g=m[4],v=m[8],_=m[1],M=m[5],T=m[9],w=m[2],E=m[6],S=m[10];if(Math.abs(g-_)<.01&&Math.abs(v-w)<.01&&Math.abs(T-E)<.01){if(Math.abs(g+_)<.1&&Math.abs(v+w)<.1&&Math.abs(T+E)<.1&&Math.abs(d+M+S-3)<.1)return this.set(1,0,0,0),this;i=Math.PI;const z=(d+1)/2,C=(M+1)/2,N=(S+1)/2,D=(g+_)/4,O=(v+w)/4,b=(T+E)/4;return z>C&&z>N?z<.01?(r=0,l=.707106781,u=.707106781):(r=Math.sqrt(z),l=D/r,u=O/r):C>N?C<.01?(r=.707106781,l=0,u=.707106781):(l=Math.sqrt(C),r=D/l,u=b/l):N<.01?(r=.707106781,l=.707106781,u=0):(u=Math.sqrt(N),r=O/u,l=b/u),this.set(r,l,u,i),this}let F=Math.sqrt((E-T)*(E-T)+(v-w)*(v-w)+(_-g)*(_-g));return Math.abs(F)<.001&&(F=1),this.x=(E-T)/F,this.y=(v-w)/F,this.z=(_-g)/F,this.w=Math.acos((d+M+S-1)/2),this}setFromMatrixPosition(t){const i=t.elements;return this.x=i[12],this.y=i[13],this.z=i[14],this.w=i[15],this}min(t){return this.x=Math.min(this.x,t.x),this.y=Math.min(this.y,t.y),this.z=Math.min(this.z,t.z),this.w=Math.min(this.w,t.w),this}max(t){return this.x=Math.max(this.x,t.x),this.y=Math.max(this.y,t.y),this.z=Math.max(this.z,t.z),this.w=Math.max(this.w,t.w),this}clamp(t,i){return this.x=me(this.x,t.x,i.x),this.y=me(this.y,t.y,i.y),this.z=me(this.z,t.z,i.z),this.w=me(this.w,t.w,i.w),this}clampScalar(t,i){return this.x=me(this.x,t,i),this.y=me(this.y,t,i),this.z=me(this.z,t,i),this.w=me(this.w,t,i),this}clampLength(t,i){const r=this.length();return this.divideScalar(r||1).multiplyScalar(me(r,t,i))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(t){return this.x*t.x+this.y*t.y+this.z*t.z+this.w*t.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(t){return this.normalize().multiplyScalar(t)}lerp(t,i){return this.x+=(t.x-this.x)*i,this.y+=(t.y-this.y)*i,this.z+=(t.z-this.z)*i,this.w+=(t.w-this.w)*i,this}lerpVectors(t,i,r){return this.x=t.x+(i.x-t.x)*r,this.y=t.y+(i.y-t.y)*r,this.z=t.z+(i.z-t.z)*r,this.w=t.w+(i.w-t.w)*r,this}equals(t){return t.x===this.x&&t.y===this.y&&t.z===this.z&&t.w===this.w}fromArray(t,i=0){return this.x=t[i],this.y=t[i+1],this.z=t[i+2],this.w=t[i+3],this}toArray(t=[],i=0){return t[i]=this.x,t[i+1]=this.y,t[i+2]=this.z,t[i+3]=this.w,t}fromBufferAttribute(t,i){return this.x=t.getX(i),this.y=t.getY(i),this.z=t.getZ(i),this.w=t.getW(i),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}};up.prototype.isVector4=!0;let tn=up;class jy extends pr{constructor(t=1,i=1,r={}){super(),r=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:In,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1,depth:1,multiview:!1,useArrayDepthTexture:!1},r),this.isRenderTarget=!0,this.width=t,this.height=i,this.depth=r.depth,this.scissor=new tn(0,0,t,i),this.scissorTest=!1,this.viewport=new tn(0,0,t,i),this.textures=[];const l={width:t,height:i,depth:r.depth},u=new Hn(l),f=r.count;for(let p=0;p<f;p++)this.textures[p]=u.clone(),this.textures[p].isRenderTargetTexture=!0,this.textures[p].renderTarget=this;this._setTextureOptions(r),this.depthBuffer=r.depthBuffer,this.stencilBuffer=r.stencilBuffer,this.resolveDepthBuffer=r.resolveDepthBuffer,this.resolveStencilBuffer=r.resolveStencilBuffer,this._depthTexture=null,this.depthTexture=r.depthTexture,this.samples=r.samples,this.multiview=r.multiview,this.useArrayDepthTexture=r.useArrayDepthTexture}_setTextureOptions(t={}){const i={minFilter:In,generateMipmaps:!1,flipY:!1,internalFormat:null};t.mapping!==void 0&&(i.mapping=t.mapping),t.wrapS!==void 0&&(i.wrapS=t.wrapS),t.wrapT!==void 0&&(i.wrapT=t.wrapT),t.wrapR!==void 0&&(i.wrapR=t.wrapR),t.magFilter!==void 0&&(i.magFilter=t.magFilter),t.minFilter!==void 0&&(i.minFilter=t.minFilter),t.format!==void 0&&(i.format=t.format),t.type!==void 0&&(i.type=t.type),t.anisotropy!==void 0&&(i.anisotropy=t.anisotropy),t.colorSpace!==void 0&&(i.colorSpace=t.colorSpace),t.flipY!==void 0&&(i.flipY=t.flipY),t.generateMipmaps!==void 0&&(i.generateMipmaps=t.generateMipmaps),t.internalFormat!==void 0&&(i.internalFormat=t.internalFormat);for(let r=0;r<this.textures.length;r++)this.textures[r].setValues(i)}get texture(){return this.textures[0]}set texture(t){this.textures[0]=t}set depthTexture(t){this._depthTexture!==null&&(this._depthTexture.renderTarget=null),t!==null&&(t.renderTarget=this),this._depthTexture=t}get depthTexture(){return this._depthTexture}setSize(t,i,r=1){if(this.width!==t||this.height!==i||this.depth!==r){this.width=t,this.height=i,this.depth=r;for(let l=0,u=this.textures.length;l<u;l++)this.textures[l].image.width=t,this.textures[l].image.height=i,this.textures[l].image.depth=r,this.textures[l].isData3DTexture!==!0&&(this.textures[l].isArrayTexture=this.textures[l].image.depth>1);this.dispose()}this.viewport.set(0,0,t,i),this.scissor.set(0,0,t,i)}clone(){return new this.constructor().copy(this)}copy(t){this.width=t.width,this.height=t.height,this.depth=t.depth,this.scissor.copy(t.scissor),this.scissorTest=t.scissorTest,this.viewport.copy(t.viewport),this.textures.length=0;for(let i=0,r=t.textures.length;i<r;i++){this.textures[i]=t.textures[i].clone(),this.textures[i].isRenderTargetTexture=!0,this.textures[i].renderTarget=this;const l=Object.assign({},t.textures[i].image);this.textures[i].source=new $d(l)}return this.depthBuffer=t.depthBuffer,this.stencilBuffer=t.stencilBuffer,this.resolveDepthBuffer=t.resolveDepthBuffer,this.resolveStencilBuffer=t.resolveStencilBuffer,t.depthTexture!==null&&(this.depthTexture=t.depthTexture.clone()),this.samples=t.samples,this.multiview=t.multiview,this.useArrayDepthTexture=t.useArrayDepthTexture,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Zi extends jy{constructor(t=1,i=1,r={}){super(t,i,r),this.isWebGLRenderTarget=!0}}class wv extends Hn{constructor(t=null,i=1,r=1,l=1){super(null),this.isDataArrayTexture=!0,this.image={data:t,width:i,height:r,depth:l},this.magFilter=Dn,this.minFilter=Dn,this.wrapR=ba,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(t){this.layerUpdates.add(t)}clearLayerUpdates(){this.layerUpdates.clear()}}class $y extends Hn{constructor(t=null,i=1,r=1,l=1){super(null),this.isData3DTexture=!0,this.image={data:t,width:i,height:r,depth:l},this.magFilter=Dn,this.minFilter=Dn,this.wrapR=ba,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const ec=class ec{constructor(t,i,r,l,u,f,p,m,d,g,v,_,M,T,w,E){this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],t!==void 0&&this.set(t,i,r,l,u,f,p,m,d,g,v,_,M,T,w,E)}set(t,i,r,l,u,f,p,m,d,g,v,_,M,T,w,E){const S=this.elements;return S[0]=t,S[4]=i,S[8]=r,S[12]=l,S[1]=u,S[5]=f,S[9]=p,S[13]=m,S[2]=d,S[6]=g,S[10]=v,S[14]=_,S[3]=M,S[7]=T,S[11]=w,S[15]=E,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new ec().fromArray(this.elements)}copy(t){const i=this.elements,r=t.elements;return i[0]=r[0],i[1]=r[1],i[2]=r[2],i[3]=r[3],i[4]=r[4],i[5]=r[5],i[6]=r[6],i[7]=r[7],i[8]=r[8],i[9]=r[9],i[10]=r[10],i[11]=r[11],i[12]=r[12],i[13]=r[13],i[14]=r[14],i[15]=r[15],this}copyPosition(t){const i=this.elements,r=t.elements;return i[12]=r[12],i[13]=r[13],i[14]=r[14],this}setFromMatrix3(t){const i=t.elements;return this.set(i[0],i[3],i[6],0,i[1],i[4],i[7],0,i[2],i[5],i[8],0,0,0,0,1),this}extractBasis(t,i,r){return this.determinantAffine()===0?(t.set(1,0,0),i.set(0,1,0),r.set(0,0,1),this):(t.setFromMatrixColumn(this,0),i.setFromMatrixColumn(this,1),r.setFromMatrixColumn(this,2),this)}makeBasis(t,i,r){return this.set(t.x,i.x,r.x,0,t.y,i.y,r.y,0,t.z,i.z,r.z,0,0,0,0,1),this}extractRotation(t){if(t.determinantAffine()===0)return this.identity();const i=this.elements,r=t.elements,l=1/ws.setFromMatrixColumn(t,0).length(),u=1/ws.setFromMatrixColumn(t,1).length(),f=1/ws.setFromMatrixColumn(t,2).length();return i[0]=r[0]*l,i[1]=r[1]*l,i[2]=r[2]*l,i[3]=0,i[4]=r[4]*u,i[5]=r[5]*u,i[6]=r[6]*u,i[7]=0,i[8]=r[8]*f,i[9]=r[9]*f,i[10]=r[10]*f,i[11]=0,i[12]=0,i[13]=0,i[14]=0,i[15]=1,this}makeRotationFromEuler(t){const i=this.elements,r=t.x,l=t.y,u=t.z,f=Math.cos(r),p=Math.sin(r),m=Math.cos(l),d=Math.sin(l),g=Math.cos(u),v=Math.sin(u);if(t.order==="XYZ"){const _=f*g,M=f*v,T=p*g,w=p*v;i[0]=m*g,i[4]=-m*v,i[8]=d,i[1]=M+T*d,i[5]=_-w*d,i[9]=-p*m,i[2]=w-_*d,i[6]=T+M*d,i[10]=f*m}else if(t.order==="YXZ"){const _=m*g,M=m*v,T=d*g,w=d*v;i[0]=_+w*p,i[4]=T*p-M,i[8]=f*d,i[1]=f*v,i[5]=f*g,i[9]=-p,i[2]=M*p-T,i[6]=w+_*p,i[10]=f*m}else if(t.order==="ZXY"){const _=m*g,M=m*v,T=d*g,w=d*v;i[0]=_-w*p,i[4]=-f*v,i[8]=T+M*p,i[1]=M+T*p,i[5]=f*g,i[9]=w-_*p,i[2]=-f*d,i[6]=p,i[10]=f*m}else if(t.order==="ZYX"){const _=f*g,M=f*v,T=p*g,w=p*v;i[0]=m*g,i[4]=T*d-M,i[8]=_*d+w,i[1]=m*v,i[5]=w*d+_,i[9]=M*d-T,i[2]=-d,i[6]=p*m,i[10]=f*m}else if(t.order==="YZX"){const _=f*m,M=f*d,T=p*m,w=p*d;i[0]=m*g,i[4]=w-_*v,i[8]=T*v+M,i[1]=v,i[5]=f*g,i[9]=-p*g,i[2]=-d*g,i[6]=M*v+T,i[10]=_-w*v}else if(t.order==="XZY"){const _=f*m,M=f*d,T=p*m,w=p*d;i[0]=m*g,i[4]=-v,i[8]=d*g,i[1]=_*v+w,i[5]=f*g,i[9]=M*v-T,i[2]=T*v-M,i[6]=p*g,i[10]=w*v+_}return i[3]=0,i[7]=0,i[11]=0,i[12]=0,i[13]=0,i[14]=0,i[15]=1,this}makeRotationFromQuaternion(t){return this.compose(tM,t,eM)}lookAt(t,i,r){const l=this.elements;return li.subVectors(t,i),li.lengthSq()===0&&(li.z=1),li.normalize(),nr.crossVectors(r,li),nr.lengthSq()===0&&(Math.abs(r.z)===1?li.x+=1e-4:li.z+=1e-4,li.normalize(),nr.crossVectors(r,li)),nr.normalize(),Su.crossVectors(li,nr),l[0]=nr.x,l[4]=Su.x,l[8]=li.x,l[1]=nr.y,l[5]=Su.y,l[9]=li.y,l[2]=nr.z,l[6]=Su.z,l[10]=li.z,this}multiply(t){return this.multiplyMatrices(this,t)}premultiply(t){return this.multiplyMatrices(t,this)}multiplyMatrices(t,i){const r=t.elements,l=i.elements,u=this.elements,f=r[0],p=r[4],m=r[8],d=r[12],g=r[1],v=r[5],_=r[9],M=r[13],T=r[2],w=r[6],E=r[10],S=r[14],F=r[3],z=r[7],C=r[11],N=r[15],D=l[0],O=l[4],b=l[8],P=l[12],q=l[1],G=l[5],Z=l[9],ht=l[13],mt=l[2],J=l[6],I=l[10],H=l[14],j=l[3],gt=l[7],Et=l[11],L=l[15];return u[0]=f*D+p*q+m*mt+d*j,u[4]=f*O+p*G+m*J+d*gt,u[8]=f*b+p*Z+m*I+d*Et,u[12]=f*P+p*ht+m*H+d*L,u[1]=g*D+v*q+_*mt+M*j,u[5]=g*O+v*G+_*J+M*gt,u[9]=g*b+v*Z+_*I+M*Et,u[13]=g*P+v*ht+_*H+M*L,u[2]=T*D+w*q+E*mt+S*j,u[6]=T*O+w*G+E*J+S*gt,u[10]=T*b+w*Z+E*I+S*Et,u[14]=T*P+w*ht+E*H+S*L,u[3]=F*D+z*q+C*mt+N*j,u[7]=F*O+z*G+C*J+N*gt,u[11]=F*b+z*Z+C*I+N*Et,u[15]=F*P+z*ht+C*H+N*L,this}multiplyScalar(t){const i=this.elements;return i[0]*=t,i[4]*=t,i[8]*=t,i[12]*=t,i[1]*=t,i[5]*=t,i[9]*=t,i[13]*=t,i[2]*=t,i[6]*=t,i[10]*=t,i[14]*=t,i[3]*=t,i[7]*=t,i[11]*=t,i[15]*=t,this}determinant(){const t=this.elements,i=t[0],r=t[4],l=t[8],u=t[12],f=t[1],p=t[5],m=t[9],d=t[13],g=t[2],v=t[6],_=t[10],M=t[14],T=t[3],w=t[7],E=t[11],S=t[15],F=m*M-d*_,z=p*M-d*v,C=p*_-m*v,N=f*M-d*g,D=f*_-m*g,O=f*v-p*g;return i*(w*F-E*z+S*C)-r*(T*F-E*N+S*D)+l*(T*z-w*N+S*O)-u*(T*C-w*D+E*O)}determinantAffine(){const t=this.elements,i=t[0],r=t[4],l=t[8],u=t[1],f=t[5],p=t[9],m=t[2],d=t[6],g=t[10];return i*(f*g-p*d)-r*(u*g-p*m)+l*(u*d-f*m)}transpose(){const t=this.elements;let i;return i=t[1],t[1]=t[4],t[4]=i,i=t[2],t[2]=t[8],t[8]=i,i=t[6],t[6]=t[9],t[9]=i,i=t[3],t[3]=t[12],t[12]=i,i=t[7],t[7]=t[13],t[13]=i,i=t[11],t[11]=t[14],t[14]=i,this}setPosition(t,i,r){const l=this.elements;return t.isVector3?(l[12]=t.x,l[13]=t.y,l[14]=t.z):(l[12]=t,l[13]=i,l[14]=r),this}invert(){const t=this.elements,i=t[0],r=t[1],l=t[2],u=t[3],f=t[4],p=t[5],m=t[6],d=t[7],g=t[8],v=t[9],_=t[10],M=t[11],T=t[12],w=t[13],E=t[14],S=t[15],F=i*p-r*f,z=i*m-l*f,C=i*d-u*f,N=r*m-l*p,D=r*d-u*p,O=l*d-u*m,b=g*w-v*T,P=g*E-_*T,q=g*S-M*T,G=v*E-_*w,Z=v*S-M*w,ht=_*S-M*E,mt=F*ht-z*Z+C*G+N*q-D*P+O*b;if(mt===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const J=1/mt;return t[0]=(p*ht-m*Z+d*G)*J,t[1]=(l*Z-r*ht-u*G)*J,t[2]=(w*O-E*D+S*N)*J,t[3]=(_*D-v*O-M*N)*J,t[4]=(m*q-f*ht-d*P)*J,t[5]=(i*ht-l*q+u*P)*J,t[6]=(E*C-T*O-S*z)*J,t[7]=(g*O-_*C+M*z)*J,t[8]=(f*Z-p*q+d*b)*J,t[9]=(r*q-i*Z-u*b)*J,t[10]=(T*D-w*C+S*F)*J,t[11]=(v*C-g*D-M*F)*J,t[12]=(p*P-f*G-m*b)*J,t[13]=(i*G-r*P+l*b)*J,t[14]=(w*z-T*N-E*F)*J,t[15]=(g*N-v*z+_*F)*J,this}scale(t){const i=this.elements,r=t.x,l=t.y,u=t.z;return i[0]*=r,i[4]*=l,i[8]*=u,i[1]*=r,i[5]*=l,i[9]*=u,i[2]*=r,i[6]*=l,i[10]*=u,i[3]*=r,i[7]*=l,i[11]*=u,this}getMaxScaleOnAxis(){const t=this.elements,i=t[0]*t[0]+t[1]*t[1]+t[2]*t[2],r=t[4]*t[4]+t[5]*t[5]+t[6]*t[6],l=t[8]*t[8]+t[9]*t[9]+t[10]*t[10];return Math.sqrt(Math.max(i,r,l))}makeTranslation(t,i,r){return t.isVector3?this.set(1,0,0,t.x,0,1,0,t.y,0,0,1,t.z,0,0,0,1):this.set(1,0,0,t,0,1,0,i,0,0,1,r,0,0,0,1),this}makeRotationX(t){const i=Math.cos(t),r=Math.sin(t);return this.set(1,0,0,0,0,i,-r,0,0,r,i,0,0,0,0,1),this}makeRotationY(t){const i=Math.cos(t),r=Math.sin(t);return this.set(i,0,r,0,0,1,0,0,-r,0,i,0,0,0,0,1),this}makeRotationZ(t){const i=Math.cos(t),r=Math.sin(t);return this.set(i,-r,0,0,r,i,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(t,i){const r=Math.cos(i),l=Math.sin(i),u=1-r,f=t.x,p=t.y,m=t.z,d=u*f,g=u*p;return this.set(d*f+r,d*p-l*m,d*m+l*p,0,d*p+l*m,g*p+r,g*m-l*f,0,d*m-l*p,g*m+l*f,u*m*m+r,0,0,0,0,1),this}makeScale(t,i,r){return this.set(t,0,0,0,0,i,0,0,0,0,r,0,0,0,0,1),this}makeShear(t,i,r,l,u,f){return this.set(1,r,u,0,t,1,f,0,i,l,1,0,0,0,0,1),this}compose(t,i,r){const l=this.elements,u=i._x,f=i._y,p=i._z,m=i._w,d=u+u,g=f+f,v=p+p,_=u*d,M=u*g,T=u*v,w=f*g,E=f*v,S=p*v,F=m*d,z=m*g,C=m*v,N=r.x,D=r.y,O=r.z;return l[0]=(1-(w+S))*N,l[1]=(M+C)*N,l[2]=(T-z)*N,l[3]=0,l[4]=(M-C)*D,l[5]=(1-(_+S))*D,l[6]=(E+F)*D,l[7]=0,l[8]=(T+z)*O,l[9]=(E-F)*O,l[10]=(1-(_+w))*O,l[11]=0,l[12]=t.x,l[13]=t.y,l[14]=t.z,l[15]=1,this}decompose(t,i,r){const l=this.elements;t.x=l[12],t.y=l[13],t.z=l[14];const u=this.determinantAffine();if(u===0)return r.set(1,1,1),i.identity(),this;let f=ws.set(l[0],l[1],l[2]).length();const p=ws.set(l[4],l[5],l[6]).length(),m=ws.set(l[8],l[9],l[10]).length();u<0&&(f=-f),wi.copy(this);const d=1/f,g=1/p,v=1/m;return wi.elements[0]*=d,wi.elements[1]*=d,wi.elements[2]*=d,wi.elements[4]*=g,wi.elements[5]*=g,wi.elements[6]*=g,wi.elements[8]*=v,wi.elements[9]*=v,wi.elements[10]*=v,i.setFromRotationMatrix(wi),r.x=f,r.y=p,r.z=m,this}makePerspective(t,i,r,l,u,f,p=qi,m=!1){const d=this.elements,g=2*u/(i-t),v=2*u/(r-l),_=(i+t)/(i-t),M=(r+l)/(r-l);let T,w;if(m)T=u/(f-u),w=f*u/(f-u);else if(p===qi)T=-(f+u)/(f-u),w=-2*f*u/(f-u);else if(p===rl)T=-f/(f-u),w=-f*u/(f-u);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+p);return d[0]=g,d[4]=0,d[8]=_,d[12]=0,d[1]=0,d[5]=v,d[9]=M,d[13]=0,d[2]=0,d[6]=0,d[10]=T,d[14]=w,d[3]=0,d[7]=0,d[11]=-1,d[15]=0,this}makeOrthographic(t,i,r,l,u,f,p=qi,m=!1){const d=this.elements,g=2/(i-t),v=2/(r-l),_=-(i+t)/(i-t),M=-(r+l)/(r-l);let T,w;if(m)T=1/(f-u),w=f/(f-u);else if(p===qi)T=-2/(f-u),w=-(f+u)/(f-u);else if(p===rl)T=-1/(f-u),w=-u/(f-u);else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+p);return d[0]=g,d[4]=0,d[8]=0,d[12]=_,d[1]=0,d[5]=v,d[9]=0,d[13]=M,d[2]=0,d[6]=0,d[10]=T,d[14]=w,d[3]=0,d[7]=0,d[11]=0,d[15]=1,this}equals(t){const i=this.elements,r=t.elements;for(let l=0;l<16;l++)if(i[l]!==r[l])return!1;return!0}fromArray(t,i=0){for(let r=0;r<16;r++)this.elements[r]=t[r+i];return this}toArray(t=[],i=0){const r=this.elements;return t[i]=r[0],t[i+1]=r[1],t[i+2]=r[2],t[i+3]=r[3],t[i+4]=r[4],t[i+5]=r[5],t[i+6]=r[6],t[i+7]=r[7],t[i+8]=r[8],t[i+9]=r[9],t[i+10]=r[10],t[i+11]=r[11],t[i+12]=r[12],t[i+13]=r[13],t[i+14]=r[14],t[i+15]=r[15],t}};ec.prototype.isMatrix4=!0;let $e=ec;const ws=new $,wi=new $e,tM=new $(0,0,0),eM=new $(1,1,1),nr=new $,Su=new $,li=new $,f0=new $e,h0=new hr;class dr{constructor(t=0,i=0,r=0,l=dr.DEFAULT_ORDER){this.isEuler=!0,this._x=t,this._y=i,this._z=r,this._order=l}get x(){return this._x}set x(t){this._x=t,this._onChangeCallback()}get y(){return this._y}set y(t){this._y=t,this._onChangeCallback()}get z(){return this._z}set z(t){this._z=t,this._onChangeCallback()}get order(){return this._order}set order(t){this._order=t,this._onChangeCallback()}set(t,i,r,l=this._order){return this._x=t,this._y=i,this._z=r,this._order=l,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(t){return this._x=t._x,this._y=t._y,this._z=t._z,this._order=t._order,this._onChangeCallback(),this}setFromRotationMatrix(t,i=this._order,r=!0){const l=t.elements,u=l[0],f=l[4],p=l[8],m=l[1],d=l[5],g=l[9],v=l[2],_=l[6],M=l[10];switch(i){case"XYZ":this._y=Math.asin(me(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(-g,M),this._z=Math.atan2(-f,u)):(this._x=Math.atan2(_,d),this._z=0);break;case"YXZ":this._x=Math.asin(-me(g,-1,1)),Math.abs(g)<.9999999?(this._y=Math.atan2(p,M),this._z=Math.atan2(m,d)):(this._y=Math.atan2(-v,u),this._z=0);break;case"ZXY":this._x=Math.asin(me(_,-1,1)),Math.abs(_)<.9999999?(this._y=Math.atan2(-v,M),this._z=Math.atan2(-f,d)):(this._y=0,this._z=Math.atan2(m,u));break;case"ZYX":this._y=Math.asin(-me(v,-1,1)),Math.abs(v)<.9999999?(this._x=Math.atan2(_,M),this._z=Math.atan2(m,u)):(this._x=0,this._z=Math.atan2(-f,d));break;case"YZX":this._z=Math.asin(me(m,-1,1)),Math.abs(m)<.9999999?(this._x=Math.atan2(-g,d),this._y=Math.atan2(-v,u)):(this._x=0,this._y=Math.atan2(p,M));break;case"XZY":this._z=Math.asin(-me(f,-1,1)),Math.abs(f)<.9999999?(this._x=Math.atan2(_,d),this._y=Math.atan2(p,u)):(this._x=Math.atan2(-g,M),this._y=0);break;default:te("Euler: .setFromRotationMatrix() encountered an unknown order: "+i)}return this._order=i,r===!0&&this._onChangeCallback(),this}setFromQuaternion(t,i,r){return f0.makeRotationFromQuaternion(t),this.setFromRotationMatrix(f0,i,r)}setFromVector3(t,i=this._order){return this.set(t.x,t.y,t.z,i)}reorder(t){return h0.setFromEuler(this),this.setFromQuaternion(h0,t)}equals(t){return t._x===this._x&&t._y===this._y&&t._z===this._z&&t._order===this._order}fromArray(t){return this._x=t[0],this._y=t[1],this._z=t[2],t[3]!==void 0&&(this._order=t[3]),this._onChangeCallback(),this}toArray(t=[],i=0){return t[i]=this._x,t[i+1]=this._y,t[i+2]=this._z,t[i+3]=this._order,t}_onChange(t){return this._onChangeCallback=t,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}dr.DEFAULT_ORDER="XYZ";class Dv{constructor(){this.mask=1}set(t){this.mask=(1<<t|0)>>>0}enable(t){this.mask|=1<<t|0}enableAll(){this.mask=-1}toggle(t){this.mask^=1<<t|0}disable(t){this.mask&=~(1<<t|0)}disableAll(){this.mask=0}test(t){return(this.mask&t.mask)!==0}isEnabled(t){return(this.mask&(1<<t|0))!==0}}let nM=0;const d0=new $,Ds=new hr,_a=new $e,yu=new $,Yo=new $,iM=new $,aM=new hr,p0=new $(1,0,0),m0=new $(0,1,0),g0=new $(0,0,1),_0={type:"added"},rM={type:"removed"},Us={type:"childadded",child:null},Th={type:"childremoved",child:null};class Un extends pr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:nM++}),this.uuid=sl(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Un.DEFAULT_UP.clone();const t=new $,i=new dr,r=new hr,l=new $(1,1,1);function u(){r.setFromEuler(i,!1)}function f(){i.setFromQuaternion(r,void 0,!1)}i._onChange(u),r._onChange(f),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:t},rotation:{configurable:!0,enumerable:!0,value:i},quaternion:{configurable:!0,enumerable:!0,value:r},scale:{configurable:!0,enumerable:!0,value:l},modelViewMatrix:{value:new $e},normalMatrix:{value:new re}}),this.matrix=new $e,this.matrixWorld=new $e,this.matrixAutoUpdate=Un.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Un.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Dv,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.customDepthMaterial=void 0,this.customDistanceMaterial=void 0,this.static=!1,this.userData={},this.pivot=null}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(t){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(t),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(t){return this.quaternion.premultiply(t),this}setRotationFromAxisAngle(t,i){this.quaternion.setFromAxisAngle(t,i)}setRotationFromEuler(t){this.quaternion.setFromEuler(t,!0)}setRotationFromMatrix(t){this.quaternion.setFromRotationMatrix(t)}setRotationFromQuaternion(t){this.quaternion.copy(t)}rotateOnAxis(t,i){return Ds.setFromAxisAngle(t,i),this.quaternion.multiply(Ds),this}rotateOnWorldAxis(t,i){return Ds.setFromAxisAngle(t,i),this.quaternion.premultiply(Ds),this}rotateX(t){return this.rotateOnAxis(p0,t)}rotateY(t){return this.rotateOnAxis(m0,t)}rotateZ(t){return this.rotateOnAxis(g0,t)}translateOnAxis(t,i){return d0.copy(t).applyQuaternion(this.quaternion),this.position.add(d0.multiplyScalar(i)),this}translateX(t){return this.translateOnAxis(p0,t)}translateY(t){return this.translateOnAxis(m0,t)}translateZ(t){return this.translateOnAxis(g0,t)}localToWorld(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(this.matrixWorld)}worldToLocal(t){return this.updateWorldMatrix(!0,!1),t.applyMatrix4(_a.copy(this.matrixWorld).invert())}lookAt(t,i,r){t.isVector3?yu.copy(t):yu.set(t,i,r);const l=this.parent;this.updateWorldMatrix(!0,!1),Yo.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?_a.lookAt(Yo,yu,this.up):_a.lookAt(yu,Yo,this.up),this.quaternion.setFromRotationMatrix(_a),l&&(_a.extractRotation(l.matrixWorld),Ds.setFromRotationMatrix(_a),this.quaternion.premultiply(Ds.invert()))}add(t){if(arguments.length>1){for(let i=0;i<arguments.length;i++)this.add(arguments[i]);return this}return t===this?(be("Object3D.add: object can't be added as a child of itself.",t),this):(t&&t.isObject3D?(t.removeFromParent(),t.parent=this,this.children.push(t),t.dispatchEvent(_0),Us.child=t,this.dispatchEvent(Us),Us.child=null):be("Object3D.add: object not an instance of THREE.Object3D.",t),this)}remove(t){if(arguments.length>1){for(let r=0;r<arguments.length;r++)this.remove(arguments[r]);return this}const i=this.children.indexOf(t);return i!==-1&&(t.parent=null,this.children.splice(i,1),t.dispatchEvent(rM),Th.child=t,this.dispatchEvent(Th),Th.child=null),this}removeFromParent(){const t=this.parent;return t!==null&&t.remove(this),this}clear(){return this.remove(...this.children)}attach(t){return this.updateWorldMatrix(!0,!1),_a.copy(this.matrixWorld).invert(),t.parent!==null&&(t.parent.updateWorldMatrix(!0,!1),_a.multiply(t.parent.matrixWorld)),t.applyMatrix4(_a),t.removeFromParent(),t.parent=this,this.children.push(t),t.updateWorldMatrix(!1,!0),t.dispatchEvent(_0),Us.child=t,this.dispatchEvent(Us),Us.child=null,this}getObjectById(t){return this.getObjectByProperty("id",t)}getObjectByName(t){return this.getObjectByProperty("name",t)}getObjectByProperty(t,i){if(this[t]===i)return this;for(let r=0,l=this.children.length;r<l;r++){const f=this.children[r].getObjectByProperty(t,i);if(f!==void 0)return f}}getObjectsByProperty(t,i,r=[]){this[t]===i&&r.push(this);const l=this.children;for(let u=0,f=l.length;u<f;u++)l[u].getObjectsByProperty(t,i,r);return r}getWorldPosition(t){return this.updateWorldMatrix(!0,!1),t.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Yo,t,iM),t}getWorldScale(t){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Yo,aM,t),t}getWorldDirection(t){this.updateWorldMatrix(!0,!1);const i=this.matrixWorld.elements;return t.set(i[8],i[9],i[10]).normalize()}raycast(){}traverse(t){t(this);const i=this.children;for(let r=0,l=i.length;r<l;r++)i[r].traverse(t)}traverseVisible(t){if(this.visible===!1)return;t(this);const i=this.children;for(let r=0,l=i.length;r<l;r++)i[r].traverseVisible(t)}traverseAncestors(t){const i=this.parent;i!==null&&(t(i),i.traverseAncestors(t))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale);const t=this.pivot;if(t!==null){const i=t.x,r=t.y,l=t.z,u=this.matrix.elements;u[12]+=i-u[0]*i-u[4]*r-u[8]*l,u[13]+=r-u[1]*i-u[5]*r-u[9]*l,u[14]+=l-u[2]*i-u[6]*r-u[10]*l}this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(t){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||t)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,t=!0);const i=this.children;for(let r=0,l=i.length;r<l;r++)i[r].updateMatrixWorld(t)}updateWorldMatrix(t,i,r=!1){const l=this.parent;if(t===!0&&l!==null&&l.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||r)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,r=!0),i===!0){const u=this.children;for(let f=0,p=u.length;f<p;f++)u[f].updateWorldMatrix(!1,!0,r)}}toJSON(t){const i=t===void 0||typeof t=="string",r={};i&&(t={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},r.metadata={version:4.7,type:"Object",generator:"Object3D.toJSON"});const l={};l.uuid=this.uuid,l.type=this.type,this.name!==""&&(l.name=this.name),this.castShadow===!0&&(l.castShadow=!0),this.receiveShadow===!0&&(l.receiveShadow=!0),this.visible===!1&&(l.visible=!1),this.frustumCulled===!1&&(l.frustumCulled=!1),this.renderOrder!==0&&(l.renderOrder=this.renderOrder),this.static!==!1&&(l.static=this.static),Object.keys(this.userData).length>0&&(l.userData=this.userData),l.layers=this.layers.mask,l.matrix=this.matrix.toArray(),l.up=this.up.toArray(),this.pivot!==null&&(l.pivot=this.pivot.toArray()),this.matrixAutoUpdate===!1&&(l.matrixAutoUpdate=!1),this.morphTargetDictionary!==void 0&&(l.morphTargetDictionary=Object.assign({},this.morphTargetDictionary)),this.morphTargetInfluences!==void 0&&(l.morphTargetInfluences=this.morphTargetInfluences.slice()),this.isInstancedMesh&&(l.type="InstancedMesh",l.count=this.count,l.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(l.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(l.type="BatchedMesh",l.perObjectFrustumCulled=this.perObjectFrustumCulled,l.sortObjects=this.sortObjects,l.drawRanges=this._drawRanges,l.reservedRanges=this._reservedRanges,l.geometryInfo=this._geometryInfo.map(p=>({...p,boundingBox:p.boundingBox?p.boundingBox.toJSON():void 0,boundingSphere:p.boundingSphere?p.boundingSphere.toJSON():void 0})),l.instanceInfo=this._instanceInfo.map(p=>({...p})),l.availableInstanceIds=this._availableInstanceIds.slice(),l.availableGeometryIds=this._availableGeometryIds.slice(),l.nextIndexStart=this._nextIndexStart,l.nextVertexStart=this._nextVertexStart,l.geometryCount=this._geometryCount,l.maxInstanceCount=this._maxInstanceCount,l.maxVertexCount=this._maxVertexCount,l.maxIndexCount=this._maxIndexCount,l.geometryInitialized=this._geometryInitialized,l.matricesTexture=this._matricesTexture.toJSON(t),l.indirectTexture=this._indirectTexture.toJSON(t),this._colorsTexture!==null&&(l.colorsTexture=this._colorsTexture.toJSON(t)),this.boundingSphere!==null&&(l.boundingSphere=this.boundingSphere.toJSON()),this.boundingBox!==null&&(l.boundingBox=this.boundingBox.toJSON()));function u(p,m){return p[m.uuid]===void 0&&(p[m.uuid]=m.toJSON(t)),m.uuid}if(this.isScene)this.background&&(this.background.isColor?l.background=this.background.toJSON():this.background.isTexture&&(l.background=this.background.toJSON(t).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(l.environment=this.environment.toJSON(t).uuid);else if(this.isMesh||this.isLine||this.isPoints){l.geometry=u(t.geometries,this.geometry);const p=this.geometry.parameters;if(p!==void 0&&p.shapes!==void 0){const m=p.shapes;if(Array.isArray(m))for(let d=0,g=m.length;d<g;d++){const v=m[d];u(t.shapes,v)}else u(t.shapes,m)}}if(this.isSkinnedMesh&&(l.bindMode=this.bindMode,l.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(u(t.skeletons,this.skeleton),l.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const p=[];for(let m=0,d=this.material.length;m<d;m++)p.push(u(t.materials,this.material[m]));l.material=p}else l.material=u(t.materials,this.material);if(this.children.length>0){l.children=[];for(let p=0;p<this.children.length;p++)l.children.push(this.children[p].toJSON(t).object)}if(this.animations.length>0){l.animations=[];for(let p=0;p<this.animations.length;p++){const m=this.animations[p];l.animations.push(u(t.animations,m))}}if(i){const p=f(t.geometries),m=f(t.materials),d=f(t.textures),g=f(t.images),v=f(t.shapes),_=f(t.skeletons),M=f(t.animations),T=f(t.nodes);p.length>0&&(r.geometries=p),m.length>0&&(r.materials=m),d.length>0&&(r.textures=d),g.length>0&&(r.images=g),v.length>0&&(r.shapes=v),_.length>0&&(r.skeletons=_),M.length>0&&(r.animations=M),T.length>0&&(r.nodes=T)}return r.object=l,r;function f(p){const m=[];for(const d in p){const g=p[d];delete g.metadata,m.push(g)}return m}}clone(t){return new this.constructor().copy(this,t)}copy(t,i=!0){if(this.name=t.name,this.up.copy(t.up),this.position.copy(t.position),this.rotation.order=t.rotation.order,this.quaternion.copy(t.quaternion),this.scale.copy(t.scale),this.pivot=t.pivot!==null?t.pivot.clone():null,this.matrix.copy(t.matrix),this.matrixWorld.copy(t.matrixWorld),this.matrixAutoUpdate=t.matrixAutoUpdate,this.matrixWorldAutoUpdate=t.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=t.matrixWorldNeedsUpdate,this.layers.mask=t.layers.mask,this.visible=t.visible,this.castShadow=t.castShadow,this.receiveShadow=t.receiveShadow,this.frustumCulled=t.frustumCulled,this.renderOrder=t.renderOrder,this.static=t.static,this.animations=t.animations.slice(),this.userData=JSON.parse(JSON.stringify(t.userData)),i===!0)for(let r=0;r<t.children.length;r++){const l=t.children[r];this.add(l.clone())}return this}}Un.DEFAULT_UP=new $(0,1,0);Un.DEFAULT_MATRIX_AUTO_UPDATE=!0;Un.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;class el extends Un{constructor(){super(),this.isGroup=!0,this.type="Group"}}const sM={type:"move"};class Ah{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new el,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new el,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new $,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new $),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new el,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new $,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new $,this._grip.eventsEnabled=!1),this._grip}dispatchEvent(t){return this._targetRay!==null&&this._targetRay.dispatchEvent(t),this._grip!==null&&this._grip.dispatchEvent(t),this._hand!==null&&this._hand.dispatchEvent(t),this}connect(t){if(t&&t.hand){const i=this._hand;if(i)for(const r of t.hand.values())this._getHandJoint(i,r)}return this.dispatchEvent({type:"connected",data:t}),this}disconnect(t){return this.dispatchEvent({type:"disconnected",data:t}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(t,i,r){let l=null,u=null,f=null;const p=this._targetRay,m=this._grip,d=this._hand;if(t&&i.session.visibilityState!=="visible-blurred"){if(d&&t.hand){f=!0;for(const w of t.hand.values()){const E=i.getJointPose(w,r),S=this._getHandJoint(d,w);E!==null&&(S.matrix.fromArray(E.transform.matrix),S.matrix.decompose(S.position,S.rotation,S.scale),S.matrixWorldNeedsUpdate=!0,S.jointRadius=E.radius),S.visible=E!==null}const g=d.joints["index-finger-tip"],v=d.joints["thumb-tip"],_=g.position.distanceTo(v.position),M=.02,T=.005;d.inputState.pinching&&_>M+T?(d.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:t.handedness,target:this})):!d.inputState.pinching&&_<=M-T&&(d.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:t.handedness,target:this}))}else m!==null&&t.gripSpace&&(u=i.getPose(t.gripSpace,r),u!==null&&(m.matrix.fromArray(u.transform.matrix),m.matrix.decompose(m.position,m.rotation,m.scale),m.matrixWorldNeedsUpdate=!0,u.linearVelocity?(m.hasLinearVelocity=!0,m.linearVelocity.copy(u.linearVelocity)):m.hasLinearVelocity=!1,u.angularVelocity?(m.hasAngularVelocity=!0,m.angularVelocity.copy(u.angularVelocity)):m.hasAngularVelocity=!1,m.eventsEnabled&&m.dispatchEvent({type:"gripUpdated",data:t,target:this})));p!==null&&(l=i.getPose(t.targetRaySpace,r),l===null&&u!==null&&(l=u),l!==null&&(p.matrix.fromArray(l.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,l.linearVelocity?(p.hasLinearVelocity=!0,p.linearVelocity.copy(l.linearVelocity)):p.hasLinearVelocity=!1,l.angularVelocity?(p.hasAngularVelocity=!0,p.angularVelocity.copy(l.angularVelocity)):p.hasAngularVelocity=!1,this.dispatchEvent(sM)))}return p!==null&&(p.visible=l!==null),m!==null&&(m.visible=u!==null),d!==null&&(d.visible=f!==null),this}_getHandJoint(t,i){if(t.joints[i.jointName]===void 0){const r=new el;r.matrixAutoUpdate=!1,r.visible=!1,t.joints[i.jointName]=r,t.add(r)}return t.joints[i.jointName]}}const Uv={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},ir={h:0,s:0,l:0},Mu={h:0,s:0,l:0};function Rh(s,t,i){return i<0&&(i+=1),i>1&&(i-=1),i<1/6?s+(t-s)*6*i:i<1/2?t:i<2/3?s+(t-s)*6*(2/3-i):s}class xe{constructor(t,i,r){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(t,i,r)}set(t,i,r){if(i===void 0&&r===void 0){const l=t;l&&l.isColor?this.copy(l):typeof l=="number"?this.setHex(l):typeof l=="string"&&this.setStyle(l)}else this.setRGB(t,i,r);return this}setScalar(t){return this.r=t,this.g=t,this.b=t,this}setHex(t,i=ci){return t=Math.floor(t),this.r=(t>>16&255)/255,this.g=(t>>8&255)/255,this.b=(t&255)/255,Ee.colorSpaceToWorking(this,i),this}setRGB(t,i,r,l=Ee.workingColorSpace){return this.r=t,this.g=i,this.b=r,Ee.colorSpaceToWorking(this,l),this}setHSL(t,i,r,l=Ee.workingColorSpace){if(t=qy(t,1),i=me(i,0,1),r=me(r,0,1),i===0)this.r=this.g=this.b=r;else{const u=r<=.5?r*(1+i):r+i-r*i,f=2*r-u;this.r=Rh(f,u,t+1/3),this.g=Rh(f,u,t),this.b=Rh(f,u,t-1/3)}return Ee.colorSpaceToWorking(this,l),this}setStyle(t,i=ci){function r(u){u!==void 0&&parseFloat(u)<1&&te("Color: Alpha component of "+t+" will be ignored.")}let l;if(l=/^(\w+)\(([^\)]*)\)/.exec(t)){let u;const f=l[1],p=l[2];switch(f){case"rgb":case"rgba":if(u=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(p))return r(u[4]),this.setRGB(Math.min(255,parseInt(u[1],10))/255,Math.min(255,parseInt(u[2],10))/255,Math.min(255,parseInt(u[3],10))/255,i);if(u=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(p))return r(u[4]),this.setRGB(Math.min(100,parseInt(u[1],10))/100,Math.min(100,parseInt(u[2],10))/100,Math.min(100,parseInt(u[3],10))/100,i);break;case"hsl":case"hsla":if(u=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(p))return r(u[4]),this.setHSL(parseFloat(u[1])/360,parseFloat(u[2])/100,parseFloat(u[3])/100,i);break;default:te("Color: Unknown color model "+t)}}else if(l=/^\#([A-Fa-f\d]+)$/.exec(t)){const u=l[1],f=u.length;if(f===3)return this.setRGB(parseInt(u.charAt(0),16)/15,parseInt(u.charAt(1),16)/15,parseInt(u.charAt(2),16)/15,i);if(f===6)return this.setHex(parseInt(u,16),i);te("Color: Invalid hex color "+t)}else if(t&&t.length>0)return this.setColorName(t,i);return this}setColorName(t,i=ci){const r=Uv[t.toLowerCase()];return r!==void 0?this.setHex(r,i):te("Color: Unknown color "+t),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(t){return this.r=t.r,this.g=t.g,this.b=t.b,this}copySRGBToLinear(t){return this.r=Aa(t.r),this.g=Aa(t.g),this.b=Aa(t.b),this}copyLinearToSRGB(t){return this.r=Ws(t.r),this.g=Ws(t.g),this.b=Ws(t.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(t=ci){return Ee.workingToColorSpace(Pn.copy(this),t),Math.round(me(Pn.r*255,0,255))*65536+Math.round(me(Pn.g*255,0,255))*256+Math.round(me(Pn.b*255,0,255))}getHexString(t=ci){return("000000"+this.getHex(t).toString(16)).slice(-6)}getHSL(t,i=Ee.workingColorSpace){Ee.workingToColorSpace(Pn.copy(this),i);const r=Pn.r,l=Pn.g,u=Pn.b,f=Math.max(r,l,u),p=Math.min(r,l,u);let m,d;const g=(p+f)/2;if(p===f)m=0,d=0;else{const v=f-p;switch(d=g<=.5?v/(f+p):v/(2-f-p),f){case r:m=(l-u)/v+(l<u?6:0);break;case l:m=(u-r)/v+2;break;case u:m=(r-l)/v+4;break}m/=6}return t.h=m,t.s=d,t.l=g,t}getRGB(t,i=Ee.workingColorSpace){return Ee.workingToColorSpace(Pn.copy(this),i),t.r=Pn.r,t.g=Pn.g,t.b=Pn.b,t}getStyle(t=ci){Ee.workingToColorSpace(Pn.copy(this),t);const i=Pn.r,r=Pn.g,l=Pn.b;return t!==ci?`color(${t} ${i.toFixed(3)} ${r.toFixed(3)} ${l.toFixed(3)})`:`rgb(${Math.round(i*255)},${Math.round(r*255)},${Math.round(l*255)})`}offsetHSL(t,i,r){return this.getHSL(ir),this.setHSL(ir.h+t,ir.s+i,ir.l+r)}add(t){return this.r+=t.r,this.g+=t.g,this.b+=t.b,this}addColors(t,i){return this.r=t.r+i.r,this.g=t.g+i.g,this.b=t.b+i.b,this}addScalar(t){return this.r+=t,this.g+=t,this.b+=t,this}sub(t){return this.r=Math.max(0,this.r-t.r),this.g=Math.max(0,this.g-t.g),this.b=Math.max(0,this.b-t.b),this}multiply(t){return this.r*=t.r,this.g*=t.g,this.b*=t.b,this}multiplyScalar(t){return this.r*=t,this.g*=t,this.b*=t,this}lerp(t,i){return this.r+=(t.r-this.r)*i,this.g+=(t.g-this.g)*i,this.b+=(t.b-this.b)*i,this}lerpColors(t,i,r){return this.r=t.r+(i.r-t.r)*r,this.g=t.g+(i.g-t.g)*r,this.b=t.b+(i.b-t.b)*r,this}lerpHSL(t,i){this.getHSL(ir),t.getHSL(Mu);const r=Sh(ir.h,Mu.h,i),l=Sh(ir.s,Mu.s,i),u=Sh(ir.l,Mu.l,i);return this.setHSL(r,l,u),this}setFromVector3(t){return this.r=t.x,this.g=t.y,this.b=t.z,this}applyMatrix3(t){const i=this.r,r=this.g,l=this.b,u=t.elements;return this.r=u[0]*i+u[3]*r+u[6]*l,this.g=u[1]*i+u[4]*r+u[7]*l,this.b=u[2]*i+u[5]*r+u[8]*l,this}equals(t){return t.r===this.r&&t.g===this.g&&t.b===this.b}fromArray(t,i=0){return this.r=t[i],this.g=t[i+1],this.b=t[i+2],this}toArray(t=[],i=0){return t[i]=this.r,t[i+1]=this.g,t[i+2]=this.b,t}fromBufferAttribute(t,i){return this.r=t.getX(i),this.g=t.getY(i),this.b=t.getZ(i),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Pn=new xe;xe.NAMES=Uv;class oM extends Un{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new dr,this.environmentIntensity=1,this.environmentRotation=new dr,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(t,i){return super.copy(t,i),t.background!==null&&(this.background=t.background.clone()),t.environment!==null&&(this.environment=t.environment.clone()),t.fog!==null&&(this.fog=t.fog.clone()),this.backgroundBlurriness=t.backgroundBlurriness,this.backgroundIntensity=t.backgroundIntensity,this.backgroundRotation.copy(t.backgroundRotation),this.environmentIntensity=t.environmentIntensity,this.environmentRotation.copy(t.environmentRotation),t.overrideMaterial!==null&&(this.overrideMaterial=t.overrideMaterial.clone()),this.matrixAutoUpdate=t.matrixAutoUpdate,this}toJSON(t){const i=super.toJSON(t);return this.fog!==null&&(i.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(i.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(i.object.backgroundIntensity=this.backgroundIntensity),i.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(i.object.environmentIntensity=this.environmentIntensity),i.object.environmentRotation=this.environmentRotation.toArray(),i}}const Di=new $,va=new $,Ch=new $,xa=new $,Ls=new $,Ns=new $,v0=new $,wh=new $,Dh=new $,Uh=new $,Lh=new tn,Nh=new tn,Oh=new tn;class Li{constructor(t=new $,i=new $,r=new $){this.a=t,this.b=i,this.c=r}static getNormal(t,i,r,l){l.subVectors(r,i),Di.subVectors(t,i),l.cross(Di);const u=l.lengthSq();return u>0?l.multiplyScalar(1/Math.sqrt(u)):l.set(0,0,0)}static getBarycoord(t,i,r,l,u){Di.subVectors(l,i),va.subVectors(r,i),Ch.subVectors(t,i);const f=Di.dot(Di),p=Di.dot(va),m=Di.dot(Ch),d=va.dot(va),g=va.dot(Ch),v=f*d-p*p;if(v===0)return u.set(0,0,0),null;const _=1/v,M=(d*m-p*g)*_,T=(f*g-p*m)*_;return u.set(1-M-T,T,M)}static containsPoint(t,i,r,l){return this.getBarycoord(t,i,r,l,xa)===null?!1:xa.x>=0&&xa.y>=0&&xa.x+xa.y<=1}static getInterpolation(t,i,r,l,u,f,p,m){return this.getBarycoord(t,i,r,l,xa)===null?(m.x=0,m.y=0,"z"in m&&(m.z=0),"w"in m&&(m.w=0),null):(m.setScalar(0),m.addScaledVector(u,xa.x),m.addScaledVector(f,xa.y),m.addScaledVector(p,xa.z),m)}static getInterpolatedAttribute(t,i,r,l,u,f){return Lh.setScalar(0),Nh.setScalar(0),Oh.setScalar(0),Lh.fromBufferAttribute(t,i),Nh.fromBufferAttribute(t,r),Oh.fromBufferAttribute(t,l),f.setScalar(0),f.addScaledVector(Lh,u.x),f.addScaledVector(Nh,u.y),f.addScaledVector(Oh,u.z),f}static isFrontFacing(t,i,r,l){return Di.subVectors(r,i),va.subVectors(t,i),Di.cross(va).dot(l)<0}set(t,i,r){return this.a.copy(t),this.b.copy(i),this.c.copy(r),this}setFromPointsAndIndices(t,i,r,l){return this.a.copy(t[i]),this.b.copy(t[r]),this.c.copy(t[l]),this}setFromAttributeAndIndices(t,i,r,l){return this.a.fromBufferAttribute(t,i),this.b.fromBufferAttribute(t,r),this.c.fromBufferAttribute(t,l),this}clone(){return new this.constructor().copy(this)}copy(t){return this.a.copy(t.a),this.b.copy(t.b),this.c.copy(t.c),this}getArea(){return Di.subVectors(this.c,this.b),va.subVectors(this.a,this.b),Di.cross(va).length()*.5}getMidpoint(t){return t.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(t){return Li.getNormal(this.a,this.b,this.c,t)}getPlane(t){return t.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(t,i){return Li.getBarycoord(t,this.a,this.b,this.c,i)}getInterpolation(t,i,r,l,u){return Li.getInterpolation(t,this.a,this.b,this.c,i,r,l,u)}containsPoint(t){return Li.containsPoint(t,this.a,this.b,this.c)}isFrontFacing(t){return Li.isFrontFacing(this.a,this.b,this.c,t)}intersectsBox(t){return t.intersectsTriangle(this)}closestPointToPoint(t,i){const r=this.a,l=this.b,u=this.c;let f,p;Ls.subVectors(l,r),Ns.subVectors(u,r),wh.subVectors(t,r);const m=Ls.dot(wh),d=Ns.dot(wh);if(m<=0&&d<=0)return i.copy(r);Dh.subVectors(t,l);const g=Ls.dot(Dh),v=Ns.dot(Dh);if(g>=0&&v<=g)return i.copy(l);const _=m*v-g*d;if(_<=0&&m>=0&&g<=0)return f=m/(m-g),i.copy(r).addScaledVector(Ls,f);Uh.subVectors(t,u);const M=Ls.dot(Uh),T=Ns.dot(Uh);if(T>=0&&M<=T)return i.copy(u);const w=M*d-m*T;if(w<=0&&d>=0&&T<=0)return p=d/(d-T),i.copy(r).addScaledVector(Ns,p);const E=g*T-M*v;if(E<=0&&v-g>=0&&M-T>=0)return v0.subVectors(u,l),p=(v-g)/(v-g+(M-T)),i.copy(l).addScaledVector(v0,p);const S=1/(E+w+_);return f=w*S,p=_*S,i.copy(r).addScaledVector(Ls,f).addScaledVector(Ns,p)}equals(t){return t.a.equals(this.a)&&t.b.equals(this.b)&&t.c.equals(this.c)}}class Qs{constructor(t=new $(1/0,1/0,1/0),i=new $(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=t,this.max=i}set(t,i){return this.min.copy(t),this.max.copy(i),this}setFromArray(t){this.makeEmpty();for(let i=0,r=t.length;i<r;i+=3)this.expandByPoint(Ui.fromArray(t,i));return this}setFromBufferAttribute(t){this.makeEmpty();for(let i=0,r=t.count;i<r;i++)this.expandByPoint(Ui.fromBufferAttribute(t,i));return this}setFromPoints(t){this.makeEmpty();for(let i=0,r=t.length;i<r;i++)this.expandByPoint(t[i]);return this}setFromCenterAndSize(t,i){const r=Ui.copy(i).multiplyScalar(.5);return this.min.copy(t).sub(r),this.max.copy(t).add(r),this}setFromObject(t,i=!1){return this.makeEmpty(),this.expandByObject(t,i)}clone(){return new this.constructor().copy(this)}copy(t){return this.min.copy(t.min),this.max.copy(t.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(t){return this.isEmpty()?t.set(0,0,0):t.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(t){return this.isEmpty()?t.set(0,0,0):t.subVectors(this.max,this.min)}expandByPoint(t){return this.min.min(t),this.max.max(t),this}expandByVector(t){return this.min.sub(t),this.max.add(t),this}expandByScalar(t){return this.min.addScalar(-t),this.max.addScalar(t),this}expandByObject(t,i=!1){t.updateWorldMatrix(!1,!1);const r=t.geometry;if(r!==void 0){const u=r.getAttribute("position");if(i===!0&&u!==void 0&&t.isInstancedMesh!==!0)for(let f=0,p=u.count;f<p;f++)t.isMesh===!0?t.getVertexPosition(f,Ui):Ui.fromBufferAttribute(u,f),Ui.applyMatrix4(t.matrixWorld),this.expandByPoint(Ui);else t.boundingBox!==void 0?(t.boundingBox===null&&t.computeBoundingBox(),Eu.copy(t.boundingBox)):(r.boundingBox===null&&r.computeBoundingBox(),Eu.copy(r.boundingBox)),Eu.applyMatrix4(t.matrixWorld),this.union(Eu)}const l=t.children;for(let u=0,f=l.length;u<f;u++)this.expandByObject(l[u],i);return this}containsPoint(t){return t.x>=this.min.x&&t.x<=this.max.x&&t.y>=this.min.y&&t.y<=this.max.y&&t.z>=this.min.z&&t.z<=this.max.z}containsBox(t){return this.min.x<=t.min.x&&t.max.x<=this.max.x&&this.min.y<=t.min.y&&t.max.y<=this.max.y&&this.min.z<=t.min.z&&t.max.z<=this.max.z}getParameter(t,i){return i.set((t.x-this.min.x)/(this.max.x-this.min.x),(t.y-this.min.y)/(this.max.y-this.min.y),(t.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(t){return t.max.x>=this.min.x&&t.min.x<=this.max.x&&t.max.y>=this.min.y&&t.min.y<=this.max.y&&t.max.z>=this.min.z&&t.min.z<=this.max.z}intersectsSphere(t){return this.clampPoint(t.center,Ui),Ui.distanceToSquared(t.center)<=t.radius*t.radius}intersectsPlane(t){let i,r;return t.normal.x>0?(i=t.normal.x*this.min.x,r=t.normal.x*this.max.x):(i=t.normal.x*this.max.x,r=t.normal.x*this.min.x),t.normal.y>0?(i+=t.normal.y*this.min.y,r+=t.normal.y*this.max.y):(i+=t.normal.y*this.max.y,r+=t.normal.y*this.min.y),t.normal.z>0?(i+=t.normal.z*this.min.z,r+=t.normal.z*this.max.z):(i+=t.normal.z*this.max.z,r+=t.normal.z*this.min.z),i<=-t.constant&&r>=-t.constant}intersectsTriangle(t){if(this.isEmpty())return!1;this.getCenter(Zo),bu.subVectors(this.max,Zo),Os.subVectors(t.a,Zo),Ps.subVectors(t.b,Zo),Is.subVectors(t.c,Zo),ar.subVectors(Ps,Os),rr.subVectors(Is,Ps),Pr.subVectors(Os,Is);let i=[0,-ar.z,ar.y,0,-rr.z,rr.y,0,-Pr.z,Pr.y,ar.z,0,-ar.x,rr.z,0,-rr.x,Pr.z,0,-Pr.x,-ar.y,ar.x,0,-rr.y,rr.x,0,-Pr.y,Pr.x,0];return!Ph(i,Os,Ps,Is,bu)||(i=[1,0,0,0,1,0,0,0,1],!Ph(i,Os,Ps,Is,bu))?!1:(Tu.crossVectors(ar,rr),i=[Tu.x,Tu.y,Tu.z],Ph(i,Os,Ps,Is,bu))}clampPoint(t,i){return i.copy(t).clamp(this.min,this.max)}distanceToPoint(t){return this.clampPoint(t,Ui).distanceTo(t)}getBoundingSphere(t){return this.isEmpty()?t.makeEmpty():(this.getCenter(t.center),t.radius=this.getSize(Ui).length()*.5),t}intersect(t){return this.min.max(t.min),this.max.min(t.max),this.isEmpty()&&this.makeEmpty(),this}union(t){return this.min.min(t.min),this.max.max(t.max),this}applyMatrix4(t){return this.isEmpty()?this:(Sa[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(t),Sa[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(t),Sa[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(t),Sa[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(t),Sa[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(t),Sa[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(t),Sa[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(t),Sa[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(t),this.setFromPoints(Sa),this)}translate(t){return this.min.add(t),this.max.add(t),this}equals(t){return t.min.equals(this.min)&&t.max.equals(this.max)}toJSON(){return{min:this.min.toArray(),max:this.max.toArray()}}fromJSON(t){return this.min.fromArray(t.min),this.max.fromArray(t.max),this}}const Sa=[new $,new $,new $,new $,new $,new $,new $,new $],Ui=new $,Eu=new Qs,Os=new $,Ps=new $,Is=new $,ar=new $,rr=new $,Pr=new $,Zo=new $,bu=new $,Tu=new $,Ir=new $;function Ph(s,t,i,r,l){for(let u=0,f=s.length-3;u<=f;u+=3){Ir.fromArray(s,u);const p=l.x*Math.abs(Ir.x)+l.y*Math.abs(Ir.y)+l.z*Math.abs(Ir.z),m=t.dot(Ir),d=i.dot(Ir),g=r.dot(Ir);if(Math.max(-Math.max(m,d,g),Math.min(m,d,g))>p)return!1}return!0}const _n=new $,Au=new ie;let lM=0;class hi extends pr{constructor(t,i,r=!1){if(super(),Array.isArray(t))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,Object.defineProperty(this,"id",{value:lM++}),this.name="",this.array=t,this.itemSize=i,this.count=t!==void 0?t.length/i:0,this.normalized=r,this.usage=a0,this.updateRanges=[],this.gpuType=Wi,this.version=0}onUploadCallback(){}set needsUpdate(t){t===!0&&this.version++}setUsage(t){return this.usage=t,this}addUpdateRange(t,i){this.updateRanges.push({start:t,count:i})}clearUpdateRanges(){this.updateRanges.length=0}copy(t){return this.name=t.name,this.array=new t.array.constructor(t.array),this.itemSize=t.itemSize,this.count=t.count,this.normalized=t.normalized,this.usage=t.usage,this.gpuType=t.gpuType,this}copyAt(t,i,r){t*=this.itemSize,r*=i.itemSize;for(let l=0,u=this.itemSize;l<u;l++)this.array[t+l]=i.array[r+l];return this}copyArray(t){return this.array.set(t),this}applyMatrix3(t){if(this.itemSize===2)for(let i=0,r=this.count;i<r;i++)Au.fromBufferAttribute(this,i),Au.applyMatrix3(t),this.setXY(i,Au.x,Au.y);else if(this.itemSize===3)for(let i=0,r=this.count;i<r;i++)_n.fromBufferAttribute(this,i),_n.applyMatrix3(t),this.setXYZ(i,_n.x,_n.y,_n.z);return this}applyMatrix4(t){for(let i=0,r=this.count;i<r;i++)_n.fromBufferAttribute(this,i),_n.applyMatrix4(t),this.setXYZ(i,_n.x,_n.y,_n.z);return this}applyNormalMatrix(t){for(let i=0,r=this.count;i<r;i++)_n.fromBufferAttribute(this,i),_n.applyNormalMatrix(t),this.setXYZ(i,_n.x,_n.y,_n.z);return this}transformDirection(t){for(let i=0,r=this.count;i<r;i++)_n.fromBufferAttribute(this,i),_n.transformDirection(t),this.setXYZ(i,_n.x,_n.y,_n.z);return this}set(t,i=0){return this.array.set(t,i),this}getComponent(t,i){let r=this.array[t*this.itemSize+i];return this.normalized&&(r=qo(r,this.array)),r}setComponent(t,i,r){return this.normalized&&(r=Zn(r,this.array)),this.array[t*this.itemSize+i]=r,this}getX(t){let i=this.array[t*this.itemSize];return this.normalized&&(i=qo(i,this.array)),i}setX(t,i){return this.normalized&&(i=Zn(i,this.array)),this.array[t*this.itemSize]=i,this}getY(t){let i=this.array[t*this.itemSize+1];return this.normalized&&(i=qo(i,this.array)),i}setY(t,i){return this.normalized&&(i=Zn(i,this.array)),this.array[t*this.itemSize+1]=i,this}getZ(t){let i=this.array[t*this.itemSize+2];return this.normalized&&(i=qo(i,this.array)),i}setZ(t,i){return this.normalized&&(i=Zn(i,this.array)),this.array[t*this.itemSize+2]=i,this}getW(t){let i=this.array[t*this.itemSize+3];return this.normalized&&(i=qo(i,this.array)),i}setW(t,i){return this.normalized&&(i=Zn(i,this.array)),this.array[t*this.itemSize+3]=i,this}setXY(t,i,r){return t*=this.itemSize,this.normalized&&(i=Zn(i,this.array),r=Zn(r,this.array)),this.array[t+0]=i,this.array[t+1]=r,this}setXYZ(t,i,r,l){return t*=this.itemSize,this.normalized&&(i=Zn(i,this.array),r=Zn(r,this.array),l=Zn(l,this.array)),this.array[t+0]=i,this.array[t+1]=r,this.array[t+2]=l,this}setXYZW(t,i,r,l,u){return t*=this.itemSize,this.normalized&&(i=Zn(i,this.array),r=Zn(r,this.array),l=Zn(l,this.array),u=Zn(u,this.array)),this.array[t+0]=i,this.array[t+1]=r,this.array[t+2]=l,this.array[t+3]=u,this}onUpload(t){return this.onUploadCallback=t,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const t={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(t.name=this.name),this.usage!==a0&&(t.usage=this.usage),t}dispose(){this.dispatchEvent({type:"dispose"})}}class Lv extends hi{constructor(t,i,r){super(new Uint16Array(t),i,r)}}class Nv extends hi{constructor(t,i,r){super(new Uint32Array(t),i,r)}}class Oi extends hi{constructor(t,i,r){super(new Float32Array(t),i,r)}}const uM=new Qs,Ko=new $,Ih=new $;class tp{constructor(t=new $,i=-1){this.isSphere=!0,this.center=t,this.radius=i}set(t,i){return this.center.copy(t),this.radius=i,this}setFromPoints(t,i){const r=this.center;i!==void 0?r.copy(i):uM.setFromPoints(t).getCenter(r);let l=0;for(let u=0,f=t.length;u<f;u++)l=Math.max(l,r.distanceToSquared(t[u]));return this.radius=Math.sqrt(l),this}copy(t){return this.center.copy(t.center),this.radius=t.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(t){return t.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(t){return t.distanceTo(this.center)-this.radius}intersectsSphere(t){const i=this.radius+t.radius;return t.center.distanceToSquared(this.center)<=i*i}intersectsBox(t){return t.intersectsSphere(this)}intersectsPlane(t){return Math.abs(t.distanceToPoint(this.center))<=this.radius}clampPoint(t,i){const r=this.center.distanceToSquared(t);return i.copy(t),r>this.radius*this.radius&&(i.sub(this.center).normalize(),i.multiplyScalar(this.radius).add(this.center)),i}getBoundingBox(t){return this.isEmpty()?(t.makeEmpty(),t):(t.set(this.center,this.center),t.expandByScalar(this.radius),t)}applyMatrix4(t){return this.center.applyMatrix4(t),this.radius=this.radius*t.getMaxScaleOnAxis(),this}translate(t){return this.center.add(t),this}expandByPoint(t){if(this.isEmpty())return this.center.copy(t),this.radius=0,this;Ko.subVectors(t,this.center);const i=Ko.lengthSq();if(i>this.radius*this.radius){const r=Math.sqrt(i),l=(r-this.radius)*.5;this.center.addScaledVector(Ko,l/r),this.radius+=l}return this}union(t){return t.isEmpty()?this:this.isEmpty()?(this.copy(t),this):(this.center.equals(t.center)===!0?this.radius=Math.max(this.radius,t.radius):(Ih.subVectors(t.center,this.center).setLength(t.radius),this.expandByPoint(Ko.copy(t.center).add(Ih)),this.expandByPoint(Ko.copy(t.center).sub(Ih))),this)}equals(t){return t.center.equals(this.center)&&t.radius===this.radius}clone(){return new this.constructor().copy(this)}toJSON(){return{radius:this.radius,center:this.center.toArray()}}fromJSON(t){return this.radius=t.radius,this.center.fromArray(t.center),this}}let cM=0;const yi=new $e,Fh=new Un,Fs=new $,ui=new Qs,Qo=new Qs,bn=new $;class Pi extends pr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:cM++}),this.uuid=sl(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.indirectOffset=0,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={},this._transformed=!1}getIndex(){return this.index}setIndex(t){return Array.isArray(t)?this.index=new(Vy(t)?Nv:Lv)(t,1):this.index=t,this}setIndirect(t,i=0){return this.indirect=t,this.indirectOffset=i,this}getIndirect(){return this.indirect}getAttribute(t){return this.attributes[t]}setAttribute(t,i){return this.attributes[t]=i,this}deleteAttribute(t){return delete this.attributes[t],this}hasAttribute(t){return this.attributes[t]!==void 0}addGroup(t,i,r=0){this.groups.push({start:t,count:i,materialIndex:r})}clearGroups(){this.groups=[]}setDrawRange(t,i){this.drawRange.start=t,this.drawRange.count=i}applyMatrix4(t){const i=this.attributes.position;i!==void 0&&(i.applyMatrix4(t),i.needsUpdate=!0);const r=this.attributes.normal;if(r!==void 0){const u=new re().getNormalMatrix(t);r.applyNormalMatrix(u),r.needsUpdate=!0}const l=this.attributes.tangent;return l!==void 0&&(l.transformDirection(t),l.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this._transformed=!0,this}applyQuaternion(t){return yi.makeRotationFromQuaternion(t),this.applyMatrix4(yi),this}rotateX(t){return yi.makeRotationX(t),this.applyMatrix4(yi),this}rotateY(t){return yi.makeRotationY(t),this.applyMatrix4(yi),this}rotateZ(t){return yi.makeRotationZ(t),this.applyMatrix4(yi),this}translate(t,i,r){return yi.makeTranslation(t,i,r),this.applyMatrix4(yi),this}scale(t,i,r){return yi.makeScale(t,i,r),this.applyMatrix4(yi),this}lookAt(t){return Fh.lookAt(t),Fh.updateMatrix(),this.applyMatrix4(Fh.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Fs).negate(),this.translate(Fs.x,Fs.y,Fs.z),this}setFromPoints(t){const i=this.getAttribute("position");if(i===void 0){const r=[];for(let l=0,u=t.length;l<u;l++){const f=t[l];r.push(f.x,f.y,f.z||0)}this.setAttribute("position",new Oi(r,3))}else{const r=Math.min(t.length,i.count);for(let l=0;l<r;l++){const u=t[l];i.setXYZ(l,u.x,u.y,u.z||0)}t.length>i.count&&te("BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),i.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Qs);const t=this.attributes.position,i=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){be("BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new $(-1/0,-1/0,-1/0),new $(1/0,1/0,1/0));return}if(t!==void 0){if(this.boundingBox.setFromBufferAttribute(t),i)for(let r=0,l=i.length;r<l;r++){const u=i[r];ui.setFromBufferAttribute(u),this.morphTargetsRelative?(bn.addVectors(this.boundingBox.min,ui.min),this.boundingBox.expandByPoint(bn),bn.addVectors(this.boundingBox.max,ui.max),this.boundingBox.expandByPoint(bn)):(this.boundingBox.expandByPoint(ui.min),this.boundingBox.expandByPoint(ui.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&be('BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new tp);const t=this.attributes.position,i=this.morphAttributes.position;if(t&&t.isGLBufferAttribute){be("BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new $,1/0);return}if(t){const r=this.boundingSphere.center;if(ui.setFromBufferAttribute(t),i)for(let u=0,f=i.length;u<f;u++){const p=i[u];Qo.setFromBufferAttribute(p),this.morphTargetsRelative?(bn.addVectors(ui.min,Qo.min),ui.expandByPoint(bn),bn.addVectors(ui.max,Qo.max),ui.expandByPoint(bn)):(ui.expandByPoint(Qo.min),ui.expandByPoint(Qo.max))}ui.getCenter(r);let l=0;for(let u=0,f=t.count;u<f;u++)bn.fromBufferAttribute(t,u),l=Math.max(l,r.distanceToSquared(bn));if(i)for(let u=0,f=i.length;u<f;u++){const p=i[u],m=this.morphTargetsRelative;for(let d=0,g=p.count;d<g;d++)bn.fromBufferAttribute(p,d),m&&(Fs.fromBufferAttribute(t,d),bn.add(Fs)),l=Math.max(l,r.distanceToSquared(bn))}this.boundingSphere.radius=Math.sqrt(l),isNaN(this.boundingSphere.radius)&&be('BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const t=this.index,i=this.attributes;if(t===null||i.position===void 0||i.normal===void 0||i.uv===void 0){be("BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const r=i.position,l=i.normal,u=i.uv;let f=this.getAttribute("tangent");(f===void 0||f.count!==r.count)&&(f=new hi(new Float32Array(4*r.count),4),this.setAttribute("tangent",f));const p=[],m=[];for(let b=0;b<r.count;b++)p[b]=new $,m[b]=new $;const d=new $,g=new $,v=new $,_=new ie,M=new ie,T=new ie,w=new $,E=new $;function S(b,P,q){d.fromBufferAttribute(r,b),g.fromBufferAttribute(r,P),v.fromBufferAttribute(r,q),_.fromBufferAttribute(u,b),M.fromBufferAttribute(u,P),T.fromBufferAttribute(u,q),g.sub(d),v.sub(d),M.sub(_),T.sub(_);const G=1/(M.x*T.y-T.x*M.y);isFinite(G)&&(w.copy(g).multiplyScalar(T.y).addScaledVector(v,-M.y).multiplyScalar(G),E.copy(v).multiplyScalar(M.x).addScaledVector(g,-T.x).multiplyScalar(G),p[b].add(w),p[P].add(w),p[q].add(w),m[b].add(E),m[P].add(E),m[q].add(E))}let F=this.groups;F.length===0&&(F=[{start:0,count:t.count}]);for(let b=0,P=F.length;b<P;++b){const q=F[b],G=q.start,Z=q.count;for(let ht=G,mt=G+Z;ht<mt;ht+=3)S(t.getX(ht+0),t.getX(ht+1),t.getX(ht+2))}const z=new $,C=new $,N=new $,D=new $;function O(b){N.fromBufferAttribute(l,b),D.copy(N);const P=p[b];z.copy(P),z.sub(N.multiplyScalar(N.dot(P))).normalize(),C.crossVectors(D,P);const G=C.dot(m[b])<0?-1:1;f.setXYZW(b,z.x,z.y,z.z,G)}for(let b=0,P=F.length;b<P;++b){const q=F[b],G=q.start,Z=q.count;for(let ht=G,mt=G+Z;ht<mt;ht+=3)O(t.getX(ht+0)),O(t.getX(ht+1)),O(t.getX(ht+2))}this._transformed=!0}computeVertexNormals(){const t=this.index,i=this.getAttribute("position");if(i!==void 0){let r=this.getAttribute("normal");if(r===void 0||r.count!==i.count)r=new hi(new Float32Array(i.count*3),3),this.setAttribute("normal",r);else for(let _=0,M=r.count;_<M;_++)r.setXYZ(_,0,0,0);const l=new $,u=new $,f=new $,p=new $,m=new $,d=new $,g=new $,v=new $;if(t)for(let _=0,M=t.count;_<M;_+=3){const T=t.getX(_+0),w=t.getX(_+1),E=t.getX(_+2);l.fromBufferAttribute(i,T),u.fromBufferAttribute(i,w),f.fromBufferAttribute(i,E),g.subVectors(f,u),v.subVectors(l,u),g.cross(v),p.fromBufferAttribute(r,T),m.fromBufferAttribute(r,w),d.fromBufferAttribute(r,E),p.add(g),m.add(g),d.add(g),r.setXYZ(T,p.x,p.y,p.z),r.setXYZ(w,m.x,m.y,m.z),r.setXYZ(E,d.x,d.y,d.z)}else for(let _=0,M=i.count;_<M;_+=3)l.fromBufferAttribute(i,_+0),u.fromBufferAttribute(i,_+1),f.fromBufferAttribute(i,_+2),g.subVectors(f,u),v.subVectors(l,u),g.cross(v),r.setXYZ(_+0,g.x,g.y,g.z),r.setXYZ(_+1,g.x,g.y,g.z),r.setXYZ(_+2,g.x,g.y,g.z);this.normalizeNormals(),r.needsUpdate=!0}}normalizeNormals(){const t=this.attributes.normal;for(let i=0,r=t.count;i<r;i++)bn.fromBufferAttribute(t,i),bn.normalize(),t.setXYZ(i,bn.x,bn.y,bn.z)}toNonIndexed(){function t(p,m){const d=p.array,g=p.itemSize,v=p.normalized,_=new d.constructor(m.length*g);let M=0,T=0;for(let w=0,E=m.length;w<E;w++){p.isInterleavedBufferAttribute?M=m[w]*p.data.stride+p.offset:M=m[w]*g;for(let S=0;S<g;S++)_[T++]=d[M++]}return new hi(_,g,v)}if(this.index===null)return te("BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const i=new Pi,r=this.index.array,l=this.attributes;for(const p in l){const m=l[p],d=t(m,r);i.setAttribute(p,d)}const u=this.morphAttributes;for(const p in u){const m=[],d=u[p];for(let g=0,v=d.length;g<v;g++){const _=d[g],M=t(_,r);m.push(M)}i.morphAttributes[p]=m}i.morphTargetsRelative=this.morphTargetsRelative;const f=this.groups;for(let p=0,m=f.length;p<m;p++){const d=f[p];i.addGroup(d.start,d.count,d.materialIndex)}return i}toJSON(){const t={metadata:{version:4.7,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(t.uuid=this.uuid,t.type=this.parameters!==void 0&&this._transformed===!0?"BufferGeometry":this.type,this.name!==""&&(t.name=this.name),Object.keys(this.userData).length>0&&(t.userData=this.userData),this.parameters!==void 0&&this._transformed!==!0){const m=this.parameters;for(const d in m)m[d]!==void 0&&(t[d]=m[d]);return t}t.data={attributes:{}};const i=this.index;i!==null&&(t.data.index={type:i.array.constructor.name,array:Array.prototype.slice.call(i.array)});const r=this.attributes;for(const m in r){const d=r[m];t.data.attributes[m]=d.toJSON(t.data)}const l={};let u=!1;for(const m in this.morphAttributes){const d=this.morphAttributes[m],g=[];for(let v=0,_=d.length;v<_;v++){const M=d[v];g.push(M.toJSON(t.data))}g.length>0&&(l[m]=g,u=!0)}u&&(t.data.morphAttributes=l,t.data.morphTargetsRelative=this.morphTargetsRelative);const f=this.groups;f.length>0&&(t.data.groups=JSON.parse(JSON.stringify(f)));const p=this.boundingSphere;return p!==null&&(t.data.boundingSphere=p.toJSON()),t}clone(){return new this.constructor().copy(this)}copy(t){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const i={};this.name=t.name;const r=t.index;r!==null&&this.setIndex(r.clone());const l=t.attributes;for(const d in l){const g=l[d];this.setAttribute(d,g.clone(i))}const u=t.morphAttributes;for(const d in u){const g=[],v=u[d];for(let _=0,M=v.length;_<M;_++)g.push(v[_].clone(i));this.morphAttributes[d]=g}this.morphTargetsRelative=t.morphTargetsRelative;const f=t.groups;for(let d=0,g=f.length;d<g;d++){const v=f[d];this.addGroup(v.start,v.count,v.materialIndex)}const p=t.boundingBox;p!==null&&(this.boundingBox=p.clone());const m=t.boundingSphere;return m!==null&&(this.boundingSphere=m.clone()),this.drawRange.start=t.drawRange.start,this.drawRange.count=t.drawRange.count,this.userData=t.userData,this._transformed=t._transformed,this}dispose(){this.dispatchEvent({type:"dispose"})}}let fM=0;class Js extends pr{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:fM++}),this.uuid=sl(),this.name="",this.type="Material",this.blending=ks,this.side=fr,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=jh,this.blendDst=$h,this.blendEquation=kr,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new xe(0,0,0),this.blendAlpha=0,this.depthFunc=qs,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=i0,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Rs,this.stencilZFail=Rs,this.stencilZPass=Rs,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.allowOverride=!0,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(t){this._alphaTest>0!=t>0&&this.version++,this._alphaTest=t}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(t){if(t!==void 0)for(const i in t){const r=t[i];if(r===void 0){te(`Material: parameter '${i}' has value of undefined.`);continue}const l=this[i];if(l===void 0){te(`Material: '${i}' is not a property of THREE.${this.type}.`);continue}l&&l.isColor?l.set(r):l&&l.isVector2&&r&&r.isVector2||l&&l.isEuler&&r&&r.isEuler||l&&l.isVector3&&r&&r.isVector3?l.copy(r):this[i]=r}}toJSON(t){const i=t===void 0||typeof t=="string";i&&(t={textures:{},images:{}});const r={metadata:{version:4.7,type:"Material",generator:"Material.toJSON"}};r.uuid=this.uuid,r.type=this.type,this.name!==""&&(r.name=this.name),this.color&&this.color.isColor&&(r.color=this.color.getHex()),this.roughness!==void 0&&(r.roughness=this.roughness),this.metalness!==void 0&&(r.metalness=this.metalness),this.sheen!==void 0&&(r.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(r.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(r.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(r.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(r.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(r.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(r.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(r.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(r.shininess=this.shininess),this.clearcoat!==void 0&&(r.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(r.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(r.clearcoatMap=this.clearcoatMap.toJSON(t).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(r.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(t).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(r.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(t).uuid,r.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.sheenColorMap&&this.sheenColorMap.isTexture&&(r.sheenColorMap=this.sheenColorMap.toJSON(t).uuid),this.sheenRoughnessMap&&this.sheenRoughnessMap.isTexture&&(r.sheenRoughnessMap=this.sheenRoughnessMap.toJSON(t).uuid),this.dispersion!==void 0&&(r.dispersion=this.dispersion),this.iridescence!==void 0&&(r.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(r.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(r.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(r.iridescenceMap=this.iridescenceMap.toJSON(t).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(r.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(t).uuid),this.anisotropy!==void 0&&(r.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(r.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(r.anisotropyMap=this.anisotropyMap.toJSON(t).uuid),this.map&&this.map.isTexture&&(r.map=this.map.toJSON(t).uuid),this.matcap&&this.matcap.isTexture&&(r.matcap=this.matcap.toJSON(t).uuid),this.alphaMap&&this.alphaMap.isTexture&&(r.alphaMap=this.alphaMap.toJSON(t).uuid),this.lightMap&&this.lightMap.isTexture&&(r.lightMap=this.lightMap.toJSON(t).uuid,r.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(r.aoMap=this.aoMap.toJSON(t).uuid,r.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(r.bumpMap=this.bumpMap.toJSON(t).uuid,r.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(r.normalMap=this.normalMap.toJSON(t).uuid,r.normalMapType=this.normalMapType,r.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(r.displacementMap=this.displacementMap.toJSON(t).uuid,r.displacementScale=this.displacementScale,r.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(r.roughnessMap=this.roughnessMap.toJSON(t).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(r.metalnessMap=this.metalnessMap.toJSON(t).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(r.emissiveMap=this.emissiveMap.toJSON(t).uuid),this.specularMap&&this.specularMap.isTexture&&(r.specularMap=this.specularMap.toJSON(t).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(r.specularIntensityMap=this.specularIntensityMap.toJSON(t).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(r.specularColorMap=this.specularColorMap.toJSON(t).uuid),this.envMap&&this.envMap.isTexture&&(r.envMap=this.envMap.toJSON(t).uuid,this.combine!==void 0&&(r.combine=this.combine)),this.envMapRotation!==void 0&&(r.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(r.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(r.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(r.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(r.gradientMap=this.gradientMap.toJSON(t).uuid),this.transmission!==void 0&&(r.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(r.transmissionMap=this.transmissionMap.toJSON(t).uuid),this.thickness!==void 0&&(r.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(r.thicknessMap=this.thicknessMap.toJSON(t).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(r.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(r.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(r.size=this.size),this.shadowSide!==null&&(r.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(r.sizeAttenuation=this.sizeAttenuation),this.blending!==ks&&(r.blending=this.blending),this.side!==fr&&(r.side=this.side),this.vertexColors===!0&&(r.vertexColors=!0),this.opacity<1&&(r.opacity=this.opacity),this.transparent===!0&&(r.transparent=!0),this.blendSrc!==jh&&(r.blendSrc=this.blendSrc),this.blendDst!==$h&&(r.blendDst=this.blendDst),this.blendEquation!==kr&&(r.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(r.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(r.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(r.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(r.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(r.blendAlpha=this.blendAlpha),this.depthFunc!==qs&&(r.depthFunc=this.depthFunc),this.depthTest===!1&&(r.depthTest=this.depthTest),this.depthWrite===!1&&(r.depthWrite=this.depthWrite),this.colorWrite===!1&&(r.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(r.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==i0&&(r.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(r.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(r.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Rs&&(r.stencilFail=this.stencilFail),this.stencilZFail!==Rs&&(r.stencilZFail=this.stencilZFail),this.stencilZPass!==Rs&&(r.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(r.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(r.rotation=this.rotation),this.polygonOffset===!0&&(r.polygonOffset=!0),this.polygonOffsetFactor!==0&&(r.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(r.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(r.linewidth=this.linewidth),this.dashSize!==void 0&&(r.dashSize=this.dashSize),this.gapSize!==void 0&&(r.gapSize=this.gapSize),this.scale!==void 0&&(r.scale=this.scale),this.dithering===!0&&(r.dithering=!0),this.alphaTest>0&&(r.alphaTest=this.alphaTest),this.alphaHash===!0&&(r.alphaHash=!0),this.alphaToCoverage===!0&&(r.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(r.premultipliedAlpha=!0),this.forceSinglePass===!0&&(r.forceSinglePass=!0),this.allowOverride===!1&&(r.allowOverride=!1),this.wireframe===!0&&(r.wireframe=!0),this.wireframeLinewidth>1&&(r.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(r.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(r.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(r.flatShading=!0),this.visible===!1&&(r.visible=!1),this.toneMapped===!1&&(r.toneMapped=!1),this.fog===!1&&(r.fog=!1),Object.keys(this.userData).length>0&&(r.userData=this.userData);function l(u){const f=[];for(const p in u){const m=u[p];delete m.metadata,f.push(m)}return f}if(i){const u=l(t.textures),f=l(t.images);u.length>0&&(r.textures=u),f.length>0&&(r.images=f)}return r}fromJSON(t,i){if(t.uuid!==void 0&&(this.uuid=t.uuid),t.name!==void 0&&(this.name=t.name),t.color!==void 0&&this.color!==void 0&&this.color.setHex(t.color),t.roughness!==void 0&&(this.roughness=t.roughness),t.metalness!==void 0&&(this.metalness=t.metalness),t.sheen!==void 0&&(this.sheen=t.sheen),t.sheenColor!==void 0&&(this.sheenColor=new xe().setHex(t.sheenColor)),t.sheenRoughness!==void 0&&(this.sheenRoughness=t.sheenRoughness),t.emissive!==void 0&&this.emissive!==void 0&&this.emissive.setHex(t.emissive),t.specular!==void 0&&this.specular!==void 0&&this.specular.setHex(t.specular),t.specularIntensity!==void 0&&(this.specularIntensity=t.specularIntensity),t.specularColor!==void 0&&this.specularColor!==void 0&&this.specularColor.setHex(t.specularColor),t.shininess!==void 0&&(this.shininess=t.shininess),t.clearcoat!==void 0&&(this.clearcoat=t.clearcoat),t.clearcoatRoughness!==void 0&&(this.clearcoatRoughness=t.clearcoatRoughness),t.dispersion!==void 0&&(this.dispersion=t.dispersion),t.iridescence!==void 0&&(this.iridescence=t.iridescence),t.iridescenceIOR!==void 0&&(this.iridescenceIOR=t.iridescenceIOR),t.iridescenceThicknessRange!==void 0&&(this.iridescenceThicknessRange=t.iridescenceThicknessRange),t.transmission!==void 0&&(this.transmission=t.transmission),t.thickness!==void 0&&(this.thickness=t.thickness),t.attenuationDistance!==void 0&&(this.attenuationDistance=t.attenuationDistance),t.attenuationColor!==void 0&&this.attenuationColor!==void 0&&this.attenuationColor.setHex(t.attenuationColor),t.anisotropy!==void 0&&(this.anisotropy=t.anisotropy),t.anisotropyRotation!==void 0&&(this.anisotropyRotation=t.anisotropyRotation),t.fog!==void 0&&(this.fog=t.fog),t.flatShading!==void 0&&(this.flatShading=t.flatShading),t.blending!==void 0&&(this.blending=t.blending),t.combine!==void 0&&(this.combine=t.combine),t.side!==void 0&&(this.side=t.side),t.shadowSide!==void 0&&(this.shadowSide=t.shadowSide),t.opacity!==void 0&&(this.opacity=t.opacity),t.transparent!==void 0&&(this.transparent=t.transparent),t.alphaTest!==void 0&&(this.alphaTest=t.alphaTest),t.alphaHash!==void 0&&(this.alphaHash=t.alphaHash),t.depthFunc!==void 0&&(this.depthFunc=t.depthFunc),t.depthTest!==void 0&&(this.depthTest=t.depthTest),t.depthWrite!==void 0&&(this.depthWrite=t.depthWrite),t.colorWrite!==void 0&&(this.colorWrite=t.colorWrite),t.blendSrc!==void 0&&(this.blendSrc=t.blendSrc),t.blendDst!==void 0&&(this.blendDst=t.blendDst),t.blendEquation!==void 0&&(this.blendEquation=t.blendEquation),t.blendSrcAlpha!==void 0&&(this.blendSrcAlpha=t.blendSrcAlpha),t.blendDstAlpha!==void 0&&(this.blendDstAlpha=t.blendDstAlpha),t.blendEquationAlpha!==void 0&&(this.blendEquationAlpha=t.blendEquationAlpha),t.blendColor!==void 0&&this.blendColor!==void 0&&this.blendColor.setHex(t.blendColor),t.blendAlpha!==void 0&&(this.blendAlpha=t.blendAlpha),t.stencilWriteMask!==void 0&&(this.stencilWriteMask=t.stencilWriteMask),t.stencilFunc!==void 0&&(this.stencilFunc=t.stencilFunc),t.stencilRef!==void 0&&(this.stencilRef=t.stencilRef),t.stencilFuncMask!==void 0&&(this.stencilFuncMask=t.stencilFuncMask),t.stencilFail!==void 0&&(this.stencilFail=t.stencilFail),t.stencilZFail!==void 0&&(this.stencilZFail=t.stencilZFail),t.stencilZPass!==void 0&&(this.stencilZPass=t.stencilZPass),t.stencilWrite!==void 0&&(this.stencilWrite=t.stencilWrite),t.wireframe!==void 0&&(this.wireframe=t.wireframe),t.wireframeLinewidth!==void 0&&(this.wireframeLinewidth=t.wireframeLinewidth),t.wireframeLinecap!==void 0&&(this.wireframeLinecap=t.wireframeLinecap),t.wireframeLinejoin!==void 0&&(this.wireframeLinejoin=t.wireframeLinejoin),t.rotation!==void 0&&(this.rotation=t.rotation),t.linewidth!==void 0&&(this.linewidth=t.linewidth),t.dashSize!==void 0&&(this.dashSize=t.dashSize),t.gapSize!==void 0&&(this.gapSize=t.gapSize),t.scale!==void 0&&(this.scale=t.scale),t.polygonOffset!==void 0&&(this.polygonOffset=t.polygonOffset),t.polygonOffsetFactor!==void 0&&(this.polygonOffsetFactor=t.polygonOffsetFactor),t.polygonOffsetUnits!==void 0&&(this.polygonOffsetUnits=t.polygonOffsetUnits),t.dithering!==void 0&&(this.dithering=t.dithering),t.alphaToCoverage!==void 0&&(this.alphaToCoverage=t.alphaToCoverage),t.premultipliedAlpha!==void 0&&(this.premultipliedAlpha=t.premultipliedAlpha),t.forceSinglePass!==void 0&&(this.forceSinglePass=t.forceSinglePass),t.allowOverride!==void 0&&(this.allowOverride=t.allowOverride),t.visible!==void 0&&(this.visible=t.visible),t.toneMapped!==void 0&&(this.toneMapped=t.toneMapped),t.userData!==void 0&&(this.userData=t.userData),t.vertexColors!==void 0&&(typeof t.vertexColors=="number"?this.vertexColors=t.vertexColors>0:this.vertexColors=t.vertexColors),t.size!==void 0&&(this.size=t.size),t.sizeAttenuation!==void 0&&(this.sizeAttenuation=t.sizeAttenuation),t.map!==void 0&&(this.map=i[t.map]||null),t.matcap!==void 0&&(this.matcap=i[t.matcap]||null),t.alphaMap!==void 0&&(this.alphaMap=i[t.alphaMap]||null),t.bumpMap!==void 0&&(this.bumpMap=i[t.bumpMap]||null),t.bumpScale!==void 0&&(this.bumpScale=t.bumpScale),t.normalMap!==void 0&&(this.normalMap=i[t.normalMap]||null),t.normalMapType!==void 0&&(this.normalMapType=t.normalMapType),t.normalScale!==void 0){let r=t.normalScale;Array.isArray(r)===!1&&(r=[r,r]),this.normalScale=new ie().fromArray(r)}return t.displacementMap!==void 0&&(this.displacementMap=i[t.displacementMap]||null),t.displacementScale!==void 0&&(this.displacementScale=t.displacementScale),t.displacementBias!==void 0&&(this.displacementBias=t.displacementBias),t.roughnessMap!==void 0&&(this.roughnessMap=i[t.roughnessMap]||null),t.metalnessMap!==void 0&&(this.metalnessMap=i[t.metalnessMap]||null),t.emissiveMap!==void 0&&(this.emissiveMap=i[t.emissiveMap]||null),t.emissiveIntensity!==void 0&&(this.emissiveIntensity=t.emissiveIntensity),t.specularMap!==void 0&&(this.specularMap=i[t.specularMap]||null),t.specularIntensityMap!==void 0&&(this.specularIntensityMap=i[t.specularIntensityMap]||null),t.specularColorMap!==void 0&&(this.specularColorMap=i[t.specularColorMap]||null),t.envMap!==void 0&&(this.envMap=i[t.envMap]||null),t.envMapRotation!==void 0&&this.envMapRotation.fromArray(t.envMapRotation),t.envMapIntensity!==void 0&&(this.envMapIntensity=t.envMapIntensity),t.reflectivity!==void 0&&(this.reflectivity=t.reflectivity),t.refractionRatio!==void 0&&(this.refractionRatio=t.refractionRatio),t.lightMap!==void 0&&(this.lightMap=i[t.lightMap]||null),t.lightMapIntensity!==void 0&&(this.lightMapIntensity=t.lightMapIntensity),t.aoMap!==void 0&&(this.aoMap=i[t.aoMap]||null),t.aoMapIntensity!==void 0&&(this.aoMapIntensity=t.aoMapIntensity),t.gradientMap!==void 0&&(this.gradientMap=i[t.gradientMap]||null),t.clearcoatMap!==void 0&&(this.clearcoatMap=i[t.clearcoatMap]||null),t.clearcoatRoughnessMap!==void 0&&(this.clearcoatRoughnessMap=i[t.clearcoatRoughnessMap]||null),t.clearcoatNormalMap!==void 0&&(this.clearcoatNormalMap=i[t.clearcoatNormalMap]||null),t.clearcoatNormalScale!==void 0&&(this.clearcoatNormalScale=new ie().fromArray(t.clearcoatNormalScale)),t.iridescenceMap!==void 0&&(this.iridescenceMap=i[t.iridescenceMap]||null),t.iridescenceThicknessMap!==void 0&&(this.iridescenceThicknessMap=i[t.iridescenceThicknessMap]||null),t.transmissionMap!==void 0&&(this.transmissionMap=i[t.transmissionMap]||null),t.thicknessMap!==void 0&&(this.thicknessMap=i[t.thicknessMap]||null),t.anisotropyMap!==void 0&&(this.anisotropyMap=i[t.anisotropyMap]||null),t.sheenColorMap!==void 0&&(this.sheenColorMap=i[t.sheenColorMap]||null),t.sheenRoughnessMap!==void 0&&(this.sheenRoughnessMap=i[t.sheenRoughnessMap]||null),this}clone(){return new this.constructor().copy(this)}copy(t){this.name=t.name,this.blending=t.blending,this.side=t.side,this.vertexColors=t.vertexColors,this.opacity=t.opacity,this.transparent=t.transparent,this.blendSrc=t.blendSrc,this.blendDst=t.blendDst,this.blendEquation=t.blendEquation,this.blendSrcAlpha=t.blendSrcAlpha,this.blendDstAlpha=t.blendDstAlpha,this.blendEquationAlpha=t.blendEquationAlpha,this.blendColor.copy(t.blendColor),this.blendAlpha=t.blendAlpha,this.depthFunc=t.depthFunc,this.depthTest=t.depthTest,this.depthWrite=t.depthWrite,this.stencilWriteMask=t.stencilWriteMask,this.stencilFunc=t.stencilFunc,this.stencilRef=t.stencilRef,this.stencilFuncMask=t.stencilFuncMask,this.stencilFail=t.stencilFail,this.stencilZFail=t.stencilZFail,this.stencilZPass=t.stencilZPass,this.stencilWrite=t.stencilWrite;const i=t.clippingPlanes;let r=null;if(i!==null){const l=i.length;r=new Array(l);for(let u=0;u!==l;++u)r[u]=i[u].clone()}return this.clippingPlanes=r,this.clipIntersection=t.clipIntersection,this.clipShadows=t.clipShadows,this.shadowSide=t.shadowSide,this.colorWrite=t.colorWrite,this.precision=t.precision,this.polygonOffset=t.polygonOffset,this.polygonOffsetFactor=t.polygonOffsetFactor,this.polygonOffsetUnits=t.polygonOffsetUnits,this.dithering=t.dithering,this.alphaTest=t.alphaTest,this.alphaHash=t.alphaHash,this.alphaToCoverage=t.alphaToCoverage,this.premultipliedAlpha=t.premultipliedAlpha,this.forceSinglePass=t.forceSinglePass,this.allowOverride=t.allowOverride,this.visible=t.visible,this.toneMapped=t.toneMapped,this.userData=JSON.parse(JSON.stringify(t.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(t){t===!0&&this.version++}}const ya=new $,zh=new $,Ru=new $,sr=new $,Bh=new $,Cu=new $,Hh=new $;class Ov{constructor(t=new $,i=new $(0,0,-1)){this.origin=t,this.direction=i}set(t,i){return this.origin.copy(t),this.direction.copy(i),this}copy(t){return this.origin.copy(t.origin),this.direction.copy(t.direction),this}at(t,i){return i.copy(this.origin).addScaledVector(this.direction,t)}lookAt(t){return this.direction.copy(t).sub(this.origin).normalize(),this}recast(t){return this.origin.copy(this.at(t,ya)),this}closestPointToPoint(t,i){i.subVectors(t,this.origin);const r=i.dot(this.direction);return r<0?i.copy(this.origin):i.copy(this.origin).addScaledVector(this.direction,r)}distanceToPoint(t){return Math.sqrt(this.distanceSqToPoint(t))}distanceSqToPoint(t){const i=ya.subVectors(t,this.origin).dot(this.direction);return i<0?this.origin.distanceToSquared(t):(ya.copy(this.origin).addScaledVector(this.direction,i),ya.distanceToSquared(t))}distanceSqToSegment(t,i,r,l){zh.copy(t).add(i).multiplyScalar(.5),Ru.copy(i).sub(t).normalize(),sr.copy(this.origin).sub(zh);const u=t.distanceTo(i)*.5,f=-this.direction.dot(Ru),p=sr.dot(this.direction),m=-sr.dot(Ru),d=sr.lengthSq(),g=Math.abs(1-f*f);let v,_,M,T;if(g>0)if(v=f*m-p,_=f*p-m,T=u*g,v>=0)if(_>=-T)if(_<=T){const w=1/g;v*=w,_*=w,M=v*(v+f*_+2*p)+_*(f*v+_+2*m)+d}else _=u,v=Math.max(0,-(f*_+p)),M=-v*v+_*(_+2*m)+d;else _=-u,v=Math.max(0,-(f*_+p)),M=-v*v+_*(_+2*m)+d;else _<=-T?(v=Math.max(0,-(-f*u+p)),_=v>0?-u:Math.min(Math.max(-u,-m),u),M=-v*v+_*(_+2*m)+d):_<=T?(v=0,_=Math.min(Math.max(-u,-m),u),M=_*(_+2*m)+d):(v=Math.max(0,-(f*u+p)),_=v>0?u:Math.min(Math.max(-u,-m),u),M=-v*v+_*(_+2*m)+d);else _=f>0?-u:u,v=Math.max(0,-(f*_+p)),M=-v*v+_*(_+2*m)+d;return r&&r.copy(this.origin).addScaledVector(this.direction,v),l&&l.copy(zh).addScaledVector(Ru,_),M}intersectSphere(t,i){ya.subVectors(t.center,this.origin);const r=ya.dot(this.direction),l=ya.dot(ya)-r*r,u=t.radius*t.radius;if(l>u)return null;const f=Math.sqrt(u-l),p=r-f,m=r+f;return m<0?null:p<0?this.at(m,i):this.at(p,i)}intersectsSphere(t){return t.radius<0?!1:this.distanceSqToPoint(t.center)<=t.radius*t.radius}distanceToPlane(t){const i=t.normal.dot(this.direction);if(i===0)return t.distanceToPoint(this.origin)===0?0:null;const r=-(this.origin.dot(t.normal)+t.constant)/i;return r>=0?r:null}intersectPlane(t,i){const r=this.distanceToPlane(t);return r===null?null:this.at(r,i)}intersectsPlane(t){const i=t.distanceToPoint(this.origin);return i===0||t.normal.dot(this.direction)*i<0}intersectBox(t,i){let r,l,u,f,p,m;const d=1/this.direction.x,g=1/this.direction.y,v=1/this.direction.z,_=this.origin;return d>=0?(r=(t.min.x-_.x)*d,l=(t.max.x-_.x)*d):(r=(t.max.x-_.x)*d,l=(t.min.x-_.x)*d),g>=0?(u=(t.min.y-_.y)*g,f=(t.max.y-_.y)*g):(u=(t.max.y-_.y)*g,f=(t.min.y-_.y)*g),r>f||u>l||((u>r||isNaN(r))&&(r=u),(f<l||isNaN(l))&&(l=f),v>=0?(p=(t.min.z-_.z)*v,m=(t.max.z-_.z)*v):(p=(t.max.z-_.z)*v,m=(t.min.z-_.z)*v),r>m||p>l)||((p>r||r!==r)&&(r=p),(m<l||l!==l)&&(l=m),l<0)?null:this.at(r>=0?r:l,i)}intersectsBox(t){return this.intersectBox(t,ya)!==null}intersectTriangle(t,i,r,l,u){Bh.subVectors(i,t),Cu.subVectors(r,t),Hh.crossVectors(Bh,Cu);let f=this.direction.dot(Hh),p;if(f>0){if(l)return null;p=1}else if(f<0)p=-1,f=-f;else return null;sr.subVectors(this.origin,t);const m=p*this.direction.dot(Cu.crossVectors(sr,Cu));if(m<0)return null;const d=p*this.direction.dot(Bh.cross(sr));if(d<0||m+d>f)return null;const g=-p*sr.dot(Hh);return g<0?null:this.at(g/f,u)}applyMatrix4(t){return this.origin.applyMatrix4(t),this.direction.transformDirection(t),this}equals(t){return t.origin.equals(this.origin)&&t.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Pv extends Js{constructor(t){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new xe(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new dr,this.combine=hv,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.color.copy(t.color),this.map=t.map,this.lightMap=t.lightMap,this.lightMapIntensity=t.lightMapIntensity,this.aoMap=t.aoMap,this.aoMapIntensity=t.aoMapIntensity,this.specularMap=t.specularMap,this.alphaMap=t.alphaMap,this.envMap=t.envMap,this.envMapRotation.copy(t.envMapRotation),this.combine=t.combine,this.reflectivity=t.reflectivity,this.refractionRatio=t.refractionRatio,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.wireframeLinecap=t.wireframeLinecap,this.wireframeLinejoin=t.wireframeLinejoin,this.fog=t.fog,this}}const x0=new $e,Fr=new Ov,wu=new tp,S0=new $,Du=new $,Uu=new $,Lu=new $,Gh=new $,Nu=new $,y0=new $,Ou=new $;class Qi extends Un{constructor(t=new Pi,i=new Pv){super(),this.isMesh=!0,this.type="Mesh",this.geometry=t,this.material=i,this.morphTargetDictionary=void 0,this.morphTargetInfluences=void 0,this.count=1,this.updateMorphTargets()}copy(t,i){return super.copy(t,i),t.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=t.morphTargetInfluences.slice()),t.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},t.morphTargetDictionary)),this.material=Array.isArray(t.material)?t.material.slice():t.material,this.geometry=t.geometry,this}updateMorphTargets(){const i=this.geometry.morphAttributes,r=Object.keys(i);if(r.length>0){const l=i[r[0]];if(l!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let u=0,f=l.length;u<f;u++){const p=l[u].name||String(u);this.morphTargetInfluences.push(0),this.morphTargetDictionary[p]=u}}}}getVertexPosition(t,i){const r=this.geometry,l=r.attributes.position,u=r.morphAttributes.position,f=r.morphTargetsRelative;i.fromBufferAttribute(l,t);const p=this.morphTargetInfluences;if(u&&p){Nu.set(0,0,0);for(let m=0,d=u.length;m<d;m++){const g=p[m],v=u[m];g!==0&&(Gh.fromBufferAttribute(v,t),f?Nu.addScaledVector(Gh,g):Nu.addScaledVector(Gh.sub(i),g))}i.add(Nu)}return i}raycast(t,i){const r=this.geometry,l=this.material,u=this.matrixWorld;l!==void 0&&(r.boundingSphere===null&&r.computeBoundingSphere(),wu.copy(r.boundingSphere),wu.applyMatrix4(u),Fr.copy(t.ray).recast(t.near),!(wu.containsPoint(Fr.origin)===!1&&(Fr.intersectSphere(wu,S0)===null||Fr.origin.distanceToSquared(S0)>(t.far-t.near)**2))&&(x0.copy(u).invert(),Fr.copy(t.ray).applyMatrix4(x0),!(r.boundingBox!==null&&Fr.intersectsBox(r.boundingBox)===!1)&&this._computeIntersections(t,i,Fr)))}_computeIntersections(t,i,r){let l;const u=this.geometry,f=this.material,p=u.index,m=u.attributes.position,d=u.attributes.uv,g=u.attributes.uv1,v=u.attributes.normal,_=u.groups,M=u.drawRange;if(p!==null)if(Array.isArray(f))for(let T=0,w=_.length;T<w;T++){const E=_[T],S=f[E.materialIndex],F=Math.max(E.start,M.start),z=Math.min(p.count,Math.min(E.start+E.count,M.start+M.count));for(let C=F,N=z;C<N;C+=3){const D=p.getX(C),O=p.getX(C+1),b=p.getX(C+2);l=Pu(this,S,t,r,d,g,v,D,O,b),l&&(l.faceIndex=Math.floor(C/3),l.face.materialIndex=E.materialIndex,i.push(l))}}else{const T=Math.max(0,M.start),w=Math.min(p.count,M.start+M.count);for(let E=T,S=w;E<S;E+=3){const F=p.getX(E),z=p.getX(E+1),C=p.getX(E+2);l=Pu(this,f,t,r,d,g,v,F,z,C),l&&(l.faceIndex=Math.floor(E/3),i.push(l))}}else if(m!==void 0)if(Array.isArray(f))for(let T=0,w=_.length;T<w;T++){const E=_[T],S=f[E.materialIndex],F=Math.max(E.start,M.start),z=Math.min(m.count,Math.min(E.start+E.count,M.start+M.count));for(let C=F,N=z;C<N;C+=3){const D=C,O=C+1,b=C+2;l=Pu(this,S,t,r,d,g,v,D,O,b),l&&(l.faceIndex=Math.floor(C/3),l.face.materialIndex=E.materialIndex,i.push(l))}}else{const T=Math.max(0,M.start),w=Math.min(m.count,M.start+M.count);for(let E=T,S=w;E<S;E+=3){const F=E,z=E+1,C=E+2;l=Pu(this,f,t,r,d,g,v,F,z,C),l&&(l.faceIndex=Math.floor(E/3),i.push(l))}}}}function hM(s,t,i,r,l,u,f,p){let m;if(t.side===Qn?m=r.intersectTriangle(f,u,l,!0,p):m=r.intersectTriangle(l,u,f,t.side===fr,p),m===null)return null;Ou.copy(p),Ou.applyMatrix4(s.matrixWorld);const d=i.ray.origin.distanceTo(Ou);return d<i.near||d>i.far?null:{distance:d,point:Ou.clone(),object:s}}function Pu(s,t,i,r,l,u,f,p,m,d){s.getVertexPosition(p,Du),s.getVertexPosition(m,Uu),s.getVertexPosition(d,Lu);const g=hM(s,t,i,r,Du,Uu,Lu,y0);if(g){const v=new $;Li.getBarycoord(y0,Du,Uu,Lu,v),l&&(g.uv=Li.getInterpolatedAttribute(l,p,m,d,v,new ie)),u&&(g.uv1=Li.getInterpolatedAttribute(u,p,m,d,v,new ie)),f&&(g.normal=Li.getInterpolatedAttribute(f,p,m,d,v,new $),g.normal.dot(r.direction)>0&&g.normal.multiplyScalar(-1));const _={a:p,b:m,c:d,normal:new $,materialIndex:0};Li.getNormal(Du,Uu,Lu,_.normal),g.face=_,g.barycoord=v}return g}class dM extends Hn{constructor(t=null,i=1,r=1,l,u,f,p,m,d=Dn,g=Dn,v,_){super(null,f,p,m,d,g,l,u,v,_),this.isDataTexture=!0,this.image={data:t,width:i,height:r},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Vh=new $,pM=new $,mM=new re;class lr{constructor(t=new $(1,0,0),i=0){this.isPlane=!0,this.normal=t,this.constant=i}set(t,i){return this.normal.copy(t),this.constant=i,this}setComponents(t,i,r,l){return this.normal.set(t,i,r),this.constant=l,this}setFromNormalAndCoplanarPoint(t,i){return this.normal.copy(t),this.constant=-i.dot(this.normal),this}setFromCoplanarPoints(t,i,r){const l=Vh.subVectors(r,i).cross(pM.subVectors(t,i)).normalize();return this.setFromNormalAndCoplanarPoint(l,t),this}copy(t){return this.normal.copy(t.normal),this.constant=t.constant,this}normalize(){const t=1/this.normal.length();return this.normal.multiplyScalar(t),this.constant*=t,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(t){return this.normal.dot(t)+this.constant}distanceToSphere(t){return this.distanceToPoint(t.center)-t.radius}projectPoint(t,i){return i.copy(t).addScaledVector(this.normal,-this.distanceToPoint(t))}intersectLine(t,i,r=!0){const l=t.delta(Vh),u=this.normal.dot(l);if(u===0)return this.distanceToPoint(t.start)===0?i.copy(t.start):null;const f=-(t.start.dot(this.normal)+this.constant)/u;return r===!0&&(f<0||f>1)?null:i.copy(t.start).addScaledVector(l,f)}intersectsLine(t){const i=this.distanceToPoint(t.start),r=this.distanceToPoint(t.end);return i<0&&r>0||r<0&&i>0}intersectsBox(t){return t.intersectsPlane(this)}intersectsSphere(t){return t.intersectsPlane(this)}coplanarPoint(t){return t.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(t,i){const r=i||mM.getNormalMatrix(t),l=this.coplanarPoint(Vh).applyMatrix4(t),u=this.normal.applyMatrix3(r).normalize();return this.constant=-l.dot(u),this}translate(t){return this.constant-=t.dot(this.normal),this}equals(t){return t.normal.equals(this.normal)&&t.constant===this.constant}clone(){return new this.constructor().copy(this)}}const zr=new tp,gM=new ie(.5,.5),Iu=new $;class ep{constructor(t=new lr,i=new lr,r=new lr,l=new lr,u=new lr,f=new lr){this.planes=[t,i,r,l,u,f]}set(t,i,r,l,u,f){const p=this.planes;return p[0].copy(t),p[1].copy(i),p[2].copy(r),p[3].copy(l),p[4].copy(u),p[5].copy(f),this}copy(t){const i=this.planes;for(let r=0;r<6;r++)i[r].copy(t.planes[r]);return this}setFromProjectionMatrix(t,i=qi,r=!1){const l=this.planes,u=t.elements,f=u[0],p=u[1],m=u[2],d=u[3],g=u[4],v=u[5],_=u[6],M=u[7],T=u[8],w=u[9],E=u[10],S=u[11],F=u[12],z=u[13],C=u[14],N=u[15];if(l[0].setComponents(d-f,M-g,S-T,N-F).normalize(),l[1].setComponents(d+f,M+g,S+T,N+F).normalize(),l[2].setComponents(d+p,M+v,S+w,N+z).normalize(),l[3].setComponents(d-p,M-v,S-w,N-z).normalize(),r)l[4].setComponents(m,_,E,C).normalize(),l[5].setComponents(d-m,M-_,S-E,N-C).normalize();else if(l[4].setComponents(d-m,M-_,S-E,N-C).normalize(),i===qi)l[5].setComponents(d+m,M+_,S+E,N+C).normalize();else if(i===rl)l[5].setComponents(m,_,E,C).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+i);return this}intersectsObject(t){if(t.boundingSphere!==void 0)t.boundingSphere===null&&t.computeBoundingSphere(),zr.copy(t.boundingSphere).applyMatrix4(t.matrixWorld);else{const i=t.geometry;i.boundingSphere===null&&i.computeBoundingSphere(),zr.copy(i.boundingSphere).applyMatrix4(t.matrixWorld)}return this.intersectsSphere(zr)}intersectsSprite(t){zr.center.set(0,0,0);const i=gM.distanceTo(t.center);return zr.radius=.7071067811865476+i,zr.applyMatrix4(t.matrixWorld),this.intersectsSphere(zr)}intersectsSphere(t){const i=this.planes,r=t.center,l=-t.radius;for(let u=0;u<6;u++)if(i[u].distanceToPoint(r)<l)return!1;return!0}intersectsBox(t){const i=this.planes;for(let r=0;r<6;r++){const l=i[r];if(Iu.x=l.normal.x>0?t.max.x:t.min.x,Iu.y=l.normal.y>0?t.max.y:t.min.y,Iu.z=l.normal.z>0?t.max.z:t.min.z,l.distanceToPoint(Iu)<0)return!1}return!0}containsPoint(t){const i=this.planes;for(let r=0;r<6;r++)if(i[r].distanceToPoint(t)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}class Iv extends Hn{constructor(t=[],i=Yr,r,l,u,f,p,m,d,g){super(t,i,r,l,u,f,p,m,d,g),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(t){this.image=t}}class Zs extends Hn{constructor(t,i,r=Ki,l,u,f,p=Dn,m=Dn,d,g=Ca,v=1){if(g!==Ca&&g!==qr)throw new Error("THREE.DepthTexture: format must be either THREE.DepthFormat or THREE.DepthStencilFormat");const _={width:t,height:i,depth:v};super(_,l,u,f,p,m,g,r,d),this.isDepthTexture=!0,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(t){return super.copy(t),this.source=new $d(Object.assign({},t.image)),this.compareFunction=t.compareFunction,this}toJSON(t){const i=super.toJSON(t);return this.compareFunction!==null&&(i.compareFunction=this.compareFunction),i}}class _M extends Zs{constructor(t,i=Ki,r=Yr,l,u,f=Dn,p=Dn,m,d=Ca){const g={width:t,height:t,depth:1},v=[g,g,g,g,g,g];super(t,t,i,r,l,u,f,p,m,d),this.image=v,this.isCubeDepthTexture=!0,this.isCubeTexture=!0}get images(){return this.image}set images(t){this.image=t}}class Fv extends Hn{constructor(t=null){super(),this.sourceTexture=t,this.isExternalTexture=!0}copy(t){return super.copy(t),this.sourceTexture=t.sourceTexture,this}}class ol extends Pi{constructor(t=1,i=1,r=1,l=1,u=1,f=1){super(),this.type="BoxGeometry",this.parameters={width:t,height:i,depth:r,widthSegments:l,heightSegments:u,depthSegments:f};const p=this;l=Math.floor(l),u=Math.floor(u),f=Math.floor(f);const m=[],d=[],g=[],v=[];let _=0,M=0;T("z","y","x",-1,-1,r,i,t,f,u,0),T("z","y","x",1,-1,r,i,-t,f,u,1),T("x","z","y",1,1,t,r,i,l,f,2),T("x","z","y",1,-1,t,r,-i,l,f,3),T("x","y","z",1,-1,t,i,r,l,u,4),T("x","y","z",-1,-1,t,i,-r,l,u,5),this.setIndex(m),this.setAttribute("position",new Oi(d,3)),this.setAttribute("normal",new Oi(g,3)),this.setAttribute("uv",new Oi(v,2));function T(w,E,S,F,z,C,N,D,O,b,P){const q=C/O,G=N/b,Z=C/2,ht=N/2,mt=D/2,J=O+1,I=b+1;let H=0,j=0;const gt=new $;for(let Et=0;Et<I;Et++){const L=Et*G-ht;for(let K=0;K<J;K++){const Mt=K*q-Z;gt[w]=Mt*F,gt[E]=L*z,gt[S]=mt,d.push(gt.x,gt.y,gt.z),gt[w]=0,gt[E]=0,gt[S]=D>0?1:-1,g.push(gt.x,gt.y,gt.z),v.push(K/O),v.push(1-Et/b),H+=1}}for(let Et=0;Et<b;Et++)for(let L=0;L<O;L++){const K=_+L+J*Et,Mt=_+L+J*(Et+1),Rt=_+(L+1)+J*(Et+1),Pt=_+(L+1)+J*Et;m.push(K,Mt,Pt),m.push(Mt,Rt,Pt),j+=6}p.addGroup(M,j,P),M+=j,_+=H}}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new ol(t.width,t.height,t.depth,t.widthSegments,t.heightSegments,t.depthSegments)}}class ic extends Pi{constructor(t=1,i=1,r=1,l=1){super(),this.type="PlaneGeometry",this.parameters={width:t,height:i,widthSegments:r,heightSegments:l};const u=t/2,f=i/2,p=Math.floor(r),m=Math.floor(l),d=p+1,g=m+1,v=t/p,_=i/m,M=[],T=[],w=[],E=[];for(let S=0;S<g;S++){const F=S*_-f;for(let z=0;z<d;z++){const C=z*v-u;T.push(C,-F,0),w.push(0,0,1),E.push(z/p),E.push(1-S/m)}}for(let S=0;S<m;S++)for(let F=0;F<p;F++){const z=F+d*S,C=F+d*(S+1),N=F+1+d*(S+1),D=F+1+d*S;M.push(z,C,D),M.push(C,N,D)}this.setIndex(M),this.setAttribute("position",new Oi(T,3)),this.setAttribute("normal",new Oi(w,3)),this.setAttribute("uv",new Oi(E,2))}copy(t){return super.copy(t),this.parameters=Object.assign({},t.parameters),this}static fromJSON(t){return new ic(t.width,t.height,t.widthSegments,t.heightSegments)}}function Ks(s){const t={};for(const i in s){t[i]={};for(const r in s[i]){const l=s[i][r];if(M0(l))l.isRenderTargetTexture?(te("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),t[i][r]=null):t[i][r]=l.clone();else if(Array.isArray(l))if(M0(l[0])){const u=[];for(let f=0,p=l.length;f<p;f++)u[f]=l[f].clone();t[i][r]=u}else t[i][r]=l.slice();else t[i][r]=l}}return t}function zn(s){const t={};for(let i=0;i<s.length;i++){const r=Ks(s[i]);for(const l in r)t[l]=r[l]}return t}function M0(s){return s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)}function vM(s){const t=[];for(let i=0;i<s.length;i++)t.push(s[i].clone());return t}function zv(s){const t=s.getRenderTarget();return t===null?s.outputColorSpace:t.isXRRenderTarget===!0?t.texture.colorSpace:Ee.workingColorSpace}const xM={clone:Ks,merge:zn};var SM=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,yM=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Ji extends Js{constructor(t){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=SM,this.fragmentShader=yM,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,t!==void 0&&this.setValues(t)}copy(t){return super.copy(t),this.fragmentShader=t.fragmentShader,this.vertexShader=t.vertexShader,this.uniforms=Ks(t.uniforms),this.uniformsGroups=vM(t.uniformsGroups),this.defines=Object.assign({},t.defines),this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.fog=t.fog,this.lights=t.lights,this.clipping=t.clipping,this.extensions=Object.assign({},t.extensions),this.glslVersion=t.glslVersion,this.defaultAttributeValues=Object.assign({},t.defaultAttributeValues),this.index0AttributeName=t.index0AttributeName,this.uniformsNeedUpdate=t.uniformsNeedUpdate,this}toJSON(t){const i=super.toJSON(t);i.glslVersion=this.glslVersion,i.uniforms={};for(const l in this.uniforms){const f=this.uniforms[l].value;f&&f.isTexture?i.uniforms[l]={type:"t",value:f.toJSON(t).uuid}:f&&f.isColor?i.uniforms[l]={type:"c",value:f.getHex()}:f&&f.isVector2?i.uniforms[l]={type:"v2",value:f.toArray()}:f&&f.isVector3?i.uniforms[l]={type:"v3",value:f.toArray()}:f&&f.isVector4?i.uniforms[l]={type:"v4",value:f.toArray()}:f&&f.isMatrix3?i.uniforms[l]={type:"m3",value:f.toArray()}:f&&f.isMatrix4?i.uniforms[l]={type:"m4",value:f.toArray()}:i.uniforms[l]={value:f}}Object.keys(this.defines).length>0&&(i.defines=this.defines),i.vertexShader=this.vertexShader,i.fragmentShader=this.fragmentShader,i.lights=this.lights,i.clipping=this.clipping;const r={};for(const l in this.extensions)this.extensions[l]===!0&&(r[l]=!0);return Object.keys(r).length>0&&(i.extensions=r),i}fromJSON(t,i){if(super.fromJSON(t,i),t.uniforms!==void 0)for(const r in t.uniforms){const l=t.uniforms[r];switch(this.uniforms[r]={},l.type){case"t":this.uniforms[r].value=i[l.value]||null;break;case"c":this.uniforms[r].value=new xe().setHex(l.value);break;case"v2":this.uniforms[r].value=new ie().fromArray(l.value);break;case"v3":this.uniforms[r].value=new $().fromArray(l.value);break;case"v4":this.uniforms[r].value=new tn().fromArray(l.value);break;case"m3":this.uniforms[r].value=new re().fromArray(l.value);break;case"m4":this.uniforms[r].value=new $e().fromArray(l.value);break;default:this.uniforms[r].value=l.value}}if(t.defines!==void 0&&(this.defines=t.defines),t.vertexShader!==void 0&&(this.vertexShader=t.vertexShader),t.fragmentShader!==void 0&&(this.fragmentShader=t.fragmentShader),t.glslVersion!==void 0&&(this.glslVersion=t.glslVersion),t.extensions!==void 0)for(const r in t.extensions)this.extensions[r]=t.extensions[r];return t.lights!==void 0&&(this.lights=t.lights),t.clipping!==void 0&&(this.clipping=t.clipping),this}}class MM extends Ji{constructor(t){super(t),this.isRawShaderMaterial=!0,this.type="RawShaderMaterial"}}class EM extends Js{constructor(t){super(),this.isMeshStandardMaterial=!0,this.type="MeshStandardMaterial",this.defines={STANDARD:""},this.color=new xe(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new xe(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Ju,this.normalScale=new ie(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new dr,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(t)}copy(t){return super.copy(t),this.defines={STANDARD:""},this.color.copy(t.color),this.roughness=t.roughness,this.metalness=t.metalness,this.map=t.map,this.lightMap=t.lightMap,this.lightMapIntensity=t.lightMapIntensity,this.aoMap=t.aoMap,this.aoMapIntensity=t.aoMapIntensity,this.emissive.copy(t.emissive),this.emissiveMap=t.emissiveMap,this.emissiveIntensity=t.emissiveIntensity,this.bumpMap=t.bumpMap,this.bumpScale=t.bumpScale,this.normalMap=t.normalMap,this.normalMapType=t.normalMapType,this.normalScale.copy(t.normalScale),this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this.roughnessMap=t.roughnessMap,this.metalnessMap=t.metalnessMap,this.alphaMap=t.alphaMap,this.envMap=t.envMap,this.envMapRotation.copy(t.envMapRotation),this.envMapIntensity=t.envMapIntensity,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.wireframeLinecap=t.wireframeLinecap,this.wireframeLinejoin=t.wireframeLinejoin,this.flatShading=t.flatShading,this.fog=t.fog,this}}class bM extends Js{constructor(t){super(),this.isMeshNormalMaterial=!0,this.type="MeshNormalMaterial",this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Ju,this.normalScale=new ie(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.flatShading=!1,this.setValues(t)}copy(t){return super.copy(t),this.bumpMap=t.bumpMap,this.bumpScale=t.bumpScale,this.normalMap=t.normalMap,this.normalMapType=t.normalMapType,this.normalScale.copy(t.normalScale),this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this.flatShading=t.flatShading,this}}class TM extends Js{constructor(t){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=Oy,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(t)}copy(t){return super.copy(t),this.depthPacking=t.depthPacking,this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this.wireframe=t.wireframe,this.wireframeLinewidth=t.wireframeLinewidth,this}}class AM extends Js{constructor(t){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(t)}copy(t){return super.copy(t),this.map=t.map,this.alphaMap=t.alphaMap,this.displacementMap=t.displacementMap,this.displacementScale=t.displacementScale,this.displacementBias=t.displacementBias,this}}const E0={enabled:!1,files:{},add:function(s,t){this.enabled!==!1&&(b0(s)||(this.files[s]=t))},get:function(s){if(this.enabled!==!1&&!b0(s))return this.files[s]},remove:function(s){delete this.files[s]},clear:function(){this.files={}}};function b0(s){try{const t=s.slice(s.indexOf(":")+1);return new URL(t).protocol==="blob:"}catch{return!1}}class RM{constructor(t,i,r){const l=this;let u=!1,f=0,p=0,m;const d=[];this.onStart=void 0,this.onLoad=t,this.onProgress=i,this.onError=r,this._abortController=null,this.itemStart=function(g){p++,u===!1&&l.onStart!==void 0&&l.onStart(g,f,p),u=!0},this.itemEnd=function(g){f++,l.onProgress!==void 0&&l.onProgress(g,f,p),f===p&&(u=!1,l.onLoad!==void 0&&l.onLoad())},this.itemError=function(g){l.onError!==void 0&&l.onError(g)},this.resolveURL=function(g){return g=g.normalize("NFC"),m?m(g):g},this.setURLModifier=function(g){return m=g,this},this.addHandler=function(g,v){return d.push(g,v),this},this.removeHandler=function(g){const v=d.indexOf(g);return v!==-1&&d.splice(v,2),this},this.getHandler=function(g){for(let v=0,_=d.length;v<_;v+=2){const M=d[v],T=d[v+1];if(M.global&&(M.lastIndex=0),M.test(g))return T}return null},this.abort=function(){return this.abortController.abort(),this._abortController=null,this}}get abortController(){return this._abortController||(this._abortController=new AbortController),this._abortController}}const CM=new RM;class np{constructor(t){this.manager=t!==void 0?t:CM,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}load(){}loadAsync(t,i){const r=this;return new Promise(function(l,u){r.load(t,l,i,u)})}parse(){}setCrossOrigin(t){return this.crossOrigin=t,this}setWithCredentials(t){return this.withCredentials=t,this}setPath(t){return this.path=t,this}setResourcePath(t){return this.resourcePath=t,this}setRequestHeader(t){return this.requestHeader=t,this}abort(){return this}}np.DEFAULT_MATERIAL_NAME="__DEFAULT";const Ma={};class wM extends Error{constructor(t,i){super(t),this.response=i}}class DM extends np{constructor(t){super(t),this.mimeType="",this.responseType="",this._abortController=new AbortController}load(t,i,r,l){t===void 0&&(t=""),this.path!==void 0&&(t=this.path+t),t=this.manager.resolveURL(t);const u=E0.get(`file:${t}`);if(u!==void 0){this.manager.itemStart(t),setTimeout(()=>{i&&i(u),this.manager.itemEnd(t)},0);return}if(Ma[t]!==void 0){Ma[t].push({onLoad:i,onProgress:r,onError:l});return}Ma[t]=[],Ma[t].push({onLoad:i,onProgress:r,onError:l});const f=new Request(t,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin",signal:typeof AbortSignal.any=="function"?AbortSignal.any([this._abortController.signal,this.manager.abortController.signal]):this._abortController.signal}),p=this.mimeType,m=this.responseType;fetch(f).then(d=>{if(d.status===200||d.status===0){if(d.status===0&&te("FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||d.body===void 0||d.body.getReader===void 0)return d;const g=Ma[t],v=d.body.getReader(),_=d.headers.get("X-File-Size")||d.headers.get("Content-Length"),M=_?parseInt(_):0,T=M!==0;let w=0;const E=new ReadableStream({start(S){F();function F(){v.read().then(({done:z,value:C})=>{if(z)S.close();else{w+=C.byteLength;const N=new ProgressEvent("progress",{lengthComputable:T,loaded:w,total:M});for(let D=0,O=g.length;D<O;D++){const b=g[D];b.onProgress&&b.onProgress(N)}S.enqueue(C),F()}},z=>{S.error(z)})}}});return new Response(E)}else throw new wM(`fetch for "${d.url}" responded with ${d.status}: ${d.statusText}`,d)}).then(d=>{switch(m){case"arraybuffer":return d.arrayBuffer();case"blob":return d.blob();case"document":return d.text().then(g=>new DOMParser().parseFromString(g,p));case"json":return d.json();default:if(p==="")return d.text();{const v=/charset="?([^;"\s]*)"?/i.exec(p),_=v&&v[1]?v[1].toLowerCase():void 0,M=new TextDecoder(_);return d.arrayBuffer().then(T=>M.decode(T))}}}).then(d=>{E0.add(`file:${t}`,d);const g=Ma[t];delete Ma[t];for(let v=0,_=g.length;v<_;v++){const M=g[v];M.onLoad&&M.onLoad(d)}}).catch(d=>{const g=Ma[t];if(g===void 0)throw this.manager.itemError(t),d;delete Ma[t];for(let v=0,_=g.length;v<_;v++){const M=g[v];M.onError&&M.onError(d)}this.manager.itemError(t)}).finally(()=>{this.manager.itemEnd(t)}),this.manager.itemStart(t)}setResponseType(t){return this.responseType=t,this}setMimeType(t){return this.mimeType=t,this}abort(){return this._abortController.abort(),this._abortController=new AbortController,this}}class Bv extends Un{constructor(t,i=1){super(),this.isLight=!0,this.type="Light",this.color=new xe(t),this.intensity=i}dispose(){this.dispatchEvent({type:"dispose"})}copy(t,i){return super.copy(t,i),this.color.copy(t.color),this.intensity=t.intensity,this}toJSON(t){const i=super.toJSON(t);return i.object.color=this.color.getHex(),i.object.intensity=this.intensity,i}}class UM extends Bv{constructor(t,i,r){super(t,r),this.isHemisphereLight=!0,this.type="HemisphereLight",this.position.copy(Un.DEFAULT_UP),this.updateMatrix(),this.groundColor=new xe(i)}copy(t,i){return super.copy(t,i),this.groundColor.copy(t.groundColor),this}toJSON(t){const i=super.toJSON(t);return i.object.groundColor=this.groundColor.getHex(),i}}const kh=new $e,T0=new $,A0=new $;class LM{constructor(t){this.camera=t,this.intensity=1,this.bias=0,this.biasNode=null,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new ie(512,512),this.mapType=fi,this.map=null,this.mapPass=null,this.matrix=new $e,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new ep,this._frameExtents=new ie(1,1),this._viewportCount=1,this._viewports=[new tn(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(t){const i=this.camera,r=this.matrix;T0.setFromMatrixPosition(t.matrixWorld),i.position.copy(T0),A0.setFromMatrixPosition(t.target.matrixWorld),i.lookAt(A0),i.updateMatrixWorld(),kh.multiplyMatrices(i.projectionMatrix,i.matrixWorldInverse),this._frustum.setFromProjectionMatrix(kh,i.coordinateSystem,i.reversedDepth),i.coordinateSystem===rl||i.reversedDepth?r.set(.5,0,0,.5,0,.5,0,.5,0,0,1,0,0,0,0,1):r.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),r.multiply(kh)}getViewport(t){return this._viewports[t]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(t){return this.camera=t.camera.clone(),this.intensity=t.intensity,this.bias=t.bias,this.radius=t.radius,this.autoUpdate=t.autoUpdate,this.needsUpdate=t.needsUpdate,this.normalBias=t.normalBias,this.blurSamples=t.blurSamples,this.mapSize.copy(t.mapSize),this.biasNode=t.biasNode,this}clone(){return new this.constructor().copy(this)}toJSON(){const t={};return this.intensity!==1&&(t.intensity=this.intensity),this.bias!==0&&(t.bias=this.bias),this.normalBias!==0&&(t.normalBias=this.normalBias),this.radius!==1&&(t.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(t.mapSize=this.mapSize.toArray()),t.camera=this.camera.toJSON(!1).object,delete t.camera.matrix,t}}const Fu=new $,zu=new hr,Vi=new $;class Hv extends Un{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new $e,this.projectionMatrix=new $e,this.projectionMatrixInverse=new $e,this.coordinateSystem=qi,this._reversedDepth=!1}get reversedDepth(){return this._reversedDepth}copy(t,i){return super.copy(t,i),this.matrixWorldInverse.copy(t.matrixWorldInverse),this.projectionMatrix.copy(t.projectionMatrix),this.projectionMatrixInverse.copy(t.projectionMatrixInverse),this.coordinateSystem=t.coordinateSystem,this}getWorldDirection(t){return super.getWorldDirection(t).negate()}updateMatrixWorld(t){super.updateMatrixWorld(t),this.matrixWorld.decompose(Fu,zu,Vi),Vi.x===1&&Vi.y===1&&Vi.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(Fu,zu,Vi.set(1,1,1)).invert()}updateWorldMatrix(t,i,r=!1){super.updateWorldMatrix(t,i,r),this.matrixWorld.decompose(Fu,zu,Vi),Vi.x===1&&Vi.y===1&&Vi.z===1?this.matrixWorldInverse.copy(this.matrixWorld).invert():this.matrixWorldInverse.compose(Fu,zu,Vi.set(1,1,1)).invert()}clone(){return new this.constructor().copy(this)}}const or=new $,R0=new ie,C0=new ie;class Mi extends Hv{constructor(t=50,i=1,r=.1,l=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=t,this.zoom=1,this.near=r,this.far=l,this.focus=10,this.aspect=i,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(t,i){return super.copy(t,i),this.fov=t.fov,this.zoom=t.zoom,this.near=t.near,this.far=t.far,this.focus=t.focus,this.aspect=t.aspect,this.view=t.view===null?null:Object.assign({},t.view),this.filmGauge=t.filmGauge,this.filmOffset=t.filmOffset,this}setFocalLength(t){const i=.5*this.getFilmHeight()/t;this.fov=Bd*2*Math.atan(i),this.updateProjectionMatrix()}getFocalLength(){const t=Math.tan(Yu*.5*this.fov);return .5*this.getFilmHeight()/t}getEffectiveFOV(){return Bd*2*Math.atan(Math.tan(Yu*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(t,i,r){or.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),i.set(or.x,or.y).multiplyScalar(-t/or.z),or.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),r.set(or.x,or.y).multiplyScalar(-t/or.z)}getViewSize(t,i){return this.getViewBounds(t,R0,C0),i.subVectors(C0,R0)}setViewOffset(t,i,r,l,u,f){this.aspect=t/i,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=i,this.view.offsetX=r,this.view.offsetY=l,this.view.width=u,this.view.height=f,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=this.near;let i=t*Math.tan(Yu*.5*this.fov)/this.zoom,r=2*i,l=this.aspect*r,u=-.5*l;const f=this.view;if(this.view!==null&&this.view.enabled){const m=f.fullWidth,d=f.fullHeight;u+=f.offsetX*l/m,i-=f.offsetY*r/d,l*=f.width/m,r*=f.height/d}const p=this.filmOffset;p!==0&&(u+=t*p/this.getFilmWidth()),this.projectionMatrix.makePerspective(u,u+l,i,i-r,t,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const i=super.toJSON(t);return i.object.fov=this.fov,i.object.zoom=this.zoom,i.object.near=this.near,i.object.far=this.far,i.object.focus=this.focus,i.object.aspect=this.aspect,this.view!==null&&(i.object.view=Object.assign({},this.view)),i.object.filmGauge=this.filmGauge,i.object.filmOffset=this.filmOffset,i}}class ip extends Hv{constructor(t=-1,i=1,r=1,l=-1,u=.1,f=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=t,this.right=i,this.top=r,this.bottom=l,this.near=u,this.far=f,this.updateProjectionMatrix()}copy(t,i){return super.copy(t,i),this.left=t.left,this.right=t.right,this.top=t.top,this.bottom=t.bottom,this.near=t.near,this.far=t.far,this.zoom=t.zoom,this.view=t.view===null?null:Object.assign({},t.view),this}setViewOffset(t,i,r,l,u,f){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=t,this.view.fullHeight=i,this.view.offsetX=r,this.view.offsetY=l,this.view.width=u,this.view.height=f,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const t=(this.right-this.left)/(2*this.zoom),i=(this.top-this.bottom)/(2*this.zoom),r=(this.right+this.left)/2,l=(this.top+this.bottom)/2;let u=r-t,f=r+t,p=l+i,m=l-i;if(this.view!==null&&this.view.enabled){const d=(this.right-this.left)/this.view.fullWidth/this.zoom,g=(this.top-this.bottom)/this.view.fullHeight/this.zoom;u+=d*this.view.offsetX,f=u+d*this.view.width,p-=g*this.view.offsetY,m=p-g*this.view.height}this.projectionMatrix.makeOrthographic(u,f,p,m,this.near,this.far,this.coordinateSystem,this.reversedDepth),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(t){const i=super.toJSON(t);return i.object.zoom=this.zoom,i.object.left=this.left,i.object.right=this.right,i.object.top=this.top,i.object.bottom=this.bottom,i.object.near=this.near,i.object.far=this.far,this.view!==null&&(i.object.view=Object.assign({},this.view)),i}}class NM extends LM{constructor(){super(new ip(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class OM extends Bv{constructor(t,i){super(t,i),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Un.DEFAULT_UP),this.updateMatrix(),this.target=new Un,this.shadow=new NM}dispose(){super.dispose(),this.shadow.dispose()}copy(t){return super.copy(t),this.target=t.target.clone(),this.shadow=t.shadow.clone(),this}toJSON(t){const i=super.toJSON(t);return i.object.shadow=this.shadow.toJSON(),i.object.target=this.target.uuid,i}}const zs=-90,Bs=1;class PM extends Un{constructor(t,i,r){super(),this.type="CubeCamera",this.renderTarget=r,this.coordinateSystem=null,this.activeMipmapLevel=0;const l=new Mi(zs,Bs,t,i);l.layers=this.layers,this.add(l);const u=new Mi(zs,Bs,t,i);u.layers=this.layers,this.add(u);const f=new Mi(zs,Bs,t,i);f.layers=this.layers,this.add(f);const p=new Mi(zs,Bs,t,i);p.layers=this.layers,this.add(p);const m=new Mi(zs,Bs,t,i);m.layers=this.layers,this.add(m);const d=new Mi(zs,Bs,t,i);d.layers=this.layers,this.add(d)}updateCoordinateSystem(){const t=this.coordinateSystem,i=this.children.concat(),[r,l,u,f,p,m]=i;for(const d of i)this.remove(d);if(t===qi)r.up.set(0,1,0),r.lookAt(1,0,0),l.up.set(0,1,0),l.lookAt(-1,0,0),u.up.set(0,0,-1),u.lookAt(0,1,0),f.up.set(0,0,1),f.lookAt(0,-1,0),p.up.set(0,1,0),p.lookAt(0,0,1),m.up.set(0,1,0),m.lookAt(0,0,-1);else if(t===rl)r.up.set(0,-1,0),r.lookAt(-1,0,0),l.up.set(0,-1,0),l.lookAt(1,0,0),u.up.set(0,0,1),u.lookAt(0,1,0),f.up.set(0,0,-1),f.lookAt(0,-1,0),p.up.set(0,-1,0),p.lookAt(0,0,1),m.up.set(0,-1,0),m.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+t);for(const d of i)this.add(d),d.updateMatrixWorld()}update(t,i){this.parent===null&&this.updateMatrixWorld();const{renderTarget:r,activeMipmapLevel:l}=this;this.coordinateSystem!==t.coordinateSystem&&(this.coordinateSystem=t.coordinateSystem,this.updateCoordinateSystem());const[u,f,p,m,d,g]=this.children,v=t.getRenderTarget(),_=t.getActiveCubeFace(),M=t.getActiveMipmapLevel(),T=t.xr.enabled;t.xr.enabled=!1;const w=r.texture.generateMipmaps;r.texture.generateMipmaps=!1;let E=!1;t.isWebGLRenderer===!0?E=t.state.buffers.depth.getReversed():E=t.reversedDepthBuffer,t.setRenderTarget(r,0,l),E&&t.autoClear===!1&&t.clearDepth(),t.render(i,u),t.setRenderTarget(r,1,l),E&&t.autoClear===!1&&t.clearDepth(),t.render(i,f),t.setRenderTarget(r,2,l),E&&t.autoClear===!1&&t.clearDepth(),t.render(i,p),t.setRenderTarget(r,3,l),E&&t.autoClear===!1&&t.clearDepth(),t.render(i,m),t.setRenderTarget(r,4,l),E&&t.autoClear===!1&&t.clearDepth(),t.render(i,d),r.texture.generateMipmaps=w,t.setRenderTarget(r,5,l),E&&t.autoClear===!1&&t.clearDepth(),t.render(i,g),t.setRenderTarget(v,_,M),t.xr.enabled=T,r.texture.needsPMREMUpdate=!0}}class IM extends Mi{constructor(t=[]){super(),this.isArrayCamera=!0,this.isMultiViewCamera=!1,this.cameras=t}}class w0{constructor(t=1,i=0,r=0){this.radius=t,this.phi=i,this.theta=r}set(t,i,r){return this.radius=t,this.phi=i,this.theta=r,this}copy(t){return this.radius=t.radius,this.phi=t.phi,this.theta=t.theta,this}makeSafe(){return this.phi=me(this.phi,1e-6,Math.PI-1e-6),this}setFromVector3(t){return this.setFromCartesianCoords(t.x,t.y,t.z)}setFromCartesianCoords(t,i,r){return this.radius=Math.sqrt(t*t+i*i+r*r),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(t,r),this.phi=Math.acos(me(i/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}const cp=class cp{constructor(t,i,r,l){this.elements=[1,0,0,1],t!==void 0&&this.set(t,i,r,l)}identity(){return this.set(1,0,0,1),this}fromArray(t,i=0){for(let r=0;r<4;r++)this.elements[r]=t[r+i];return this}set(t,i,r,l){const u=this.elements;return u[0]=t,u[2]=i,u[1]=r,u[3]=l,this}};cp.prototype.isMatrix2=!0;let D0=cp;class FM extends pr{constructor(t,i=null){super(),this.object=t,this.domElement=i,this.enabled=!0,this.state=-1,this.keys={},this.mouseButtons={LEFT:null,MIDDLE:null,RIGHT:null},this.touches={ONE:null,TWO:null}}connect(t){if(t===void 0){te("Controls: connect() now requires an element.");return}this.domElement!==null&&this.disconnect(),this.domElement=t}disconnect(){}dispose(){}update(){}}function U0(s,t,i,r){const l=zM(r);switch(i){case Tv:return s*t;case Rv:return s*t/l.components*l.byteLength;case Zd:return s*t/l.components*l.byteLength;case Zr:return s*t*2/l.components*l.byteLength;case Kd:return s*t*2/l.components*l.byteLength;case Av:return s*t*3/l.components*l.byteLength;case Ni:return s*t*4/l.components*l.byteLength;case Qd:return s*t*4/l.components*l.byteLength;case ku:case Xu:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*8;case Wu:case qu:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*16;case cd:case hd:return Math.max(s,16)*Math.max(t,8)/4;case ud:case fd:return Math.max(s,8)*Math.max(t,8)/2;case dd:case pd:case gd:case _d:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*8;case md:case Ku:case vd:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*16;case xd:return Math.floor((s+3)/4)*Math.floor((t+3)/4)*16;case Sd:return Math.floor((s+4)/5)*Math.floor((t+3)/4)*16;case yd:return Math.floor((s+4)/5)*Math.floor((t+4)/5)*16;case Md:return Math.floor((s+5)/6)*Math.floor((t+4)/5)*16;case Ed:return Math.floor((s+5)/6)*Math.floor((t+5)/6)*16;case bd:return Math.floor((s+7)/8)*Math.floor((t+4)/5)*16;case Td:return Math.floor((s+7)/8)*Math.floor((t+5)/6)*16;case Ad:return Math.floor((s+7)/8)*Math.floor((t+7)/8)*16;case Rd:return Math.floor((s+9)/10)*Math.floor((t+4)/5)*16;case Cd:return Math.floor((s+9)/10)*Math.floor((t+5)/6)*16;case wd:return Math.floor((s+9)/10)*Math.floor((t+7)/8)*16;case Dd:return Math.floor((s+9)/10)*Math.floor((t+9)/10)*16;case Ud:return Math.floor((s+11)/12)*Math.floor((t+9)/10)*16;case Ld:return Math.floor((s+11)/12)*Math.floor((t+11)/12)*16;case Nd:case Od:case Pd:return Math.ceil(s/4)*Math.ceil(t/4)*16;case Id:case Fd:return Math.ceil(s/4)*Math.ceil(t/4)*8;case Qu:case zd:return Math.ceil(s/4)*Math.ceil(t/4)*16}throw new Error(`Unable to determine texture byte length for ${i} format.`)}function zM(s){switch(s){case fi:case yv:return{byteLength:1,components:1};case il:case Mv:case Ra:return{byteLength:2,components:1};case qd:case Yd:return{byteLength:2,components:4};case Ki:case Wd:case Wi:return{byteLength:4,components:1};case Ev:case bv:return{byteLength:4,components:3}}throw new Error(`THREE.TextureUtils: Unknown texture type ${s}.`)}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Xd}}));typeof window<"u"&&(window.__THREE__?te("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Xd);function Gv(){let s=null,t=!1,i=null,r=null;function l(u,f){i(u,f),r=s.requestAnimationFrame(l)}return{start:function(){t!==!0&&i!==null&&s!==null&&(r=s.requestAnimationFrame(l),t=!0)},stop:function(){s!==null&&s.cancelAnimationFrame(r),t=!1},setAnimationLoop:function(u){i=u},setContext:function(u){s=u}}}function BM(s){const t=new WeakMap;function i(p,m){const d=p.array,g=p.usage,v=d.byteLength,_=s.createBuffer();s.bindBuffer(m,_),s.bufferData(m,d,g),p.onUploadCallback();let M;if(d instanceof Float32Array)M=s.FLOAT;else if(typeof Float16Array<"u"&&d instanceof Float16Array)M=s.HALF_FLOAT;else if(d instanceof Uint16Array)p.isFloat16BufferAttribute?M=s.HALF_FLOAT:M=s.UNSIGNED_SHORT;else if(d instanceof Int16Array)M=s.SHORT;else if(d instanceof Uint32Array)M=s.UNSIGNED_INT;else if(d instanceof Int32Array)M=s.INT;else if(d instanceof Int8Array)M=s.BYTE;else if(d instanceof Uint8Array)M=s.UNSIGNED_BYTE;else if(d instanceof Uint8ClampedArray)M=s.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+d);return{buffer:_,type:M,bytesPerElement:d.BYTES_PER_ELEMENT,version:p.version,size:v}}function r(p,m,d){const g=m.array,v=m.updateRanges;if(s.bindBuffer(d,p),v.length===0)s.bufferSubData(d,0,g);else{v.sort((M,T)=>M.start-T.start);let _=0;for(let M=1;M<v.length;M++){const T=v[_],w=v[M];w.start<=T.start+T.count+1?T.count=Math.max(T.count,w.start+w.count-T.start):(++_,v[_]=w)}v.length=_+1;for(let M=0,T=v.length;M<T;M++){const w=v[M];s.bufferSubData(d,w.start*g.BYTES_PER_ELEMENT,g,w.start,w.count)}m.clearUpdateRanges()}m.onUploadCallback()}function l(p){return p.isInterleavedBufferAttribute&&(p=p.data),t.get(p)}function u(p){p.isInterleavedBufferAttribute&&(p=p.data);const m=t.get(p);m&&(s.deleteBuffer(m.buffer),t.delete(p))}function f(p,m){if(p.isInterleavedBufferAttribute&&(p=p.data),p.isGLBufferAttribute){const g=t.get(p);(!g||g.version<p.version)&&t.set(p,{buffer:p.buffer,type:p.type,bytesPerElement:p.elementSize,version:p.version});return}const d=t.get(p);if(d===void 0)t.set(p,i(p,m));else if(d.version<p.version){if(d.size!==p.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");r(d.buffer,p,m),d.version=p.version}}return{get:l,remove:u,update:f}}var HM=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,GM=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,VM=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,kM=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,XM=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,WM=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,qM=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,YM=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,ZM=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec4 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 );
	}
#endif`,KM=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,QM=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,JM=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,jM=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,$M=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,tE=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,eE=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,nE=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,iE=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,aE=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,rE=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#endif`,sE=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#endif`,oE=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec4 vColor;
#endif`,lE=`#if defined( USE_COLOR ) || defined( USE_COLOR_ALPHA ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec4( 1.0 );
#endif
#ifdef USE_COLOR_ALPHA
	vColor *= color;
#elif defined( USE_COLOR )
	vColor.rgb *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.rgb *= instanceColor.rgb;
#endif
#ifdef USE_BATCHING_COLOR
	vColor *= getBatchingColor( getIndirectIndex( gl_DrawID ) );
#endif`,uE=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
#define inverseTransformDirection transformDirectionByInverseViewMatrix
vec3 transformNormalByInverseViewMatrix( in vec3 normal, in mat4 viewMatrix ) {
	return normalize( ( vec4( normal, 0.0 ) * viewMatrix ).xyz );
}
vec3 transformDirectionByInverseViewMatrix( in vec3 dir, in mat4 viewMatrix ) {
	return normalize( ( vec4( dir, 0.0 ) * viewMatrix ).xyz );
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,cE=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,fE=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
#endif`,hE=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,dE=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,pE=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,mE=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,gE="gl_FragColor = linearToOutputTexel( gl_FragColor );",_E=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,vE=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * reflectVec );
		#ifdef ENVMAP_BLENDING_MULTIPLY
			outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_MIX )
			outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
		#elif defined( ENVMAP_BLENDING_ADD )
			outgoingLight += envColor.xyz * specularStrength * reflectivity;
		#endif
	#endif
#endif`,xE=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
#endif`,SE=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,yE=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,ME=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = transformNormalByInverseViewMatrix( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,EE=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,bE=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,TE=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,AE=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,RE=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,CE=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,wE=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,DE=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,UE=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif
#include <lightprobes_pars_fragment>`,LE=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = transformNormalByInverseViewMatrix( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, pow4( roughness ) ) );
			reflectVec = transformDirectionByInverseViewMatrix( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,NE=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,OE=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,PE=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,IE=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,FE=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.diffuseContribution = diffuseColor.rgb * ( 1.0 - metalnessFactor );
material.metalness = metalnessFactor;
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor;
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = vec3( 0.04 );
	material.specularColorBlended = mix( material.specularColor, diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.0001, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,zE=`uniform sampler2D dfgLUT;
struct PhysicalMaterial {
	vec3 diffuseColor;
	vec3 diffuseContribution;
	vec3 specularColor;
	vec3 specularColorBlended;
	float roughness;
	float metalness;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
		vec3 iridescenceFresnelDielectric;
		vec3 iridescenceFresnelMetallic;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		return 0.5 / max( gv + gl, EPSILON );
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColorBlended;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transpose( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float rInv = 1.0 / ( roughness + 0.1 );
	float a = -1.9362 + 1.0678 * roughness + 0.4573 * r2 - 0.8469 * rInv;
	float b = -0.6014 + 0.5538 * roughness - 0.4670 * r2 - 0.1255 * rInv;
	float DG = exp( a * dotNV + b );
	return saturate( DG );
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 fab = texture2D( dfgLUT, vec2( roughness, dotNV ) ).rg;
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
vec3 BRDF_GGX_Multiscatter( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 singleScatter = BRDF_GGX( lightDir, viewDir, normal, material );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	vec2 dfgV = texture2D( dfgLUT, vec2( material.roughness, dotNV ) ).rg;
	vec2 dfgL = texture2D( dfgLUT, vec2( material.roughness, dotNL ) ).rg;
	vec3 FssEss_V = material.specularColorBlended * dfgV.x + material.specularF90 * dfgV.y;
	vec3 FssEss_L = material.specularColorBlended * dfgL.x + material.specularF90 * dfgL.y;
	float Ess_V = dfgV.x + dfgV.y;
	float Ess_L = dfgL.x + dfgL.y;
	float Ems_V = 1.0 - Ess_V;
	float Ems_L = 1.0 - Ess_L;
	vec3 Favg = material.specularColorBlended + ( 1.0 - material.specularColorBlended ) * 0.047619;
	vec3 Fms = FssEss_V * FssEss_L * Favg / ( 1.0 - Ems_V * Ems_L * Favg + EPSILON );
	float compensationFactor = Ems_V * Ems_L;
	vec3 multiScatter = Fms * compensationFactor;
	return singleScatter + multiScatter;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColorBlended * t2.x + ( material.specularF90 - material.specularColorBlended ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseContribution * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
		#ifdef USE_CLEARCOAT
			vec3 Ncc = geometryClearcoatNormal;
			vec2 uvClearcoat = LTC_Uv( Ncc, viewDir, material.clearcoatRoughness );
			vec4 t1Clearcoat = texture2D( ltc_1, uvClearcoat );
			vec4 t2Clearcoat = texture2D( ltc_2, uvClearcoat );
			mat3 mInvClearcoat = mat3(
				vec3( t1Clearcoat.x, 0, t1Clearcoat.y ),
				vec3(             0, 1,             0 ),
				vec3( t1Clearcoat.z, 0, t1Clearcoat.w )
			);
			vec3 fresnelClearcoat = material.clearcoatF0 * t2Clearcoat.x + ( material.clearcoatF90 - material.clearcoatF0 ) * t2Clearcoat.y;
			clearcoatSpecularDirect += lightColor * fresnelClearcoat * LTC_Evaluate( Ncc, viewDir, position, mInvClearcoat, rectCoords );
		#endif
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
 
 		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
 
 		float sheenAlbedoV = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
 		float sheenAlbedoL = IBLSheenBRDF( geometryNormal, directLight.direction, material.sheenRoughness );
 
 		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * max( sheenAlbedoV, sheenAlbedoL );
 
 		irradiance *= sheenEnergyComp;
 
 	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX_Multiscatter( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseContribution );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 diffuse = irradiance * BRDF_Lambert( material.diffuseContribution );
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		diffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectDiffuse += diffuse;
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness ) * RECIPROCAL_PI;
 	#endif
	vec3 singleScatteringDielectric = vec3( 0.0 );
	vec3 multiScatteringDielectric = vec3( 0.0 );
	vec3 singleScatteringMetallic = vec3( 0.0 );
	vec3 multiScatteringMetallic = vec3( 0.0 );
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnelDielectric, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.iridescence, material.iridescenceFresnelMetallic, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScatteringDielectric, multiScatteringDielectric );
		computeMultiscattering( geometryNormal, geometryViewDir, material.diffuseColor, material.specularF90, material.roughness, singleScatteringMetallic, multiScatteringMetallic );
	#endif
	vec3 singleScattering = mix( singleScatteringDielectric, singleScatteringMetallic, material.metalness );
	vec3 multiScattering = mix( multiScatteringDielectric, multiScatteringMetallic, material.metalness );
	vec3 totalScatteringDielectric = singleScatteringDielectric + multiScatteringDielectric;
	vec3 diffuse = material.diffuseContribution * ( 1.0 - totalScatteringDielectric );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	vec3 indirectSpecular = radiance * singleScattering;
	indirectSpecular += multiScattering * cosineWeightedIrradiance;
	vec3 indirectDiffuse = diffuse * cosineWeightedIrradiance;
	#ifdef USE_SHEEN
		float sheenAlbedo = IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
		float sheenEnergyComp = 1.0 - max3( material.sheenColor ) * sheenAlbedo;
		indirectSpecular *= sheenEnergyComp;
		indirectDiffuse *= sheenEnergyComp;
	#endif
	reflectedLight.indirectSpecular += indirectSpecular;
	reflectedLight.indirectDiffuse += indirectDiffuse;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,BE=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnelDielectric = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceFresnelMetallic = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.diffuseColor );
		material.iridescenceFresnel = mix( material.iridescenceFresnelDielectric, material.iridescenceFresnelMetallic, material.metalness );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS ) && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
	#ifdef USE_LIGHT_PROBES_GRID
		vec3 probeWorldPos = ( ( vec4( geometryPosition, 1.0 ) - viewMatrix[ 3 ] ) * viewMatrix ).xyz;
		vec3 probeWorldNormal = transformNormalByInverseViewMatrix( geometryNormal, viewMatrix );
		irradiance += getLightProbeGridIrradiance( probeWorldPos, probeWorldNormal );
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,HE=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( ENVMAP_TYPE_CUBE_UV )
		#if defined( STANDARD ) || defined( LAMBERT ) || defined( PHONG )
			iblIrradiance += getIBLIrradiance( geometryNormal );
		#endif
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,GE=`#if defined( RE_IndirectDiffuse )
	#if defined( LAMBERT ) || defined( PHONG )
		irradiance += iblIrradiance;
	#endif
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,VE=`#ifdef USE_LIGHT_PROBES_GRID
uniform highp sampler3D probesSH;
uniform vec3 probesMin;
uniform vec3 probesMax;
uniform vec3 probesResolution;
vec3 getLightProbeGridIrradiance( vec3 worldPos, vec3 worldNormal ) {
	vec3 res = probesResolution;
	vec3 gridRange = probesMax - probesMin;
	vec3 resMinusOne = res - 1.0;
	vec3 probeSpacing = gridRange / resMinusOne;
	vec3 samplePos = worldPos + worldNormal * probeSpacing * 0.5;
	vec3 uvw = clamp( ( samplePos - probesMin ) / gridRange, 0.0, 1.0 );
	uvw = uvw * resMinusOne / res + 0.5 / res;
	float nz          = res.z;
	float paddedSlices = nz + 2.0;
	float atlasDepth  = 7.0 * paddedSlices;
	float uvZBase     = uvw.z * nz + 1.0;
	vec4 s0 = texture( probesSH, vec3( uvw.xy, ( uvZBase                       ) / atlasDepth ) );
	vec4 s1 = texture( probesSH, vec3( uvw.xy, ( uvZBase +       paddedSlices   ) / atlasDepth ) );
	vec4 s2 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 2.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s3 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 3.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s4 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 4.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s5 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 5.0 * paddedSlices   ) / atlasDepth ) );
	vec4 s6 = texture( probesSH, vec3( uvw.xy, ( uvZBase + 6.0 * paddedSlices   ) / atlasDepth ) );
	vec3 c0 = s0.xyz;
	vec3 c1 = vec3( s0.w, s1.xy );
	vec3 c2 = vec3( s1.zw, s2.x );
	vec3 c3 = s2.yzw;
	vec3 c4 = s3.xyz;
	vec3 c5 = vec3( s3.w, s4.xy );
	vec3 c6 = vec3( s4.zw, s5.x );
	vec3 c7 = s5.yzw;
	vec3 c8 = s6.xyz;
	float x = worldNormal.x, y = worldNormal.y, z = worldNormal.z;
	vec3 result = c0 * 0.886227;
	result += c1 * 2.0 * 0.511664 * y;
	result += c2 * 2.0 * 0.511664 * z;
	result += c3 * 2.0 * 0.511664 * x;
	result += c4 * 2.0 * 0.429043 * x * y;
	result += c5 * 2.0 * 0.429043 * y * z;
	result += c6 * ( 0.743125 * z * z - 0.247708 );
	result += c7 * 2.0 * 0.429043 * x * z;
	result += c8 * 0.429043 * ( x * x - y * y );
	return max( result, vec3( 0.0 ) );
}
#endif`,kE=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,XE=`#if defined( USE_LOGARITHMIC_DEPTH_BUFFER )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,WE=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,qE=`#ifdef USE_LOGARITHMIC_DEPTH_BUFFER
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,YE=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,ZE=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,KE=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,QE=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,JE=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,jE=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,$E=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,tb=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,eb=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,nb=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,ib=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,ab=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#ifdef DOUBLE_SIDED
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#ifdef DOUBLE_SIDED
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,rb=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#if defined( USE_PACKED_NORMALMAP )
		mapN = vec3( mapN.xy, sqrt( saturate( 1.0 - dot( mapN.xy, mapN.xy ) ) ) );
	#endif
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,sb=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,ob=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,lb=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
		#ifdef FLIP_SIDED
			vBitangent = - vBitangent;
		#endif
	#endif
#endif`,ub=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,cb=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,fb=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,hb=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,db=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,pb=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,mb=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	#ifdef USE_REVERSED_DEPTH_BUFFER
	
		return depth * ( far - near ) - far;
	#else
		return depth * ( near - far ) - near;
	#endif
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	
	#ifdef USE_REVERSED_DEPTH_BUFFER
		return ( near * far ) / ( ( near - far ) * depth - near );
	#else
		return ( near * far ) / ( ( far - near ) * depth - far );
	#endif
}`,gb=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,_b=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,vb=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,xb=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,Sb=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,yb=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,Mb=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#else
			uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		#endif
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform sampler2DShadow spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#else
			uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		#endif
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#if defined( SHADOWMAP_TYPE_PCF )
			uniform samplerCubeShadow pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#elif defined( SHADOWMAP_TYPE_BASIC )
			uniform samplerCube pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		#endif
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float interleavedGradientNoise( vec2 position ) {
			return fract( 52.9829189 * fract( dot( position, vec2( 0.06711056, 0.00583715 ) ) ) );
		}
		vec2 vogelDiskSample( int sampleIndex, int samplesCount, float phi ) {
			const float goldenAngle = 2.399963229728653;
			float r = sqrt( ( float( sampleIndex ) + 0.5 ) / float( samplesCount ) );
			float theta = float( sampleIndex ) * goldenAngle + phi;
			return vec2( cos( theta ), sin( theta ) ) * r;
		}
	#endif
	#if defined( SHADOWMAP_TYPE_PCF )
		float getShadow( sampler2DShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			shadowCoord.z += shadowBias;
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
				float radius = shadowRadius * texelSize.x;
				float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
				shadow = (
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 0, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 1, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 2, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 3, 5, phi ) * radius, shadowCoord.z ) ) +
					texture( shadowMap, vec3( shadowCoord.xy + vogelDiskSample( 4, 5, phi ) * radius, shadowCoord.z ) )
				) * 0.2;
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#elif defined( SHADOWMAP_TYPE_VSM )
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				vec2 distribution = texture2D( shadowMap, shadowCoord.xy ).rg;
				float mean = distribution.x;
				float variance = distribution.y * distribution.y;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					float hard_shadow = step( mean, shadowCoord.z );
				#else
					float hard_shadow = step( shadowCoord.z, mean );
				#endif
				
				if ( hard_shadow == 1.0 ) {
					shadow = 1.0;
				} else {
					variance = max( variance, 0.0000001 );
					float d = shadowCoord.z - mean;
					float p_max = variance / ( variance + d * d );
					p_max = clamp( ( p_max - 0.3 ) / 0.65, 0.0, 1.0 );
					shadow = max( hard_shadow, p_max );
				}
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#else
		float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
			float shadow = 1.0;
			shadowCoord.xyz /= shadowCoord.w;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				shadowCoord.z -= shadowBias;
			#else
				shadowCoord.z += shadowBias;
			#endif
			bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
			bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
			if ( frustumTest ) {
				float depth = texture2D( shadowMap, shadowCoord.xy ).r;
				#ifdef USE_REVERSED_DEPTH_BUFFER
					shadow = step( depth, shadowCoord.z );
				#else
					shadow = step( shadowCoord.z, depth );
				#endif
			}
			return mix( 1.0, shadow, shadowIntensity );
		}
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	#if defined( SHADOWMAP_TYPE_PCF )
	float getPointShadow( samplerCubeShadow shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 bd3D = normalize( lightToPosition );
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			#ifdef USE_REVERSED_DEPTH_BUFFER
				float dp = ( shadowCameraNear * ( shadowCameraFar - viewSpaceZ ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp -= shadowBias;
			#else
				float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
				dp += shadowBias;
			#endif
			float texelSize = shadowRadius / shadowMapSize.x;
			vec3 absDir = abs( bd3D );
			vec3 tangent = absDir.x > absDir.z ? vec3( 0.0, 1.0, 0.0 ) : vec3( 1.0, 0.0, 0.0 );
			tangent = normalize( cross( bd3D, tangent ) );
			vec3 bitangent = cross( bd3D, tangent );
			float phi = interleavedGradientNoise( gl_FragCoord.xy ) * PI2;
			vec2 sample0 = vogelDiskSample( 0, 5, phi );
			vec2 sample1 = vogelDiskSample( 1, 5, phi );
			vec2 sample2 = vogelDiskSample( 2, 5, phi );
			vec2 sample3 = vogelDiskSample( 3, 5, phi );
			vec2 sample4 = vogelDiskSample( 4, 5, phi );
			shadow = (
				texture( shadowMap, vec4( bd3D + ( tangent * sample0.x + bitangent * sample0.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample1.x + bitangent * sample1.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample2.x + bitangent * sample2.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample3.x + bitangent * sample3.y ) * texelSize, dp ) ) +
				texture( shadowMap, vec4( bd3D + ( tangent * sample4.x + bitangent * sample4.y ) * texelSize, dp ) )
			) * 0.2;
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#elif defined( SHADOWMAP_TYPE_BASIC )
	float getPointShadow( samplerCube shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		vec3 absVec = abs( lightToPosition );
		float viewSpaceZ = max( max( absVec.x, absVec.y ), absVec.z );
		if ( viewSpaceZ - shadowCameraFar <= 0.0 && viewSpaceZ - shadowCameraNear >= 0.0 ) {
			float dp = ( shadowCameraFar * ( viewSpaceZ - shadowCameraNear ) ) / ( viewSpaceZ * ( shadowCameraFar - shadowCameraNear ) );
			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			float depth = textureCube( shadowMap, bd3D ).r;
			#ifdef USE_REVERSED_DEPTH_BUFFER
				depth = 1.0 - depth;
			#endif
			shadow = step( dp, depth );
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	#endif
	#endif
#endif`,Eb=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,bb=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	#ifdef HAS_NORMAL
		vec3 shadowWorldNormal = transformNormalByInverseViewMatrix( transformedNormal, viewMatrix );
	#else
		vec3 shadowWorldNormal = vec3( 0.0 );
	#endif
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,Tb=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0 && ( defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_BASIC ) )
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,Ab=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,Rb=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,Cb=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,wb=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,Db=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,Ub=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,Lb=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,Nb=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,Ob=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = transformNormalByInverseViewMatrix( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseContribution, material.specularColorBlended, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,Pb=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		#else
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,Ib=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,Fb=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,zb=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,Bb=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const Hb=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,Gb=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Vb=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,kb=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vWorldDirection );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Xb=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Wb=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,qb=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,Yb=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	#ifdef USE_REVERSED_DEPTH_BUFFER
		float fragCoordZ = vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ];
	#else
		float fragCoordZ = 0.5 * vHighPrecisionZW[ 0 ] / vHighPrecisionZW[ 1 ] + 0.5;
	#endif
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,Zb=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,Kb=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = vec4( dist, 0.0, 0.0, 1.0 );
}`,Qb=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,Jb=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,jb=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,$b=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,tT=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,eT=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,nT=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,iT=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,aT=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,rT=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,sT=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,oT=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( normalize( normal ) * 0.5 + 0.5, diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,lT=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,uT=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,cT=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,fT=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
 
		outgoingLight = outgoingLight + sheenSpecularDirect + sheenSpecularIndirect;
 
 	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,hT=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,dT=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,pT=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,mT=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,gT=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,_T=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,vT=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,xT=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,ue={alphahash_fragment:HM,alphahash_pars_fragment:GM,alphamap_fragment:VM,alphamap_pars_fragment:kM,alphatest_fragment:XM,alphatest_pars_fragment:WM,aomap_fragment:qM,aomap_pars_fragment:YM,batching_pars_vertex:ZM,batching_vertex:KM,begin_vertex:QM,beginnormal_vertex:JM,bsdfs:jM,iridescence_fragment:$M,bumpmap_pars_fragment:tE,clipping_planes_fragment:eE,clipping_planes_pars_fragment:nE,clipping_planes_pars_vertex:iE,clipping_planes_vertex:aE,color_fragment:rE,color_pars_fragment:sE,color_pars_vertex:oE,color_vertex:lE,common:uE,cube_uv_reflection_fragment:cE,defaultnormal_vertex:fE,displacementmap_pars_vertex:hE,displacementmap_vertex:dE,emissivemap_fragment:pE,emissivemap_pars_fragment:mE,colorspace_fragment:gE,colorspace_pars_fragment:_E,envmap_fragment:vE,envmap_common_pars_fragment:xE,envmap_pars_fragment:SE,envmap_pars_vertex:yE,envmap_physical_pars_fragment:LE,envmap_vertex:ME,fog_vertex:EE,fog_pars_vertex:bE,fog_fragment:TE,fog_pars_fragment:AE,gradientmap_pars_fragment:RE,lightmap_pars_fragment:CE,lights_lambert_fragment:wE,lights_lambert_pars_fragment:DE,lights_pars_begin:UE,lights_toon_fragment:NE,lights_toon_pars_fragment:OE,lights_phong_fragment:PE,lights_phong_pars_fragment:IE,lights_physical_fragment:FE,lights_physical_pars_fragment:zE,lights_fragment_begin:BE,lights_fragment_maps:HE,lights_fragment_end:GE,lightprobes_pars_fragment:VE,logdepthbuf_fragment:kE,logdepthbuf_pars_fragment:XE,logdepthbuf_pars_vertex:WE,logdepthbuf_vertex:qE,map_fragment:YE,map_pars_fragment:ZE,map_particle_fragment:KE,map_particle_pars_fragment:QE,metalnessmap_fragment:JE,metalnessmap_pars_fragment:jE,morphinstance_vertex:$E,morphcolor_vertex:tb,morphnormal_vertex:eb,morphtarget_pars_vertex:nb,morphtarget_vertex:ib,normal_fragment_begin:ab,normal_fragment_maps:rb,normal_pars_fragment:sb,normal_pars_vertex:ob,normal_vertex:lb,normalmap_pars_fragment:ub,clearcoat_normal_fragment_begin:cb,clearcoat_normal_fragment_maps:fb,clearcoat_pars_fragment:hb,iridescence_pars_fragment:db,opaque_fragment:pb,packing:mb,premultiplied_alpha_fragment:gb,project_vertex:_b,dithering_fragment:vb,dithering_pars_fragment:xb,roughnessmap_fragment:Sb,roughnessmap_pars_fragment:yb,shadowmap_pars_fragment:Mb,shadowmap_pars_vertex:Eb,shadowmap_vertex:bb,shadowmask_pars_fragment:Tb,skinbase_vertex:Ab,skinning_pars_vertex:Rb,skinning_vertex:Cb,skinnormal_vertex:wb,specularmap_fragment:Db,specularmap_pars_fragment:Ub,tonemapping_fragment:Lb,tonemapping_pars_fragment:Nb,transmission_fragment:Ob,transmission_pars_fragment:Pb,uv_pars_fragment:Ib,uv_pars_vertex:Fb,uv_vertex:zb,worldpos_vertex:Bb,background_vert:Hb,background_frag:Gb,backgroundCube_vert:Vb,backgroundCube_frag:kb,cube_vert:Xb,cube_frag:Wb,depth_vert:qb,depth_frag:Yb,distance_vert:Zb,distance_frag:Kb,equirect_vert:Qb,equirect_frag:Jb,linedashed_vert:jb,linedashed_frag:$b,meshbasic_vert:tT,meshbasic_frag:eT,meshlambert_vert:nT,meshlambert_frag:iT,meshmatcap_vert:aT,meshmatcap_frag:rT,meshnormal_vert:sT,meshnormal_frag:oT,meshphong_vert:lT,meshphong_frag:uT,meshphysical_vert:cT,meshphysical_frag:fT,meshtoon_vert:hT,meshtoon_frag:dT,points_vert:pT,points_frag:mT,shadow_vert:gT,shadow_frag:_T,sprite_vert:vT,sprite_frag:xT},Ot={common:{diffuse:{value:new xe(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new re},alphaMap:{value:null},alphaMapTransform:{value:new re},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new re}},envmap:{envMap:{value:null},envMapRotation:{value:new re},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98},dfgLUT:{value:null}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new re}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new re}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new re},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new re},normalScale:{value:new ie(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new re},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new re}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new re}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new re}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new xe(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null},probesSH:{value:null},probesMin:{value:new $},probesMax:{value:new $},probesResolution:{value:new $}},points:{diffuse:{value:new xe(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new re},alphaTest:{value:0},uvTransform:{value:new re}},sprite:{diffuse:{value:new xe(16777215)},opacity:{value:1},center:{value:new ie(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new re},alphaMap:{value:null},alphaMapTransform:{value:new re},alphaTest:{value:0}}},Xi={basic:{uniforms:zn([Ot.common,Ot.specularmap,Ot.envmap,Ot.aomap,Ot.lightmap,Ot.fog]),vertexShader:ue.meshbasic_vert,fragmentShader:ue.meshbasic_frag},lambert:{uniforms:zn([Ot.common,Ot.specularmap,Ot.envmap,Ot.aomap,Ot.lightmap,Ot.emissivemap,Ot.bumpmap,Ot.normalmap,Ot.displacementmap,Ot.fog,Ot.lights,{emissive:{value:new xe(0)},envMapIntensity:{value:1}}]),vertexShader:ue.meshlambert_vert,fragmentShader:ue.meshlambert_frag},phong:{uniforms:zn([Ot.common,Ot.specularmap,Ot.envmap,Ot.aomap,Ot.lightmap,Ot.emissivemap,Ot.bumpmap,Ot.normalmap,Ot.displacementmap,Ot.fog,Ot.lights,{emissive:{value:new xe(0)},specular:{value:new xe(1118481)},shininess:{value:30},envMapIntensity:{value:1}}]),vertexShader:ue.meshphong_vert,fragmentShader:ue.meshphong_frag},standard:{uniforms:zn([Ot.common,Ot.envmap,Ot.aomap,Ot.lightmap,Ot.emissivemap,Ot.bumpmap,Ot.normalmap,Ot.displacementmap,Ot.roughnessmap,Ot.metalnessmap,Ot.fog,Ot.lights,{emissive:{value:new xe(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:ue.meshphysical_vert,fragmentShader:ue.meshphysical_frag},toon:{uniforms:zn([Ot.common,Ot.aomap,Ot.lightmap,Ot.emissivemap,Ot.bumpmap,Ot.normalmap,Ot.displacementmap,Ot.gradientmap,Ot.fog,Ot.lights,{emissive:{value:new xe(0)}}]),vertexShader:ue.meshtoon_vert,fragmentShader:ue.meshtoon_frag},matcap:{uniforms:zn([Ot.common,Ot.bumpmap,Ot.normalmap,Ot.displacementmap,Ot.fog,{matcap:{value:null}}]),vertexShader:ue.meshmatcap_vert,fragmentShader:ue.meshmatcap_frag},points:{uniforms:zn([Ot.points,Ot.fog]),vertexShader:ue.points_vert,fragmentShader:ue.points_frag},dashed:{uniforms:zn([Ot.common,Ot.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:ue.linedashed_vert,fragmentShader:ue.linedashed_frag},depth:{uniforms:zn([Ot.common,Ot.displacementmap]),vertexShader:ue.depth_vert,fragmentShader:ue.depth_frag},normal:{uniforms:zn([Ot.common,Ot.bumpmap,Ot.normalmap,Ot.displacementmap,{opacity:{value:1}}]),vertexShader:ue.meshnormal_vert,fragmentShader:ue.meshnormal_frag},sprite:{uniforms:zn([Ot.sprite,Ot.fog]),vertexShader:ue.sprite_vert,fragmentShader:ue.sprite_frag},background:{uniforms:{uvTransform:{value:new re},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:ue.background_vert,fragmentShader:ue.background_frag},backgroundCube:{uniforms:{envMap:{value:null},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new re}},vertexShader:ue.backgroundCube_vert,fragmentShader:ue.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:ue.cube_vert,fragmentShader:ue.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:ue.equirect_vert,fragmentShader:ue.equirect_frag},distance:{uniforms:zn([Ot.common,Ot.displacementmap,{referencePosition:{value:new $},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:ue.distance_vert,fragmentShader:ue.distance_frag},shadow:{uniforms:zn([Ot.lights,Ot.fog,{color:{value:new xe(0)},opacity:{value:1}}]),vertexShader:ue.shadow_vert,fragmentShader:ue.shadow_frag}};Xi.physical={uniforms:zn([Xi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new re},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new re},clearcoatNormalScale:{value:new ie(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new re},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new re},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new re},sheen:{value:0},sheenColor:{value:new xe(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new re},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new re},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new re},transmissionSamplerSize:{value:new ie},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new re},attenuationDistance:{value:0},attenuationColor:{value:new xe(0)},specularColor:{value:new xe(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new re},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new re},anisotropyVector:{value:new ie},anisotropyMap:{value:null},anisotropyMapTransform:{value:new re}}]),vertexShader:ue.meshphysical_vert,fragmentShader:ue.meshphysical_frag};const Bu={r:0,b:0,g:0},ST=new $e,Vv=new re;Vv.set(-1,0,0,0,1,0,0,0,1);function yT(s,t,i,r,l,u){const f=new xe(0);let p=l===!0?0:1,m,d,g=null,v=0,_=null;function M(F){let z=F.isScene===!0?F.background:null;if(z&&z.isTexture){const C=F.backgroundBlurriness>0;z=t.get(z,C)}return z}function T(F){let z=!1;const C=M(F);C===null?E(f,p):C&&C.isColor&&(E(C,1),z=!0);const N=s.xr.getEnvironmentBlendMode();N==="additive"?i.buffers.color.setClear(0,0,0,1,u):N==="alpha-blend"&&i.buffers.color.setClear(0,0,0,0,u),(s.autoClear||z)&&(i.buffers.depth.setTest(!0),i.buffers.depth.setMask(!0),i.buffers.color.setMask(!0),s.clear(s.autoClearColor,s.autoClearDepth,s.autoClearStencil))}function w(F,z){const C=M(z);C&&(C.isCubeTexture||C.mapping===nc)?(d===void 0&&(d=new Qi(new ol(1,1,1),new Ji({name:"BackgroundCubeMaterial",uniforms:Ks(Xi.backgroundCube.uniforms),vertexShader:Xi.backgroundCube.vertexShader,fragmentShader:Xi.backgroundCube.fragmentShader,side:Qn,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),d.geometry.deleteAttribute("normal"),d.geometry.deleteAttribute("uv"),d.onBeforeRender=function(N,D,O){this.matrixWorld.copyPosition(O.matrixWorld)},Object.defineProperty(d.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),r.update(d)),d.material.uniforms.envMap.value=C,d.material.uniforms.backgroundBlurriness.value=z.backgroundBlurriness,d.material.uniforms.backgroundIntensity.value=z.backgroundIntensity,d.material.uniforms.backgroundRotation.value.setFromMatrix4(ST.makeRotationFromEuler(z.backgroundRotation)).transpose(),C.isCubeTexture&&C.isRenderTargetTexture===!1&&d.material.uniforms.backgroundRotation.value.premultiply(Vv),d.material.toneMapped=Ee.getTransfer(C.colorSpace)!==Fe,(g!==C||v!==C.version||_!==s.toneMapping)&&(d.material.needsUpdate=!0,g=C,v=C.version,_=s.toneMapping),d.layers.enableAll(),F.unshift(d,d.geometry,d.material,0,0,null)):C&&C.isTexture&&(m===void 0&&(m=new Qi(new ic(2,2),new Ji({name:"BackgroundMaterial",uniforms:Ks(Xi.background.uniforms),vertexShader:Xi.background.vertexShader,fragmentShader:Xi.background.fragmentShader,side:fr,depthTest:!1,depthWrite:!1,fog:!1,allowOverride:!1})),m.geometry.deleteAttribute("normal"),Object.defineProperty(m.material,"map",{get:function(){return this.uniforms.t2D.value}}),r.update(m)),m.material.uniforms.t2D.value=C,m.material.uniforms.backgroundIntensity.value=z.backgroundIntensity,m.material.toneMapped=Ee.getTransfer(C.colorSpace)!==Fe,C.matrixAutoUpdate===!0&&C.updateMatrix(),m.material.uniforms.uvTransform.value.copy(C.matrix),(g!==C||v!==C.version||_!==s.toneMapping)&&(m.material.needsUpdate=!0,g=C,v=C.version,_=s.toneMapping),m.layers.enableAll(),F.unshift(m,m.geometry,m.material,0,0,null))}function E(F,z){F.getRGB(Bu,zv(s)),i.buffers.color.setClear(Bu.r,Bu.g,Bu.b,z,u)}function S(){d!==void 0&&(d.geometry.dispose(),d.material.dispose(),d=void 0),m!==void 0&&(m.geometry.dispose(),m.material.dispose(),m=void 0)}return{getClearColor:function(){return f},setClearColor:function(F,z=1){f.set(F),p=z,E(f,p)},getClearAlpha:function(){return p},setClearAlpha:function(F){p=F,E(f,p)},render:T,addToRenderList:w,dispose:S}}function MT(s,t){const i=s.getParameter(s.MAX_VERTEX_ATTRIBS),r={},l=_(null);let u=l,f=!1;function p(G,Z,ht,mt,J){let I=!1;const H=v(G,mt,ht,Z);u!==H&&(u=H,d(u.object)),I=M(G,mt,ht,J),I&&T(G,mt,ht,J),J!==null&&t.update(J,s.ELEMENT_ARRAY_BUFFER),(I||f)&&(f=!1,C(G,Z,ht,mt),J!==null&&s.bindBuffer(s.ELEMENT_ARRAY_BUFFER,t.get(J).buffer))}function m(){return s.createVertexArray()}function d(G){return s.bindVertexArray(G)}function g(G){return s.deleteVertexArray(G)}function v(G,Z,ht,mt){const J=mt.wireframe===!0;let I=r[Z.id];I===void 0&&(I={},r[Z.id]=I);const H=G.isInstancedMesh===!0?G.id:0;let j=I[H];j===void 0&&(j={},I[H]=j);let gt=j[ht.id];gt===void 0&&(gt={},j[ht.id]=gt);let Et=gt[J];return Et===void 0&&(Et=_(m()),gt[J]=Et),Et}function _(G){const Z=[],ht=[],mt=[];for(let J=0;J<i;J++)Z[J]=0,ht[J]=0,mt[J]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:Z,enabledAttributes:ht,attributeDivisors:mt,object:G,attributes:{},index:null}}function M(G,Z,ht,mt){const J=u.attributes,I=Z.attributes;let H=0;const j=ht.getAttributes();for(const gt in j)if(j[gt].location>=0){const L=J[gt];let K=I[gt];if(K===void 0&&(gt==="instanceMatrix"&&G.instanceMatrix&&(K=G.instanceMatrix),gt==="instanceColor"&&G.instanceColor&&(K=G.instanceColor)),L===void 0||L.attribute!==K||K&&L.data!==K.data)return!0;H++}return u.attributesNum!==H||u.index!==mt}function T(G,Z,ht,mt){const J={},I=Z.attributes;let H=0;const j=ht.getAttributes();for(const gt in j)if(j[gt].location>=0){let L=I[gt];L===void 0&&(gt==="instanceMatrix"&&G.instanceMatrix&&(L=G.instanceMatrix),gt==="instanceColor"&&G.instanceColor&&(L=G.instanceColor));const K={};K.attribute=L,L&&L.data&&(K.data=L.data),J[gt]=K,H++}u.attributes=J,u.attributesNum=H,u.index=mt}function w(){const G=u.newAttributes;for(let Z=0,ht=G.length;Z<ht;Z++)G[Z]=0}function E(G){S(G,0)}function S(G,Z){const ht=u.newAttributes,mt=u.enabledAttributes,J=u.attributeDivisors;ht[G]=1,mt[G]===0&&(s.enableVertexAttribArray(G),mt[G]=1),J[G]!==Z&&(s.vertexAttribDivisor(G,Z),J[G]=Z)}function F(){const G=u.newAttributes,Z=u.enabledAttributes;for(let ht=0,mt=Z.length;ht<mt;ht++)Z[ht]!==G[ht]&&(s.disableVertexAttribArray(ht),Z[ht]=0)}function z(G,Z,ht,mt,J,I,H){H===!0?s.vertexAttribIPointer(G,Z,ht,J,I):s.vertexAttribPointer(G,Z,ht,mt,J,I)}function C(G,Z,ht,mt){w();const J=mt.attributes,I=ht.getAttributes(),H=Z.defaultAttributeValues;for(const j in I){const gt=I[j];if(gt.location>=0){let Et=J[j];if(Et===void 0&&(j==="instanceMatrix"&&G.instanceMatrix&&(Et=G.instanceMatrix),j==="instanceColor"&&G.instanceColor&&(Et=G.instanceColor)),Et!==void 0){const L=Et.normalized,K=Et.itemSize,Mt=t.get(Et);if(Mt===void 0)continue;const Rt=Mt.buffer,Pt=Mt.type,at=Mt.bytesPerElement,xt=Pt===s.INT||Pt===s.UNSIGNED_INT||Et.gpuType===Wd;if(Et.isInterleavedBufferAttribute){const yt=Et.data,Bt=yt.stride,ee=Et.offset;if(yt.isInstancedInterleavedBuffer){for(let Kt=0;Kt<gt.locationSize;Kt++)S(gt.location+Kt,yt.meshPerAttribute);G.isInstancedMesh!==!0&&mt._maxInstanceCount===void 0&&(mt._maxInstanceCount=yt.meshPerAttribute*yt.count)}else for(let Kt=0;Kt<gt.locationSize;Kt++)E(gt.location+Kt);s.bindBuffer(s.ARRAY_BUFFER,Rt);for(let Kt=0;Kt<gt.locationSize;Kt++)z(gt.location+Kt,K/gt.locationSize,Pt,L,Bt*at,(ee+K/gt.locationSize*Kt)*at,xt)}else{if(Et.isInstancedBufferAttribute){for(let yt=0;yt<gt.locationSize;yt++)S(gt.location+yt,Et.meshPerAttribute);G.isInstancedMesh!==!0&&mt._maxInstanceCount===void 0&&(mt._maxInstanceCount=Et.meshPerAttribute*Et.count)}else for(let yt=0;yt<gt.locationSize;yt++)E(gt.location+yt);s.bindBuffer(s.ARRAY_BUFFER,Rt);for(let yt=0;yt<gt.locationSize;yt++)z(gt.location+yt,K/gt.locationSize,Pt,L,K*at,K/gt.locationSize*yt*at,xt)}}else if(H!==void 0){const L=H[j];if(L!==void 0)switch(L.length){case 2:s.vertexAttrib2fv(gt.location,L);break;case 3:s.vertexAttrib3fv(gt.location,L);break;case 4:s.vertexAttrib4fv(gt.location,L);break;default:s.vertexAttrib1fv(gt.location,L)}}}}F()}function N(){P();for(const G in r){const Z=r[G];for(const ht in Z){const mt=Z[ht];for(const J in mt){const I=mt[J];for(const H in I)g(I[H].object),delete I[H];delete mt[J]}}delete r[G]}}function D(G){if(r[G.id]===void 0)return;const Z=r[G.id];for(const ht in Z){const mt=Z[ht];for(const J in mt){const I=mt[J];for(const H in I)g(I[H].object),delete I[H];delete mt[J]}}delete r[G.id]}function O(G){for(const Z in r){const ht=r[Z];for(const mt in ht){const J=ht[mt];if(J[G.id]===void 0)continue;const I=J[G.id];for(const H in I)g(I[H].object),delete I[H];delete J[G.id]}}}function b(G){for(const Z in r){const ht=r[Z],mt=G.isInstancedMesh===!0?G.id:0,J=ht[mt];if(J!==void 0){for(const I in J){const H=J[I];for(const j in H)g(H[j].object),delete H[j];delete J[I]}delete ht[mt],Object.keys(ht).length===0&&delete r[Z]}}}function P(){q(),f=!0,u!==l&&(u=l,d(u.object))}function q(){l.geometry=null,l.program=null,l.wireframe=!1}return{setup:p,reset:P,resetDefaultState:q,dispose:N,releaseStatesOfGeometry:D,releaseStatesOfObject:b,releaseStatesOfProgram:O,initAttributes:w,enableAttribute:E,disableUnusedAttributes:F}}function ET(s,t,i){let r;function l(m){r=m}function u(m,d){s.drawArrays(r,m,d),i.update(d,r,1)}function f(m,d,g){g!==0&&(s.drawArraysInstanced(r,m,d,g),i.update(d,r,g))}function p(m,d,g){if(g===0)return;t.get("WEBGL_multi_draw").multiDrawArraysWEBGL(r,m,0,d,0,g);let _=0;for(let M=0;M<g;M++)_+=d[M];i.update(_,r,1)}this.setMode=l,this.render=u,this.renderInstances=f,this.renderMultiDraw=p}function bT(s,t,i,r){let l;function u(){if(l!==void 0)return l;if(t.has("EXT_texture_filter_anisotropic")===!0){const O=t.get("EXT_texture_filter_anisotropic");l=s.getParameter(O.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else l=0;return l}function f(O){return!(O!==Ni&&r.convert(O)!==s.getParameter(s.IMPLEMENTATION_COLOR_READ_FORMAT))}function p(O){const b=O===Ra&&(t.has("EXT_color_buffer_half_float")||t.has("EXT_color_buffer_float"));return!(O!==fi&&r.convert(O)!==s.getParameter(s.IMPLEMENTATION_COLOR_READ_TYPE)&&O!==Wi&&!b)}function m(O){if(O==="highp"){if(s.getShaderPrecisionFormat(s.VERTEX_SHADER,s.HIGH_FLOAT).precision>0&&s.getShaderPrecisionFormat(s.FRAGMENT_SHADER,s.HIGH_FLOAT).precision>0)return"highp";O="mediump"}return O==="mediump"&&s.getShaderPrecisionFormat(s.VERTEX_SHADER,s.MEDIUM_FLOAT).precision>0&&s.getShaderPrecisionFormat(s.FRAGMENT_SHADER,s.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let d=i.precision!==void 0?i.precision:"highp";const g=m(d);g!==d&&(te("WebGLRenderer:",d,"not supported, using",g,"instead."),d=g);const v=i.logarithmicDepthBuffer===!0,_=i.reversedDepthBuffer===!0&&t.has("EXT_clip_control");i.reversedDepthBuffer===!0&&_===!1&&te("WebGLRenderer: Unable to use reversed depth buffer due to missing EXT_clip_control extension. Fallback to default depth buffer.");const M=s.getParameter(s.MAX_TEXTURE_IMAGE_UNITS),T=s.getParameter(s.MAX_VERTEX_TEXTURE_IMAGE_UNITS),w=s.getParameter(s.MAX_TEXTURE_SIZE),E=s.getParameter(s.MAX_CUBE_MAP_TEXTURE_SIZE),S=s.getParameter(s.MAX_VERTEX_ATTRIBS),F=s.getParameter(s.MAX_VERTEX_UNIFORM_VECTORS),z=s.getParameter(s.MAX_VARYING_VECTORS),C=s.getParameter(s.MAX_FRAGMENT_UNIFORM_VECTORS),N=s.getParameter(s.MAX_SAMPLES),D=s.getParameter(s.SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:u,getMaxPrecision:m,textureFormatReadable:f,textureTypeReadable:p,precision:d,logarithmicDepthBuffer:v,reversedDepthBuffer:_,maxTextures:M,maxVertexTextures:T,maxTextureSize:w,maxCubemapSize:E,maxAttributes:S,maxVertexUniforms:F,maxVaryings:z,maxFragmentUniforms:C,maxSamples:N,samples:D}}function TT(s){const t=this;let i=null,r=0,l=!1,u=!1;const f=new lr,p=new re,m={value:null,needsUpdate:!1};this.uniform=m,this.numPlanes=0,this.numIntersection=0,this.init=function(v,_){const M=v.length!==0||_||r!==0||l;return l=_,r=v.length,M},this.beginShadows=function(){u=!0,g(null)},this.endShadows=function(){u=!1},this.setGlobalState=function(v,_){i=g(v,_,0)},this.setState=function(v,_,M){const T=v.clippingPlanes,w=v.clipIntersection,E=v.clipShadows,S=s.get(v);if(!l||T===null||T.length===0||u&&!E)u?g(null):d();else{const F=u?0:r,z=F*4;let C=S.clippingState||null;m.value=C,C=g(T,_,z,M);for(let N=0;N!==z;++N)C[N]=i[N];S.clippingState=C,this.numIntersection=w?this.numPlanes:0,this.numPlanes+=F}};function d(){m.value!==i&&(m.value=i,m.needsUpdate=r>0),t.numPlanes=r,t.numIntersection=0}function g(v,_,M,T){const w=v!==null?v.length:0;let E=null;if(w!==0){if(E=m.value,T!==!0||E===null){const S=M+w*4,F=_.matrixWorldInverse;p.getNormalMatrix(F),(E===null||E.length<S)&&(E=new Float32Array(S));for(let z=0,C=M;z!==w;++z,C+=4)f.copy(v[z]).applyMatrix4(F,p),f.normal.toArray(E,C),E[C+3]=f.constant}m.value=E,m.needsUpdate=!0}return t.numPlanes=w,t.numIntersection=0,E}}const cr=4,L0=[.125,.215,.35,.446,.526,.582],Xr=20,AT=256,Jo=new ip,N0=new xe;let Xh=null,Wh=0,qh=0,Yh=!1;const RT=new $;class O0{constructor(t){this._renderer=t,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._sizeLods=[],this._sigmas=[],this._lodMeshes=[],this._backgroundBox=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._blurMaterial=null,this._ggxMaterial=null}fromScene(t,i=0,r=.1,l=100,u={}){const{size:f=256,position:p=RT}=u;Xh=this._renderer.getRenderTarget(),Wh=this._renderer.getActiveCubeFace(),qh=this._renderer.getActiveMipmapLevel(),Yh=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(f);const m=this._allocateTargets();return m.depthBuffer=!0,this._sceneToCubeUV(t,r,l,m,p),i>0&&this._blur(m,0,0,i),this._applyPMREM(m),this._cleanup(m),m}fromEquirectangular(t,i=null){return this._fromTexture(t,i)}fromCubemap(t,i=null){return this._fromTexture(t,i)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=F0(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=I0(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose(),this._backgroundBox!==null&&(this._backgroundBox.geometry.dispose(),this._backgroundBox.material.dispose())}_setSize(t){this._lodMax=Math.floor(Math.log2(t)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._ggxMaterial!==null&&this._ggxMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let t=0;t<this._lodMeshes.length;t++)this._lodMeshes[t].geometry.dispose()}_cleanup(t){this._renderer.setRenderTarget(Xh,Wh,qh),this._renderer.xr.enabled=Yh,t.scissorTest=!1,Hs(t,0,0,t.width,t.height)}_fromTexture(t,i){t.mapping===Yr||t.mapping===Ys?this._setSize(t.image.length===0?16:t.image[0].width||t.image[0].image.width):this._setSize(t.image.width/4),Xh=this._renderer.getRenderTarget(),Wh=this._renderer.getActiveCubeFace(),qh=this._renderer.getActiveMipmapLevel(),Yh=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const r=i||this._allocateTargets();return this._textureToCubeUV(t,r),this._applyPMREM(r),this._cleanup(r),r}_allocateTargets(){const t=3*Math.max(this._cubeSize,112),i=4*this._cubeSize,r={magFilter:In,minFilter:In,generateMipmaps:!1,type:Ra,format:Ni,colorSpace:ju,depthBuffer:!1},l=P0(t,i,r);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==t||this._pingPongRenderTarget.height!==i){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=P0(t,i,r);const{_lodMax:u}=this;({lodMeshes:this._lodMeshes,sizeLods:this._sizeLods,sigmas:this._sigmas}=CT(u)),this._blurMaterial=DT(u,t,i),this._ggxMaterial=wT(u,t,i)}return l}_compileMaterial(t){const i=new Qi(new Pi,t);this._renderer.compile(i,Jo)}_sceneToCubeUV(t,i,r,l,u){const m=new Mi(90,1,i,r),d=[1,-1,1,1,1,1],g=[1,1,1,-1,-1,-1],v=this._renderer,_=v.autoClear,M=v.toneMapping;v.getClearColor(N0),v.toneMapping=Yi,v.autoClear=!1,v.state.buffers.depth.getReversed()&&(v.setRenderTarget(l),v.clearDepth(),v.setRenderTarget(null)),this._backgroundBox===null&&(this._backgroundBox=new Qi(new ol,new Pv({name:"PMREM.Background",side:Qn,depthWrite:!1,depthTest:!1})));const w=this._backgroundBox,E=w.material;let S=!1;const F=t.background;F?F.isColor&&(E.color.copy(F),t.background=null,S=!0):(E.color.copy(N0),S=!0);for(let z=0;z<6;z++){const C=z%3;C===0?(m.up.set(0,d[z],0),m.position.set(u.x,u.y,u.z),m.lookAt(u.x+g[z],u.y,u.z)):C===1?(m.up.set(0,0,d[z]),m.position.set(u.x,u.y,u.z),m.lookAt(u.x,u.y+g[z],u.z)):(m.up.set(0,d[z],0),m.position.set(u.x,u.y,u.z),m.lookAt(u.x,u.y,u.z+g[z]));const N=this._cubeSize;Hs(l,C*N,z>2?N:0,N,N),v.setRenderTarget(l),S&&v.render(w,m),v.render(t,m)}v.toneMapping=M,v.autoClear=_,t.background=F}_textureToCubeUV(t,i){const r=this._renderer,l=t.mapping===Yr||t.mapping===Ys;l?(this._cubemapMaterial===null&&(this._cubemapMaterial=F0()),this._cubemapMaterial.uniforms.flipEnvMap.value=t.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=I0());const u=l?this._cubemapMaterial:this._equirectMaterial,f=this._lodMeshes[0];f.material=u;const p=u.uniforms;p.envMap.value=t;const m=this._cubeSize;Hs(i,0,0,3*m,2*m),r.setRenderTarget(i),r.render(f,Jo)}_applyPMREM(t){const i=this._renderer,r=i.autoClear;i.autoClear=!1;const l=this._lodMeshes.length;for(let u=1;u<l;u++)this._applyGGXFilter(t,u-1,u);i.autoClear=r}_applyGGXFilter(t,i,r){const l=this._renderer,u=this._pingPongRenderTarget,f=this._ggxMaterial,p=this._lodMeshes[r];p.material=f;const m=f.uniforms,d=r/(this._lodMeshes.length-1),g=i/(this._lodMeshes.length-1),v=Math.sqrt(d*d-g*g),_=0+d*1.25,M=v*_,{_lodMax:T}=this,w=this._sizeLods[r],E=3*w*(r>T-cr?r-T+cr:0),S=4*(this._cubeSize-w);m.envMap.value=t.texture,m.roughness.value=M,m.mipInt.value=T-i,Hs(u,E,S,3*w,2*w),l.setRenderTarget(u),l.render(p,Jo),m.envMap.value=u.texture,m.roughness.value=0,m.mipInt.value=T-r,Hs(t,E,S,3*w,2*w),l.setRenderTarget(t),l.render(p,Jo)}_blur(t,i,r,l,u){const f=this._pingPongRenderTarget;this._halfBlur(t,f,i,r,l,"latitudinal",u),this._halfBlur(f,t,r,r,l,"longitudinal",u)}_halfBlur(t,i,r,l,u,f,p){const m=this._renderer,d=this._blurMaterial;f!=="latitudinal"&&f!=="longitudinal"&&be("blur direction must be either latitudinal or longitudinal!");const g=3,v=this._lodMeshes[l];v.material=d;const _=d.uniforms,M=this._sizeLods[r]-1,T=isFinite(u)?Math.PI/(2*M):2*Math.PI/(2*Xr-1),w=u/T,E=isFinite(u)?1+Math.floor(g*w):Xr;E>Xr&&te(`sigmaRadians, ${u}, is too large and will clip, as it requested ${E} samples when the maximum is set to ${Xr}`);const S=[];let F=0;for(let O=0;O<Xr;++O){const b=O/w,P=Math.exp(-b*b/2);S.push(P),O===0?F+=P:O<E&&(F+=2*P)}for(let O=0;O<S.length;O++)S[O]=S[O]/F;_.envMap.value=t.texture,_.samples.value=E,_.weights.value=S,_.latitudinal.value=f==="latitudinal",p&&(_.poleAxis.value=p);const{_lodMax:z}=this;_.dTheta.value=T,_.mipInt.value=z-r;const C=this._sizeLods[l],N=3*C*(l>z-cr?l-z+cr:0),D=4*(this._cubeSize-C);Hs(i,N,D,3*C,2*C),m.setRenderTarget(i),m.render(v,Jo)}}function CT(s){const t=[],i=[],r=[];let l=s;const u=s-cr+1+L0.length;for(let f=0;f<u;f++){const p=Math.pow(2,l);t.push(p);let m=1/p;f>s-cr?m=L0[f-s+cr-1]:f===0&&(m=0),i.push(m);const d=1/(p-2),g=-d,v=1+d,_=[g,g,v,g,v,v,g,g,v,v,g,v],M=6,T=6,w=3,E=2,S=1,F=new Float32Array(w*T*M),z=new Float32Array(E*T*M),C=new Float32Array(S*T*M);for(let D=0;D<M;D++){const O=D%3*2/3-1,b=D>2?0:-1,P=[O,b,0,O+2/3,b,0,O+2/3,b+1,0,O,b,0,O+2/3,b+1,0,O,b+1,0];F.set(P,w*T*D),z.set(_,E*T*D);const q=[D,D,D,D,D,D];C.set(q,S*T*D)}const N=new Pi;N.setAttribute("position",new hi(F,w)),N.setAttribute("uv",new hi(z,E)),N.setAttribute("faceIndex",new hi(C,S)),r.push(new Qi(N,null)),l>cr&&l--}return{lodMeshes:r,sizeLods:t,sigmas:i}}function P0(s,t,i){const r=new Zi(s,t,i);return r.texture.mapping=nc,r.texture.name="PMREM.cubeUv",r.scissorTest=!0,r}function Hs(s,t,i,r,l){s.viewport.set(t,i,r,l),s.scissor.set(t,i,r,l)}function wT(s,t,i){return new Ji({name:"PMREMGGXConvolution",defines:{GGX_SAMPLES:AT,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/i,CUBEUV_MAX_MIP:`${s}.0`},uniforms:{envMap:{value:null},roughness:{value:0},mipInt:{value:0}},vertexShader:ac(),fragmentShader:`

			precision highp float;
			precision highp int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform float roughness;
			uniform float mipInt;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			#define PI 3.14159265359

			// Van der Corput radical inverse
			float radicalInverse_VdC(uint bits) {
				bits = (bits << 16u) | (bits >> 16u);
				bits = ((bits & 0x55555555u) << 1u) | ((bits & 0xAAAAAAAAu) >> 1u);
				bits = ((bits & 0x33333333u) << 2u) | ((bits & 0xCCCCCCCCu) >> 2u);
				bits = ((bits & 0x0F0F0F0Fu) << 4u) | ((bits & 0xF0F0F0F0u) >> 4u);
				bits = ((bits & 0x00FF00FFu) << 8u) | ((bits & 0xFF00FF00u) >> 8u);
				return float(bits) * 2.3283064365386963e-10; // / 0x100000000
			}

			// Hammersley sequence
			vec2 hammersley(uint i, uint N) {
				return vec2(float(i) / float(N), radicalInverse_VdC(i));
			}

			// GGX VNDF importance sampling (Eric Heitz 2018)
			// "Sampling the GGX Distribution of Visible Normals"
			// https://jcgt.org/published/0007/04/01/
			vec3 importanceSampleGGX_VNDF(vec2 Xi, vec3 V, float roughness) {
				float alpha = roughness * roughness;

				// Section 4.1: Orthonormal basis
				vec3 T1 = vec3(1.0, 0.0, 0.0);
				vec3 T2 = cross(V, T1);

				// Section 4.2: Parameterization of projected area
				float r = sqrt(Xi.x);
				float phi = 2.0 * PI * Xi.y;
				float t1 = r * cos(phi);
				float t2 = r * sin(phi);
				float s = 0.5 * (1.0 + V.z);
				t2 = (1.0 - s) * sqrt(1.0 - t1 * t1) + s * t2;

				// Section 4.3: Reprojection onto hemisphere
				vec3 Nh = t1 * T1 + t2 * T2 + sqrt(max(0.0, 1.0 - t1 * t1 - t2 * t2)) * V;

				// Section 3.4: Transform back to ellipsoid configuration
				return normalize(vec3(alpha * Nh.x, alpha * Nh.y, max(0.0, Nh.z)));
			}

			void main() {
				vec3 N = normalize(vOutputDirection);
				vec3 V = N; // Assume view direction equals normal for pre-filtering

				vec3 prefilteredColor = vec3(0.0);
				float totalWeight = 0.0;

				// For very low roughness, just sample the environment directly
				if (roughness < 0.001) {
					gl_FragColor = vec4(bilinearCubeUV(envMap, N, mipInt), 1.0);
					return;
				}

				// Tangent space basis for VNDF sampling
				vec3 up = abs(N.z) < 0.999 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 0.0, 0.0);
				vec3 tangent = normalize(cross(up, N));
				vec3 bitangent = cross(N, tangent);

				for(uint i = 0u; i < uint(GGX_SAMPLES); i++) {
					vec2 Xi = hammersley(i, uint(GGX_SAMPLES));

					// For PMREM, V = N, so in tangent space V is always (0, 0, 1)
					vec3 H_tangent = importanceSampleGGX_VNDF(Xi, vec3(0.0, 0.0, 1.0), roughness);

					// Transform H back to world space
					vec3 H = normalize(tangent * H_tangent.x + bitangent * H_tangent.y + N * H_tangent.z);
					vec3 L = normalize(2.0 * dot(V, H) * H - V);

					float NdotL = max(dot(N, L), 0.0);

					if(NdotL > 0.0) {
						// Sample environment at fixed mip level
						// VNDF importance sampling handles the distribution filtering
						vec3 sampleColor = bilinearCubeUV(envMap, L, mipInt);

						// Weight by NdotL for the split-sum approximation
						// VNDF PDF naturally accounts for the visible microfacet distribution
						prefilteredColor += sampleColor * NdotL;
						totalWeight += NdotL;
					}
				}

				if (totalWeight > 0.0) {
					prefilteredColor = prefilteredColor / totalWeight;
				}

				gl_FragColor = vec4(prefilteredColor, 1.0);
			}
		`,blending:Ta,depthTest:!1,depthWrite:!1})}function DT(s,t,i){const r=new Float32Array(Xr),l=new $(0,1,0);return new Ji({name:"SphericalGaussianBlur",defines:{n:Xr,CUBEUV_TEXEL_WIDTH:1/t,CUBEUV_TEXEL_HEIGHT:1/i,CUBEUV_MAX_MIP:`${s}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:r},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:l}},vertexShader:ac(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:Ta,depthTest:!1,depthWrite:!1})}function I0(){return new Ji({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:ac(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:Ta,depthTest:!1,depthWrite:!1})}function F0(){return new Ji({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:ac(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Ta,depthTest:!1,depthWrite:!1})}function ac(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}class kv extends Zi{constructor(t=1,i={}){super(t,t,i),this.isWebGLCubeRenderTarget=!0;const r={width:t,height:t,depth:1},l=[r,r,r,r,r,r];this.texture=new Iv(l),this._setTextureOptions(i),this.texture.isRenderTargetTexture=!0}fromEquirectangularTexture(t,i){this.texture.type=i.type,this.texture.colorSpace=i.colorSpace,this.texture.generateMipmaps=i.generateMipmaps,this.texture.minFilter=i.minFilter,this.texture.magFilter=i.magFilter;const r={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},l=new ol(5,5,5),u=new Ji({name:"CubemapFromEquirect",uniforms:Ks(r.uniforms),vertexShader:r.vertexShader,fragmentShader:r.fragmentShader,side:Qn,blending:Ta});u.uniforms.tEquirect.value=i;const f=new Qi(l,u),p=i.minFilter;return i.minFilter===Wr&&(i.minFilter=In),new PM(1,10,this).update(t,f),i.minFilter=p,f.geometry.dispose(),f.material.dispose(),this}clear(t,i=!0,r=!0,l=!0){const u=t.getRenderTarget();for(let f=0;f<6;f++)t.setRenderTarget(this,f),t.clear(i,r,l);t.setRenderTarget(u)}}function UT(s){let t=new WeakMap,i=new WeakMap,r=null;function l(_,M=!1){return _==null?null:M?f(_):u(_)}function u(_){if(_&&_.isTexture){const M=_.mapping;if(M===_h||M===vh)if(t.has(_)){const T=t.get(_).texture;return p(T,_.mapping)}else{const T=_.image;if(T&&T.height>0){const w=new kv(T.height);return w.fromEquirectangularTexture(s,_),t.set(_,w),_.addEventListener("dispose",d),p(w.texture,_.mapping)}else return null}}return _}function f(_){if(_&&_.isTexture){const M=_.mapping,T=M===_h||M===vh,w=M===Yr||M===Ys;if(T||w){let E=i.get(_);const S=E!==void 0?E.texture.pmremVersion:0;if(_.isRenderTargetTexture&&_.pmremVersion!==S)return r===null&&(r=new O0(s)),E=T?r.fromEquirectangular(_,E):r.fromCubemap(_,E),E.texture.pmremVersion=_.pmremVersion,i.set(_,E),E.texture;if(E!==void 0)return E.texture;{const F=_.image;return T&&F&&F.height>0||w&&F&&m(F)?(r===null&&(r=new O0(s)),E=T?r.fromEquirectangular(_):r.fromCubemap(_),E.texture.pmremVersion=_.pmremVersion,i.set(_,E),_.addEventListener("dispose",g),E.texture):null}}}return _}function p(_,M){return M===_h?_.mapping=Yr:M===vh&&(_.mapping=Ys),_}function m(_){let M=0;const T=6;for(let w=0;w<T;w++)_[w]!==void 0&&M++;return M===T}function d(_){const M=_.target;M.removeEventListener("dispose",d);const T=t.get(M);T!==void 0&&(t.delete(M),T.dispose())}function g(_){const M=_.target;M.removeEventListener("dispose",g);const T=i.get(M);T!==void 0&&(i.delete(M),T.dispose())}function v(){t=new WeakMap,i=new WeakMap,r!==null&&(r.dispose(),r=null)}return{get:l,dispose:v}}function LT(s){const t={};function i(r){if(t[r]!==void 0)return t[r];const l=s.getExtension(r);return t[r]=l,l}return{has:function(r){return i(r)!==null},init:function(){i("EXT_color_buffer_float"),i("WEBGL_clip_cull_distance"),i("OES_texture_float_linear"),i("EXT_color_buffer_half_float"),i("WEBGL_multisampled_render_to_texture"),i("WEBGL_render_shared_exponent")},get:function(r){const l=i(r);return l===null&&Xs("WebGLRenderer: "+r+" extension not supported."),l}}}function NT(s,t,i,r){const l={},u=new WeakMap;function f(v){const _=v.target;_.index!==null&&t.remove(_.index);for(const T in _.attributes)t.remove(_.attributes[T]);_.removeEventListener("dispose",f),delete l[_.id];const M=u.get(_);M&&(t.remove(M),u.delete(_)),r.releaseStatesOfGeometry(_),_.isInstancedBufferGeometry===!0&&delete _._maxInstanceCount,i.memory.geometries--}function p(v,_){return l[_.id]===!0||(_.addEventListener("dispose",f),l[_.id]=!0,i.memory.geometries++),_}function m(v){const _=v.attributes;for(const M in _)t.update(_[M],s.ARRAY_BUFFER)}function d(v){const _=[],M=v.index,T=v.attributes.position;let w=0;if(T===void 0)return;if(M!==null){const F=M.array;w=M.version;for(let z=0,C=F.length;z<C;z+=3){const N=F[z+0],D=F[z+1],O=F[z+2];_.push(N,D,D,O,O,N)}}else{const F=T.array;w=T.version;for(let z=0,C=F.length/3-1;z<C;z+=3){const N=z+0,D=z+1,O=z+2;_.push(N,D,D,O,O,N)}}const E=new(T.count>=65535?Nv:Lv)(_,1);E.version=w;const S=u.get(v);S&&t.remove(S),u.set(v,E)}function g(v){const _=u.get(v);if(_){const M=v.index;M!==null&&_.version<M.version&&d(v)}else d(v);return u.get(v)}return{get:p,update:m,getWireframeAttribute:g}}function OT(s,t,i){let r;function l(v){r=v}let u,f;function p(v){u=v.type,f=v.bytesPerElement}function m(v,_){s.drawElements(r,_,u,v*f),i.update(_,r,1)}function d(v,_,M){M!==0&&(s.drawElementsInstanced(r,_,u,v*f,M),i.update(_,r,M))}function g(v,_,M){if(M===0)return;t.get("WEBGL_multi_draw").multiDrawElementsWEBGL(r,_,0,u,v,0,M);let w=0;for(let E=0;E<M;E++)w+=_[E];i.update(w,r,1)}this.setMode=l,this.setIndex=p,this.render=m,this.renderInstances=d,this.renderMultiDraw=g}function PT(s){const t={geometries:0,textures:0},i={frame:0,calls:0,triangles:0,points:0,lines:0};function r(u,f,p){switch(i.calls++,f){case s.TRIANGLES:i.triangles+=p*(u/3);break;case s.LINES:i.lines+=p*(u/2);break;case s.LINE_STRIP:i.lines+=p*(u-1);break;case s.LINE_LOOP:i.lines+=p*u;break;case s.POINTS:i.points+=p*u;break;default:be("WebGLInfo: Unknown draw mode:",f);break}}function l(){i.calls=0,i.triangles=0,i.points=0,i.lines=0}return{memory:t,render:i,programs:null,autoReset:!0,reset:l,update:r}}function IT(s,t,i){const r=new WeakMap,l=new tn;function u(f,p,m){const d=f.morphTargetInfluences,g=p.morphAttributes.position||p.morphAttributes.normal||p.morphAttributes.color,v=g!==void 0?g.length:0;let _=r.get(p);if(_===void 0||_.count!==v){let q=function(){b.dispose(),r.delete(p),p.removeEventListener("dispose",q)};var M=q;_!==void 0&&_.texture.dispose();const T=p.morphAttributes.position!==void 0,w=p.morphAttributes.normal!==void 0,E=p.morphAttributes.color!==void 0,S=p.morphAttributes.position||[],F=p.morphAttributes.normal||[],z=p.morphAttributes.color||[];let C=0;T===!0&&(C=1),w===!0&&(C=2),E===!0&&(C=3);let N=p.attributes.position.count*C,D=1;N>t.maxTextureSize&&(D=Math.ceil(N/t.maxTextureSize),N=t.maxTextureSize);const O=new Float32Array(N*D*4*v),b=new wv(O,N,D,v);b.type=Wi,b.needsUpdate=!0;const P=C*4;for(let G=0;G<v;G++){const Z=S[G],ht=F[G],mt=z[G],J=N*D*4*G;for(let I=0;I<Z.count;I++){const H=I*P;T===!0&&(l.fromBufferAttribute(Z,I),O[J+H+0]=l.x,O[J+H+1]=l.y,O[J+H+2]=l.z,O[J+H+3]=0),w===!0&&(l.fromBufferAttribute(ht,I),O[J+H+4]=l.x,O[J+H+5]=l.y,O[J+H+6]=l.z,O[J+H+7]=0),E===!0&&(l.fromBufferAttribute(mt,I),O[J+H+8]=l.x,O[J+H+9]=l.y,O[J+H+10]=l.z,O[J+H+11]=mt.itemSize===4?l.w:1)}}_={count:v,texture:b,size:new ie(N,D)},r.set(p,_),p.addEventListener("dispose",q)}if(f.isInstancedMesh===!0&&f.morphTexture!==null)m.getUniforms().setValue(s,"morphTexture",f.morphTexture,i);else{let T=0;for(let E=0;E<d.length;E++)T+=d[E];const w=p.morphTargetsRelative?1:1-T;m.getUniforms().setValue(s,"morphTargetBaseInfluence",w),m.getUniforms().setValue(s,"morphTargetInfluences",d)}m.getUniforms().setValue(s,"morphTargetsTexture",_.texture,i),m.getUniforms().setValue(s,"morphTargetsTextureSize",_.size)}return{update:u}}function FT(s,t,i,r,l){let u=new WeakMap;function f(d){const g=l.render.frame,v=d.geometry,_=t.get(d,v);if(u.get(_)!==g&&(t.update(_),u.set(_,g)),d.isInstancedMesh&&(d.hasEventListener("dispose",m)===!1&&d.addEventListener("dispose",m),u.get(d)!==g&&(i.update(d.instanceMatrix,s.ARRAY_BUFFER),d.instanceColor!==null&&i.update(d.instanceColor,s.ARRAY_BUFFER),u.set(d,g))),d.isSkinnedMesh){const M=d.skeleton;u.get(M)!==g&&(M.update(),u.set(M,g))}return _}function p(){u=new WeakMap}function m(d){const g=d.target;g.removeEventListener("dispose",m),r.releaseStatesOfObject(g),i.remove(g.instanceMatrix),g.instanceColor!==null&&i.remove(g.instanceColor)}return{update:f,dispose:p}}const zT={[dv]:"LINEAR_TONE_MAPPING",[pv]:"REINHARD_TONE_MAPPING",[mv]:"CINEON_TONE_MAPPING",[gv]:"ACES_FILMIC_TONE_MAPPING",[vv]:"AGX_TONE_MAPPING",[xv]:"NEUTRAL_TONE_MAPPING",[_v]:"CUSTOM_TONE_MAPPING"};function BT(s,t,i,r,l,u){const f=new Zi(t,i,{type:s,depthBuffer:l,stencilBuffer:u,samples:r?4:0,depthTexture:l?new Zs(t,i):void 0}),p=new Zi(t,i,{type:Ra,depthBuffer:!1,stencilBuffer:!1}),m=new Pi;m.setAttribute("position",new Oi([-1,3,0,-1,-1,0,3,-1,0],3)),m.setAttribute("uv",new Oi([0,2,0,0,2,0],2));const d=new MM({uniforms:{tDiffuse:{value:null}},vertexShader:`
			precision highp float;

			uniform mat4 modelViewMatrix;
			uniform mat4 projectionMatrix;

			attribute vec3 position;
			attribute vec2 uv;

			varying vec2 vUv;

			void main() {
				vUv = uv;
				gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
			}`,fragmentShader:`
			precision highp float;

			uniform sampler2D tDiffuse;

			varying vec2 vUv;

			#include <tonemapping_pars_fragment>
			#include <colorspace_pars_fragment>

			void main() {
				gl_FragColor = texture2D( tDiffuse, vUv );

				#ifdef LINEAR_TONE_MAPPING
					gl_FragColor.rgb = LinearToneMapping( gl_FragColor.rgb );
				#elif defined( REINHARD_TONE_MAPPING )
					gl_FragColor.rgb = ReinhardToneMapping( gl_FragColor.rgb );
				#elif defined( CINEON_TONE_MAPPING )
					gl_FragColor.rgb = CineonToneMapping( gl_FragColor.rgb );
				#elif defined( ACES_FILMIC_TONE_MAPPING )
					gl_FragColor.rgb = ACESFilmicToneMapping( gl_FragColor.rgb );
				#elif defined( AGX_TONE_MAPPING )
					gl_FragColor.rgb = AgXToneMapping( gl_FragColor.rgb );
				#elif defined( NEUTRAL_TONE_MAPPING )
					gl_FragColor.rgb = NeutralToneMapping( gl_FragColor.rgb );
				#elif defined( CUSTOM_TONE_MAPPING )
					gl_FragColor.rgb = CustomToneMapping( gl_FragColor.rgb );
				#endif

				#ifdef SRGB_TRANSFER
					gl_FragColor = sRGBTransferOETF( gl_FragColor );
				#endif
			}`,depthTest:!1,depthWrite:!1}),g=new Qi(m,d),v=new ip(-1,1,1,-1,0,1);let _=null,M=null,T=!1,w,E=null,S=[],F=!1;this.setSize=function(z,C){f.setSize(z,C),p.setSize(z,C);for(let N=0;N<S.length;N++){const D=S[N];D.setSize&&D.setSize(z,C)}},this.setEffects=function(z){S=z,F=S.length>0&&S[0].isRenderPass===!0;const C=f.width,N=f.height;for(let D=0;D<S.length;D++){const O=S[D];O.setSize&&O.setSize(C,N)}},this.begin=function(z,C){if(T||z.toneMapping===Yi&&S.length===0)return!1;if(E=C,C!==null){const N=C.width,D=C.height;(f.width!==N||f.height!==D)&&this.setSize(N,D)}return F===!1&&z.setRenderTarget(f),w=z.toneMapping,z.toneMapping=Yi,!0},this.hasRenderPass=function(){return F},this.end=function(z,C){z.toneMapping=w,T=!0;let N=f,D=p;for(let O=0;O<S.length;O++){const b=S[O];if(b.enabled!==!1&&(b.render(z,D,N,C),b.needsSwap!==!1)){const P=N;N=D,D=P}}if(_!==z.outputColorSpace||M!==z.toneMapping){_=z.outputColorSpace,M=z.toneMapping,d.defines={},Ee.getTransfer(_)===Fe&&(d.defines.SRGB_TRANSFER="");const O=zT[M];O&&(d.defines[O]=""),d.needsUpdate=!0}d.uniforms.tDiffuse.value=N.texture,z.setRenderTarget(E),z.render(g,v),E=null,T=!1},this.isCompositing=function(){return T},this.dispose=function(){f.depthTexture&&f.depthTexture.dispose(),f.dispose(),p.dispose(),m.dispose(),d.dispose()}}const Xv=new Hn,Hd=new Zs(1,1),Wv=new wv,qv=new $y,Yv=new Iv,z0=[],B0=[],H0=new Float32Array(16),G0=new Float32Array(9),V0=new Float32Array(4);function js(s,t,i){const r=s[0];if(r<=0||r>0)return s;const l=t*i;let u=z0[l];if(u===void 0&&(u=new Float32Array(l),z0[l]=u),t!==0){r.toArray(u,0);for(let f=1,p=0;f!==t;++f)p+=i,s[f].toArray(u,p)}return u}function yn(s,t){if(s.length!==t.length)return!1;for(let i=0,r=s.length;i<r;i++)if(s[i]!==t[i])return!1;return!0}function Mn(s,t){for(let i=0,r=t.length;i<r;i++)s[i]=t[i]}function rc(s,t){let i=B0[t];i===void 0&&(i=new Int32Array(t),B0[t]=i);for(let r=0;r!==t;++r)i[r]=s.allocateTextureUnit();return i}function HT(s,t){const i=this.cache;i[0]!==t&&(s.uniform1f(this.addr,t),i[0]=t)}function GT(s,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y)&&(s.uniform2f(this.addr,t.x,t.y),i[0]=t.x,i[1]=t.y);else{if(yn(i,t))return;s.uniform2fv(this.addr,t),Mn(i,t)}}function VT(s,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z)&&(s.uniform3f(this.addr,t.x,t.y,t.z),i[0]=t.x,i[1]=t.y,i[2]=t.z);else if(t.r!==void 0)(i[0]!==t.r||i[1]!==t.g||i[2]!==t.b)&&(s.uniform3f(this.addr,t.r,t.g,t.b),i[0]=t.r,i[1]=t.g,i[2]=t.b);else{if(yn(i,t))return;s.uniform3fv(this.addr,t),Mn(i,t)}}function kT(s,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z||i[3]!==t.w)&&(s.uniform4f(this.addr,t.x,t.y,t.z,t.w),i[0]=t.x,i[1]=t.y,i[2]=t.z,i[3]=t.w);else{if(yn(i,t))return;s.uniform4fv(this.addr,t),Mn(i,t)}}function XT(s,t){const i=this.cache,r=t.elements;if(r===void 0){if(yn(i,t))return;s.uniformMatrix2fv(this.addr,!1,t),Mn(i,t)}else{if(yn(i,r))return;V0.set(r),s.uniformMatrix2fv(this.addr,!1,V0),Mn(i,r)}}function WT(s,t){const i=this.cache,r=t.elements;if(r===void 0){if(yn(i,t))return;s.uniformMatrix3fv(this.addr,!1,t),Mn(i,t)}else{if(yn(i,r))return;G0.set(r),s.uniformMatrix3fv(this.addr,!1,G0),Mn(i,r)}}function qT(s,t){const i=this.cache,r=t.elements;if(r===void 0){if(yn(i,t))return;s.uniformMatrix4fv(this.addr,!1,t),Mn(i,t)}else{if(yn(i,r))return;H0.set(r),s.uniformMatrix4fv(this.addr,!1,H0),Mn(i,r)}}function YT(s,t){const i=this.cache;i[0]!==t&&(s.uniform1i(this.addr,t),i[0]=t)}function ZT(s,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y)&&(s.uniform2i(this.addr,t.x,t.y),i[0]=t.x,i[1]=t.y);else{if(yn(i,t))return;s.uniform2iv(this.addr,t),Mn(i,t)}}function KT(s,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z)&&(s.uniform3i(this.addr,t.x,t.y,t.z),i[0]=t.x,i[1]=t.y,i[2]=t.z);else{if(yn(i,t))return;s.uniform3iv(this.addr,t),Mn(i,t)}}function QT(s,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z||i[3]!==t.w)&&(s.uniform4i(this.addr,t.x,t.y,t.z,t.w),i[0]=t.x,i[1]=t.y,i[2]=t.z,i[3]=t.w);else{if(yn(i,t))return;s.uniform4iv(this.addr,t),Mn(i,t)}}function JT(s,t){const i=this.cache;i[0]!==t&&(s.uniform1ui(this.addr,t),i[0]=t)}function jT(s,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y)&&(s.uniform2ui(this.addr,t.x,t.y),i[0]=t.x,i[1]=t.y);else{if(yn(i,t))return;s.uniform2uiv(this.addr,t),Mn(i,t)}}function $T(s,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z)&&(s.uniform3ui(this.addr,t.x,t.y,t.z),i[0]=t.x,i[1]=t.y,i[2]=t.z);else{if(yn(i,t))return;s.uniform3uiv(this.addr,t),Mn(i,t)}}function tA(s,t){const i=this.cache;if(t.x!==void 0)(i[0]!==t.x||i[1]!==t.y||i[2]!==t.z||i[3]!==t.w)&&(s.uniform4ui(this.addr,t.x,t.y,t.z,t.w),i[0]=t.x,i[1]=t.y,i[2]=t.z,i[3]=t.w);else{if(yn(i,t))return;s.uniform4uiv(this.addr,t),Mn(i,t)}}function eA(s,t,i){const r=this.cache,l=i.allocateTextureUnit();r[0]!==l&&(s.uniform1i(this.addr,l),r[0]=l);let u;this.type===s.SAMPLER_2D_SHADOW?(Hd.compareFunction=i.isReversedDepthBuffer()?jd:Jd,u=Hd):u=Xv,i.setTexture2D(t||u,l)}function nA(s,t,i){const r=this.cache,l=i.allocateTextureUnit();r[0]!==l&&(s.uniform1i(this.addr,l),r[0]=l),i.setTexture3D(t||qv,l)}function iA(s,t,i){const r=this.cache,l=i.allocateTextureUnit();r[0]!==l&&(s.uniform1i(this.addr,l),r[0]=l),i.setTextureCube(t||Yv,l)}function aA(s,t,i){const r=this.cache,l=i.allocateTextureUnit();r[0]!==l&&(s.uniform1i(this.addr,l),r[0]=l),i.setTexture2DArray(t||Wv,l)}function rA(s){switch(s){case 5126:return HT;case 35664:return GT;case 35665:return VT;case 35666:return kT;case 35674:return XT;case 35675:return WT;case 35676:return qT;case 5124:case 35670:return YT;case 35667:case 35671:return ZT;case 35668:case 35672:return KT;case 35669:case 35673:return QT;case 5125:return JT;case 36294:return jT;case 36295:return $T;case 36296:return tA;case 35678:case 36198:case 36298:case 36306:case 35682:return eA;case 35679:case 36299:case 36307:return nA;case 35680:case 36300:case 36308:case 36293:return iA;case 36289:case 36303:case 36311:case 36292:return aA}}function sA(s,t){s.uniform1fv(this.addr,t)}function oA(s,t){const i=js(t,this.size,2);s.uniform2fv(this.addr,i)}function lA(s,t){const i=js(t,this.size,3);s.uniform3fv(this.addr,i)}function uA(s,t){const i=js(t,this.size,4);s.uniform4fv(this.addr,i)}function cA(s,t){const i=js(t,this.size,4);s.uniformMatrix2fv(this.addr,!1,i)}function fA(s,t){const i=js(t,this.size,9);s.uniformMatrix3fv(this.addr,!1,i)}function hA(s,t){const i=js(t,this.size,16);s.uniformMatrix4fv(this.addr,!1,i)}function dA(s,t){s.uniform1iv(this.addr,t)}function pA(s,t){s.uniform2iv(this.addr,t)}function mA(s,t){s.uniform3iv(this.addr,t)}function gA(s,t){s.uniform4iv(this.addr,t)}function _A(s,t){s.uniform1uiv(this.addr,t)}function vA(s,t){s.uniform2uiv(this.addr,t)}function xA(s,t){s.uniform3uiv(this.addr,t)}function SA(s,t){s.uniform4uiv(this.addr,t)}function yA(s,t,i){const r=this.cache,l=t.length,u=rc(i,l);yn(r,u)||(s.uniform1iv(this.addr,u),Mn(r,u));let f;this.type===s.SAMPLER_2D_SHADOW?f=Hd:f=Xv;for(let p=0;p!==l;++p)i.setTexture2D(t[p]||f,u[p])}function MA(s,t,i){const r=this.cache,l=t.length,u=rc(i,l);yn(r,u)||(s.uniform1iv(this.addr,u),Mn(r,u));for(let f=0;f!==l;++f)i.setTexture3D(t[f]||qv,u[f])}function EA(s,t,i){const r=this.cache,l=t.length,u=rc(i,l);yn(r,u)||(s.uniform1iv(this.addr,u),Mn(r,u));for(let f=0;f!==l;++f)i.setTextureCube(t[f]||Yv,u[f])}function bA(s,t,i){const r=this.cache,l=t.length,u=rc(i,l);yn(r,u)||(s.uniform1iv(this.addr,u),Mn(r,u));for(let f=0;f!==l;++f)i.setTexture2DArray(t[f]||Wv,u[f])}function TA(s){switch(s){case 5126:return sA;case 35664:return oA;case 35665:return lA;case 35666:return uA;case 35674:return cA;case 35675:return fA;case 35676:return hA;case 5124:case 35670:return dA;case 35667:case 35671:return pA;case 35668:case 35672:return mA;case 35669:case 35673:return gA;case 5125:return _A;case 36294:return vA;case 36295:return xA;case 36296:return SA;case 35678:case 36198:case 36298:case 36306:case 35682:return yA;case 35679:case 36299:case 36307:return MA;case 35680:case 36300:case 36308:case 36293:return EA;case 36289:case 36303:case 36311:case 36292:return bA}}class AA{constructor(t,i,r){this.id=t,this.addr=r,this.cache=[],this.type=i.type,this.setValue=rA(i.type)}}class RA{constructor(t,i,r){this.id=t,this.addr=r,this.cache=[],this.type=i.type,this.size=i.size,this.setValue=TA(i.type)}}class CA{constructor(t){this.id=t,this.seq=[],this.map={}}setValue(t,i,r){const l=this.seq;for(let u=0,f=l.length;u!==f;++u){const p=l[u];p.setValue(t,i[p.id],r)}}}const Zh=/(\w+)(\])?(\[|\.)?/g;function k0(s,t){s.seq.push(t),s.map[t.id]=t}function wA(s,t,i){const r=s.name,l=r.length;for(Zh.lastIndex=0;;){const u=Zh.exec(r),f=Zh.lastIndex;let p=u[1];const m=u[2]==="]",d=u[3];if(m&&(p=p|0),d===void 0||d==="["&&f+2===l){k0(i,d===void 0?new AA(p,s,t):new RA(p,s,t));break}else{let v=i.map[p];v===void 0&&(v=new CA(p),k0(i,v)),i=v}}}class Zu{constructor(t,i){this.seq=[],this.map={};const r=t.getProgramParameter(i,t.ACTIVE_UNIFORMS);for(let f=0;f<r;++f){const p=t.getActiveUniform(i,f),m=t.getUniformLocation(i,p.name);wA(p,m,this)}const l=[],u=[];for(const f of this.seq)f.type===t.SAMPLER_2D_SHADOW||f.type===t.SAMPLER_CUBE_SHADOW||f.type===t.SAMPLER_2D_ARRAY_SHADOW?l.push(f):u.push(f);l.length>0&&(this.seq=l.concat(u))}setValue(t,i,r,l){const u=this.map[i];u!==void 0&&u.setValue(t,r,l)}setOptional(t,i,r){const l=i[r];l!==void 0&&this.setValue(t,r,l)}static upload(t,i,r,l){for(let u=0,f=i.length;u!==f;++u){const p=i[u],m=r[p.id];m.needsUpdate!==!1&&p.setValue(t,m.value,l)}}static seqWithValue(t,i){const r=[];for(let l=0,u=t.length;l!==u;++l){const f=t[l];f.id in i&&r.push(f)}return r}}function X0(s,t,i){const r=s.createShader(t);return s.shaderSource(r,i),s.compileShader(r),r}const DA=37297;let UA=0;function LA(s,t){const i=s.split(`
`),r=[],l=Math.max(t-6,0),u=Math.min(t+6,i.length);for(let f=l;f<u;f++){const p=f+1;r.push(`${p===t?">":" "} ${p}: ${i[f]}`)}return r.join(`
`)}const W0=new re;function NA(s){Ee._getMatrix(W0,Ee.workingColorSpace,s);const t=`mat3( ${W0.elements.map(i=>i.toFixed(4))} )`;switch(Ee.getTransfer(s)){case $u:return[t,"LinearTransferOETF"];case Fe:return[t,"sRGBTransferOETF"];default:return te("WebGLProgram: Unsupported color space: ",s),[t,"LinearTransferOETF"]}}function q0(s,t,i){const r=s.getShaderParameter(t,s.COMPILE_STATUS),u=(s.getShaderInfoLog(t)||"").trim();if(r&&u==="")return"";const f=/ERROR: 0:(\d+)/.exec(u);if(f){const p=parseInt(f[1]);return i.toUpperCase()+`

`+u+`

`+LA(s.getShaderSource(t),p)}else return u}function OA(s,t){const i=NA(t);return[`vec4 ${s}( vec4 value ) {`,`	return ${i[1]}( vec4( value.rgb * ${i[0]}, value.a ) );`,"}"].join(`
`)}const PA={[dv]:"Linear",[pv]:"Reinhard",[mv]:"Cineon",[gv]:"ACESFilmic",[vv]:"AgX",[xv]:"Neutral",[_v]:"Custom"};function IA(s,t){const i=PA[t];return i===void 0?(te("WebGLProgram: Unsupported toneMapping:",t),"vec3 "+s+"( vec3 color ) { return LinearToneMapping( color ); }"):"vec3 "+s+"( vec3 color ) { return "+i+"ToneMapping( color ); }"}const Hu=new $;function FA(){Ee.getLuminanceCoefficients(Hu);const s=Hu.x.toFixed(4),t=Hu.y.toFixed(4),i=Hu.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${s}, ${t}, ${i} );`,"	return dot( weights, rgb );","}"].join(`
`)}function zA(s){return[s.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",s.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(nl).join(`
`)}function BA(s){const t=[];for(const i in s){const r=s[i];r!==!1&&t.push("#define "+i+" "+r)}return t.join(`
`)}function HA(s,t){const i={},r=s.getProgramParameter(t,s.ACTIVE_ATTRIBUTES);for(let l=0;l<r;l++){const u=s.getActiveAttrib(t,l),f=u.name;let p=1;u.type===s.FLOAT_MAT2&&(p=2),u.type===s.FLOAT_MAT3&&(p=3),u.type===s.FLOAT_MAT4&&(p=4),i[f]={type:u.type,location:s.getAttribLocation(t,f),locationSize:p}}return i}function nl(s){return s!==""}function Y0(s,t){const i=t.numSpotLightShadows+t.numSpotLightMaps-t.numSpotLightShadowsWithMaps;return s.replace(/NUM_DIR_LIGHTS/g,t.numDirLights).replace(/NUM_SPOT_LIGHTS/g,t.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,t.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,i).replace(/NUM_RECT_AREA_LIGHTS/g,t.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,t.numPointLights).replace(/NUM_HEMI_LIGHTS/g,t.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,t.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,t.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,t.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,t.numPointLightShadows)}function Z0(s,t){return s.replace(/NUM_CLIPPING_PLANES/g,t.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,t.numClippingPlanes-t.numClipIntersection)}const GA=/^[ \t]*#include +<([\w\d./]+)>/gm;function Gd(s){return s.replace(GA,kA)}const VA=new Map;function kA(s,t){let i=ue[t];if(i===void 0){const r=VA.get(t);if(r!==void 0)i=ue[r],te('WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',t,r);else throw new Error("THREE.WebGLProgram: Can not resolve #include <"+t+">")}return Gd(i)}const XA=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function K0(s){return s.replace(XA,WA)}function WA(s,t,i,r){let l="";for(let u=parseInt(t);u<parseInt(i);u++)l+=r.replace(/\[\s*i\s*\]/g,"[ "+u+" ]").replace(/UNROLLED_LOOP_INDEX/g,u);return l}function Q0(s){let t=`precision ${s.precision} float;
	precision ${s.precision} int;
	precision ${s.precision} sampler2D;
	precision ${s.precision} samplerCube;
	precision ${s.precision} sampler3D;
	precision ${s.precision} sampler2DArray;
	precision ${s.precision} sampler2DShadow;
	precision ${s.precision} samplerCubeShadow;
	precision ${s.precision} sampler2DArrayShadow;
	precision ${s.precision} isampler2D;
	precision ${s.precision} isampler3D;
	precision ${s.precision} isamplerCube;
	precision ${s.precision} isampler2DArray;
	precision ${s.precision} usampler2D;
	precision ${s.precision} usampler3D;
	precision ${s.precision} usamplerCube;
	precision ${s.precision} usampler2DArray;
	`;return s.precision==="highp"?t+=`
#define HIGH_PRECISION`:s.precision==="mediump"?t+=`
#define MEDIUM_PRECISION`:s.precision==="lowp"&&(t+=`
#define LOW_PRECISION`),t}const qA={[Vu]:"SHADOWMAP_TYPE_PCF",[tl]:"SHADOWMAP_TYPE_VSM"};function YA(s){return qA[s.shadowMapType]||"SHADOWMAP_TYPE_BASIC"}const ZA={[Yr]:"ENVMAP_TYPE_CUBE",[Ys]:"ENVMAP_TYPE_CUBE",[nc]:"ENVMAP_TYPE_CUBE_UV"};function KA(s){return s.envMap===!1?"ENVMAP_TYPE_CUBE":ZA[s.envMapMode]||"ENVMAP_TYPE_CUBE"}const QA={[Ys]:"ENVMAP_MODE_REFRACTION"};function JA(s){return s.envMap===!1?"ENVMAP_MODE_REFLECTION":QA[s.envMapMode]||"ENVMAP_MODE_REFLECTION"}const jA={[hv]:"ENVMAP_BLENDING_MULTIPLY",[Uy]:"ENVMAP_BLENDING_MIX",[Ly]:"ENVMAP_BLENDING_ADD"};function $A(s){return s.envMap===!1?"ENVMAP_BLENDING_NONE":jA[s.combine]||"ENVMAP_BLENDING_NONE"}function t1(s){const t=s.envMapCubeUVHeight;if(t===null)return null;const i=Math.log2(t)-2,r=1/t;return{texelWidth:1/(3*Math.max(Math.pow(2,i),112)),texelHeight:r,maxMip:i}}function e1(s,t,i,r){const l=s.getContext(),u=i.defines;let f=i.vertexShader,p=i.fragmentShader;const m=YA(i),d=KA(i),g=JA(i),v=$A(i),_=t1(i),M=zA(i),T=BA(u),w=l.createProgram();let E,S,F=i.glslVersion?"#version "+i.glslVersion+`
`:"";i.isRawShaderMaterial?(E=["#define SHADER_TYPE "+i.shaderType,"#define SHADER_NAME "+i.shaderName,T].filter(nl).join(`
`),E.length>0&&(E+=`
`),S=["#define SHADER_TYPE "+i.shaderType,"#define SHADER_NAME "+i.shaderName,T].filter(nl).join(`
`),S.length>0&&(S+=`
`)):(E=[Q0(i),"#define SHADER_TYPE "+i.shaderType,"#define SHADER_NAME "+i.shaderName,T,i.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",i.batching?"#define USE_BATCHING":"",i.batchingColor?"#define USE_BATCHING_COLOR":"",i.instancing?"#define USE_INSTANCING":"",i.instancingColor?"#define USE_INSTANCING_COLOR":"",i.instancingMorph?"#define USE_INSTANCING_MORPH":"",i.useFog&&i.fog?"#define USE_FOG":"",i.useFog&&i.fogExp2?"#define FOG_EXP2":"",i.map?"#define USE_MAP":"",i.envMap?"#define USE_ENVMAP":"",i.envMap?"#define "+g:"",i.lightMap?"#define USE_LIGHTMAP":"",i.aoMap?"#define USE_AOMAP":"",i.bumpMap?"#define USE_BUMPMAP":"",i.normalMap?"#define USE_NORMALMAP":"",i.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",i.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",i.displacementMap?"#define USE_DISPLACEMENTMAP":"",i.emissiveMap?"#define USE_EMISSIVEMAP":"",i.anisotropy?"#define USE_ANISOTROPY":"",i.anisotropyMap?"#define USE_ANISOTROPYMAP":"",i.clearcoatMap?"#define USE_CLEARCOATMAP":"",i.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",i.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",i.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",i.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",i.specularMap?"#define USE_SPECULARMAP":"",i.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",i.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",i.roughnessMap?"#define USE_ROUGHNESSMAP":"",i.metalnessMap?"#define USE_METALNESSMAP":"",i.alphaMap?"#define USE_ALPHAMAP":"",i.alphaHash?"#define USE_ALPHAHASH":"",i.transmission?"#define USE_TRANSMISSION":"",i.transmissionMap?"#define USE_TRANSMISSIONMAP":"",i.thicknessMap?"#define USE_THICKNESSMAP":"",i.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",i.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",i.mapUv?"#define MAP_UV "+i.mapUv:"",i.alphaMapUv?"#define ALPHAMAP_UV "+i.alphaMapUv:"",i.lightMapUv?"#define LIGHTMAP_UV "+i.lightMapUv:"",i.aoMapUv?"#define AOMAP_UV "+i.aoMapUv:"",i.emissiveMapUv?"#define EMISSIVEMAP_UV "+i.emissiveMapUv:"",i.bumpMapUv?"#define BUMPMAP_UV "+i.bumpMapUv:"",i.normalMapUv?"#define NORMALMAP_UV "+i.normalMapUv:"",i.displacementMapUv?"#define DISPLACEMENTMAP_UV "+i.displacementMapUv:"",i.metalnessMapUv?"#define METALNESSMAP_UV "+i.metalnessMapUv:"",i.roughnessMapUv?"#define ROUGHNESSMAP_UV "+i.roughnessMapUv:"",i.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+i.anisotropyMapUv:"",i.clearcoatMapUv?"#define CLEARCOATMAP_UV "+i.clearcoatMapUv:"",i.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+i.clearcoatNormalMapUv:"",i.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+i.clearcoatRoughnessMapUv:"",i.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+i.iridescenceMapUv:"",i.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+i.iridescenceThicknessMapUv:"",i.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+i.sheenColorMapUv:"",i.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+i.sheenRoughnessMapUv:"",i.specularMapUv?"#define SPECULARMAP_UV "+i.specularMapUv:"",i.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+i.specularColorMapUv:"",i.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+i.specularIntensityMapUv:"",i.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+i.transmissionMapUv:"",i.thicknessMapUv?"#define THICKNESSMAP_UV "+i.thicknessMapUv:"",i.vertexTangents&&i.flatShading===!1?"#define USE_TANGENT":"",i.vertexNormals?"#define HAS_NORMAL":"",i.vertexColors?"#define USE_COLOR":"",i.vertexAlphas?"#define USE_COLOR_ALPHA":"",i.vertexUv1s?"#define USE_UV1":"",i.vertexUv2s?"#define USE_UV2":"",i.vertexUv3s?"#define USE_UV3":"",i.pointsUvs?"#define USE_POINTS_UV":"",i.flatShading?"#define FLAT_SHADED":"",i.skinning?"#define USE_SKINNING":"",i.morphTargets?"#define USE_MORPHTARGETS":"",i.morphNormals&&i.flatShading===!1?"#define USE_MORPHNORMALS":"",i.morphColors?"#define USE_MORPHCOLORS":"",i.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+i.morphTextureStride:"",i.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+i.morphTargetsCount:"",i.doubleSided?"#define DOUBLE_SIDED":"",i.flipSided?"#define FLIP_SIDED":"",i.shadowMapEnabled?"#define USE_SHADOWMAP":"",i.shadowMapEnabled?"#define "+m:"",i.sizeAttenuation?"#define USE_SIZEATTENUATION":"",i.numLightProbes>0?"#define USE_LIGHT_PROBES":"",i.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",i.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(nl).join(`
`),S=[Q0(i),"#define SHADER_TYPE "+i.shaderType,"#define SHADER_NAME "+i.shaderName,T,i.useFog&&i.fog?"#define USE_FOG":"",i.useFog&&i.fogExp2?"#define FOG_EXP2":"",i.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",i.map?"#define USE_MAP":"",i.matcap?"#define USE_MATCAP":"",i.envMap?"#define USE_ENVMAP":"",i.envMap?"#define "+d:"",i.envMap?"#define "+g:"",i.envMap?"#define "+v:"",_?"#define CUBEUV_TEXEL_WIDTH "+_.texelWidth:"",_?"#define CUBEUV_TEXEL_HEIGHT "+_.texelHeight:"",_?"#define CUBEUV_MAX_MIP "+_.maxMip+".0":"",i.lightMap?"#define USE_LIGHTMAP":"",i.aoMap?"#define USE_AOMAP":"",i.bumpMap?"#define USE_BUMPMAP":"",i.normalMap?"#define USE_NORMALMAP":"",i.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",i.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",i.packedNormalMap?"#define USE_PACKED_NORMALMAP":"",i.emissiveMap?"#define USE_EMISSIVEMAP":"",i.anisotropy?"#define USE_ANISOTROPY":"",i.anisotropyMap?"#define USE_ANISOTROPYMAP":"",i.clearcoat?"#define USE_CLEARCOAT":"",i.clearcoatMap?"#define USE_CLEARCOATMAP":"",i.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",i.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",i.dispersion?"#define USE_DISPERSION":"",i.iridescence?"#define USE_IRIDESCENCE":"",i.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",i.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",i.specularMap?"#define USE_SPECULARMAP":"",i.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",i.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",i.roughnessMap?"#define USE_ROUGHNESSMAP":"",i.metalnessMap?"#define USE_METALNESSMAP":"",i.alphaMap?"#define USE_ALPHAMAP":"",i.alphaTest?"#define USE_ALPHATEST":"",i.alphaHash?"#define USE_ALPHAHASH":"",i.sheen?"#define USE_SHEEN":"",i.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",i.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",i.transmission?"#define USE_TRANSMISSION":"",i.transmissionMap?"#define USE_TRANSMISSIONMAP":"",i.thicknessMap?"#define USE_THICKNESSMAP":"",i.vertexTangents&&i.flatShading===!1?"#define USE_TANGENT":"",i.vertexColors||i.instancingColor?"#define USE_COLOR":"",i.vertexAlphas||i.batchingColor?"#define USE_COLOR_ALPHA":"",i.vertexUv1s?"#define USE_UV1":"",i.vertexUv2s?"#define USE_UV2":"",i.vertexUv3s?"#define USE_UV3":"",i.pointsUvs?"#define USE_POINTS_UV":"",i.gradientMap?"#define USE_GRADIENTMAP":"",i.flatShading?"#define FLAT_SHADED":"",i.doubleSided?"#define DOUBLE_SIDED":"",i.flipSided?"#define FLIP_SIDED":"",i.shadowMapEnabled?"#define USE_SHADOWMAP":"",i.shadowMapEnabled?"#define "+m:"",i.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",i.numLightProbes>0?"#define USE_LIGHT_PROBES":"",i.numLightProbeGrids>0?"#define USE_LIGHT_PROBES_GRID":"",i.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",i.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",i.logarithmicDepthBuffer?"#define USE_LOGARITHMIC_DEPTH_BUFFER":"",i.reversedDepthBuffer?"#define USE_REVERSED_DEPTH_BUFFER":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",i.toneMapping!==Yi?"#define TONE_MAPPING":"",i.toneMapping!==Yi?ue.tonemapping_pars_fragment:"",i.toneMapping!==Yi?IA("toneMapping",i.toneMapping):"",i.dithering?"#define DITHERING":"",i.opaque?"#define OPAQUE":"",ue.colorspace_pars_fragment,OA("linearToOutputTexel",i.outputColorSpace),FA(),i.useDepthPacking?"#define DEPTH_PACKING "+i.depthPacking:"",`
`].filter(nl).join(`
`)),f=Gd(f),f=Y0(f,i),f=Z0(f,i),p=Gd(p),p=Y0(p,i),p=Z0(p,i),f=K0(f),p=K0(p),i.isRawShaderMaterial!==!0&&(F=`#version 300 es
`,E=[M,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+E,S=["#define varying in",i.glslVersion===r0?"":"layout(location = 0) out highp vec4 pc_fragColor;",i.glslVersion===r0?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+S);const z=F+E+f,C=F+S+p,N=X0(l,l.VERTEX_SHADER,z),D=X0(l,l.FRAGMENT_SHADER,C);l.attachShader(w,N),l.attachShader(w,D),i.index0AttributeName!==void 0?l.bindAttribLocation(w,0,i.index0AttributeName):i.hasPositionAttribute===!0&&l.bindAttribLocation(w,0,"position"),l.linkProgram(w);function O(G){if(s.debug.checkShaderErrors){const Z=l.getProgramInfoLog(w)||"",ht=l.getShaderInfoLog(N)||"",mt=l.getShaderInfoLog(D)||"",J=Z.trim(),I=ht.trim(),H=mt.trim();let j=!0,gt=!0;if(l.getProgramParameter(w,l.LINK_STATUS)===!1)if(j=!1,typeof s.debug.onShaderError=="function")s.debug.onShaderError(l,w,N,D);else{const Et=q0(l,N,"vertex"),L=q0(l,D,"fragment");be("WebGLProgram: Shader Error "+l.getError()+" - VALIDATE_STATUS "+l.getProgramParameter(w,l.VALIDATE_STATUS)+`

Material Name: `+G.name+`
Material Type: `+G.type+`

Program Info Log: `+J+`
`+Et+`
`+L)}else J!==""?te("WebGLProgram: Program Info Log:",J):(I===""||H==="")&&(gt=!1);gt&&(G.diagnostics={runnable:j,programLog:J,vertexShader:{log:I,prefix:E},fragmentShader:{log:H,prefix:S}})}l.deleteShader(N),l.deleteShader(D),b=new Zu(l,w),P=HA(l,w)}let b;this.getUniforms=function(){return b===void 0&&O(this),b};let P;this.getAttributes=function(){return P===void 0&&O(this),P};let q=i.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return q===!1&&(q=l.getProgramParameter(w,DA)),q},this.destroy=function(){r.releaseStatesOfProgram(this),l.deleteProgram(w),this.program=void 0},this.type=i.shaderType,this.name=i.shaderName,this.id=UA++,this.cacheKey=t,this.usedTimes=1,this.program=w,this.vertexShader=N,this.fragmentShader=D,this}let n1=0;class i1{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(t,i,r){const l=this._getShaderCacheForMaterial(t);return l.has(i)===!1&&(l.add(i),i.usedTimes++),l.has(r)===!1&&(l.add(r),r.usedTimes++),this}remove(t){const i=this.materialCache.get(t);for(const r of i)r.usedTimes--,r.usedTimes===0&&this.shaderCache.delete(r.code);return this.materialCache.delete(t),this}getVertexShaderStage(t){return this._getShaderStage(t.vertexShader)}getFragmentShaderStage(t){return this._getShaderStage(t.fragmentShader)}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(t){const i=this.materialCache;let r=i.get(t);return r===void 0&&(r=new Set,i.set(t,r)),r}_getShaderStage(t){const i=this.shaderCache;let r=i.get(t);return r===void 0&&(r=new a1(t),i.set(t,r)),r}}class a1{constructor(t){this.id=n1++,this.code=t,this.usedTimes=0}}function r1(s){return s===Zr||s===Ku||s===Qu}function s1(s,t,i,r,l,u){const f=new Dv,p=new i1,m=new Set,d=[],g=new Map,v=r.logarithmicDepthBuffer;let _=r.precision;const M={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distance",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function T(b){return m.add(b),b===0?"uv":`uv${b}`}function w(b,P,q,G,Z,ht){const mt=G.fog,J=Z.geometry,I=b.isMeshStandardMaterial||b.isMeshLambertMaterial||b.isMeshPhongMaterial?G.environment:null,H=b.isMeshStandardMaterial||b.isMeshLambertMaterial&&!b.envMap||b.isMeshPhongMaterial&&!b.envMap,j=t.get(b.envMap||I,H),gt=j&&j.mapping===nc?j.image.height:null,Et=M[b.type];b.precision!==null&&(_=r.getMaxPrecision(b.precision),_!==b.precision&&te("WebGLProgram.getParameters:",b.precision,"not supported, using",_,"instead."));const L=J.morphAttributes.position||J.morphAttributes.normal||J.morphAttributes.color,K=L!==void 0?L.length:0;let Mt=0;J.morphAttributes.position!==void 0&&(Mt=1),J.morphAttributes.normal!==void 0&&(Mt=2),J.morphAttributes.color!==void 0&&(Mt=3);let Rt,Pt,at,xt;if(Et){const Gt=Xi[Et];Rt=Gt.vertexShader,Pt=Gt.fragmentShader}else{Rt=b.vertexShader,Pt=b.fragmentShader;const Gt=p.getVertexShaderStage(b),Ke=p.getFragmentShaderStage(b);p.update(b,Gt,Ke),at=Gt.id,xt=Ke.id}const yt=s.getRenderTarget(),Bt=s.state.buffers.depth.getReversed(),ee=Z.isInstancedMesh===!0,Kt=Z.isBatchedMesh===!0,qe=!!b.map,ce=!!b.matcap,Se=!!j,ye=!!b.aoMap,fe=!!b.lightMap,en=!!b.bumpMap&&b.wireframe===!1,nn=!!b.normalMap,an=!!b.displacementMap,ln=!!b.emissiveMap,We=!!b.metalnessMap,rn=!!b.roughnessMap,W=b.anisotropy>0,ze=b.clearcoat>0,Ce=b.dispersion>0,U=b.iridescence>0,y=b.sheen>0,Q=b.transmission>0,rt=W&&!!b.anisotropyMap,ct=ze&&!!b.clearcoatMap,bt=ze&&!!b.clearcoatNormalMap,wt=ze&&!!b.clearcoatRoughnessMap,ut=U&&!!b.iridescenceMap,ft=U&&!!b.iridescenceThicknessMap,At=y&&!!b.sheenColorMap,Ft=y&&!!b.sheenRoughnessMap,Lt=!!b.specularMap,Dt=!!b.specularColorMap,Zt=!!b.specularIntensityMap,Qt=Q&&!!b.transmissionMap,ne=Q&&!!b.thicknessMap,k=!!b.gradientMap,Tt=!!b.alphaMap,pt=b.alphaTest>0,Ct=!!b.alphaHash,It=!!b.extensions;let St=Yi;b.toneMapped&&(yt===null||yt.isXRRenderTarget===!0)&&(St=s.toneMapping);const Wt={shaderID:Et,shaderType:b.type,shaderName:b.name,vertexShader:Rt,fragmentShader:Pt,defines:b.defines,customVertexShaderID:at,customFragmentShaderID:xt,isRawShaderMaterial:b.isRawShaderMaterial===!0,glslVersion:b.glslVersion,precision:_,batching:Kt,batchingColor:Kt&&Z._colorsTexture!==null,instancing:ee,instancingColor:ee&&Z.instanceColor!==null,instancingMorph:ee&&Z.morphTexture!==null,outputColorSpace:yt===null?s.outputColorSpace:yt.isXRRenderTarget===!0?yt.texture.colorSpace:Ee.workingColorSpace,alphaToCoverage:!!b.alphaToCoverage,map:qe,matcap:ce,envMap:Se,envMapMode:Se&&j.mapping,envMapCubeUVHeight:gt,aoMap:ye,lightMap:fe,bumpMap:en,normalMap:nn,displacementMap:an,emissiveMap:ln,normalMapObjectSpace:nn&&b.normalMapType===Py,normalMapTangentSpace:nn&&b.normalMapType===Ju,packedNormalMap:nn&&b.normalMapType===Ju&&r1(b.normalMap.format),metalnessMap:We,roughnessMap:rn,anisotropy:W,anisotropyMap:rt,clearcoat:ze,clearcoatMap:ct,clearcoatNormalMap:bt,clearcoatRoughnessMap:wt,dispersion:Ce,iridescence:U,iridescenceMap:ut,iridescenceThicknessMap:ft,sheen:y,sheenColorMap:At,sheenRoughnessMap:Ft,specularMap:Lt,specularColorMap:Dt,specularIntensityMap:Zt,transmission:Q,transmissionMap:Qt,thicknessMap:ne,gradientMap:k,opaque:b.transparent===!1&&b.blending===ks&&b.alphaToCoverage===!1,alphaMap:Tt,alphaTest:pt,alphaHash:Ct,combine:b.combine,mapUv:qe&&T(b.map.channel),aoMapUv:ye&&T(b.aoMap.channel),lightMapUv:fe&&T(b.lightMap.channel),bumpMapUv:en&&T(b.bumpMap.channel),normalMapUv:nn&&T(b.normalMap.channel),displacementMapUv:an&&T(b.displacementMap.channel),emissiveMapUv:ln&&T(b.emissiveMap.channel),metalnessMapUv:We&&T(b.metalnessMap.channel),roughnessMapUv:rn&&T(b.roughnessMap.channel),anisotropyMapUv:rt&&T(b.anisotropyMap.channel),clearcoatMapUv:ct&&T(b.clearcoatMap.channel),clearcoatNormalMapUv:bt&&T(b.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:wt&&T(b.clearcoatRoughnessMap.channel),iridescenceMapUv:ut&&T(b.iridescenceMap.channel),iridescenceThicknessMapUv:ft&&T(b.iridescenceThicknessMap.channel),sheenColorMapUv:At&&T(b.sheenColorMap.channel),sheenRoughnessMapUv:Ft&&T(b.sheenRoughnessMap.channel),specularMapUv:Lt&&T(b.specularMap.channel),specularColorMapUv:Dt&&T(b.specularColorMap.channel),specularIntensityMapUv:Zt&&T(b.specularIntensityMap.channel),transmissionMapUv:Qt&&T(b.transmissionMap.channel),thicknessMapUv:ne&&T(b.thicknessMap.channel),alphaMapUv:Tt&&T(b.alphaMap.channel),vertexTangents:!!J.attributes.tangent&&(nn||W),vertexNormals:!!J.attributes.normal,vertexColors:b.vertexColors,vertexAlphas:b.vertexColors===!0&&!!J.attributes.color&&J.attributes.color.itemSize===4,pointsUvs:Z.isPoints===!0&&!!J.attributes.uv&&(qe||Tt),fog:!!mt,useFog:b.fog===!0,fogExp2:!!mt&&mt.isFogExp2,flatShading:b.wireframe===!1&&(b.flatShading===!0||J.attributes.normal===void 0&&nn===!1&&(b.isMeshLambertMaterial||b.isMeshPhongMaterial||b.isMeshStandardMaterial||b.isMeshPhysicalMaterial)),sizeAttenuation:b.sizeAttenuation===!0,logarithmicDepthBuffer:v,reversedDepthBuffer:Bt,skinning:Z.isSkinnedMesh===!0,hasPositionAttribute:J.attributes.position!==void 0,morphTargets:J.morphAttributes.position!==void 0,morphNormals:J.morphAttributes.normal!==void 0,morphColors:J.morphAttributes.color!==void 0,morphTargetsCount:K,morphTextureStride:Mt,numDirLights:P.directional.length,numPointLights:P.point.length,numSpotLights:P.spot.length,numSpotLightMaps:P.spotLightMap.length,numRectAreaLights:P.rectArea.length,numHemiLights:P.hemi.length,numDirLightShadows:P.directionalShadowMap.length,numPointLightShadows:P.pointShadowMap.length,numSpotLightShadows:P.spotShadowMap.length,numSpotLightShadowsWithMaps:P.numSpotLightShadowsWithMaps,numLightProbes:P.numLightProbes,numLightProbeGrids:ht.length,numClippingPlanes:u.numPlanes,numClipIntersection:u.numIntersection,dithering:b.dithering,shadowMapEnabled:s.shadowMap.enabled&&q.length>0,shadowMapType:s.shadowMap.type,toneMapping:St,decodeVideoTexture:qe&&b.map.isVideoTexture===!0&&Ee.getTransfer(b.map.colorSpace)===Fe,decodeVideoTextureEmissive:ln&&b.emissiveMap.isVideoTexture===!0&&Ee.getTransfer(b.emissiveMap.colorSpace)===Fe,premultipliedAlpha:b.premultipliedAlpha,doubleSided:b.side===Ea,flipSided:b.side===Qn,useDepthPacking:b.depthPacking>=0,depthPacking:b.depthPacking||0,index0AttributeName:b.index0AttributeName,extensionClipCullDistance:It&&b.extensions.clipCullDistance===!0&&i.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(It&&b.extensions.multiDraw===!0||Kt)&&i.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:i.has("KHR_parallel_shader_compile"),customProgramCacheKey:b.customProgramCacheKey()};return Wt.vertexUv1s=m.has(1),Wt.vertexUv2s=m.has(2),Wt.vertexUv3s=m.has(3),m.clear(),Wt}function E(b){const P=[];if(b.shaderID?P.push(b.shaderID):(P.push(b.customVertexShaderID),P.push(b.customFragmentShaderID)),b.defines!==void 0)for(const q in b.defines)P.push(q),P.push(b.defines[q]);return b.isRawShaderMaterial===!1&&(S(P,b),F(P,b),P.push(s.outputColorSpace)),P.push(b.customProgramCacheKey),P.join()}function S(b,P){b.push(P.precision),b.push(P.outputColorSpace),b.push(P.envMapMode),b.push(P.envMapCubeUVHeight),b.push(P.mapUv),b.push(P.alphaMapUv),b.push(P.lightMapUv),b.push(P.aoMapUv),b.push(P.bumpMapUv),b.push(P.normalMapUv),b.push(P.displacementMapUv),b.push(P.emissiveMapUv),b.push(P.metalnessMapUv),b.push(P.roughnessMapUv),b.push(P.anisotropyMapUv),b.push(P.clearcoatMapUv),b.push(P.clearcoatNormalMapUv),b.push(P.clearcoatRoughnessMapUv),b.push(P.iridescenceMapUv),b.push(P.iridescenceThicknessMapUv),b.push(P.sheenColorMapUv),b.push(P.sheenRoughnessMapUv),b.push(P.specularMapUv),b.push(P.specularColorMapUv),b.push(P.specularIntensityMapUv),b.push(P.transmissionMapUv),b.push(P.thicknessMapUv),b.push(P.combine),b.push(P.fogExp2),b.push(P.sizeAttenuation),b.push(P.morphTargetsCount),b.push(P.morphAttributeCount),b.push(P.numDirLights),b.push(P.numPointLights),b.push(P.numSpotLights),b.push(P.numSpotLightMaps),b.push(P.numHemiLights),b.push(P.numRectAreaLights),b.push(P.numDirLightShadows),b.push(P.numPointLightShadows),b.push(P.numSpotLightShadows),b.push(P.numSpotLightShadowsWithMaps),b.push(P.numLightProbes),b.push(P.shadowMapType),b.push(P.toneMapping),b.push(P.numClippingPlanes),b.push(P.numClipIntersection),b.push(P.depthPacking)}function F(b,P){f.disableAll(),P.instancing&&f.enable(0),P.instancingColor&&f.enable(1),P.instancingMorph&&f.enable(2),P.matcap&&f.enable(3),P.envMap&&f.enable(4),P.normalMapObjectSpace&&f.enable(5),P.normalMapTangentSpace&&f.enable(6),P.clearcoat&&f.enable(7),P.iridescence&&f.enable(8),P.alphaTest&&f.enable(9),P.vertexColors&&f.enable(10),P.vertexAlphas&&f.enable(11),P.vertexUv1s&&f.enable(12),P.vertexUv2s&&f.enable(13),P.vertexUv3s&&f.enable(14),P.vertexTangents&&f.enable(15),P.anisotropy&&f.enable(16),P.alphaHash&&f.enable(17),P.batching&&f.enable(18),P.dispersion&&f.enable(19),P.batchingColor&&f.enable(20),P.gradientMap&&f.enable(21),P.packedNormalMap&&f.enable(22),P.vertexNormals&&f.enable(23),b.push(f.mask),f.disableAll(),P.fog&&f.enable(0),P.useFog&&f.enable(1),P.flatShading&&f.enable(2),P.logarithmicDepthBuffer&&f.enable(3),P.reversedDepthBuffer&&f.enable(4),P.skinning&&f.enable(5),P.morphTargets&&f.enable(6),P.morphNormals&&f.enable(7),P.morphColors&&f.enable(8),P.premultipliedAlpha&&f.enable(9),P.shadowMapEnabled&&f.enable(10),P.doubleSided&&f.enable(11),P.flipSided&&f.enable(12),P.useDepthPacking&&f.enable(13),P.dithering&&f.enable(14),P.transmission&&f.enable(15),P.sheen&&f.enable(16),P.opaque&&f.enable(17),P.pointsUvs&&f.enable(18),P.decodeVideoTexture&&f.enable(19),P.decodeVideoTextureEmissive&&f.enable(20),P.alphaToCoverage&&f.enable(21),P.numLightProbeGrids>0&&f.enable(22),P.hasPositionAttribute&&f.enable(23),b.push(f.mask)}function z(b){const P=M[b.type];let q;if(P){const G=Xi[P];q=xM.clone(G.uniforms)}else q=b.uniforms;return q}function C(b,P){let q=g.get(P);return q!==void 0?++q.usedTimes:(q=new e1(s,P,b,l),d.push(q),g.set(P,q)),q}function N(b){if(--b.usedTimes===0){const P=d.indexOf(b);d[P]=d[d.length-1],d.pop(),g.delete(b.cacheKey),b.destroy()}}function D(b){p.remove(b)}function O(){p.dispose()}return{getParameters:w,getProgramCacheKey:E,getUniforms:z,acquireProgram:C,releaseProgram:N,releaseShaderCache:D,programs:d,dispose:O}}function o1(){let s=new WeakMap;function t(f){return s.has(f)}function i(f){let p=s.get(f);return p===void 0&&(p={},s.set(f,p)),p}function r(f){s.delete(f)}function l(f,p,m){s.get(f)[p]=m}function u(){s=new WeakMap}return{has:t,get:i,remove:r,update:l,dispose:u}}function l1(s,t){return s.groupOrder!==t.groupOrder?s.groupOrder-t.groupOrder:s.renderOrder!==t.renderOrder?s.renderOrder-t.renderOrder:s.material.id!==t.material.id?s.material.id-t.material.id:s.materialVariant!==t.materialVariant?s.materialVariant-t.materialVariant:s.z!==t.z?s.z-t.z:s.id-t.id}function J0(s,t){return s.groupOrder!==t.groupOrder?s.groupOrder-t.groupOrder:s.renderOrder!==t.renderOrder?s.renderOrder-t.renderOrder:s.z!==t.z?t.z-s.z:s.id-t.id}function j0(){const s=[];let t=0;const i=[],r=[],l=[];function u(){t=0,i.length=0,r.length=0,l.length=0}function f(_){let M=0;return _.isInstancedMesh&&(M+=2),_.isSkinnedMesh&&(M+=1),M}function p(_,M,T,w,E,S){let F=s[t];return F===void 0?(F={id:_.id,object:_,geometry:M,material:T,materialVariant:f(_),groupOrder:w,renderOrder:_.renderOrder,z:E,group:S},s[t]=F):(F.id=_.id,F.object=_,F.geometry=M,F.material=T,F.materialVariant=f(_),F.groupOrder=w,F.renderOrder=_.renderOrder,F.z=E,F.group=S),t++,F}function m(_,M,T,w,E,S){const F=p(_,M,T,w,E,S);T.transmission>0?r.push(F):T.transparent===!0?l.push(F):i.push(F)}function d(_,M,T,w,E,S){const F=p(_,M,T,w,E,S);T.transmission>0?r.unshift(F):T.transparent===!0?l.unshift(F):i.unshift(F)}function g(_,M,T){i.length>1&&i.sort(_||l1),r.length>1&&r.sort(M||J0),l.length>1&&l.sort(M||J0),T&&(i.reverse(),r.reverse(),l.reverse())}function v(){for(let _=t,M=s.length;_<M;_++){const T=s[_];if(T.id===null)break;T.id=null,T.object=null,T.geometry=null,T.material=null,T.group=null}}return{opaque:i,transmissive:r,transparent:l,init:u,push:m,unshift:d,finish:v,sort:g}}function u1(){let s=new WeakMap;function t(r,l){const u=s.get(r);let f;return u===void 0?(f=new j0,s.set(r,[f])):l>=u.length?(f=new j0,u.push(f)):f=u[l],f}function i(){s=new WeakMap}return{get:t,dispose:i}}function c1(){const s={};return{get:function(t){if(s[t.id]!==void 0)return s[t.id];let i;switch(t.type){case"DirectionalLight":i={direction:new $,color:new xe};break;case"SpotLight":i={position:new $,direction:new $,color:new xe,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":i={position:new $,color:new xe,distance:0,decay:0};break;case"HemisphereLight":i={direction:new $,skyColor:new xe,groundColor:new xe};break;case"RectAreaLight":i={color:new xe,position:new $,halfWidth:new $,halfHeight:new $};break}return s[t.id]=i,i}}}function f1(){const s={};return{get:function(t){if(s[t.id]!==void 0)return s[t.id];let i;switch(t.type){case"DirectionalLight":i={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new ie};break;case"SpotLight":i={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new ie};break;case"PointLight":i={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new ie,shadowCameraNear:1,shadowCameraFar:1e3};break}return s[t.id]=i,i}}}let h1=0;function d1(s,t){return(t.castShadow?2:0)-(s.castShadow?2:0)+(t.map?1:0)-(s.map?1:0)}function p1(s){const t=new c1,i=f1(),r={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let d=0;d<9;d++)r.probe.push(new $);const l=new $,u=new $e,f=new $e;function p(d){let g=0,v=0,_=0;for(let P=0;P<9;P++)r.probe[P].set(0,0,0);let M=0,T=0,w=0,E=0,S=0,F=0,z=0,C=0,N=0,D=0,O=0;d.sort(d1);for(let P=0,q=d.length;P<q;P++){const G=d[P],Z=G.color,ht=G.intensity,mt=G.distance;let J=null;if(G.shadow&&G.shadow.map&&(G.shadow.map.texture.format===Zr?J=G.shadow.map.texture:J=G.shadow.map.depthTexture||G.shadow.map.texture),G.isAmbientLight)g+=Z.r*ht,v+=Z.g*ht,_+=Z.b*ht;else if(G.isLightProbe){for(let I=0;I<9;I++)r.probe[I].addScaledVector(G.sh.coefficients[I],ht);O++}else if(G.isDirectionalLight){const I=t.get(G);if(I.color.copy(G.color).multiplyScalar(G.intensity),G.castShadow){const H=G.shadow,j=i.get(G);j.shadowIntensity=H.intensity,j.shadowBias=H.bias,j.shadowNormalBias=H.normalBias,j.shadowRadius=H.radius,j.shadowMapSize=H.mapSize,r.directionalShadow[M]=j,r.directionalShadowMap[M]=J,r.directionalShadowMatrix[M]=G.shadow.matrix,F++}r.directional[M]=I,M++}else if(G.isSpotLight){const I=t.get(G);I.position.setFromMatrixPosition(G.matrixWorld),I.color.copy(Z).multiplyScalar(ht),I.distance=mt,I.coneCos=Math.cos(G.angle),I.penumbraCos=Math.cos(G.angle*(1-G.penumbra)),I.decay=G.decay,r.spot[w]=I;const H=G.shadow;if(G.map&&(r.spotLightMap[N]=G.map,N++,H.updateMatrices(G),G.castShadow&&D++),r.spotLightMatrix[w]=H.matrix,G.castShadow){const j=i.get(G);j.shadowIntensity=H.intensity,j.shadowBias=H.bias,j.shadowNormalBias=H.normalBias,j.shadowRadius=H.radius,j.shadowMapSize=H.mapSize,r.spotShadow[w]=j,r.spotShadowMap[w]=J,C++}w++}else if(G.isRectAreaLight){const I=t.get(G);I.color.copy(Z).multiplyScalar(ht),I.halfWidth.set(G.width*.5,0,0),I.halfHeight.set(0,G.height*.5,0),r.rectArea[E]=I,E++}else if(G.isPointLight){const I=t.get(G);if(I.color.copy(G.color).multiplyScalar(G.intensity),I.distance=G.distance,I.decay=G.decay,G.castShadow){const H=G.shadow,j=i.get(G);j.shadowIntensity=H.intensity,j.shadowBias=H.bias,j.shadowNormalBias=H.normalBias,j.shadowRadius=H.radius,j.shadowMapSize=H.mapSize,j.shadowCameraNear=H.camera.near,j.shadowCameraFar=H.camera.far,r.pointShadow[T]=j,r.pointShadowMap[T]=J,r.pointShadowMatrix[T]=G.shadow.matrix,z++}r.point[T]=I,T++}else if(G.isHemisphereLight){const I=t.get(G);I.skyColor.copy(G.color).multiplyScalar(ht),I.groundColor.copy(G.groundColor).multiplyScalar(ht),r.hemi[S]=I,S++}}E>0&&(s.has("OES_texture_float_linear")===!0?(r.rectAreaLTC1=Ot.LTC_FLOAT_1,r.rectAreaLTC2=Ot.LTC_FLOAT_2):(r.rectAreaLTC1=Ot.LTC_HALF_1,r.rectAreaLTC2=Ot.LTC_HALF_2)),r.ambient[0]=g,r.ambient[1]=v,r.ambient[2]=_;const b=r.hash;(b.directionalLength!==M||b.pointLength!==T||b.spotLength!==w||b.rectAreaLength!==E||b.hemiLength!==S||b.numDirectionalShadows!==F||b.numPointShadows!==z||b.numSpotShadows!==C||b.numSpotMaps!==N||b.numLightProbes!==O)&&(r.directional.length=M,r.spot.length=w,r.rectArea.length=E,r.point.length=T,r.hemi.length=S,r.directionalShadow.length=F,r.directionalShadowMap.length=F,r.pointShadow.length=z,r.pointShadowMap.length=z,r.spotShadow.length=C,r.spotShadowMap.length=C,r.directionalShadowMatrix.length=F,r.pointShadowMatrix.length=z,r.spotLightMatrix.length=C+N-D,r.spotLightMap.length=N,r.numSpotLightShadowsWithMaps=D,r.numLightProbes=O,b.directionalLength=M,b.pointLength=T,b.spotLength=w,b.rectAreaLength=E,b.hemiLength=S,b.numDirectionalShadows=F,b.numPointShadows=z,b.numSpotShadows=C,b.numSpotMaps=N,b.numLightProbes=O,r.version=h1++)}function m(d,g){let v=0,_=0,M=0,T=0,w=0;const E=g.matrixWorldInverse;for(let S=0,F=d.length;S<F;S++){const z=d[S];if(z.isDirectionalLight){const C=r.directional[v];C.direction.setFromMatrixPosition(z.matrixWorld),l.setFromMatrixPosition(z.target.matrixWorld),C.direction.sub(l),C.direction.transformDirection(E),v++}else if(z.isSpotLight){const C=r.spot[M];C.position.setFromMatrixPosition(z.matrixWorld),C.position.applyMatrix4(E),C.direction.setFromMatrixPosition(z.matrixWorld),l.setFromMatrixPosition(z.target.matrixWorld),C.direction.sub(l),C.direction.transformDirection(E),M++}else if(z.isRectAreaLight){const C=r.rectArea[T];C.position.setFromMatrixPosition(z.matrixWorld),C.position.applyMatrix4(E),f.identity(),u.copy(z.matrixWorld),u.premultiply(E),f.extractRotation(u),C.halfWidth.set(z.width*.5,0,0),C.halfHeight.set(0,z.height*.5,0),C.halfWidth.applyMatrix4(f),C.halfHeight.applyMatrix4(f),T++}else if(z.isPointLight){const C=r.point[_];C.position.setFromMatrixPosition(z.matrixWorld),C.position.applyMatrix4(E),_++}else if(z.isHemisphereLight){const C=r.hemi[w];C.direction.setFromMatrixPosition(z.matrixWorld),C.direction.transformDirection(E),w++}}}return{setup:p,setupView:m,state:r}}function $0(s){const t=new p1(s),i=[],r=[],l=[];function u(_){v.camera=_,i.length=0,r.length=0,l.length=0}function f(_){i.push(_)}function p(_){r.push(_)}function m(_){l.push(_)}function d(){t.setup(i)}function g(_){t.setupView(i,_)}const v={lightsArray:i,shadowsArray:r,lightProbeGridArray:l,camera:null,lights:t,transmissionRenderTarget:{},textureUnits:0};return{init:u,state:v,setupLights:d,setupLightsView:g,pushLight:f,pushShadow:p,pushLightProbeGrid:m}}function m1(s){let t=new WeakMap;function i(l,u=0){const f=t.get(l);let p;return f===void 0?(p=new $0(s),t.set(l,[p])):u>=f.length?(p=new $0(s),f.push(p)):p=f[u],p}function r(){t=new WeakMap}return{get:i,dispose:r}}const g1=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,_1=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ).rg;
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ).r;
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( max( 0.0, squared_mean - mean * mean ) );
	gl_FragColor = vec4( mean, std_dev, 0.0, 1.0 );
}`,v1=[new $(1,0,0),new $(-1,0,0),new $(0,1,0),new $(0,-1,0),new $(0,0,1),new $(0,0,-1)],x1=[new $(0,-1,0),new $(0,-1,0),new $(0,0,1),new $(0,0,-1),new $(0,-1,0),new $(0,-1,0)],tv=new $e,jo=new $,Kh=new $;function S1(s,t,i){let r=new ep;const l=new ie,u=new ie,f=new tn,p=new TM,m=new AM,d={},g=i.maxTextureSize,v={[fr]:Qn,[Qn]:fr,[Ea]:Ea},_=new Ji({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new ie},radius:{value:4}},vertexShader:g1,fragmentShader:_1}),M=_.clone();M.defines.HORIZONTAL_PASS=1;const T=new Pi;T.setAttribute("position",new hi(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const w=new Qi(T,_),E=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Vu;let S=this.type;this.render=function(D,O,b){if(E.enabled===!1||E.autoUpdate===!1&&E.needsUpdate===!1||D.length===0)return;this.type===hy&&(te("WebGLShadowMap: PCFSoftShadowMap has been deprecated. Using PCFShadowMap instead."),this.type=Vu);const P=s.getRenderTarget(),q=s.getActiveCubeFace(),G=s.getActiveMipmapLevel(),Z=s.state;Z.setBlending(Ta),Z.buffers.depth.getReversed()===!0?Z.buffers.color.setClear(0,0,0,0):Z.buffers.color.setClear(1,1,1,1),Z.buffers.depth.setTest(!0),Z.setScissorTest(!1);const ht=S!==this.type;ht&&O.traverse(function(mt){mt.material&&(Array.isArray(mt.material)?mt.material.forEach(J=>J.needsUpdate=!0):mt.material.needsUpdate=!0)});for(let mt=0,J=D.length;mt<J;mt++){const I=D[mt],H=I.shadow;if(H===void 0){te("WebGLShadowMap:",I,"has no shadow.");continue}if(H.autoUpdate===!1&&H.needsUpdate===!1)continue;l.copy(H.mapSize);const j=H.getFrameExtents();l.multiply(j),u.copy(H.mapSize),(l.x>g||l.y>g)&&(l.x>g&&(u.x=Math.floor(g/j.x),l.x=u.x*j.x,H.mapSize.x=u.x),l.y>g&&(u.y=Math.floor(g/j.y),l.y=u.y*j.y,H.mapSize.y=u.y));const gt=s.state.buffers.depth.getReversed();if(H.camera._reversedDepth=gt,H.map===null||ht===!0){if(H.map!==null&&(H.map.depthTexture!==null&&(H.map.depthTexture.dispose(),H.map.depthTexture=null),H.map.dispose()),this.type===tl){if(I.isPointLight){te("WebGLShadowMap: VSM shadow maps are not supported for PointLights. Use PCF or BasicShadowMap instead.");continue}H.map=new Zi(l.x,l.y,{format:Zr,type:Ra,minFilter:In,magFilter:In,generateMipmaps:!1}),H.map.texture.name=I.name+".shadowMap",H.map.depthTexture=new Zs(l.x,l.y,Wi),H.map.depthTexture.name=I.name+".shadowMapDepth",H.map.depthTexture.format=Ca,H.map.depthTexture.compareFunction=null,H.map.depthTexture.minFilter=Dn,H.map.depthTexture.magFilter=Dn}else I.isPointLight?(H.map=new kv(l.x),H.map.depthTexture=new _M(l.x,Ki)):(H.map=new Zi(l.x,l.y),H.map.depthTexture=new Zs(l.x,l.y,Ki)),H.map.depthTexture.name=I.name+".shadowMap",H.map.depthTexture.format=Ca,this.type===Vu?(H.map.depthTexture.compareFunction=gt?jd:Jd,H.map.depthTexture.minFilter=In,H.map.depthTexture.magFilter=In):(H.map.depthTexture.compareFunction=null,H.map.depthTexture.minFilter=Dn,H.map.depthTexture.magFilter=Dn);H.camera.updateProjectionMatrix()}const Et=H.map.isWebGLCubeRenderTarget?6:1;for(let L=0;L<Et;L++){if(H.map.isWebGLCubeRenderTarget)s.setRenderTarget(H.map,L),s.clear();else{L===0&&(s.setRenderTarget(H.map),s.clear());const K=H.getViewport(L);f.set(u.x*K.x,u.y*K.y,u.x*K.z,u.y*K.w),Z.viewport(f)}if(I.isPointLight){const K=H.camera,Mt=H.matrix,Rt=I.distance||K.far;Rt!==K.far&&(K.far=Rt,K.updateProjectionMatrix()),jo.setFromMatrixPosition(I.matrixWorld),K.position.copy(jo),Kh.copy(K.position),Kh.add(v1[L]),K.up.copy(x1[L]),K.lookAt(Kh),K.updateMatrixWorld(),Mt.makeTranslation(-jo.x,-jo.y,-jo.z),tv.multiplyMatrices(K.projectionMatrix,K.matrixWorldInverse),H._frustum.setFromProjectionMatrix(tv,K.coordinateSystem,K.reversedDepth)}else H.updateMatrices(I);r=H.getFrustum(),C(O,b,H.camera,I,this.type)}H.isPointLightShadow!==!0&&this.type===tl&&F(H,b),H.needsUpdate=!1}S=this.type,E.needsUpdate=!1,s.setRenderTarget(P,q,G)};function F(D,O){const b=t.update(w);_.defines.VSM_SAMPLES!==D.blurSamples&&(_.defines.VSM_SAMPLES=D.blurSamples,M.defines.VSM_SAMPLES=D.blurSamples,_.needsUpdate=!0,M.needsUpdate=!0),D.mapPass===null&&(D.mapPass=new Zi(l.x,l.y,{format:Zr,type:Ra})),_.uniforms.shadow_pass.value=D.map.depthTexture,_.uniforms.resolution.value=D.mapSize,_.uniforms.radius.value=D.radius,s.setRenderTarget(D.mapPass),s.clear(),s.renderBufferDirect(O,null,b,_,w,null),M.uniforms.shadow_pass.value=D.mapPass.texture,M.uniforms.resolution.value=D.mapSize,M.uniforms.radius.value=D.radius,s.setRenderTarget(D.map),s.clear(),s.renderBufferDirect(O,null,b,M,w,null)}function z(D,O,b,P){let q=null;const G=b.isPointLight===!0?D.customDistanceMaterial:D.customDepthMaterial;if(G!==void 0)q=G;else if(q=b.isPointLight===!0?m:p,s.localClippingEnabled&&O.clipShadows===!0&&Array.isArray(O.clippingPlanes)&&O.clippingPlanes.length!==0||O.displacementMap&&O.displacementScale!==0||O.alphaMap&&O.alphaTest>0||O.map&&O.alphaTest>0||O.alphaToCoverage===!0){const Z=q.uuid,ht=O.uuid;let mt=d[Z];mt===void 0&&(mt={},d[Z]=mt);let J=mt[ht];J===void 0&&(J=q.clone(),mt[ht]=J,O.addEventListener("dispose",N)),q=J}if(q.visible=O.visible,q.wireframe=O.wireframe,P===tl?q.side=O.shadowSide!==null?O.shadowSide:O.side:q.side=O.shadowSide!==null?O.shadowSide:v[O.side],q.alphaMap=O.alphaMap,q.alphaTest=O.alphaToCoverage===!0?.5:O.alphaTest,q.map=O.map,q.clipShadows=O.clipShadows,q.clippingPlanes=O.clippingPlanes,q.clipIntersection=O.clipIntersection,q.displacementMap=O.displacementMap,q.displacementScale=O.displacementScale,q.displacementBias=O.displacementBias,q.wireframeLinewidth=O.wireframeLinewidth,q.linewidth=O.linewidth,b.isPointLight===!0&&q.isMeshDistanceMaterial===!0){const Z=s.properties.get(q);Z.light=b}return q}function C(D,O,b,P,q){if(D.visible===!1)return;if(D.layers.test(O.layers)&&(D.isMesh||D.isLine||D.isPoints)&&(D.castShadow||D.receiveShadow&&q===tl)&&(!D.frustumCulled||r.intersectsObject(D))){D.modelViewMatrix.multiplyMatrices(b.matrixWorldInverse,D.matrixWorld);const ht=t.update(D),mt=D.material;if(Array.isArray(mt)){const J=ht.groups;for(let I=0,H=J.length;I<H;I++){const j=J[I],gt=mt[j.materialIndex];if(gt&&gt.visible){const Et=z(D,gt,P,q);D.onBeforeShadow(s,D,O,b,ht,Et,j),s.renderBufferDirect(b,null,ht,Et,D,j),D.onAfterShadow(s,D,O,b,ht,Et,j)}}}else if(mt.visible){const J=z(D,mt,P,q);D.onBeforeShadow(s,D,O,b,ht,J,null),s.renderBufferDirect(b,null,ht,J,D,null),D.onAfterShadow(s,D,O,b,ht,J,null)}}const Z=D.children;for(let ht=0,mt=Z.length;ht<mt;ht++)C(Z[ht],O,b,P,q)}function N(D){D.target.removeEventListener("dispose",N);for(const b in d){const P=d[b],q=D.target.uuid;q in P&&(P[q].dispose(),delete P[q])}}}function y1(s,t){function i(){let k=!1;const Tt=new tn;let pt=null;const Ct=new tn(0,0,0,0);return{setMask:function(It){pt!==It&&!k&&(s.colorMask(It,It,It,It),pt=It)},setLocked:function(It){k=It},setClear:function(It,St,Wt,Gt,Ke){Ke===!0&&(It*=Gt,St*=Gt,Wt*=Gt),Tt.set(It,St,Wt,Gt),Ct.equals(Tt)===!1&&(s.clearColor(It,St,Wt,Gt),Ct.copy(Tt))},reset:function(){k=!1,pt=null,Ct.set(-1,0,0,0)}}}function r(){let k=!1,Tt=!1,pt=null,Ct=null,It=null;return{setReversed:function(St){if(Tt!==St){const Wt=t.get("EXT_clip_control");St?Wt.clipControlEXT(Wt.LOWER_LEFT_EXT,Wt.ZERO_TO_ONE_EXT):Wt.clipControlEXT(Wt.LOWER_LEFT_EXT,Wt.NEGATIVE_ONE_TO_ONE_EXT),Tt=St;const Gt=It;It=null,this.setClear(Gt)}},getReversed:function(){return Tt},setTest:function(St){St?yt(s.DEPTH_TEST):Bt(s.DEPTH_TEST)},setMask:function(St){pt!==St&&!k&&(s.depthMask(St),pt=St)},setFunc:function(St){if(Tt&&(St=Wy[St]),Ct!==St){switch(St){case td:s.depthFunc(s.NEVER);break;case ed:s.depthFunc(s.ALWAYS);break;case nd:s.depthFunc(s.LESS);break;case qs:s.depthFunc(s.LEQUAL);break;case id:s.depthFunc(s.EQUAL);break;case ad:s.depthFunc(s.GEQUAL);break;case rd:s.depthFunc(s.GREATER);break;case sd:s.depthFunc(s.NOTEQUAL);break;default:s.depthFunc(s.LEQUAL)}Ct=St}},setLocked:function(St){k=St},setClear:function(St){It!==St&&(It=St,Tt&&(St=1-St),s.clearDepth(St))},reset:function(){k=!1,pt=null,Ct=null,It=null,Tt=!1}}}function l(){let k=!1,Tt=null,pt=null,Ct=null,It=null,St=null,Wt=null,Gt=null,Ke=null;return{setTest:function(Ue){k||(Ue?yt(s.STENCIL_TEST):Bt(s.STENCIL_TEST))},setMask:function(Ue){Tt!==Ue&&!k&&(s.stencilMask(Ue),Tt=Ue)},setFunc:function(Ue,Jn,jn){(pt!==Ue||Ct!==Jn||It!==jn)&&(s.stencilFunc(Ue,Jn,jn),pt=Ue,Ct=Jn,It=jn)},setOp:function(Ue,Jn,jn){(St!==Ue||Wt!==Jn||Gt!==jn)&&(s.stencilOp(Ue,Jn,jn),St=Ue,Wt=Jn,Gt=jn)},setLocked:function(Ue){k=Ue},setClear:function(Ue){Ke!==Ue&&(s.clearStencil(Ue),Ke=Ue)},reset:function(){k=!1,Tt=null,pt=null,Ct=null,It=null,St=null,Wt=null,Gt=null,Ke=null}}}const u=new i,f=new r,p=new l,m=new WeakMap,d=new WeakMap;let g={},v={},_={},M=new WeakMap,T=[],w=null,E=!1,S=null,F=null,z=null,C=null,N=null,D=null,O=null,b=new xe(0,0,0),P=0,q=!1,G=null,Z=null,ht=null,mt=null,J=null;const I=s.getParameter(s.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let H=!1,j=0;const gt=s.getParameter(s.VERSION);gt.indexOf("WebGL")!==-1?(j=parseFloat(/^WebGL (\d)/.exec(gt)[1]),H=j>=1):gt.indexOf("OpenGL ES")!==-1&&(j=parseFloat(/^OpenGL ES (\d)/.exec(gt)[1]),H=j>=2);let Et=null,L={};const K=s.getParameter(s.SCISSOR_BOX),Mt=s.getParameter(s.VIEWPORT),Rt=new tn().fromArray(K),Pt=new tn().fromArray(Mt);function at(k,Tt,pt,Ct){const It=new Uint8Array(4),St=s.createTexture();s.bindTexture(k,St),s.texParameteri(k,s.TEXTURE_MIN_FILTER,s.NEAREST),s.texParameteri(k,s.TEXTURE_MAG_FILTER,s.NEAREST);for(let Wt=0;Wt<pt;Wt++)k===s.TEXTURE_3D||k===s.TEXTURE_2D_ARRAY?s.texImage3D(Tt,0,s.RGBA,1,1,Ct,0,s.RGBA,s.UNSIGNED_BYTE,It):s.texImage2D(Tt+Wt,0,s.RGBA,1,1,0,s.RGBA,s.UNSIGNED_BYTE,It);return St}const xt={};xt[s.TEXTURE_2D]=at(s.TEXTURE_2D,s.TEXTURE_2D,1),xt[s.TEXTURE_CUBE_MAP]=at(s.TEXTURE_CUBE_MAP,s.TEXTURE_CUBE_MAP_POSITIVE_X,6),xt[s.TEXTURE_2D_ARRAY]=at(s.TEXTURE_2D_ARRAY,s.TEXTURE_2D_ARRAY,1,1),xt[s.TEXTURE_3D]=at(s.TEXTURE_3D,s.TEXTURE_3D,1,1),u.setClear(0,0,0,1),f.setClear(1),p.setClear(0),yt(s.DEPTH_TEST),f.setFunc(qs),en(!1),nn($_),yt(s.CULL_FACE),ye(Ta);function yt(k){g[k]!==!0&&(s.enable(k),g[k]=!0)}function Bt(k){g[k]!==!1&&(s.disable(k),g[k]=!1)}function ee(k,Tt){return _[k]!==Tt?(s.bindFramebuffer(k,Tt),_[k]=Tt,k===s.DRAW_FRAMEBUFFER&&(_[s.FRAMEBUFFER]=Tt),k===s.FRAMEBUFFER&&(_[s.DRAW_FRAMEBUFFER]=Tt),!0):!1}function Kt(k,Tt){let pt=T,Ct=!1;if(k){pt=M.get(Tt),pt===void 0&&(pt=[],M.set(Tt,pt));const It=k.textures;if(pt.length!==It.length||pt[0]!==s.COLOR_ATTACHMENT0){for(let St=0,Wt=It.length;St<Wt;St++)pt[St]=s.COLOR_ATTACHMENT0+St;pt.length=It.length,Ct=!0}}else pt[0]!==s.BACK&&(pt[0]=s.BACK,Ct=!0);Ct&&s.drawBuffers(pt)}function qe(k){return w!==k?(s.useProgram(k),w=k,!0):!1}const ce={[kr]:s.FUNC_ADD,[py]:s.FUNC_SUBTRACT,[my]:s.FUNC_REVERSE_SUBTRACT};ce[gy]=s.MIN,ce[_y]=s.MAX;const Se={[vy]:s.ZERO,[xy]:s.ONE,[Sy]:s.SRC_COLOR,[jh]:s.SRC_ALPHA,[Ay]:s.SRC_ALPHA_SATURATE,[by]:s.DST_COLOR,[My]:s.DST_ALPHA,[yy]:s.ONE_MINUS_SRC_COLOR,[$h]:s.ONE_MINUS_SRC_ALPHA,[Ty]:s.ONE_MINUS_DST_COLOR,[Ey]:s.ONE_MINUS_DST_ALPHA,[Ry]:s.CONSTANT_COLOR,[Cy]:s.ONE_MINUS_CONSTANT_COLOR,[wy]:s.CONSTANT_ALPHA,[Dy]:s.ONE_MINUS_CONSTANT_ALPHA};function ye(k,Tt,pt,Ct,It,St,Wt,Gt,Ke,Ue){if(k===Ta){E===!0&&(Bt(s.BLEND),E=!1);return}if(E===!1&&(yt(s.BLEND),E=!0),k!==dy){if(k!==S||Ue!==q){if((F!==kr||N!==kr)&&(s.blendEquation(s.FUNC_ADD),F=kr,N=kr),Ue)switch(k){case ks:s.blendFuncSeparate(s.ONE,s.ONE_MINUS_SRC_ALPHA,s.ONE,s.ONE_MINUS_SRC_ALPHA);break;case t0:s.blendFunc(s.ONE,s.ONE);break;case e0:s.blendFuncSeparate(s.ZERO,s.ONE_MINUS_SRC_COLOR,s.ZERO,s.ONE);break;case n0:s.blendFuncSeparate(s.DST_COLOR,s.ONE_MINUS_SRC_ALPHA,s.ZERO,s.ONE);break;default:be("WebGLState: Invalid blending: ",k);break}else switch(k){case ks:s.blendFuncSeparate(s.SRC_ALPHA,s.ONE_MINUS_SRC_ALPHA,s.ONE,s.ONE_MINUS_SRC_ALPHA);break;case t0:s.blendFuncSeparate(s.SRC_ALPHA,s.ONE,s.ONE,s.ONE);break;case e0:be("WebGLState: SubtractiveBlending requires material.premultipliedAlpha = true");break;case n0:be("WebGLState: MultiplyBlending requires material.premultipliedAlpha = true");break;default:be("WebGLState: Invalid blending: ",k);break}z=null,C=null,D=null,O=null,b.set(0,0,0),P=0,S=k,q=Ue}return}It=It||Tt,St=St||pt,Wt=Wt||Ct,(Tt!==F||It!==N)&&(s.blendEquationSeparate(ce[Tt],ce[It]),F=Tt,N=It),(pt!==z||Ct!==C||St!==D||Wt!==O)&&(s.blendFuncSeparate(Se[pt],Se[Ct],Se[St],Se[Wt]),z=pt,C=Ct,D=St,O=Wt),(Gt.equals(b)===!1||Ke!==P)&&(s.blendColor(Gt.r,Gt.g,Gt.b,Ke),b.copy(Gt),P=Ke),S=k,q=!1}function fe(k,Tt){k.side===Ea?Bt(s.CULL_FACE):yt(s.CULL_FACE);let pt=k.side===Qn;Tt&&(pt=!pt),en(pt),k.blending===ks&&k.transparent===!1?ye(Ta):ye(k.blending,k.blendEquation,k.blendSrc,k.blendDst,k.blendEquationAlpha,k.blendSrcAlpha,k.blendDstAlpha,k.blendColor,k.blendAlpha,k.premultipliedAlpha),f.setFunc(k.depthFunc),f.setTest(k.depthTest),f.setMask(k.depthWrite),u.setMask(k.colorWrite);const Ct=k.stencilWrite;p.setTest(Ct),Ct&&(p.setMask(k.stencilWriteMask),p.setFunc(k.stencilFunc,k.stencilRef,k.stencilFuncMask),p.setOp(k.stencilFail,k.stencilZFail,k.stencilZPass)),ln(k.polygonOffset,k.polygonOffsetFactor,k.polygonOffsetUnits),k.alphaToCoverage===!0?yt(s.SAMPLE_ALPHA_TO_COVERAGE):Bt(s.SAMPLE_ALPHA_TO_COVERAGE)}function en(k){G!==k&&(k?s.frontFace(s.CW):s.frontFace(s.CCW),G=k)}function nn(k){k!==cy?(yt(s.CULL_FACE),k!==Z&&(k===$_?s.cullFace(s.BACK):k===fy?s.cullFace(s.FRONT):s.cullFace(s.FRONT_AND_BACK))):Bt(s.CULL_FACE),Z=k}function an(k){k!==ht&&(H&&s.lineWidth(k),ht=k)}function ln(k,Tt,pt){k?(yt(s.POLYGON_OFFSET_FILL),(mt!==Tt||J!==pt)&&(mt=Tt,J=pt,f.getReversed()&&(Tt=-Tt),s.polygonOffset(Tt,pt))):Bt(s.POLYGON_OFFSET_FILL)}function We(k){k?yt(s.SCISSOR_TEST):Bt(s.SCISSOR_TEST)}function rn(k){k===void 0&&(k=s.TEXTURE0+I-1),Et!==k&&(s.activeTexture(k),Et=k)}function W(k,Tt,pt){pt===void 0&&(Et===null?pt=s.TEXTURE0+I-1:pt=Et);let Ct=L[pt];Ct===void 0&&(Ct={type:void 0,texture:void 0},L[pt]=Ct),(Ct.type!==k||Ct.texture!==Tt)&&(Et!==pt&&(s.activeTexture(pt),Et=pt),s.bindTexture(k,Tt||xt[k]),Ct.type=k,Ct.texture=Tt)}function ze(){const k=L[Et];k!==void 0&&k.type!==void 0&&(s.bindTexture(k.type,null),k.type=void 0,k.texture=void 0)}function Ce(){try{s.compressedTexImage2D(...arguments)}catch(k){be("WebGLState:",k)}}function U(){try{s.compressedTexImage3D(...arguments)}catch(k){be("WebGLState:",k)}}function y(){try{s.texSubImage2D(...arguments)}catch(k){be("WebGLState:",k)}}function Q(){try{s.texSubImage3D(...arguments)}catch(k){be("WebGLState:",k)}}function rt(){try{s.compressedTexSubImage2D(...arguments)}catch(k){be("WebGLState:",k)}}function ct(){try{s.compressedTexSubImage3D(...arguments)}catch(k){be("WebGLState:",k)}}function bt(){try{s.texStorage2D(...arguments)}catch(k){be("WebGLState:",k)}}function wt(){try{s.texStorage3D(...arguments)}catch(k){be("WebGLState:",k)}}function ut(){try{s.texImage2D(...arguments)}catch(k){be("WebGLState:",k)}}function ft(){try{s.texImage3D(...arguments)}catch(k){be("WebGLState:",k)}}function At(k){return v[k]!==void 0?v[k]:s.getParameter(k)}function Ft(k,Tt){v[k]!==Tt&&(s.pixelStorei(k,Tt),v[k]=Tt)}function Lt(k){Rt.equals(k)===!1&&(s.scissor(k.x,k.y,k.z,k.w),Rt.copy(k))}function Dt(k){Pt.equals(k)===!1&&(s.viewport(k.x,k.y,k.z,k.w),Pt.copy(k))}function Zt(k,Tt){let pt=d.get(Tt);pt===void 0&&(pt=new WeakMap,d.set(Tt,pt));let Ct=pt.get(k);Ct===void 0&&(Ct=s.getUniformBlockIndex(Tt,k.name),pt.set(k,Ct))}function Qt(k,Tt){const Ct=d.get(Tt).get(k);m.get(Tt)!==Ct&&(s.uniformBlockBinding(Tt,Ct,k.__bindingPointIndex),m.set(Tt,Ct))}function ne(){s.disable(s.BLEND),s.disable(s.CULL_FACE),s.disable(s.DEPTH_TEST),s.disable(s.POLYGON_OFFSET_FILL),s.disable(s.SCISSOR_TEST),s.disable(s.STENCIL_TEST),s.disable(s.SAMPLE_ALPHA_TO_COVERAGE),s.blendEquation(s.FUNC_ADD),s.blendFunc(s.ONE,s.ZERO),s.blendFuncSeparate(s.ONE,s.ZERO,s.ONE,s.ZERO),s.blendColor(0,0,0,0),s.colorMask(!0,!0,!0,!0),s.clearColor(0,0,0,0),s.depthMask(!0),s.depthFunc(s.LESS),f.setReversed(!1),s.clearDepth(1),s.stencilMask(4294967295),s.stencilFunc(s.ALWAYS,0,4294967295),s.stencilOp(s.KEEP,s.KEEP,s.KEEP),s.clearStencil(0),s.cullFace(s.BACK),s.frontFace(s.CCW),s.polygonOffset(0,0),s.activeTexture(s.TEXTURE0),s.bindFramebuffer(s.FRAMEBUFFER,null),s.bindFramebuffer(s.DRAW_FRAMEBUFFER,null),s.bindFramebuffer(s.READ_FRAMEBUFFER,null),s.useProgram(null),s.lineWidth(1),s.scissor(0,0,s.canvas.width,s.canvas.height),s.viewport(0,0,s.canvas.width,s.canvas.height),s.pixelStorei(s.PACK_ALIGNMENT,4),s.pixelStorei(s.UNPACK_ALIGNMENT,4),s.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,!1),s.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,!1),s.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,s.BROWSER_DEFAULT_WEBGL),s.pixelStorei(s.PACK_ROW_LENGTH,0),s.pixelStorei(s.PACK_SKIP_PIXELS,0),s.pixelStorei(s.PACK_SKIP_ROWS,0),s.pixelStorei(s.UNPACK_ROW_LENGTH,0),s.pixelStorei(s.UNPACK_IMAGE_HEIGHT,0),s.pixelStorei(s.UNPACK_SKIP_PIXELS,0),s.pixelStorei(s.UNPACK_SKIP_ROWS,0),s.pixelStorei(s.UNPACK_SKIP_IMAGES,0),g={},v={},Et=null,L={},_={},M=new WeakMap,T=[],w=null,E=!1,S=null,F=null,z=null,C=null,N=null,D=null,O=null,b=new xe(0,0,0),P=0,q=!1,G=null,Z=null,ht=null,mt=null,J=null,Rt.set(0,0,s.canvas.width,s.canvas.height),Pt.set(0,0,s.canvas.width,s.canvas.height),u.reset(),f.reset(),p.reset()}return{buffers:{color:u,depth:f,stencil:p},enable:yt,disable:Bt,bindFramebuffer:ee,drawBuffers:Kt,useProgram:qe,setBlending:ye,setMaterial:fe,setFlipSided:en,setCullFace:nn,setLineWidth:an,setPolygonOffset:ln,setScissorTest:We,activeTexture:rn,bindTexture:W,unbindTexture:ze,compressedTexImage2D:Ce,compressedTexImage3D:U,texImage2D:ut,texImage3D:ft,pixelStorei:Ft,getParameter:At,updateUBOMapping:Zt,uniformBlockBinding:Qt,texStorage2D:bt,texStorage3D:wt,texSubImage2D:y,texSubImage3D:Q,compressedTexSubImage2D:rt,compressedTexSubImage3D:ct,scissor:Lt,viewport:Dt,reset:ne}}function M1(s,t,i,r,l,u,f){const p=t.has("WEBGL_multisampled_render_to_texture")?t.get("WEBGL_multisampled_render_to_texture"):null,m=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),d=new ie,g=new WeakMap,v=new Set;let _;const M=new WeakMap;let T=!1;try{T=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function w(U,y){return T?new OffscreenCanvas(U,y):tc("canvas")}function E(U,y,Q){let rt=1;const ct=Ce(U);if((ct.width>Q||ct.height>Q)&&(rt=Q/Math.max(ct.width,ct.height)),rt<1)if(typeof HTMLImageElement<"u"&&U instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&U instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&U instanceof ImageBitmap||typeof VideoFrame<"u"&&U instanceof VideoFrame){const bt=Math.floor(rt*ct.width),wt=Math.floor(rt*ct.height);_===void 0&&(_=w(bt,wt));const ut=y?w(bt,wt):_;return ut.width=bt,ut.height=wt,ut.getContext("2d").drawImage(U,0,0,bt,wt),te("WebGLRenderer: Texture has been resized from ("+ct.width+"x"+ct.height+") to ("+bt+"x"+wt+")."),ut}else return"data"in U&&te("WebGLRenderer: Image in DataTexture is too big ("+ct.width+"x"+ct.height+")."),U;return U}function S(U){return U.generateMipmaps}function F(U){s.generateMipmap(U)}function z(U){return U.isWebGLCubeRenderTarget?s.TEXTURE_CUBE_MAP:U.isWebGL3DRenderTarget?s.TEXTURE_3D:U.isWebGLArrayRenderTarget||U.isCompressedArrayTexture?s.TEXTURE_2D_ARRAY:s.TEXTURE_2D}function C(U,y,Q,rt,ct,bt=!1){if(U!==null){if(s[U]!==void 0)return s[U];te("WebGLRenderer: Attempt to use non-existing WebGL internal format '"+U+"'")}let wt;rt&&(wt=t.get("EXT_texture_norm16"),wt||te("WebGLRenderer: Unable to use normalized textures without EXT_texture_norm16 extension"));let ut=y;if(y===s.RED&&(Q===s.FLOAT&&(ut=s.R32F),Q===s.HALF_FLOAT&&(ut=s.R16F),Q===s.UNSIGNED_BYTE&&(ut=s.R8),Q===s.UNSIGNED_SHORT&&wt&&(ut=wt.R16_EXT),Q===s.SHORT&&wt&&(ut=wt.R16_SNORM_EXT)),y===s.RED_INTEGER&&(Q===s.UNSIGNED_BYTE&&(ut=s.R8UI),Q===s.UNSIGNED_SHORT&&(ut=s.R16UI),Q===s.UNSIGNED_INT&&(ut=s.R32UI),Q===s.BYTE&&(ut=s.R8I),Q===s.SHORT&&(ut=s.R16I),Q===s.INT&&(ut=s.R32I)),y===s.RG&&(Q===s.FLOAT&&(ut=s.RG32F),Q===s.HALF_FLOAT&&(ut=s.RG16F),Q===s.UNSIGNED_BYTE&&(ut=s.RG8),Q===s.UNSIGNED_SHORT&&wt&&(ut=wt.RG16_EXT),Q===s.SHORT&&wt&&(ut=wt.RG16_SNORM_EXT)),y===s.RG_INTEGER&&(Q===s.UNSIGNED_BYTE&&(ut=s.RG8UI),Q===s.UNSIGNED_SHORT&&(ut=s.RG16UI),Q===s.UNSIGNED_INT&&(ut=s.RG32UI),Q===s.BYTE&&(ut=s.RG8I),Q===s.SHORT&&(ut=s.RG16I),Q===s.INT&&(ut=s.RG32I)),y===s.RGB_INTEGER&&(Q===s.UNSIGNED_BYTE&&(ut=s.RGB8UI),Q===s.UNSIGNED_SHORT&&(ut=s.RGB16UI),Q===s.UNSIGNED_INT&&(ut=s.RGB32UI),Q===s.BYTE&&(ut=s.RGB8I),Q===s.SHORT&&(ut=s.RGB16I),Q===s.INT&&(ut=s.RGB32I)),y===s.RGBA_INTEGER&&(Q===s.UNSIGNED_BYTE&&(ut=s.RGBA8UI),Q===s.UNSIGNED_SHORT&&(ut=s.RGBA16UI),Q===s.UNSIGNED_INT&&(ut=s.RGBA32UI),Q===s.BYTE&&(ut=s.RGBA8I),Q===s.SHORT&&(ut=s.RGBA16I),Q===s.INT&&(ut=s.RGBA32I)),y===s.RGB&&(Q===s.UNSIGNED_SHORT&&wt&&(ut=wt.RGB16_EXT),Q===s.SHORT&&wt&&(ut=wt.RGB16_SNORM_EXT),Q===s.UNSIGNED_INT_5_9_9_9_REV&&(ut=s.RGB9_E5),Q===s.UNSIGNED_INT_10F_11F_11F_REV&&(ut=s.R11F_G11F_B10F)),y===s.RGBA){const ft=bt?$u:Ee.getTransfer(ct);Q===s.FLOAT&&(ut=s.RGBA32F),Q===s.HALF_FLOAT&&(ut=s.RGBA16F),Q===s.UNSIGNED_BYTE&&(ut=ft===Fe?s.SRGB8_ALPHA8:s.RGBA8),Q===s.UNSIGNED_SHORT&&wt&&(ut=wt.RGBA16_EXT),Q===s.SHORT&&wt&&(ut=wt.RGBA16_SNORM_EXT),Q===s.UNSIGNED_SHORT_4_4_4_4&&(ut=s.RGBA4),Q===s.UNSIGNED_SHORT_5_5_5_1&&(ut=s.RGB5_A1)}return(ut===s.R16F||ut===s.R32F||ut===s.RG16F||ut===s.RG32F||ut===s.RGBA16F||ut===s.RGBA32F)&&t.get("EXT_color_buffer_float"),ut}function N(U,y){let Q;return U?y===null||y===Ki||y===al?Q=s.DEPTH24_STENCIL8:y===Wi?Q=s.DEPTH32F_STENCIL8:y===il&&(Q=s.DEPTH24_STENCIL8,te("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):y===null||y===Ki||y===al?Q=s.DEPTH_COMPONENT24:y===Wi?Q=s.DEPTH_COMPONENT32F:y===il&&(Q=s.DEPTH_COMPONENT16),Q}function D(U,y){return S(U)===!0||U.isFramebufferTexture&&U.minFilter!==Dn&&U.minFilter!==In?Math.log2(Math.max(y.width,y.height))+1:U.mipmaps!==void 0&&U.mipmaps.length>0?U.mipmaps.length:U.isCompressedTexture&&Array.isArray(U.image)?y.mipmaps.length:1}function O(U){const y=U.target;y.removeEventListener("dispose",O),P(y),y.isVideoTexture&&g.delete(y),y.isHTMLTexture&&v.delete(y)}function b(U){const y=U.target;y.removeEventListener("dispose",b),G(y)}function P(U){const y=r.get(U);if(y.__webglInit===void 0)return;const Q=U.source,rt=M.get(Q);if(rt){const ct=rt[y.__cacheKey];ct.usedTimes--,ct.usedTimes===0&&q(U),Object.keys(rt).length===0&&M.delete(Q)}r.remove(U)}function q(U){const y=r.get(U);s.deleteTexture(y.__webglTexture);const Q=U.source,rt=M.get(Q);delete rt[y.__cacheKey],f.memory.textures--}function G(U){const y=r.get(U);if(U.depthTexture&&(U.depthTexture.dispose(),r.remove(U.depthTexture)),U.isWebGLCubeRenderTarget)for(let rt=0;rt<6;rt++){if(Array.isArray(y.__webglFramebuffer[rt]))for(let ct=0;ct<y.__webglFramebuffer[rt].length;ct++)s.deleteFramebuffer(y.__webglFramebuffer[rt][ct]);else s.deleteFramebuffer(y.__webglFramebuffer[rt]);y.__webglDepthbuffer&&s.deleteRenderbuffer(y.__webglDepthbuffer[rt])}else{if(Array.isArray(y.__webglFramebuffer))for(let rt=0;rt<y.__webglFramebuffer.length;rt++)s.deleteFramebuffer(y.__webglFramebuffer[rt]);else s.deleteFramebuffer(y.__webglFramebuffer);if(y.__webglDepthbuffer&&s.deleteRenderbuffer(y.__webglDepthbuffer),y.__webglMultisampledFramebuffer&&s.deleteFramebuffer(y.__webglMultisampledFramebuffer),y.__webglColorRenderbuffer)for(let rt=0;rt<y.__webglColorRenderbuffer.length;rt++)y.__webglColorRenderbuffer[rt]&&s.deleteRenderbuffer(y.__webglColorRenderbuffer[rt]);y.__webglDepthRenderbuffer&&s.deleteRenderbuffer(y.__webglDepthRenderbuffer)}const Q=U.textures;for(let rt=0,ct=Q.length;rt<ct;rt++){const bt=r.get(Q[rt]);bt.__webglTexture&&(s.deleteTexture(bt.__webglTexture),f.memory.textures--),r.remove(Q[rt])}r.remove(U)}let Z=0;function ht(){Z=0}function mt(){return Z}function J(U){Z=U}function I(){const U=Z;return U>=l.maxTextures&&te("WebGLTextures: Trying to use "+U+" texture units while this GPU supports only "+l.maxTextures),Z+=1,U}function H(U){const y=[];return y.push(U.wrapS),y.push(U.wrapT),y.push(U.wrapR||0),y.push(U.magFilter),y.push(U.minFilter),y.push(U.anisotropy),y.push(U.internalFormat),y.push(U.format),y.push(U.type),y.push(U.generateMipmaps),y.push(U.premultiplyAlpha),y.push(U.flipY),y.push(U.unpackAlignment),y.push(U.colorSpace),y.join()}function j(U,y){const Q=r.get(U);if(U.isVideoTexture&&W(U),U.isRenderTargetTexture===!1&&U.isExternalTexture!==!0&&U.version>0&&Q.__version!==U.version){const rt=U.image;if(rt===null)te("WebGLRenderer: Texture marked for update but no image data found.");else if(rt.complete===!1)te("WebGLRenderer: Texture marked for update but image is incomplete");else{Bt(Q,U,y);return}}else U.isExternalTexture&&(Q.__webglTexture=U.sourceTexture?U.sourceTexture:null);i.bindTexture(s.TEXTURE_2D,Q.__webglTexture,s.TEXTURE0+y)}function gt(U,y){const Q=r.get(U);if(U.isRenderTargetTexture===!1&&U.version>0&&Q.__version!==U.version){Bt(Q,U,y);return}else U.isExternalTexture&&(Q.__webglTexture=U.sourceTexture?U.sourceTexture:null);i.bindTexture(s.TEXTURE_2D_ARRAY,Q.__webglTexture,s.TEXTURE0+y)}function Et(U,y){const Q=r.get(U);if(U.isRenderTargetTexture===!1&&U.version>0&&Q.__version!==U.version){Bt(Q,U,y);return}i.bindTexture(s.TEXTURE_3D,Q.__webglTexture,s.TEXTURE0+y)}function L(U,y){const Q=r.get(U);if(U.isCubeDepthTexture!==!0&&U.version>0&&Q.__version!==U.version){ee(Q,U,y);return}i.bindTexture(s.TEXTURE_CUBE_MAP,Q.__webglTexture,s.TEXTURE0+y)}const K={[od]:s.REPEAT,[ba]:s.CLAMP_TO_EDGE,[ld]:s.MIRRORED_REPEAT},Mt={[Dn]:s.NEAREST,[Ny]:s.NEAREST_MIPMAP_NEAREST,[xu]:s.NEAREST_MIPMAP_LINEAR,[In]:s.LINEAR,[xh]:s.LINEAR_MIPMAP_NEAREST,[Wr]:s.LINEAR_MIPMAP_LINEAR},Rt={[Iy]:s.NEVER,[Gy]:s.ALWAYS,[Fy]:s.LESS,[Jd]:s.LEQUAL,[zy]:s.EQUAL,[jd]:s.GEQUAL,[By]:s.GREATER,[Hy]:s.NOTEQUAL};function Pt(U,y){if(y.type===Wi&&t.has("OES_texture_float_linear")===!1&&(y.magFilter===In||y.magFilter===xh||y.magFilter===xu||y.magFilter===Wr||y.minFilter===In||y.minFilter===xh||y.minFilter===xu||y.minFilter===Wr)&&te("WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),s.texParameteri(U,s.TEXTURE_WRAP_S,K[y.wrapS]),s.texParameteri(U,s.TEXTURE_WRAP_T,K[y.wrapT]),(U===s.TEXTURE_3D||U===s.TEXTURE_2D_ARRAY)&&s.texParameteri(U,s.TEXTURE_WRAP_R,K[y.wrapR]),s.texParameteri(U,s.TEXTURE_MAG_FILTER,Mt[y.magFilter]),s.texParameteri(U,s.TEXTURE_MIN_FILTER,Mt[y.minFilter]),y.compareFunction&&(s.texParameteri(U,s.TEXTURE_COMPARE_MODE,s.COMPARE_REF_TO_TEXTURE),s.texParameteri(U,s.TEXTURE_COMPARE_FUNC,Rt[y.compareFunction])),t.has("EXT_texture_filter_anisotropic")===!0){if(y.magFilter===Dn||y.minFilter!==xu&&y.minFilter!==Wr||y.type===Wi&&t.has("OES_texture_float_linear")===!1)return;if(y.anisotropy>1||r.get(y).__currentAnisotropy){const Q=t.get("EXT_texture_filter_anisotropic");s.texParameterf(U,Q.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(y.anisotropy,l.getMaxAnisotropy())),r.get(y).__currentAnisotropy=y.anisotropy}}}function at(U,y){let Q=!1;U.__webglInit===void 0&&(U.__webglInit=!0,y.addEventListener("dispose",O));const rt=y.source;let ct=M.get(rt);ct===void 0&&(ct={},M.set(rt,ct));const bt=H(y);if(bt!==U.__cacheKey){ct[bt]===void 0&&(ct[bt]={texture:s.createTexture(),usedTimes:0},f.memory.textures++,Q=!0),ct[bt].usedTimes++;const wt=ct[U.__cacheKey];wt!==void 0&&(ct[U.__cacheKey].usedTimes--,wt.usedTimes===0&&q(y)),U.__cacheKey=bt,U.__webglTexture=ct[bt].texture}return Q}function xt(U,y,Q){return Math.floor(Math.floor(U/Q)/y)}function yt(U,y,Q,rt){const bt=U.updateRanges;if(bt.length===0)i.texSubImage2D(s.TEXTURE_2D,0,0,0,y.width,y.height,Q,rt,y.data);else{bt.sort((Ft,Lt)=>Ft.start-Lt.start);let wt=0;for(let Ft=1;Ft<bt.length;Ft++){const Lt=bt[wt],Dt=bt[Ft],Zt=Lt.start+Lt.count,Qt=xt(Dt.start,y.width,4),ne=xt(Lt.start,y.width,4);Dt.start<=Zt+1&&Qt===ne&&xt(Dt.start+Dt.count-1,y.width,4)===Qt?Lt.count=Math.max(Lt.count,Dt.start+Dt.count-Lt.start):(++wt,bt[wt]=Dt)}bt.length=wt+1;const ut=i.getParameter(s.UNPACK_ROW_LENGTH),ft=i.getParameter(s.UNPACK_SKIP_PIXELS),At=i.getParameter(s.UNPACK_SKIP_ROWS);i.pixelStorei(s.UNPACK_ROW_LENGTH,y.width);for(let Ft=0,Lt=bt.length;Ft<Lt;Ft++){const Dt=bt[Ft],Zt=Math.floor(Dt.start/4),Qt=Math.ceil(Dt.count/4),ne=Zt%y.width,k=Math.floor(Zt/y.width),Tt=Qt,pt=1;i.pixelStorei(s.UNPACK_SKIP_PIXELS,ne),i.pixelStorei(s.UNPACK_SKIP_ROWS,k),i.texSubImage2D(s.TEXTURE_2D,0,ne,k,Tt,pt,Q,rt,y.data)}U.clearUpdateRanges(),i.pixelStorei(s.UNPACK_ROW_LENGTH,ut),i.pixelStorei(s.UNPACK_SKIP_PIXELS,ft),i.pixelStorei(s.UNPACK_SKIP_ROWS,At)}}function Bt(U,y,Q){let rt=s.TEXTURE_2D;(y.isDataArrayTexture||y.isCompressedArrayTexture)&&(rt=s.TEXTURE_2D_ARRAY),y.isData3DTexture&&(rt=s.TEXTURE_3D);const ct=at(U,y),bt=y.source;i.bindTexture(rt,U.__webglTexture,s.TEXTURE0+Q);const wt=r.get(bt);if(bt.version!==wt.__version||ct===!0){if(i.activeTexture(s.TEXTURE0+Q),(typeof ImageBitmap<"u"&&y.image instanceof ImageBitmap)===!1){const pt=Ee.getPrimaries(Ee.workingColorSpace),Ct=y.colorSpace===ur?null:Ee.getPrimaries(y.colorSpace),It=y.colorSpace===ur||pt===Ct?s.NONE:s.BROWSER_DEFAULT_WEBGL;i.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,y.flipY),i.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,y.premultiplyAlpha),i.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,It)}i.pixelStorei(s.UNPACK_ALIGNMENT,y.unpackAlignment);let ft=E(y.image,!1,l.maxTextureSize);ft=ze(y,ft);const At=u.convert(y.format,y.colorSpace),Ft=u.convert(y.type);let Lt=C(y.internalFormat,At,Ft,y.normalized,y.colorSpace,y.isVideoTexture);Pt(rt,y);let Dt;const Zt=y.mipmaps,Qt=y.isVideoTexture!==!0,ne=wt.__version===void 0||ct===!0,k=bt.dataReady,Tt=D(y,ft);if(y.isDepthTexture)Lt=N(y.format===qr,y.type),ne&&(Qt?i.texStorage2D(s.TEXTURE_2D,1,Lt,ft.width,ft.height):i.texImage2D(s.TEXTURE_2D,0,Lt,ft.width,ft.height,0,At,Ft,null));else if(y.isDataTexture)if(Zt.length>0){Qt&&ne&&i.texStorage2D(s.TEXTURE_2D,Tt,Lt,Zt[0].width,Zt[0].height);for(let pt=0,Ct=Zt.length;pt<Ct;pt++)Dt=Zt[pt],Qt?k&&i.texSubImage2D(s.TEXTURE_2D,pt,0,0,Dt.width,Dt.height,At,Ft,Dt.data):i.texImage2D(s.TEXTURE_2D,pt,Lt,Dt.width,Dt.height,0,At,Ft,Dt.data);y.generateMipmaps=!1}else Qt?(ne&&i.texStorage2D(s.TEXTURE_2D,Tt,Lt,ft.width,ft.height),k&&yt(y,ft,At,Ft)):i.texImage2D(s.TEXTURE_2D,0,Lt,ft.width,ft.height,0,At,Ft,ft.data);else if(y.isCompressedTexture)if(y.isCompressedArrayTexture){Qt&&ne&&i.texStorage3D(s.TEXTURE_2D_ARRAY,Tt,Lt,Zt[0].width,Zt[0].height,ft.depth);for(let pt=0,Ct=Zt.length;pt<Ct;pt++)if(Dt=Zt[pt],y.format!==Ni)if(At!==null)if(Qt){if(k)if(y.layerUpdates.size>0){const It=U0(Dt.width,Dt.height,y.format,y.type);for(const St of y.layerUpdates){const Wt=Dt.data.subarray(St*It/Dt.data.BYTES_PER_ELEMENT,(St+1)*It/Dt.data.BYTES_PER_ELEMENT);i.compressedTexSubImage3D(s.TEXTURE_2D_ARRAY,pt,0,0,St,Dt.width,Dt.height,1,At,Wt)}y.clearLayerUpdates()}else i.compressedTexSubImage3D(s.TEXTURE_2D_ARRAY,pt,0,0,0,Dt.width,Dt.height,ft.depth,At,Dt.data)}else i.compressedTexImage3D(s.TEXTURE_2D_ARRAY,pt,Lt,Dt.width,Dt.height,ft.depth,0,Dt.data,0,0);else te("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else Qt?k&&i.texSubImage3D(s.TEXTURE_2D_ARRAY,pt,0,0,0,Dt.width,Dt.height,ft.depth,At,Ft,Dt.data):i.texImage3D(s.TEXTURE_2D_ARRAY,pt,Lt,Dt.width,Dt.height,ft.depth,0,At,Ft,Dt.data)}else{Qt&&ne&&i.texStorage2D(s.TEXTURE_2D,Tt,Lt,Zt[0].width,Zt[0].height);for(let pt=0,Ct=Zt.length;pt<Ct;pt++)Dt=Zt[pt],y.format!==Ni?At!==null?Qt?k&&i.compressedTexSubImage2D(s.TEXTURE_2D,pt,0,0,Dt.width,Dt.height,At,Dt.data):i.compressedTexImage2D(s.TEXTURE_2D,pt,Lt,Dt.width,Dt.height,0,Dt.data):te("WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):Qt?k&&i.texSubImage2D(s.TEXTURE_2D,pt,0,0,Dt.width,Dt.height,At,Ft,Dt.data):i.texImage2D(s.TEXTURE_2D,pt,Lt,Dt.width,Dt.height,0,At,Ft,Dt.data)}else if(y.isDataArrayTexture)if(Qt){if(ne&&i.texStorage3D(s.TEXTURE_2D_ARRAY,Tt,Lt,ft.width,ft.height,ft.depth),k)if(y.layerUpdates.size>0){const pt=U0(ft.width,ft.height,y.format,y.type);for(const Ct of y.layerUpdates){const It=ft.data.subarray(Ct*pt/ft.data.BYTES_PER_ELEMENT,(Ct+1)*pt/ft.data.BYTES_PER_ELEMENT);i.texSubImage3D(s.TEXTURE_2D_ARRAY,0,0,0,Ct,ft.width,ft.height,1,At,Ft,It)}y.clearLayerUpdates()}else i.texSubImage3D(s.TEXTURE_2D_ARRAY,0,0,0,0,ft.width,ft.height,ft.depth,At,Ft,ft.data)}else i.texImage3D(s.TEXTURE_2D_ARRAY,0,Lt,ft.width,ft.height,ft.depth,0,At,Ft,ft.data);else if(y.isData3DTexture)Qt?(ne&&i.texStorage3D(s.TEXTURE_3D,Tt,Lt,ft.width,ft.height,ft.depth),k&&i.texSubImage3D(s.TEXTURE_3D,0,0,0,0,ft.width,ft.height,ft.depth,At,Ft,ft.data)):i.texImage3D(s.TEXTURE_3D,0,Lt,ft.width,ft.height,ft.depth,0,At,Ft,ft.data);else if(y.isFramebufferTexture){if(ne)if(Qt)i.texStorage2D(s.TEXTURE_2D,Tt,Lt,ft.width,ft.height);else{let pt=ft.width,Ct=ft.height;for(let It=0;It<Tt;It++)i.texImage2D(s.TEXTURE_2D,It,Lt,pt,Ct,0,At,Ft,null),pt>>=1,Ct>>=1}}else if(y.isHTMLTexture){if("texElementImage2D"in s){const pt=s.canvas;if(pt.hasAttribute("layoutsubtree")||pt.setAttribute("layoutsubtree","true"),ft.parentNode!==pt){pt.appendChild(ft),v.add(y),pt.onpaint=Ct=>{const It=Ct.changedElements;for(const St of v)It.includes(St.image)&&(St.needsUpdate=!0)},pt.requestPaint();return}if(s.texElementImage2D.length===3)s.texElementImage2D(s.TEXTURE_2D,s.RGBA8,ft);else{const It=s.RGBA,St=s.RGBA,Wt=s.UNSIGNED_BYTE;s.texElementImage2D(s.TEXTURE_2D,0,It,St,Wt,ft)}s.texParameteri(s.TEXTURE_2D,s.TEXTURE_MIN_FILTER,s.LINEAR),s.texParameteri(s.TEXTURE_2D,s.TEXTURE_WRAP_S,s.CLAMP_TO_EDGE),s.texParameteri(s.TEXTURE_2D,s.TEXTURE_WRAP_T,s.CLAMP_TO_EDGE)}}else if(Zt.length>0){if(Qt&&ne){const pt=Ce(Zt[0]);i.texStorage2D(s.TEXTURE_2D,Tt,Lt,pt.width,pt.height)}for(let pt=0,Ct=Zt.length;pt<Ct;pt++)Dt=Zt[pt],Qt?k&&i.texSubImage2D(s.TEXTURE_2D,pt,0,0,At,Ft,Dt):i.texImage2D(s.TEXTURE_2D,pt,Lt,At,Ft,Dt);y.generateMipmaps=!1}else if(Qt){if(ne){const pt=Ce(ft);i.texStorage2D(s.TEXTURE_2D,Tt,Lt,pt.width,pt.height)}k&&i.texSubImage2D(s.TEXTURE_2D,0,0,0,At,Ft,ft)}else i.texImage2D(s.TEXTURE_2D,0,Lt,At,Ft,ft);S(y)&&F(rt),wt.__version=bt.version,y.onUpdate&&y.onUpdate(y)}U.__version=y.version}function ee(U,y,Q){if(y.image.length!==6)return;const rt=at(U,y),ct=y.source;i.bindTexture(s.TEXTURE_CUBE_MAP,U.__webglTexture,s.TEXTURE0+Q);const bt=r.get(ct);if(ct.version!==bt.__version||rt===!0){i.activeTexture(s.TEXTURE0+Q);const wt=Ee.getPrimaries(Ee.workingColorSpace),ut=y.colorSpace===ur?null:Ee.getPrimaries(y.colorSpace),ft=y.colorSpace===ur||wt===ut?s.NONE:s.BROWSER_DEFAULT_WEBGL;i.pixelStorei(s.UNPACK_FLIP_Y_WEBGL,y.flipY),i.pixelStorei(s.UNPACK_PREMULTIPLY_ALPHA_WEBGL,y.premultiplyAlpha),i.pixelStorei(s.UNPACK_ALIGNMENT,y.unpackAlignment),i.pixelStorei(s.UNPACK_COLORSPACE_CONVERSION_WEBGL,ft);const At=y.isCompressedTexture||y.image[0].isCompressedTexture,Ft=y.image[0]&&y.image[0].isDataTexture,Lt=[];for(let St=0;St<6;St++)!At&&!Ft?Lt[St]=E(y.image[St],!0,l.maxCubemapSize):Lt[St]=Ft?y.image[St].image:y.image[St],Lt[St]=ze(y,Lt[St]);const Dt=Lt[0],Zt=u.convert(y.format,y.colorSpace),Qt=u.convert(y.type),ne=C(y.internalFormat,Zt,Qt,y.normalized,y.colorSpace),k=y.isVideoTexture!==!0,Tt=bt.__version===void 0||rt===!0,pt=ct.dataReady;let Ct=D(y,Dt);Pt(s.TEXTURE_CUBE_MAP,y);let It;if(At){k&&Tt&&i.texStorage2D(s.TEXTURE_CUBE_MAP,Ct,ne,Dt.width,Dt.height);for(let St=0;St<6;St++){It=Lt[St].mipmaps;for(let Wt=0;Wt<It.length;Wt++){const Gt=It[Wt];y.format!==Ni?Zt!==null?k?pt&&i.compressedTexSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,Wt,0,0,Gt.width,Gt.height,Zt,Gt.data):i.compressedTexImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,Wt,ne,Gt.width,Gt.height,0,Gt.data):te("WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):k?pt&&i.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,Wt,0,0,Gt.width,Gt.height,Zt,Qt,Gt.data):i.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,Wt,ne,Gt.width,Gt.height,0,Zt,Qt,Gt.data)}}}else{if(It=y.mipmaps,k&&Tt){It.length>0&&Ct++;const St=Ce(Lt[0]);i.texStorage2D(s.TEXTURE_CUBE_MAP,Ct,ne,St.width,St.height)}for(let St=0;St<6;St++)if(Ft){k?pt&&i.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,0,0,0,Lt[St].width,Lt[St].height,Zt,Qt,Lt[St].data):i.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,0,ne,Lt[St].width,Lt[St].height,0,Zt,Qt,Lt[St].data);for(let Wt=0;Wt<It.length;Wt++){const Ke=It[Wt].image[St].image;k?pt&&i.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,Wt+1,0,0,Ke.width,Ke.height,Zt,Qt,Ke.data):i.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,Wt+1,ne,Ke.width,Ke.height,0,Zt,Qt,Ke.data)}}else{k?pt&&i.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,0,0,0,Zt,Qt,Lt[St]):i.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,0,ne,Zt,Qt,Lt[St]);for(let Wt=0;Wt<It.length;Wt++){const Gt=It[Wt];k?pt&&i.texSubImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,Wt+1,0,0,Zt,Qt,Gt.image[St]):i.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+St,Wt+1,ne,Zt,Qt,Gt.image[St])}}}S(y)&&F(s.TEXTURE_CUBE_MAP),bt.__version=ct.version,y.onUpdate&&y.onUpdate(y)}U.__version=y.version}function Kt(U,y,Q,rt,ct,bt){const wt=u.convert(Q.format,Q.colorSpace),ut=u.convert(Q.type),ft=C(Q.internalFormat,wt,ut,Q.normalized,Q.colorSpace),At=r.get(y),Ft=r.get(Q);if(Ft.__renderTarget=y,!At.__hasExternalTextures){const Lt=Math.max(1,y.width>>bt),Dt=Math.max(1,y.height>>bt);ct===s.TEXTURE_3D||ct===s.TEXTURE_2D_ARRAY?i.texImage3D(ct,bt,ft,Lt,Dt,y.depth,0,wt,ut,null):i.texImage2D(ct,bt,ft,Lt,Dt,0,wt,ut,null)}i.bindFramebuffer(s.FRAMEBUFFER,U),rn(y)?p.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,rt,ct,Ft.__webglTexture,0,We(y)):(ct===s.TEXTURE_2D||ct>=s.TEXTURE_CUBE_MAP_POSITIVE_X&&ct<=s.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&s.framebufferTexture2D(s.FRAMEBUFFER,rt,ct,Ft.__webglTexture,bt),i.bindFramebuffer(s.FRAMEBUFFER,null)}function qe(U,y,Q){if(s.bindRenderbuffer(s.RENDERBUFFER,U),y.depthBuffer){const rt=y.depthTexture,ct=rt&&rt.isDepthTexture?rt.type:null,bt=N(y.stencilBuffer,ct),wt=y.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT;rn(y)?p.renderbufferStorageMultisampleEXT(s.RENDERBUFFER,We(y),bt,y.width,y.height):Q?s.renderbufferStorageMultisample(s.RENDERBUFFER,We(y),bt,y.width,y.height):s.renderbufferStorage(s.RENDERBUFFER,bt,y.width,y.height),s.framebufferRenderbuffer(s.FRAMEBUFFER,wt,s.RENDERBUFFER,U)}else{const rt=y.textures;for(let ct=0;ct<rt.length;ct++){const bt=rt[ct],wt=u.convert(bt.format,bt.colorSpace),ut=u.convert(bt.type),ft=C(bt.internalFormat,wt,ut,bt.normalized,bt.colorSpace);rn(y)?p.renderbufferStorageMultisampleEXT(s.RENDERBUFFER,We(y),ft,y.width,y.height):Q?s.renderbufferStorageMultisample(s.RENDERBUFFER,We(y),ft,y.width,y.height):s.renderbufferStorage(s.RENDERBUFFER,ft,y.width,y.height)}}s.bindRenderbuffer(s.RENDERBUFFER,null)}function ce(U,y,Q){const rt=y.isWebGLCubeRenderTarget===!0;if(i.bindFramebuffer(s.FRAMEBUFFER,U),!(y.depthTexture&&y.depthTexture.isDepthTexture))throw new Error("THREE.WebGLTextures: renderTarget.depthTexture must be an instance of THREE.DepthTexture.");const ct=r.get(y.depthTexture);if(ct.__renderTarget=y,(!ct.__webglTexture||y.depthTexture.image.width!==y.width||y.depthTexture.image.height!==y.height)&&(y.depthTexture.image.width=y.width,y.depthTexture.image.height=y.height,y.depthTexture.needsUpdate=!0),rt){if(ct.__webglInit===void 0&&(ct.__webglInit=!0,y.depthTexture.addEventListener("dispose",O)),ct.__webglTexture===void 0){ct.__webglTexture=s.createTexture(),i.bindTexture(s.TEXTURE_CUBE_MAP,ct.__webglTexture),Pt(s.TEXTURE_CUBE_MAP,y.depthTexture);const At=u.convert(y.depthTexture.format),Ft=u.convert(y.depthTexture.type);let Lt;y.depthTexture.format===Ca?Lt=s.DEPTH_COMPONENT24:y.depthTexture.format===qr&&(Lt=s.DEPTH24_STENCIL8);for(let Dt=0;Dt<6;Dt++)s.texImage2D(s.TEXTURE_CUBE_MAP_POSITIVE_X+Dt,0,Lt,y.width,y.height,0,At,Ft,null)}}else j(y.depthTexture,0);const bt=ct.__webglTexture,wt=We(y),ut=rt?s.TEXTURE_CUBE_MAP_POSITIVE_X+Q:s.TEXTURE_2D,ft=y.depthTexture.format===qr?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT;if(y.depthTexture.format===Ca)rn(y)?p.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,ft,ut,bt,0,wt):s.framebufferTexture2D(s.FRAMEBUFFER,ft,ut,bt,0);else if(y.depthTexture.format===qr)rn(y)?p.framebufferTexture2DMultisampleEXT(s.FRAMEBUFFER,ft,ut,bt,0,wt):s.framebufferTexture2D(s.FRAMEBUFFER,ft,ut,bt,0);else throw new Error("THREE.WebGLTextures: Unknown depthTexture format.")}function Se(U){const y=r.get(U),Q=U.isWebGLCubeRenderTarget===!0;if(y.__boundDepthTexture!==U.depthTexture){const rt=U.depthTexture;if(y.__depthDisposeCallback&&y.__depthDisposeCallback(),rt){const ct=()=>{delete y.__boundDepthTexture,delete y.__depthDisposeCallback,rt.removeEventListener("dispose",ct)};rt.addEventListener("dispose",ct),y.__depthDisposeCallback=ct}y.__boundDepthTexture=rt}if(U.depthTexture&&!y.__autoAllocateDepthBuffer)if(Q)for(let rt=0;rt<6;rt++)ce(y.__webglFramebuffer[rt],U,rt);else{const rt=U.texture.mipmaps;rt&&rt.length>0?ce(y.__webglFramebuffer[0],U,0):ce(y.__webglFramebuffer,U,0)}else if(Q){y.__webglDepthbuffer=[];for(let rt=0;rt<6;rt++)if(i.bindFramebuffer(s.FRAMEBUFFER,y.__webglFramebuffer[rt]),y.__webglDepthbuffer[rt]===void 0)y.__webglDepthbuffer[rt]=s.createRenderbuffer(),qe(y.__webglDepthbuffer[rt],U,!1);else{const ct=U.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,bt=y.__webglDepthbuffer[rt];s.bindRenderbuffer(s.RENDERBUFFER,bt),s.framebufferRenderbuffer(s.FRAMEBUFFER,ct,s.RENDERBUFFER,bt)}}else{const rt=U.texture.mipmaps;if(rt&&rt.length>0?i.bindFramebuffer(s.FRAMEBUFFER,y.__webglFramebuffer[0]):i.bindFramebuffer(s.FRAMEBUFFER,y.__webglFramebuffer),y.__webglDepthbuffer===void 0)y.__webglDepthbuffer=s.createRenderbuffer(),qe(y.__webglDepthbuffer,U,!1);else{const ct=U.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,bt=y.__webglDepthbuffer;s.bindRenderbuffer(s.RENDERBUFFER,bt),s.framebufferRenderbuffer(s.FRAMEBUFFER,ct,s.RENDERBUFFER,bt)}}i.bindFramebuffer(s.FRAMEBUFFER,null)}function ye(U,y,Q){const rt=r.get(U);y!==void 0&&Kt(rt.__webglFramebuffer,U,U.texture,s.COLOR_ATTACHMENT0,s.TEXTURE_2D,0),Q!==void 0&&Se(U)}function fe(U){const y=U.texture,Q=r.get(U),rt=r.get(y);U.addEventListener("dispose",b);const ct=U.textures,bt=U.isWebGLCubeRenderTarget===!0,wt=ct.length>1;if(wt||(rt.__webglTexture===void 0&&(rt.__webglTexture=s.createTexture()),rt.__version=y.version,f.memory.textures++),bt){Q.__webglFramebuffer=[];for(let ut=0;ut<6;ut++)if(y.mipmaps&&y.mipmaps.length>0){Q.__webglFramebuffer[ut]=[];for(let ft=0;ft<y.mipmaps.length;ft++)Q.__webglFramebuffer[ut][ft]=s.createFramebuffer()}else Q.__webglFramebuffer[ut]=s.createFramebuffer()}else{if(y.mipmaps&&y.mipmaps.length>0){Q.__webglFramebuffer=[];for(let ut=0;ut<y.mipmaps.length;ut++)Q.__webglFramebuffer[ut]=s.createFramebuffer()}else Q.__webglFramebuffer=s.createFramebuffer();if(wt)for(let ut=0,ft=ct.length;ut<ft;ut++){const At=r.get(ct[ut]);At.__webglTexture===void 0&&(At.__webglTexture=s.createTexture(),f.memory.textures++)}if(U.samples>0&&rn(U)===!1){Q.__webglMultisampledFramebuffer=s.createFramebuffer(),Q.__webglColorRenderbuffer=[],i.bindFramebuffer(s.FRAMEBUFFER,Q.__webglMultisampledFramebuffer);for(let ut=0;ut<ct.length;ut++){const ft=ct[ut];Q.__webglColorRenderbuffer[ut]=s.createRenderbuffer(),s.bindRenderbuffer(s.RENDERBUFFER,Q.__webglColorRenderbuffer[ut]);const At=u.convert(ft.format,ft.colorSpace),Ft=u.convert(ft.type),Lt=C(ft.internalFormat,At,Ft,ft.normalized,ft.colorSpace,U.isXRRenderTarget===!0),Dt=We(U);s.renderbufferStorageMultisample(s.RENDERBUFFER,Dt,Lt,U.width,U.height),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+ut,s.RENDERBUFFER,Q.__webglColorRenderbuffer[ut])}s.bindRenderbuffer(s.RENDERBUFFER,null),U.depthBuffer&&(Q.__webglDepthRenderbuffer=s.createRenderbuffer(),qe(Q.__webglDepthRenderbuffer,U,!0)),i.bindFramebuffer(s.FRAMEBUFFER,null)}}if(bt){i.bindTexture(s.TEXTURE_CUBE_MAP,rt.__webglTexture),Pt(s.TEXTURE_CUBE_MAP,y);for(let ut=0;ut<6;ut++)if(y.mipmaps&&y.mipmaps.length>0)for(let ft=0;ft<y.mipmaps.length;ft++)Kt(Q.__webglFramebuffer[ut][ft],U,y,s.COLOR_ATTACHMENT0,s.TEXTURE_CUBE_MAP_POSITIVE_X+ut,ft);else Kt(Q.__webglFramebuffer[ut],U,y,s.COLOR_ATTACHMENT0,s.TEXTURE_CUBE_MAP_POSITIVE_X+ut,0);S(y)&&F(s.TEXTURE_CUBE_MAP),i.unbindTexture()}else if(wt){for(let ut=0,ft=ct.length;ut<ft;ut++){const At=ct[ut],Ft=r.get(At);let Lt=s.TEXTURE_2D;(U.isWebGL3DRenderTarget||U.isWebGLArrayRenderTarget)&&(Lt=U.isWebGL3DRenderTarget?s.TEXTURE_3D:s.TEXTURE_2D_ARRAY),i.bindTexture(Lt,Ft.__webglTexture),Pt(Lt,At),Kt(Q.__webglFramebuffer,U,At,s.COLOR_ATTACHMENT0+ut,Lt,0),S(At)&&F(Lt)}i.unbindTexture()}else{let ut=s.TEXTURE_2D;if((U.isWebGL3DRenderTarget||U.isWebGLArrayRenderTarget)&&(ut=U.isWebGL3DRenderTarget?s.TEXTURE_3D:s.TEXTURE_2D_ARRAY),i.bindTexture(ut,rt.__webglTexture),Pt(ut,y),y.mipmaps&&y.mipmaps.length>0)for(let ft=0;ft<y.mipmaps.length;ft++)Kt(Q.__webglFramebuffer[ft],U,y,s.COLOR_ATTACHMENT0,ut,ft);else Kt(Q.__webglFramebuffer,U,y,s.COLOR_ATTACHMENT0,ut,0);S(y)&&F(ut),i.unbindTexture()}U.depthBuffer&&Se(U)}function en(U){const y=U.textures;for(let Q=0,rt=y.length;Q<rt;Q++){const ct=y[Q];if(S(ct)){const bt=z(U),wt=r.get(ct).__webglTexture;i.bindTexture(bt,wt),F(bt),i.unbindTexture()}}}const nn=[],an=[];function ln(U){if(U.samples>0){if(rn(U)===!1){const y=U.textures,Q=U.width,rt=U.height;let ct=s.COLOR_BUFFER_BIT;const bt=U.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT,wt=r.get(U),ut=y.length>1;if(ut)for(let At=0;At<y.length;At++)i.bindFramebuffer(s.FRAMEBUFFER,wt.__webglMultisampledFramebuffer),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+At,s.RENDERBUFFER,null),i.bindFramebuffer(s.FRAMEBUFFER,wt.__webglFramebuffer),s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0+At,s.TEXTURE_2D,null,0);i.bindFramebuffer(s.READ_FRAMEBUFFER,wt.__webglMultisampledFramebuffer);const ft=U.texture.mipmaps;ft&&ft.length>0?i.bindFramebuffer(s.DRAW_FRAMEBUFFER,wt.__webglFramebuffer[0]):i.bindFramebuffer(s.DRAW_FRAMEBUFFER,wt.__webglFramebuffer);for(let At=0;At<y.length;At++){if(U.resolveDepthBuffer&&(U.depthBuffer&&(ct|=s.DEPTH_BUFFER_BIT),U.stencilBuffer&&U.resolveStencilBuffer&&(ct|=s.STENCIL_BUFFER_BIT)),ut){s.framebufferRenderbuffer(s.READ_FRAMEBUFFER,s.COLOR_ATTACHMENT0,s.RENDERBUFFER,wt.__webglColorRenderbuffer[At]);const Ft=r.get(y[At]).__webglTexture;s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0,s.TEXTURE_2D,Ft,0)}s.blitFramebuffer(0,0,Q,rt,0,0,Q,rt,ct,s.NEAREST),m===!0&&(nn.length=0,an.length=0,nn.push(s.COLOR_ATTACHMENT0+At),U.depthBuffer&&U.resolveDepthBuffer===!1&&(nn.push(bt),an.push(bt),s.invalidateFramebuffer(s.DRAW_FRAMEBUFFER,an)),s.invalidateFramebuffer(s.READ_FRAMEBUFFER,nn))}if(i.bindFramebuffer(s.READ_FRAMEBUFFER,null),i.bindFramebuffer(s.DRAW_FRAMEBUFFER,null),ut)for(let At=0;At<y.length;At++){i.bindFramebuffer(s.FRAMEBUFFER,wt.__webglMultisampledFramebuffer),s.framebufferRenderbuffer(s.FRAMEBUFFER,s.COLOR_ATTACHMENT0+At,s.RENDERBUFFER,wt.__webglColorRenderbuffer[At]);const Ft=r.get(y[At]).__webglTexture;i.bindFramebuffer(s.FRAMEBUFFER,wt.__webglFramebuffer),s.framebufferTexture2D(s.DRAW_FRAMEBUFFER,s.COLOR_ATTACHMENT0+At,s.TEXTURE_2D,Ft,0)}i.bindFramebuffer(s.DRAW_FRAMEBUFFER,wt.__webglMultisampledFramebuffer)}else if(U.depthBuffer&&U.resolveDepthBuffer===!1&&m){const y=U.stencilBuffer?s.DEPTH_STENCIL_ATTACHMENT:s.DEPTH_ATTACHMENT;s.invalidateFramebuffer(s.DRAW_FRAMEBUFFER,[y])}}}function We(U){return Math.min(l.maxSamples,U.samples)}function rn(U){const y=r.get(U);return U.samples>0&&t.has("WEBGL_multisampled_render_to_texture")===!0&&y.__useRenderToTexture!==!1}function W(U){const y=f.render.frame;g.get(U)!==y&&(g.set(U,y),U.update())}function ze(U,y){const Q=U.colorSpace,rt=U.format,ct=U.type;return U.isCompressedTexture===!0||U.isVideoTexture===!0||Q!==ju&&Q!==ur&&(Ee.getTransfer(Q)===Fe?(rt!==Ni||ct!==fi)&&te("WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):be("WebGLTextures: Unsupported texture color space:",Q)),y}function Ce(U){return typeof HTMLImageElement<"u"&&U instanceof HTMLImageElement?(d.width=U.naturalWidth||U.width,d.height=U.naturalHeight||U.height):typeof VideoFrame<"u"&&U instanceof VideoFrame?(d.width=U.displayWidth,d.height=U.displayHeight):(d.width=U.width,d.height=U.height),d}this.allocateTextureUnit=I,this.resetTextureUnits=ht,this.getTextureUnits=mt,this.setTextureUnits=J,this.setTexture2D=j,this.setTexture2DArray=gt,this.setTexture3D=Et,this.setTextureCube=L,this.rebindTextures=ye,this.setupRenderTarget=fe,this.updateRenderTargetMipmap=en,this.updateMultisampleRenderTarget=ln,this.setupDepthRenderbuffer=Se,this.setupFrameBufferTexture=Kt,this.useMultisampledRTT=rn,this.isReversedDepthBuffer=function(){return i.buffers.depth.getReversed()}}function E1(s,t){function i(r,l=ur){let u;const f=Ee.getTransfer(l);if(r===fi)return s.UNSIGNED_BYTE;if(r===qd)return s.UNSIGNED_SHORT_4_4_4_4;if(r===Yd)return s.UNSIGNED_SHORT_5_5_5_1;if(r===Ev)return s.UNSIGNED_INT_5_9_9_9_REV;if(r===bv)return s.UNSIGNED_INT_10F_11F_11F_REV;if(r===yv)return s.BYTE;if(r===Mv)return s.SHORT;if(r===il)return s.UNSIGNED_SHORT;if(r===Wd)return s.INT;if(r===Ki)return s.UNSIGNED_INT;if(r===Wi)return s.FLOAT;if(r===Ra)return s.HALF_FLOAT;if(r===Tv)return s.ALPHA;if(r===Av)return s.RGB;if(r===Ni)return s.RGBA;if(r===Ca)return s.DEPTH_COMPONENT;if(r===qr)return s.DEPTH_STENCIL;if(r===Rv)return s.RED;if(r===Zd)return s.RED_INTEGER;if(r===Zr)return s.RG;if(r===Kd)return s.RG_INTEGER;if(r===Qd)return s.RGBA_INTEGER;if(r===ku||r===Xu||r===Wu||r===qu)if(f===Fe)if(u=t.get("WEBGL_compressed_texture_s3tc_srgb"),u!==null){if(r===ku)return u.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(r===Xu)return u.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(r===Wu)return u.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(r===qu)return u.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(u=t.get("WEBGL_compressed_texture_s3tc"),u!==null){if(r===ku)return u.COMPRESSED_RGB_S3TC_DXT1_EXT;if(r===Xu)return u.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(r===Wu)return u.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(r===qu)return u.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(r===ud||r===cd||r===fd||r===hd)if(u=t.get("WEBGL_compressed_texture_pvrtc"),u!==null){if(r===ud)return u.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(r===cd)return u.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(r===fd)return u.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(r===hd)return u.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(r===dd||r===pd||r===md||r===gd||r===_d||r===Ku||r===vd)if(u=t.get("WEBGL_compressed_texture_etc"),u!==null){if(r===dd||r===pd)return f===Fe?u.COMPRESSED_SRGB8_ETC2:u.COMPRESSED_RGB8_ETC2;if(r===md)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:u.COMPRESSED_RGBA8_ETC2_EAC;if(r===gd)return u.COMPRESSED_R11_EAC;if(r===_d)return u.COMPRESSED_SIGNED_R11_EAC;if(r===Ku)return u.COMPRESSED_RG11_EAC;if(r===vd)return u.COMPRESSED_SIGNED_RG11_EAC}else return null;if(r===xd||r===Sd||r===yd||r===Md||r===Ed||r===bd||r===Td||r===Ad||r===Rd||r===Cd||r===wd||r===Dd||r===Ud||r===Ld)if(u=t.get("WEBGL_compressed_texture_astc"),u!==null){if(r===xd)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:u.COMPRESSED_RGBA_ASTC_4x4_KHR;if(r===Sd)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:u.COMPRESSED_RGBA_ASTC_5x4_KHR;if(r===yd)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:u.COMPRESSED_RGBA_ASTC_5x5_KHR;if(r===Md)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:u.COMPRESSED_RGBA_ASTC_6x5_KHR;if(r===Ed)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:u.COMPRESSED_RGBA_ASTC_6x6_KHR;if(r===bd)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:u.COMPRESSED_RGBA_ASTC_8x5_KHR;if(r===Td)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:u.COMPRESSED_RGBA_ASTC_8x6_KHR;if(r===Ad)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:u.COMPRESSED_RGBA_ASTC_8x8_KHR;if(r===Rd)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:u.COMPRESSED_RGBA_ASTC_10x5_KHR;if(r===Cd)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:u.COMPRESSED_RGBA_ASTC_10x6_KHR;if(r===wd)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:u.COMPRESSED_RGBA_ASTC_10x8_KHR;if(r===Dd)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:u.COMPRESSED_RGBA_ASTC_10x10_KHR;if(r===Ud)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:u.COMPRESSED_RGBA_ASTC_12x10_KHR;if(r===Ld)return f===Fe?u.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:u.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(r===Nd||r===Od||r===Pd)if(u=t.get("EXT_texture_compression_bptc"),u!==null){if(r===Nd)return f===Fe?u.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:u.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(r===Od)return u.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(r===Pd)return u.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(r===Id||r===Fd||r===Qu||r===zd)if(u=t.get("EXT_texture_compression_rgtc"),u!==null){if(r===Id)return u.COMPRESSED_RED_RGTC1_EXT;if(r===Fd)return u.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(r===Qu)return u.COMPRESSED_RED_GREEN_RGTC2_EXT;if(r===zd)return u.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return r===al?s.UNSIGNED_INT_24_8:s[r]!==void 0?s[r]:null}return{convert:i}}const b1=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,T1=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class A1{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(t,i){if(this.texture===null){const r=new Fv(t.texture);(t.depthNear!==i.depthNear||t.depthFar!==i.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=r}}getMesh(t){if(this.texture!==null&&this.mesh===null){const i=t.cameras[0].viewport,r=new Ji({vertexShader:b1,fragmentShader:T1,uniforms:{depthColor:{value:this.texture},depthWidth:{value:i.z},depthHeight:{value:i.w}}});this.mesh=new Qi(new ic(20,20),r)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class R1 extends pr{constructor(t,i){super();const r=this;let l=null,u=1,f=null,p="local-floor",m=1,d=null,g=null,v=null,_=null,M=null,T=null;const w=typeof XRWebGLBinding<"u",E=new A1,S={},F=i.getContextAttributes();let z=null,C=null;const N=[],D=[],O=new ie;let b=null;const P=new Mi;P.viewport=new tn;const q=new Mi;q.viewport=new tn;const G=[P,q],Z=new IM;let ht=null,mt=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(at){let xt=N[at];return xt===void 0&&(xt=new Ah,N[at]=xt),xt.getTargetRaySpace()},this.getControllerGrip=function(at){let xt=N[at];return xt===void 0&&(xt=new Ah,N[at]=xt),xt.getGripSpace()},this.getHand=function(at){let xt=N[at];return xt===void 0&&(xt=new Ah,N[at]=xt),xt.getHandSpace()};function J(at){const xt=D.indexOf(at.inputSource);if(xt===-1)return;const yt=N[xt];yt!==void 0&&(yt.update(at.inputSource,at.frame,d||f),yt.dispatchEvent({type:at.type,data:at.inputSource}))}function I(){l.removeEventListener("select",J),l.removeEventListener("selectstart",J),l.removeEventListener("selectend",J),l.removeEventListener("squeeze",J),l.removeEventListener("squeezestart",J),l.removeEventListener("squeezeend",J),l.removeEventListener("end",I),l.removeEventListener("inputsourceschange",H);for(let at=0;at<N.length;at++){const xt=D[at];xt!==null&&(D[at]=null,N[at].disconnect(xt))}ht=null,mt=null,E.reset();for(const at in S)delete S[at];t.setRenderTarget(z),M=null,_=null,v=null,l=null,C=null,Pt.stop(),r.isPresenting=!1,t.setPixelRatio(b),t.setSize(O.width,O.height,!1),r.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(at){u=at,r.isPresenting===!0&&te("WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(at){p=at,r.isPresenting===!0&&te("WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return d||f},this.setReferenceSpace=function(at){d=at},this.getBaseLayer=function(){return _!==null?_:M},this.getBinding=function(){return v===null&&w&&(v=new XRWebGLBinding(l,i)),v},this.getFrame=function(){return T},this.getSession=function(){return l},this.setSession=async function(at){if(l=at,l!==null){if(z=t.getRenderTarget(),l.addEventListener("select",J),l.addEventListener("selectstart",J),l.addEventListener("selectend",J),l.addEventListener("squeeze",J),l.addEventListener("squeezestart",J),l.addEventListener("squeezeend",J),l.addEventListener("end",I),l.addEventListener("inputsourceschange",H),F.xrCompatible!==!0&&await i.makeXRCompatible(),b=t.getPixelRatio(),t.getSize(O),w&&"createProjectionLayer"in XRWebGLBinding.prototype){let yt=null,Bt=null,ee=null;F.depth&&(ee=F.stencil?i.DEPTH24_STENCIL8:i.DEPTH_COMPONENT24,yt=F.stencil?qr:Ca,Bt=F.stencil?al:Ki);const Kt={colorFormat:i.RGBA8,depthFormat:ee,scaleFactor:u};v=this.getBinding(),_=v.createProjectionLayer(Kt),l.updateRenderState({layers:[_]}),t.setPixelRatio(1),t.setSize(_.textureWidth,_.textureHeight,!1),C=new Zi(_.textureWidth,_.textureHeight,{format:Ni,type:fi,depthTexture:new Zs(_.textureWidth,_.textureHeight,Bt,void 0,void 0,void 0,void 0,void 0,void 0,yt),stencilBuffer:F.stencil,colorSpace:t.outputColorSpace,samples:F.antialias?4:0,resolveDepthBuffer:_.ignoreDepthValues===!1,resolveStencilBuffer:_.ignoreDepthValues===!1})}else{const yt={antialias:F.antialias,alpha:!0,depth:F.depth,stencil:F.stencil,framebufferScaleFactor:u};M=new XRWebGLLayer(l,i,yt),l.updateRenderState({baseLayer:M}),t.setPixelRatio(1),t.setSize(M.framebufferWidth,M.framebufferHeight,!1),C=new Zi(M.framebufferWidth,M.framebufferHeight,{format:Ni,type:fi,colorSpace:t.outputColorSpace,stencilBuffer:F.stencil,resolveDepthBuffer:M.ignoreDepthValues===!1,resolveStencilBuffer:M.ignoreDepthValues===!1})}C.isXRRenderTarget=!0,this.setFoveation(m),d=null,f=await l.requestReferenceSpace(p),Pt.setContext(l),Pt.start(),r.isPresenting=!0,r.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(l!==null)return l.environmentBlendMode},this.getDepthTexture=function(){return E.getDepthTexture()};function H(at){for(let xt=0;xt<at.removed.length;xt++){const yt=at.removed[xt],Bt=D.indexOf(yt);Bt>=0&&(D[Bt]=null,N[Bt].disconnect(yt))}for(let xt=0;xt<at.added.length;xt++){const yt=at.added[xt];let Bt=D.indexOf(yt);if(Bt===-1){for(let Kt=0;Kt<N.length;Kt++)if(Kt>=D.length){D.push(yt),Bt=Kt;break}else if(D[Kt]===null){D[Kt]=yt,Bt=Kt;break}if(Bt===-1)break}const ee=N[Bt];ee&&ee.connect(yt)}}const j=new $,gt=new $;function Et(at,xt,yt){j.setFromMatrixPosition(xt.matrixWorld),gt.setFromMatrixPosition(yt.matrixWorld);const Bt=j.distanceTo(gt),ee=xt.projectionMatrix.elements,Kt=yt.projectionMatrix.elements,qe=ee[14]/(ee[10]-1),ce=ee[14]/(ee[10]+1),Se=(ee[9]+1)/ee[5],ye=(ee[9]-1)/ee[5],fe=(ee[8]-1)/ee[0],en=(Kt[8]+1)/Kt[0],nn=qe*fe,an=qe*en,ln=Bt/(-fe+en),We=ln*-fe;if(xt.matrixWorld.decompose(at.position,at.quaternion,at.scale),at.translateX(We),at.translateZ(ln),at.matrixWorld.compose(at.position,at.quaternion,at.scale),at.matrixWorldInverse.copy(at.matrixWorld).invert(),ee[10]===-1)at.projectionMatrix.copy(xt.projectionMatrix),at.projectionMatrixInverse.copy(xt.projectionMatrixInverse);else{const rn=qe+ln,W=ce+ln,ze=nn-We,Ce=an+(Bt-We),U=Se*ce/W*rn,y=ye*ce/W*rn;at.projectionMatrix.makePerspective(ze,Ce,U,y,rn,W),at.projectionMatrixInverse.copy(at.projectionMatrix).invert()}}function L(at,xt){xt===null?at.matrixWorld.copy(at.matrix):at.matrixWorld.multiplyMatrices(xt.matrixWorld,at.matrix),at.matrixWorldInverse.copy(at.matrixWorld).invert()}this.updateCamera=function(at){if(l===null)return;let xt=at.near,yt=at.far;E.texture!==null&&(E.depthNear>0&&(xt=E.depthNear),E.depthFar>0&&(yt=E.depthFar)),Z.near=q.near=P.near=xt,Z.far=q.far=P.far=yt,(ht!==Z.near||mt!==Z.far)&&(l.updateRenderState({depthNear:Z.near,depthFar:Z.far}),ht=Z.near,mt=Z.far),Z.layers.mask=at.layers.mask|6,P.layers.mask=Z.layers.mask&-5,q.layers.mask=Z.layers.mask&-3;const Bt=at.parent,ee=Z.cameras;L(Z,Bt);for(let Kt=0;Kt<ee.length;Kt++)L(ee[Kt],Bt);ee.length===2?Et(Z,P,q):Z.projectionMatrix.copy(P.projectionMatrix),K(at,Z,Bt)};function K(at,xt,yt){yt===null?at.matrix.copy(xt.matrixWorld):(at.matrix.copy(yt.matrixWorld),at.matrix.invert(),at.matrix.multiply(xt.matrixWorld)),at.matrix.decompose(at.position,at.quaternion,at.scale),at.updateMatrixWorld(!0),at.projectionMatrix.copy(xt.projectionMatrix),at.projectionMatrixInverse.copy(xt.projectionMatrixInverse),at.isPerspectiveCamera&&(at.fov=Bd*2*Math.atan(1/at.projectionMatrix.elements[5]),at.zoom=1)}this.getCamera=function(){return Z},this.getFoveation=function(){if(!(_===null&&M===null))return m},this.setFoveation=function(at){m=at,_!==null&&(_.fixedFoveation=at),M!==null&&M.fixedFoveation!==void 0&&(M.fixedFoveation=at)},this.hasDepthSensing=function(){return E.texture!==null},this.getDepthSensingMesh=function(){return E.getMesh(Z)},this.getCameraTexture=function(at){return S[at]};let Mt=null;function Rt(at,xt){if(g=xt.getViewerPose(d||f),T=xt,g!==null){const yt=g.views;M!==null&&(t.setRenderTargetFramebuffer(C,M.framebuffer),t.setRenderTarget(C));let Bt=!1;yt.length!==Z.cameras.length&&(Z.cameras.length=0,Bt=!0);for(let ce=0;ce<yt.length;ce++){const Se=yt[ce];let ye=null;if(M!==null)ye=M.getViewport(Se);else{const en=v.getViewSubImage(_,Se);ye=en.viewport,ce===0&&(t.setRenderTargetTextures(C,en.colorTexture,en.depthStencilTexture),t.setRenderTarget(C))}let fe=G[ce];fe===void 0&&(fe=new Mi,fe.layers.enable(ce),fe.viewport=new tn,G[ce]=fe),fe.matrix.fromArray(Se.transform.matrix),fe.matrix.decompose(fe.position,fe.quaternion,fe.scale),fe.projectionMatrix.fromArray(Se.projectionMatrix),fe.projectionMatrixInverse.copy(fe.projectionMatrix).invert(),fe.viewport.set(ye.x,ye.y,ye.width,ye.height),ce===0&&(Z.matrix.copy(fe.matrix),Z.matrix.decompose(Z.position,Z.quaternion,Z.scale)),Bt===!0&&Z.cameras.push(fe)}const ee=l.enabledFeatures;if(ee&&ee.includes("depth-sensing")&&l.depthUsage=="gpu-optimized"&&w){v=r.getBinding();const ce=v.getDepthInformation(yt[0]);ce&&ce.isValid&&ce.texture&&E.init(ce,l.renderState)}if(ee&&ee.includes("camera-access")&&w){t.state.unbindTexture(),v=r.getBinding();for(let ce=0;ce<yt.length;ce++){const Se=yt[ce].camera;if(Se){let ye=S[Se];ye||(ye=new Fv,S[Se]=ye);const fe=v.getCameraImage(Se);ye.sourceTexture=fe}}}}for(let yt=0;yt<N.length;yt++){const Bt=D[yt],ee=N[yt];Bt!==null&&ee!==void 0&&ee.update(Bt,xt,d||f)}Mt&&Mt(at,xt),xt.detectedPlanes&&r.dispatchEvent({type:"planesdetected",data:xt}),T=null}const Pt=new Gv;Pt.setAnimationLoop(Rt),this.setAnimationLoop=function(at){Mt=at},this.dispose=function(){}}}const C1=new $e,Zv=new re;Zv.set(-1,0,0,0,1,0,0,0,1);function w1(s,t){function i(E,S){E.matrixAutoUpdate===!0&&E.updateMatrix(),S.value.copy(E.matrix)}function r(E,S){S.color.getRGB(E.fogColor.value,zv(s)),S.isFog?(E.fogNear.value=S.near,E.fogFar.value=S.far):S.isFogExp2&&(E.fogDensity.value=S.density)}function l(E,S,F,z,C){S.isNodeMaterial?S.uniformsNeedUpdate=!1:S.isMeshBasicMaterial?u(E,S):S.isMeshLambertMaterial?(u(E,S),S.envMap&&(E.envMapIntensity.value=S.envMapIntensity)):S.isMeshToonMaterial?(u(E,S),v(E,S)):S.isMeshPhongMaterial?(u(E,S),g(E,S),S.envMap&&(E.envMapIntensity.value=S.envMapIntensity)):S.isMeshStandardMaterial?(u(E,S),_(E,S),S.isMeshPhysicalMaterial&&M(E,S,C)):S.isMeshMatcapMaterial?(u(E,S),T(E,S)):S.isMeshDepthMaterial?u(E,S):S.isMeshDistanceMaterial?(u(E,S),w(E,S)):S.isMeshNormalMaterial?u(E,S):S.isLineBasicMaterial?(f(E,S),S.isLineDashedMaterial&&p(E,S)):S.isPointsMaterial?m(E,S,F,z):S.isSpriteMaterial?d(E,S):S.isShadowMaterial?(E.color.value.copy(S.color),E.opacity.value=S.opacity):S.isShaderMaterial&&(S.uniformsNeedUpdate=!1)}function u(E,S){E.opacity.value=S.opacity,S.color&&E.diffuse.value.copy(S.color),S.emissive&&E.emissive.value.copy(S.emissive).multiplyScalar(S.emissiveIntensity),S.map&&(E.map.value=S.map,i(S.map,E.mapTransform)),S.alphaMap&&(E.alphaMap.value=S.alphaMap,i(S.alphaMap,E.alphaMapTransform)),S.bumpMap&&(E.bumpMap.value=S.bumpMap,i(S.bumpMap,E.bumpMapTransform),E.bumpScale.value=S.bumpScale,S.side===Qn&&(E.bumpScale.value*=-1)),S.normalMap&&(E.normalMap.value=S.normalMap,i(S.normalMap,E.normalMapTransform),E.normalScale.value.copy(S.normalScale),S.side===Qn&&E.normalScale.value.negate()),S.displacementMap&&(E.displacementMap.value=S.displacementMap,i(S.displacementMap,E.displacementMapTransform),E.displacementScale.value=S.displacementScale,E.displacementBias.value=S.displacementBias),S.emissiveMap&&(E.emissiveMap.value=S.emissiveMap,i(S.emissiveMap,E.emissiveMapTransform)),S.specularMap&&(E.specularMap.value=S.specularMap,i(S.specularMap,E.specularMapTransform)),S.alphaTest>0&&(E.alphaTest.value=S.alphaTest);const F=t.get(S),z=F.envMap,C=F.envMapRotation;z&&(E.envMap.value=z,E.envMapRotation.value.setFromMatrix4(C1.makeRotationFromEuler(C)).transpose(),z.isCubeTexture&&z.isRenderTargetTexture===!1&&E.envMapRotation.value.premultiply(Zv),E.reflectivity.value=S.reflectivity,E.ior.value=S.ior,E.refractionRatio.value=S.refractionRatio),S.lightMap&&(E.lightMap.value=S.lightMap,E.lightMapIntensity.value=S.lightMapIntensity,i(S.lightMap,E.lightMapTransform)),S.aoMap&&(E.aoMap.value=S.aoMap,E.aoMapIntensity.value=S.aoMapIntensity,i(S.aoMap,E.aoMapTransform))}function f(E,S){E.diffuse.value.copy(S.color),E.opacity.value=S.opacity,S.map&&(E.map.value=S.map,i(S.map,E.mapTransform))}function p(E,S){E.dashSize.value=S.dashSize,E.totalSize.value=S.dashSize+S.gapSize,E.scale.value=S.scale}function m(E,S,F,z){E.diffuse.value.copy(S.color),E.opacity.value=S.opacity,E.size.value=S.size*F,E.scale.value=z*.5,S.map&&(E.map.value=S.map,i(S.map,E.uvTransform)),S.alphaMap&&(E.alphaMap.value=S.alphaMap,i(S.alphaMap,E.alphaMapTransform)),S.alphaTest>0&&(E.alphaTest.value=S.alphaTest)}function d(E,S){E.diffuse.value.copy(S.color),E.opacity.value=S.opacity,E.rotation.value=S.rotation,S.map&&(E.map.value=S.map,i(S.map,E.mapTransform)),S.alphaMap&&(E.alphaMap.value=S.alphaMap,i(S.alphaMap,E.alphaMapTransform)),S.alphaTest>0&&(E.alphaTest.value=S.alphaTest)}function g(E,S){E.specular.value.copy(S.specular),E.shininess.value=Math.max(S.shininess,1e-4)}function v(E,S){S.gradientMap&&(E.gradientMap.value=S.gradientMap)}function _(E,S){E.metalness.value=S.metalness,S.metalnessMap&&(E.metalnessMap.value=S.metalnessMap,i(S.metalnessMap,E.metalnessMapTransform)),E.roughness.value=S.roughness,S.roughnessMap&&(E.roughnessMap.value=S.roughnessMap,i(S.roughnessMap,E.roughnessMapTransform)),S.envMap&&(E.envMapIntensity.value=S.envMapIntensity)}function M(E,S,F){E.ior.value=S.ior,S.sheen>0&&(E.sheenColor.value.copy(S.sheenColor).multiplyScalar(S.sheen),E.sheenRoughness.value=S.sheenRoughness,S.sheenColorMap&&(E.sheenColorMap.value=S.sheenColorMap,i(S.sheenColorMap,E.sheenColorMapTransform)),S.sheenRoughnessMap&&(E.sheenRoughnessMap.value=S.sheenRoughnessMap,i(S.sheenRoughnessMap,E.sheenRoughnessMapTransform))),S.clearcoat>0&&(E.clearcoat.value=S.clearcoat,E.clearcoatRoughness.value=S.clearcoatRoughness,S.clearcoatMap&&(E.clearcoatMap.value=S.clearcoatMap,i(S.clearcoatMap,E.clearcoatMapTransform)),S.clearcoatRoughnessMap&&(E.clearcoatRoughnessMap.value=S.clearcoatRoughnessMap,i(S.clearcoatRoughnessMap,E.clearcoatRoughnessMapTransform)),S.clearcoatNormalMap&&(E.clearcoatNormalMap.value=S.clearcoatNormalMap,i(S.clearcoatNormalMap,E.clearcoatNormalMapTransform),E.clearcoatNormalScale.value.copy(S.clearcoatNormalScale),S.side===Qn&&E.clearcoatNormalScale.value.negate())),S.dispersion>0&&(E.dispersion.value=S.dispersion),S.iridescence>0&&(E.iridescence.value=S.iridescence,E.iridescenceIOR.value=S.iridescenceIOR,E.iridescenceThicknessMinimum.value=S.iridescenceThicknessRange[0],E.iridescenceThicknessMaximum.value=S.iridescenceThicknessRange[1],S.iridescenceMap&&(E.iridescenceMap.value=S.iridescenceMap,i(S.iridescenceMap,E.iridescenceMapTransform)),S.iridescenceThicknessMap&&(E.iridescenceThicknessMap.value=S.iridescenceThicknessMap,i(S.iridescenceThicknessMap,E.iridescenceThicknessMapTransform))),S.transmission>0&&(E.transmission.value=S.transmission,E.transmissionSamplerMap.value=F.texture,E.transmissionSamplerSize.value.set(F.width,F.height),S.transmissionMap&&(E.transmissionMap.value=S.transmissionMap,i(S.transmissionMap,E.transmissionMapTransform)),E.thickness.value=S.thickness,S.thicknessMap&&(E.thicknessMap.value=S.thicknessMap,i(S.thicknessMap,E.thicknessMapTransform)),E.attenuationDistance.value=S.attenuationDistance,E.attenuationColor.value.copy(S.attenuationColor)),S.anisotropy>0&&(E.anisotropyVector.value.set(S.anisotropy*Math.cos(S.anisotropyRotation),S.anisotropy*Math.sin(S.anisotropyRotation)),S.anisotropyMap&&(E.anisotropyMap.value=S.anisotropyMap,i(S.anisotropyMap,E.anisotropyMapTransform))),E.specularIntensity.value=S.specularIntensity,E.specularColor.value.copy(S.specularColor),S.specularColorMap&&(E.specularColorMap.value=S.specularColorMap,i(S.specularColorMap,E.specularColorMapTransform)),S.specularIntensityMap&&(E.specularIntensityMap.value=S.specularIntensityMap,i(S.specularIntensityMap,E.specularIntensityMapTransform))}function T(E,S){S.matcap&&(E.matcap.value=S.matcap)}function w(E,S){const F=t.get(S).light;E.referencePosition.value.setFromMatrixPosition(F.matrixWorld),E.nearDistance.value=F.shadow.camera.near,E.farDistance.value=F.shadow.camera.far}return{refreshFogUniforms:r,refreshMaterialUniforms:l}}function D1(s,t,i,r){let l={},u={},f=[];const p=s.getParameter(s.MAX_UNIFORM_BUFFER_BINDINGS);function m(C,N){const D=N.program;r.uniformBlockBinding(C,D)}function d(C,N){let D=l[C.id];D===void 0&&(E(C),D=g(C),l[C.id]=D,C.addEventListener("dispose",F));const O=N.program;r.updateUBOMapping(C,O);const b=t.render.frame;u[C.id]!==b&&(_(C),u[C.id]=b)}function g(C){const N=v();C.__bindingPointIndex=N;const D=s.createBuffer(),O=C.__size,b=C.usage;return s.bindBuffer(s.UNIFORM_BUFFER,D),s.bufferData(s.UNIFORM_BUFFER,O,b),s.bindBuffer(s.UNIFORM_BUFFER,null),s.bindBufferBase(s.UNIFORM_BUFFER,N,D),D}function v(){for(let C=0;C<p;C++)if(f.indexOf(C)===-1)return f.push(C),C;return be("WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function _(C){const N=l[C.id],D=C.uniforms,O=C.__cache;s.bindBuffer(s.UNIFORM_BUFFER,N);for(let b=0,P=D.length;b<P;b++){const q=D[b];if(Array.isArray(q))for(let G=0,Z=q.length;G<Z;G++)M(q[G],b,G,O);else M(q,b,0,O)}s.bindBuffer(s.UNIFORM_BUFFER,null)}function M(C,N,D,O){if(w(C,N,D,O)===!0){const b=C.__offset,P=C.value;if(Array.isArray(P)){let q=0;for(let G=0;G<P.length;G++){const Z=P[G],ht=S(Z);T(Z,C.__data,q),typeof Z!="number"&&typeof Z!="boolean"&&!Z.isMatrix3&&!ArrayBuffer.isView(Z)&&(q+=ht.storage/Float32Array.BYTES_PER_ELEMENT)}}else T(P,C.__data,0);s.bufferSubData(s.UNIFORM_BUFFER,b,C.__data)}}function T(C,N,D){typeof C=="number"||typeof C=="boolean"?N[0]=C:C.isMatrix3?(N[0]=C.elements[0],N[1]=C.elements[1],N[2]=C.elements[2],N[3]=0,N[4]=C.elements[3],N[5]=C.elements[4],N[6]=C.elements[5],N[7]=0,N[8]=C.elements[6],N[9]=C.elements[7],N[10]=C.elements[8],N[11]=0):ArrayBuffer.isView(C)?N.set(new C.constructor(C.buffer,C.byteOffset,N.length)):C.toArray(N,D)}function w(C,N,D,O){const b=C.value,P=N+"_"+D;if(O[P]===void 0)return typeof b=="number"||typeof b=="boolean"?O[P]=b:ArrayBuffer.isView(b)?O[P]=b.slice():O[P]=b.clone(),!0;{const q=O[P];if(typeof b=="number"||typeof b=="boolean"){if(q!==b)return O[P]=b,!0}else{if(ArrayBuffer.isView(b))return!0;if(q.equals(b)===!1)return q.copy(b),!0}}return!1}function E(C){const N=C.uniforms;let D=0;const O=16;for(let P=0,q=N.length;P<q;P++){const G=Array.isArray(N[P])?N[P]:[N[P]];for(let Z=0,ht=G.length;Z<ht;Z++){const mt=G[Z],J=Array.isArray(mt.value)?mt.value:[mt.value];for(let I=0,H=J.length;I<H;I++){const j=J[I],gt=S(j),Et=D%O,L=Et%gt.boundary,K=Et+L;D+=L,K!==0&&O-K<gt.storage&&(D+=O-K),mt.__data=new Float32Array(gt.storage/Float32Array.BYTES_PER_ELEMENT),mt.__offset=D,D+=gt.storage}}}const b=D%O;return b>0&&(D+=O-b),C.__size=D,C.__cache={},this}function S(C){const N={boundary:0,storage:0};return typeof C=="number"||typeof C=="boolean"?(N.boundary=4,N.storage=4):C.isVector2?(N.boundary=8,N.storage=8):C.isVector3||C.isColor?(N.boundary=16,N.storage=12):C.isVector4?(N.boundary=16,N.storage=16):C.isMatrix3?(N.boundary=48,N.storage=48):C.isMatrix4?(N.boundary=64,N.storage=64):C.isTexture?te("WebGLRenderer: Texture samplers can not be part of an uniforms group."):ArrayBuffer.isView(C)?(N.boundary=16,N.storage=C.byteLength):te("WebGLRenderer: Unsupported uniform value type.",C),N}function F(C){const N=C.target;N.removeEventListener("dispose",F);const D=f.indexOf(N.__bindingPointIndex);f.splice(D,1),s.deleteBuffer(l[N.id]),delete l[N.id],delete u[N.id]}function z(){for(const C in l)s.deleteBuffer(l[C]);f=[],l={},u={}}return{bind:m,update:d,dispose:z}}const U1=new Uint16Array([12469,15057,12620,14925,13266,14620,13807,14376,14323,13990,14545,13625,14713,13328,14840,12882,14931,12528,14996,12233,15039,11829,15066,11525,15080,11295,15085,10976,15082,10705,15073,10495,13880,14564,13898,14542,13977,14430,14158,14124,14393,13732,14556,13410,14702,12996,14814,12596,14891,12291,14937,11834,14957,11489,14958,11194,14943,10803,14921,10506,14893,10278,14858,9960,14484,14039,14487,14025,14499,13941,14524,13740,14574,13468,14654,13106,14743,12678,14818,12344,14867,11893,14889,11509,14893,11180,14881,10751,14852,10428,14812,10128,14765,9754,14712,9466,14764,13480,14764,13475,14766,13440,14766,13347,14769,13070,14786,12713,14816,12387,14844,11957,14860,11549,14868,11215,14855,10751,14825,10403,14782,10044,14729,9651,14666,9352,14599,9029,14967,12835,14966,12831,14963,12804,14954,12723,14936,12564,14917,12347,14900,11958,14886,11569,14878,11247,14859,10765,14828,10401,14784,10011,14727,9600,14660,9289,14586,8893,14508,8533,15111,12234,15110,12234,15104,12216,15092,12156,15067,12010,15028,11776,14981,11500,14942,11205,14902,10752,14861,10393,14812,9991,14752,9570,14682,9252,14603,8808,14519,8445,14431,8145,15209,11449,15208,11451,15202,11451,15190,11438,15163,11384,15117,11274,15055,10979,14994,10648,14932,10343,14871,9936,14803,9532,14729,9218,14645,8742,14556,8381,14461,8020,14365,7603,15273,10603,15272,10607,15267,10619,15256,10631,15231,10614,15182,10535,15118,10389,15042,10167,14963,9787,14883,9447,14800,9115,14710,8665,14615,8318,14514,7911,14411,7507,14279,7198,15314,9675,15313,9683,15309,9712,15298,9759,15277,9797,15229,9773,15166,9668,15084,9487,14995,9274,14898,8910,14800,8539,14697,8234,14590,7790,14479,7409,14367,7067,14178,6621,15337,8619,15337,8631,15333,8677,15325,8769,15305,8871,15264,8940,15202,8909,15119,8775,15022,8565,14916,8328,14804,8009,14688,7614,14569,7287,14448,6888,14321,6483,14088,6171,15350,7402,15350,7419,15347,7480,15340,7613,15322,7804,15287,7973,15229,8057,15148,8012,15046,7846,14933,7611,14810,7357,14682,7069,14552,6656,14421,6316,14251,5948,14007,5528,15356,5942,15356,5977,15353,6119,15348,6294,15332,6551,15302,6824,15249,7044,15171,7122,15070,7050,14949,6861,14818,6611,14679,6349,14538,6067,14398,5651,14189,5311,13935,4958,15359,4123,15359,4153,15356,4296,15353,4646,15338,5160,15311,5508,15263,5829,15188,6042,15088,6094,14966,6001,14826,5796,14678,5543,14527,5287,14377,4985,14133,4586,13869,4257,15360,1563,15360,1642,15358,2076,15354,2636,15341,3350,15317,4019,15273,4429,15203,4732,15105,4911,14981,4932,14836,4818,14679,4621,14517,4386,14359,4156,14083,3795,13808,3437,15360,122,15360,137,15358,285,15355,636,15344,1274,15322,2177,15281,2765,15215,3223,15120,3451,14995,3569,14846,3567,14681,3466,14511,3305,14344,3121,14037,2800,13753,2467,15360,0,15360,1,15359,21,15355,89,15346,253,15325,479,15287,796,15225,1148,15133,1492,15008,1749,14856,1882,14685,1886,14506,1783,14324,1608,13996,1398,13702,1183]);let ki=null;function L1(){return ki===null&&(ki=new dM(U1,16,16,Zr,Ra),ki.name="DFG_LUT",ki.minFilter=In,ki.magFilter=In,ki.wrapS=ba,ki.wrapT=ba,ki.generateMipmaps=!1,ki.needsUpdate=!0),ki}class N1{constructor(t={}){const{canvas:i=ky(),context:r=null,depth:l=!0,stencil:u=!1,alpha:f=!1,antialias:p=!1,premultipliedAlpha:m=!0,preserveDrawingBuffer:d=!1,powerPreference:g="default",failIfMajorPerformanceCaveat:v=!1,reversedDepthBuffer:_=!1,outputBufferType:M=fi}=t;this.isWebGLRenderer=!0;let T;if(r!==null){if(typeof WebGLRenderingContext<"u"&&r instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");T=r.getContextAttributes().alpha}else T=f;const w=M,E=new Set([Qd,Kd,Zd]),S=new Set([fi,Ki,il,al,qd,Yd]),F=new Uint32Array(4),z=new Int32Array(4),C=new $;let N=null,D=null;const O=[],b=[];let P=null;this.domElement=i,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this.toneMapping=Yi,this.toneMappingExposure=1,this.transmissionResolutionScale=1;const q=this;let G=!1,Z=null,ht=null,mt=null,J=null;this._outputColorSpace=ci;let I=0,H=0,j=null,gt=-1,Et=null;const L=new tn,K=new tn;let Mt=null;const Rt=new xe(0);let Pt=0,at=i.width,xt=i.height,yt=1,Bt=null,ee=null;const Kt=new tn(0,0,at,xt),qe=new tn(0,0,at,xt);let ce=!1;const Se=new ep;let ye=!1,fe=!1;const en=new $e,nn=new $,an=new tn,ln={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let We=!1;function rn(){return j===null?yt:1}let W=r;function ze(A,X){return i.getContext(A,X)}try{const A={alpha:!0,depth:l,stencil:u,antialias:p,premultipliedAlpha:m,preserveDrawingBuffer:d,powerPreference:g,failIfMajorPerformanceCaveat:v};if("setAttribute"in i&&i.setAttribute("data-engine",`three.js r${Xd}`),i.addEventListener("webglcontextlost",Ke,!1),i.addEventListener("webglcontextrestored",Ue,!1),i.addEventListener("webglcontextcreationerror",Jn,!1),W===null){const X="webgl2";if(W=ze(X,A),W===null)throw ze(X)?new Error("THREE.WebGLRenderer: Error creating WebGL context with your selected attributes."):new Error("THREE.WebGLRenderer: Error creating WebGL context.")}}catch(A){throw be("WebGLRenderer: "+A.message),A}let Ce,U,y,Q,rt,ct,bt,wt,ut,ft,At,Ft,Lt,Dt,Zt,Qt,ne,k,Tt,pt,Ct,It,St;function Wt(){Ce=new LT(W),Ce.init(),Ct=new E1(W,Ce),U=new bT(W,Ce,t,Ct),y=new y1(W,Ce),U.reversedDepthBuffer&&_&&y.buffers.depth.setReversed(!0),ht=W.createFramebuffer(),mt=W.createFramebuffer(),J=W.createFramebuffer(),Q=new PT(W),rt=new o1,ct=new M1(W,Ce,y,rt,U,Ct,Q),bt=new UT(q),wt=new BM(W),It=new MT(W,wt),ut=new NT(W,wt,Q,It),ft=new FT(W,ut,wt,It,Q),k=new IT(W,U,ct),Zt=new TT(rt),At=new s1(q,bt,Ce,U,It,Zt),Ft=new w1(q,rt),Lt=new u1,Dt=new m1(Ce),ne=new yT(q,bt,y,ft,T,m),Qt=new S1(q,ft,U),St=new D1(W,Q,U,y),Tt=new ET(W,Ce,Q),pt=new OT(W,Ce,Q),Q.programs=At.programs,q.capabilities=U,q.extensions=Ce,q.properties=rt,q.renderLists=Lt,q.shadowMap=Qt,q.state=y,q.info=Q}Wt(),w!==fi&&(P=new BT(w,i.width,i.height,p,l,u));const Gt=new R1(q,W);this.xr=Gt,this.getContext=function(){return W},this.getContextAttributes=function(){return W.getContextAttributes()},this.forceContextLoss=function(){const A=Ce.get("WEBGL_lose_context");A&&A.loseContext()},this.forceContextRestore=function(){const A=Ce.get("WEBGL_lose_context");A&&A.restoreContext()},this.getPixelRatio=function(){return yt},this.setPixelRatio=function(A){A!==void 0&&(yt=A,this.setSize(at,xt,!1))},this.getSize=function(A){return A.set(at,xt)},this.setSize=function(A,X,st=!0){if(Gt.isPresenting){te("WebGLRenderer: Can't change size while VR device is presenting.");return}at=A,xt=X,i.width=Math.floor(A*yt),i.height=Math.floor(X*yt),st===!0&&(i.style.width=A+"px",i.style.height=X+"px"),P!==null&&P.setSize(i.width,i.height),this.setViewport(0,0,A,X)},this.getDrawingBufferSize=function(A){return A.set(at*yt,xt*yt).floor()},this.setDrawingBufferSize=function(A,X,st){at=A,xt=X,yt=st,i.width=Math.floor(A*st),i.height=Math.floor(X*st),this.setViewport(0,0,A,X)},this.setEffects=function(A){if(w===fi){be("WebGLRenderer: setEffects() requires outputBufferType set to HalfFloatType or FloatType.");return}if(A){for(let X=0;X<A.length;X++)if(A[X].isOutputPass===!0){te("WebGLRenderer: OutputPass is not needed in setEffects(). Tone mapping and color space conversion are applied automatically.");break}}P.setEffects(A||[])},this.getCurrentViewport=function(A){return A.copy(L)},this.getViewport=function(A){return A.copy(Kt)},this.setViewport=function(A,X,st,nt){A.isVector4?Kt.set(A.x,A.y,A.z,A.w):Kt.set(A,X,st,nt),y.viewport(L.copy(Kt).multiplyScalar(yt).round())},this.getScissor=function(A){return A.copy(qe)},this.setScissor=function(A,X,st,nt){A.isVector4?qe.set(A.x,A.y,A.z,A.w):qe.set(A,X,st,nt),y.scissor(K.copy(qe).multiplyScalar(yt).round())},this.getScissorTest=function(){return ce},this.setScissorTest=function(A){y.setScissorTest(ce=A)},this.setOpaqueSort=function(A){Bt=A},this.setTransparentSort=function(A){ee=A},this.getClearColor=function(A){return A.copy(ne.getClearColor())},this.setClearColor=function(){ne.setClearColor(...arguments)},this.getClearAlpha=function(){return ne.getClearAlpha()},this.setClearAlpha=function(){ne.setClearAlpha(...arguments)},this.clear=function(A=!0,X=!0,st=!0){let nt=0;if(A){let it=!1;if(j!==null){const Nt=j.texture.format;it=E.has(Nt)}if(it){const Nt=j.texture.type,Ht=S.has(Nt),Ut=ne.getClearColor(),kt=ne.getClearAlpha(),Vt=Ut.r,Jt=Ut.g,se=Ut.b;Ht?(F[0]=Vt,F[1]=Jt,F[2]=se,F[3]=kt,W.clearBufferuiv(W.COLOR,0,F)):(z[0]=Vt,z[1]=Jt,z[2]=se,z[3]=kt,W.clearBufferiv(W.COLOR,0,z))}else nt|=W.COLOR_BUFFER_BIT}X&&(nt|=W.DEPTH_BUFFER_BIT,this.state.buffers.depth.setMask(!0)),st&&(nt|=W.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),nt!==0&&W.clear(nt)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.setNodesHandler=function(A){A.setRenderer(this),Z=A},this.dispose=function(){i.removeEventListener("webglcontextlost",Ke,!1),i.removeEventListener("webglcontextrestored",Ue,!1),i.removeEventListener("webglcontextcreationerror",Jn,!1),ne.dispose(),Lt.dispose(),Dt.dispose(),rt.dispose(),bt.dispose(),ft.dispose(),It.dispose(),St.dispose(),At.dispose(),Gt.dispose(),Gt.removeEventListener("sessionstart",fn),Gt.removeEventListener("sessionend",Tn),Gn.stop()};function Ke(A){A.preventDefault(),o0("WebGLRenderer: Context Lost."),G=!0}function Ue(){o0("WebGLRenderer: Context Restored."),G=!1;const A=Q.autoReset,X=Qt.enabled,st=Qt.autoUpdate,nt=Qt.needsUpdate,it=Qt.type;Wt(),Q.autoReset=A,Qt.enabled=X,Qt.autoUpdate=st,Qt.needsUpdate=nt,Qt.type=it}function Jn(A){be("WebGLRenderer: A WebGL context could not be created. Reason: ",A.statusMessage)}function jn(A){const X=A.target;X.removeEventListener("dispose",jn),$s(X)}function $s(A){to(A),rt.remove(A)}function to(A){const X=rt.get(A).programs;X!==void 0&&(X.forEach(function(st){At.releaseProgram(st)}),A.isShaderMaterial&&At.releaseShaderCache(A))}this.renderBufferDirect=function(A,X,st,nt,it,Nt){X===null&&(X=ln);const Ht=it.isMesh&&it.matrixWorld.determinantAffine()<0,Ut=Ua(A,X,st,nt,it);y.setMaterial(nt,Ht);let kt=st.index,Vt=1;if(nt.wireframe===!0){if(kt=ut.getWireframeAttribute(st),kt===void 0)return;Vt=2}const Jt=st.drawRange,se=st.attributes.position;let Yt=Jt.start*Vt,Te=(Jt.start+Jt.count)*Vt;Nt!==null&&(Yt=Math.max(Yt,Nt.start*Vt),Te=Math.min(Te,(Nt.start+Nt.count)*Vt)),kt!==null?(Yt=Math.max(Yt,0),Te=Math.min(Te,kt.count)):se!=null&&(Yt=Math.max(Yt,0),Te=Math.min(Te,se.count));const Qe=Te-Yt;if(Qe<0||Qe===1/0)return;It.setup(it,nt,Ut,st,kt);let ke,Le=Tt;if(kt!==null&&(ke=wt.get(kt),Le=pt,Le.setIndex(ke)),it.isMesh)nt.wireframe===!0?(y.setLineWidth(nt.wireframeLinewidth*rn()),Le.setMode(W.LINES)):Le.setMode(W.TRIANGLES);else if(it.isLine){let Ne=nt.linewidth;Ne===void 0&&(Ne=1),y.setLineWidth(Ne*rn()),it.isLineSegments?Le.setMode(W.LINES):it.isLineLoop?Le.setMode(W.LINE_LOOP):Le.setMode(W.LINE_STRIP)}else it.isPoints?Le.setMode(W.POINTS):it.isSprite&&Le.setMode(W.TRIANGLES);if(it.isBatchedMesh)if(Ce.get("WEBGL_multi_draw"))Le.renderMultiDraw(it._multiDrawStarts,it._multiDrawCounts,it._multiDrawCount);else{const Ne=it._multiDrawStarts,zt=it._multiDrawCounts,Ln=it._multiDrawCount,he=kt?wt.get(kt).bytesPerElement:1,vn=rt.get(nt).currentProgram.getUniforms();for(let $n=0;$n<Ln;$n++)vn.setValue(W,"_gl_DrawID",$n),Le.render(Ne[$n]/he,zt[$n])}else if(it.isInstancedMesh)Le.renderInstances(Yt,Qe,it.count);else if(st.isInstancedBufferGeometry){const Ne=st._maxInstanceCount!==void 0?st._maxInstanceCount:1/0,zt=Math.min(st.instanceCount,Ne);Le.renderInstances(Yt,Qe,zt)}else Le.render(Yt,Qe)};function eo(A,X,st){A.transparent===!0&&A.side===Ea&&A.forceSinglePass===!1?(A.side=Qn,A.needsUpdate=!0,Da(A,X,st),A.side=fr,A.needsUpdate=!0,Da(A,X,st),A.side=Ea):Da(A,X,st)}this.compile=function(A,X,st=null){st===null&&(st=A),D=Dt.get(st),D.init(X),b.push(D),st.traverseVisible(function(it){it.isLight&&it.layers.test(X.layers)&&(D.pushLight(it),it.castShadow&&D.pushShadow(it))}),A!==st&&A.traverseVisible(function(it){it.isLight&&it.layers.test(X.layers)&&(D.pushLight(it),it.castShadow&&D.pushShadow(it))}),D.setupLights();const nt=new Set;return A.traverse(function(it){if(!(it.isMesh||it.isPoints||it.isLine||it.isSprite))return;const Nt=it.material;if(Nt)if(Array.isArray(Nt))for(let Ht=0;Ht<Nt.length;Ht++){const Ut=Nt[Ht];eo(Ut,st,it),nt.add(Ut)}else eo(Nt,st,it),nt.add(Nt)}),D=b.pop(),nt},this.compileAsync=function(A,X,st=null){const nt=this.compile(A,X,st);return new Promise(it=>{function Nt(){if(nt.forEach(function(Ht){rt.get(Ht).currentProgram.isReady()&&nt.delete(Ht)}),nt.size===0){it(A);return}setTimeout(Nt,10)}Ce.get("KHR_parallel_shader_compile")!==null?Nt():setTimeout(Nt,10)})};let Kr=null;function Ii(A){Kr&&Kr(A)}function fn(){Gn.stop()}function Tn(){Gn.start()}const Gn=new Gv;Gn.setAnimationLoop(Ii),typeof self<"u"&&Gn.setContext(self),this.setAnimationLoop=function(A){Kr=A,Gt.setAnimationLoop(A),A===null?Gn.stop():Gn.start()},Gt.addEventListener("sessionstart",fn),Gt.addEventListener("sessionend",Tn),this.render=function(A,X){if(X!==void 0&&X.isCamera!==!0){be("WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(G===!0)return;Z!==null&&Z.renderStart(A,X);const st=Gt.enabled===!0&&Gt.isPresenting===!0,nt=P!==null&&(j===null||st)&&P.begin(q,j);if(A.matrixWorldAutoUpdate===!0&&A.updateMatrixWorld(),X.parent===null&&X.matrixWorldAutoUpdate===!0&&X.updateMatrixWorld(),Gt.enabled===!0&&Gt.isPresenting===!0&&(P===null||P.isCompositing()===!1)&&(Gt.cameraAutoUpdate===!0&&Gt.updateCamera(X),X=Gt.getCamera()),A.isScene===!0&&A.onBeforeRender(q,A,X,j),D=Dt.get(A,b.length),D.init(X),D.state.textureUnits=ct.getTextureUnits(),b.push(D),en.multiplyMatrices(X.projectionMatrix,X.matrixWorldInverse),Se.setFromProjectionMatrix(en,qi,X.reversedDepth),fe=this.localClippingEnabled,ye=Zt.init(this.clippingPlanes,fe),N=Lt.get(A,O.length),N.init(),O.push(N),Gt.enabled===!0&&Gt.isPresenting===!0){const Ht=q.xr.getDepthSensingMesh();Ht!==null&&mr(Ht,X,-1/0,q.sortObjects)}mr(A,X,0,q.sortObjects),N.finish(),q.sortObjects===!0&&N.sort(Bt,ee,X.reversedDepth),We=Gt.enabled===!1||Gt.isPresenting===!1||Gt.hasDepthSensing()===!1,We&&ne.addToRenderList(N,A),this.info.render.frame++,this.info.autoReset===!0&&this.info.reset(),ye===!0&&Zt.beginShadows();const it=D.state.shadowsArray;if(Qt.render(it,A,X),ye===!0&&Zt.endShadows(),(nt&&P.hasRenderPass())===!1){const Ht=N.opaque,Ut=N.transmissive;if(D.setupLights(),X.isArrayCamera){const kt=X.cameras;if(Ut.length>0)for(let Vt=0,Jt=kt.length;Vt<Jt;Vt++){const se=kt[Vt];ul(Ht,Ut,A,se)}We&&ne.render(A);for(let Vt=0,Jt=kt.length;Vt<Jt;Vt++){const se=kt[Vt];ll(N,A,se,se.viewport)}}else Ut.length>0&&ul(Ht,Ut,A,X),We&&ne.render(A),ll(N,A,X)}j!==null&&H===0&&(ct.updateMultisampleRenderTarget(j),ct.updateRenderTargetMipmap(j)),nt&&P.end(q),A.isScene===!0&&A.onAfterRender(q,A,X),It.resetDefaultState(),gt=-1,Et=null,b.pop(),b.length>0?(D=b[b.length-1],ct.setTextureUnits(D.state.textureUnits),ye===!0&&Zt.setGlobalState(q.clippingPlanes,D.state.camera)):D=null,O.pop(),O.length>0?N=O[O.length-1]:N=null,Z!==null&&Z.renderEnd()};function mr(A,X,st,nt){if(A.visible===!1)return;if(A.layers.test(X.layers)){if(A.isGroup)st=A.renderOrder;else if(A.isLOD)A.autoUpdate===!0&&A.update(X);else if(A.isLightProbeGrid)D.pushLightProbeGrid(A);else if(A.isLight)D.pushLight(A),A.castShadow&&D.pushShadow(A);else if(A.isSprite){if(!A.frustumCulled||Se.intersectsSprite(A)){nt&&an.setFromMatrixPosition(A.matrixWorld).applyMatrix4(en);const Ht=ft.update(A),Ut=A.material;Ut.visible&&N.push(A,Ht,Ut,st,an.z,null)}}else if((A.isMesh||A.isLine||A.isPoints)&&(!A.frustumCulled||Se.intersectsObject(A))){const Ht=ft.update(A),Ut=A.material;if(nt&&(A.boundingSphere!==void 0?(A.boundingSphere===null&&A.computeBoundingSphere(),an.copy(A.boundingSphere.center)):(Ht.boundingSphere===null&&Ht.computeBoundingSphere(),an.copy(Ht.boundingSphere.center)),an.applyMatrix4(A.matrixWorld).applyMatrix4(en)),Array.isArray(Ut)){const kt=Ht.groups;for(let Vt=0,Jt=kt.length;Vt<Jt;Vt++){const se=kt[Vt],Yt=Ut[se.materialIndex];Yt&&Yt.visible&&N.push(A,Ht,Yt,st,an.z,se)}}else Ut.visible&&N.push(A,Ht,Ut,st,an.z,null)}}const Nt=A.children;for(let Ht=0,Ut=Nt.length;Ht<Ut;Ht++)mr(Nt[Ht],X,st,nt)}function ll(A,X,st,nt){const{opaque:it,transmissive:Nt,transparent:Ht}=A;D.setupLightsView(st),ye===!0&&Zt.setGlobalState(q.clippingPlanes,st),nt&&y.viewport(L.copy(nt)),it.length>0&&gr(it,X,st),Nt.length>0&&gr(Nt,X,st),Ht.length>0&&gr(Ht,X,st),y.buffers.depth.setTest(!0),y.buffers.depth.setMask(!0),y.buffers.color.setMask(!0),y.setPolygonOffset(!1)}function ul(A,X,st,nt){if((st.isScene===!0?st.overrideMaterial:null)!==null)return;if(D.state.transmissionRenderTarget[nt.id]===void 0){const Yt=Ce.has("EXT_color_buffer_half_float")||Ce.has("EXT_color_buffer_float");D.state.transmissionRenderTarget[nt.id]=new Zi(1,1,{generateMipmaps:!0,type:Yt?Ra:fi,minFilter:Wr,samples:Math.max(4,U.samples),stencilBuffer:u,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Ee.workingColorSpace})}const Nt=D.state.transmissionRenderTarget[nt.id],Ht=nt.viewport||L;Nt.setSize(Ht.z*q.transmissionResolutionScale,Ht.w*q.transmissionResolutionScale);const Ut=q.getRenderTarget(),kt=q.getActiveCubeFace(),Vt=q.getActiveMipmapLevel();q.setRenderTarget(Nt),q.getClearColor(Rt),Pt=q.getClearAlpha(),Pt<1&&q.setClearColor(16777215,.5),q.clear(),We&&ne.render(st);const Jt=q.toneMapping;q.toneMapping=Yi;const se=nt.viewport;if(nt.viewport!==void 0&&(nt.viewport=void 0),D.setupLightsView(nt),ye===!0&&Zt.setGlobalState(q.clippingPlanes,nt),gr(A,st,nt),ct.updateMultisampleRenderTarget(Nt),ct.updateRenderTargetMipmap(Nt),Ce.has("WEBGL_multisampled_render_to_texture")===!1){let Yt=!1;for(let Te=0,Qe=X.length;Te<Qe;Te++){const ke=X[Te],{object:Le,geometry:Ne,material:zt,group:Ln}=ke;if(zt.side===Ea&&Le.layers.test(nt.layers)){const he=zt.side;zt.side=Qn,zt.needsUpdate=!0,wa(Le,st,nt,Ne,zt,Ln),zt.side=he,zt.needsUpdate=!0,Yt=!0}}Yt===!0&&(ct.updateMultisampleRenderTarget(Nt),ct.updateRenderTargetMipmap(Nt))}q.setRenderTarget(Ut,kt,Vt),q.setClearColor(Rt,Pt),se!==void 0&&(nt.viewport=se),q.toneMapping=Jt}function gr(A,X,st){const nt=X.isScene===!0?X.overrideMaterial:null;for(let it=0,Nt=A.length;it<Nt;it++){const Ht=A[it],{object:Ut,geometry:kt,group:Vt}=Ht;let Jt=Ht.material;Jt.allowOverride===!0&&nt!==null&&(Jt=nt),Ut.layers.test(st.layers)&&wa(Ut,X,st,kt,Jt,Vt)}}function wa(A,X,st,nt,it,Nt){A.onBeforeRender(q,X,st,nt,it,Nt),A.modelViewMatrix.multiplyMatrices(st.matrixWorldInverse,A.matrixWorld),A.normalMatrix.getNormalMatrix(A.modelViewMatrix),it.onBeforeRender(q,X,st,nt,A,Nt),it.transparent===!0&&it.side===Ea&&it.forceSinglePass===!1?(it.side=Qn,it.needsUpdate=!0,q.renderBufferDirect(st,X,nt,it,A,Nt),it.side=fr,it.needsUpdate=!0,q.renderBufferDirect(st,X,nt,it,A,Nt),it.side=Ea):q.renderBufferDirect(st,X,nt,it,A,Nt),A.onAfterRender(q,X,st,nt,it,Nt)}function Da(A,X,st){X.isScene!==!0&&(X=ln);const nt=rt.get(A),it=D.state.lights,Nt=D.state.shadowsArray,Ht=it.state.version,Ut=At.getParameters(A,it.state,Nt,X,st,D.state.lightProbeGridArray),kt=At.getProgramCacheKey(Ut);let Vt=nt.programs;nt.environment=A.isMeshStandardMaterial||A.isMeshLambertMaterial||A.isMeshPhongMaterial?X.environment:null,nt.fog=X.fog;const Jt=A.isMeshStandardMaterial||A.isMeshLambertMaterial&&!A.envMap||A.isMeshPhongMaterial&&!A.envMap;nt.envMap=bt.get(A.envMap||nt.environment,Jt),nt.envMapRotation=nt.environment!==null&&A.envMap===null?X.environmentRotation:A.envMapRotation,Vt===void 0&&(A.addEventListener("dispose",jn),Vt=new Map,nt.programs=Vt);let se=Vt.get(kt);if(se!==void 0){if(nt.currentProgram===se&&nt.lightsStateVersion===Ht)return $i(A,Ut),se}else Ut.uniforms=At.getUniforms(A),Z!==null&&A.isNodeMaterial&&Z.build(A,st,Ut),A.onBeforeCompile(Ut,q),se=At.acquireProgram(Ut,kt),Vt.set(kt,se),nt.uniforms=Ut.uniforms;const Yt=nt.uniforms;return(!A.isShaderMaterial&&!A.isRawShaderMaterial||A.clipping===!0)&&(Yt.clippingPlanes=Zt.uniform),$i(A,Ut),nt.needsLights=cl(A),nt.lightsStateVersion=Ht,nt.needsLights&&(Yt.ambientLightColor.value=it.state.ambient,Yt.lightProbe.value=it.state.probe,Yt.directionalLights.value=it.state.directional,Yt.directionalLightShadows.value=it.state.directionalShadow,Yt.spotLights.value=it.state.spot,Yt.spotLightShadows.value=it.state.spotShadow,Yt.rectAreaLights.value=it.state.rectArea,Yt.ltc_1.value=it.state.rectAreaLTC1,Yt.ltc_2.value=it.state.rectAreaLTC2,Yt.pointLights.value=it.state.point,Yt.pointLightShadows.value=it.state.pointShadow,Yt.hemisphereLights.value=it.state.hemi,Yt.directionalShadowMatrix.value=it.state.directionalShadowMatrix,Yt.spotLightMatrix.value=it.state.spotLightMatrix,Yt.spotLightMap.value=it.state.spotLightMap,Yt.pointShadowMatrix.value=it.state.pointShadowMatrix),nt.lightProbeGrid=D.state.lightProbeGridArray.length>0,nt.currentProgram=se,nt.uniformsList=null,se}function ji(A){if(A.uniformsList===null){const X=A.currentProgram.getUniforms();A.uniformsList=Zu.seqWithValue(X.seq,A.uniforms)}return A.uniformsList}function $i(A,X){const st=rt.get(A);st.outputColorSpace=X.outputColorSpace,st.batching=X.batching,st.batchingColor=X.batchingColor,st.instancing=X.instancing,st.instancingColor=X.instancingColor,st.instancingMorph=X.instancingMorph,st.skinning=X.skinning,st.morphTargets=X.morphTargets,st.morphNormals=X.morphNormals,st.morphColors=X.morphColors,st.morphTargetsCount=X.morphTargetsCount,st.numClippingPlanes=X.numClippingPlanes,st.numIntersection=X.numClipIntersection,st.vertexAlphas=X.vertexAlphas,st.vertexTangents=X.vertexTangents,st.toneMapping=X.toneMapping}function _r(A,X){if(A.length===0)return null;if(A.length===1)return A[0].texture!==null?A[0]:null;C.setFromMatrixPosition(X.matrixWorld);for(let st=0,nt=A.length;st<nt;st++){const it=A[st];if(it.texture!==null&&it.boundingBox.containsPoint(C))return it}return null}function Ua(A,X,st,nt,it){X.isScene!==!0&&(X=ln),ct.resetTextureUnits();const Nt=X.fog,Ht=nt.isMeshStandardMaterial||nt.isMeshLambertMaterial||nt.isMeshPhongMaterial?X.environment:null,Ut=j===null?q.outputColorSpace:j.isXRRenderTarget===!0?j.texture.colorSpace:Ee.workingColorSpace,kt=nt.isMeshStandardMaterial||nt.isMeshLambertMaterial&&!nt.envMap||nt.isMeshPhongMaterial&&!nt.envMap,Vt=bt.get(nt.envMap||Ht,kt),Jt=nt.vertexColors===!0&&!!st.attributes.color&&st.attributes.color.itemSize===4,se=!!st.attributes.tangent&&(!!nt.normalMap||nt.anisotropy>0),Yt=!!st.morphAttributes.position,Te=!!st.morphAttributes.normal,Qe=!!st.morphAttributes.color;let ke=Yi;nt.toneMapped&&(j===null||j.isXRRenderTarget===!0)&&(ke=q.toneMapping);const Le=st.morphAttributes.position||st.morphAttributes.normal||st.morphAttributes.color,Ne=Le!==void 0?Le.length:0,zt=rt.get(nt),Ln=D.state.lights;if(ye===!0&&(fe===!0||A!==Et)){const De=A===Et&&nt.id===gt;Zt.setState(nt,A,De)}let he=!1;nt.version===zt.__version?(zt.needsLights&&zt.lightsStateVersion!==Ln.state.version||zt.outputColorSpace!==Ut||it.isBatchedMesh&&zt.batching===!1||!it.isBatchedMesh&&zt.batching===!0||it.isBatchedMesh&&zt.batchingColor===!0&&it.colorTexture===null||it.isBatchedMesh&&zt.batchingColor===!1&&it.colorTexture!==null||it.isInstancedMesh&&zt.instancing===!1||!it.isInstancedMesh&&zt.instancing===!0||it.isSkinnedMesh&&zt.skinning===!1||!it.isSkinnedMesh&&zt.skinning===!0||it.isInstancedMesh&&zt.instancingColor===!0&&it.instanceColor===null||it.isInstancedMesh&&zt.instancingColor===!1&&it.instanceColor!==null||it.isInstancedMesh&&zt.instancingMorph===!0&&it.morphTexture===null||it.isInstancedMesh&&zt.instancingMorph===!1&&it.morphTexture!==null||zt.envMap!==Vt||nt.fog===!0&&zt.fog!==Nt||zt.numClippingPlanes!==void 0&&(zt.numClippingPlanes!==Zt.numPlanes||zt.numIntersection!==Zt.numIntersection)||zt.vertexAlphas!==Jt||zt.vertexTangents!==se||zt.morphTargets!==Yt||zt.morphNormals!==Te||zt.morphColors!==Qe||zt.toneMapping!==ke||zt.morphTargetsCount!==Ne||!!zt.lightProbeGrid!=D.state.lightProbeGridArray.length>0)&&(he=!0):(he=!0,zt.__version=nt.version);let vn=zt.currentProgram;he===!0&&(vn=Da(nt,X,it),Z&&nt.isNodeMaterial&&Z.onUpdateProgram(nt,vn,zt));let $n=!1,bi=!1,ti=!1;const Oe=vn.getUniforms(),Je=zt.uniforms;if(y.useProgram(vn.program)&&($n=!0,bi=!0,ti=!0),nt.id!==gt&&(gt=nt.id,bi=!0),zt.needsLights){const De=_r(D.state.lightProbeGridArray,it);zt.lightProbeGrid!==De&&(zt.lightProbeGrid=De,bi=!0)}if($n||Et!==A){y.buffers.depth.getReversed()&&A.reversedDepth!==!0&&(A._reversedDepth=!0,A.updateProjectionMatrix()),Oe.setValue(W,"projectionMatrix",A.projectionMatrix),Oe.setValue(W,"viewMatrix",A.matrixWorldInverse);const Fi=Oe.map.cameraPosition;Fi!==void 0&&Fi.setValue(W,nn.setFromMatrixPosition(A.matrixWorld)),U.logarithmicDepthBuffer&&Oe.setValue(W,"logDepthBufFC",2/(Math.log(A.far+1)/Math.LN2)),(nt.isMeshPhongMaterial||nt.isMeshToonMaterial||nt.isMeshLambertMaterial||nt.isMeshBasicMaterial||nt.isMeshStandardMaterial||nt.isShaderMaterial)&&Oe.setValue(W,"isOrthographic",A.isOrthographicCamera===!0),Et!==A&&(Et=A,bi=!0,ti=!0)}if(zt.needsLights&&(Ln.state.directionalShadowMap.length>0&&Oe.setValue(W,"directionalShadowMap",Ln.state.directionalShadowMap,ct),Ln.state.spotShadowMap.length>0&&Oe.setValue(W,"spotShadowMap",Ln.state.spotShadowMap,ct),Ln.state.pointShadowMap.length>0&&Oe.setValue(W,"pointShadowMap",Ln.state.pointShadowMap,ct)),it.isSkinnedMesh){Oe.setOptional(W,it,"bindMatrix"),Oe.setOptional(W,it,"bindMatrixInverse");const De=it.skeleton;De&&(De.boneTexture===null&&De.computeBoneTexture(),Oe.setValue(W,"boneTexture",De.boneTexture,ct))}it.isBatchedMesh&&(Oe.setOptional(W,it,"batchingTexture"),Oe.setValue(W,"batchingTexture",it._matricesTexture,ct),Oe.setOptional(W,it,"batchingIdTexture"),Oe.setValue(W,"batchingIdTexture",it._indirectTexture,ct),Oe.setOptional(W,it,"batchingColorTexture"),it._colorsTexture!==null&&Oe.setValue(W,"batchingColorTexture",it._colorsTexture,ct));const Ti=st.morphAttributes;if((Ti.position!==void 0||Ti.normal!==void 0||Ti.color!==void 0)&&k.update(it,st,vn),(bi||zt.receiveShadow!==it.receiveShadow)&&(zt.receiveShadow=it.receiveShadow,Oe.setValue(W,"receiveShadow",it.receiveShadow)),(nt.isMeshStandardMaterial||nt.isMeshLambertMaterial||nt.isMeshPhongMaterial)&&nt.envMap===null&&X.environment!==null&&(Je.envMapIntensity.value=X.environmentIntensity),Je.dfgLUT!==void 0&&(Je.dfgLUT.value=L1()),bi){if(Oe.setValue(W,"toneMappingExposure",q.toneMappingExposure),zt.needsLights&&hn(Je,ti),Nt&&nt.fog===!0&&Ft.refreshFogUniforms(Je,Nt),Ft.refreshMaterialUniforms(Je,nt,yt,xt,D.state.transmissionRenderTarget[A.id]),zt.needsLights&&zt.lightProbeGrid){const De=zt.lightProbeGrid;Je.probesSH.value=De.texture,Je.probesMin.value.copy(De.boundingBox.min),Je.probesMax.value.copy(De.boundingBox.max),Je.probesResolution.value.copy(De.resolution)}Zu.upload(W,ji(zt),Je,ct)}if(nt.isShaderMaterial&&nt.uniformsNeedUpdate===!0&&(Zu.upload(W,ji(zt),Je,ct),nt.uniformsNeedUpdate=!1),nt.isSpriteMaterial&&Oe.setValue(W,"center",it.center),Oe.setValue(W,"modelViewMatrix",it.modelViewMatrix),Oe.setValue(W,"normalMatrix",it.normalMatrix),Oe.setValue(W,"modelMatrix",it.matrixWorld),nt.uniformsGroups!==void 0){const De=nt.uniformsGroups;for(let Fi=0,La=De.length;Fi<La;Fi++){const vr=De[Fi];St.update(vr,vn),St.bind(vr,vn)}}return vn}function hn(A,X){A.ambientLightColor.needsUpdate=X,A.lightProbe.needsUpdate=X,A.directionalLights.needsUpdate=X,A.directionalLightShadows.needsUpdate=X,A.pointLights.needsUpdate=X,A.pointLightShadows.needsUpdate=X,A.spotLights.needsUpdate=X,A.spotLightShadows.needsUpdate=X,A.rectAreaLights.needsUpdate=X,A.hemisphereLights.needsUpdate=X}function cl(A){return A.isMeshLambertMaterial||A.isMeshToonMaterial||A.isMeshPhongMaterial||A.isMeshStandardMaterial||A.isShadowMaterial||A.isShaderMaterial&&A.lights===!0}this.getActiveCubeFace=function(){return I},this.getActiveMipmapLevel=function(){return H},this.getRenderTarget=function(){return j},this.setRenderTargetTextures=function(A,X,st){const nt=rt.get(A);nt.__autoAllocateDepthBuffer=A.resolveDepthBuffer===!1,nt.__autoAllocateDepthBuffer===!1&&(nt.__useRenderToTexture=!1),rt.get(A.texture).__webglTexture=X,rt.get(A.depthTexture).__webglTexture=nt.__autoAllocateDepthBuffer?void 0:st,nt.__hasExternalTextures=!0},this.setRenderTargetFramebuffer=function(A,X){const st=rt.get(A);st.__webglFramebuffer=X,st.__useDefaultFramebuffer=X===void 0},this.setRenderTarget=function(A,X=0,st=0){j=A,I=X,H=st;let nt=null,it=!1,Nt=!1;if(A){const Ut=rt.get(A);if(Ut.__useDefaultFramebuffer!==void 0){y.bindFramebuffer(W.FRAMEBUFFER,Ut.__webglFramebuffer),L.copy(A.viewport),K.copy(A.scissor),Mt=A.scissorTest,y.viewport(L),y.scissor(K),y.setScissorTest(Mt),gt=-1;return}else if(Ut.__webglFramebuffer===void 0)ct.setupRenderTarget(A);else if(Ut.__hasExternalTextures)ct.rebindTextures(A,rt.get(A.texture).__webglTexture,rt.get(A.depthTexture).__webglTexture);else if(A.depthBuffer){const Jt=A.depthTexture;if(Ut.__boundDepthTexture!==Jt){if(Jt!==null&&rt.has(Jt)&&(A.width!==Jt.image.width||A.height!==Jt.image.height))throw new Error("THREE.WebGLRenderer: Attached DepthTexture is initialized to the incorrect size.");ct.setupDepthRenderbuffer(A)}}const kt=A.texture;(kt.isData3DTexture||kt.isDataArrayTexture||kt.isCompressedArrayTexture)&&(Nt=!0);const Vt=rt.get(A).__webglFramebuffer;A.isWebGLCubeRenderTarget?(Array.isArray(Vt[X])?nt=Vt[X][st]:nt=Vt[X],it=!0):A.samples>0&&ct.useMultisampledRTT(A)===!1?nt=rt.get(A).__webglMultisampledFramebuffer:Array.isArray(Vt)?nt=Vt[st]:nt=Vt,L.copy(A.viewport),K.copy(A.scissor),Mt=A.scissorTest}else L.copy(Kt).multiplyScalar(yt).floor(),K.copy(qe).multiplyScalar(yt).floor(),Mt=ce;if(st!==0&&(nt=ht),y.bindFramebuffer(W.FRAMEBUFFER,nt)&&y.drawBuffers(A,nt),y.viewport(L),y.scissor(K),y.setScissorTest(Mt),it){const Ut=rt.get(A.texture);W.framebufferTexture2D(W.FRAMEBUFFER,W.COLOR_ATTACHMENT0,W.TEXTURE_CUBE_MAP_POSITIVE_X+X,Ut.__webglTexture,st)}else if(Nt){const Ut=X;for(let kt=0;kt<A.textures.length;kt++){const Vt=rt.get(A.textures[kt]);W.framebufferTextureLayer(W.FRAMEBUFFER,W.COLOR_ATTACHMENT0+kt,Vt.__webglTexture,st,Ut)}}else if(A!==null&&st!==0){const Ut=rt.get(A.texture);W.framebufferTexture2D(W.FRAMEBUFFER,W.COLOR_ATTACHMENT0,W.TEXTURE_2D,Ut.__webglTexture,st)}gt=-1},this.readRenderTargetPixels=function(A,X,st,nt,it,Nt,Ht,Ut=0){if(!(A&&A.isWebGLRenderTarget)){be("WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let kt=rt.get(A).__webglFramebuffer;if(A.isWebGLCubeRenderTarget&&Ht!==void 0&&(kt=kt[Ht]),kt){y.bindFramebuffer(W.FRAMEBUFFER,kt);try{const Vt=A.textures[Ut],Jt=Vt.format,se=Vt.type;if(A.textures.length>1&&W.readBuffer(W.COLOR_ATTACHMENT0+Ut),!U.textureFormatReadable(Jt)){be("WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!U.textureTypeReadable(se)){be("WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}X>=0&&X<=A.width-nt&&st>=0&&st<=A.height-it&&W.readPixels(X,st,nt,it,Ct.convert(Jt),Ct.convert(se),Nt)}finally{const Vt=j!==null?rt.get(j).__webglFramebuffer:null;y.bindFramebuffer(W.FRAMEBUFFER,Vt)}}},this.readRenderTargetPixelsAsync=async function(A,X,st,nt,it,Nt,Ht,Ut=0){if(!(A&&A.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let kt=rt.get(A).__webglFramebuffer;if(A.isWebGLCubeRenderTarget&&Ht!==void 0&&(kt=kt[Ht]),kt)if(X>=0&&X<=A.width-nt&&st>=0&&st<=A.height-it){y.bindFramebuffer(W.FRAMEBUFFER,kt);const Vt=A.textures[Ut],Jt=Vt.format,se=Vt.type;if(A.textures.length>1&&W.readBuffer(W.COLOR_ATTACHMENT0+Ut),!U.textureFormatReadable(Jt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!U.textureTypeReadable(se))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");const Yt=W.createBuffer();W.bindBuffer(W.PIXEL_PACK_BUFFER,Yt),W.bufferData(W.PIXEL_PACK_BUFFER,Nt.byteLength,W.STREAM_READ),W.readPixels(X,st,nt,it,Ct.convert(Jt),Ct.convert(se),0);const Te=j!==null?rt.get(j).__webglFramebuffer:null;y.bindFramebuffer(W.FRAMEBUFFER,Te);const Qe=W.fenceSync(W.SYNC_GPU_COMMANDS_COMPLETE,0);return W.flush(),await Xy(W,Qe,4),W.bindBuffer(W.PIXEL_PACK_BUFFER,Yt),W.getBufferSubData(W.PIXEL_PACK_BUFFER,0,Nt),W.deleteBuffer(Yt),W.deleteSync(Qe),Nt}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")},this.copyFramebufferToTexture=function(A,X=null,st=0){const nt=Math.pow(2,-st),it=Math.floor(A.image.width*nt),Nt=Math.floor(A.image.height*nt),Ht=X!==null?X.x:0,Ut=X!==null?X.y:0;ct.setTexture2D(A,0),W.copyTexSubImage2D(W.TEXTURE_2D,st,0,0,Ht,Ut,it,Nt),y.unbindTexture()},this.copyTextureToTexture=function(A,X,st=null,nt=null,it=0,Nt=0){let Ht,Ut,kt,Vt,Jt,se,Yt,Te,Qe;const ke=A.isCompressedTexture?A.mipmaps[Nt]:A.image;if(st!==null)Ht=st.max.x-st.min.x,Ut=st.max.y-st.min.y,kt=st.isBox3?st.max.z-st.min.z:1,Vt=st.min.x,Jt=st.min.y,se=st.isBox3?st.min.z:0;else{const Je=Math.pow(2,-it);Ht=Math.floor(ke.width*Je),Ut=Math.floor(ke.height*Je),A.isDataArrayTexture?kt=ke.depth:A.isData3DTexture?kt=Math.floor(ke.depth*Je):kt=1,Vt=0,Jt=0,se=0}nt!==null?(Yt=nt.x,Te=nt.y,Qe=nt.z):(Yt=0,Te=0,Qe=0);const Le=Ct.convert(X.format),Ne=Ct.convert(X.type);let zt;X.isData3DTexture?(ct.setTexture3D(X,0),zt=W.TEXTURE_3D):X.isDataArrayTexture||X.isCompressedArrayTexture?(ct.setTexture2DArray(X,0),zt=W.TEXTURE_2D_ARRAY):(ct.setTexture2D(X,0),zt=W.TEXTURE_2D),y.activeTexture(W.TEXTURE0),y.pixelStorei(W.UNPACK_FLIP_Y_WEBGL,X.flipY),y.pixelStorei(W.UNPACK_PREMULTIPLY_ALPHA_WEBGL,X.premultiplyAlpha),y.pixelStorei(W.UNPACK_ALIGNMENT,X.unpackAlignment);const Ln=y.getParameter(W.UNPACK_ROW_LENGTH),he=y.getParameter(W.UNPACK_IMAGE_HEIGHT),vn=y.getParameter(W.UNPACK_SKIP_PIXELS),$n=y.getParameter(W.UNPACK_SKIP_ROWS),bi=y.getParameter(W.UNPACK_SKIP_IMAGES);y.pixelStorei(W.UNPACK_ROW_LENGTH,ke.width),y.pixelStorei(W.UNPACK_IMAGE_HEIGHT,ke.height),y.pixelStorei(W.UNPACK_SKIP_PIXELS,Vt),y.pixelStorei(W.UNPACK_SKIP_ROWS,Jt),y.pixelStorei(W.UNPACK_SKIP_IMAGES,se);const ti=A.isDataArrayTexture||A.isData3DTexture,Oe=X.isDataArrayTexture||X.isData3DTexture;if(A.isDepthTexture){const Je=rt.get(A),Ti=rt.get(X),De=rt.get(Je.__renderTarget),Fi=rt.get(Ti.__renderTarget);y.bindFramebuffer(W.READ_FRAMEBUFFER,De.__webglFramebuffer),y.bindFramebuffer(W.DRAW_FRAMEBUFFER,Fi.__webglFramebuffer);for(let La=0;La<kt;La++)ti&&(W.framebufferTextureLayer(W.READ_FRAMEBUFFER,W.COLOR_ATTACHMENT0,rt.get(A).__webglTexture,it,se+La),W.framebufferTextureLayer(W.DRAW_FRAMEBUFFER,W.COLOR_ATTACHMENT0,rt.get(X).__webglTexture,Nt,Qe+La)),W.blitFramebuffer(Vt,Jt,Ht,Ut,Yt,Te,Ht,Ut,W.DEPTH_BUFFER_BIT,W.NEAREST);y.bindFramebuffer(W.READ_FRAMEBUFFER,null),y.bindFramebuffer(W.DRAW_FRAMEBUFFER,null)}else if(it!==0||A.isRenderTargetTexture||rt.has(A)){const Je=rt.get(A),Ti=rt.get(X);y.bindFramebuffer(W.READ_FRAMEBUFFER,mt),y.bindFramebuffer(W.DRAW_FRAMEBUFFER,J);for(let De=0;De<kt;De++)ti?W.framebufferTextureLayer(W.READ_FRAMEBUFFER,W.COLOR_ATTACHMENT0,Je.__webglTexture,it,se+De):W.framebufferTexture2D(W.READ_FRAMEBUFFER,W.COLOR_ATTACHMENT0,W.TEXTURE_2D,Je.__webglTexture,it),Oe?W.framebufferTextureLayer(W.DRAW_FRAMEBUFFER,W.COLOR_ATTACHMENT0,Ti.__webglTexture,Nt,Qe+De):W.framebufferTexture2D(W.DRAW_FRAMEBUFFER,W.COLOR_ATTACHMENT0,W.TEXTURE_2D,Ti.__webglTexture,Nt),it!==0?W.blitFramebuffer(Vt,Jt,Ht,Ut,Yt,Te,Ht,Ut,W.COLOR_BUFFER_BIT,W.NEAREST):Oe?W.copyTexSubImage3D(zt,Nt,Yt,Te,Qe+De,Vt,Jt,Ht,Ut):W.copyTexSubImage2D(zt,Nt,Yt,Te,Vt,Jt,Ht,Ut);y.bindFramebuffer(W.READ_FRAMEBUFFER,null),y.bindFramebuffer(W.DRAW_FRAMEBUFFER,null)}else Oe?A.isDataTexture||A.isData3DTexture?W.texSubImage3D(zt,Nt,Yt,Te,Qe,Ht,Ut,kt,Le,Ne,ke.data):X.isCompressedArrayTexture?W.compressedTexSubImage3D(zt,Nt,Yt,Te,Qe,Ht,Ut,kt,Le,ke.data):W.texSubImage3D(zt,Nt,Yt,Te,Qe,Ht,Ut,kt,Le,Ne,ke):A.isDataTexture?W.texSubImage2D(W.TEXTURE_2D,Nt,Yt,Te,Ht,Ut,Le,Ne,ke.data):A.isCompressedTexture?W.compressedTexSubImage2D(W.TEXTURE_2D,Nt,Yt,Te,ke.width,ke.height,Le,ke.data):W.texSubImage2D(W.TEXTURE_2D,Nt,Yt,Te,Ht,Ut,Le,Ne,ke);y.pixelStorei(W.UNPACK_ROW_LENGTH,Ln),y.pixelStorei(W.UNPACK_IMAGE_HEIGHT,he),y.pixelStorei(W.UNPACK_SKIP_PIXELS,vn),y.pixelStorei(W.UNPACK_SKIP_ROWS,$n),y.pixelStorei(W.UNPACK_SKIP_IMAGES,bi),Nt===0&&X.generateMipmaps&&W.generateMipmap(zt),y.unbindTexture()},this.initRenderTarget=function(A){rt.get(A).__webglFramebuffer===void 0&&ct.setupRenderTarget(A)},this.initTexture=function(A){A.isCubeTexture?ct.setTextureCube(A,0):A.isData3DTexture?ct.setTexture3D(A,0):A.isDataArrayTexture||A.isCompressedArrayTexture?ct.setTexture2DArray(A,0):ct.setTexture2D(A,0),y.unbindTexture()},this.resetState=function(){I=0,H=0,j=null,y.reset(),It.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return qi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(t){this._outputColorSpace=t;const i=this.getContext();i.drawingBufferColorSpace=Ee._getDrawingBufferColorSpace(t),i.unpackColorSpace=Ee._getUnpackColorSpace()}}const ev={type:"change"},ap={type:"start"},Kv={type:"end"},Gu=new Ov,nv=new lr,O1=Math.cos(70*Yy.DEG2RAD),Sn=new $,Kn=2*Math.PI,Ve={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6},Qh=1e-6;class P1 extends FM{constructor(t,i=null){super(t,i),this.state=Ve.NONE,this.target=new $,this.cursor=new $,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.keyRotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"},this.mouseButtons={LEFT:Vs.ROTATE,MIDDLE:Vs.DOLLY,RIGHT:Vs.PAN},this.touches={ONE:Gs.ROTATE,TWO:Gs.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._cursorStyle="auto",this._domElementKeyEvents=null,this._lastPosition=new $,this._lastQuaternion=new hr,this._lastTargetPosition=new $,this._quat=new hr().setFromUnitVectors(t.up,new $(0,1,0)),this._quatInverse=this._quat.clone().invert(),this._spherical=new w0,this._sphericalDelta=new w0,this._scale=1,this._panOffset=new $,this._rotateStart=new ie,this._rotateEnd=new ie,this._rotateDelta=new ie,this._panStart=new ie,this._panEnd=new ie,this._panDelta=new ie,this._dollyStart=new ie,this._dollyEnd=new ie,this._dollyDelta=new ie,this._dollyDirection=new $,this._mouse=new ie,this._performCursorZoom=!1,this._pointers=[],this._pointerPositions={},this._controlActive=!1,this._onPointerMove=F1.bind(this),this._onPointerDown=I1.bind(this),this._onPointerUp=z1.bind(this),this._onContextMenu=W1.bind(this),this._onMouseWheel=G1.bind(this),this._onKeyDown=V1.bind(this),this._onTouchStart=k1.bind(this),this._onTouchMove=X1.bind(this),this._onMouseDown=B1.bind(this),this._onMouseMove=H1.bind(this),this._interceptControlDown=q1.bind(this),this._interceptControlUp=Y1.bind(this),this.domElement!==null&&this.connect(this.domElement),this.update()}set cursorStyle(t){this._cursorStyle=t,t==="grab"?this.domElement.style.cursor="grab":this.domElement.style.cursor="auto"}get cursorStyle(){return this._cursorStyle}connect(t){super.connect(t),this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointercancel",this._onPointerUp),this.domElement.addEventListener("contextmenu",this._onContextMenu),this.domElement.addEventListener("wheel",this._onMouseWheel,{passive:!1}),this.domElement.getRootNode().addEventListener("keydown",this._interceptControlDown,{passive:!0,capture:!0}),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.ownerDocument.removeEventListener("pointermove",this._onPointerMove),this.domElement.ownerDocument.removeEventListener("pointerup",this._onPointerUp),this.domElement.removeEventListener("pointercancel",this._onPointerUp),this.domElement.removeEventListener("wheel",this._onMouseWheel),this.domElement.removeEventListener("contextmenu",this._onContextMenu),this.stopListenToKeyEvents(),this.domElement.getRootNode().removeEventListener("keydown",this._interceptControlDown,{capture:!0}),this.domElement.style.touchAction=""}dispose(){this.disconnect()}getPolarAngle(){return this._spherical.phi}getAzimuthalAngle(){return this._spherical.theta}getDistance(){return this.object.position.distanceTo(this.target)}listenToKeyEvents(t){t.addEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=t}stopListenToKeyEvents(){this._domElementKeyEvents!==null&&(this._domElementKeyEvents.removeEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=null)}saveState(){this.target0.copy(this.target),this.position0.copy(this.object.position),this.zoom0=this.object.zoom}reset(){this.target.copy(this.target0),this.object.position.copy(this.position0),this.object.zoom=this.zoom0,this.object.updateProjectionMatrix(),this.dispatchEvent(ev),this.update(),this.state=Ve.NONE}pan(t,i){this._pan(t,i),this.update()}dollyIn(t){this._dollyIn(t),this.update()}dollyOut(t){this._dollyOut(t),this.update()}rotateLeft(t){this._rotateLeft(t),this.update()}rotateUp(t){this._rotateUp(t),this.update()}update(t=null){const i=this.object.position;Sn.copy(i).sub(this.target),Sn.applyQuaternion(this._quat),this._spherical.setFromVector3(Sn),this.autoRotate&&this.state===Ve.NONE&&this._rotateLeft(this._getAutoRotationAngle(t)),this.enableDamping?(this._spherical.theta+=this._sphericalDelta.theta*this.dampingFactor,this._spherical.phi+=this._sphericalDelta.phi*this.dampingFactor):(this._spherical.theta+=this._sphericalDelta.theta,this._spherical.phi+=this._sphericalDelta.phi);let r=this.minAzimuthAngle,l=this.maxAzimuthAngle;isFinite(r)&&isFinite(l)&&(r<-Math.PI?r+=Kn:r>Math.PI&&(r-=Kn),l<-Math.PI?l+=Kn:l>Math.PI&&(l-=Kn),r<=l?this._spherical.theta=Math.max(r,Math.min(l,this._spherical.theta)):this._spherical.theta=this._spherical.theta>(r+l)/2?Math.max(r,this._spherical.theta):Math.min(l,this._spherical.theta)),this._spherical.phi=Math.max(this.minPolarAngle,Math.min(this.maxPolarAngle,this._spherical.phi)),this._spherical.makeSafe(),this.enableDamping===!0?this.target.addScaledVector(this._panOffset,this.dampingFactor):this.target.add(this._panOffset),this.target.sub(this.cursor),this.target.clampLength(this.minTargetRadius,this.maxTargetRadius),this.target.add(this.cursor);let u=!1;if(this.zoomToCursor&&this._performCursorZoom||this.object.isOrthographicCamera)this._spherical.radius=this._clampDistance(this._spherical.radius);else{const f=this._spherical.radius;this._spherical.radius=this._clampDistance(this._spherical.radius*this._scale),u=f!=this._spherical.radius}if(Sn.setFromSpherical(this._spherical),Sn.applyQuaternion(this._quatInverse),i.copy(this.target).add(Sn),this.object.lookAt(this.target),this.enableDamping===!0?(this._sphericalDelta.theta*=1-this.dampingFactor,this._sphericalDelta.phi*=1-this.dampingFactor,this._panOffset.multiplyScalar(1-this.dampingFactor)):(this._sphericalDelta.set(0,0,0),this._panOffset.set(0,0,0)),this.zoomToCursor&&this._performCursorZoom){let f=null;if(this.object.isPerspectiveCamera){const p=Sn.length();f=this._clampDistance(p*this._scale);const m=p-f;this.object.position.addScaledVector(this._dollyDirection,m),this.object.updateMatrixWorld(),u=!!m}else if(this.object.isOrthographicCamera){const p=new $(this._mouse.x,this._mouse.y,0);p.unproject(this.object);const m=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),this.object.updateProjectionMatrix(),u=m!==this.object.zoom;const d=new $(this._mouse.x,this._mouse.y,0);d.unproject(this.object),this.object.position.sub(d).add(p),this.object.updateMatrixWorld(),f=Sn.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),this.zoomToCursor=!1;f!==null&&(this.screenSpacePanning?this.target.set(0,0,-1).transformDirection(this.object.matrix).multiplyScalar(f).add(this.object.position):(Gu.origin.copy(this.object.position),Gu.direction.set(0,0,-1).transformDirection(this.object.matrix),Math.abs(this.object.up.dot(Gu.direction))<O1?this.object.lookAt(this.target):(nv.setFromNormalAndCoplanarPoint(this.object.up,this.target),Gu.intersectPlane(nv,this.target))))}else if(this.object.isOrthographicCamera){const f=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),f!==this.object.zoom&&(this.object.updateProjectionMatrix(),u=!0)}return this._scale=1,this._performCursorZoom=!1,u||this._lastPosition.distanceToSquared(this.object.position)>Qh||8*(1-this._lastQuaternion.dot(this.object.quaternion))>Qh||this._lastTargetPosition.distanceToSquared(this.target)>Qh?(this.dispatchEvent(ev),this._lastPosition.copy(this.object.position),this._lastQuaternion.copy(this.object.quaternion),this._lastTargetPosition.copy(this.target),!0):!1}_getAutoRotationAngle(t){return t!==null?Kn/60*this.autoRotateSpeed*t:Kn/60/60*this.autoRotateSpeed}_getZoomScale(t){const i=Math.abs(t*.01);return Math.pow(.95,this.zoomSpeed*i)}_rotateLeft(t){this._sphericalDelta.theta-=t}_rotateUp(t){this._sphericalDelta.phi-=t}_panLeft(t,i){Sn.setFromMatrixColumn(i,0),Sn.multiplyScalar(-t),this._panOffset.add(Sn)}_panUp(t,i){this.screenSpacePanning===!0?Sn.setFromMatrixColumn(i,1):(Sn.setFromMatrixColumn(i,0),Sn.crossVectors(this.object.up,Sn)),Sn.multiplyScalar(t),this._panOffset.add(Sn)}_pan(t,i){const r=this.domElement;if(this.object.isPerspectiveCamera){const l=this.object.position;Sn.copy(l).sub(this.target);let u=Sn.length();u*=Math.tan(this.object.fov/2*Math.PI/180),this._panLeft(2*t*u/r.clientHeight,this.object.matrix),this._panUp(2*i*u/r.clientHeight,this.object.matrix)}else this.object.isOrthographicCamera?(this._panLeft(t*(this.object.right-this.object.left)/this.object.zoom/r.clientWidth,this.object.matrix),this._panUp(i*(this.object.top-this.object.bottom)/this.object.zoom/r.clientHeight,this.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),this.enablePan=!1)}_dollyOut(t){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale/=t:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_dollyIn(t){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale*=t:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_updateZoomParameters(t,i){if(!this.zoomToCursor)return;this._performCursorZoom=!0;const r=this.domElement.getBoundingClientRect(),l=t-r.left,u=i-r.top,f=r.width,p=r.height;this._mouse.x=l/f*2-1,this._mouse.y=-(u/p)*2+1,this._dollyDirection.set(this._mouse.x,this._mouse.y,1).unproject(this.object).sub(this.object.position).normalize()}_clampDistance(t){return Math.max(this.minDistance,Math.min(this.maxDistance,t))}_handleMouseDownRotate(t){this._rotateStart.set(t.clientX,t.clientY)}_handleMouseDownDolly(t){this._updateZoomParameters(t.clientX,t.clientX),this._dollyStart.set(t.clientX,t.clientY)}_handleMouseDownPan(t){this._panStart.set(t.clientX,t.clientY)}_handleMouseMoveRotate(t){this._rotateEnd.set(t.clientX,t.clientY),this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const i=this.domElement;this._rotateLeft(Kn*this._rotateDelta.x/i.clientHeight),this._rotateUp(Kn*this._rotateDelta.y/i.clientHeight),this._rotateStart.copy(this._rotateEnd),this.update()}_handleMouseMoveDolly(t){this._dollyEnd.set(t.clientX,t.clientY),this._dollyDelta.subVectors(this._dollyEnd,this._dollyStart),this._dollyDelta.y>0?this._dollyOut(this._getZoomScale(this._dollyDelta.y)):this._dollyDelta.y<0&&this._dollyIn(this._getZoomScale(this._dollyDelta.y)),this._dollyStart.copy(this._dollyEnd),this.update()}_handleMouseMovePan(t){this._panEnd.set(t.clientX,t.clientY),this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd),this.update()}_handleMouseWheel(t){this._updateZoomParameters(t.clientX,t.clientY),t.deltaY<0?this._dollyIn(this._getZoomScale(t.deltaY)):t.deltaY>0&&this._dollyOut(this._getZoomScale(t.deltaY)),this.update()}_handleKeyDown(t){let i=!1;switch(t.code){case this.keys.UP:t.ctrlKey||t.metaKey||t.shiftKey?this.enableRotate&&this._rotateUp(Kn*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(0,this.keyPanSpeed),i=!0;break;case this.keys.BOTTOM:t.ctrlKey||t.metaKey||t.shiftKey?this.enableRotate&&this._rotateUp(-Kn*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(0,-this.keyPanSpeed),i=!0;break;case this.keys.LEFT:t.ctrlKey||t.metaKey||t.shiftKey?this.enableRotate&&this._rotateLeft(Kn*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(this.keyPanSpeed,0),i=!0;break;case this.keys.RIGHT:t.ctrlKey||t.metaKey||t.shiftKey?this.enableRotate&&this._rotateLeft(-Kn*this.keyRotateSpeed/this.domElement.clientHeight):this.enablePan&&this._pan(-this.keyPanSpeed,0),i=!0;break}i&&(t.preventDefault(),this.update())}_handleTouchStartRotate(t){if(this._pointers.length===1)this._rotateStart.set(t.pageX,t.pageY);else{const i=this._getSecondPointerPosition(t),r=.5*(t.pageX+i.x),l=.5*(t.pageY+i.y);this._rotateStart.set(r,l)}}_handleTouchStartPan(t){if(this._pointers.length===1)this._panStart.set(t.pageX,t.pageY);else{const i=this._getSecondPointerPosition(t),r=.5*(t.pageX+i.x),l=.5*(t.pageY+i.y);this._panStart.set(r,l)}}_handleTouchStartDolly(t){const i=this._getSecondPointerPosition(t),r=t.pageX-i.x,l=t.pageY-i.y,u=Math.sqrt(r*r+l*l);this._dollyStart.set(0,u)}_handleTouchStartDollyPan(t){this.enableZoom&&this._handleTouchStartDolly(t),this.enablePan&&this._handleTouchStartPan(t)}_handleTouchStartDollyRotate(t){this.enableZoom&&this._handleTouchStartDolly(t),this.enableRotate&&this._handleTouchStartRotate(t)}_handleTouchMoveRotate(t){if(this._pointers.length==1)this._rotateEnd.set(t.pageX,t.pageY);else{const r=this._getSecondPointerPosition(t),l=.5*(t.pageX+r.x),u=.5*(t.pageY+r.y);this._rotateEnd.set(l,u)}this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const i=this.domElement;this._rotateLeft(Kn*this._rotateDelta.x/i.clientHeight),this._rotateUp(Kn*this._rotateDelta.y/i.clientHeight),this._rotateStart.copy(this._rotateEnd)}_handleTouchMovePan(t){if(this._pointers.length===1)this._panEnd.set(t.pageX,t.pageY);else{const i=this._getSecondPointerPosition(t),r=.5*(t.pageX+i.x),l=.5*(t.pageY+i.y);this._panEnd.set(r,l)}this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd)}_handleTouchMoveDolly(t){const i=this._getSecondPointerPosition(t),r=t.pageX-i.x,l=t.pageY-i.y,u=Math.sqrt(r*r+l*l);this._dollyEnd.set(0,u),this._dollyDelta.set(0,Math.pow(this._dollyEnd.y/this._dollyStart.y,this.zoomSpeed)),this._dollyOut(this._dollyDelta.y),this._dollyStart.copy(this._dollyEnd);const f=(t.pageX+i.x)*.5,p=(t.pageY+i.y)*.5;this._updateZoomParameters(f,p)}_handleTouchMoveDollyPan(t){this.enableZoom&&this._handleTouchMoveDolly(t),this.enablePan&&this._handleTouchMovePan(t)}_handleTouchMoveDollyRotate(t){this.enableZoom&&this._handleTouchMoveDolly(t),this.enableRotate&&this._handleTouchMoveRotate(t)}_addPointer(t){this._pointers.push(t.pointerId)}_removePointer(t){delete this._pointerPositions[t.pointerId];for(let i=0;i<this._pointers.length;i++)if(this._pointers[i]==t.pointerId){this._pointers.splice(i,1);return}}_isTrackingPointer(t){for(let i=0;i<this._pointers.length;i++)if(this._pointers[i]==t.pointerId)return!0;return!1}_trackPointer(t){let i=this._pointerPositions[t.pointerId];i===void 0&&(i=new ie,this._pointerPositions[t.pointerId]=i),i.set(t.pageX,t.pageY)}_getSecondPointerPosition(t){const i=t.pointerId===this._pointers[0]?this._pointers[1]:this._pointers[0];return this._pointerPositions[i]}_customWheelEvent(t){const i=t.deltaMode,r={clientX:t.clientX,clientY:t.clientY,deltaY:t.deltaY};switch(i){case 1:r.deltaY*=16;break;case 2:r.deltaY*=100;break}return t.ctrlKey&&!this._controlActive&&(r.deltaY*=10),r}}function I1(s){this.enabled!==!1&&(this._pointers.length===0&&(this.domElement.setPointerCapture(s.pointerId),this.domElement.ownerDocument.addEventListener("pointermove",this._onPointerMove),this.domElement.ownerDocument.addEventListener("pointerup",this._onPointerUp)),!this._isTrackingPointer(s)&&(this._addPointer(s),s.pointerType==="touch"?this._onTouchStart(s):this._onMouseDown(s),this._cursorStyle==="grab"&&(this.domElement.style.cursor="grabbing")))}function F1(s){this.enabled!==!1&&(s.pointerType==="touch"?this._onTouchMove(s):this._onMouseMove(s))}function z1(s){switch(this._removePointer(s),this._pointers.length){case 0:this.domElement.releasePointerCapture(s.pointerId),this.domElement.ownerDocument.removeEventListener("pointermove",this._onPointerMove),this.domElement.ownerDocument.removeEventListener("pointerup",this._onPointerUp),this.dispatchEvent(Kv),this.state=Ve.NONE,this._cursorStyle==="grab"&&(this.domElement.style.cursor="grab");break;case 1:const t=this._pointers[0],i=this._pointerPositions[t];this._onTouchStart({pointerId:t,pageX:i.x,pageY:i.y});break}}function B1(s){let t;switch(s.button){case 0:t=this.mouseButtons.LEFT;break;case 1:t=this.mouseButtons.MIDDLE;break;case 2:t=this.mouseButtons.RIGHT;break;default:t=-1}switch(t){case Vs.DOLLY:if(this.enableZoom===!1)return;this._handleMouseDownDolly(s),this.state=Ve.DOLLY;break;case Vs.ROTATE:if(s.ctrlKey||s.metaKey||s.shiftKey){if(this.enablePan===!1)return;this._handleMouseDownPan(s),this.state=Ve.PAN}else{if(this.enableRotate===!1)return;this._handleMouseDownRotate(s),this.state=Ve.ROTATE}break;case Vs.PAN:if(s.ctrlKey||s.metaKey||s.shiftKey){if(this.enableRotate===!1)return;this._handleMouseDownRotate(s),this.state=Ve.ROTATE}else{if(this.enablePan===!1)return;this._handleMouseDownPan(s),this.state=Ve.PAN}break;default:this.state=Ve.NONE}this.state!==Ve.NONE&&this.dispatchEvent(ap)}function H1(s){switch(this.state){case Ve.ROTATE:if(this.enableRotate===!1)return;this._handleMouseMoveRotate(s);break;case Ve.DOLLY:if(this.enableZoom===!1)return;this._handleMouseMoveDolly(s);break;case Ve.PAN:if(this.enablePan===!1)return;this._handleMouseMovePan(s);break}}function G1(s){this.enabled===!1||this.enableZoom===!1||this.state!==Ve.NONE||(s.preventDefault(),this.dispatchEvent(ap),this._handleMouseWheel(this._customWheelEvent(s)),this.dispatchEvent(Kv))}function V1(s){this.enabled!==!1&&this._handleKeyDown(s)}function k1(s){switch(this._trackPointer(s),this._pointers.length){case 1:switch(this.touches.ONE){case Gs.ROTATE:if(this.enableRotate===!1)return;this._handleTouchStartRotate(s),this.state=Ve.TOUCH_ROTATE;break;case Gs.PAN:if(this.enablePan===!1)return;this._handleTouchStartPan(s),this.state=Ve.TOUCH_PAN;break;default:this.state=Ve.NONE}break;case 2:switch(this.touches.TWO){case Gs.DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchStartDollyPan(s),this.state=Ve.TOUCH_DOLLY_PAN;break;case Gs.DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchStartDollyRotate(s),this.state=Ve.TOUCH_DOLLY_ROTATE;break;default:this.state=Ve.NONE}break;default:this.state=Ve.NONE}this.state!==Ve.NONE&&this.dispatchEvent(ap)}function X1(s){switch(this._trackPointer(s),this.state){case Ve.TOUCH_ROTATE:if(this.enableRotate===!1)return;this._handleTouchMoveRotate(s),this.update();break;case Ve.TOUCH_PAN:if(this.enablePan===!1)return;this._handleTouchMovePan(s),this.update();break;case Ve.TOUCH_DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchMoveDollyPan(s),this.update();break;case Ve.TOUCH_DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchMoveDollyRotate(s),this.update();break;default:this.state=Ve.NONE}}function W1(s){this.enabled!==!1&&s.preventDefault()}function q1(s){s.key==="Control"&&(this._controlActive=!0,this.domElement.getRootNode().addEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}function Y1(s){s.key==="Control"&&(this._controlActive=!1,this.domElement.getRootNode().removeEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}class Z1 extends np{constructor(t){super(t)}load(t,i,r,l){const u=this,f=new DM(this.manager);f.setPath(this.path),f.setResponseType("arraybuffer"),f.setRequestHeader(this.requestHeader),f.setWithCredentials(this.withCredentials),f.load(t,function(p){try{i(u.parse(p))}catch(m){l?l(m):console.error(m),u.manager.itemError(t)}},r,l)}parse(t){function i(d){const g=new DataView(d),v=32/8*3+32/8*3*3+16/8,_=g.getUint32(80,!0);if(80+32/8+_*v===g.byteLength)return!0;const T=[115,111,108,105,100];for(let w=0;w<5;w++)if(r(T,g,w))return!1;return!0}function r(d,g,v){for(let _=0,M=d.length;_<M;_++)if(d[_]!==g.getUint8(v+_))return!1;return!0}function l(d){const g=new DataView(d),v=g.getUint32(80,!0);let _,M,T,w=!1,E,S,F,z,C;for(let G=0;G<70;G++)g.getUint32(G,!1)==1129270351&&g.getUint8(G+4)==82&&g.getUint8(G+5)==61&&(w=!0,E=new Float32Array(v*3*3),S=g.getUint8(G+6)/255,F=g.getUint8(G+7)/255,z=g.getUint8(G+8)/255,C=g.getUint8(G+9)/255);const N=84,D=50,O=new Pi,b=new Float32Array(v*3*3),P=new Float32Array(v*3*3),q=new xe;for(let G=0;G<v;G++){const Z=N+G*D,ht=g.getFloat32(Z,!0),mt=g.getFloat32(Z+4,!0),J=g.getFloat32(Z+8,!0);if(w){const I=g.getUint16(Z+48,!0);(I&32768)===0?(_=(I&31)/31,M=(I>>5&31)/31,T=(I>>10&31)/31):(_=S,M=F,T=z)}for(let I=1;I<=3;I++){const H=Z+I*12,j=G*3*3+(I-1)*3;b[j]=g.getFloat32(H,!0),b[j+1]=g.getFloat32(H+4,!0),b[j+2]=g.getFloat32(H+8,!0),P[j]=ht,P[j+1]=mt,P[j+2]=J,w&&(q.setRGB(_,M,T,ci),E[j]=q.r,E[j+1]=q.g,E[j+2]=q.b)}}return O.setAttribute("position",new hi(b,3)),O.setAttribute("normal",new hi(P,3)),w&&(O.setAttribute("color",new hi(E,3)),O.hasColors=!0,O.alpha=C),O}function u(d){const g=new Pi,v=/solid([\s\S]*?)endsolid/g,_=/facet([\s\S]*?)endfacet/g,M=/solid\s(.+)/;let T=0;const w=/[\s]+([+-]?(?:\d*)(?:\.\d*)?(?:[eE][+-]?\d+)?)/.source,E=new RegExp("vertex"+w+w+w,"g"),S=new RegExp("normal"+w+w+w,"g"),F=[],z=[],C=[],N=new $;let D,O=0,b=0,P=0;for(;(D=v.exec(d))!==null;){b=P;const q=D[0],G=(D=M.exec(q))!==null?D[1]:"";for(C.push(G);(D=_.exec(q))!==null;){let mt=0,J=0;const I=D[0];for(;(D=S.exec(I))!==null;)N.x=parseFloat(D[1]),N.y=parseFloat(D[2]),N.z=parseFloat(D[3]),J++;for(;(D=E.exec(I))!==null;)F.push(parseFloat(D[1]),parseFloat(D[2]),parseFloat(D[3])),z.push(N.x,N.y,N.z),mt++,P++;J!==1&&console.error("THREE.STLLoader: Something isn't right with the normal of face number "+T),mt!==3&&console.error("THREE.STLLoader: Something isn't right with the vertices of face number "+T),T++}const Z=b,ht=P-b;g.userData.groupNames=C,g.addGroup(Z,ht,O),O++}return g.setAttribute("position",new Oi(F,3)),g.setAttribute("normal",new Oi(z,3)),g}function f(d){return typeof d!="string"?new TextDecoder().decode(d):d}function p(d){if(typeof d=="string"){const g=new Uint8Array(d.length);for(let v=0;v<d.length;v++)g[v]=d.charCodeAt(v)&255;return g.buffer||g}else return d}const m=p(t);return i(m)?l(m):u(f(t))}}var Br={},Hr={},Gr={},$o={},iv;function sc(){if(iv)return $o;iv=1,Object.defineProperty($o,"__esModule",{value:!0}),$o.Settings=void 0;var s=(function(){function i(){this.knowns={false:!1,null:null,true:!0},this.unary={"!":function(r){return!r},"+":function(r){return+r},"-":function(r){return-1*r},"~":function(r){return~r}},this.binary={"&&":{precedence:0,func:function(r,l){return r&&t(l)}},"||":{precedence:0,func:function(r,l){return r||t(l)}},"|":{precedence:1,func:function(r,l){return r|t(l)}},"^":{precedence:1,func:function(r,l){return r^t(l)}},"&":{precedence:1,func:function(r,l){return r&t(l)}},"===":{precedence:2,func:function(r,l){return r===t(l)}},"!==":{precedence:2,func:function(r,l){return r!==t(l)}},"==":{precedence:2,func:function(r,l){return r==t(l)}},"!=":{precedence:2,func:function(r,l){return r!=t(l)}},"<<":{precedence:3,func:function(r,l){return r<<t(l)}},">>>":{precedence:3,func:function(r,l){return r>>>t(l)}},">>":{precedence:3,func:function(r,l){return r>>t(l)}},"<=":{precedence:4,func:function(r,l){return r<=t(l)}},">=":{precedence:4,func:function(r,l){return r>=t(l)}},"<":{precedence:4,func:function(r,l){return r<t(l)}},">":{precedence:4,func:function(r,l){return r>t(l)}},"+":{precedence:5,func:function(r,l){return r+t(l)}},"-":{precedence:5,func:function(r,l){return r-t(l)}},"*":{precedence:6,func:function(r,l){return r*t(l)}},"/":{precedence:6,func:function(r,l){return r/t(l)}},"%":{precedence:6,func:function(r,l){return r%t(l)}}}}return Object.defineProperty(i.prototype,"knownIdentifiers",{get:function(){return Object.getOwnPropertyNames(this.knowns)},enumerable:!1,configurable:!0}),Object.defineProperty(i.prototype,"unaryOperators",{get:function(){return Object.getOwnPropertyNames(this.unary)},enumerable:!1,configurable:!0}),Object.defineProperty(i.prototype,"binaryOperators",{get:function(){return Object.getOwnPropertyNames(this.binary).sort(function(r,l){return l.length-r.length})},enumerable:!1,configurable:!0}),i.prototype.addKnownValue=function(r,l){return this.knowns[r]=l,this},i.prototype.containsKnown=function(r){return r in this.knowns},i.prototype.getKnownValue=function(r){return this.knowns[r]},i.prototype.addUnaryOperator=function(r,l){return this.unary[r]=l,this},i.prototype.containsUnary=function(r){return this.unary[r]!=null},i.prototype.getUnaryOperator=function(r){return this.unary[r]},i.prototype.addBinaryOperator=function(r,l,u){return u===void 0&&(u=7),this.binary[r]={precedence:u,func:l},this},i.prototype.containsBinary=function(r){return this.binary[r]!=null},i.prototype.getBinaryOperator=function(r){return this.binary[r]},i.default=new i,i})();$o.Settings=s;function t(i){return typeof i=="function"?i():i}return $o}var av;function Qv(){if(av)return Gr;av=1;var s=Gr&&Gr.__spreadArrays||function(){for(var r=0,l=0,u=arguments.length;l<u;l++)r+=arguments[l].length;for(var f=Array(r),p=0,l=0;l<u;l++)for(var m=arguments[l],d=0,g=m.length;d<g;d++,p++)f[p]=m[d];return f};Object.defineProperty(Gr,"__esModule",{value:!0}),Gr.ExpressionVisitor=void 0;var t=sc(),i=(function(){function r(l){l===void 0&&(l=t.Settings.default),this.settings=l}return r.prototype.process=function(l,u){return l.type==="Func"?this.visitFunc(l,u):this.visit(l,u)},r.prototype.visit=function(l,u){switch(l.type){case"Array":return this.visitArray(l,u);case"Binary":return this.visitBinary(l,u);case"Call":return this.visitCall(l,u);case"Indexer":return this.visitIndexer(l,u);case"Literal":return this.visitLiteral(l,u);case"Member":return this.visitMember(l,u);case"Object":return this.visitObject(l,u);case"Ternary":return this.visitTernary(l,u);case"Unary":return this.visitUnary(l,u);case"Variable":return this.visitVariable(l,u);case"Group":var f=l;if(f.expressions.length===1)return this.visit(f.expressions[0],u);case"Assign":case"Func":throw new Error("Invalid "+l.type+" expression usage");default:throw new Error("Unsupported ExpressionType "+l.type)}},r.prototype.visitArray=function(l,u){var f=this;return l.items.map(function(p){return f.visit(p,u)})},r.prototype.visitBinary=function(l,u){var f=l;return this.evalBinary(this.visit(f.left,u),f.operator,f.right,u)},r.prototype.visitCall=function(l,u){var f=this,p=this.visit(l.callee,u),m=l.args.map(function(d){return d.type==="Func"?f.visitFunc(d,u):f.visit(d,u)});return p.apply(void 0,m)},r.prototype.visitFunc=function(l,u){var f=this;return function(){for(var p=[],m=0;m<arguments.length;m++)p[m]=arguments[m];var d={};return l.parameters.forEach(function(g,v){return d[g]=p[v]}),f.visit(l.body,s([d],u))}},r.prototype.visitIndexer=function(l,u){var f=l,p=this.visit(f.owner,u),m=this.visit(f.key,u);return p!=null?p[m]:null},r.prototype.visitLiteral=function(l,u){return l.value},r.prototype.visitMember=function(l,u){return this.readVar(l.name,[this.visit(l.owner,u)])},r.prototype.visitObject=function(l,u){var f=this,p={};return l.members.forEach(function(m){return p[m.name]=f.visit(m.right,u)}),p},r.prototype.visitTernary=function(l,u){var f=l;return this.visit(f.predicate,u)?this.visit(f.whenTrue,u):this.visit(f.whenFalse,u)},r.prototype.visitUnary=function(l,u){var f=this.visit(l.target,u),p=this.settings.getUnaryOperator(l.operator);if(!p)throw new Error("Unknown unary operator "+l.operator);return p(f)},r.prototype.visitVariable=function(l,u){return this.readVar(l.name,u)},r.prototype.evalBinary=function(l,u,f,p){var m,d=this,g=this.settings.getBinaryOperator(u);if(!g)throw new Error("Unknown binary operator "+u);if(["&&","||"].indexOf(u)!==-1)return g.func(l,function(){return d.visit(f,p)});var v=this.visit(f,p);return m=this.tryFixDate(l,v),l=m[0],v=m[1],g.func(l,v)},r.prototype.readVar=function(l,u){var f=u.find(function(m){return m&&l in m}),p=f&&f[l];return p&&p.bind&&typeof p.bind=="function"?p.bind(f):p},r.prototype.tryFixDate=function(l,u){return Object.prototype.toString.call(l)==="[object Date]"&&(l=l.getTime(),typeof u=="string"&&(u=Date.parse(u))),[l,u]},r})();return Gr.ExpressionVisitor=i,Gr}var Vr={},rv;function Jv(){if(rv)return Vr;rv=1,Object.defineProperty(Vr,"__esModule",{value:!0}),Vr.Tokenizer=Vr.tokenize=void 0;var s=sc();function t(r,l){return new i(r,l).process()}Vr.tokenize=t;var i=(function(){function r(l,u){u===void 0&&(u=s.Settings.default),this.exp=l,this.settings=u,this.separator=".",this.len=l.length,this._idx=0,this._cd=l.charCodeAt(0),this._ch=l[0]}return r.literalExp=function(l){return{type:"Literal",value:l}},r.variableExp=function(l){return{type:"Variable",name:l}},r.unaryExp=function(l,u){return{type:"Unary",target:u,operator:l}},r.groupExp=function(l){return{type:"Group",expressions:l}},r.assignExp=function(l,u){return{type:"Assign",name:l,right:u}},r.objectExp=function(l){return{type:"Object",members:l}},r.arrayExp=function(l){return{type:"Array",items:l}},r.binaryExp=function(l,u,f){return{type:"Binary",operator:l,left:u,right:f}},r.memberExp=function(l,u){return{type:"Member",owner:l,name:u}},r.indexerExp=function(l,u){return{type:"Indexer",owner:l,key:u}},r.funcExp=function(l,u){return{type:"Func",parameters:l,body:u}},r.callExp=function(l,u){return{type:"Call",callee:l,args:u}},r.ternaryExp=function(l,u,f){return{type:"Ternary",predicate:l,whenTrue:u,whenFalse:f}},Object.defineProperty(r.prototype,"idx",{get:function(){return this._idx},enumerable:!1,configurable:!0}),Object.defineProperty(r.prototype,"cd",{get:function(){return this._cd},enumerable:!1,configurable:!0}),Object.defineProperty(r.prototype,"ch",{get:function(){return this._ch},enumerable:!1,configurable:!0}),r.prototype.process=function(){if(!this.exp)return null;var l=this.getExp();if(this.idx<this.len)throw new Error("Cannot parse expression, stuck at "+this.idx);return l},r.prototype.getExp=function(){this.skip();var l=this.tryLiteral()||this.tryVariable()||this.tryUnary()||this.tryGroup()||this.tryObject()||this.tryArray();if(!l)return l;l=this.tryKnown(l)||l;var u;do this.skip(),u=l,l=this.tryMember(l)||this.tryIndexer(l)||this.tryFunc(l)||this.tryCall(l)||this.tryTernary(l)||this.tryBinary(l);while(l);return u},r.prototype.tryLiteral=function(){var l=this;function u(){var p="";function m(){for(;l.isNumber();)p+=l.ch,l.move()}if(m(),l.get(l.separator)&&(p+=l.separator,m()),p){if(l.isVariableStart())throw new Error("Unexpected character ("+l.ch+") at index "+l.idx);return r.literalExp(Number(p))}return null}function f(){var p=l.ch,m;if(p==="`")m=!0;else if(p!=='"'&&p!=="'")return null;for(var d=p,g=[],v="";p=l.move();){if(p===d)return l.move(),g.length?(v&&g.push(r.literalExp(v)),g.reduce(function(_,M){return r.binaryExp("+",_,M)},r.literalExp(""))):r.literalExp(v);if(p==="\\")switch(p=l.move(),p){case"b":v+="\b";break;case"f":v+="\f";break;case"n":v+=`
`;break;case"r":v+="\r";break;case"t":v+="	";break;case"v":v+="\v";break;case"0":v+="\0";break;case"\\":v+="\\";break;case"'":v+="'";break;case'"':v+='"';break;default:v+="\\"+p;break}else if(m&&l.get("${")){if(v&&(g.push(r.literalExp(v)),v=""),g.push(l.getExp()),l.skip(),l.ch!=="}")throw new Error("Unterminated template literal at "+l.idx)}else v+=p}throw new Error("Unclosed quote after "+v)}return u()||f()},r.prototype.getVariableName=function(){var l="";if(this.isVariableStart())do l+=this.ch,this.move();while(this.stillVariable());return l},r.prototype.tryVariable=function(){var l=this.getVariableName();return l?r.variableExp(l):null},r.prototype.tryUnary=function(){var l=this,u=this.settings.unaryOperators.find(function(f){return l.get(f)});return u?r.unaryExp(u,this.getExp()):null},r.prototype.tryGroup=function(){return this.get("(")?r.groupExp(this.getGroup()):null},r.prototype.getGroup=function(){var l=[];do{var u=this.getExp();u&&l.push(u)}while(this.get(","));return this.to(")"),l},r.prototype.tryObject=function(){if(!this.get("{"))return null;var l=[];do{this.skip();var u=this.getExp();if(u.type!=="Variable"&&u.type!=="Member")throw new Error("Invalid assignment at "+this.idx);if(this.skip(),this.get(":")){if(u.type!=="Variable")throw new Error("Invalid assignment at "+this.idx);this.skip(),l.push(r.assignExp(u.name,this.getExp()))}else l.push(r.assignExp(u.name,u))}while(this.get(","));return this.to("}"),r.objectExp(l)},r.prototype.tryArray=function(){if(!this.get("["))return null;var l=[];do l.push(this.getExp());while(this.get(","));return this.to("]"),r.arrayExp(l)},r.prototype.tryKnown=function(l){if(l.type==="Variable"){var u=l;if(this.settings.containsKnown(u.name))return r.literalExp(this.settings.getKnownValue(u.name))}return null},r.prototype.tryMember=function(l){if(!this.get("."))return null;this.skip();var u=this.getVariableName();if(!u)throw new Error("Invalid member identifier at "+this.idx);return r.memberExp(l,u)},r.prototype.tryIndexer=function(l){if(!this.get("["))return null;this.skip();var u=this.getExp();if(u==null)throw new Error("Invalid indexer identifier at "+this.idx);return this.to("]"),r.indexerExp(l,u)},r.prototype.tryFunc=function(l){if(this.get("=>"))return r.funcExp(this.getParameters(l),this.getExp());if(l.type==="Variable"&&l.name==="function"){var u=this.getParameters(this.getExp());this.to("{"),this.skip(),this.get("return");var f=this.getExp();return this.get(";"),this.to("}"),r.funcExp(u,f)}return null},r.prototype.getParameters=function(l){var u=this;if(l.type==="Group"){var f=l;return f.expressions.map(function(p){if(p.type!=="Variable")throw new Error("Invalid parameter at "+u.idx);return p.name})}if(l.type!=="Variable")throw new Error("Invalid parameter at "+this.idx);return[l.name]},r.prototype.tryCall=function(l){return this.get("(")?this.getCall(l):null},r.prototype.getCall=function(l){var u=this.getGroup();return r.callExp(l,u)},r.prototype.tryTernary=function(l){if(!this.get("?"))return null;var u=this.getExp();this.to(":");var f=this.getExp();return r.ternaryExp(l,u,f)},r.prototype.tryBinary=function(l){var u=this,f=this.settings.binaryOperators.find(function(m){return u.get(m)});if(!f)return null;var p=this.getExp();return p.type==="Binary"?this.fixPrecedence(l,f,p):r.binaryExp(f,l,p)},r.prototype.isSpace=function(){return this.cd===32||this.cd===9||this.cd===160||this.cd===10||this.cd===13},r.prototype.isNumber=function(){return this.cd>=48&&this.cd<=57},r.prototype.isVariableStart=function(){return this.cd===36||this.cd===95||this.cd>=65&&this.cd<=90||this.cd>=97&&this.cd<=122},r.prototype.stillVariable=function(){return this.isVariableStart()||this.isNumber()},r.prototype.move=function(l){return l===void 0&&(l=1),this._idx+=l,this._cd=this.exp.charCodeAt(this.idx),this._ch=this.exp.charAt(this.idx)},r.prototype.get=function(l){return this.eq(this.idx,l)?!!this.move(l.length):!1},r.prototype.skip=function(){for(;this.isSpace()&&this.move(););},r.prototype.eq=function(l,u){return this.exp.substr(l,u.length)===u},r.prototype.to=function(l){if(this.skip(),!this.eq(this.idx,l))throw new Error("Expected "+l+" at index "+this.idx+", found "+this.exp[this.idx]);this.move(l.length)},r.prototype.fixPrecedence=function(l,u,f){var p=this.settings.getBinaryOperator(u).precedence,m=this.settings.getBinaryOperator(f.operator).precedence;return m<p?r.binaryExp(f.operator,r.binaryExp(u,l,f.left),f.right):r.binaryExp(u,l,f)},r})();return Vr.Tokenizer=i,Vr}var sv;function K1(){if(sv)return Hr;sv=1;var s=Hr&&Hr.__spreadArrays||function(){for(var u=0,f=0,p=arguments.length;f<p;f++)u+=arguments[f].length;for(var m=Array(u),d=0,f=0;f<p;f++)for(var g=arguments[f],v=0,_=g.length;v<_;v++,d++)m[d]=g[v];return m};Object.defineProperty(Hr,"__esModule",{value:!0}),Hr.evaluate=void 0;var t=Qv(),i=sc(),r=Jv();function l(u,f){for(var p=[],m=2;m<arguments.length;m++)p[m-2]=arguments[m];return f instanceof i.Settings||(p=s([f],p),f=void 0),new t.ExpressionVisitor(f).process(typeof u=="string"?r.tokenize(u,f):u,p)}return Hr.evaluate=l,Hr}var Jh={},ov;function Q1(){return ov||(ov=1,Object.defineProperty(Jh,"__esModule",{value:!0})),Jh}var lv;function J1(){return lv||(lv=1,(function(s){var t=Br&&Br.__createBinding||(Object.create?(function(r,l,u,f){f===void 0&&(f=u),Object.defineProperty(r,f,{enumerable:!0,get:function(){return l[u]}})}):(function(r,l,u,f){f===void 0&&(f=u),r[f]=l[u]})),i=Br&&Br.__exportStar||function(r,l){for(var u in r)u!=="default"&&!l.hasOwnProperty(u)&&t(l,r,u)};Object.defineProperty(s,"__esModule",{value:!0}),i(K1(),s),i(Qv(),s),i(sc(),s),i(Jv(),s),i(Q1(),s)})(Br)),Br}var uv=J1();const Ei={};for(const s of Object.getOwnPropertyNames(Math))Ei[s]=Math[s];Ei.ln=Math.log;Ei.log=(s,t)=>Math.log(t)/Math.log(s);Ei.mod=(s,t)=>s%t;Ei.sin=s=>Math.sin(s*Math.PI/180);Ei.cos=s=>Math.cos(s*Math.PI/180);Ei.tan=s=>Math.tan(s*Math.PI/180);Ei.asin=s=>Math.asin(s)*180/Math.PI;Ei.acos=s=>Math.acos(s)*180/Math.PI;Ei.atan=s=>Math.atan(s)*180/Math.PI;Ei.atan2=(s,t)=>Math.atan2(s,t)*180/Math.PI;const cv=new Map;function Vd(s){if(s===null||typeof s!="object")return s;if(Array.isArray(s))return s.map(Vd);const t=Object.fromEntries(Object.entries(s).map(([i,r])=>[i,Vd(r)]));return t.type==="Binary"&&t.operator==="^"?{type:"Call",callee:{type:"Variable",name:"pow"},args:[t.left,t.right]}:t}function fv(s,t){let i=cv.get(s);i||(i=Vd(uv.tokenize(s)),cv.set(s,i));const r=uv.evaluate(i,{...Ei,$t:t});return typeof r=="number"?r:Number(r)}function j1(s){return s===null?new bM:new EM({color:new xe(s),metalness:.1,roughness:.6})}class rp{group=new el;children=[];loaded;animated;operations;constructor(t,i,r=null){this.group.matrixAutoUpdate=!1,this.operations=t.operations??[];const l=t.color??r,u=[];t.model&&u.push(this.loadModel(`${i}${t.model}`,l));for(const f of t.children??[]){const p=new rp(f,i,l);this.children.push(p),this.group.add(p.group),u.push(p.loaded)}this.loaded=Promise.all(u).then(()=>{}),this.animated=this.operations.some(f=>JSON.stringify(f).includes("$t"))||this.children.some(f=>f.animated)}async loadModel(t,i){const r=await new Z1().loadAsync(t);r.computeVertexNormals(),this.group.add(new Qi(r,j1(i)))}update(t){const i=new $e,r=new $e,l=new $;for(const u of this.operations)u[0]==="r"?(l.set(u[2][0],u[2][1],u[2][2]).normalize(),r.makeRotationAxis(l,fv(u[1],t)*Math.PI/180)):r.makeTranslation(...u[1].map(f=>fv(f,t))),i.premultiply(r);this.group.matrix.copy(i);for(const u of this.children)u.update(t)}}async function $1(s,t,i){const r=await fetch(t);if(!r.ok)throw new Error(`Failed to load build snapshot: ${r.status}`);const l=await r.json(),u=new oM;u.add(new UM(16777215,5596791,1.2));const f=new OM(16777215,1.5);f.position.set(1,-1,2),u.add(f);const p=new rp(l.root,"/artifacts/");u.add(p.group);const m=new N1({antialias:!0,alpha:!0});m.setPixelRatio(window.devicePixelRatio),m.domElement.className="functional-model",m.domElement.setAttribute("aria-label","Functional model"),m.domElement.setAttribute("role","img"),s.appendChild(m.domElement);const d=new Mi(50,1,.1,1e4);d.up.set(0,0,1);const g=new P1(d,m.domElement);g.rotateSpeed=.5;let v=0,_=p.animated,M,T;if(p.animated){const N=document.createElement("div");N.className="animation-controls",N.hidden=!0;const D=document.createElement("button");D.className="timeline-toggle",D.textContent="Timeline",D.setAttribute("aria-expanded","false"),D.addEventListener("click",()=>{N.hidden=!N.hidden,D.setAttribute("aria-expanded",String(!N.hidden))}),T=document.createElement("button"),M=document.createElement("input"),M.type="range",M.min="0",M.max="1",M.step=String(1/l.animation.frames);const O=()=>{T&&(T.textContent=_?"Pause":"Play")};T.addEventListener("click",()=>{_=!_,O()}),M.addEventListener("input",()=>{_=!1,v=Number(M?.value),O()}),O(),N.append(T,M),s.append(D,N)}p.update(v),await p.loaded,u.updateMatrixWorld(!0);const w=new Qs().setFromObject(u),E=w.getCenter(new $),S=w.getSize(new $).length()/2/Math.tan(d.fov*Math.PI/360)*1.2;d.near=S/100,d.far=S*100,d.updateProjectionMatrix(),g.target.copy(E),g.update(),i?(d.position.copy(i.camera),g.target.copy(i.target),g.update()):(d.position.copy(E).addScaledVector(new $(1,-1,.8).normalize(),S),g.target.copy(E),g.update());const F=()=>{m.setSize(s.clientWidth,s.clientHeight),d.aspect=s.clientWidth/s.clientHeight,d.updateProjectionMatrix()},z=new ResizeObserver(F);z.observe(s),F();let C;return m.setAnimationLoop(N=>{const D=C===void 0?0:(N-C)/1e3;C=N,_&&(v=(v+D/(l.animation.frames/l.animation.fps))%1,M&&(M.value=String(v))),p.update(v),m.render(u,d)}),{view:()=>({camera:d.position.clone(),target:g.target.clone()}),dispose:()=>{m.setAnimationLoop(null),z.disconnect(),g.dispose(),m.dispose(),s.replaceChildren()}}}function tR({generation:s}){const t=Bn.useRef(null),i=Bn.useRef(void 0),[r,l]=Bn.useState(null);return Bn.useEffect(()=>{const u=t.current;if(!u)return;let f=!1,p;return l(null),$1(u,`/artifacts/viewer.json?generation=${s}`,i.current).then(m=>{const d=()=>{i.current=m.view(),m.dispose()};f?d():p=d}).catch(m=>{f||l(m.message)}),()=>{f=!0,p?.()}},[s]),r?ve.jsx("p",{className:"empty",children:r}):ve.jsx("div",{className:"functional-model-host",ref:t})}function eR({entries:s,onSubmit:t}){const[i,r]=Bn.useState(""),[l,u]=Bn.useState(!1),f=Bn.useRef(null),p=s[s.length-1];Bn.useLayoutEffect(()=>{p?.author==="foreman"&&f.current&&(f.current.scrollTop=f.current.scrollHeight)},[p?.author,p?.sequence]);const m=async d=>{if(d.preventDefault(),!(!i.trim()||l)){u(!0);try{await t(i),r("")}finally{u(!1)}}};return ve.jsxs(ve.Fragment,{children:[ve.jsx("ol",{className:"conversation-transcript","aria-label":"Conversation transcript",ref:f,children:s.length===0?ve.jsx("li",{className:"empty",children:"Send a message to begin the conversation."}):s.map(d=>ve.jsxs("li",{"data-conversation-author":d.author,children:[ve.jsx("strong",{children:d.author==="maker"?"Maker":"Foreman"}),ve.jsx("p",{children:d.text})]},d.sequence))}),ve.jsxs("form",{className:"conversation-composer","aria-label":"Message composer",onSubmit:m,children:[ve.jsx("textarea",{"aria-label":"Message",id:"message",name:"message",value:i,onChange:d=>r(d.target.value)}),ve.jsx("button",{type:"submit",disabled:!i.trim()||l,children:"Send"})]})]})}function nR({agents:s}){return ve.jsx(ve.Fragment,{children:ve.jsxs("section",{"aria-labelledby":"agents-heading",children:[ve.jsx("h2",{id:"agents-heading",children:"Agents"}),s.length===0?ve.jsx("p",{className:"empty",children:"No agents are currently manifested."}):ve.jsx("ul",{children:s.map(t=>ve.jsxs("li",{"data-agent-role":t.role,"data-agent-state":t.state,children:[ve.jsx("span",{children:t.label}),ve.jsx("span",{className:`state ${t.state}`,children:t.state})]},t.role))})]})})}function iR(){const[s,t]=Bn.useState(null),[i,r]=Bn.useState(!1),[l,u]=Bn.useState([]),[f,p]=Bn.useState(0);Bn.useEffect(()=>{const d=new EventSource("/events/lifecycle");return d.onopen=()=>r(!0),d.onerror=()=>r(!1),()=>d.close()},[]),Bn.useEffect(()=>{let d,g=!1,v;const _=w=>{v!==w.id&&(d?.close(),v=w.id,d=new EventSource(`/api/runs/${w.id}/stream`),d.addEventListener("shop-floor",E=>{const S=JSON.parse(E.data);if(S.kind==="conversation_entry"){const N=S.payload;u(D=>D.some(O=>O.sequence===N.sequence)?D:[...D,N]);return}if(S.kind==="model_changed"){p(N=>N+1);return}if(!S.kind.startsWith("agent_")&&!S.kind.startsWith("work_"))return;const{role:F,label:z,state:C}=S.payload;t(N=>{if(!N)return N;const D=N.agents.filter(O=>O.role!==F);return C!==null&&S.kind!=="agent_stopped"&&D.push({role:F,label:z,state:C}),{...N,agents:D.sort((O,b)=>O.role.localeCompare(b.role))}})}))},M=async()=>{const w=await fetch("/api/runs/latest");if(!w.ok||g)return;const E=await w.json(),S=await fetch(`/api/runs/${E.id}/conversation`);if(!S.ok||g)return;const F=await S.json();t(E),u(F.entries),_(E)};M();const T=window.setInterval(()=>{M()},1e3);return()=>{g=!0,window.clearInterval(T),d?.close()}},[]);const m=async d=>{if(!s)return;const g=await fetch(`/api/runs/${s.id}/conversation/maker`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:d})});if(!g.ok)return;const v=await g.json();u(_=>_.some(M=>M.sequence===v.sequence)?_:[..._,v])};return ve.jsxs("main",{className:"shop-workspace",children:[ve.jsxs("aside",{className:"shop-menu","aria-label":"Shop menu",children:[ve.jsxs("header",{className:"shop-brand",children:[ve.jsx("h1",{children:"shop-floor"}),ve.jsxs("p",{id:"shop-status","aria-live":"polite",children:["Shop is ",i?"open":"closed"]}),ve.jsx("p",{className:"run-status",children:s?`Run ${s.id} · ${s.status}`:"Waiting for a run."})]}),ve.jsx(nR,{agents:s?.agents??[]})]}),ve.jsxs("div",{className:"shop-content",children:[ve.jsxs("section",{className:"artifact-view","aria-labelledby":"artifact-heading",children:[ve.jsx("h2",{id:"artifact-heading",children:"Artifact view"}),ve.jsx(tR,{generation:f})]}),ve.jsx("section",{className:"conversation","aria-label":"Chat",children:ve.jsx(eR,{entries:l,onSubmit:m})})]})]})}uy.createRoot(document.getElementById("root")).render(ve.jsx(Bn.StrictMode,{children:ve.jsx(iR,{})}));
