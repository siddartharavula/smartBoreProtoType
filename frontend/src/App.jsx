import React, { useEffect, useRef, useState } from "react";

const App = () => {
  const vantaRef = useRef(null);

  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [locationLoading, setLocationLoading] = useState(false);
  const [error, setError] = useState("");
  const [predictTrigger, setPredictTrigger] = useState(0);

  const MIN_LATITUDE = 15.87248;
  const MAX_LATITUDE = 19.89171;

  const MIN_LONGITUDE = 77.31305;
  const MAX_LONGITUDE = 80.93706;

  // Vanta background
  useEffect(() => {
    if (!window.VANTA || !window.THREE) {
      console.log("Vanta or Three.js not loaded");
      return;
    }

    const effect = window.VANTA.WAVES({
      el: vantaRef.current,
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200,
      minWidth: 200,
      scale: 1,
      scaleMobile: 1,
      shininess: 63,
      waveHeight: 33,
      waveSpeed: 1.3,
      zoom: 0.65,
    });

    const canvas = vantaRef.current?.querySelector("canvas");

    if (canvas) {
      canvas.style.position = "fixed";
      canvas.style.top = "0";
      canvas.style.left = "0";
      canvas.style.width = "100%";
      canvas.style.height = "100%";
      canvas.style.zIndex = "0";
    }

    return () => {
      effect.destroy();
    };
  }, []);

  // Get user's location
  const handleUseLocation = () => {
    setError("");
    setPrediction(null);

    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.");
      return;
    }

    setLocationLoading(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        if (
          lat < MIN_LATITUDE ||
          lat > MAX_LATITUDE ||
          lon < MIN_LONGITUDE ||
          lon > MAX_LONGITUDE
        ) {
          setError(
            "Your current location is outside the supported area for Smart Bore."
          );
          setLocationLoading(false);
          return;
        }

        setLatitude(lat.toFixed(5));
        setLongitude(lon.toFixed(5));
        setLocationLoading(false);
      },
      (error) => {
        setLocationLoading(false);

        if (error.code === 1) {
          setError("Location permission was denied.");
        } else if (error.code === 2) {
          setError("Unable to determine your location.");
        } else if (error.code === 3) {
          setError("Location request timed out.");
        } else {
          setError("Unable to get your location.");
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  };

  // Call backend
  useEffect(() => {
    if (predictTrigger === 0) return;

    const getPrediction = async () => {
      try {
        setLoading(true);
        setError("");

        const lat = Number(latitude);
        const lng = Number(longitude);

        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/predict`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              lat: lat,
              lng: lng,
            }),
          }
        );

        const text = await response.text();

        console.log("Backend response:", text);

        if (!text) {
          throw new Error("Backend returned an empty response.");
        }

        const data = JSON.parse(text);

        if (!response.ok) {
          throw new Error(
            data.message || data.error || "Prediction failed"
          );
        }

        setPrediction({
          successRate:
            data.successRate !== undefined
              ? Number(data.successRate).toFixed(2)
              : data.water_probability !== undefined
              ? (Number(data.water_probability) * 100).toFixed(2)
              : null,

          expectedDepth:
            data.expectedDepth !== undefined
              ? data.expectedDepth !== null
                ? Number(data.expectedDepth).toFixed(2)
                : null
              : data.depth_estimate !== undefined
              ? data.depth_estimate !== null
                ? Number(data.depth_estimate).toFixed(2)
                : null
              : null,
        });
      } catch (err) {
        console.error(err);
        setError(err.message || "Unable to fetch prediction.");
      } finally {
        setLoading(false);
      }
    };

    getPrediction();
  }, [predictTrigger]);

  // Submit prediction
  const handleSubmit = (e) => {
    e.preventDefault();

    setError("");
    setPrediction(null);

    if (latitude === "" || longitude === "") {
      setError("Please enter both latitude and longitude.");
      return;
    }

    const lat = Number(latitude);
    const lon = Number(longitude);

    if (lat < MIN_LATITUDE || lat > MAX_LATITUDE) {
      setError(
        `Please re-enter latitude between ${MIN_LATITUDE} and ${MAX_LATITUDE}.`
      );
      return;
    }

    if (lon < MIN_LONGITUDE || lon > MAX_LONGITUDE) {
      setError(
        `Please re-enter longitude between ${MIN_LONGITUDE} and ${MAX_LONGITUDE}.`
      );
      return;
    }

    setPredictTrigger((prev) => prev + 1);
  };

  return (
    <div
      ref={vantaRef}
      className="relative min-h-screen w-full overflow-x-hidden bg-gray-950"
    >
      <div className="relative z-10 min-h-screen px-4 py-8 sm:px-8 sm:py-10 lg:px-15">
        {/* Title */}
        <h1 className="mt-4 text-center text-4xl font-extrabold text-white sm:mt-8 sm:text-5xl lg:text-6xl">
          Smart Bore
        </h1>

        {/* Main card */}
        <div className="mx-auto mt-8 w-full max-w-4xl rounded-2xl bg-gray-900/90 p-5 shadow-2xl backdrop-blur-sm sm:mt-10 sm:p-8 lg:p-10">
          {/* Heading */}
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white sm:text-4xl">
              Location Details
            </h2>

            <p className="mt-2 text-sm text-gray-400 sm:text-md">
              Enter the geographical coordinates to continue.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="mt-6 space-y-6">
            {/* Latitude */}
            <div>
              <label className="mb-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xl font-bold text-gray-300 sm:text-2xl">
                <span>Latitude</span>

                <span className="text-xs font-normal text-gray-400 sm:text-sm">
                  {MIN_LATITUDE} to {MAX_LATITUDE}
                </span>
              </label>

              <input
                type="number"
                step="any"
                min={MIN_LATITUDE}
                max={MAX_LATITUDE}
                value={latitude}
                onChange={(e) => {
                  setLatitude(e.target.value);
                  setError("");
                  setPrediction(null);
                }}
                placeholder="e.g. 17.3850"
                className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none transition placeholder:text-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>

            {/* Longitude */}
            <div>
              <label className="mb-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xl font-bold text-gray-300 sm:text-2xl">
                <span>Longitude</span>

                <span className="text-xs font-normal text-gray-400 sm:text-sm">
                  {MIN_LONGITUDE} to {MAX_LONGITUDE}
                </span>
              </label>

              <input
                type="number"
                step="any"
                min={MIN_LONGITUDE}
                max={MAX_LONGITUDE}
                value={longitude}
                onChange={(e) => {
                  setLongitude(e.target.value);
                  setError("");
                  setPrediction(null);
                }}
                placeholder="e.g. 78.4867"
                className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-white outline-none transition placeholder:text-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                required
              />
            </div>

            {/* Location and Predict buttons */}
            <div className="mt-5 flex flex-col gap-3">
              <button
                type="button"
                onClick={handleUseLocation}
                disabled={locationLoading || loading}
                className="w-full rounded-xl border border-blue-500 bg-blue-500/10 px-4 py-2 text-lg font-semibold text-blue-400 transition hover:bg-blue-500/20 disabled:cursor-not-allowed disabled:opacity-50 sm:text-xl"
              >
                {locationLoading ? "Getting Location..." : "Use My Location"}
              </button>

              <button
                type="submit"
                disabled={loading || locationLoading}
                className="w-full rounded-xl bg-blue-600 px-4 py-3 text-lg font-bold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50 sm:text-xl"
              >
                {loading ? "Predicting..." : "Predict"}
              </button>
            </div>
          </form>

          {/* Error */}
          {error && (
            <div className="mt-6 rounded-xl border border-red-800 bg-red-950/90 p-4 text-center text-sm font-medium text-red-400 sm:text-base">
              {error}
            </div>
          )}

          {/* Prediction results */}
          {prediction !== null && (
            <div className="mt-8 flex flex-col gap-6 md:flex-row">
              {/* Success rate */}
              <div className="flex-1 rounded-xl bg-gray-950 p-6 text-center">
                <p className="text-sm text-gray-400 sm:text-base">
                  Success Rate
                </p>

                <p className="mt-2 text-4xl font-bold text-green-400 sm:text-5xl">
                  {prediction.successRate}%
                </p>
              </div>

              {/* Expected depth */}
              <div className="flex-1 rounded-xl bg-gray-950 p-6 text-center">
                <p className="text-sm text-gray-400 sm:text-base">
                  Expected Water Depth
                </p>

                <p className="mt-2 text-3xl font-bold text-blue-400 sm:text-4xl">
                  {prediction.expectedDepth !== null
                    ? `${prediction.expectedDepth} ft`
                    : "Water may be below 1500 ft"}
                </p>
              </div>
            </div>
          )}
        </div>
        {loading && (
          <p className="mx-auto mt-4 max-w-4xl text-center text-sm text-gray-300 sm:text-base">
            The server may take some time to predict. Please wait...
          </p>
        )}
      </div>
    </div>
  );
};

export default App;