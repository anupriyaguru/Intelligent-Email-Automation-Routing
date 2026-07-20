"""Shared test fixtures for email-orchestrator-agent."""
import os
import sys
from pathlib import Path

import pytest

# Ensure app/ is on the Python path
AGENT_DIR = Path(__file__).parent
APP_DIR = AGENT_DIR / "app"
sys.path.insert(0, str(APP_DIR))

# Enable test mode — uses mcp-mock.json instead of live AgentGateway
os.environ.setdefault("IBD_TESTING", "1")


@pytest.fixture(scope="session")
def agent_path() -> Path:
    """Return the root path of the agent directory."""
    return AGENT_DIR


@pytest.fixture
def mock_email_ar():
    return {
        "subject": "Account statement request for Q4",
        "body": "Hello, could you please send me the account statement for Q4 2024? Our account number is BP-12345.",
        "sender_email": "finance@customer.example.com",
    }


@pytest.fixture
def mock_email_ap():
    return {
        "subject": "Invoice INV-98765 payment status",
        "body": "Dear team, we submitted invoice INV-98765 on November 1st for $2,500. Could you confirm the payment date?",
        "sender_email": "ap@vendor.example.com",
    }


@pytest.fixture
def mock_email_dispute():
    return {
        "subject": "Dispute — Invoice INV-11111",
        "body": "We dispute charge on invoice INV-11111 for $350. We never received the goods referenced in this invoice.",
        "sender_email": "billing@customer.example.com",
    }


@pytest.fixture
def mock_email_overdue():
    return {
        "subject": "Re: Overdue balance",
        "body": "We have received your collections letter. We would like to discuss a payment arrangement for our overdue balance of $8,500.",
        "sender_email": "cfo@customer.example.com",
    }
