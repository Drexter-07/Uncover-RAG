#!/bin/bash

# 1. Run the scraper if the data file is missing (Auto-Healing)
if [ ! -f treatments.json ]; then
    echo "⚠️ treatments.json not found. Running scraper..."
    python scraper.py
fi

# 2. Start the Server (Production Mode - No Reload)
echo "🚀 Starting Uvicorn Server..."
uvicorn main:app --host 0.0.0.0 --port 10000