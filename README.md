# 📧 Intelligent Email Automation & Routing

**Multi-Agent AI System for Automated Email Processing and Response Generation**

A production-ready intelligent email automation platform that uses multiple specialized AI agents to process, classify, route, and respond to customer and vendor emails automatically.

---

## 🚀 Quick Start - Local Setup

### Prerequisites

Before you begin, ensure you have the following installed:

1. **Node.js** (version 14 or higher)
   - Download from: https://nodejs.org/
   - Choose the **LTS (Long Term Support)** version
   - Install with default settings
   - After installation, restart your computer

2. **Python** (version 3.9 or higher)
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify installation: Open command prompt and type `python --version`

3. **Python Dependencies**
   - Open command prompt in the project root directory
   - Run: `pip install -r requirements.txt` (if requirements.txt exists)
   - Or install manually: `pip install langchain langgraph fastapi uvicorn pydantic opentelemetry-api`

---

## 📋 Setup Instructions

### Step 1: Start All Agents

Open a command prompt and navigate to the project directory, then run:

```bash
start_agents.bat
```

**What this does:**
- Starts the **Orchestrator Agent** on port 5000
- Starts **5 Sub-Agents** (AR, AP, Treasury, Collections, CS) on ports 5001-5005
- Starts the **Review Dashboard** on port 4004
- All services run in background
- Creates logs in the `logs/` directory

**Expected output:**
```
Starting Email Orchestration Multi-Agent System
================================================

Starting agents...

1. Starting Orchestrator Agent on port 5000...
2. Starting AR Sub-Agent on port 5001...
3. Starting AP Sub-Agent on port 5002...
4. Starting Treasury Sub-Agent on port 5003...
5. Starting Collections Sub-Agent on port 5004...
6. Starting CS Sub-Agent on port 5005...
7. Starting Review Dashboard on port 4004...

================================================
Service Status
================================================
✓ Orchestrator Agent (5000): UP
✓ AR Agent (5001): UP
✓ AP Agent (5002): UP
✓ Treasury Agent (5003): UP
✓ Collections Agent (5004): UP
✓ CS Agent (5005): UP
✓ Review Dashboard (4004): UP
================================================
All services started!
```

**Wait 10-15 seconds** for all services to fully start.

---

### Step 2: Start Dashboard (Alternative)

If you only want to run the Review Dashboard without all agents:

```bash
start_dashboard.bat
```

**What this does:**
- Checks Node.js installation
- Installs Express dependencies (first run only)
- Starts the Review Dashboard on port 4004
- Keeps window open to show server logs

**Expected output:**
```
================================================
Email Review Dashboard Setup and Start
================================================

[1/4] Checking Node.js installation...
[OK] Node.js detected:
v18.17.0
[OK] npm version:
9.6.7

[2/4] Checking dashboard directory...
[OK] Dashboard directory found

[3/4] Checking dependencies...
[OK] Dependencies already installed

[4/4] Starting Dashboard Server...
================================================

Dashboard Server Starting on port 4004...

Once started, access the dashboard at:
  http://localhost:4004

========================================
  Email Review Dashboard - Running
========================================
  Server:  http://localhost:4004
  API:     http://localhost:4004/api/review/
========================================
```

---

### Step 3: Open the Demo UI

1. Navigate to the project root directory
2. Find the file: `bp_inquiry_automation.html`
3. **Double-click** the file to open in your default browser

**OR**

Right-click → Open with → Choose your browser (Chrome, Edge, Firefox)

**What you'll see:**
- SAP Fiori-style interface
- Email submission form
- Real-time agent processing timeline
- Milestone tracking (M1-M6)
- Agent workflow visualization

---

### Step 4: Access the Review Dashboard

Open your web browser and go to:

```
http://localhost:4004
```

**What you'll see:**
- List of all flagged cases pending human review
- Case details (sender, subject, intent, confidence score)
- AI-generated draft responses
- Approve/Reject/Edit actions
- Case resolution tracking

---

## 🎯 How to Use the System

### **Option A: Using the Demo UI** (`bp_inquiry_automation.html`)

