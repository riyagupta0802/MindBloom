"""
==============================================================================
MINDBLOOM ML — DIFFICULTY PREDICTION MODULE (PHASE 4)
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Technology: Python 3, Scikit-learn, Joblib
Description: Loads the trained Random Forest model and performs real-time
             difficulty inference with class probabilities.
==============================================================================
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np

# Ensure ml directory is in sys.path regardless of caller's cwd
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from preprocessing import (
        prepare_feature_vector,
        decode_difficulty,
        REVERSE_DIFFICULTY_MAP
    )
except ImportError:
    from ml.preprocessing import (
        prepare_feature_vector,
        decode_difficulty,
        REVERSE_DIFFICULTY_MAP
    )

MODEL_PATH = CURRENT_DIR / "model.pkl"

# Global cached model instance to avoid repeated disk reads
_cached_model = None


def load_model(force_reload: bool = False):
    """
    Loads and caches the trained Random Forest model from model.pkl.
    Raises FileNotFoundError if model.pkl does not exist.
    """
    global _cached_model
    if _cached_model is None or force_reload:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found at '{MODEL_PATH}'. "
                f"Please run 'python ml/train_model.py' to generate model.pkl first."
            )
        _cached_model = joblib.load(MODEL_PATH)
    return _cached_model


def predict_difficulty(performance_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts the recommended game difficulty tier for a user's next session
    based on their cognitive game performance metrics.

    Parameters:
        performance_data (dict):
            - accuracy (float): 0.0 to 100.0
            - response_time (int): Seconds taken to finish game
            - mistakes (int): Number of mismatched attempts
            - score (int): Game score
            - hints_used (int): Number of hints requested
            - previous_difficulty (str): 'Easy', 'Medium', or 'Hard'

    Returns:
        dict:
            - recommended_difficulty (str): 'Easy', 'Medium', or 'Hard'
            - probabilities (dict): { 'Easy': float, 'Medium': float, 'Hard': float }
            - confidence (float): The probability score of the winning prediction
    """
    model = load_model()

    # 1. Validate and convert inputs to 2D numpy feature array
    X = prepare_feature_vector(performance_data)

    # 2. Perform multiclass classification prediction
    predicted_class_index = int(model.predict(X)[0])
    recommended_difficulty = decode_difficulty(predicted_class_index)

    # 3. Calculate prediction probabilities
    probabilities = {}
    confidence = 0.0

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[0]
        # Map class index to class names
        for idx, class_label in sorted(REVERSE_DIFFICULTY_MAP.items()):
            prob_val = round(float(probs[idx]), 4) if idx < len(probs) else 0.0
            probabilities[class_label] = prob_val

        confidence = probabilities.get(recommended_difficulty, 0.0)

    return {
        "recommended_difficulty": recommended_difficulty,
        "probabilities": probabilities,
        "confidence": confidence
    }


def demo_test():
    """
    Runs quick demonstration predictions for strong, moderate, and struggling performance.
    """
    print("\n==================================================")
    print("MINDBLOOM — ML DIFFICULTY PREDICTION DEMO")
    print("==================================================")

    test_cases = [
        {
            "name": "Case 1: Strong Performance (Fast, High Accuracy, 0 Mistakes)",
            "data": {
                "accuracy": 95.0,
                "response_time": 26,
                "mistakes": 0,
                "score": 600,
                "hints_used": 0,
                "previous_difficulty": "Medium"
            }
        },
        {
            "name": "Case 2: Steady/Moderate Performance (Average Time & Accuracy)",
            "data": {
                "accuracy": 75.0,
                "response_time": 52,
                "mistakes": 2,
                "score": 450,
                "hints_used": 1,
                "previous_difficulty": "Medium"
            }
        },
        {
            "name": "Case 3: Struggling Performance (Slow, Low Accuracy, Many Mistakes)",
            "data": {
                "accuracy": 45.0,
                "response_time": 95,
                "mistakes": 6,
                "score": 180,
                "hints_used": 3,
                "previous_difficulty": "Medium"
            }
        }
    ]

    for tc in test_cases:
        print(f"\n--- {tc['name']} ---")
        print("Input Performance:", tc["data"])
        result = predict_difficulty(tc["data"])
        print(f"-> Recommended Difficulty: {result['recommended_difficulty']}")
        print(f"-> Model Prediction Probabilities: {result['probabilities']}")
        print(f"-> Confidence: {result['confidence'] * 100:.1f}%")

    print("\n[NOTE] Prediction probabilities reflect statistical model confidence")
    print("for game difficulty adaptation only. Not a medical assessment.")


if __name__ == "__main__":
    demo_test()

