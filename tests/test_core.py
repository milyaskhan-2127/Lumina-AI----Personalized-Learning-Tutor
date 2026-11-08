import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import store
from backend.mcp_server import calculate_expression
from backend.agent import graph

def test_calculator_safety():
    assert calculate_expression('sqrt(144) + 2**3')['result']==20
    for expr in ["__import__('os').system('whoami')",'2**1000000','[1][0]','1/0','abs(-2,3)']:
        with pytest.raises((ValueError,ZeroDivisionError)):
            calculate_expression(expr)

def test_api_validation_and_memory():
    with TestClient(app) as c:
        assert c.put('/api/profile',json={'name':'Demo','field_of_interest':'Robotics'}).status_code==200
        assert c.get('/api/profile').json()['name']=='Demo'
        assert c.delete('/api/profile/name').status_code==200
        assert 'name' not in c.get('/api/profile').json()
        assert c.post('/api/documents',files={'file':('bad.exe',b'bad')}).status_code==415
        assert c.post('/api/documents',files={'file':('empty.txt',b'')}).status_code==422
        assert c.post('/api/quizzes',json={'topic':'Hi','count':500}).status_code==422
        assert c.post('/api/conversations/missing/chat',json={'message':'hello'}).status_code==404

def test_private_answer_key_and_idempotent_grading():
    with TestClient(app) as c:
        ident=store.uid()
        questions=[{'question':'2+2?','options':['3','4','5','6'],'answer':1,'explanation':'Two pairs make four.'}]
        store.execute('INSERT INTO quizzes VALUES (?,?,?,?,?)',(ident,'Arithmetic','easy',json.dumps(questions),store.now()))
        quiz=c.get('/api/quizzes/'+ident).json()
        assert 'answer' not in quiz['questions'][0] and 'explanation' not in quiz['questions'][0]
        r=c.post('/api/quizzes/'+ident+'/submit',json={'answers':[1]}).json()
        assert r['score']==1
        repeated=c.post('/api/quizzes/'+ident+'/submit',json={'answers':[0]}).json()
        assert repeated['id']==r['id'] and repeated['score']==1
        assert c.delete('/api/results/'+r['id']).status_code==200
        assert 'result' not in c.get('/api/quizzes/'+ident).json()

def test_bounded_retrieval_retry_and_refusal(monkeypatch):
    import backend.agent as agent
    calls=[]
    async def fake_completion(messages,**kwargs):
        if kwargs.get('json_mode'):
            return json.dumps({'route':'retrieve','query':'quantum physics','memories':{}})
        return 'quantum physics'
    async def no_evidence(question,documents):
        calls.append(question)
        return []
    async def run():
        queue=asyncio.Queue()
        result=await graph.ainvoke({'run':store.uid(),'question':'Explain quantum physics','document_ids':['test-doc'],'history':[],'queue':queue})
        assert 'sufficient relevant evidence' in result['answer']
        assert len(calls)==2
        events=[]
        while not queue.empty():
            events.append(await queue.get())
        assert any(e['type']=='event' and e['event']['node']=='retry' for e in events)
    store.init()
    monkeypatch.setattr(agent,'completion',fake_completion)
    monkeypatch.setattr(agent.rag,'retrieve',no_evidence)
    asyncio.run(run())

def test_nvidia_retry_and_stream_metadata(monkeypatch):
    import httpx
    import backend.llm as llm
    original=httpx.AsyncClient
    attempts=[]
    def handler(request):
        body=json.loads(request.content)
        if body.get('stream'):
            return httpx.Response(200,text='data: {"choices": []}\n\ndata: {"choices": [{"delta": {"content": "Connected"}}]}\n\ndata: [DONE]\n\n',headers={'content-type':'text/event-stream'})
        attempts.append(1)
        return httpx.Response(429) if len(attempts)==1 else httpx.Response(200,json={'choices':[{'message':{'content':'Ready'}}]})
    monkeypatch.setattr(llm,'KEY','unit-test-key')
    monkeypatch.setattr(llm.httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(handler)))
    async def run():
        assert await llm.completion([{'role':'user','content':'Hi'}])=='Ready'
        assert len(attempts)==2
        chunks=[chunk async for chunk in llm.tokens([{'role':'user','content':'Hi'}])]
        assert chunks==['Connected']
    asyncio.run(run())

def test_focus_timer_records_only_completed_actual_time():
    from datetime import datetime,timedelta,timezone
    with TestClient(app) as c:
        s=c.post('/api/focus/start',json={'topic':'Agent workflows','planned_seconds':60}).json()
        assert c.post('/api/focus/'+s['id']+'/complete').status_code==409
        assert c.get('/api/analytics').json()['study_seconds']==0
        paused=c.post('/api/focus/'+s['id']+'/pause').json()
        assert paused['status']=='paused'
        assert c.post('/api/focus/'+s['id']+'/resume').json()['status']=='running'
        # Move this isolated fixture's start time back to verify the server clock gate.
        store.execute('UPDATE focus_sessions SET last_started=? WHERE id=?',((datetime.now(timezone.utc)-timedelta(seconds=61)).isoformat(),s['id']))
        complete=c.post('/api/focus/'+s['id']+'/complete').json()
        assert complete['status']=='completed'
        assert c.get('/api/analytics').json()['study_seconds']==60
        assert c.post('/api/focus/'+s['id']+'/complete').status_code==200
        assert c.get('/api/analytics').json()['study_seconds']==60
        other=c.post('/api/focus/start',json={'planned_seconds':60}).json()
        assert c.post('/api/focus/'+other['id']+'/reset').json()['status']=='cancelled'
        assert c.get('/api/analytics').json()['study_seconds']==60

def test_document_quiz_retrieves_subject_and_passes_real_evidence(monkeypatch):
    import backend.agent as agent
    asked=[]
    async def retrieve(question,documents):
        asked.append(question)
        return [{'label':'S1','text':'A workflow loads memory, selects tools, and answers.','document_id':'doc','title':'Lecture','page':1,'location':'page','score':.6}]
    async def tool(name,args):
        assert name=='generate_quiz' and args['count']==3
        assert 'loads memory' in args['context']
        return {'discovered_tools':['generate_quiz'],'result':{'quiz_id':'fixture-quiz'}}
    monkeypatch.setattr(agent.rag,'retrieve',retrieve)
    monkeypatch.setattr(agent,'invoke',tool)
    async def run():
        result=await agent.retrieval({'run':store.uid(),'question':'Generate a practice quiz with your MCP tool','document_ids':['doc'],'plan':{'tool':'generate_quiz','query':'MCP quiz command','args':{'topic':'Agent Workflows','count':3}},'queue':asyncio.Queue()})
        assert result['tool']['result']['quiz_id']=='fixture-quiz'
    store.init();asyncio.run(run())
    assert asked==['Agent Workflows']

def test_quiz_answer_formats_are_validated_without_guessing():
    from backend.mcp_server import validate_questions
    def data(answer):return {'questions':[{'question':'Which is correct?','options':['one','two','three','four'],'answer':answer,'explanation':'Expected option two.'}]}
    assert validate_questions(data('B'),'mcq',1)[0]['answer']==1
    assert validate_questions(data('two'),'mcq',1)[0]['answer']==1
    with pytest.raises(ValueError):validate_questions(data(4),'mcq',1)
    with pytest.raises(ValueError):validate_questions(data(True),'mcq',1)
