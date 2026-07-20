"""Runtime skill loader — exposes a load(path) tool to the agent."""
import logging
from pathlib import Path
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent / "skills"


class LoadSkillInput(BaseModel):
    path: str = Field(description="Relative path to the skill file, e.g. 'email-classification/SKILL.md'")


async def _load_skill(path: str) -> str:
    """Load a runtime skill file by relative path."""
    full_path = SKILLS_DIR / path
    if not full_path.exists():
        return f"Skill file not found: {path}"
    try:
        return full_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading skill file {path}: {e}"


def get_load_skill_resource_tool() -> list:
    """Return the load skill tool as a list for agent tool registration."""
    tool = StructuredTool(
        name="load_skill",
        description="Load a runtime skill file by its relative path (e.g. 'email-classification/SKILL.md'). Use this to read skill instructions, policies, and reference materials.",
        args_schema=LoadSkillInput,
        coroutine=_load_skill,
        handle_tool_error=True,
    )
    return [tool]
