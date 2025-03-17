import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate, Link } from "react-router-dom";
import { ClerkProvider, SignedIn, SignedOut, SignIn, UserButton } from "@clerk/clerk-react";
import MonitoringPanel from "./MonitoringPanel";
import SettingsPage from "./SettingsPage";
import "./styles.css"; // Import the CSS file
import React from "react";

const clerkKey = "pk_test_am9pbnQtYmFzaWxpc2stMjcuY2xlcmsuYWNjb3VudHMuZGV2JA";

function App() {
    return (
        <ClerkProvider publishableKey={clerkKey}>
            <Router>
                <div className="app-container">
                    <header className="app-header">
                        <h1>Keylogger Monitoring</h1>
                        <SignedIn>
                            <div className="user-controls">
                                <UserButton />
                                <nav className="nav-links">
                                    <Link to="/">Monitoring</Link>
                                    <Link to="/settings">Settings</Link>
                                </nav>
                            </div>
                        </SignedIn>
                    </header>

                    <main className="app-main">
                        <SignedOut>
                            <div className="signin-container">
                                <SignIn />
                            </div>
                        </SignedOut>

                        <SignedIn>
                            <Routes>
                                <Route path="/" element={<MonitoringPanel />} />
                                <Route path="/settings" element={<SettingsPage />} />
                            </Routes>
                        </SignedIn>
                    </main>

                    <footer className="app-footer">
                        <p>&copy; 2025 Keylogger Monitoring. All rights reserved.</p>
                    </footer>
                </div>
            </Router>
        </ClerkProvider>
    );
}

export default App;