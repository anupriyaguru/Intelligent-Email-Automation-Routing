"""Server tests — verify the A2A server starts and responds."""
import pytest
import httpx


@pytest.mark.server
def test_agent_card_endpoint(start_agent):
    port = start_agent["port"]
    response = httpx.get(f"http://localhost:{port}/.well-known/agent.json", timeout=10)
    assert response.status_code == 200
    card = response.json()
    assert "name" in card
    assert "skills" in card
