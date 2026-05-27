
# 🔐 Ethical Security AI Agent

## 📌 Project Description

This project is an AI-powered cybersecurity monitoring system developed as part of the BCA Final Year Project.

The Ethical Security AI Agent detects suspicious employee activities and insider threats using Machine Learning, behavioral analysis, and Explainable AI techniques. The system analyzes employee behavior patterns and generates risk scores, AI explanations, and alert notifications for potential security threats.

---

# 💻 Technologies Used

- Python
- Streamlit
- FastAPI
- MySQL
- Scikit-learn
- SHAP
- JWT Authentication
- Pandas
- Matplotlib
- XAMPP / MySQL Server

---

# 🚀 Features

- User Registration & Login
- JWT-Based Authentication
- AI-Based Threat Detection
- Insider Threat Monitoring
- Employee Risk Scoring
- Explainable AI Analysis
- SHAP Feature Importance
- Email Alert System
- Admin Dashboard
- Bulk CSV Analysis
- Data Visualization Charts
- Activity Logging System

---

# ⚙️ How to Run

## 1️⃣ Install Required Software

- Install Python
- Install MySQL or XAMPP
- Install VS Code / PyCharm

---

## 2️⃣ Clone the Project

```bash
git clone https://github.com/your-username/ethical-security-ai-agent.git


3️⃣ Install Required Packages

pip install -r requirements.txt

4️⃣ Configure Database

Create a MySQL database:
CREATE DATABASE security_agent;


5️⃣ Update .env File

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=security_agent


6️⃣ Run FastAPI Backend

uvicorn backend:app --reload


7️⃣ Run Streamlit Frontend

streamlit run agent.py


🌐 Application URLs

FastAPI Backend
http://127.0.0.1:8000

Streamlit Frontend
http://localhost:8501

🔑 Demo Login Credentials

Admin Login
Username: admin
Password: 1234admin


📂 Project Modules

agent.py → Streamlit Frontend
backend.py → FastAPI Backend
model.py → Machine Learning Model
auth.py → JWT Authentication
database.py → MySQL Database Connection
logs.csv → Activity Logs
requirements.txt → Required Packages


🤖 Machine Learning Used

Isolation Forest
Used for:
Anomaly Detection
Insider Threat Detection
Risk Prediction

SHAP Explainability
Used for:
Feature Importance
AI Decision Explanation
Transparent Security Analysis

📊 System Workflow

User logs into the system
Employee activity data is entered
AI model analyzes behavior
Risk score is generated
Threat level is classified
AI explanation is displayed
Email alert is sent
Logs are stored in database


👨‍💻 Developed By

 MCA Student
