from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw" / "provided"
CANONICAL_FIXTURE_DIR = RAW_DIR / "archive_3"
TRAIN_CSV = RAW_DIR / "archive_2" / "train.csv"
TEST_CSV = RAW_DIR / "archive_2" / "test.csv"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
MODEL_DIR = ROOT_DIR / "models"
SQLITE_DB = PROCESSED_DIR / "fifa2026_predictions.db"
PREDICTIONS_CSV = PROCESSED_DIR / "fixture_predictions.csv"
MODEL_PATH = MODEL_DIR / "winner_pipeline.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"

FOOTBALL_FEATURE_WEIGHT = 0.85
ASTROLOGY_FEATURE_WEIGHT = 0.10
NUMEROLOGY_FEATURE_WEIGHT = 0.05
