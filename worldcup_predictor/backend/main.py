from pathlib import Path
import sys

# Ensure `worldcup_predictor` package root is on sys.path so `src` is importable
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import match_router, simulation_router, results_router

app = FastAPI(title="World Cup Oracle 2026 API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match_router)
app.include_router(simulation_router)
app.include_router(results_router)


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": True}
