
# **Parental Monitoring System**

## **Overview**

This project is a **Parental Monitoring System** designed to help parents monitor their children's computer activity in a safe and responsible manner. It allows for **keystroke logging**, **screenshot capture**, and **email reporting**, ensuring that parents can keep an eye on their child's online behavior.  

The system is built using **Python** with **Flask** for the backend, **React** for the frontend, and **Clerk** for authentication. It also integrates with a database to store logs and screenshots securely.

🚨 **Important**: This software is intended for ethical use **only**. The user must have explicit consent before monitoring any system they do not own. Unauthorized use of this tool may violate privacy laws.  

---

## **Features**

✅ **Keystroke Logging**  
- Logs typed keystrokes to help parents understand their child's online interactions.  

✅ **Screenshot Capture**  
- Takes periodic screenshots to provide a visual history of activity.  

✅ **Email Reports**  
- Sends email reports at regular intervals with keystroke logs and screenshots.  

✅ **Secure Authentication**  
- Uses **Clerk** for user authentication, ensuring that only authorized parents can access the logs.  

✅ **Database Integration**  
- Stores logs and screenshots securely using **NeonDB** (or any other SQLAlchemy-supported database).  

✅ **RESTful API**  
- Allows for seamless integration with a frontend or mobile application.  

✅ **Download Logs**  
- Parents can download logs and screenshots in a ZIP file for offline review.  

---

## **Intended Use Cases**  

✔ **Parental Monitoring** – Keep an eye on children's online activities to protect them from cyber threats.  
✔ **Self-Monitoring** – Track your own activity for productivity analysis.  
❌ **Unethical Surveillance** – Any use of this tool to monitor another person **without consent** is strictly prohibited.  

---

## **Prerequisites**

Before running the application, ensure you have the following installed:  

1. **Python 3.8+**  
2. **Pip** (Python package manager)  
3. **Clerk Account** (for authentication)  
4. **SMTP Email Account** (for email reporting)  
5. **Database** (NeonDB or any SQLAlchemy-supported database)  

---

## **Installation & Setup**

1️⃣ **Clone the Repository**  
```bash
git clone https://github.com/rajm012/keylogger-webapp.git
cd keylogger-webapp
```

2️⃣ **Install Dependencies**  
```bash
pip install -r requirements.txt
```

3️⃣ **Set Up Environment Variables**  
Create a `.env` file in the root directory and add the following variables:  
```env
CLERK_JWT_PUBLIC_KEY=your_clerk_jwt_public_key
SQLALCHEMY_DATABASE_URI=your_database_uri
```

4️⃣ **Initialize the Database**  
```bash
python -c "from app import db; db.create_all()"
```

5️⃣ **Run the Application**  
```bash
python app.py
```

---

## **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/start_monitoring` | `POST` | Starts keystroke logging and screenshot capture. |
| `/stop_monitoring` | `POST` | Stops monitoring. |
| `/get_logs` | `GET` | Fetches all keystroke logs and screenshots for the authenticated user. |
| `/download_logs` | `GET` | Downloads logs as a ZIP file. |
| `/get_settings` | `GET` | Retrieves current configuration settings. |
| `/update_settings` | `POST` | Updates email and logging intervals. |
| `/get_monitoring_status` | `GET` | Checks if monitoring is currently active. |

---

## **Frontend Integration**

1️⃣ **Install Dependencies**  
```bash
cd frontend
npm install
```

2️⃣ **Run the Frontend**  
```bash
npm start
```

3️⃣ **Access the Web Application**  
Go to `http://localhost:3000` in your browser.

---

## **Configuration**

The system uses a `config.json` file for settings, which can be updated via API.  
Example default configuration:  

```json
{
  "email_interval": 600,
  "screenshot_interval": 30,
  "keylog_interval": 5,
  "sender_mail": "example@example.com",
  "receiver_mail": "parent@example.com"
}
```

---

## **Security & Privacy Considerations**  

🔒 **Authentication:** Only authorized users can access logs.  
🔐 **Data Encryption:** Sensitive information should be encrypted before storage.  
⚖️ **Legal Compliance:** Ensure monitoring is done with appropriate **consent**.  

---

## **License**  

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.  

---

## **Contributing**  

Contributions are welcome! Feel free to open an issue or submit a pull request.  

---

## **Contact**  

📩 **Email**: rajmahimaurya@gmail.com  
🌐 **GitHub**: [rajm012](https://github.com/rajm012)  

---

🚀 **Monitor Responsibly!** 🚀
