# Structured Output Agent

A small beginner project that makes an LLM response more reliable with Pydantic schemas, local validation, bounded retries, and validation logs.

## Quick start

From this folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env`, add your API key, then run:

```powershell
python -m app.main "The customer cannot log in after changing their password."
```

Run the tests without using an API:

```powershell
pytest
```

## What the code demonstrates

- `app/models.py` defines strict Pydantic contracts.
- `app/tools.py` validates tool arguments and tool responses.
- `app/agent.py` parses model JSON, validates it, logs failures, and retries once.
- `app/main.py` provides the command-line interface.
- `tests/` mocks model responses so tests are fast and free.

The provider-specific OpenAI call is isolated in `openai_response_provider()`. The core agent accepts any callable that returns JSON text, which keeps the retry and validation logic easy to test.

Read [agent-ml-basics.md](agent-ml-basics.md) for the beginner concepts and [project-details.md](project-details.md) for the full project explanation.
