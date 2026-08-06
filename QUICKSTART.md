#  Quick Start Guide

**Get the Email Automation System running in 3 minutes!**

---

## ✅ Prerequisites

1. **Node.js** - Download from https://nodejs.org/ (LTS version)
2. **Python 3.9+** - Download from https://www.python.org/

After installation, **restart your computer**.

---

##  3 Simple Steps

### Step 1: Start All Agents

Open Command Prompt in the project folder and run:

```bash
start_agents.bat
```

Wait for all services to show **"UP"** status (10-15 seconds).

---

### Step 2: Open the Demo UI

Double-click the file:

```
bp_inquiry_automation.html
```

It will open in your browser.

---

### Step 3: Try It Out!

**In the Demo UI:**

1. Fill in the form:
   - **From Email**: `john.doe@acme.com`
   - **Subject**: `Payment status inquiry`
   - **Body**: `What is the status of invoice #12345?`

2. Click **"Process Email"**

3. Watch the AI agents process the email in real-time!

---

##  Access the Dashboard

Open your browser and go to:

```
http://localhost:4004
```

View and approve/reject AI-generated responses.

---

##  Stop Everything

```bash
stop_agents.bat
```

---

##  Troubleshooting

**Services won't start?**
- Make sure Node.js and Python are installed
- Restart your computer after installation
- Run `stop_agents.bat` then try again

**Dashboard not loading?**
- Check if port 4004 is available
- Try: `http://localhost:4004/api/review/ReviewCases`
- Should see JSON data

**Demo UI not working?**
- Make sure `start_agents.bat` is running
- All 7 services must show "UP" status
- Check browser console (F12) for errors

---

##  What's Running?

| Service | Port | What It Does |
|---------|------|-------------|
| Orchestrator | 5000 | Main coordinator |
| AR Agent | 5001 | Accounts Receivable |
| AP Agent | 5002 | Accounts Payable |
| Treasury Agent | 5003 | Banking operations |
| Collections Agent | 5004 | Overdue payments |
| CS Agent | 5005 | Customer Service |
| Dashboard | 4004 | Human review interface |

---

