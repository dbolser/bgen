import os
import sys
from pathlib import Path

def run_bgenix():
    exe = Path(__file__).resolve().parent / 'bin' / 'bgenix'
    os.execv(str(exe), ['bgenix'] + sys.argv[1:])
