const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();

app.use(
  cors({
    origin: [
      "http://localhost:5173",
      "https://smart-bore-proto-type.vercel.app"
    ]
  })
);

app.use(express.json());

app.get("/", (req, res) => {
  res.json({
    message: "Smart Bore backend is running"
  });
});

app.post("/predict", async (req, res) => {
  try {
    const { latitude, longitude } = req.body;

    if (
      latitude === undefined ||
      longitude === undefined
    ) {
      return res.status(400).json({
        message: "Latitude and longitude are required"
      });
    }

    const response = await axios.post(
      `${process.env.ML_API_URL}/predict`,
      {
        latitude,
        longitude
      }
    );

    res.json({
      successRate: response.data.successRate,
      expectedDepth: response.data.expectedDepth,
      waterFound: response.data.waterFound
    });

  } catch (error) {
    console.error("ML API Error:", error.message);

    res.status(500).json({
      message: "Prediction failed"
    });
  }
});

app.listen(
  process.env.PORT || 5000,
  "0.0.0.0",
  () => {
    console.log("Smart Bore backend is running");
  }
);