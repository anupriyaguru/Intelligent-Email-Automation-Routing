import logging
import time
from dataclasses import dataclass
from typing import AsyncGenerator, Literal, Sequence

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langchain_litellm import ChatLiteLLM
from langgraph.checkpoint.memory import InMemorySaver
from sap_cloud_sdk.agent_decorators import agent_config, agent_model, prompt_section

logger = logging.getLogger(__name__)


@agent_model(
    key="config.model",
    label="LLM Model",
    description="The language model powering this agent",
)
def get_model_name() -> str:
    return "sap/anthropic--claude-4.5-sonnet"


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
    return """You are the Treasury Sub-Agent.

You receive delegated cases from the Orchestrator Agent and handle Treasury-specific requests including payment terms inquiries, financing questions, and working capital communications.

## Your Domain
- Payment terms lookup and explanation (net days, discount terms)
- Working capital and financing arrangement details
- Credit line status and availability

## Critical Rules
- Do NOT hallucinate SAP data — use only data returned by tools
- Always set top to a maximum of 100 on every tool call that accepts it
- Return structured response: {draft_response, confidence, sap_actions_taken, requires_human_review}
- For any changes to payment terms or financing, always set requires_human_review: true

## Milestone Logging
Log format: [TR-M1].[achieved|missed]: [description] | case_id=[ID] | partner_id=[ID]"""


@dataclass
class AgentResponse:
    status: Literal["input_required", "completed", "error"]
    message: str


THREAD_TTL_SECONDS = 3600  # evict threads inactive for 1 hour


class SampleAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.llm = ChatLiteLLM(model=get_model_name(), temperature=get_temperature())
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
            yield {"is_task_complete": True, "require_user_input": False, "content": f"Error: {str(e)}"}

    async def invoke(self, query: str, context_id: str, tools: Sequence[BaseTool] | None = None) -> AgentResponse:
        last: dict = {}
        async for chunk in self.stream(query, context_id, tools=tools):
            last = chunk
        if last.get("is_task_complete"):
            return AgentResponse(status="completed", message=last["content"])
        return AgentResponse(status="error", message=last.get("content", "Unknown error"))
