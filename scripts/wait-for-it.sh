#!/usr/bin/env bash
# Minimal wait-for-it: wait until a TCP host:port accepts connections.
# Usage: wait-for-it.sh host port [timeout_seconds]
HOST=$1
PORT=$2
TIMEOUT=${3:-60}

echo "Waiting for $HOST:$PORT (timeout ${TIMEOUT}s)..."
for i in $(seq 1 "$TIMEOUT"); do
    if nc -z "$HOST" "$PORT" 2>/dev/null; then
        echo "$HOST:$PORT is available after ${i}s"
        exit 0
    fi
    sleep 1
done
echo "ERROR: $HOST:$PORT not available after ${TIMEOUT}s" >&2
exit 1
