from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

depth_model = joblib.load(
    BASE_DIR.parent / "ml-model" / "models" / "depth_model.joblib"
)

water_model = joblib.load(
    BASE_DIR.parent / "ml-model" / "models" / "water_model.joblib"
)

app = Flask(__name__)

CORS(
    app,
    origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://smartboreprototype.vercel.app"
    ]
)


@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json()

        lat = data.get("lat")
        lng = data.get("lng")

        water_depth = depth_model.predict([[lat, lng]])[0]

        water_probability = water_model.predict_proba(
            [[lat, lng]]
        )[0][1]

        return jsonify({
            "depth_estimate": round(float(water_depth), 2),
            "water_probability": round(float(water_probability), 2)
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500