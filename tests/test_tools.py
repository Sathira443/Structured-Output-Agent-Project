import pytest
from pydantic import ValidationError

from app.models import CustomerPlanArgs
from app.tools import ToolValidationError, get_customer_plan, validate_customer_plan_response


def test_customer_plan_tool_returns_validated_result() -> None:
    result = get_customer_plan(CustomerPlanArgs(customer_id="cus_001"))

    assert result.plan == "pro"
    assert result.active is True


def test_invalid_tool_arguments_are_rejected() -> None:
    with pytest.raises(ToolValidationError):
        get_customer_plan({"customer_id": ""})


def test_unknown_customer_is_rejected() -> None:
    with pytest.raises(ToolValidationError):
        get_customer_plan({"customer_id": "cus_missing"})


def test_malformed_tool_response_is_rejected(caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(ToolValidationError) as error:
        with caplog.at_level("WARNING"):
            validate_customer_plan_response(
                {"customer_id": "cus_001", "plan": "pro", "active": "sometimes"}
            )

    assert isinstance(error.value.__cause__, ValidationError)
    assert any(
        getattr(record, "event", None) == "tool_validation_failed"
        for record in caplog.records
    )
