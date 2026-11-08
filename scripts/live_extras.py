"""Supplemental real-API tests: short answers, regeneration, language and MCP memory."""
import json
from live_demo import start,stop,request,chat,record,OUT,log,client

try:
    start()
    quiz=request('POST','/quizzes',json={'topic':'Define emergence in agent-based modeling','count':1,'difficulty':'easy','kind':'short'})
    assert quiz['questions'][0]['options']==[]
    result=request('POST',f'/quizzes/{quiz["id"]}/submit',json={'answers':['Emergence means system-level patterns arise from the local interactions of individual autonomous agents.']})
    assert result['total']==1 and len(result['feedback'])==1
    record('Live MCP short-answer quiz and semantic grading',{'score':result['score'],'feedback':result['feedback']})
    session=request('POST','/conversations')['id']
    chat(session,'Explain positive feedback in one sentence.')
    response=client.post(f'/api/conversations/{session}/chat',json={'message':'Explain positive feedback in one sentence.','regenerate':True})
    assert response.status_code==200 and '"type": "done"' in response.text,response.text[:100]
    messages=request('GET','/conversations/'+session)
    assert len(messages)==2 and messages[0]['role']=='user' and messages[1]['role']=='assistant'
    record('Response regeneration without duplicated conversation turns',{'persisted_messages':2})
    request('PUT','/profile',json={'name':'Demo Learner','preferred_language':'Roman Urdu','explanation_style':'Simple examples'})
    new=request('POST','/conversations')['id']
    answer,_,_=chat(new,'Negative feedback ko ek seedhi misal se samjhao. Roman Urdu mein jawab do.')
    assert any(word in answer.lower() for word in ('hai','hota','jaise','misal')),answer
    record('Preferred language and simple-example personalization',{'language':'Roman Urdu','answer':answer})
    answer,_,events=chat(new,'Remember that I find probability difficult. Use your learning progress tool to save this difficulty.')
    assert any(e['node']=='mcp' and 'save_learning_progress' in e['detail'] for e in events)
    assert 'probability' in request('GET','/profile').get('weak_topics','').lower()
    record('Actual MCP difficulty-memory write',{'transport':'stdio','topic':'probability'})
    print('Evidence:',OUT/'verification.json',flush=True)
finally:
    stop();log.close();client.close()
