# File: Dockerfile
# PURPOSE: Custom container for HF Spaces. Installs Node.js and
#          pre-installs the MCP npm servers globally so npx finds
#          them instantly instead of reinstalling (and printing noisy
#          install logs to stdout) on every agent run.
# WHERE THIS RUNS: Hugging Face Spaces build step

FROM python:3.13-slim

# Install Node.js (needed for npx-based MCP servers)
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Pre-install MCP npm servers GLOBALLY.
# NOTE: mcp-server-sqlite-npx is the correct package name —
# @modelcontextprotocol/server-sqlite does NOT exist on npm.
RUN npm install -g \
    @modelcontextprotocol/server-brave-search \
    mcp-server-sqlite-npx

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make sure folders the agents depend on exist at runtime,
# and seed the mock Salesforce database during the build.
RUN mkdir -p /app/output /app/data /app/servers /app/agents && \
    python data/setup_db.py

EXPOSE 7860

CMD ["python", "app.py"]