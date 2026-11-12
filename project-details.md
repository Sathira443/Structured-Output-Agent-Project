# Project 1: Structured Output Agent

## Goal

Build a support-ticket extraction agent that demonstrates how schemas, validation, retries, and logs make LLM applications more reliable.

The user enters an unstructured ticket. The LLM returns a `TicketResult`. The application validates it with Pydantic, logs failures, retries once, and prints either valid JSON or a controlled error.

The project also includes one deterministic `get_customer_plan` tool whose arguments and response are validated.

## Install

Required: Python 3.11+, Git, VS Code Python extension, and an API key from a model provider.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`. Run the CLI:

```powershell
python -m app.main "The customer cannot log in after changing their password."
```

Run tests without making API calls:

```powershell
pytest
```

You do not need LangChain, LangGraph, a vector database, Docker, or a frontend for version 1.

## Project layout

```text
structured-output-agent/
  app/
    models.py          # Pydantic schemas
    tools.py           # validated deterministic tool
    agent.py           # provider call, parsing, retry, logging
    main.py            # CLI
  tests/               # mocked unit tests
  agent-ml-basics.md
  project-details.md
  README.md
  requirements.txt
  .env.example
```

## Contracts

`TicketResult` requires:

- `category`: billing, technical, account, or other
- `priority`: integer from 1 through 5
- `summary`: 1 through 500 characters
- `needs_human`: boolean

`CustomerPlanArgs` requires a non-empty customer ID. `CustomerPlanResult` requires the customer ID, plan, and active status.

Extra fields are rejected so the application does not silently accept unexpected model output.

## Agent flow

```text
run(ticket_text)
  -> call the LLM with a JSON schema
  -> parse JSON
  -> TicketResult.model_validate(data)
  -> return result if valid
  -> log validation failure
  -> retry once with a correction instruction
  -> validate again
  -> raise AgentOutputError if still invalid
```

The provider-specific OpenAI code is isolated in `app/agent.py`. The core agent accepts a callable returning JSON text, which makes the retry logic easy to test without spending money on API calls.

## Tool flow

```text
validate tool arguments
  -> run the deterministic customer lookup
  -> validate the raw response
  -> return CustomerPlanResult
```

A malformed tool response raises `ToolValidationError` instead of silently entering the rest of the application.

## Logging

The agent logs `request_id`, `attempt`, `event`, `model_name`, validation error type, and elapsed time. It does not log the raw ticket or API key.

Events include `validation_failed`, `success`, and `final_failure`.

## Tests included

- valid and invalid ticket schemas
- rejected extra fields
- valid tool arguments and results
- invalid tool arguments
- missing customers
- malformed tool responses
- first-attempt model success
- validation failure followed by a successful retry
- final failure after two invalid responses
- empty input rejection

## Milestones

1. Run the schema and tool tests.
2. Run one real model call from the CLI.
3. Observe a validation failure and retry in the logs.
4. Read and modify the mocked tests.
5. Add a real customer API only after the deterministic version is understood.

## Definition of done

- Every model response is parsed and validated before use.
- Every tool input and output is validated.
- Validation failures are logged without exposing secrets.
- Retries are bounded.
- Tests cover success, retry, and final failure.
- The CLI returns a clear error instead of accepting bad data silently.
