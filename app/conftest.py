"""
Makes the app's own modules importable from tests.

The app is written to run with `frontend/app` as the import root (`from ui...`,
`from service...`), so pytest needs that directory on sys.path before it
collects anything under tests/.
"""
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
