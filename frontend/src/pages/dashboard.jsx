import { useState } from "react";
import { startMonitoring, stopMonitoring } from "../api/monitoring";
import React from "react";

const Dashboard = () => {
  const [isMonitoring, setIsMonitoring] = useState(false);

  const handleStart = async () => {
    try {
      await startMonitoring();
      setIsMonitoring(true);
    } catch (error) {
      alert("Failed to start monitoring!", error);
    }
  };

  const handleStop = async () => {
    try {
      await stopMonitoring();
      setIsMonitoring(false);
    } catch (error) {
      alert("Failed to stop monitoring!", error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-6">Keylogger Monitoring</h1>
      <div className="flex gap-4">
        <button
          className={`px-6 py-3 rounded text-white font-semibold ${
            isMonitoring ? "bg-gray-600 cursor-not-allowed" : "bg-green-500 hover:bg-green-700"
          }`}
          onClick={handleStart}
          disabled={isMonitoring}
        >
          Start Monitoring
        </button>
        <button
          className={`px-6 py-3 rounded text-white font-semibold ${
            isMonitoring ? "bg-red-500 hover:bg-red-700" : "bg-gray-600 cursor-not-allowed"
          }`}
          onClick={handleStop}
          disabled={!isMonitoring}
        >
          Stop Monitoring
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
