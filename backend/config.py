import os
from ipaddress import IPv4Address, AddressValueError
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')
os.environ.setdefault('ANONYMIZED_TELEMETRY','False')
DATA = Path(os.getenv('LUMINA_DATA_DIR', str(ROOT / 'backend' / 'data')))
if not DATA.is_absolute():
    DATA = ROOT / DATA
DATA.mkdir(parents=True, exist_ok=True)
KEY = os.getenv('NVIDIA_API_KEY', '').strip()
# Local convenience only; this file is never served or copied into the frontend.
if not KEY and (ROOT / 'API.txt').exists():
    raw = (ROOT / 'API.txt').read_text().strip()
    import re
    match = re.search(r'nvapi-[A-Za-z0-9_-]+', raw)
    KEY = match.group(0) if match else raw
BASE = os.getenv('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1').rstrip('/')
MODEL = os.getenv('NVIDIA_MODEL', 'nvidia/nemotron-3.5-bolt-e4b')
EMBED_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'nvidia')
EMBED_MODEL = os.getenv('EMBEDDING_MODEL', 'nvidia/nemotron-3.5-embed-1b')

# start.ps1 supplies this computer's active LAN addresses. Accept exact origins,
# never an arbitrary website or a wildcard, while the API stays on loopback.
FRONTEND_ORIGINS = {'http://localhost:5173','http://127.0.0.1:5173'}
for host in os.getenv('LUMINA_LAN_HOSTS','').split(','):
    try:
        address=IPv4Address(host.strip())
    except AddressValueError:
        continue
    if address.is_private and not (address.is_loopback or address.is_link_local or address.is_unspecified):
        FRONTEND_ORIGINS.add(f'http://{address}:5173')
