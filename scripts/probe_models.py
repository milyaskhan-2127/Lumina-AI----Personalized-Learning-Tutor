import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import httpx
from backend.config import KEY,BASE
async def probe(model,embedding=False,mode='query',count=1):
    async with httpx.AsyncClient(timeout=100) as c:
        payload={'model':model,'input':['Hello learning']*count,'input_type':mode,'truncate':'END'} if embedding else {'model':model,'messages':[{'role':'user','content':'Reply with only: Lumina is connected.'}],'max_tokens':60,'stream':False}
        r=await c.post(BASE+('/embeddings' if embedding else '/chat/completions'),headers={'Authorization':'Bearer '+KEY},json=payload)
        print(model,mode,count,'HTTP',r.status_code,flush=True)
        if r.is_success:
            print('dimensions: '+str(len(r.json()['data'][0]['embedding'])) if embedding else str(r.json()['choices'][0]['message'].get('content') or 'No final content returned'),flush=True)
        else:
            print('Model endpoint unavailable',flush=True)
async def main():
    from backend.rag import extract, embed
    pages=extract(Path(__file__).resolve().parent.parent/'examples'/'01-agent-modeling.pdf','pdf')
    print('PDF passage lengths:',[len(t) for _,t in pages],flush=True)
    async def check(label,texts):
        async with httpx.AsyncClient(timeout=60) as c:
            r=await c.post(BASE+'/embeddings',headers={'Authorization':'Bearer '+KEY},json={'model':'nvidia/nemotron-3.5-embed-1b','input':texts,'input_type':'passage','truncate':'END'})
            print(label,'HTTP',r.status_code,flush=True)
    await asyncio.gather(check('first',[pages[0][1]]),check('second',[pages[1][1]]),check('normalized-batch',[' '.join(t.split()) for _,t in pages]))
asyncio.run(main())
