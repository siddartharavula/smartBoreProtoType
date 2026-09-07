const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();


// ============================================================
// MIDDLEWARE
// ============================================================

app.use(
  cors({
    origin: "http://localhost:5173",
  })
);

app.use(express.json());


// ============================================================
// HOME ROUTE
// ============================================================

app.get("/", (req, res) => {
  res.json({
    message: "Smart Bore backend is running",
  });
});


// ============================================================
// PREDICTION ROUTE
// ============================================================

app.post("/predict", async (req, res) => {
  try {

    const {
      latitude,
      longitude,
    } = req.body;


    // --------------------------------------------------------
    // VALIDATION
    // --------------------------------------------------------

    if (
      latitude === undefined ||
      longitude === undefined
    ) {

      return res.status(400).json({
        message:
          "Latitude and longitude are required",
      });

    }


    console.log(
      "\n========== REQUEST FROM REACT =========="
    );

    console.log(
      "Latitude:",
      latitude
    );

    console.log(
      "Longitude:",
      longitude
    );


    // --------------------------------------------------------
    // CALL FLASK ML API
    // --------------------------------------------------------

    const response = await axios.post(

      "http://127.0.0.1:5001/predict",

      {
        latitude,
        longitude,
      }

    );


    console.log(
      "\n========== RESPONSE FROM ML =========="
    );

    console.log(
      "Success Rate:",
      response.data.successRate
    );

    console.log(
      "Expected Depth:",
      response.data.expectedDepth
    );


    // --------------------------------------------------------
    // SEND RESULT TO REACT
    // --------------------------------------------------------

    res.json({

      successRate:
        response.data.successRate,

      expectedDepth:
        response.data.expectedDepth,

      waterFound:
        response.data.waterFound,

    });


  } catch (error) {

    console.error(
      "\nML API Error:",
      error.message
    );


    res.status(500).json({

      message:
        "Prediction failed",

    });

  }
});


// ============================================================
// START SERVER
// ============================================================

app.listen(
  5000,
  () => {

    console.log(
      "Server running on http://localhost:5000"
    );

  }
);