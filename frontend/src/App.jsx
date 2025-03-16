import {useState} from "react";
import axios from "axios";
import React from "react";
import "./index.css";

function App() {
  const [loading, setLoading] = useState(false);
  const [monitoring, setMonitoring] = useState(false);

  const handleMonitoring = async (action) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:5000/${action}_monitoring`
      );
      setMonitoring(action === "start");
      console.log(response.data);
    } catch (error) {
      console.error("Error:", error);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-4">Keylogger WebApp</h1>

      <div className="flex gap-4">
        <button
          onClick={() => handleMonitoring("start")}
          disabled={monitoring || loading}
          className={`px-4 py-2 rounded ${
            monitoring
              ? "bg-gray-600 cursor-not-allowed"
              : "bg-green-500 hover:bg-green-600"
          }`}
        >
          {loading && monitoring ? "Starting..." : "Start Monitoring"}
        </button>

        <button
          onClick={() => handleMonitoring("stop")}
          disabled={!monitoring || loading}
          className={`px-4 py-2 rounded ${
            !monitoring
              ? "bg-gray-600 cursor-not-allowed"
              : "bg-red-500 hover:bg-red-600"
          }`}
        >
          {loading && !monitoring ? "Stopping..." : "Stop Monitoring"}
        </button>
      </div>
    </div>
  );
}

export default App;
