import json
import sqlite3
import uuid
from datetime import datetime, timezone
from .config import DATA

def now():
    return datetime.now(timezone.utc).isoformat()

def uid():
    return uuid.uuid4().hex

def db():
    con = sqlite3.connect(DATA / 'lumina.sqlite', timeout=30)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    return con

def init():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS profile (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS conversations (id TEXT PRIMARY KEY, title TEXT, created TEXT);
        CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, conversation_id TEXT, role TEXT, content TEXT, sources TEXT DEFAULT '[]', created TEXT);
        CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, title TEXT, type TEXT, pages INTEGER, chunks INTEGER, created TEXT, preview TEXT, path TEXT);
        CREATE TABLE IF NOT EXISTS quizzes (id TEXT PRIMARY KEY, topic TEXT, difficulty TEXT, questions TEXT, created TEXT);
        CREATE TABLE IF NOT EXISTS results (id TEXT PRIMARY KEY, quiz_id TEXT UNIQUE, topic TEXT, score REAL, total INTEGER, feedback TEXT, created TEXT);
        CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, run_id TEXT, node TEXT, status TEXT, detail TEXT, created TEXT);
        CREATE TABLE IF NOT EXISTS focus_sessions (id TEXT PRIMARY KEY, topic TEXT, planned_seconds INTEGER, status TEXT, active_seconds REAL, last_started TEXT, created TEXT, completed_at TEXT);
        ''')

def query(sql, args=()):
    with db() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]

def execute(sql, args=()):
    with db() as c:
        c.execute(sql, args)

FIELDS = {'name','education_level','field_of_interest','favorite_subjects','learning_goals','preferred_language','explanation_style','weak_topics','study_preferences','completed_goals'}

def profile():
    return {r['key']: json.loads(r['value']) for r in query('SELECT * FROM profile')}

def save_profile(values):
    for k,v in values.items():
        if k in FIELDS and isinstance(v, (str,list)):
            execute('INSERT OR REPLACE INTO profile VALUES (?,?)', (k,json.dumps(v,ensure_ascii=False)))
    return profile()

def event(run, node, detail, status='complete'):
    e = dict(id=uid(),run_id=run,node=node,status=status,detail=detail,created=now())
    execute('INSERT INTO events VALUES (:id,:run_id,:node,:status,:detail,:created)', e)
    return e
