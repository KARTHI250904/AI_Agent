# Updated `agent.py`

import streamlit as st
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Security AI Agent", layout="centered")

st.title("🔐 Ethical Security AI Agent")

# =========================
# GLOBAL LOG FILE
# =========================
log_file = "logs.csv"

# =========================
# SAVE LOG
# =========================
def save_log(data):
    clean_data = data.copy()

    if isinstance(clean_data.get("explanation"), dict):
        clean_data["explanation"] = str(clean_data["explanation"])

    df = pd.DataFrame([clean_data])

    if os.path.exists(log_file):
        df.to_csv(log_file, mode="a", header=False, index=False)
    else:
        df.to_csv(log_file, index=False)

# =========================
# EMAIL FUNCTION
# =========================
def send_email_alert(data):

    sender_email = "securityteam010203@gmail.com"
    receiver_email = "karthickkumar25092004@gmail.com"
    password = "ctzs ueqj yenb htdl"

    risk_score = float(data.get("risk_score", 0))

    if risk_score < 0.3:
        alert_type = "LOW"
    elif risk_score < 0.5:
        alert_type = "MEDIUM"
    elif risk_score < 0.75:
        alert_type = "HIGH"
    else:
        alert_type = "CRITICAL"

    subject = f"ALERT: {alert_type} Risk - Employee {data.get('employee_id')}"

    explanation = data.get("explanation", {})
    features = explanation.get("input_data", {})

    body = f"""
ALERT TYPE: {alert_type}

Employee ID: {data.get('employee_id')}
Risk Score: {round(risk_score, 2)}
Decision: {data.get('decision')}

Details:
Login Hour: {features.get('login_hour', 'N/A')}
Location Changed: {'Yes' if features.get('location_change', 0) == 1 else 'No'}
Network: {'Yes' if features.get('network', 0) == 1 else 'No'}
Sensitive Access: {'Yes' if features.get('sensitive', 0) == 1 else 'No'}
Records: {features.get('records', 'N/A')}
Download: {'Yes' if features.get('download', 0) == 1 else 'No'}

Explanation:
{explanation.get('reason', 'AI-based anomaly detection')}
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)

    except Exception as e:
        st.warning(f"Email failed: {e}")

# =========================
# LOGIN
# =========================
if "token" not in st.session_state:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        try:
            res = requests.post(
                f"{API_URL}/login",
                json={
                    "username": username,
                    "password": password
                }
            )

            if res.status_code == 200:
                st.session_state.token = res.json()["access_token"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid login")

        except Exception as e:
            st.error(f"Backend connection error: {e}")

    st.stop()

# =========================
# AFTER LOGIN
# =========================
st.success("Logged in")

headers = {
    "Authorization": f"Bearer {st.session_state.token}"
}

menu = st.sidebar.selectbox(
    "Menu",
    ["Analyze", "Bulk CSV", "Admin Panel"]
)

# =====================================================
# SINGLE ANALYSIS
# =====================================================
if menu == "Analyze":

    emp_id = int(st.number_input("Employee ID", min_value=0))

    login_hour = st.slider("Login Hour", 0, 23)

    location_change = st.selectbox("Location", ["No", "Yes"])

    network = st.selectbox("Network", ["No", "Yes"])

    sensitive = st.selectbox("Sensitive", ["No", "Yes"])

    records = st.number_input("Records", 0, 10000)

    download = st.selectbox("Download", ["No", "Yes"])

    # ========================================
    # YES/NO CONVERTER
    # ========================================
    def convert(x):
        return 1 if x == "Yes" else 0

    # ========================================
    # CUSTOM RISK ENGINE
    # ========================================
    def risk_engine(
        login_hour,
        location_change,
        network,
        sensitive,
        records,
        download
    ):

        risk = 0

        if login_hour < 6 or login_hour > 22:
            risk += 0.2

        if location_change == "Yes":
            risk += 0.2

        if network == "Yes":
            risk += 0.2

        if sensitive == "Yes":
            risk += 0.2

        if records > 5000:
            risk += 0.1

        if download == "Yes":
            risk += 0.3

        return min(risk, 1)

    # ========================================
    # DECISION FUNCTION
    # ========================================
    def decision(score):

        if score < 0.20:
            return "LOW RISK"

        elif score < 0.50:
            return "MEDIUM RISK"

        elif score < 0.75:
            return "HIGH RISK"

        return "CRITICAL RISK"

    # ========================================
    # ANALYZE BUTTON
    # ========================================
    if st.button("Analyze"):

        # ========================================
        # CUSTOM RISK SCORE
        # ========================================
        custom_risk_score = risk_engine(
            login_hour,
            location_change,
            network,
            sensitive,
            records,
            download
        )

        custom_decision = decision(
            custom_risk_score
        )

        # ========================================
        # NORMALIZATION
        # ========================================
        normalized_login_hour = round(
            login_hour / 23,
            2
        )

        normalized_records = round(
            records / 10000,
            2
        )

        payload = {

            "employee_id": emp_id,

            "login_hour":
                normalized_login_hour,

            "location_change":
                convert(location_change),

            "network":
                convert(network),

            "sensitive":
                convert(sensitive),

            "records":
                normalized_records,

            "download":
                convert(download)
        }

        try:

            res = requests.post(
                f"{API_URL}/analyze",
                json=payload,
                headers=headers
            )

            if res.status_code == 200:

                data = res.json()

                data["employee_id"] = emp_id

                # ========================================
                # OVERRIDE ML SCORE
                # ========================================
                data["risk_score"] = custom_risk_score

                data["decision"] = custom_decision

                risk_score = float(
                    data.get("risk_score", 0)
                )

                st.success("Analysis Complete")

                # ========================================
                # RISK SCORE
                # ========================================
                st.metric(
                    label="Risk Score",
                    value=f"{risk_score:.2f}"
                )

                # ========================================
                # DECISION
                # ========================================
                st.subheader(
                    f"Decision: {data['decision']}"
                )

                # ========================================
                # SAVE + EMAIL
                # ========================================
                save_log(data)

                send_email_alert(data)

                # ========================================
                # CUSTOM RISK PIE CHART
                # ========================================

                risk_labels = []
                risk_values = []

                # Login hour risk
                if login_hour < 6 or login_hour > 22:
                    risk_labels.append("Login Hour")
                    risk_values.append(0.2)

                # Location risk
                if location_change == "Yes":
                    risk_labels.append("Location")
                    risk_values.append(0.2)

                # Network risk
                if network == "Yes":
                    risk_labels.append("Network")
                    risk_values.append(0.2)

                # Sensitive risk
                if sensitive == "Yes":
                    risk_labels.append("Sensitive")
                    risk_values.append(0.2)

                # Records risk
                if records > 5000:
                    risk_labels.append("Records")
                    risk_values.append(0.1)

                # Download risk
                if download == "Yes":
                    risk_labels.append("Download")
                    risk_values.append(0.3)

                # ========================================
                # SHOW PIE CHART
                # ========================================

                if len(risk_values) > 0:

                    fig, ax = plt.subplots(
                        figsize=(7, 7)
                    )

                    ax.pie(
                        risk_values,
                        labels=risk_labels,
                        autopct="%1.1f%%",
                        startangle=90,
                        textprops={"fontsize": 12}
                    )

                    ax.set_title(
                        "Risk Contribution by Features"
                    )

                    st.pyplot(fig)

                else:

                    st.info(
                        "No risk factors detected"
                    )

                # ========================================
                # INPUT SUMMARY
                # ========================================
                st.subheader("Input Summary")

                summary_df = pd.DataFrame({

                    "Feature": [
                        "Login Hour",
                        "Location",
                        "Network",
                        "Sensitive",
                        "Records",
                        "Download"
                    ],

                    "Value": [
                        str(login_hour),
                        str(location_change),
                        str(network),
                        str(sensitive),
                        str(records),
                        str(download)
                    ]
                })

                st.table(summary_df)

                # ========================================
                # EXPLANATION
                # ========================================
                st.subheader("AI Explanation")

                st.info(
                    data["explanation"].get(
                        "reason",
                        "No explanation available"
                    )
                )
            else:

                st.error(
                    f"API Error: {res.text}"
                )

        except Exception as e:

            st.error(
                f"Connection failed: {e}"
            )


# =====================================================
# BULK CSV
# =====================================================
elif menu == "Bulk CSV":

    file = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if file:

        df = pd.read_csv(file)

        st.dataframe(df.head())

        # ========================================
        # YES/NO CONVERTER
        # ========================================
        def convert(x):
            return 1 if str(x).strip().lower() == "yes" else 0

        # ========================================
        # CUSTOM RISK ENGINE
        # ========================================
        def risk_engine(
            login_hour,
            location_change,
            network,
            sensitive,
            records,
            download
        ):

            risk = 0

            if login_hour < 6 or login_hour > 22:
                risk += 0.2

            if location_change == "Yes":
                risk += 0.2

            if network == "Yes":
                risk += 0.2

            if sensitive == "Yes":
                risk += 0.2

            if records > 5000:
                risk += 0.1

            if download == "Yes":
                risk += 0.3

            return min(risk, 1)

        # ========================================
        # DECISION FUNCTION
        # ========================================
        def decision(score):

            if score < 0.20:
                return "LOW RISK"

            elif score < 0.50:
                return "MEDIUM RISK"

            elif score < 0.75:
                return "HIGH RISK"

            return "CRITICAL RISK"

        if st.button("Analyze All"):

            results = []

            for _, row in df.iterrows():

                try:

                    # ========================================
                    # ORIGINAL VALUES
                    # ========================================
                    login_hour = int(row["login_hour"])

                    location_change = str(
                        row["location_change"]
                    )

                    network = str(
                        row["network"]
                    )

                    sensitive = str(
                        row["sensitive"]
                    )

                    records = int(
                        row["records"]
                    )

                    download = str(
                        row["download"]
                    )

                    # ========================================
                    # CUSTOM RISK SCORE
                    # ========================================
                    custom_risk_score = risk_engine(
                        login_hour,
                        location_change,
                        network,
                        sensitive,
                        records,
                        download
                    )

                    custom_decision = decision(
                        custom_risk_score
                    )

                    # ========================================
                    # NORMALIZATION
                    # ========================================
                    normalized_login_hour = round(
                        login_hour / 23,
                        2
                    )

                    normalized_records = round(
                        records / 10000,
                        2
                    )

                    payload = {

                        "employee_id": int(
                            row["employee_id"]
                        ),

                        "login_hour":
                            normalized_login_hour,

                        "location_change":
                            convert(location_change),

                        "network":
                            convert(network),

                        "sensitive":
                            convert(sensitive),

                        "records":
                            normalized_records,

                        "download":
                            convert(download)
                    }

                    # ========================================
                    # API CALL
                    # ========================================
                    res = requests.post(
                        f"{API_URL}/analyze",
                        json=payload,
                        headers=headers
                    )

                    if res.status_code == 200:

                        data = res.json()

                        # ========================================
                        # OVERRIDE ML SCORE
                        # ========================================
                        data["risk_score"] = custom_risk_score

                        data["decision"] = custom_decision

                        data["employee_id"] = row[
                            "employee_id"
                        ]

                        results.append(data)

                        save_log(data)

                        send_email_alert(data)

                except Exception as e:

                    st.error(
                        f"Error processing row: {e}"
                    )

            # ========================================
            # RESULTS TABLE
            # ========================================
            if len(results) > 0:

                st.success("Bulk Analysis Done")

                results_df = pd.DataFrame(results)

                # Fix mixed datatype issue
                results_df = results_df.astype(str)

                st.dataframe(results_df)

                # ========================================
                # BULK RISK PIE CHART
                # ========================================
                low_count = 0
                medium_count = 0
                high_count = 0
                critical_count = 0

                for item in results:

                    decision_value = item.get(
                        "decision",
                        ""
                    )

                    if decision_value == "LOW RISK":
                        low_count += 1

                    elif decision_value == "MEDIUM RISK":
                        medium_count += 1

                    elif decision_value == "HIGH RISK":
                        high_count += 1

                    elif decision_value == "CRITICAL RISK":
                        critical_count += 1

                labels = []
                values = []

                if low_count > 0:
                    labels.append("LOW")
                    values.append(low_count)

                if medium_count > 0:
                    labels.append("MEDIUM")
                    values.append(medium_count)

                if high_count > 0:
                    labels.append("HIGH")
                    values.append(high_count)

                if critical_count > 0:
                    labels.append("CRITICAL")
                    values.append(critical_count)

                if len(values) > 0:

                    fig, ax = plt.subplots(
                        figsize=(7, 7)
                    )

                    ax.pie(
                        values,
                        labels=labels,
                        autopct="%1.1f%%",
                        startangle=90,
                        textprops={"fontsize": 12}
                    )

                    ax.set_title(
                        "Bulk CSV Risk Distribution"
                    )

                    st.pyplot(fig)

                # ========================================
                # RISK SUMMARY TABLE
                # ========================================
                # ========================================
                # RISK SUMMARY TABLE WITH EMPLOYEE IDS
                # ========================================
                st.subheader("Risk Summary")

                low_emp_ids = []
                medium_emp_ids = []
                high_emp_ids = []
                critical_emp_ids = []

                for item in results:

                    decision_value = item.get(
                        "decision",
                        ""
                    )

                    emp_id_value = str(
                        item.get("employee_id", "")
                    )

                    if decision_value == "LOW RISK":
                        low_emp_ids.append(emp_id_value)

                    elif decision_value == "MEDIUM RISK":
                        medium_emp_ids.append(emp_id_value)

                    elif decision_value == "HIGH RISK":
                        high_emp_ids.append(emp_id_value)

                    elif decision_value == "CRITICAL RISK":
                        critical_emp_ids.append(emp_id_value)

                summary_df = pd.DataFrame({

                    "Risk Level": [
                        "LOW",
                        "MEDIUM",
                        "HIGH",
                        "CRITICAL"
                    ],

                    "Count": [
                        str(low_count),
                        str(medium_count),
                        str(high_count),
                        str(critical_count)
                    ],

                    "Employee IDs": [

                        ", ".join(low_emp_ids)
                        if low_emp_ids else "None",

                        ", ".join(medium_emp_ids)
                        if medium_emp_ids else "None",

                        ", ".join(high_emp_ids)
                        if high_emp_ids else "None",

                        ", ".join(critical_emp_ids)
                        if critical_emp_ids else "None"
                    ]
                })

                summary_df = summary_df.astype(str)

                st.table(summary_df)

            else:

                st.warning(
                    "No valid results generated"
                )
# =====================================================
# ADMIN PANEL
# =====================================================
elif menu == "Admin Panel":

    st.subheader("📊 Admin Dashboard")

    try:
        res = requests.get(f"{API_URL}/logs", headers=headers)

        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            st.dataframe(df)
        else:
            st.error("Access denied")

    except Exception as e:
        st.error(f"Cannot load logs: {e}")

    if os.path.exists(log_file):

        st.subheader("Local Logs")

        try:
            st.dataframe(pd.read_csv(log_file))

        except Exception:
            st.error("⚠️ Log file corrupted. Delete logs.csv and rerun.")


