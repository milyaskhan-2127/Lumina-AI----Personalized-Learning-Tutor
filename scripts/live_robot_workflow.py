"""Verify the exact document -> explanation -> MCP quiz -> saved result demo."""
from pathlib import Path
from live_demo import start,stop,request,chat,record,OUT,log,client
ROOT=Path(__file__).resolve().parent.parent
try:
    start()
    with (ROOT/'examples'/'06-agent-workflows.pdf').open('rb') as f:
        document=request('POST','/documents',files={'file':('Agent Workflows.pdf',f)})
    ident=request('POST','/conversations')['id']
    answer,sources,events=chat(ident,'Explain Agent Workflows using this lecture. Include memory, routing, retrieval, tools, response and memory update. Cite the page.',[document['id']])
    assert sources and any(s['page']==1 for s in sources)
    record('Exact demo document and cited workflow explanation',{'sources':len(sources),'answer_characters':len(answer)})
    answer,sources,events=chat(ident,'Use your generate_quiz MCP tool to create a 3-question easy multiple-choice quiz on Agent Workflows from this selected PDF. Save it so I can answer in Quiz Studio.',[document['id']])
    assert any(e['node']=='mcp' and 'generate_quiz' in e['detail'] and e['status']=='complete' for e in events),events
    quizzes=request('GET','/quizzes')
    assert quizzes
    q=request('GET','/quizzes/'+quizzes[0]['id'])
    assert len(q['questions'])==3
    record('Document-grounded MCP quiz from a follow-up request',{'questions':3,'source_count':len(sources),'transport':'stdio'})
    result=request('POST','/quizzes/'+q['id']+'/submit',json={'answers':[0,0,0]})
    assert result['total']==3 and len(request('GET','/analytics')['results'])==1
    record('Actual answer grading and persistent learning result',{'score':result['score'],'total':3})
    print('Evidence:',OUT/'verification.json',flush=True)
finally:
    stop();log.close();client.close()
