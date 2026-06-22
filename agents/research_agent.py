# File: agents/research_agent.py
# PURPOSE: Enriches ONE account with web-based churn signals via the
#          brave-search MCP server. Called once per account, in
#          parallel, by the Supervisor.
# CALLED BY: supervisor.py
# NOTE: This file is imported, not run directly (except for the
#       standalone test at the bottom).

import os

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

CHURN_KEYWORDS = [
    "layoff", "layoffs", "cut", "cuts", "downsize", "downsizing",
    "freeze", "churn", "resign", "resignation", "bankruptcy",
    "restructuring", "acquired", "acquisition",
]


async def run_research_agent(account: dict) -> dict:
    """
    Search the web for churn-risk signals for one account.
    Returns {"web_signal": str, "web_signal_detected": bool}
    """
    company = account["name"]

    brave_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env={**os.environ},
    )

    try:
        async with stdio_client(brave_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "brave_web_search",
                    {
                        "query": f"{company} layoffs budget cuts "
                                 f"restructuring news",
                        "count": 3,
                    },
                )
                snippets = (
                    result.content[0].text if result.content else ""
                )

                has_signal = any(
                    keyword in snippets.lower()
                    for keyword in CHURN_KEYWORDS
                )

                return {
                    "web_signal": (
                        snippets[:200] if has_signal
                        else "No churn signals found"
                    ),
                    "web_signal_detected": has_signal,
                }
    except Exception as e:
        # Don't let one failed search take down the whole pipeline —
        # return a clearly-flagged neutral result instead.
        return {
            "web_signal": f"Research failed: {e}",
            "web_signal_detected": False,
        }


# Standalone test
if __name__ == "__main__":
    import asyncio

    async def _test():
        fake_account = {"name": "Salesforce"}
        result = await run_research_agent(fake_account)
        print(f"Result for {fake_account['name']}:")
        print(f"  web_signal_detected: {result['web_signal_detected']}")
        print(f"  web_signal: {result['web_signal']}")

    asyncio.run(_test())