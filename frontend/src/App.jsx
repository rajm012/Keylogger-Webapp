import { useState, useEffect } from "react";
import { ClerkProvider, SignedIn, SignedOut, SignIn, UserButton } from "@clerk/clerk-react";
import "./styles.css";
import React from "react";

const clerkKey = "pk_test_am9pbnQtYmFzaWxpc2stMjcuY2xlcmsuYWNjb3VudHMuZGV2JA";

function App() {
    return (
        <ClerkProvider publishableKey={clerkKey}>
            <MainApp />
        </ClerkProvider>
    );
}

function MainApp() {
    return (
        <div className="container">
            <h1>Keylogger Monitoring</h1>

            <SignedOut>
                <SignIn />
            </SignedOut>

            <SignedIn>
                <UserButton />
                <MonitoringPanel />
            </SignedIn>
        </div>
    );
}

function MonitoringPanel() {
    const [isMonitoring, setIsMonitoring] = useState(false);
    const [keystrokes, setKeystrokes] = useState([]);
    const [screenshots, setScreenshots] = useState([]);

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

    return (
        <>
            <button className="start-btn" onClick={startMonitoring}>Start Monitoring</button>
            <button className="stop-btn" onClick={stopMonitoring}>Stop Monitoring</button>
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
                        <img key={index} src={`http://127.0.0.1:5000/screenshots/${img}`} alt="screenshot" />
                    ))
                ) : (
                    <p>No screenshots captured yet.</p>
                )}
            </div>
        </>
    );
}

export default App;