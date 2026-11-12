import json
import logging
import os
import time
import uuid
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from .models import TicketResult

logger = logging.getLogger(__name__)
ResponseProvider = Callable[[str], str]


class AgentOutputError(RuntimeError):
    """Raised when the model cannot produce a valid result in the retry budget."""


class StructuredOutputAgent:
    def __init__(
        self,
        response_provider: ResponseProvider,
        model_name: str = "demo-model",
        max_attempts: int = 2,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.response_provider = response_provider
        self.model_name = model_name
        self.max_attempts = max_attempts

    def run(self, ticket_text: str) -> TicketResult:
        if not ticket_text.strip():
            raise ValueError("ticket_text must not be empty")

        request_id = str(uuid.uuid4())
        last_error: Exception | None = None
        started_at = time.perf_counter()

        for attempt in range(1, self.max_attempts + 1):
            prompt = self._build_prompt(ticket_text, last_error)
            raw_response = self.response_provider(prompt)

            try:
                result = self._parse_and_validate(raw_response)
            except (json.JSONDecodeError, TypeError, ValidationError) as error:
                last_error = error
                logger.warning(
                    "Model output validation failed",
                    extra={
                        "request_id": request_id,
                        "attempt": attempt,
                        "event": "validation_failed",
                        "model_name": self.model_name,
                        "validation_error": type(error).__name__,
                    },
                )
                continue

            logger.info(
                "Structured output accepted",
                extra={
                    "request_id": request_id,
                    "attempt": attempt,
                    "event": "success",
                    "model_name": self.model_name,
                    "elapsed_ms": round((time.perf_counter() - started_at) * 1000, 2),
                },
            )
            return result

        logger.error(
            "Model output remained invalid after retry budget",
            extra={
                "request_id": request_id,
                "attempt": self.max_attempts,
                "event": "final_failure",
                "model_name": self.model_name,
                "validation_error": type(last_error).__name__ if last_error else "unknown",
            },
        )
        raise AgentOutputError(
            f"The model did not return valid TicketResult data after {self.max_attempts} attempts"
        ) from last_error

    @staticmethod
    def _parse_and_validate(raw_response: str) -> TicketResult:
        data: Any = json.loads(raw_response)
        return TicketResult.model_validate(data)

    @staticmethod
    def _build_prompt(ticket_text: str, previous_error: Exception | None) -> str:
        correction = ""
        if previous_error is not None:
            correction = (
                " Your previous response violated the JSON contract. "
                "Return only valid JSON with the required fields and allowed values."
            )
        return (
            "Extract this support ticket into a JSON object with exactly these fields: "
            "category (billing, technical, account, or other), priority (integer 1-5), "
            "summary (1-500 characters), and needs_human (boolean)."
            f"{correction}\n\nTicket:\n{ticket_text}"
        )


def openai_response_provider() -> tuple[ResponseProvider, str]:
    """Create a provider using the official OpenAI SDK only when the CLI needs it."""
    from openai import OpenAI

    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    schema = TicketResult.model_json_schema()

    def request(prompt: str) -> str:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You extract support tickets and return only the requested JSON object.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ticket_result",
                    "strict": True,
                    "schema": schema,
                },
            },
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("The model returned an empty response")
        return content

    return request, model_name
