import ast
import re
from pathlib import Path

def readSetting(name: str):
    text = Path("src/settings.py").read_text().splitlines()
    pattern = re.compile(rf"^{name}\s*=\s*(.+)$")
    for line in text:
        m = pattern.match(line)
        if m:
            return ast.literal_eval(m.group(1).strip())
    raise KeyError(f"{name} not found in settings.py")
