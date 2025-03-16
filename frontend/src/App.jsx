import React from "react";
import { SignInButton, SignOutButton, useAuth, useUser } from "@clerk/clerk-react";
import { useState } from "react";

function App() {
  const { isSignedIn, user } = useUser();
  const { getToken } = useAuth();
  const [isMonitoring, setIsMonitoring] = useState(false);

  async function sendMonitoringRequest(endpoint) {
    try {
      const token = await getToken(); // Get the auth token

      const response = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // Attach token for authentication
        },
      });

      const data = await response.json();
      console.log(data);

      if (response.ok) {
        setIsMonitoring(endpoint === "start_monitoring");
      }
    } catch (error) {
      console.error(`Error in ${endpoint}:`, error);
    }
  }

  return (
    <div>
       <div>
      <h1>Keylogger Web App</h1>

      {!isSignedIn ? (
        <>
          <h2>Please Sign In</h2>
          <SignInButton mode="modal" />
        </>
      ) : (
        <>
          <h2>Welcome, {user?.fullName}!</h2>
          <SignOutButton />
        </>
        )}
      </div>
      {isSignedIn ? (
        <>
          <h1>Welcome, {user?.fullName}</h1>

          <button
            onClick={() => sendMonitoringRequest("start_monitoring")}
            disabled={isMonitoring}
          >
            Start Monitoring
          </button>

          <button
            onClick={() => sendMonitoringRequest("stop_monitoring")}
            disabled={!isMonitoring}
          >
            Stop Monitoring
          </button>
        </>
      ) : (
        <h1>Please log in</h1>
      )}
    </div>

    
  );
}

export default App;
