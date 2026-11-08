import type { MascotState } from './useMascotStore';
export function animationPose(state:MascotState,t:number,reduced:boolean){
 const wave=Math.sin(t*7),slow=Math.sin(t*1.8),active=!reduced;
 return {float:active?Math.sin(t*1.6)*.045:0,
 bounce:state==='celebrating'&&active?Math.abs(Math.sin(t*5))*.22:state==='greeting'&&active?Math.abs(Math.sin(t*3))*.055:0,
 headX:state==='reading'?.24:state==='thinking'?-.1:state==='sleeping'?.12:state==='teaching'&&active?slow*.04:0,
 headZ:state==='thinking'?-.12:state==='encouraging'?.12:state==='hover'?-.08:0,
 leftArm:state==='celebrating'?2.1:state==='reading'?.55:state==='greeting'?2+(active?wave*.22:0):state==='encouraging'?1.3:.16+(active?slow*.025:0),
 rightArm:state==='celebrating'?-2.1:state==='reading'?-.55:state==='teaching'?-1.1+(active?Math.sin(t*2.7)*.09:0):-.16-(active?slow*.025:0),
 eyes:state==='sleeping'?.08:state==='thinking'?.6:state==='error'?.55:1,
 chest:state==='celebrating'?3.1:state==='thinking'?1.8+(active?slow*.3:0):1.2+(active?slow*.12:0),
 book:state==='reading',listening:state==='listening',talking:state==='talking',turn:state==='hover'?.05:0}
}
