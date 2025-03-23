import streamlit as st

# 1. Set page config FIRST
st.set_page_config(page_title="AI Medical Bill Recovery Agent", layout="wide")

import pandas as pd
import random
import datetime
import matplotlib.pyplot as plt
import smtplib
import threading
from email.mime.text import MIMEText
from streamlit_extras.metric_cards import style_metric_cards

# --- Email sending utility ---
def send_email(subject, body, to_email):
    sender_email = "demodb.notify@gmail.com"  # Replace with your Gmail
    app_password = "ynwjwhawgpzwoyhz"         # Replace with your App Password

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, msg.as_string())
    except Exception as e:
        st.error(f"Failed to send email to {to_email}: {e}")

# --- Generate Mock Patient Data ---
def generate_mock_data():
    names = [
        'John Doe', 'Jane Smith', 'Alice Johnson', 'Bob Lee', 'Maria Kim',
        'Ethan Zhang', 'Olivia Brown', 'Liam Wilson', 'Emma Davis', 'Noah Patel'
    ]
    data = []
    for name in names:
        score = random.randint(25, 95)
        balance_due = random.randint(300, 2000)
        due_date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))
        late_fee = int(balance_due * 0.05)
        action = (
            "Send Reminder" if score >= 80 else
            "Offer Payment Plan" if score >= 50 else
            "Escalate"
        )
        data.append({
            'Name': name,
            'Email': 'abhijeetkb@gmail.com',  # Hardcoded for testing
            'Balance Due': balance_due,
            'Due Date': due_date.strftime('%Y-%m-%d'),
            'Late Fee': late_fee,
            'Payment Score': score,
            'Recommended Action': action,
            'Status': "Uncontacted"
        })
    return pd.DataFrame(data)

# --- Session State Initialization ---
if "df" not in st.session_state:
    st.session_state.df = generate_mock_data()

# --- Color coding function ---
def color_score(score):
    if score >= 80:
        return "green"
    elif score >= 50:
        return "orange"
    else:
        return "red"

# --- Sidebar Filters ---
st.sidebar.title("🔍 Filter Options")
filter_option = st.sidebar.selectbox(
    "Filter by Payment Likelihood",
    ["All", "High (80-100%)", "Medium (50-79%)", "Low (<50%)"]
)

# --- Main Title ---
st.title("💰 AI Medical Bill Recovery Agent")
st.caption("AI-powered insights for prioritizing and recovering unpaid healthcare accounts.")

# --- Filtered Data ---
df = st.session_state.df
if filter_option == "High (80-100%)":
    view_df = df[df["Payment Score"] >= 80]
elif filter_option == "Medium (50-79%)":
    view_df = df[(df["Payment Score"] >= 50) & (df["Payment Score"] < 80)]
elif filter_option == "Low (<50%)":
    view_df = df[df["Payment Score"] < 50]
else:
    view_df = df

# --- Trigger All Button ---
if st.button("🚀 Trigger All Actions"):
    for i in df.index:
        df.at[i, 'Status'] = '✅ Triggered'
    st.success("All actions marked as triggered. Sending emails asynchronously...")

    # Asynchronous bulk email sending
    def send_bulk_emails():
        for i in df.index:
            name = df.at[i, 'Name']
            balance = df.at[i, 'Balance Due']
            due = df.at[i, 'Due Date']
            fee = df.at[i, 'Late Fee']
            action = df.at[i, 'Recommended Action']

            email_body = f"""
            Dear {name},

            This is a reminder that your account has an outstanding balance of ${balance}, which was due on {due}.
            A late fee of ${fee} has been applied.

            Recommended Action: {action}

            Please log in to your account to complete the payment or set up a payment plan.

            Thank you,
            Revenue Recovery Team
            """
            send_email(
                subject="[Action Required] Outstanding Balance Notification",
                body=email_body,
                to_email=df.at[i, 'Email']
            )

    threading.Thread(target=send_bulk_emails).start()

# --- Table ---
st.subheader("📋 Unpaid Accounts")

for _, row in view_df.iterrows():
    # Find the actual index in the original df
    actual_index = df[df["Name"] == row["Name"]].index[0]

    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 2, 2, 2, 2, 1.5])
    col1.write(f"**{row['Name']}**")
    col2.write(f"${row['Balance Due']}")
    col3.write(row['Due Date'])
    col4.markdown(
        f"<span style='color:{color_score(row['Payment Score'])}'>{row['Payment Score']}%</span>",
        unsafe_allow_html=True
    )
    col5.write(row['Recommended Action'])

    current_status = df.at[actual_index, 'Status']
    if current_status == '✅ Triggered':
        col6.success(current_status)
    else:
        col6.write(current_status)

    if col7.button("Trigger", key=f"trigger_{actual_index}"):
        # Update DataFrame status immediately
        df.at[actual_index, 'Status'] = '✅ Triggered'
        st.toast(f"Action triggered for {row['Name']}", icon="✅")

        # Force a page reload so status updates right away (no waiting)
        st.rerun()

        # Asynchronously send this single email
        def send_individual_email(name, balance, due, fee, action, email):
            body = f"""
            Dear {name},

            This is a reminder that your account has an outstanding balance of ${balance}, which was due on {due}.
            A late fee of ${fee} has been applied.

            Recommended Action: {action}

            Please log in to your account to complete the payment or set up a payment plan.

            Thank you,
            Revenue Recovery Team
            """
            send_email(
                subject="[Action Required] Outstanding Balance Notification",
                body=body,
                to_email=email
            )

        threading.Thread(
            target=send_individual_email,
            args=(
                row['Name'],
                row['Balance Due'],
                row['Due Date'],
                row['Late Fee'],
                row['Recommended Action'],
                row['Email']
            )
        ).start()

# --- Visualizations ---
st.subheader("📊 Payment Score Insights")
colA, colB = st.columns(2)

with colA:
    fig1, ax1 = plt.subplots(figsize=(5, 3))
    score_bins = [0, 50, 80, 100]
    labels = ['Low (<50%)', 'Medium (50-79%)', 'High (80-100%)']
    df['Score Range'] = pd.cut(df['Payment Score'], bins=score_bins, labels=labels, include_lowest=True)
    score_counts = df['Score Range'].value_counts().reindex(labels)
    ax1.bar(score_counts.index, score_counts.values, color=['red', 'orange', 'green'])
    ax1.set_ylabel("# of Accounts")
    ax1.set_title("Accounts by Payment Score")
    st.pyplot(fig1)

with colB:
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    action_counts = df['Recommended Action'].value_counts()
    ax2.pie(action_counts, labels=action_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    ax2.set_title("Recommended Actions")
    st.pyplot(fig2)

# Optional style enhancements
style_metric_cards()
