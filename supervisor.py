# File: supervisor.py
# PURPOSE: Orchestrates the full multi-agent pipeline:
#          Data Agent -> Research Agent (parallel) -> Report Agent
# WHERE THIS FILE LIVES: project root (crm-analyst-multiagent/supervisor.py)
# HOW TO RUN: python supervisor.py
#             (or imported by app.py for the Gradio UI later)

import asyncio
import time

from agents.data_agent import run_data_agent
from agents.research_agent import run_research_agent
from agents.report_agent import run_report_agent


async def run_supervisor(user_question: str) -> dict:
    """
    Runs the full pipeline and returns a dict with the PDF path,
    the number of accounts analyzed, and total latency in ms.
    """
    start = time.time()
    print(f"[Supervisor] Question: {user_question}")

    # ---- Step 1: Data Agent ----
    print("[Supervisor] -> Delegating to Data Agent "
          "(querying SQLite + scoring risk)...")
    at_risk_accounts = await run_data_agent(
        region="AMER", inactive_days=90
    )
    print(f"[Supervisor] Data Agent found "
          f"{len(at_risk_accounts)} at-risk accounts")

    if not at_risk_accounts:
        print("[Supervisor] No at-risk accounts found. Stopping early.")
        return {
            "pdf_path": None,
            "accounts_analyzed": 0,
            "latency_ms": round((time.time() - start) * 1000),
        }

    # ---- Step 2: Research Agent (parallel, one call per account) ----
    print(f"[Supervisor] -> Delegating to Research Agent "
          f"({len(at_risk_accounts)} accounts, in parallel)...")
    research_tasks = [
        run_research_agent(account) for account in at_risk_accounts
    ]
    research_results = await asyncio.gather(
        *research_tasks, return_exceptions=True
    )

    for account, enrichment in zip(at_risk_accounts, research_results):
        if isinstance(enrichment, Exception):
            print(f"[Supervisor]   Research failed for "
                  f"{account['name']}: {enrichment}")
            account["web_signal"] = "Research failed"
            account["web_signal_detected"] = False
        else:
            account.update(enrichment)

    # ---- Step 3: Report Agent ----
    print("[Supervisor] -> Delegating to Report Agent "
          "(generating PDF)...")
    pdf_path = await run_report_agent(at_risk_accounts, user_question)

    elapsed_ms = round((time.time() - start) * 1000)
    print(f"[Supervisor] Done in {elapsed_ms}ms. Report: {pdf_path}")

    return {
        "pdf_path": pdf_path,
        "accounts_analyzed": len(at_risk_accounts),
        "latency_ms": elapsed_ms,
    }


if __name__ == "__main__":
    result = asyncio.run(run_supervisor(
        "Which AMER accounts had no activity in 90 days "
        "and are at risk of churn?"
    ))
    print("\n=== Final Result ===")
    print(result)