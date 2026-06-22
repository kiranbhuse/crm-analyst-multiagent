# File: tests/test_pdf_server.py
# PURPOSE: Calls generate_pdf_report directly via MCP, with fake sample
#          data, to confirm the PDF server actually produces a valid PDF
#          before wiring it into the full multi-agent pipeline.
# WHERE TO RUN: Terminal, from the PROJECT ROOT, venv active
# HOW TO RUN: python tests/test_pdf_server.py

import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(
        command="python",
        args=["servers/pdf_server.py"],
    )

    sample_accounts = [
        {
            "name": "Company 01", "region": "AMER",
            "days_inactive": 135, "risk_score": 90,
            "risk_level": "CRITICAL",
            "top_factor": "critical inactivity (>120 days)",
        },
        {
            "name": "Company 02", "region": "AMER",
            "days_inactive": 95, "risk_score": 55,
            "risk_level": "HIGH",
            "top_factor": "moderate inactivity (90-120 days)",
        },
    ]

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "generate_pdf_report",
                {
                    "accounts_json": json.dumps(sample_accounts),
                    "question": "Test: which AMER accounts are at risk?",
                    "output_path": "output/test_report.pdf",
                },
            )

            output_path = result.content[0].text
            print(f"PDF server returned path: {output_path}")

            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"PASSED: file exists, {size} bytes")
            else:
                print("FAILED: file was not actually created")


if __name__ == "__main__":
    asyncio.run(main())