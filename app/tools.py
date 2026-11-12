from collections.abc import Mapping
import logging
from typing import Any

from pydantic import ValidationError

from .models import CustomerPlanArgs, CustomerPlanResult

logger = logging.getLogger(__name__)


class ToolValidationError(ValueError):
    """Raised when a tool request or response violates its contract."""


CUSTOMERS: dict[str, dict[str, Any]] = {
    "cus_001": {"plan": "pro", "active": True},
    "cus_002": {"plan": "free", "active": False},
}


def validate_customer_plan_response(raw_response: Mapping[str, Any]) -> CustomerPlanResult:
    """Validate a raw tool response before it crosses the tool boundary."""
    try:
        return CustomerPlanResult.model_validate(raw_response)
    except ValidationError as error:
        logger.warning(
            "Tool response validation failed",
            extra={
                "event": "tool_validation_failed",
                "tool_name": "get_customer_plan",
                "validation_error": type(error).__name__,
            },
        )
        raise ToolValidationError("The customer-plan tool returned an invalid response") from error


def get_customer_plan(arguments: CustomerPlanArgs | Mapping[str, Any]) -> CustomerPlanResult:
    """Return a validated customer plan from the deterministic demo store."""
    try:
        validated_args = (
            arguments
            if isinstance(arguments, CustomerPlanArgs)
            else CustomerPlanArgs.model_validate(arguments)
        )
    except ValidationError as error:
        logger.warning(
            "Tool argument validation failed",
            extra={
                "event": "tool_validation_failed",
                "tool_name": "get_customer_plan",
                "validation_error": type(error).__name__,
            },
        )
        raise ToolValidationError("The customer-plan tool received invalid arguments") from error

    customer = CUSTOMERS.get(validated_args.customer_id)
    if customer is None:
        raise ToolValidationError("The requested customer was not found")

    return validate_customer_plan_response(
        {
            "customer_id": validated_args.customer_id,
            **customer,
        }
    )
