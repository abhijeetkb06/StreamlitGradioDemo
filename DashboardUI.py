import streamlit as st
import pandas as pd
import random
import datetime
import matplotlib.pyplot as plt
from streamlit_extras.metric_cards import style_metric_cards

# --- Generate Mock Patient Data ---
def generate_mock_data():
    names = [
        'John Doe', 'Jane Smith', 'Alice Johnson', 'Bob Lee', 'Maria Kim',
        'Ethan Zhang', 'Olivia Brown', 'Liam Wilson', 'Emma Davis', 'Noah Patel'
    ]
    data = []
    for name in names:
        score = random.randint(25, 95)
        action = (
            "Send Reminder" if score >= 80 else
            "Offer Payment Plan" if score >= 50 else
            "Escalate"
        )
        data.append({
            'Name': name,
            'Balance Due': f"${random.randint(300, 2000)}",
            'Due Date': (datetime.date.today() + datetime.timedelta(days=random.randint(5, 30))).strftime('%Y-%m-%d'),
            'Payment Score': score,
            'Recommended Action': action,
            'Status': "Uncontacted"
        })
    return pd.DataFrame(data)

# --- Color coding function ---
def color_score(score):
    if score >= 80:
        return "green"
    elif score >= 50:
        return "orange"
    else:
        return "red"

# --- Sidebar Filters ---
st.set_page_config(page_title="AI Revenue Guardian", layout="wide")
st.sidebar.title("🔍 Filter Options")
filter_option = st.sidebar.selectbox("Filter by Payment Likelihood", ["All", "High (80-100%)", "Medium (50-79%)", "Low (<50%)"])

# --- Main Title ---
st.title("💰 AI-Powered Revenue Guardian Dashboard")
st.caption("AI-powered insights for prioritizing and recovering unpaid healthcare accounts.")

# --- Generate and Filter Data ---
df = generate_mock_data()
if filter_option == "High (80-100%)":
    df = df[df["Payment Score"] >= 80]
elif filter_option == "Medium (50-79%)":
    df = df[(df["Payment Score"] >= 50) & (df["Payment Score"] < 80)]
elif filter_option == "Low (<50%)":
    df = df[df["Payment Score"] < 50]

# --- Triggered State Tracker ---
triggered_status = {}

# --- Trigger All Button ---
if st.button("🚀 Trigger All Actions"):
    for i in df.index:
        df.at[i, 'Status'] = '✅ Triggered'
    st.success("All actions triggered successfully!")

# --- Table ---
st.subheader("📋 Unpaid Accounts")
for index, row in df.iterrows():
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 2, 2, 2, 2, 1.5])
    col1.write(f"**{row['Name']}**")
    col2.write(row['Balance Due'])
    col3.write(row['Due Date'])
    col4.markdown(f"<span style='color:{color_score(row['Payment Score'])}'>{row['Payment Score']}%</span>", unsafe_allow_html=True)
    col5.write(row['Recommended Action'])
    status = row['Status']
    if status == "✅ Triggered":
        col6.success(status)
    else:
        col6.write(status)

    if col7.button("Trigger", key=index):
        df.at[index, 'Status'] = '✅ Triggered'
        st.toast(f"Action triggered for {row['Name']}", icon="✅")

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

# --- Optional: Style enhancements ---
style_metric_cards()
