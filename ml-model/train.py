import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "borewell.csv"

MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print("Dataset loaded.")
print("Rows:", len(df))


# ============================================================
# CREATE WATER TARGET
# ============================================================

df["water_found"] = df["water_depth"].notna()


# ============================================================
# COMMON FEATURES
# ============================================================

features = [
    "latitude",
    "longitude"
]


# ============================================================
# WATER CLASSIFICATION MODEL
# ============================================================

print("\n========================================")
print("TRAINING WATER MODEL")
print("========================================")


water_df = df.copy()

X_water = water_df[features]

y_water = water_df["water_found"]


X_train, X_test, y_train, y_test = train_test_split(
    X_water,
    y_water,
    test_size=0.3,
    random_state=42,
    stratify=y_water
)


water_model = RandomForestClassifier(
    random_state=42,
    class_weight="balanced"
)


water_param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [5, 10, 15, 20],
    "min_samples_leaf": [1, 2, 4]
}


water_grid = GridSearchCV(
    water_model,
    water_param_grid,
    cv=5,
    scoring="f1",
    n_jobs=-1
)


print("Running GridSearchCV for water model...")

water_grid.fit(
    X_train,
    y_train
)


best_water_model = water_grid.best_estimator_


# ============================================================
# WATER MODEL EVALUATION
# ============================================================

water_predictions = best_water_model.predict(
    X_test
)


print("\nWater Model Results:")

print(
    "Accuracy :",
    round(
        accuracy_score(
            y_test,
            water_predictions
        ),
        4
    )
)

print(
    "Precision:",
    round(
        precision_score(
            y_test,
            water_predictions
        ),
        4
    )
)

print(
    "Recall   :",
    round(
        recall_score(
            y_test,
            water_predictions
        ),
        4
    )
)

print(
    "F1 Score :",
    round(
        f1_score(
            y_test,
            water_predictions
        ),
        4
    )
)


# ============================================================
# SAVE WATER MODEL
# ============================================================

water_model_path = (
    MODEL_DIR / "water_model.joblib"
)

joblib.dump(
    best_water_model,
    water_model_path
)

print(
    "\nWater model saved to:",
    water_model_path
)


# ============================================================
# DEPTH REGRESSION MODEL
# ============================================================

print("\n========================================")
print("TRAINING DEPTH MODEL")
print("========================================")


depth_df = df.dropna(
    subset=["water_depth"]
)


X_depth = depth_df[features]

y_depth = depth_df["water_depth"]


X_train, X_test, y_train, y_test = train_test_split(
    X_depth,
    y_depth,
    test_size=0.3,
    random_state=42
)


depth_model = RandomForestRegressor(
    random_state=42
)


depth_param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [5, 10, 15, 20],
    "min_samples_leaf": [1, 2, 4]
}


depth_grid = GridSearchCV(
    depth_model,
    depth_param_grid,
    cv=5,
    scoring="neg_mean_absolute_error",
    n_jobs=-1
)


print("Running GridSearchCV for depth model...")

depth_grid.fit(
    X_train,
    y_train
)


best_depth_model = depth_grid.best_estimator_


# ============================================================
# DEPTH MODEL EVALUATION
# ============================================================

depth_predictions = best_depth_model.predict(
    X_test
)


mae = mean_absolute_error(
    y_test,
    depth_predictions
)

mse = mean_squared_error(
    y_test,
    depth_predictions
)

rmse = np.sqrt(mse)

r2 = r2_score(
    y_test,
    depth_predictions
)


print("\nDepth Model Results:")

print(
    "MAE :",
    round(mae, 2),
    "ft"
)

print(
    "MSE :",
    round(mse, 2)
)

print(
    "RMSE:",
    round(rmse, 2),
    "ft"
)

print(
    "R²  :",
    round(r2, 4)
)


# ============================================================
# SAVE DEPTH MODEL
# ============================================================

depth_model_path = (
    MODEL_DIR / "depth_model.joblib"
)

joblib.dump(
    best_depth_model,
    depth_model_path
)

print(
    "\nDepth model saved to:",
    depth_model_path
)


# ============================================================
# COMPLETE
# ============================================================

print("\n========================================")
print("TRAINING COMPLETE")
print("========================================")

print("\nModels created:")

print(
    "1.",
    water_model_path
)

print(
    "2.",
    depth_model_path
)