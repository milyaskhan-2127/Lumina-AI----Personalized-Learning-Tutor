export type Doc={id:string;title:string;type:string;pages:number;chunks:number;created?:string;preview?:string};
export type Conversation={id:string;title:string;created:string};
export type Source={label:string;document_id:string;title:string;page:number;location:string;text:string;score?:number};
export type Message={id?:string;role:string;content:string;sources?:Source[];error?:boolean};
export type Event={id:string;run_id:string;node:string;status:string;detail:string;created:string};
export type Result={id:string;topic:string;score:number;total:number;created:string;feedback?:{correct:boolean;answer:string;explanation:string}[]};
export type Analytics={study_seconds?:number;study_sessions?:{id:string;topic:string;seconds:number;completed_at:string}[];average:number;streak:number;sessions:number;documents:number;messages:number;mastered:string[];weak_topics:string;results:Result[]};
export type Quiz={id:string;topic:string;difficulty:string;questions:{question:string;options:string[];source_labels?:string[]}[];sources?:Source[];result?:Result};
