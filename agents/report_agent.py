# File: agents/report_agent.py
# PURPOSE: Generates the final PDF churn risk report via the custom-pdf
#          MCP server, using the merged account data from the Data
#          Agent and Research Agent.
# CALLED BY: supervisor.py
# NOTE: GitHub auto-push is intentionally left out of this version to
#       keep the pipeline simple and reliable first. It can be added
#       as a later enhancement once the core flow is proven to work.

import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_report_agent(accounts: list, question: str) -> str:
    """
    Generate a PDF report from the account list via the custom-pdf
    MCP server. Returns the path to the generated PDF.
    """
    pdf_params = StdioServerParameters(
        command="python",
        args=["servers/pdf_server.py"],
    )

    async with stdio_client(pdf_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "generate_pdf_report",
                {
                    "accounts_json": json.dumps(accounts),
                    "question": question,
                    "output_path": "output/churn_report.pdf",
                },
            )
            pdf_path = result.content[0].text
            return pdf_path


# Standalone test
if __name__ == "__main__":
    import asyncio

    async def _test():
        fake_accounts = [
            {
                "name": "Company 15", "region": "AMER",
                "days_inactive": 135, "risk_score": 70,
                "risk_level": "HIGH",
                "top_factor": "critical inactivity (>120 days)",
            },
            {
                "name": "Company 02", "region": "AMER",
                "days_inactive": 95, "risk_score": 55,
                "risk_level": "HIGH",
                "top_factor": "moderate inactivity (90-120 days)",
            },
        ]
        path = await run_report_agent(
            fake_accounts,
            "Which AMER accounts had no activity in 90 days?",
        )
        print(f"Report generated at: {path}")

    asyncio.run(_test())