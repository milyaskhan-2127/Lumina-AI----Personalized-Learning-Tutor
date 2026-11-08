import { useEffect, useRef, type ReactNode } from 'react';
import { animate, motion, useMotionValue, useReducedMotion, useSpring, useTransform } from 'framer-motion';

export function GlassCard({children,className='',delay=0}:{children:ReactNode;className?:string;delay?:number}){
 const reduced=useReducedMotion(),ref=useRef<HTMLDivElement>(null);
 const x=useSpring(0,{stiffness:180,damping:24}),y=useSpring(0,{stiffness:180,damping:24});
 const reset=()=>{x.set(0);y.set(0)};
 return <motion.div ref={ref} className={'glass premium-card '+className} initial={reduced?false:{opacity:0,y:14}} whileInView={{opacity:1,y:0}} viewport={{once:true,amount:.08}} transition={{duration:.45,delay}} style={{rotateX:x,rotateY:y,transformPerspective:1100}} onPointerMove={e=>{if(reduced||e.pointerType!=='mouse')return;const r=e.currentTarget.getBoundingClientRect();x.set(-(e.clientY-r.top-r.height/2)/r.height*3);y.set((e.clientX-r.left-r.width/2)/r.width*3);e.currentTarget.style.setProperty('--spot-x',`${e.clientX-r.left}px`);e.currentTarget.style.setProperty('--spot-y',`${e.clientY-r.top}px`)}} onPointerLeave={reset} onBlur={reset}>{children}</motion.div>
}
export function Counter({value,suffix=''}:{value:number;suffix?:string}){
 const reduced=useReducedMotion(),number=useMotionValue(reduced?value:0),display=useTransform(number,n=>Math.round(n).toLocaleString());
 useEffect(()=>{if(reduced){number.set(value);return}const control=animate(number,value,{duration:.95,ease:'easeOut'});return()=>control.stop()},[value,reduced,number]);
 return <><motion.span>{display}</motion.span>{suffix}</>
}
export function useSurfaceEffects(){
 useEffect(()=>{
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  let frame=0;let target:HTMLElement|null=null;let pointer:{x:number;y:number}|null=null;
  const move=(event:PointerEvent)=>{
   if(event.pointerType!=='mouse')return;
   const el=(event.target as HTMLElement).closest<HTMLElement>('.button,.quick-action-tile,.nav-item,.document-card,.suggestion-grid button');
   if(target&&target!==el){target.style.removeProperty('--mag-x');target.style.removeProperty('--mag-y')}
   target=el;pointer={x:event.clientX,y:event.clientY};
   if(frame)return;
   frame=requestAnimationFrame(()=>{frame=0;if(!target||!pointer)return;const r=target.getBoundingClientRect();target.style.setProperty('--pointer-x',`${pointer.x-r.left}px`);target.style.setProperty('--pointer-y',`${pointer.y-r.top}px`);if(target.classList.contains('button')){target.style.setProperty('--mag-x',`${(pointer.x-r.left-r.width/2)*.045}px`);target.style.setProperty('--mag-y',`${(pointer.y-r.top-r.height/2)*.08}px`)}})
  };
  const click=(event:PointerEvent)=>{const el=(event.target as HTMLElement).closest<HTMLButtonElement>('button');if(!el||el.disabled)return;const r=el.getBoundingClientRect(),ripple=document.createElement('span');ripple.className='click-ripple';ripple.style.left=`${event.clientX-r.left}px`;ripple.style.top=`${event.clientY-r.top}px`;el.appendChild(ripple);ripple.addEventListener('animationend',()=>ripple.remove(),{once:true})};
  const leave=(event:PointerEvent)=>{if(target&&!target.contains(event.relatedTarget as Node)){target.style.removeProperty('--mag-x');target.style.removeProperty('--mag-y');target=null}};
  document.addEventListener('pointermove',move,{passive:true});document.addEventListener('pointerdown',click,{passive:true});document.addEventListener('pointerout',leave,{passive:true});
  return()=>{cancelAnimationFrame(frame);document.removeEventListener('pointermove',move);document.removeEventListener('pointerdown',click);document.removeEventListener('pointerout',leave);document.querySelectorAll('.click-ripple').forEach(r=>r.remove())};
 },[])
}
