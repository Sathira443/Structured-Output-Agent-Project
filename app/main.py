import argparse
import logging
import sys

from dotenv import load_dotenv

from .agent import AgentOutputError, StructuredOutputAgent, openai_response_provider


class ContextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        request_id = getattr(record, "request_id", "-")
        attempt = getattr(record, "attempt", "-")
        event = getattr(record, "event", "-")
        return (
            f"{record.levelname} event={event} request_id={request_id} "
            f"attempt={attempt} message={record.getMessage()}"
        )


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(ContextFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a support ticket into validated JSON")
    parser.add_argument("ticket", nargs="?", help="Support ticket text")
    args = parser.parse_args()

    load_dotenv()
    configure_logging()
    ticket = args.ticket or input("Support ticket: ")

    try:
        provider, model_name = openai_response_provider()
        result = StructuredOutputAgent(provider, model_name=model_name).run(ticket)
    except (AgentOutputError, ValueError, KeyError) as error:
        print(f"Request failed: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        logging.getLogger(__name__).exception("Provider request failed")
        print(f"Provider request failed: {error}", file=sys.stderr)
        return 1

    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
