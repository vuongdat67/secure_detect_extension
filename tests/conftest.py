import os
import sys
from pathlib import Path

# Add repository root to sys.path so `import backend` works when running pytest from repo root.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Ensure default env flag keeps models lightweight in tests.
os.environ.setdefault("SECURECOPILOT_LOAD_MODELS", "0")
