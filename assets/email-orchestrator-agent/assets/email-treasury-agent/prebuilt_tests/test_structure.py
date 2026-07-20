"""Structure tests — verify required files and modules exist."""
import pytest
from pathlib import Path


@pytest.mark.structure
def test_app_directory_exists(agent_path):
    assert (agent_path / "app").is_dir(), "app/ directory must exist"


@pytest.mark.structure
def test_main_py_exists(agent_path):
    assert (agent_path / "app" / "main.py").exists(), "app/main.py must exist"


@pytest.mark.structure
def test_agent_py_exists(agent_path):
    assert (agent_path / "app" / "agent.py").exists(), "app/agent.py must exist"


@pytest.mark.structure
def test_mcp_tools_py_exists(agent_path):
    assert (agent_path / "app" / "mcp_tools.py").exists(), "app/mcp_tools.py must exist"


@pytest.mark.structure
def test_requirements_txt_exists(agent_path):
    assert (agent_path / "requirements.txt").exists(), "requirements.txt must exist"


@pytest.mark.structure
def test_skills_directory_exists(agent_path):
    assert (agent_path / "app" / "skills").is_dir(), "app/skills/ directory must exist"
