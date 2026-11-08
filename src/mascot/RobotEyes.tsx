import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Group, MathUtils } from 'three';
import { useMascotStore } from './useMascotStore';

export function RobotEyes({reduced}:{reduced:boolean}){
 const group=useRef<Group>(null),left=useRef<Group>(null),right=useRef<Group>(null),mouth=useRef<Group>(null),nextBlink=useRef(2+Math.random()*3),blink=useRef(0);
 useFrame(({clock},delta)=>{const store=useMascotStore.getState(),state=store.state,pointer=store.screenPointer,t=clock.elapsedTime;if(!group.current||!left.current||!right.current)return;
  if(!reduced&&t>nextBlink.current){blink.current=t;nextBlink.current=t+3+Math.random()*4}
  const blinking=!reduced&&t-blink.current<.14&&t>1;
  const scale=state==='sleeping'?.1:blinking?.08:state==='thinking'?.55:state==='error'?.45:1;
  for(const eye of [left.current,right.current])eye.scale.y=MathUtils.damp(eye.scale.y,scale,30,delta);
  group.current.position.x=MathUtils.damp(group.current.position.x,reduced?0:pointer.x*.08,7,delta);
  group.current.position.y=MathUtils.damp(group.current.position.y,state==='reading'?-.08:reduced?0:pointer.y*.035,7,delta);
  if(mouth.current)mouth.current.scale.y=MathUtils.damp(mouth.current.scale.y,state==='talking'&&!reduced?.75+Math.abs(Math.sin(t*11))*.9:state==='celebrating'?1.35:.6,12,delta);
 });
 return <group ref={group} position={[0,.03,.655]}><group ref={left} position={[-.32,.08,0]} rotation={[0,0,-.04]}><mesh><torusGeometry args={[.115,.024,8,22,Math.PI]}/><meshBasicMaterial color="#23efff" toneMapped={false}/></mesh></group><group ref={right} position={[.32,.08,0]} rotation={[0,0,.04]}><mesh><torusGeometry args={[.115,.024,8,22,Math.PI]}/><meshBasicMaterial color="#23efff" toneMapped={false}/></mesh></group><group ref={mouth} position={[0,-.19,.002]}><mesh rotation={[0,0,Math.PI]}><circleGeometry args={[.092,22,0,Math.PI]}/><meshBasicMaterial color="#51efff" toneMapped={false}/></mesh></group></group>
}
