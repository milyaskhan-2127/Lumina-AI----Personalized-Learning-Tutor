import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from backend.llm import completion
from backend.rag import embed

async def main():
    reply=await completion([{'role':'user','content':'Reply with only: Lumina is connected.'}],max_tokens=30)
    print('LLM:',reply)
    vector=await embed(['Learning is building understanding.'],'query')
    print('Embeddings: connected, dimensions =',len(vector[0]))

if __name__=='__main__':
    asyncio.run(main())
