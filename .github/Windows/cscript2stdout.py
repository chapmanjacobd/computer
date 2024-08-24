import subprocess
import sys
import tempfile
from pathlib import Path

args = sys.argv
temp_path = tempfile.mktemp(suffix='.csv')
subprocess.run(['cscript.exe', args[1], args[2], temp_path])
print(Path(temp_path).read_text())
