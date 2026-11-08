"""Check the running servers, secret isolation, and frontend build without printing secrets."""
from pathlib import Path
import sys
import httpx
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from backend.config import KEY
with httpx.Client(timeout=20,trust_env=False) as c:
    assert c.get('http://127.0.0.1:5173/').status_code==200
    assert c.get('http://127.0.0.1:8000/api/health').json()['configured']
    for path in ('API.txt','api.txt','.env','backend/data/lumina.sqlite'):
        response=c.get('http://127.0.0.1:5173/'+path)
        assert response.status_code in (403,404),f'Private path was exposed: {path}'
        assert not KEY or KEY not in response.text
    assert c.post('http://127.0.0.1:8000/api/conversations',headers={'Origin':'https://example.invalid'}).status_code==403
    print('PASS: frontend/backend readiness; private-file access blocked; foreign-origin mutation blocked')
    files=[p for p in (ROOT/'dist').rglob('*') if p.is_file() and p.suffix in ('.html','.js','.css','.json')]
    assert files,'Production build is missing'
    assert not KEY or all(KEY not in p.read_text(encoding='utf-8',errors='ignore') for p in files)
    print('PASS: NVIDIA key absent from production assets')
