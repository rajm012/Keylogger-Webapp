import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:5000"; // Flask backend URL

export const startMonitoring = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/start_monitoring`);
    return response.data;
  } catch (error) {
    console.error("Error starting monitoring:", error);
    throw error;
  }
};

export const stopMonitoring = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/stop_monitoring`);
    return response.data;
  } catch (error) {
    console.error("Error stopping monitoring:", error);
    throw error;
  }
};
