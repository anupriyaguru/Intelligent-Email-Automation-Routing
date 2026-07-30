#!/bin/bash

# Start all agents for end-to-end testing
# This script starts all 6 agents and the review dashboard in separate background processes

echo "Starting Email Orchestration Multi-Agent System"
echo "================================================"
echo ""

# Kill any existing processes on these ports
echo "Cleaning up existing processes..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:5002 | xargs kill -9 2>/dev/null || true
lsof -ti:5003 | xargs kill -9 2>/dev/null || true
lsof -ti:5004 | xargs kill -9 2>/dev/null || true
lsof -ti:5005 | xargs kill -9 2>/dev/null || true
lsof -ti:4004 | xargs kill -9 2>/dev/null || true

# Create logs directory
mkdir -p logs

# Export environment for testing
export IBD_TESTING=1

echo "Starting agents..."
echo ""

# Start Orchestrator Agent
echo "1. Starting Orchestrator Agent on port 5000..."
cd assets/email-orchestrator-agent
python app/main.py --port 5000 > ../../logs/orchestrator.log 2>&1 &
ORCH_PID=$!
echo "   PID: $ORCH_PID"
cd ../..

sleep 2

# Start AR Sub-Agent
echo "2. Starting AR Sub-Agent on port 5001..."
cd assets/email-ar-agent
python app/main.py --port 5001 > ../../logs/ar-agent.log 2>&1 &
AR_PID=$!
echo "   PID: $AR_PID"
cd ../..

sleep 1

# Start AP Sub-Agent
echo "3. Starting AP Sub-Agent on port 5002..."
cd assets/email-ap-agent
python app/main.py --port 5002 > ../../logs/ap-agent.log 2>&1 &
AP_PID=$!
echo "   PID: $AP_PID"
cd ../..

sleep 1

# Start Treasury Sub-Agent
echo "4. Starting Treasury Sub-Agent on port 5003..."
cd assets/email-treasury-agent
python app/main.py --port 5003 > ../../logs/treasury-agent.log 2>&1 &
TREASURY_PID=$!
echo "   PID: $TREASURY_PID"
cd ../..

sleep 1

# Start Collections Sub-Agent
echo "5. Starting Collections Sub-Agent on port 5004..."
cd assets/email-collections-agent
python app/main.py --port 5004 > ../../logs/collections-agent.log 2>&1 &
COLLECTIONS_PID=$!
echo "   PID: $COLLECTIONS_PID"
cd ../..

sleep 1

# Start CS Sub-Agent
echo "6. Starting CS Sub-Agent on port 5005..."
cd assets/email-cs-agent
python app/main.py --port 5005 > ../../logs/cs-agent.log 2>&1 &
CS_PID=$!
echo "   PID: $CS_PID"
cd ../..

sleep 1

# Start Review Dashboard
echo "7. Starting Review Dashboard on port 4004..."
cd assets/email-review-dashboard-cap
npm install --silent
cds watch > ../../logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "   PID: $DASHBOARD_PID"
cd ../..

echo ""
echo "Waiting for services to start..."
sleep 5

echo ""
echo "================================================"
echo "Service Status"
echo "================================================"

# Check each service
check_service() {
    local url=$1
    local name=$2
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|401"; then
        echo "✓ $name: UP"
    else
        echo "✗ $name: DOWN"
    fi
}

check_service "http://localhost:5000/.well-known/agent.json" "Orchestrator Agent (5000)"
check_service "http://localhost:5001/.well-known/agent.json" "AR Agent (5001)"
check_service "http://localhost:5002/.well-known/agent.json" "AP Agent (5002)"
check_service "http://localhost:5003/.well-known/agent.json" "Treasury Agent (5003)"
check_service "http://localhost:5004/.well-known/agent.json" "Collections Agent (5004)"
check_service "http://localhost:5005/.well-known/agent.json" "CS Agent (5005)"
check_service "http://localhost:4004/odata/v4/review/ReviewCases" "Review Dashboard (4004)"

echo ""
echo "================================================"
echo "All services started!"
echo "================================================"
echo ""
echo "Process IDs:"
echo "  Orchestrator:  $ORCH_PID"
echo "  AR Agent:      $AR_PID"
echo "  AP Agent:      $AP_PID"
echo "  Treasury:      $TREASURY_PID"
echo "  Collections:   $COLLECTIONS_PID"
echo "  CS Agent:      $CS_PID"
echo "  Dashboard:     $DASHBOARD_PID"
echo ""
echo "Logs available in ./logs/ directory"
echo ""
echo "To run end-to-end test:"
echo "  python test_e2e_workflow.py"
echo ""
echo "To stop all services:"
echo "  ./stop_agents.sh"
echo ""
echo "Press Ctrl+C to stop all services..."

# Save PIDs to file for cleanup
echo "$ORCH_PID $AR_PID $AP_PID $TREASURY_PID $COLLECTIONS_PID $CS_PID $DASHBOARD_PID" > .agent_pids

# Wait for user interrupt
trap "echo ''; echo 'Stopping all services...'; kill $ORCH_PID $AR_PID $AP_PID $TREASURY_PID $COLLECTIONS_PID $CS_PID $DASHBOARD_PID 2>/dev/null; rm -f .agent_pids; echo 'All services stopped.'; exit 0" INT

# Keep script running
wait
