#!/bin/bash
cd "$(dirname "$0")"

export PYTHONPATH=$(pwd)
export SERVER_NAME=0.0.0.0

echo "Starting Qdrant..."
chmod +x installer_files/qdrant/qdrant
./installer_files/qdrant/qdrant --disable-telemetry > qdrant.log 2>&1 &
QDRANT_PID=$!
echo "Qdrant started with PID $QDRANT_PID"

echo "Waiting for Qdrant to initialize..."
python pq/check_qdrant_up.py

echo "Starting Prompt Quill UI..."
python pq/prompt_quill_ui_qdrant.py
