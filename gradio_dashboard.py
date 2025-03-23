import gradio as gr
import pandas as pd
import random
import datetime
import matplotlib.pyplot as plt

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

# --- Filter + Chart Generator ---
def dashboard(filter_option):
    df = generate_mock_data()

    if filter_option == "High (80-100%)":
        df = df[df["Payment Score"] >= 80]
    elif filter_option == "Medium (50-79%)":
        df = df[(df["Payment Score"] >= 50) & (df["Payment Score"] < 80)]
    elif filter_option == "Low (<50%)":
        df = df[df["Payment Score"] < 50]

    # Color-code scores
    def format_score(score):
        color = "green" if score >= 80 else "orange" if score >= 50 else "red"
        return f"<span style='color:{color}'>{score}%</span>"

    df_display = df.copy()
    df_display['Payment Score'] = df_display['Payment Score'].apply(format_score)

    html_table = df_display.to_html(escape=False, index=False)

    # Bar chart
    fig1, ax1 = plt.subplots(figsize=(5, 3))
    score_bins = [0, 50, 80, 100]
    labels = ['Low (<50%)', 'Medium (50-79%)', 'High (80-100%)']
    df['Score Range'] = pd.cut(df['Payment Score'], bins=score_bins, labels=labels, include_lowest=True)
    score_counts = df['Score Range'].value_counts().reindex(labels)
    ax1.bar(score_counts.index, score_counts.values, color=['red', 'orange', 'green'])
    ax1.set_ylabel("# of Accounts")
    ax1.set_title("Accounts by Payment Score")

    # Pie chart
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    action_counts = df['Recommended Action'].value_counts()
    ax2.pie(action_counts, labels=action_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.set_title("Recommended Actions")
    ax2.axis("equal")

    return html_table, fig1, fig2

# --- Gradio UI ---
with gr.Blocks(title="AI Revenue Guardian Dashboard") as demo:
    gr.Markdown("## 💰 AI-Powered Revenue Guardian Dashboard")
    gr.Markdown("Use filters to prioritize accounts and visualize payment recovery strategy.")

    filter_dropdown = gr.Dropdown(
        choices=["All", "High (80-100%)", "Medium (50-79%)", "Low (<50%)"],
        value="All",
        label="Filter by Payment Likelihood"
    )

    table_output = gr.HTML()
    bar_chart_output = gr.Plot()
    pie_chart_output = gr.Plot()

    filter_dropdown.change(
        fn=dashboard,
        inputs=[filter_dropdown],
        outputs=[table_output, bar_chart_output, pie_chart_output]
    )

    gr.Markdown("### 📋 Unpaid Accounts")
    table_output

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📊 Accounts by Payment Score")
            bar_chart_output
        with gr.Column():
            gr.Markdown("### 🧠 Recommended Actions")
            pie_chart_output

demo.launch()
