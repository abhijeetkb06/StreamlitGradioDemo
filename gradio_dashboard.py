import gradio as gr
import pandas as pd
import random
import datetime
import matplotlib.pyplot as plt

# --- Generate Mock Data ---
def generate_mock_data():
    names = ['John Doe', 'Jane Smith', 'Alice Johnson', 'Bob Lee', 'Maria Kim',
             'Ethan Zhang', 'Olivia Brown', 'Liam Wilson', 'Emma Davis', 'Noah Patel']
    records = []
    for name in names:
        score = random.randint(25, 95)
        action = (
            "Send Reminder" if score >= 80 else
            "Offer Payment Plan" if score >= 50 else
            "Escalate"
        )
        records.append({
            'Name': name,
            'Balance Due': f"${random.randint(300, 2000)}",
            'Due Date': (datetime.date.today() + datetime.timedelta(days=random.randint(5, 30))).strftime('%Y-%m-%d'),
            'Payment Score': score,
            'Recommended Action': action,
            'Status': "Uncontacted"
        })
    return pd.DataFrame(records)

# --- Filter Function ---
def filter_data(range_label):
    df = generate_mock_data()
    if range_label == "High (80-100%)":
        df = df[df["Payment Score"] >= 80]
    elif range_label == "Medium (50-79%)":
        df = df[(df["Payment Score"] >= 50) & (df["Payment Score"] < 80)]
    elif range_label == "Low (<50%)":
        df = df[df["Payment Score"] < 50]
    return df

# --- Bar Chart ---
def score_bar_chart(df):
    fig, ax = plt.subplots()
    score_bins = [0, 50, 80, 100]
    labels = ['Low (<50%)', 'Medium (50-79%)', 'High (80-100%)']
    df['Score Range'] = pd.cut(df['Payment Score'], bins=score_bins, labels=labels, include_lowest=True)
    counts = df['Score Range'].value_counts().reindex(labels)
    ax.bar(counts.index, counts.values, color=['red', 'orange', 'green'])
    ax.set_title("Accounts by Payment Score")
    return fig

# --- Pie Chart ---
def action_pie_chart(df):
    fig, ax = plt.subplots()
    counts = df['Recommended Action'].value_counts()
    ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
    ax.set_title("Recommended Action Breakdown")
    ax.axis("equal")
    return fig

# --- Master Function ---
def update_dashboard(filter_option):
    df = filter_data(filter_option)
    table_html = df.to_html(index=False, classes="styled-table")
    return table_html, score_bar_chart(df), action_pie_chart(df)

# --- Gradio UI ---
with gr.Blocks(title="AI Revenue Guardian") as demo:
    gr.Markdown("## 💰 AI-Powered Revenue Guardian Dashboard")
    gr.Markdown("Use filters to prioritize accounts and visualize payment recovery strategy.")

    with gr.Row():
        filter_dropdown = gr.Dropdown(
            choices=["All", "High (80-100%)", "Medium (50-79%)", "Low (<50%)"],
            label="Filter by Payment Score",
            value="All"
        )

    table_output = gr.HTML()
    bar_chart_output = gr.Plot()
    pie_chart_output = gr.Plot()

    filter_dropdown.change(
        fn=update_dashboard,
        inputs=[filter_dropdown],
        outputs=[table_output, bar_chart_output, pie_chart_output]
    )

    gr.Markdown("### 📋 Accounts Table")
    table_output
    gr.Markdown("### 📊 Score Distribution")
    bar_chart_output
    gr.Markdown("### 🧠 Action Breakdown")
    pie_chart_output

# Launch
demo.launch()
