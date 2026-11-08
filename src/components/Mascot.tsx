import { lazy, Suspense } from 'react';
import { useReducedMotion, useSpring, motion } from 'framer-motion';
import { FileText, Code2, ChartNoAxesCombined } from 'lucide-react';
import { useMascotStore } from '../mascot/useMascotStore';
const LuminaMascot=lazy(()=>import('../mascot/LuminaMascot'));

export function Mascot({compact=false}:{compact?:boolean}){
 const reduced=useReducedMotion(),x=useSpring(0,{stiffness:95,damping:20}),y=useSpring(0,{stiffness:95,damping:20});
 const state=useMascotStore(s=>s.state),message=useMascotStore(s=>s.message);
 return <div className={'mascot-stage '+(compact?'mascot-compact':'')} onPointerMove={e=>{if(reduced||e.pointerType!=='mouse')return;const r=e.currentTarget.getBoundingClientRect();x.set((e.clientX-r.left-r.width/2)*.035);y.set((e.clientY-r.top-r.height/2)*.025)}} onPointerLeave={()=>{x.set(0);y.set(0)}}>
  <div className="mascot-aura"/><div className="mascot-orbit orbit-a"/><div className="mascot-orbit orbit-b"/>
  <div className="mascot-platform"><span/></div>
  <motion.div className="robot-parallax" style={{x,y}}><Suspense fallback={<img className="mascot-static-image" src="/assets/lumina-robot.png" alt="Lumina robot tutor illustration"/>}><LuminaMascot compact={compact} onBook={()=>window.dispatchEvent(new CustomEvent('lumina:navigate',{detail:'library'}))}/></Suspense></motion.div>
  {!compact&&<><span className="orbit-file file-pdf"><FileText size={23}/><b>PDF</b></span><span className="orbit-file file-word"><b>W</b></span><span className="orbit-file file-ppt"><b>P</b></span><span className="orbit-file file-code"><Code2 size={28}/></span><span className="orbit-file file-chart"><ChartNoAxesCombined size={27}/></span><span className="mascot-spark spark-1">✦</span><span className="mascot-spark spark-2">✦</span><span className="mascot-spark spark-3">✧</span><span className="mascot-particle particle-1"/><span className="mascot-particle particle-2"/><span className="mascot-particle particle-3"/></>}
  {!compact&&!['idle','sleeping','hover','teaching'].includes(state)&&<div className="mascot-hero-status"><span>{message}</span></div>}
 </div>
}
