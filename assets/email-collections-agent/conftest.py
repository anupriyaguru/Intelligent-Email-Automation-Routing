"""Shared test fixtures for email-collections-agent."""
import os
import sys
from pathlib import Path

import pytest

AGENT_DIR = Path(__file__).parent
APP_DIR = AGENT_DIR / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("IBD_TESTING", "1")


@pytest.fixture(scope="session")
def agent_path() -> Path:
    return AGENT_DIR
