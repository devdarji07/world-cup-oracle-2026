import joblib
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
from sklearn.multioutput import MultiOutputRegressor
from src.feature_engineering import load_data, build_match_features, export_features

ROOT = Path(__file__).resolve().parents[1]


def train_models():
    matches, rankings, markets, groups = load_data(
        ROOT / "data" / "matches.csv",
        ROOT / "data" / "fifa_rankings.csv",
        ROOT / "data" / "squad_market_values.csv",
        ROOT / "data" / "worldcup_groups.csv",
    )
    features = build_match_features(matches, rankings, markets)
    export_features(features, str(ROOT / "data" / "features.csv"))
    model_features = [
        "teamA_rank",
        "teamB_rank",
        "rank_difference",
        "teamA_market_value",
        "teamB_market_value",
        "market_value_difference",
        "teamA_last5_form",
        "teamB_last5_form",
        "teamA_last10_winrate",
        "teamB_last10_winrate",
        "teamA_avg_goals_scored",
        "teamB_avg_goals_scored",
        "teamA_avg_goals_conceded",
        "teamB_avg_goals_conceded",
        "head_to_head_wins",
        "head_to_head_draws",
    ]
    filtered = features.dropna(subset=model_features + ["result"])
    X = filtered[model_features]
    y = filtered["result"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.18, random_state=42, stratify=y)
    print("Training match outcome model (XGBoost)...", flush=True)
    model = xgb.XGBClassifier(objective="multi:softprob", eval_metric="mlogloss", use_label_encoder=False, random_state=42, n_estimators=10, verbosity=0)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    print("Match Outcome Accuracy:", accuracy_score(y_test, predictions))
    print(classification_report(y_test, predictions))
    (ROOT / "models").mkdir(parents=True, exist_ok=True)
    joblib.dump(model, str(ROOT / "models" / "match_outcome_model.pkl"))
    print("Training score prediction model (XGBoost regressor)...", flush=True)
    score_model = MultiOutputRegressor(
        xgb.XGBRegressor(objective="reg:squarederror", random_state=42, n_estimators=100, verbosity=0)
    )
    score_targets = filtered[["home_score", "away_score"]].fillna(0)
    score_model.fit(X, score_targets)
    joblib.dump(score_model, str(ROOT / "models" / "score_prediction_model.pkl"))
    print("Models saved to", str(ROOT / "models"), flush=True)


if __name__ == "__main__":
    train_models()
