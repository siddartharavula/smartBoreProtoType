import pandas as pd

from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    GridSearchCV
)

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from depthModel import (
    predict_depth,
    depth_metrics
)


# ============================================================
# DATA PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "borewell.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    DATA_PATH
)


# ============================================================
# WATER TARGET
# ============================================================

# True  -> 300-ft continuous water zone exists
# False -> no suitable 300-ft continuous water zone

df["water_found"] = (
    df["water_depth"].notna()
)


# ============================================================
# FEATURES AND TARGET
# ============================================================

X = df[
    [
        "latitude",
        "longitude"
    ]
]

y = df[
    "water_found"
]


# ============================================================
# SPLIT DATA
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.3,

    random_state=42,

    stratify=y
)


# ============================================================
# WATER MODEL
# ============================================================

model = RandomForestClassifier(

    random_state=42,

    class_weight="balanced"
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

    scoring="f1",

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
# WATER MODEL RESULTS
# ============================================================

y_pred = best_model.predict(
    X_test
)


print("\n========== WATER MODEL ==========")

print(
    "Predicts: 300-ft continuous water zone"
)


print("\nConfusion Matrix:")

print(
    pd.DataFrame(
        confusion_matrix(
            y_test,
            y_pred
        ),

        index=[
            "Actual False",
            "Actual True"
        ],

        columns=[
            "Predicted False",
            "Predicted True"
        ]
    )
)


print(
    "Accuracy :",
    round(
        accuracy_score(
            y_test,
            y_pred
        ),
        4
    )
)


print(
    "Precision:",
    round(
        precision_score(
            y_test,
            y_pred
        ),
        4
    )
)


print(
    "Recall   :",
    round(
        recall_score(
            y_test,
            y_pred
        ),
        4
    )
)


print(
    "F1 Score :",
    round(
        f1_score(
            y_test,
            y_pred
        ),
        4
    )
)


# ============================================================
# DEPTH MODEL RESULTS
# ============================================================

print("\n========== DEPTH MODEL ==========")

print(
    "Predicts: Starting depth of 300-ft water zone"
)


print(
    "MAE :",
    round(
        depth_metrics["mae"],
        2
    ),
    "ft"
)


print(
    "MSE :",
    round(
        depth_metrics["mse"],
        2
    )
)


print(
    "RMSE:",
    round(
        depth_metrics["rmse"],
        2
    ),
    "ft"
)


print(
    "R²  :",
    round(
        depth_metrics["r2"],
        4
    )
)


# ============================================================
# COMMAND LINE PREDICTION
# ============================================================

if __name__ == "__main__":

    print("\n========== PREDICTION ==========")

    latitude = float(
        input("Enter Latitude: ")
    )

    longitude = float(
        input("Enter Longitude: ")
    )


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


    # ========================================================
    # WATER PREDICTION
    # ========================================================

    water_found = best_model.predict(
        new_location
    )[0]


    water_probability = best_model.predict_proba(
        new_location
    )[0][1]


    print(
        "\nWater Found:",
        water_found
    )


    print(
        "Water Probability:",
        round(
            water_probability * 100,
            2
        ),
        "%"
    )


    # ========================================================
    # DEPTH PREDICTION
    # ========================================================

    if water_found:

        predicted_depth = predict_depth(

            latitude,

            longitude
        )


        print(
            "Estimated Water Depth:",
            round(
                predicted_depth,
                2
            ),
            "ft"
        )

    else:

        print(
            "No suitable 300-ft continuous water zone found."
        )