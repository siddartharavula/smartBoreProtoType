import pandas as pd
import numpy as np

from pathlib import Path

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# DATA PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "borewell.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)


# ============================================================
# PREPARE DEPTH DATA
# ============================================================

depth_df = df.dropna(
    subset=["water_depth"]
)

X = depth_df[
    ["latitude", "longitude"]
]

y = depth_df[
    "water_depth"
]


# ============================================================
# SPLIT DATA
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)


# ============================================================
# DEPTH MODEL
# ============================================================

model = RandomForestRegressor(
    random_state=42
)


# ============================================================
# HYPERPARAMETER TUNING
# ============================================================

param_grid = {

    "n_estimators": [
        100,
        200,
        300
    ],

    "max_depth": [
        5,
        10,
        15,
        20
    ],

    "min_samples_leaf": [
        1,
        2,
        4
    ]
}


grid_search = GridSearchCV(
    model,
    param_grid,
    cv=5,
    scoring="neg_mean_absolute_error",
    n_jobs=-1
)


grid_search.fit(
    X_train,
    y_train
)


# ============================================================
# BEST MODEL
# ============================================================

best_model = grid_search.best_estimator_


# ============================================================
# DEPTH MODEL METRICS
# ============================================================

y_pred = best_model.predict(
    X_test
)

mae = mean_absolute_error(
    y_test,
    y_pred
)

mse = mean_squared_error(
    y_test,
    y_pred
)

rmse = np.sqrt(mse)

r2 = r2_score(
    y_test,
    y_pred
)


depth_metrics = {

    "mae": mae,

    "mse": mse,

    "rmse": rmse,

    "r2": r2
}


# ============================================================
# DEPTH PREDICTION FUNCTION
# ============================================================

def predict_depth(latitude, longitude):

    new_location = pd.DataFrame(
        [
            [
                latitude,
                longitude
            ]
        ],
        columns=[
            "latitude",
            "longitude"
        ]
    )

    prediction = best_model.predict(
        new_location
    )[0]

    return float(prediction)