import { FileText, Upload } from 'lucide-react';
import type { Doc } from '../types';

type Props={docs:Doc[];selected:string[];onChange:(ids:string[])=>void;mode:'documents'|'general';onModeChange:(mode:'documents'|'general')=>void;busy:boolean;onUpload:()=>void};

export function QuizDocumentPicker({docs,selected,onChange,mode,onModeChange,busy,onUpload}:Props){
 return <div className="quiz-source-picker">
  <label>Quiz source<select aria-label="Quiz source" value={mode} disabled={busy} onChange={e=>onModeChange(e.target.value as Props['mode'])}><option value="documents">Selected documents only</option><option value="general">General topic</option></select></label>
  {mode==='documents'&&<fieldset className="quiz-document-picker"><legend>Choose documents</legend>
   {docs.length?<div className="quiz-document-options">{docs.map(doc=><label className="quiz-document-option" key={doc.id}><input type="checkbox" checked={selected.includes(doc.id)} disabled={busy} onChange={e=>onChange(e.target.checked?[...selected,doc.id]:selected.filter(id=>id!==doc.id))}/><FileText size={16}/><span>{doc.title}<small>{doc.chunks} searchable excerpts</small></span></label>)}</div>:<button type="button" className="text-button" disabled={busy} onClick={onUpload}><Upload size={15}/>Upload study material</button>}
   <small className="quiz-source-help">Only checked documents will be used. Leave Topic blank to practice the whole document.</small>
  </fieldset>}
 </div>;
}
