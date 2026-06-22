# File: agents/data_agent.py
# PURPOSE: Queries the mock Salesforce database (via the sqlite MCP
#          server) to find at-risk accounts, then scores each one
#          using the custom-risk MCP server.
# CALLED BY: supervisor.py
# NOTE: This file is imported, not run directly.

import json
from datetime import datetime, timedelta

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_data_agent(region: str = "AMER", inactive_days: int = 90) -> list:
    """
    Returns a list of at-risk accounts, each enriched with a risk_score,
    risk_level, and top_factor from the custom-risk MCP server.
    """
    results = []

    # ---- Step 1: connect to the sqlite MCP server, query at-risk accounts ----
    sqlite_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-server-sqlite-npx", "./data/salesforce.db"],
    )

    async with stdio_client(sqlite_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            cutoff = (
                datetime.now() - timedelta(days=inactive_days)
            ).date().isoformat()

            query_result = await session.call_tool(
                "read_query",
                {
                    "query": f"""
                        SELECT
                            id, name, region, arr, health_score,
                            last_activity_date, contract_end, industry,
                            CAST(julianday('now') -
                                 julianday(last_activity_date) AS INTEGER)
                                 AS days_inactive,
                            CAST(julianday(contract_end) -
                                 julianday('now') AS INTEGER)
                                 AS days_to_renewal
                        FROM accounts
                        WHERE region = '{region}'
                        AND last_activity_date < '{cutoff}'
                        ORDER BY health_score ASC
                        LIMIT 20
                    """
                },
            )
            accounts = json.loads(query_result.content[0].text)

    # ---- Step 2: connect to the custom-risk MCP server, score each account ----
    risk_params = StdioServerParameters(
        command="python",
        args=["servers/risk_scorer_server.py"],
    )

    async with stdio_client(risk_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            for account in accounts:
                score_result = await session.call_tool(
                    "calculate_risk_score",
                    {
                        "days_inactive": account["days_inactive"],
                        "health_score": account["health_score"],
                        "days_to_contract_end": account["days_to_renewal"],
                    },
                )
                score = json.loads(score_result.content[0].text)
                account.update(score)
                results.append(account)

    return sorted(results, key=lambda a: -a.get("risk_score", 0))


# Standalone test — lets you verify this agent works in isolation
# before wiring it into the full supervisor pipeline.
if __name__ == "__main__":
    import asyncio

    async def _test():
        accounts = await run_data_agent(region="AMER", inactive_days=90)
        print(f"Found {len(accounts)} at-risk AMER accounts\n")
        for a in accounts[:5]:
            print(f"  {a['name']}: risk_score={a['risk_score']} "
                  f"({a['risk_level']}) - {a['top_factor']}")

    asyncio.run(_test())