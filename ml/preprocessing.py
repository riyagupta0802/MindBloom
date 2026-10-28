"""
==============================================================================
MINDBLOOM ML — PREPROCESSING MODULE (PHASE 4)
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Technology: Python 3, Pandas, NumPy
Description: Centralized feature validation, encoding, and transformation
             for both training and real-time difficulty inference.
==============================================================================
"""

from typing import Dict, Any, Tuple, Union
import numpy as np
import pandas as pd

# Standard categorical mappings for difficulty tiers
DIFFICULTY_MAP = {
    "easy": 0,
    "medium": 1,
    "hard": 2
}

REVERSE_DIFFICULTY_MAP = {
    0: "Easy",
    1: "Medium",
    2: "Hard"
}

# The ordered feature columns expected by the trained Random Forest model
FEATURE_COLUMNS = [
    "accuracy",
    "response_time",
    "mistakes",
    "score",
    "hints_used",
    "prev_diff_encoded"
]


def normalize_difficulty_str(diff: Any) -> str:
    """
    Normalizes difficulty strings (e.g., 'easy', 'Easy', 'EASY') into title case.
    """
    if not isinstance(diff, str):
        raise ValueError(f"Difficulty must be a string, got {type(diff).__name__}")
    clean = diff.strip().lower()
    if clean not in DIFFICULTY_MAP:
        raise ValueError(f"Invalid difficulty '{diff}'. Must be one of: Easy, Medium, Hard.")
    return clean.capitalize()


def encode_difficulty(diff: Any) -> int:
    """
    Encodes a difficulty string ('Easy', 'Medium', 'Hard') to an integer (0, 1, 2).
    """
    if not isinstance(diff, str):
        raise ValueError(f"Expected difficulty string, got {type(diff).__name__}")
    clean = diff.strip().lower()
    if clean not in DIFFICULTY_MAP:
        raise ValueError(f"Unknown difficulty tier '{diff}'. Allowed: 'Easy', 'Medium', 'Hard'.")
    return DIFFICULTY_MAP[clean]


def decode_difficulty(index: int) -> str:
    """
    Decodes an integer target (0, 1, 2) back to a human-readable difficulty label.
    """
    if index not in REVERSE_DIFFICULTY_MAP:
        raise ValueError(f"Unknown class index {index}. Expected 0, 1, or 2.")
    return REVERSE_DIFFICULTY_MAP[index]


def validate_gameplay_features(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates gameplay performance metrics to reject corrupted, negative,
    or physically impossible values.
    """
    required = ["accuracy", "response_time", "mistakes", "score", "hints_used", "previous_difficulty"]
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required feature: '{field}'")

    try:
        accuracy = float(data["accuracy"])
    except (ValueError, TypeError):
        raise ValueError(f"Accuracy must be a number, got {data.get('accuracy')}")

    if not (0.0 <= accuracy <= 100.0):
        raise ValueError(f"Accuracy must be between 0.0 and 100.0 (got {accuracy})")

    try:
        response_time = int(data["response_time"])
        mistakes = int(data["mistakes"])
        score = int(data["score"])
        hints_used = int(data.get("hints_used", 0))
    except (ValueError, TypeError) as err:
        raise ValueError(f"Performance metrics must be valid integers: {err}")

    if response_time < 0:
        raise ValueError(f"Response time cannot be negative (got {response_time})")
    if mistakes < 0:
        raise ValueError(f"Mistakes cannot be negative (got {mistakes})")
    if score < 0:
        raise ValueError(f"Score cannot be negative (got {score})")
    if hints_used < 0:
        raise ValueError(f"Hints used cannot be negative (got {hints_used})")

    norm_diff = normalize_difficulty_str(data["previous_difficulty"])

    return {
        "accuracy": accuracy,
        "response_time": response_time,
        "mistakes": mistakes,
        "score": score,
        "hints_used": hints_used,
        "previous_difficulty": norm_diff
    }


def prepare_feature_vector(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Validates and transforms a single gameplay dictionary into a 1-row pandas DataFrame
    with feature names matching the trained Random Forest model.
    """
    validated = validate_gameplay_features(data)
    diff_encoded = encode_difficulty(validated["previous_difficulty"])

    feature_values = {
        "accuracy": [validated["accuracy"]],
        "response_time": [validated["response_time"]],
        "mistakes": [validated["mistakes"]],
        "score": [validated["score"]],
        "hints_used": [validated["hints_used"]],
        "prev_diff_encoded": [diff_encoded]
    }

    return pd.DataFrame(feature_values, columns=FEATURE_COLUMNS, dtype=np.float64)


def preprocess_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Preprocesses a pandas DataFrame for model training.
    Encodes 'previous_difficulty' and target 'recommended_difficulty'.
    Returns (X, y).
    """
    df = df.copy()

    # Verify required feature columns
    expected_cols = [
        "accuracy", "response_time", "mistakes", "score",
        "hints_used", "previous_difficulty"
    ]
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Dataset missing required column: '{col}'")

    # Support both 'recommended_difficulty' and 'next_difficulty' column names
    if "recommended_difficulty" not in df.columns and "next_difficulty" in df.columns:
        df["recommended_difficulty"] = df["next_difficulty"]
    elif "recommended_difficulty" not in df.columns:
        raise ValueError("Dataset missing required target column: 'recommended_difficulty'")

    # Encode previous difficulty
    df["prev_diff_encoded"] = df["previous_difficulty"].apply(encode_difficulty)

    # Encode target
    y = df["recommended_difficulty"].apply(encode_difficulty)

    # Select features
    X = df[FEATURE_COLUMNS].astype(np.float64)

    return X, y