1. **Open the HTML file** in your browser
2. **Fill in the email form:**
   - **From Email**: Enter sender's email (e.g., `john.doe@acme.com`)
   - **Subject**: Email subject line (e.g., `Payment status inquiry`)
   - **Body**: Email content (e.g., `Can you tell me the status of my invoice #12345?`)
3. **Click "Process Email"**
4. **Watch the workflow:**
   - M1: Email ingested and classified
   - M2: Knowledge base queried
   - M3: Business partner identified
   - M4: Routed to sub-agent
   - M5: Response sent
   - M6: Case stored in KB

### **Option B: Using API Directly**

Send a POST request to the Orchestrator Agent:

```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "sender_email": "john.doe@acme.com",
    "subject": "Invoice payment status",
    "body": "Can you check the status of invoice #12345?"
  }'
```

### **Option C: Review Dashboard**

1. Open `http://localhost:4004` in browser
2. Browse flagged cases
3. Click on a case to view details
4. Review AI-generated response
5. **Approve** (sends response) or **Reject** (escalate)
6. Optionally edit the draft before approving

---

## 🛑 Stopping the Services

### Stop All Agents

```bash
stop_agents.bat
```

**What this does:**
- Kills all agent processes (ports 5000-5005)
- Kills the dashboard process (port 4004)
- Cleans up background processes

### Stop Dashboard Only

Press `Ctrl+C` in the dashboard command window, or simply close the window.

---

## 📂 Project Structure

```
Intelligent Email Automation & Routing/
├── start_agents.bat              # Start all services
├── start_dashboard.bat            # Start dashboard only
├── stop_agents.bat                # Stop all services
├── bp_inquiry_automation.html     # Demo UI
├── README.md                      # This file
│
├── assets/
│   ├── email-orchestrator-agent/  # Main coordinator (Port 5000)
│   ├── email-ar-agent/            # AR specialist (Port 5001)
│   ├── email-ap-agent/            # AP specialist (Port 5002)
│   ├── email-treasury-agent/      # Treasury specialist (Port 5003)
│   ├── email-collections-agent/   # Collections specialist (Port 5004)
│   ├── email-cs-agent/            # CS specialist (Port 5005)
│   └── email-review-dashboard-cap/# Review dashboard (Port 4004)
│
└── logs/                          # Service logs (auto-created)
    ├── orchestrator.log
    ├── ar-agent.log
    ├── ap-agent.log
    ├── treasury-agent.log
    ├── collections-agent.log
    ├── cs-agent.log
    └── dashboard.log
```

---

## 🔍 Troubleshooting

### Problem: "Node.js is not installed"

**Solution:**
1. Download Node.js from https://nodejs.org/
2. Install with default settings
3. Restart your computer
4. Run `start_dashboard.bat` again

---

### Problem: "Python is not installed" or "python not recognized"

**Solution:**
1. Download Python from https://www.python.org/downloads/
2. During installation, **check "Add Python to PATH"**
3. Restart your computer
4. Verify: Open command prompt, type `python --version`

---

### Problem: Port already in use

**Error message:** `Address already in use` or `Port 5000 is already allocated`

**Solution:**
1. Run `stop_agents.bat` to clean up
2. Close any applications using ports 4004, 5000-5005
3. Run `start_agents.bat` again

**Manual cleanup (Windows):**
```bash
# Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

---

### Problem: Dashboard shows blank page

**Solution:**
1. Check if server is running: `http://localhost:4004/api/review/ReviewCases`
2. If you see JSON data, the server is working
3. Clear browser cache (Ctrl+Shift+Delete)
4. Try a different browser

---

### Problem: Agents not responding

**Solution:**
1. Check logs in `logs/` directory
2. Look for error messages
3. Ensure all dependencies are installed
4. Restart all services: `stop_agents.bat` then `start_agents.bat`

---

### Problem: Demo UI not loading emails

**Solution:**
1. Ensure `start_agents.bat` is running (all 7 services)
2. Check browser console for errors (F12 → Console tab)
3. Verify orchestrator is running: `http://localhost:5000/.well-known/agent.json`
4. Check if testing mode is enabled: Look for `IBD_TESTING=1` in `start_agents.bat`

---

## 🎓 Understanding the System

### **The 7 Services**

