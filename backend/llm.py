import asyncio
import json
import httpx
from .config import KEY, BASE, MODEL

class AIError(Exception):
    pass

def error_message(status):
    return {401:'NVIDIA rejected the API key. Check API.txt or NVIDIA_API_KEY.',403:'This NVIDIA key cannot access the selected model.',410:'The selected NVIDIA model has been retired. Set an available NVIDIA_MODEL or EMBEDDING_MODEL in .env and restart.',429:'NVIDIA rate limit reached. Please wait a moment and retry.'}.get(status, f'NVIDIA service returned HTTP {status}. Please retry.')

async def completion(messages, *, stream=False, json_mode=False, max_tokens=2400):
    if not KEY:
        raise AIError('Add your NVIDIA key to API.txt or NVIDIA_API_KEY, then restart the backend.')
    body = dict(model=MODEL,messages=messages,temperature=0.3,max_tokens=max_tokens,stream=stream)
    if json_mode:
        body['response_format'] = {'type':'json_object'}
    async with httpx.AsyncClient(timeout=httpx.Timeout(120,connect=20)) as client:
        for attempt in range(3):
            try:
                response = await client.post(BASE+'/chat/completions',headers={'Authorization':f'Bearer {KEY}'},json=body)
            except httpx.HTTPError:
                if attempt < 2:
                    await asyncio.sleep(attempt+1)
                    continue
                raise AIError('NVIDIA connection timed out or is unavailable. Please retry.')
            if response.status_code in (429,500,502,503) and attempt < 2:
                await asyncio.sleep(attempt+1)
                continue
            if response.is_error:
                raise AIError(error_message(response.status_code))
            choices=response.json().get('choices',[])
            content=choices[0].get('message',{}).get('content') if choices else None
            if not content:
                raise AIError('NVIDIA returned no final answer. Choose a non-reasoning model or increase the token budget.')
            return content

async def tokens(messages):
    if not KEY:
        raise AIError('Add your NVIDIA key to API.txt or NVIDIA_API_KEY, then restart the backend.')
    async with httpx.AsyncClient(timeout=httpx.Timeout(120,connect=20)) as client:
        for attempt in range(3):
            try:
                async with client.stream('POST',BASE+'/chat/completions',headers={'Authorization':f'Bearer {KEY}'},json=dict(model=MODEL,messages=messages,temperature=0.4,max_tokens=2800,stream=True)) as r:
                    if r.status_code in (429,500,502,503) and attempt < 2:
                        await r.aread()
                        await asyncio.sleep(attempt+1)
                        continue
                    if r.is_error:
                        raise AIError(error_message(r.status_code))
                    async for line in r.aiter_lines():
                        if line.startswith('data: ') and line[6:] != '[DONE]':
                            data = json.loads(line[6:])
                            choices=data.get('choices') or []
                            if not choices:
                                continue  # usage/metadata events contain no completion choice
                            content = choices[0].get('delta',{}).get('content')
                            if content:
                                yield content
                    return
            except httpx.HTTPError:
                # Never retry after emitting tokens: this could duplicate a response.
                raise AIError('The NVIDIA stream was interrupted. You can regenerate this answer.')

def parse_json(text):
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n',1)[1].rsplit('```',1)[0]
    return json.loads(text)
