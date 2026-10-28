# MindBloom Machine Learning — Adaptive Difficulty System (Phase 4)

**Project:** MindBloom — AI-Powered Cognitive & Memory Assistance Platform  
**Target:** SIH 2026 Problem Statement SIH26003  
**Audience:** Third-Year Computer Science & Engineering (CSE) Students

---

## 1. Why Machine Learning is Used

Elderly individuals experiencing mild cognitive impairment or age-related memory slips have widely different cognitive paces. A fixed difficulty system that forces every user through the same rigid progression can easily cause:
- **Frustration & anxiety** if games become too hard too quickly.
- **Boredom & lack of stimulation** if games remain too simple.

By applying Machine Learning to analyze previous gameplay performance (accuracy, response speed, mistakes, and hints), MindBloom dynamically suggests the most comfortable difficulty tier (**Easy**, **Medium**, or **Hard**) for the user's next session.

> [!IMPORTANT]
> **Strict Non-Medical Limitation:**  
> This Machine Learning model is strictly an **adaptive game-difficulty predictor**.  
> **It does NOT diagnose, treat, prevent, or cure dementia, Alzheimer's disease, or any medical or neurological condition.** It is strictly an assistive algorithm designed to keep gameplay engaging and stress-free.

---

## 2. Why Random Forest Classifier?

We selected **Random Forest** (`sklearn.ensemble.RandomForestClassifier`) because:
1. **Explainable & Reliable:** Random Forests combine multiple decision trees to form robust voting boundaries, making decisions easy to explain during academic evaluations and hackathon presentations.
2. **Robust on Tabular Data:** It outperforms deep learning on small to medium structured tabular datasets without requiring heavy GPU hardware.
3. **Resistant to Overfitting:** Bootstrap aggregation (bagging) and random feature subspace selection prevent the model from memorizing training data.
4. **Predictive Probabilities:** Supports `predict_proba()`, allowing the system to inspect confidence levels across all difficulty tiers.

---

## 3. Input Features (Gameplay Metrics)

The model relies exclusively on 6 non-invasive performance metrics that the frontend game and database naturally collect:

| Feature Name | Type | Description |
|---|---|---|
| `accuracy` | Float (0.0 to 100.0) | Percentage of correct matching attempts over total attempts |
| `response_time` | Integer ($\ge 0$) | Total elapsed seconds taken to complete the game board |
| `mistakes` | Integer ($\ge 0$) | Number of non-matching card pairs flipped |
| `score` | Integer ($\ge 0$) | Cumulative score calculated with bonus and mistake penalties |
| `hints_used` | Integer ($\ge 0$) | Count of assist hints requested during the round |
| `previous_difficulty` | String ('Easy', 'Medium', 'Hard') | Difficulty level of the session just completed |

---

## 4. Target Variable

The target variable is **`recommended_difficulty`** with three categorical classes:
- **`Easy`** (Class 0): 4 pairs = 8 cards (calmer pace, minimal memory load)
- **`Medium`** (Class 1): 6 pairs = 12 cards (balanced cognitive stimulation)
- **`Hard`** (Class 2): 8 pairs = 16 cards (higher challenge for sharp focus)

---

## 5. Dataset & Ethical Data Sourcing

- **Synthetic Training Dataset (`ml/dataset.csv`):** Contains 600 varied records generated with realistic statistical distributions simulating different player sessions (fast/accurate, steady/moderate, struggling/frequent mistakes).
- **Ethical Integrity:** No real dementia patient clinical data was used or simulated as authentic clinical data. The dataset is explicitly designated as **demo/synthetic**.

---

## 6. Real MySQL Database Transition

The training pipeline in `train_model.py` is designed with an automatic data-loading fallback:
1. When launched, it checks the MySQL `game_sessions` table via environment variables.
2. If **$\ge 50$ real gameplay sessions** have been recorded in the database, it trains directly on accumulated gameplay data.
3. If fewer than 50 records exist, it safely trains on `ml/dataset.csv`.

---

## 7. Model Preprocessing (`ml/preprocessing.py`)

To ensure complete consistency between training and live inference, all transformations are centralized in `preprocessing.py`:
- Numerical range validation (rejects negative scores, times, or accuracy $> 100$).
- Categorical encoding: `{'Easy': 0, 'Medium': 1, 'Hard': 2}`.
- Converts inputs into a structured 1-row DataFrame preserving feature names.

---

## 8. How to Train the Model

From the root directory:

```bash
python ml/train_model.py
```

**Training Output:**
- Stratified 80/20 train/test split (480 training rows, 120 test rows).
- Evaluates Test Accuracy, Weighted Precision, Recall, and F1-Score.
- Outputs detailed classification report and confusion matrix.
- Serializes the trained model to **`ml/model.pkl`**.
- Writes metadata and evaluation scores to **`ml/model_metadata.json`**.

---

## 9. How to Test Predictions via CLI

Run `predict.py` directly to see sample inference:

```bash
python ml/predict.py
```

Example input:
```json
{
  "accuracy": 95.0,
  "response_time": 26,
  "mistakes": 0,
  "score": 600,
  "hints_used": 0,
  "previous_difficulty": "Medium"
}
```

Example output:
```
Recommended Difficulty: Hard
Model Prediction Probabilities: {'Easy': 0.0, 'Medium': 0.0021, 'Hard': 0.9979}
Confidence: 99.8%
```

---

## 10. FastAPI Backend Integration

The backend exposes an inference route at **`POST /api/ml/predict`**.

### Request:
```bash
curl -X POST http://127.0.0.1:8000/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "accuracy": 92.5,
    "response_time": 30,
    "mistakes": 1,
    "score": 580,
    "hints_used": 0,
    "previous_difficulty": "Medium"
  }'
```

### Response:
```json
{
  "recommended_difficulty": "Hard",
  "probabilities": {
    "Easy": 0.001,
    "Medium": 0.045,
    "Hard": 0.954
  },
  "confidence": 0.954,
  "model_version": "1.0.0",
  "disclaimer": "Academic prototype for cognitive gaming difficulty adaptation only. Not a medical diagnosis or clinical assessment."
}
```

