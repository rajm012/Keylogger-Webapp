import React, { useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000"; // Backend URL

const StartStopButtons = () => {
  const [monitoring, setMonitoring] = useState(false);

  const startMonitoring = async () => {
    try {
      const response = await axios.post(`${API_URL}/start_monitoring`);
      alert(response.data.message);
      setMonitoring(true);
    } catch (error) {
      console.error("Error starting monitoring:", error);
      alert("Failed to start monitoring!");
    }
  };

  const stopMonitoring = async () => {
    try {
      const response = await axios.post(`${API_URL}/stop_monitoring`);
      alert(response.data.message);
      setMonitoring(false);
    } catch (error) {
      console.error("Error stopping monitoring:", error);
      alert("Failed to stop monitoring!");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <button onClick={startMonitoring} disabled={monitoring} style={buttonStyle}>
        Start Monitoring
      </button>
      <button onClick={stopMonitoring} disabled={!monitoring} style={buttonStyle}>
        Stop Monitoring
      </button>
    </div>
  );
};

const buttonStyle = {
  padding: "10px 20px",
  margin: "10px",
  fontSize: "16px",
  cursor: "pointer",
};

export default StartStopButtons;
