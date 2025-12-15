from __future__ import annotations

import os
import sys
from pathlib import Path

# Подменяем системные пути для тестов
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Фейковые енвы для тестов
os.environ.setdefault("BOT_TOKEN", "test-bot-token")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SHEET_DOC_ID", "dummy-sheet")
os.environ.setdefault("CHROMA_PERSIST_DIR", "dummy-chroma")
