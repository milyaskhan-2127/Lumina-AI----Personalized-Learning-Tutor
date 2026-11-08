import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import httpx
from backend.config import KEY,BASE
async def main():
    async with httpx.AsyncClient(timeout=30) as c:
        r=await c.get(BASE+'/models',headers={'Authorization':'Bearer '+KEY})
        print('Model catalog HTTP',r.status_code)
        if r.is_success:
            for item in r.json().get('data',[]):
                name=item['id']
                if any(x in name for x in ('llama-3','nemotron','nv-embedqa','qwen3')):
                    print(name)
asyncio.run(main())
