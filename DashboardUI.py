import streamlit as st

# Must be the first Streamlit command
st.set_page_config(page_title="AI Medical Bill Recovery Agent", layout="wide")

import pandas as pd
import random
import datetime
import matplotlib.pyplot as plt
import smtplib
import threading
from email.mime.text import MIMEText
from streamlit_extras.metric_cards import style_metric_cards

# --- Email utility ---
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
        return True
    except Exception as e:
        st.error(f"Failed to send email to {to_email}: {e}")
        return False

# --- Generate Mock Patient Data ---
def generate_mock_data():
    names = [
        'John Doe', 'Jane Smith', 'Alice Johnson', 'Bob Lee', 'Maria Kim',
        'Ethan Zhang', 'Olivia Brown', 'Liam Wilson', 'Emma Davis', 'Noah Patel'
    ]
    data = []
    for i, name in enumerate(names):
        score = random.randint(25, 95)
        balance_due = random.randint(300, 2000)
        due_date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))
        late_fee = int(balance_due * 0.05)
        action = ("Send Reminder" if score >= 80 else
                  "Offer Payment Plan" if score >= 50 else
                  "Escalate")
        data.append({
            'RowID': i,  # Unique ID for each row
            'Name': name,
            'Balance Due': balance_due,
            'Due Date': due_date.strftime('%Y-%m-%d'),
            'Late Fee': late_fee,
            'Payment Score': score,
            'Recommended Action': action,
            'Status': "Uncontacted"
        })
    return pd.DataFrame(data)

# --- Session State ---
if "df" not in st.session_state:
    st.session_state.df = generate_mock_data()

if "filter_choice" not in st.session_state:
    st.session_state.filter_choice = "All"

# --- color coding ---
def color_score(score):
    if score >= 80:
        return "green"
    elif score >= 50:
        return "orange"
    else:
        return "red"

# --- Sidebar Filter ---
st.sidebar.title("🔍 Filter Options")
choice = st.sidebar.selectbox(
    "Filter by Payment Likelihood",
    ["All", "High (80-100%)", "Medium (50-79%)", "Low (<50%)"],
    index=["All","High (80-100%)","Medium (50-79%)","Low (<50%)"].index(st.session_state.filter_choice)
)
if choice != st.session_state.filter_choice:
    st.session_state.filter_choice = choice

# --- Title ---
st.title("💰 AI Medical Bill Recovery Agent")
st.caption("AI-powered insights for prioritizing and recovering unpaid healthcare accounts.")

# Quick references
df = st.session_state.df

# --- Trigger All ---
if st.button("🚀 Trigger All Actions"):
    for i in df.index:
        df.at[i, 'Status'] = '📧 Email Sent'
    st.success("All actions now marked as Email Sent. Sending bulk emails asynchronously...")

    def send_bulk_emails():
        for i in df.index:
            row = df.loc[i]
            subj = f"[BULK] Notification"
            body = f"""
            Dear {row['Name']},

            This is a reminder that your account has an outstanding balance of ${row['Balance Due']}, 
            which was due on {row['Due Date']}.
            A late fee of ${row['Late Fee']} has been applied.

            Recommended Action: {row['Recommended Action']}
            """
            send_email(subj, body, "abhijeetkb@gmail.com")

    threading.Thread(target=send_bulk_emails).start()

# --- Filter data ---
if st.session_state.filter_choice == "High (80-100%)":
    view_df = df[df["Payment Score"] >= 80]
elif st.session_state.filter_choice == "Medium (50-79%)":
    view_df = df[(df["Payment Score"] >= 50) & (df["Payment Score"] < 80)]
elif st.session_state.filter_choice == "Low (<50%)":
    view_df = df[df["Payment Score"] < 50]
else:
    view_df = df

# --- Table ---
st.subheader("📋 Unpaid Accounts")

for i, row in view_df.iterrows():
    row_key = row['RowID']
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2,1,2,2,2,2,1.5])

    # 1) Check if user triggered email for this row
    #    If so, update the DataFrame row BEFORE showing status
    button_key = f"trigger_button_{row_key}"
    if col7.button("Trigger", key=button_key):
        # Update the row's status in memory
        df.at[i, 'Status'] = '📧 Email Sent'
        st.toast(f"Email sent to {row['Name']}", icon="✅")

        def send_individual_email():
            suffix = random.randint(1000,9999)
            subject_line = f"[INDIVIDUAL_{suffix}] Payment Notice"
            body = f"""
            Dear {row['Name']},

            This is a reminder that your account has an outstanding balance of ${row['Balance Due']}, 
            which was due on {row['Due Date']}.
            A late fee of ${row['Late Fee']} has been applied.

            Recommended Action: {row['Recommended Action']}
            """
            send_email(subject_line, body, "abhijeetkb@gmail.com")

        threading.Thread(target=send_individual_email).start()

    # 2) Now read the updated row from the DataFrame
    updated_status = df.at[i, 'Status']

    # 3) Show the row
    col1.write(f"**{row['Name']}**")
    col2.write(f"${row['Balance Due']}")
    col3.write(row['Due Date'])
    col4.markdown(
        f"<span style='color:{color_score(row['Payment Score'])}'>{row['Payment Score']}%</span>",
        unsafe_allow_html=True
    )
    col5.write(row['Recommended Action'])

    if updated_status == '📧 Email Sent':
        col6.success(updated_status)
    else:
        col6.write(updated_status)

# --- Visualization ---
st.subheader("📊 Payment Score Insights")
cA, cB = st.columns(2)

with cA:
    fig1, ax1 = plt.subplots(figsize=(5,3))
    bins = [0,50,80,100]
    labs = ['Low (<50%)','Medium (50-79%)','High (80-100%)']
    df['Score Range'] = pd.cut(df['Payment Score'], bins=bins, labels=labs, include_lowest=True)
    score_counts = df['Score Range'].value_counts().reindex(labs)
    ax1.bar(score_counts.index, score_counts.values, color=['red','orange','green'])
    ax1.set_ylabel("# of Accounts")
    ax1.set_title("Accounts by Payment Score")
    st.pyplot(fig1)

with cB:
    fig2, ax2 = plt.subplots(figsize=(5,3))
    action_counts = df['Recommended Action'].value_counts()
    ax2.pie(action_counts, labels=action_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    ax2.set_title("Recommended Actions")
    st.pyplot(fig2)

style_metric_cards()
