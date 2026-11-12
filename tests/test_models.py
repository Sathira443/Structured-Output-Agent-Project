import pytest
from pydantic import ValidationError

from app.models import TicketResult


def test_valid_ticket_result_is_accepted() -> None:
    result = TicketResult(
        category="technical",
        priority=2,
        summary="The customer cannot log in.",
        needs_human=False,
    )

    assert result.priority == 2


def test_priority_outside_contract_is_rejected() -> None:
    with pytest.raises(ValidationError):
        TicketResult(
            category="technical",
            priority=8,
            summary="The customer cannot log in.",
            needs_human=False,
        )


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        TicketResult(
            category="technical",
            priority=2,
            summary="The customer cannot log in.",
            needs_human=False,
            extra_field="not allowed",
        )
