"""Simple test script to send emails to the orchestrator via A2A protocol."""
import asyncio
import httpx
import os

# Enable testing mode to use Mock LLM
os.environ['IBD_TESTING'] = '1'

async def send_email(email_text: str):
    """Send an email to the orchestrator."""

    payload = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "msg-test-001",
                "role": "user",
                "parts": [{"text": email_text}]
            }
        },
        "id": 1
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post("http://localhost:5000/", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.json()

# Test email - high value invoice (should flag for review)
email = """FROM: vendor@supplierco.com
SUBJECT: Dispute Invoice INV-2026-8523
BODY: We are disputing invoice INV-2026-8523 for $15000. The amount is incorrect."""

print("Sending high-value invoice email...")
print("="*80)
result = asyncio.run(send_email(email))
print("="*80)
print("\nNow check the dashboard at http://localhost:5173")
