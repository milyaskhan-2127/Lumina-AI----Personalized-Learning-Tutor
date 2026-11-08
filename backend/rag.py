import asyncio
import os
from pathlib import Path
import httpx
from .config import DATA, KEY, BASE, EMBED_MODEL, EMBED_PROVIDER
from .llm import AIError, error_message

_collection = None
_local = None

def collection():
    global _collection
    if _collection is None:
        import chromadb
        client = chromadb.PersistentClient(path=str(DATA/'chroma'))
        # A separate collection for each embedding space prevents mixing dimensions.
        import hashlib
        name = 'lumina-' + hashlib.sha256((EMBED_PROVIDER+EMBED_MODEL).encode()).hexdigest()[:16]
        _collection = client.get_or_create_collection(name,metadata={'hnsw:space':'cosine'})
    return _collection

async def embed(texts, mode):
    if EMBED_PROVIDER == 'local':
        def local():
            global _local
            if _local is None:
                from sentence_transformers import SentenceTransformer
                _local = SentenceTransformer(EMBED_MODEL)
            return _local.encode(texts,normalize_embeddings=True).tolist()
        return await asyncio.to_thread(local)
    # The hosted multimodal model currently fails on unequal-length passage batches.
    # Bound concurrency and submit one text per request; retain stable input ordering.
    if len(texts)>1:
        semaphore=asyncio.Semaphore(3)
        async def one(text):
            async with semaphore:
                return (await embed([text],mode))[0]
        return await asyncio.gather(*(one(text) for text in texts))
    if not KEY:
        raise AIError('NVIDIA API key is required to embed documents.')
    async with httpx.AsyncClient(timeout=90) as client:
        for attempt in range(3):
            try:
                r = await client.post(BASE+'/embeddings',headers={'Authorization':f'Bearer {KEY}'},json={'model':EMBED_MODEL,'input':texts,'input_type':mode,'truncate':'END'})
            except httpx.HTTPError:
                raise AIError('Could not connect to the NVIDIA embedding service.')
            if r.status_code in (429,500,502,503) and attempt<2:
                await asyncio.sleep(attempt+1)
                continue
            if r.is_error:
                raise AIError(error_message(r.status_code))
            return [x['embedding'] for x in sorted(r.json()['data'],key=lambda x:x['index'])]

def extract(path: Path, kind: str):
    if kind == 'pdf':
        import pymupdf as fitz
        with fitz.open(path) as doc:
            if len(doc)>500:
                raise ValueError('PDF limit is 500 pages.')
            return [(i+1,p.get_text()) for i,p in enumerate(doc)]
    if kind in ('docx','pptx'):
        import zipfile
        with zipfile.ZipFile(path) as z:
            if sum(i.file_size for i in z.infolist()) > 100*1024*1024:
                raise ValueError('Expanded document exceeds the 100 MB limit.')
    if kind == 'docx':
        from docx import Document
        d = Document(path)
        # DOCX has no reliable physical page numbering; use section 1.
        return [(1,'\n'.join([p.text for p in d.paragraphs]+[' | '.join(c.text for c in r.cells) for t in d.tables for r in t.rows]))]
    if kind == 'pptx':
        from pptx import Presentation
        return [(i+1,'\n'.join(s.text for s in slide.shapes if s.has_text_frame)) for i,slide in enumerate(Presentation(path).slides)]
    return [(1,path.read_text(encoding='utf-8-sig',errors='replace'))]

async def index_document(doc_id, title, path, kind):
    pages = await asyncio.to_thread(extract,path,kind)
    chunks=[]
    for page,text in pages:
        text=text.strip()
        for start in range(0,len(text),1000):
            part=text[start:start+1250].strip()
            if part:
                chunks.append((part,dict(document_id=doc_id,title=title,page=page,location='slide' if kind=='pptx' else 'page' if kind=='pdf' else 'section')))
    if not chunks:
        raise ValueError('No extractable text found. For scanned PDFs, run OCR first and upload the searchable copy.')
    if len(chunks)>2500:
        raise ValueError('Document exceeds 2,500 chunks. Split it into smaller files.')
    try:
        for start in range(0,len(chunks),32):
            batch=chunks[start:start+32]
            vectors=await embed([c[0] for c in batch],'passage')
            await asyncio.to_thread(collection().add,ids=[f'{doc_id}:{start+i}' for i in range(len(batch))],embeddings=vectors,documents=[c[0] for c in batch],metadatas=[c[1] for c in batch])
    except Exception:
        await asyncio.to_thread(collection().delete,where={'document_id':doc_id})
        raise
    return len(pages),len(chunks),'\n\n'.join(t for _,t in pages)[:12000]

async def retrieve(question, documents):
    if not documents:
        return []
    vector=await embed([question],'query')
    col=collection()
    if not col.count():
        return []
    result=await asyncio.to_thread(col.query,query_embeddings=vector,n_results=min(8,col.count()),where={'document_id':{'$in':documents}},include=['documents','metadatas','distances'])
    sources=[]
    for text,meta,distance in zip(result['documents'][0],result['metadatas'][0],result['distances'][0]):
        score=1-distance
        if score>=float(os.getenv('RETRIEVAL_MIN_SCORE','0.35')):
            sources.append(dict(**meta,text=text,score=round(score,3),label=f'S{len(sources)+1}'))
    return sources[:6]
