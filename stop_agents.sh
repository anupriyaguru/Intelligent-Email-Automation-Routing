#!/bin/bash

# Stop all agent processes

echo "Stopping all agents..."

if [ -f .agent_pids ]; then
    PIDS=$(cat .agent_pids)
    for PID in $PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping process $PID"
            kill $PID 2>/dev/null
        fi
    done
    rm -f .agent_pids
    echo "All agents stopped."
else
    echo "No .agent_pids file found. Cleaning up ports..."
    lsof -ti:5000 | xargs kill -9 2>/dev/null || true
    lsof -ti:5001 | xargs kill -9 2>/dev/null || true
    lsof -ti:5002 | xargs kill -9 2>/dev/null || true
    lsof -ti:5003 | xargs kill -9 2>/dev/null || true
    lsof -ti:5004 | xargs kill -9 2>/dev/null || true
    lsof -ti:5005 | xargs kill -9 2>/dev/null || true
    lsof -ti:4004 | xargs kill -9 2>/dev/null || true
    echo "Ports cleaned up."
fi
