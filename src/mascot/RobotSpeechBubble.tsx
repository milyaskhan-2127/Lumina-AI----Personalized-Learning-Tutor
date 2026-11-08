import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import { useMascotStore } from './useMascotStore';
export function RobotSpeechBubble(){const state=useMascotStore(s=>s.state),message=useMascotStore(s=>s.message);return <AnimatePresence mode="wait"><motion.div key={message} className={'robot-speech-bubble robot-bubble-'+state} initial={{opacity:0,y:5,scale:.97}} animate={{opacity:1,y:0,scale:1}} exit={{opacity:0,y:-4}} role="status"><span>{message}</span>{state==='error'&&<button aria-label="Dismiss robot error" onClick={()=>useMascotStore.getState().setActivity('error',null)}><X size={13}/></button>}</motion.div></AnimatePresence>}
