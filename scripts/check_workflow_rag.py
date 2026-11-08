import asyncio
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from backend import store,rag
async def main():
    store.init()
    docs=store.query("SELECT id,title FROM documents WHERE title='06-agent-workflows.pdf'")
    for question in ['Agent Workflows','agent workflow steps memory planning retrieval tools','Use your generate_quiz MCP tool to create a 3-question easy multiple-choice quiz on Agent Workflows from this selected PDF. Save it so I can answer in Quiz Studio.']:
        sources=await rag.retrieve(question,[d['id'] for d in docs])
        print(question[:45],len(sources),[s['score'] for s in sources],flush=True)
asyncio.run(main())
