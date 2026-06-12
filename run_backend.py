"""Start the World Cup Oracle API from the repository root."""

from pathlib import Path
import sys

import uvicorn

ROOT = Path(__file__).resolve().parent
PROJECT_DIR = ROOT / "worldcup_predictor"
sys.path.insert(0, str(PROJECT_DIR))


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
