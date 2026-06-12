# World Cup Oracle 2026

A production-grade AI/ML platform for predicting FIFA World Cup 2026 outcomes from the group stage through the final.

## Project structure

- `worldcup_predictor/data/`
- `worldcup_predictor/models/`
- `worldcup_predictor/results/`
- `worldcup_predictor/src/`
- `worldcup_predictor/backend/`
- `worldcup_predictor/frontend/`

## Setup

1. Install Python dependencies

   ```powershell
   cd worldcup_predictor
   python -m pip install -U pip
   python -m pip install fastapi uvicorn pandas numpy scikit-learn xgboost joblib python-dotenv
   ```

2. Install frontend dependencies

   ```bash
   cd worldcup_predictor/frontend
   npm install
   ```

3. Copy your dataset files into `worldcup_predictor/data/`:
   - `matches.csv`
   - `fifa_rankings.csv`
   - `squad_market_values.csv`
   - `worldcup_groups.csv`

4. Train models

   ```powershell
   cd worldcup_predictor
   python -m src.train_model
   ```

5. Start backend

   ```powershell
   cd ..
   .\start_backend.ps1
   ```

   Alternatively, from the repository root:

   ```powershell
   .\.venv\Scripts\python.exe run_backend.py
   ```

6. Start frontend

   ```bash
   cd worldcup_predictor/frontend
   npm run dev
   ```

## API Endpoints

- `POST /predict-match`
- `POST /simulate-group-stage`
- `POST /simulate-tournament`
- `POST /run-monte-carlo`
- `GET /group-stage-results`
- `GET /knockout-bracket`
- `GET /champion-odds`
- `GET /group-standings`
- `GET /best-third-teams`
- `GET /predict-match/{home_team}/{away_team}`
- `GET /health`

## Notes

- The current frontend is built with Next.js and TailwindCSS.
- The backend uses FastAPI with model-serving endpoints.
- Monte Carlo sweep results are stored in `worldcup_predictor/results/champion_odds.csv`.
- Tournament simulations store match predictions, standings, and best-third-place rankings in `results/`.
- Run `POST /simulate-tournament` before opening the dashboard, then run `POST /run-monte-carlo?simulations=10000` to refresh champion odds.
