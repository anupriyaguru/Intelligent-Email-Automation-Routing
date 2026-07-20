"""AP Agent tools — Accounts Payable operations via MCP tools."""
import json
import logging
from typing import Optional

from langchain_core.tools import StructuredTool
from opentelemetry import trace
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class GetVendorInvoiceStatusInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID (vendor)")
    invoice_number: Optional[str] = Field(default=None, description="Vendor's invoice number")
    po_number: Optional[str] = Field(default=None, description="Purchase order number")
    top: int = Field(default=20, le=100, description="Max records (max 100)")


class GetPaymentConfirmationInput(BaseModel):
    bp_id: str = Field(description="SAP Business Partner ID (vendor)")
    invoice_number: str = Field(description="Invoice number to confirm payment for")


class GetPurchaseOrderInput(BaseModel):
    po_number: str = Field(description="SAP Purchase Order number")
    top: int = Field(default=20, le=100, description="Max records (max 100)")


@tracer.start_as_current_span("get_vendor_invoice_status")
async def _get_invoice_status(bp_id: str, invoice_number: Optional[str] = None, po_number: Optional[str] = None, top: int = 20) -> str:
    top = min(top, 100)
    logger.info("[AP-M1].achieved: retrieving invoice status | bp_id=%s | invoice=%s", bp_id, invoice_number)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA AP OData MCP tool to retrieve vendor invoice status.",
        "bp_id": bp_id,
        "invoice_number": invoice_number,
        "po_number": po_number,
        "top": top
    })


@tracer.start_as_current_span("get_payment_confirmation")
async def _get_payment_confirmation(bp_id: str, invoice_number: str) -> str:
    logger.info("[AP-M1].achieved: retrieving payment confirmation | bp_id=%s | invoice=%s", bp_id, invoice_number)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA AP OData MCP tool to retrieve payment confirmation and bank transfer reference for this invoice.",
        "bp_id": bp_id,
        "invoice_number": invoice_number
    })


@tracer.start_as_current_span("get_purchase_order_status")
async def _get_po_status(po_number: str, top: int = 20) -> str:
    top = min(top, 100)
    logger.info("[AP-M1].achieved: retrieving PO status | po=%s", po_number)
    return json.dumps({
        "instruction": "Use the SAP S/4HANA AP OData MCP tool to retrieve purchase order status.",
        "po_number": po_number,
        "top": top
    })


def get_ap_tools() -> list:
    return [
        StructuredTool(
            name="get_vendor_invoice_status",
            description="Retrieve the processing status of a vendor invoice from SAP S/4HANA AP. Returns posting status, payment date, and clearing document.",
            args_schema=GetVendorInvoiceStatusInput,
            coroutine=_get_invoice_status,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="get_payment_confirmation",
            description="Retrieve payment confirmation and bank transfer reference for a specific vendor invoice.",
            args_schema=GetPaymentConfirmationInput,
            coroutine=_get_payment_confirmation,
            handle_tool_error=True,
        ),
        StructuredTool(
            name="get_purchase_order_status",
            description="Retrieve the status of a SAP Purchase Order including goods receipt and invoice posting.",
            args_schema=GetPurchaseOrderInput,
            coroutine=_get_po_status,
            handle_tool_error=True,
        ),
    ]
