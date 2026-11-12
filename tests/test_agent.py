import logging

import pytest

from app.agent import AgentOutputError, StructuredOutputAgent


def test_valid_first_response_is_returned() -> None:
    prompts: list[str] = []

    def provider(prompt: str) -> str:
        prompts.append(prompt)
        return '{"category":"account","priority":1,"summary":"Password reset needed","needs_human":false}'

    result = StructuredOutputAgent(provider).run("I need to reset my password")

    assert result.category == "account"
    assert len(prompts) == 1


def test_invalid_first_response_is_logged_and_retried(caplog: pytest.LogCaptureFixture) -> None:
    responses = [
        '{"category":"technical","priority":9,"summary":"Bad priority","needs_human":false}',
        '{"category":"technical","priority":3,"summary":"The app crashes","needs_human":true}',
    ]

    def provider(_: str) -> str:
        return responses.pop(0)

    with caplog.at_level(logging.WARNING):
        result = StructuredOutputAgent(provider).run("The app crashes")

    assert result.priority == 3
    assert len(responses) == 0
    assert "Model output validation failed" in caplog.text
    assert any(
        getattr(record, "event", None) == "validation_failed"
        for record in caplog.records
    )


def test_two_invalid_responses_raise_controlled_error() -> None:
    def provider(_: str) -> str:
        return "not-json"

    with pytest.raises(AgentOutputError, match="after 2 attempts"):
        StructuredOutputAgent(provider).run("A ticket")


def test_empty_ticket_is_rejected_before_provider_call() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        StructuredOutputAgent(lambda _: "{}").run(" ")
