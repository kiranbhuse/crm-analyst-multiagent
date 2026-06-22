---
title: CRM Analyst Multiagent
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Multi-Agent Salesforce CRM Analyst (MCP-powered)

A Supervisor agent orchestrates 3 specialized sub-agents, all
connected via the Model Context Protocol (MCP):

- **Data Agent** — queries a mock Salesforce database (SQLite MCP
  server) and scores accounts for churn risk (custom Risk Scorer
  MCP server)
- **Research Agent** — runs in parallel across all at-risk accounts,
  searching the web for churn signals (Brave Search MCP server)
- **Report Agent** — generates a formatted PDF risk report (custom
  PDF Generator MCP server)

Ask a business question in plain English (e.g. "Which AMER accounts
had no activity in 90 days and are at risk of churn?") and get back
a downloadable PDF report, fully automated.

## Architecture
User question

|

v

Supervisor Agent

|

+--> Data Agent       --> SQLite MCP + Risk Scorer MCP

|

+--> Research Agent   --> Brave Search MCP (parallel, one

|                         call per at-risk account)

|

+--> Report Agent     --> PDF Generator MCP
## Tech stack

- Anthropic Claude API
- Model Context Protocol (MCP) Python SDK
- Gradio (web UI)
- SQLite (mock CRM data)
- ReportLab (PDF generation)
