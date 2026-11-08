import { create } from 'zustand';

export type MascotState='idle'|'greeting'|'hover'|'listening'|'thinking'|'talking'|'reading'|'teaching'|'celebrating'|'encouraging'|'sleeping'|'error';
export type Activity={state:MascotState;message:string};
export const priorities:Record<MascotState,number>={error:100,listening:95,celebrating:90,reading:85,talking:80,teaching:75,thinking:70,encouraging:60,greeting:40,hover:20,sleeping:5,idle:0};
type Store={state:MascotState;message:string;activities:Record<string,Activity>;progress:number|null;uploadTitle:string;enabled3d:boolean;gesture:number;screenPointer:{x:number;y:number};setPointer:(x:number,y:number)=>void;setActivity:(key:string,activity:Activity|null)=>void;setProgress:(progress:number|null,title?:string)=>void;set3d:(value:boolean)=>void;react:()=>void};
export const useMascotStore=create<Store>((set,get)=>({state:'idle',message:'What would you like to understand today?',activities:{},progress:null,uploadTitle:'',enabled3d:localStorage.getItem('lumina-3d')!=='off',gesture:0,screenPointer:{x:0,y:0},setPointer:(x,y)=>set({screenPointer:{x:Math.max(-1,Math.min(1,x)),y:Math.max(-1,Math.min(1,y))}}),
 setActivity:(key,activity)=>set(current=>{const activities={...current.activities};if(activity)activities[key]=activity;else delete activities[key];const selected=Object.values(activities).sort((a,b)=>priorities[b.state]-priorities[a.state])[0];return {activities,state:selected?.state||'idle',message:selected?.message||'What would you like to understand today?'}}),
 setProgress:(progress,title)=>set({progress,uploadTitle:title||''}),
 set3d:enabled3d=>{localStorage.setItem('lumina-3d',enabled3d?'on':'off');set({enabled3d})},
 react:()=>set(current=>({gesture:current.gesture+1}))
}));

let transient:ReturnType<typeof setTimeout>|undefined;
export function mascotNotice(state:MascotState,message:string,duration=2600){clearTimeout(transient);useMascotStore.getState().setActivity('notice',{state,message});transient=setTimeout(()=>useMascotStore.getState().setActivity('notice',null),duration)}
export function clearMascotError(){useMascotStore.getState().setActivity('error',null)}
export type MascotEvent={type:'agent.started'|'agent.retrieving'|'agent.tool_started'|'agent.responding'|'agent.completed'|'agent.failed'|'document.processing'|'document.completed'|'document.failed'|'quiz.correct'|'quiz.incorrect'|'quiz.completed'|'memory.loaded';detail?:string;score?:number;total?:number};
export function dispatchMascot(event:MascotEvent){const store=useMascotStore.getState();switch(event.type){
 case 'agent.started':clearMascotError();store.setActivity('notice',null);store.setActivity('agent',{state:'thinking',message:'Let me connect this with what you already know…'});break;
 case 'agent.retrieving':store.setActivity('agent',{state:'thinking',message:'Looking through your selected study material…'});break;
 case 'agent.tool_started':store.setActivity('agent',{state:'thinking',message:'Working with a real learning tool…'});break;
 case 'agent.responding':store.setActivity('agent',{state:'teaching',message:'Let’s make this idea click. I’m building your explanation.'});break;
 case 'agent.completed':store.setActivity('agent',null);mascotNotice('teaching','Your explanation is ready. Ask me for a simpler example.',2400);break;
 case 'agent.failed':store.setActivity('agent',null);store.setActivity('error',{state:'error',message:event.detail||'That request could not finish. You can retry.'});break;
 case 'document.processing':clearMascotError();store.setActivity('document',{state:'reading',message:`Reading ${event.detail||'your document'} and building searchable knowledge…`});break;
 case 'document.completed':store.setActivity('document',null);store.setProgress(null);mascotNotice('greeting','Your document is ready! Let’s explore what’s inside.');break;
 case 'document.failed':store.setActivity('document',null);store.setProgress(null);store.setActivity('error',{state:'error',message:event.detail||'I could not read that document. Please retry.'});break;
 case 'quiz.correct':mascotNotice('celebrating','That’s it! Your practice is paying off.',3400);break;
 case 'quiz.incorrect':mascotNotice('encouraging','A missed answer is a chance to learn. Let’s look at the explanation.',3600);break;
 case 'quiz.completed':if(event.total&&event.score!==undefined)mascotNotice(event.score/event.total>=.8?'celebrating':'encouraging',`You scored ${event.score}/${event.total}. Your real progress has been saved.`,3800);break;
 case 'memory.loaded':break;
}}
