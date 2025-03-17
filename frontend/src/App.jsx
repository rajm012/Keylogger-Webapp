import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate, Link } from "react-router-dom";
import { ClerkProvider, SignedIn, SignedOut, SignIn, UserButton } from "@clerk/clerk-react";
import MonitoringPanel from "./MonitoringPanel";
import SettingsPage from "./SettingsPage";
import "./styles.css";
import React from "react";

const clerkKey = "pk_test_am9pbnQtYmFzaWxpc2stMjcuY2xlcmsuYWNjb3VudHMuZGV2JA";

function App() {
    return (
        <ClerkProvider publishableKey={clerkKey}>
            <Router>
                <div className="container">
                    <h1>Keylogger Monitoring</h1>
                    
                    <SignedOut>
                        <SignIn />
                    </SignedOut>

                    <SignedIn>
                        <UserButton />
                        <nav>
                            <Link to="/">Dashboard</Link>
                            <Link to="/settings">Settings</Link>
                        </nav>
                        <Routes>
                            <Route path="/" element={<MonitoringPanel />} />
                            <Route path="/settings" element={<SettingsPage />} />
                        </Routes>
                    </SignedIn>
                </div>
            </Router>
        </ClerkProvider>
    );
}

export default App;
