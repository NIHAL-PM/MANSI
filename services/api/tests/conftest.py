import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
os.environ.setdefault("MANSI_AUTH_JWT_SECRET", "test-secret-not-for-production")
sys.path.insert(0, str(root))
sys.path.insert(0, str(root.parent / "shared" / "python"))