| Service | Port | Purpose |
|---------|------|---------|
| **Orchestrator Agent** | 5000 | Coordinates entire workflow, routes to specialists |
| **AR Sub-Agent** | 5001 | Handles Accounts Receivable (invoices, payments) |
| **AP Sub-Agent** | 5002 | Handles Accounts Payable (vendor invoices, POs) |
| **Treasury Sub-Agent** | 5003 | Handles Treasury & banking operations |
| **Collections Sub-Agent** | 5004 | Handles Collections & overdue payments |
| **CS Sub-Agent** | 5005 | Handles Customer Service inquiries |
| **Review Dashboard** | 4004 | Human review interface for flagged cases |

### **Workflow Steps**

1. **Email Ingestion** → Orchestrator receives email
2. **Intent Classification** → AI classifies email category
3. **BP Identification** → Looks up sender in SAP master data
4. **Knowledge Base Query** → Retrieves context and history
5. **Completeness Check** → Validates required information
6. **Routing** → Delegates to appropriate sub-agent
7. **Response Generation** → Sub-agent drafts response
8. **Review Decision** → Auto-send or flag for human review
9. **Email Dispatch** → Sends response to sender
10. **KB Update** → Stores case for future learning

### **When Cases Are Flagged for Review**

- Confidence score < 75%
- Financial action > $5,000
- Unknown business partner
- Legal hold on account
- Sub-agent failure

---

## 📊 API Endpoints

### Orchestrator Agent (Port 5000)
```
POST /process                      # Process incoming email
GET  /.well-known/agent.json       # Agent metadata
GET  /health                        # Health check
```

### Review Dashboard (Port 4004)
```
GET    /api/review/ReviewCases              # List all cases
POST   /api/review/ReviewCases              # Create new case
GET    /api/review/ReviewCases/:id          # Get case details
PATCH  /api/review/ReviewCases/:id          # Update case
POST   /api/review/ReviewCases/:id/approveCase  # Approve case
POST   /api/review/ReviewCases/:id/rejectCase   # Reject case
```

---

## 🔐 Configuration

### Environment Variables

Set in `start_agents.bat`:

```bash
set IBD_TESTING=1           # Enable mock mode (no real SAP calls)
set USE_MOCK_LLM=0          # Use real LLM (0) or mock LLM (1)
```

### Financial Threshold

Edit in `assets/email-orchestrator-agent/app/tools.py`:

```python
FINANCIAL_ACTION_THRESHOLD = 5000.00  # Adjust as needed
```

### Confidence Threshold

Edit in `assets/email-orchestrator-agent/app/agent.py`:

```python
CONFIDENCE_THRESHOLD = 0.75  # Adjust as needed (0.0 - 1.0)
```

---

## 📞 Support

### Checking Logs

All service logs are stored in the `logs/` directory:

```bash
# View orchestrator logs
type logs\orchestrator.log

# View dashboard logs
type logs\dashboard.log
```

### Common Issues

1. **Port conflicts**: Use `stop_agents.bat` to clean up
2. **Missing dependencies**: Run `npm install` in dashboard directory
3. **Python errors**: Check Python version and dependencies
4. **Connection refused**: Ensure services are running (`start_agents.bat`)

---

## 🎉 Success Indicators

You know the system is working when:

✅ All 7 services show "UP" status after running `start_agents.bat`  
✅ Demo UI loads and shows the email form  
✅ Dashboard loads at `http://localhost:4004`  
✅ Submitting an email in the UI shows the workflow timeline  
✅ Logs appear in the `logs/` directory  

---

## 📚 Additional Resources

- **Dashboard README**: `assets/email-review-dashboard-cap/README.md`
- **Agent Specifications**: `specification/` directory
- **Test Files**: Each agent has a `tests/` directory

---

## 🏁 Next Steps

Once the system is running:

1. **Try different email scenarios** (payment inquiry, invoice request, etc.)
2. **Watch the agent workflow** in the demo UI
3. **Review flagged cases** in the dashboard
4. **Check the logs** to understand agent decisions
5. **Experiment with different intents** to see routing behavior

---

**Enjoy your intelligent email automation system!** 🚀

---

*For technical details and architecture overview, see the inline documentation in each agent's `app/` directory.*
