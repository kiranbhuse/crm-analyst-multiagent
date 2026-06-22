# File: data/setup_db.py
# PURPOSE: Creates salesforce.db with 3 tables and 50 mock accounts.
# WHERE THIS FILE LIVES: crm-analyst-multiagent/data/setup_db.py
# HOW TO RUN:
#   1. Terminal, from the PROJECT ROOT (crm-analyst-multiagent/), venv active
#   2. python data/setup_db.py
# RUN THIS ONCE — re-running is safe (uses INSERT OR IGNORE)

import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("data/salesforce.db")

conn.executescript("""
    CREATE TABLE IF NOT EXISTS accounts (
        id TEXT PRIMARY KEY,
        name TEXT,
        region TEXT,
        arr INTEGER,
        health_score INTEGER,
        last_activity_date DATE,
        contract_end DATE,
        industry TEXT,
        owner TEXT
    );
    CREATE TABLE IF NOT EXISTS activities (
        account_id TEXT,
        type TEXT,
        activity_date DATE,
        notes TEXT
    );
    CREATE TABLE IF NOT EXISTS agent_runs (
        ts TEXT,
        question TEXT,
        accounts_found INTEGER,
        total_latency_ms INTEGER,
        github_url TEXT
    );
""")

random.seed(42)  # reproducible data across re-runs
regions = ["AMER", "AMER", "EMEA", "APAC"]  # weighted toward AMER for the demo
industries = ["Technology", "Retail", "Finance", "Healthcare", "Manufacturing"]

for i in range(50):
    days_back = random.randint(20, 200)
    last_act = datetime.now() - timedelta(days=days_back)
    contract_end = datetime.now() + timedelta(days=random.randint(30, 400))

    conn.execute(
        "INSERT OR IGNORE INTO accounts VALUES (?,?,?,?,?,?,?,?,?)",
        [
            f"ACC{i:03d}",
            f"Company {i:02d}",
            random.choice(regions),
            random.randint(50000, 500000),
            random.randint(20, 95),
            last_act.date().isoformat(),
            contract_end.date().isoformat(),
            random.choice(industries),
            f"Rep {i % 5}",
        ],
    )

conn.commit()
conn.close()

print("Done: 50 accounts created in data/salesforce.db")