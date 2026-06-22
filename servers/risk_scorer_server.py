# File: servers/risk_scorer_server.py
# PURPOSE: Custom MCP server. Exposes calculate_risk_score tool and a
#          risk-scoring rubric resource.
# CALLED BY: agents/data_agent.py
# HOW IT RUNS: launched as a subprocess by data_agent.py via
#              StdioServerParameters — do NOT run this file directly
#              except for the standalone test below.

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("custom-risk")


@mcp.resource("risk://scoring-rubric")
def get_rubric() -> str:
    """MCP Resource: the risk scoring criteria (readable by the agent)."""
    return (
        "Days inactive > 120 = +40 pts (critical)\n"
        "Days inactive 90-120 = +25 pts (moderate)\n"
        "Health score < 40 = +30 pts (low engagement)\n"
        "Contract ending < 90 days = +30 pts (renewal risk)\n"
        "Web churn signal = +20 pts  |  Max: 100"
    )


@mcp.tool()
def calculate_risk_score(
    days_inactive: int,
    health_score: int,
    days_to_contract_end: int,
    web_signal_detected: bool = False,
) -> dict:
    """
    Calculate churn risk score (0-100) and risk level for one account.
    Called by the Data Agent for each at-risk account it finds.
    """
    score = 0
    factors = []

    if days_inactive > 120:
        score += 40
        factors.append("critical inactivity (>120 days)")
    elif days_inactive > 90:
        score += 25
        factors.append("moderate inactivity (90-120 days)")

    if health_score < 40:
        score += 30
        factors.append("low health score")

    if days_to_contract_end < 90:
        score += 30
        factors.append("contract renewal imminent")

    if web_signal_detected:
        score += 20
        factors.append("churn signal in web search")

    score = min(score, 100)

    if score > 70:
        risk_level = "CRITICAL"
    elif score > 45:
        risk_level = "HIGH"
    else:
        risk_level = "MEDIUM"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "top_factor": factors[0] if factors else "low risk",
        "all_factors": factors,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")