#  Intelligent Email Automation & Routing

**Multi-Agent AI System for Automated Email Processing and Response Generation**

A production-ready intelligent email automation platform that uses multiple specialized AI agents to process, classify, route, and respond to customer and vendor emails automatically.

---

##  Quick Start - Local Setup

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

##  Setup Instructions

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

##  How to Use the System

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

##  Stopping the Services

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
