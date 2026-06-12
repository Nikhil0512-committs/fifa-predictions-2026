from __future__ import annotations

import json
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, log_loss, mean_absolute_error, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from fifa_predictor import config
from fifa_predictor.data.ingest import load_training_data, normalise_team_features
from fifa_predictor.features.build import add_derived_team_features, add_experimental_features, model_feature_columns


@dataclass
class TrainingArtifacts:
    classifier: Pipeline
    goals_for_model: Pipeline
    goals_against_model: Pipeline
    metrics: dict


def _preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    numeric = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical = [c for c in df.columns if c not in numeric]
    return ColumnTransformer(
        [
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ]
    )


def _candidate_classifiers(random_state: int = 42) -> dict[str, object]:
    models: dict[str, object] = {
        "random_forest": RandomForestClassifier(n_estimators=350, min_samples_leaf=2, class_weight="balanced", random_state=random_state),
        "neural_network": MLPClassifier(hidden_layer_sizes=(48, 24), max_iter=700, random_state=random_state),
    }
    try:
        from xgboost import XGBClassifier

        models["xgboost"] = XGBClassifier(n_estimators=250, max_depth=3, learning_rate=0.04, eval_metric="logloss", random_state=random_state)
    except Exception:
        pass
    try:
        from lightgbm import LGBMClassifier

        models["lightgbm"] = LGBMClassifier(n_estimators=250, learning_rate=0.04, random_state=random_state, verbose=-1)
    except Exception:
        pass
    try:
        from catboost import CatBoostClassifier

        models["catboost"] = CatBoostClassifier(iterations=250, depth=4, learning_rate=0.04, verbose=False, random_seed=random_state)
    except Exception:
        pass
    return models


def train_models(random_state: int = 42) -> TrainingArtifacts:
    train, _ = load_training_data()
    train = add_experimental_features(add_derived_team_features(normalise_team_features(train)))
    y = train["quarter_finalist"].astype(int)
    feature_cols = model_feature_columns(train)
    x = train[feature_cols]

    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=random_state)
    results = {}
    best_name = ""
    best_score = -np.inf
    best_pipe: Pipeline | None = None
    for name, estimator in _candidate_classifiers(random_state).items():
        pipe = Pipeline([("preprocess", _preprocessor(x)), ("model", estimator)])
        probabilities = cross_val_predict(pipe, x, y, cv=cv, method="predict_proba")[:, 1]
        predicted = (probabilities >= 0.5).astype(int)
        auc = roc_auc_score(y, probabilities)
        results[name] = {
            "accuracy": float(accuracy_score(y, predicted)),
            "roc_auc": float(auc),
            "log_loss": float(log_loss(y, probabilities)),
        }
        if auc > best_score:
            best_name = name
            best_score = auc
            best_pipe = pipe

    assert best_pipe is not None
    best_pipe.fit(x, y)

    goals_for_target = train["goals_for_per_match"]
    goals_against_target = train["goals_against_per_match"]
    regressor_for = Pipeline([("preprocess", _preprocessor(x)), ("model", GradientBoostingRegressor(random_state=random_state))])
    regressor_against = Pipeline([("preprocess", _preprocessor(x)), ("model", GradientBoostingRegressor(random_state=random_state))])
    regressor_for.fit(x, goals_for_target)
    regressor_against.fit(x, goals_against_target)
    goals_for_pred = cross_val_predict(regressor_for, x, goals_for_target, cv=4)
    goals_against_pred = cross_val_predict(regressor_against, x, goals_against_target, cv=4)

    metrics = {
        "target": "quarter_finalist used as team-strength target for match probabilities",
        "best_classifier": best_name,
        "classification": results,
        "scoreline_regression": {
            "goals_for_mae": float(mean_absolute_error(goals_for_target, goals_for_pred)),
            "goals_against_mae": float(mean_absolute_error(goals_against_target, goals_against_pred)),
        },
        "feature_columns": feature_cols,
    }
    artifacts = TrainingArtifacts(best_pipe, regressor_for, regressor_against, metrics)
    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifacts, config.MODEL_PATH)
    config.METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return artifacts


if __name__ == "__main__":
    train_models()
