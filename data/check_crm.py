# File: check_db.py
# PURPOSE: Quick inspection script for the mock Salesforce database.
# WHERE THIS FILE LIVES: crm-analyst-multiagent/check_db.py
# HOW TO RUN: python check_db.py

import sqlite3

conn = sqlite3.connect("data/salesforce.db")

print("=== Tables ===")
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()
for t in tables:
    print(f"  - {t[0]}")

print("\n=== Account count by region ===")
rows = conn.execute(
    "SELECT region, COUNT(*) FROM accounts GROUP BY region"
).fetchall()
for region, count in rows:
    print(f"  {region}: {count} accounts")

print("\n=== Sample: 5 AMER accounts ===")
rows = conn.execute(
    "SELECT name, region, health_score, last_activity_date "
    "FROM accounts WHERE region='AMER' LIMIT 5"
).fetchall()
for row in rows:
    print(f"  {row}")

conn.close()