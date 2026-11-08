r"""Real API integration checks, isolated from the student's actual database.
Run from the project root: .venv\Scripts\python.exe scripts/live_demo.py
Uses NVIDIA API credits. No credentials or private model reasoning are logged.
"""
import os
import sys
import json
import time
import subprocess
import uuid
from pathlib import Path
import httpx

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from scripts.make_demo_documents import make_documents
OUT=ROOT/'output'/('live-'+uuid.uuid4().hex[:8])
OUT.mkdir(parents=True)
env={**os.environ,'LUMINA_DATA_DIR':str(OUT/'data'),'PYTHONUNBUFFERED':'1','ANONYMIZED_TELEMETRY':'False'}
client=httpx.Client(base_url='http://127.0.0.1:8002',timeout=320,trust_env=False)
evidence=[]
process=None
log=(OUT/'server.log').open('w',encoding='utf-8')

def record(check,detail):
    evidence.append({'check':check,'status':'passed','detail':detail})
    print('PASS:',check,flush=True)
    (OUT/'verification.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')

def start():
    global process
    process=subprocess.Popen([sys.executable,'-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8002'],cwd=ROOT,env=env,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        if process.poll() is not None:
            raise RuntimeError('Test server exited. Inspect '+str(OUT/'server.log'))
        try:
            if client.get('/api/health').is_success:
                return
        except httpx.HTTPError:
            pass
        time.sleep(.5)
    raise RuntimeError('Test server did not start.')

def stop():
    if process and process.poll() is None:
        process.terminate()
        process.wait(timeout=20)

def request(method,path,**kwargs):
    r=client.request(method,'/api'+path,**kwargs)
    if r.is_error:
        raise RuntimeError(f'{path}: HTTP {r.status_code}: {r.text[:200]}')
    return r.json()

def chat(ident,message,documents=None):
    answer='';sources=[];events=[]
    with client.stream('POST',f'/api/conversations/{ident}/chat',json={'message':message,'document_ids':documents or []}) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line.startswith('data: '):
                continue
            item=json.loads(line[6:])
            if item['type']=='error':
                raise RuntimeError(item['message'])
            if item['type']=='token': answer+=item['text']
            if item['type']=='replace': answer=item['text']
            if item['type']=='sources': sources=item['sources']
            if item['type']=='event': events.append(item['event'])
    assert answer,'No real response received'
    return answer,sources,events

def main():
    start()
    health=request('GET','/health')
    assert health['configured']
    c=request('POST','/conversations')['id']
    answer,_,events=chat(c,'My preferred name is Demo Learner and my field of interest is robotics. Remember these. Explain emergence in two sentences.')
    record('Live NVIDIA response and memory extraction',{'model':health['model'],'response_characters':len(answer),'nodes':[e['node'] for e in events]})
    p=request('GET','/profile')
    assert 'Demo Learner' in p.get('name','') and 'robot' in p.get('field_of_interest','').lower(),p
    answer,_,_=chat(c,'What concept did I just ask you to explain? Answer briefly.')
    assert 'emergen' in answer.lower(),answer
    record('Multi-turn short-term conversation memory',{'follow_up_mentions':'emergence'})
    files=make_documents(OUT/'fixtures')
    docs=[]
    for path in files:
        with path.open('rb') as f:
            d=request('POST','/documents',files={'file':(path.name,f)})
        docs.append(d)
    assert len(docs)==5 and all(d['chunks']>0 for d in docs)
    record('Five-document extraction, NVIDIA embedding and Chroma persistence',{'documents':[{'title':d['title'],'chunks':d['chunks']} for d in docs]})
    answer,sources,events=chat(c,'According to the Sable simulation notes, exactly how many agents are there and what is their starting energy? Cite the original page.',[d['id'] for d in docs])
    assert '37' in answer and '12' in answer,answer
    assert any(s['page']==2 and s['title']=='01-agent-modeling.pdf' for s in sources),sources
    assert any('['+s['label']+']' in answer for s in sources)
    record('Document-grounded answer with correct PDF page citation',{'answer':answer,'source_locations':[{'title':s['title'],'page':s['page'],'score':s['score']} for s in sources]})
    answer,_,events=chat(c,'Calculate sqrt(144) + 2**3 using the calculator tool.')
    assert '20' in answer and any(e['node']=='mcp' and 'calculate_expression' in e['detail'] for e in events),answer
    record('Real MCP discovery and calculator invocation',{'transport':'stdio','result':20})
    q=request('POST','/quizzes',json={'topic':'Agent-based modeling','count':3,'difficulty':'easy','kind':'mcq'})
    assert len(q['questions'])==3 and all('answer' not in x for x in q['questions'])
    result=request('POST',f'/quizzes/{q["id"]}/submit',json={'answers':[0]*3})
    assert len(result['feedback'])==3 and result['total']==3
    analytics=request('GET','/analytics')
    assert len(analytics['results'])==1
    record('MCP quiz generation, protected answer keys, grading and analytics',{'questions':3,'score':result['score'],'total':3})
    answer,_,events=chat(c,'Use your progress tool to tell me how many quizzes I have completed.')
    assert any(e['node']=='mcp' and 'get_student_progress' in e['detail'] for e in events)
    record('Agent-selected MCP progress tool',{'transport':'stdio','completed_quizzes':1})
    stop();start()
    p=request('GET','/profile')
    assert 'Demo Learner' in p.get('name','') and len(request('GET','/documents'))==5
    fresh=request('POST','/conversations')['id']
    answer,_,_=chat(fresh,'What is my preferred name and field of interest? Keep it brief.')
    assert 'Demo Learner' in answer and 'robot' in answer.lower(),answer
    record('Backend restart and new-session long-term memory recall',{'answer':answer,'retained_documents':5,'retained_results':len(request('GET','/analytics')['results'])})
    answer,sources,_=chat(fresh,'How many agents are in the Sable simulation?',[docs[0]['id']])
    assert '37' in answer and sources
    record('Chroma retrieval after process restart',{'retrieved_sources':len(sources)})
    bad=client.post('/api/documents',files={'file':('evil.exe',b'bad')})
    empty=client.post('/api/documents',files={'file':('empty.txt',b'')})
    assert bad.status_code==415 and empty.status_code==422
    record('Upload validation and empty-document errors',{'unsupported_status':415,'empty_status':422})
    print('Evidence:',OUT/'verification.json',flush=True)

if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        evidence.append({'check':'Live demonstration','status':'failed','detail':str(exc)})
        (OUT/'verification.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
        print('FAIL:',str(exc),flush=True)
        raise
    finally:
        stop();log.close();client.close()
