from flask import Flask, request, jsonify

import joblib
import pandas as pd

from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ML_MODEL_DIR = BASE_DIR.parent / "ml-model"

MODEL_DIR = ML_MODEL_DIR / "models"


# ============================================================
# LOAD TRAINED MODELS
# ============================================================

water_model = joblib.load(
    MODEL_DIR / "water_model.joblib"
)

depth_model = joblib.load(
    MODEL_DIR / "depth_model.joblib"
)


print("Water model loaded successfully.")
print("Depth model loaded successfully.")


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# PREDICTION
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required"
            }), 400


        if (
            "latitude" not in data
            or
            "longitude" not in data
        ):
            return jsonify({
                "message":
                "Latitude and longitude are required"
            }), 400


        latitude = float(data["latitude"])
        longitude = float(data["longitude"])


        # ====================================================
        # CREATE INPUT
        # ====================================================

        new_location = pd.DataFrame(
            [[latitude, longitude]],
            columns=[
                "latitude",
                "longitude"
            ]
        )


        # ====================================================
        # WATER PREDICTION
        # ====================================================

        water_found = water_model.predict(
            new_location
        )[0]


        # ====================================================
        # WATER PROBABILITY
        # ====================================================

        probabilities = water_model.predict_proba(
            new_location
        )[0]

        classes = water_model.classes_


        true_index = list(
            classes
        ).index(True)


        water_probability = probabilities[
            true_index
        ]


        success_rate = round(
            float(water_probability * 100),
            2
        )


        # ====================================================
        # DEPTH PREDICTION
        # ====================================================

        expected_depth = None


        if water_found:

            predicted_depth = depth_model.predict(
                new_location
            )[0]


            expected_depth = round(
                float(predicted_depth),
                2
            )


        # ====================================================
        # LOG
        # ====================================================

        print("\n========== PREDICTION ==========")

        print(
            "Latitude:",
            latitude
        )

        print(
            "Longitude:",
            longitude
        )

        print(
            "Water Found:",
            water_found
        )

        print(
            "Success Rate:",
            success_rate,
            "%"
        )

        print(
            "Expected Depth:",
            expected_depth,
            "ft"
        )


        # ====================================================
        # RESPONSE
        # ====================================================

        return jsonify({

            "successRate":
                success_rate,

            "expectedDepth":
                expected_depth,

            "waterFound":
                bool(water_found)

        })


    except Exception as error:

        print(
            "\nPrediction Error:",
            str(error)
        )

        return jsonify({

            "message":
                "Prediction failed",

            "error":
                str(error)

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5001))
    )