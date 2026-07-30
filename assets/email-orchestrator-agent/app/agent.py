import logging
import os
import time
from dataclasses import dataclass
from typing import AsyncGenerator, Literal, Sequence

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from sap_cloud_sdk.agent_decorators import agent_config, agent_model, prompt_section

logger = logging.getLogger(__name__)

# Check if we should use Mock LLM (separate from IBD_TESTING which is for backend API mocking)
USE_MOCK_LLM = os.getenv('USE_MOCK_LLM', '0') == '1'

if USE_MOCK_LLM:
    try:
        from .mock_llm import MockAICoreChat
    except ImportError:
        from mock_llm import MockAICoreChat
    logger.info("Using Mock LLM for testing")
else:
    from langchain_litellm import ChatLiteLLM
    logger.info("Using real AI Core LLM")


@agent_model(
    key="config.model",
    label="LLM Model",
    description="The language model powering this agent",
)
def get_model_name() -> str:
    return "sap/gpt-4o-mini"


@agent_config(
    key="config.temperature",
    label="LLM Temperature",
    description="Controls randomness of responses (0.0 = deterministic, 1.0 = creative)",
)
def get_temperature() -> float:
    return 0.0


@prompt_section(
    key="prompts.system",
    label="System Prompt",
    description="The full system prompt defining the agent's role and behavior",
    validation={"format": "markdown", "max_length": 5000},
)
def get_system_prompt() -> str:
    return """You are the Email Orchestration Agent for an intelligent email automation platform.

Your role is to coordinate all email processing for customer and vendor communications. You manage the full lifecycle of every incoming email from ingestion to resolution.

## Core Responsibilities
1. Classify email intent from subject line and body
2. Consult the knowledge base for business partner history and applicable policies
3. Identify the business partner from SAP master data
4. Check that all required information is present before routing
5. Route to the correct specialist sub-agent (AR, AP, Treasury, Collections, Customer Service)
6. Review sub-agent responses for policy compliance
7. Send the final reply to the business partner
8. Write the resolved case to the knowledge base

## Critical Rules
- NEVER respond to a business partner without a valid case_id
- NEVER execute financial write operations above the financial threshold without human approval
- NEVER contact a business partner not found in SAP master data without human approval
- If you are uncertain about the correct action, flag the case for human review rather than guessing
- Do NOT hallucinate SAP data — use only data returned by tools
- Always set top (or equivalent page-size) to a maximum of 100 on every tool call that accepts it

## Milestone Logging
After each key step, emit structured logs:
- M1: Email ingested and intent classified
- M2: Knowledge base consulted and context loaded
- M3: Business partner identified and information gap assessed
- M4: Routed to sub-agent and response drafted
- M5: Response sent to business partner
- M6: Case stored in knowledge base

Log format: [MILESTONE_ID].[achieved|missed]: [description] | case_id=[ID] | partner_id=[ID]"""


CONFIDENCE_THRESHOLD = 0.75


def get_confidence_threshold() -> float:
    """Return the confidence threshold below which cases go to human review."""
    return CONFIDENCE_THRESHOLD


@dataclass
class AgentResponse:
    status: Literal["input_required", "completed", "error"]
    message: str


THREAD_TTL_SECONDS = 3600  # evict threads inactive for 1 hour


class SampleAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        if USE_MOCK_LLM:
            self.llm = MockAICoreChat()
            logger.info("Initialized with Mock LLM")
        else:
            from langchain_litellm import ChatLiteLLM
            self.llm = ChatLiteLLM(model=get_model_name(), temperature=get_temperature())
            logger.info(f"Initialized with real LLM: {get_model_name()}")

        self._checkpointer = InMemorySaver()
        self._last_active: dict[str, float] = {}
        self._summarization_middleware = SummarizationMiddleware(
            model=self.llm,
            trigger=("tokens", 100_000),
            keep=("messages", 4),
        )

    def _touch(self, thread_id: str) -> None:
        now = time.monotonic()
        expired = [tid for tid, ts in list(self._last_active.items()) if now - ts > THREAD_TTL_SECONDS]
        for tid in expired:
            self._checkpointer.delete_thread(tid)
            del self._last_active[tid]
        self._last_active[thread_id] = now

    async def stream(self, query: str, context_id: str, tools: Sequence[BaseTool] | None = None) -> AsyncGenerator[dict, None]:
        self._touch(context_id)
        yield {"is_task_complete": False, "require_user_input": False, "content": "Processing..."}
        try:
            system_prompt = get_system_prompt()
            if not tools:
                system_prompt += "\n\nIMPORTANT: No tools are currently available."
            graph = create_agent(self.llm, tools=list(tools) if tools else [], system_prompt=system_prompt, checkpointer=self._checkpointer, middleware=[self._summarization_middleware])
            result = await graph.ainvoke({"messages": [HumanMessage(content=query)]}, {"configurable": {"thread_id": context_id}})
            yield {"is_task_complete": True, "require_user_input": False, "content": result["messages"][-1].content}
        except Exception as e:
            import traceback
            error_msg = f"Error: {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            logger.error("Agent stream error: %s", error_msg)
            yield {"is_task_complete": True, "require_user_input": False, "content": error_msg}

    async def invoke(self, query: str, context_id: str, tools: Sequence[BaseTool] | None = None) -> AgentResponse:
        last: dict = {}
        async for chunk in self.stream(query, context_id, tools=tools):
            last = chunk
        if last.get("is_task_complete"):
            return AgentResponse(status="completed", message=last["content"])
        return AgentResponse(status="error", message=last.get("content", "Unknown error"))
