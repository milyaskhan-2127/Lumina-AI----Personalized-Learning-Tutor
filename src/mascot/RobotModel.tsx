import { useMemo, useRef } from 'react';
import { useFrame, type ThreeEvent } from '@react-three/fiber';
import { RoundedBox } from '@react-three/drei';
import { Group, MathUtils, Mesh, MeshStandardMaterial, Shape, Vector3, CatmullRomCurve3 } from 'three';
import { RobotEyes } from './RobotEyes';
import { animationPose } from './RobotAnimations';
import { mascotNotice, useMascotStore } from './useMascotStore';

const ceramic={color:'#f2faff',metalness:.26,roughness:.25};
const blue={color:'#0759d2',metalness:.55,roughness:.2};
function Box({args,radius=.12,material=ceramic,...props}:{args:[number,number,number];radius?:number;material?:typeof ceramic;[key:string]:any}){return <RoundedBox args={args} radius={radius} smoothness={4} {...props}><meshStandardMaterial {...material}/></RoundedBox>}
export default function RobotModel({reduced,onBook}:{reduced:boolean;onBook:()=>void}){
 const body=useRef<Group>(null),head=useRef<Group>(null),left=useRef<Group>(null),right=useRef<Group>(null),book=useRef<Group>(null),leftPage=useRef<Group>(null),rightPage=useRef<Group>(null),chest=useRef<MeshStandardMaterial>(null),rings=useRef<Group>(null),scan=useRef<Mesh>(null),page=useRef<Group>(null),lastClick=useRef(0),gestureStart=useRef(0),seenGesture=useRef(0);
 const star=useMemo(()=>{const s=new Shape();for(let i=0;i<8;i++){const a=Math.PI/2+i*Math.PI/4,r=i%2?.065:.2;if(i===0)s.moveTo(Math.cos(a)*r,Math.sin(a)*r);else s.lineTo(Math.cos(a)*r,Math.sin(a)*r)}s.closePath();return s},[]);
 const tassel=useMemo(()=>new CatmullRomCurve3([new Vector3(.1,.95,.03),new Vector3(.7,.91,.12),new Vector3(.86,.77,.16),new Vector3(.86,.35,.18)]),[]);
 function react(e:ThreeEvent<MouseEvent>){e.stopPropagation();const now=performance.now();if(now-lastClick.current<850)return;lastClick.current=now;useMascotStore.getState().react();mascotNotice('greeting','A little curiosity can change everything. What shall we explore?',1800)}
 useFrame(({clock},delta)=>{const store=useMascotStore.getState(),pointer=store.screenPointer,t=clock.elapsedTime,pose=animationPose(store.state,t,reduced),d=Math.min(delta,.05);if(!body.current||!head.current||!left.current||!right.current)return;
  if(store.gesture!==seenGesture.current){seenGesture.current=store.gesture;gestureStart.current=t}
  const playful=!reduced&&t-gestureStart.current<.8&&gestureStart.current>0?Math.sin((t-gestureStart.current)/.8*Math.PI)*.22:0;
  body.current.position.y=MathUtils.damp(body.current.position.y,pose.float+pose.bounce,7,d);
  body.current.rotation.y=MathUtils.damp(body.current.rotation.y,reduced?0:pointer.x*.09+playful,6,d);
  head.current.rotation.x=MathUtils.damp(head.current.rotation.x,pose.headX+(reduced?0:-pointer.y*.11),6,d);
  head.current.rotation.y=MathUtils.damp(head.current.rotation.y,reduced?0:pointer.x*.25,6,d);
  head.current.rotation.z=MathUtils.damp(head.current.rotation.z,pose.headZ,6,d);
  left.current.rotation.z=MathUtils.damp(left.current.rotation.z,-pose.leftArm,8,d);right.current.rotation.z=MathUtils.damp(right.current.rotation.z,-pose.rightArm,8,d);
  if(chest.current)chest.current.emissiveIntensity=pose.chest;
  if(book.current){const show=pose.book;book.current.scale.setScalar(MathUtils.damp(book.current.scale.x,show?1:.001,8,d));book.current.visible=book.current.scale.x>.015}
  if(leftPage.current&&rightPage.current){leftPage.current.rotation.y=MathUtils.damp(leftPage.current.rotation.y,pose.book?-.18:-1.5,5,d);rightPage.current.rotation.y=MathUtils.damp(rightPage.current.rotation.y,pose.book?.18:1.5,5,d)}
  if(page.current&&!reduced)page.current.rotation.y=Math.sin(t*1.7)*.65;
  if(scan.current&&!reduced)scan.current.position.y=.28+Math.sin(t*2)*.27;
  if(rings.current&&!reduced)rings.current.rotation.y=t*.12;
 });
 return <group position={[0,-.15,0]}><group ref={body} onClick={react}>
  <group ref={head} position={[0,.95,0]}>
   <Box args={[1.66,1.18,1.08]} radius={.38}/>
   <Box args={[1.43,.94,.13]} radius={.26} material={{color:'#07132e',metalness:.55,roughness:.16}} position={[0,0,.57]}/>
   <Box args={[1.48,.99,.055]} radius={.27} material={{color:'#1c4aa6',metalness:.5,roughness:.25}} position={[0,0,.51]}/>
   <RobotEyes reduced={reduced}/>
   <mesh position={[-.32,.32,.654]} rotation={[0,0,-.08]}><planeGeometry args={[.6,.055]}/><meshBasicMaterial color="#9bdbff" transparent opacity={.12}/></mesh>
   {[-1,1].map(side=><group position={[side*.9,0,0]} rotation={[0,0,Math.PI/2]} key={side}><mesh><cylinderGeometry args={[.32,.32,.19,32]}/><meshStandardMaterial {...ceramic}/></mesh><mesh position={[0,side*.11,0]}><cylinderGeometry args={[.235,.235,.08,32]}/><meshStandardMaterial {...blue}/></mesh><mesh position={[0,side*.16,0]} rotation={[Math.PI/2,0,0]}><torusGeometry args={[.19,.028,9,32]}/><meshBasicMaterial color="#21e8ff" toneMapped={false}/></mesh></group>)}
   <group onClick={e=>{e.stopPropagation();mascotNotice('greeting','Learning tip: explaining an idea in your own words helps you find the gaps in your understanding.',4200);useMascotStore.getState().react()}}>
    <mesh position={[0,.64,0]}><cylinderGeometry args={[.42,.46,.22,32]}/><meshStandardMaterial color="#162c70" metalness={.35} roughness={.27}/></mesh>
    <Box args={[1.5,.1,1.33]} radius={.035} position={[0,.81,0]} rotation={[0,Math.PI/4,0]} material={{color:'#12245e',metalness:.45,roughness:.24}}/>
    <mesh position={[.03,.9,.03]}><sphereGeometry args={[.055,12,12]}/><meshStandardMaterial color="#e8b44a" metalness={.7} roughness={.25}/></mesh>
    <mesh><tubeGeometry args={[tassel,20,.015,6,false]}/><meshStandardMaterial color="#e9bc47" metalness={.6} roughness={.3}/></mesh>
    <mesh position={[.86,.23,.18]}><coneGeometry args={[.045,.23,12]}/><meshStandardMaterial color="#ffc65a" metalness={.4} roughness={.35}/></mesh>
   </group>
  </group>
  <Box args={[.92,.9,.65]} radius={.22} position={[0,-.15,0]}/>
  <Box args={[.65,.6,.07]} radius={.14} position={[0,-.13,.34]} material={blue}/>
  <mesh position={[0,-.12,.388]} onClick={e=>{e.stopPropagation();mascotNotice('encouraging','One small step is still progress. Try one question, one example, or one short quiz.',3500)}}><shapeGeometry args={[star]}/><meshStandardMaterial ref={chest} color="#9afcff" emissive="#08d6ff" emissiveIntensity={1.5} toneMapped={false}/></mesh>
  {[-1,1].map(side=><group ref={side===-1?left:right} key={side} position={[side*.59,.12,0]} onClick={e=>{e.stopPropagation();useMascotStore.getState().react();mascotNotice('greeting','Hi there! Ready for your next bright idea?',1700)}}><mesh position={[0,-.11,0]}><sphereGeometry args={[.19,16,16]}/><meshStandardMaterial {...blue}/></mesh><mesh position={[0,-.32,0]}><capsuleGeometry args={[.155,.26,5,14]}/><meshStandardMaterial {...ceramic}/></mesh><mesh position={[0,-.56,.015]}><sphereGeometry args={[.19,16,16]}/><meshStandardMaterial {...ceramic}/></mesh><mesh position={[0,-.58,.16]}><sphereGeometry args={[.08,12,12]}/><meshStandardMaterial {...blue}/></mesh></group>)}
  {[-1,1].map(side=><group key={side} position={[side*.255,-.75,0]}><mesh><capsuleGeometry args={[.16,.22,5,14]}/><meshStandardMaterial {...ceramic}/></mesh><Box args={[.36,.24,.45]} radius={.1} position={[0,-.2,.075]} material={blue}/><Box args={[.34,.035,.43]} radius={.012} position={[0,-.09,.075]} material={{color:'#4aeaff',metalness:.3,roughness:.2}}/></group>)}
  <group ref={book} scale={.001} position={[0,-.2,.76]} rotation={[-.28,0,0]} onClick={e=>{e.stopPropagation();onBook()}}>
   <group ref={leftPage}><group position={[-.31,0,0]}><Box args={[.6,.76,.055]} radius={.025} material={{color:'#087bd4',metalness:.3,roughness:.3}}/><mesh position={[0,0,.04]}><planeGeometry args={[.54,.69]}/><meshStandardMaterial color="#7af5ff" emissive="#00bcff" emissiveIntensity={.7} transparent opacity={.62} side={2}/></mesh>{[0,1,2,3].map(i=><mesh key={i} position={[0,.2-i*.115,.05]}><planeGeometry args={[.39,.018]}/><meshBasicMaterial color="#e0ffff" transparent opacity={.7}/></mesh>)}</group></group>
   <group ref={rightPage}><group position={[.31,0,0]}><Box args={[.6,.76,.055]} radius={.025} material={{color:'#087bd4',metalness:.3,roughness:.3}}/><mesh position={[0,0,.04]}><planeGeometry args={[.54,.69]}/><meshStandardMaterial color="#7af5ff" emissive="#00bcff" emissiveIntensity={.7} transparent opacity={.62} side={2}/></mesh>{[0,1,2,3].map(i=><mesh key={i} position={[0,.2-i*.115,.05]}><planeGeometry args={[.39,.018]}/><meshBasicMaterial color="#e0ffff" transparent opacity={.7}/></mesh>)}</group></group>
   <group ref={page}><mesh position={[.29,0,.07]}><planeGeometry args={[.55,.7]}/><meshBasicMaterial color="#b5ffff" transparent opacity={.18} side={2}/></mesh></group>
   <mesh ref={scan} position={[0,.2,.09]}><planeGeometry args={[1.15,.025]}/><meshBasicMaterial color="#eeffff" transparent opacity={.8}/></mesh>
  </group>
 </group>
 <group ref={rings} position={[0,.2,-.12]}>{[0,1].map(i=><mesh key={i} rotation={[Math.PI/2+(i?-.15:.2),0,i?.3:-.4]}><torusGeometry args={[1.37,.009,5,70]}/><meshBasicMaterial color={i?'#81c8ff':'#43e9ff'} transparent opacity={.35} toneMapped={false}/></mesh>)}</group>
 </group>
}
