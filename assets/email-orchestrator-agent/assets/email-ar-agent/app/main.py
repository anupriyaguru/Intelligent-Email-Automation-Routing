# CRITICAL: Initialize telemetry BEFORE importing AI frameworks
from sap_cloud_sdk.aicore import set_aicore_config
from sap_cloud_sdk.core.telemetry import auto_instrument

set_aicore_config()
auto_instrument()

import logging
import os

import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from starlette.middleware.base import BaseHTTPMiddleware

from agent_executor import AgentExecutor
from mcp_tools import set_user_token
from opentelemetry.instrumentation.starlette import StarletteInstrumentor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))


class JWTContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        auth_header = request.headers.get("authorization", "")
        token = None
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
        set_user_token(token)
        try:
            response = await call_next(request)
            return response
        finally:
            set_user_token(None)


@click.command()
@click.option("--host", default=HOST)
@click.option("--port", default=PORT)
def main(host: str, port: int):
    skill = AgentSkill(id="email-ar-agent", name="Email AR Agent", description="Accounts Receivable specialist sub-agent. Handles statements, open items, dispute cases, and credit memo requests by retrieving live data from SAP S/4HANA AR APIs.", tags=["ar", "accounts-receivable", "disputes", "credit-memo"], examples=["Get account statement for customer BP-12345", "Create dispute case for invoice INV-98765"])
    agent_card = AgentCard(name="Email AR Agent", description="Accounts Receivable specialist sub-agent. Handles statements, open items, dispute cases, and credit memo requests by retrieving live data from SAP S/4HANA AR APIs.", url=os.environ.get("AGENT_PUBLIC_URL", f"http://{host}:{port}/"), version="1.0.0", default_input_modes=["text"], default_output_modes=["text"], capabilities=AgentCapabilities(streaming=True, push_notifications=False), skills=[skill])
    server = A2AStarletteApplication(agent_card=agent_card, http_handler=DefaultRequestHandler(agent_executor=AgentExecutor(), task_store=InMemoryTaskStore()))
    app = server.build()
    app.add_middleware(JWTContextMiddleware)
    StarletteInstrumentor().instrument_app(app)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
