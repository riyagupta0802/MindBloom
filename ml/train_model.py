"""
==============================================================================
MINDBLOOM ML — MODEL TRAINING SCRIPT (PHASE 4)
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Technology: Python 3, Scikit-learn, RandomForestClassifier, Joblib
Description: Trains a multiclass Random Forest model to predict adaptive
             game difficulty ('Easy', 'Medium', 'Hard') based on gameplay performance.
==============================================================================
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# File Paths
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Import local preprocessing helpers
try:
    from preprocessing import (
        preprocess_dataframe,
        FEATURE_COLUMNS,
        REVERSE_DIFFICULTY_MAP
    )
except ImportError:
    from ml.preprocessing import (
        preprocess_dataframe,
        FEATURE_COLUMNS,
        REVERSE_DIFFICULTY_MAP
    )

DATASET_PATH = CURRENT_DIR / "dataset.csv"
MODEL_PATH = CURRENT_DIR / "model.pkl"
METADATA_PATH = CURRENT_DIR / "model_metadata.json"


def load_dataset_from_db_or_csv() -> Tuple[pd.DataFrame, str]:
    """
    Attempts to load gameplay records from MySQL database if sufficient records
    exist (>= 50 sessions). Otherwise, safely falls back to the synthetic training
    dataset ml/dataset.csv.
    """
    db_loaded = False
    df = None

    # Check for database environment variables
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "mindbloom_db")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "3306"))

    if db_user and db_password:
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name
            )
            query = """
                SELECT 
                    accuracy,
                    response_time,
                    mistakes,
                    score,
                    hints_used,
                    difficulty AS previous_difficulty,
                    difficulty AS recommended_difficulty
                FROM game_sessions
                LIMIT 500;
            """
            db_df = pd.read_sql(query, conn)
            conn.close()

            # Need at least 50 historical gameplay sessions for reliable training
            if len(db_df) >= 50:
                print(f"[DATA SOURCE] Loaded {len(db_df)} real gameplay records from MySQL database '{db_name}'.")
                return db_df, "mysql_database"
            else:
                print(f"[DATA SOURCE] Database has only {len(db_df)} records (minimum 50 required). Falling back to synthetic dataset.")
        except Exception as e:
            print(f"[DATA SOURCE] Notice: Could not load from MySQL ({e}). Using synthetic dataset.")

    # Fallback to synthetic dataset
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Training dataset not found at {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    print(f"[DATA SOURCE] Loaded {len(df)} records from synthetic dataset: {DATASET_PATH.name}")
    print("[NOTICE] Training data is synthetic/demo data and does NOT represent clinical patient data.")
    return df, "synthetic_demo_dataset"


def train():
    """
    Executes the end-to-end model training, evaluation, and serialization workflow.
    """
    print("\n==================================================")
    print("MINDBLOOM — ADAPTIVE DIFFICULTY MODEL TRAINING")
    print("==================================================")

    # 1. Load Data
    df, dataset_type = load_dataset_from_db_or_csv()

    # 2. Preprocess
    print("\n[STEP 1] Preprocessing features and target...")
    X, y = preprocess_dataframe(df)
    print(f"Features: {FEATURE_COLUMNS}")
    print(f"Feature matrix shape: {X.shape}, Target vector shape: {y.shape}")

    # 3. Train/Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
    print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

    # 4. Train Random Forest Classifier
    print("\n[STEP 2] Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)
    print("Model training completed successfully.")

    # 5. Evaluate Model
    print("\n[STEP 3] Evaluating Model on Test Set...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    print("--------------------------------------------------")
    print(f"Overall Test Accuracy : {acc * 100:.2f}%")
    print(f"Weighted Precision    : {prec * 100:.2f}%")
    print(f"Weighted Recall       : {rec * 100:.2f}%")
    print(f"Weighted F1-Score     : {f1 * 100:.2f}%")
    print("--------------------------------------------------")

    target_names = [REVERSE_DIFFICULTY_MAP[i] for i in sorted(REVERSE_DIFFICULTY_MAP.keys())]
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=target_names, digits=3))

    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix (Rows: True, Columns: Predicted):")
    print(f"Labels order: {target_names}")
    print(cm)

    # Important Medical Disclaimer Note
    print("\n==================================================")
    print("IMPORTANT DISCLAIMER:")
    print("Evaluation is based on synthetic/demo gameplay data")
    print("and does NOT represent clinical performance or diagnosis.")
    print("This model is strictly for game difficulty adaptation.")
    print("==================================================")

    # 6. Save Model to model.pkl
    print(f"\n[STEP 4] Saving model to {MODEL_PATH}...")
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved successfully ({MODEL_PATH.stat().st_size} bytes).")

    # 7. Save Model Metadata
    metadata = {
        "model_type": "RandomForestClassifier",
        "version": "1.0.0",
        "training_date": datetime.now().isoformat(),
        "dataset_type": dataset_type,
        "n_samples": len(df),
        "features": FEATURE_COLUMNS,
        "feature_columns": FEATURE_COLUMNS,
        "classes": target_names,
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 8,
            "min_samples_split": 4,
            "min_samples_leaf": 2,
            "random_state": 42
        },
        "metrics": {
            "accuracy": round(float(acc), 4),
            "test_accuracy": round(float(acc), 4),
            "weighted_precision": round(float(prec), 4),
            "weighted_recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "weighted_f1": round(float(f1), 4)
        },
        "disclaimer": "Academic prototype for cognitive gaming difficulty adaptation (SIH 2026). Strictly not a medical diagnostic or clinical assessment tool."
    }

    import json
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Model metadata saved to {METADATA_PATH}.")
    print("Model training and evaluation completed successfully.")

    return model, metadata


if __name__ == "__main__":
    from typing import Tuple
    train()
