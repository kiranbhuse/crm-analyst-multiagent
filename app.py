# File: app.py
# PURPOSE: Gradio web UI wrapper for the Supervisor multi-agent pipeline.
# WHERE THIS RUNS: locally first (python app.py), then on HF Spaces.
# WHERE THIS FILE LIVES: project root, same folder as supervisor.py

import asyncio
import os

import gradio as gr

from supervisor import run_supervisor


def analyze(question: str):
    """Called when the user clicks Submit in the Gradio UI."""
    if not question or not question.strip():
        return None, "Please enter a business question."

    result = asyncio.run(run_supervisor(question))

    if result["accounts_analyzed"] == 0:
        return None, "No at-risk accounts found for this query."

    summary = (
        f"Analyzed {result['accounts_analyzed']} accounts "
        f"in {result['latency_ms']}ms.\n"
        f"Report saved to: {result['pdf_path']}"
    )

    return result["pdf_path"], summary


demo = gr.Interface(
    fn=analyze,
    inputs=gr.Textbox(
        label="Business Question",
        value="Which AMER accounts had no activity in 90 days "
              "and are at risk of churn?",
        lines=2,
    ),
    outputs=[
        gr.File(label="Download Risk Report PDF"),
        gr.Textbox(label="Summary"),
    ],
    title="🤖 Multi-Agent Salesforce CRM Analyst (MCP-powered)",
    description=(
        "A Supervisor agent orchestrates 3 sub-agents: a Data Agent "
        "(SQLite + risk scoring), a Research Agent (parallel web "
        "search for churn signals), and a Report Agent (PDF "
        "generation) — all connected via the Model Context Protocol."
    ),
)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
    )