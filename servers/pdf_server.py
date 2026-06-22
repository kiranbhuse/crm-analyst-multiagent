# File: servers/pdf_server.py
# PURPOSE: Custom MCP server. Exposes generate_pdf_report tool.
# CALLED BY: agents/report_agent.py
# HOW IT RUNS: launched as a subprocess by report_agent.py via
#              StdioServerParameters — do NOT run this file directly
#              except for the standalone test below.

import json

from mcp.server.fastmcp import FastMCP
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

mcp = FastMCP("custom-pdf")
styles = getSampleStyleSheet()


@mcp.tool()
def generate_pdf_report(
    accounts_json: str,
    question: str,
    output_path: str = "output/churn_report.pdf",
) -> str:
    """
    Generate a formatted PDF churn risk report from JSON account data.
    accounts_json: JSON string of the account list, as produced by
                   the Data Agent (with risk_score, risk_level, etc.
                   already attached to each account).
    Returns: the output_path where the PDF was saved.
    """
    accounts = json.loads(accounts_json)

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = [
        Paragraph("Salesforce CRM Churn Risk Report", styles["Title"]),
        Paragraph(f"Query: {question}", styles["Normal"]),
        Spacer(1, 12),
    ]

    headers = [
        "Account", "Region", "Days Inactive",
        "Risk Score", "Risk Level", "Top Factor",
    ]
    rows = [headers] + [
        [
            account.get("name", ""),
            account.get("region", ""),
            str(account.get("days_inactive", "")),
            str(account.get("risk_score", "")),
            account.get("risk_level", ""),
            str(account.get("top_factor", ""))[:45],
        ]
        for account in accounts[:15]
    ]

    table = Table(rows, colWidths=[1.2 * 72, 0.7 * 72, 0.9 * 72,
                                    0.8 * 72, 0.8 * 72, 2.1 * 72])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#534AB7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F1EFE8")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    story.append(table)
    doc.build(story)

    return output_path


if __name__ == "__main__":
    mcp.run(transport="stdio")