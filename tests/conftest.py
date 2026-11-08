import os
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
(ROOT/'output').mkdir(exist_ok=True)
os.environ['LUMINA_DATA_DIR']=tempfile.mkdtemp(prefix='unit-',dir=ROOT/'output')
os.environ['ANONYMIZED_TELEMETRY']='False'
