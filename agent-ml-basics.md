# Agent and LLM Basics for Beginners

## What this project teaches

This project does not train a machine-learning model. It uses an existing large language model (LLM) and builds a reliable program around it.

An LLM can produce useful text, but your application must validate its output before trusting it.

## Key terms

### LLM

A large language model predicts text from the input it receives. It is good at language and pattern matching, but it does not guarantee that its answer is correct, complete, or valid JSON.

### Prompt

A prompt is the instruction and data sent to the model. Saying "return valid JSON" helps, but a prompt is not a type system.

### Agent

An agent is an LLM inside a program that can read a request, decide what is needed, call a tool, observe the result, and produce a final answer. This project intentionally uses a small agent: one model call, one optional tool, and one validated result.

### Tool

A tool is a normal program function that the model may request. Your application validates the arguments, runs the function, validates its result, and sends that result back to the model. The LLM does not execute Python directly.

### Schema

A schema describes the exact shape and types of accepted data. Pydantic models provide these schemas in Python. Missing fields, extra fields, and invalid values are rejected.

### Structured output

Structured output means asking the model for data in a defined shape instead of free-form prose. Use provider/API schema enforcement when available, then always parse and validate locally with Pydantic.

### Retry

A retry is another attempt after a recoverable failure. This project retries parsing or validation failures once, then returns a controlled error. Retries do not prove that the answer is correct.

### Observability and logging

Logs record what happened. This project records a request ID, attempt number, event, model name, validation error type, and elapsed time. Never log API keys, passwords, or private customer data.

## Complete flow

```text
User request
    -> application sends instructions to LLM
    -> LLM returns JSON
    -> application parses JSON
    -> Pydantic validates it
        -> valid: use it
        -> invalid: log failure and retry once
        -> still invalid: return controlled error
```

For a tool:

```text
LLM requests a tool
    -> validate tool arguments
    -> run ordinary Python function
    -> validate tool response
    -> continue with the validated result
```

## What you do not need yet

You do not need neural-network training, embeddings, vector databases, LangChain, LangGraph, Kubernetes, or multi-agent orchestration for this project.

## Learning order

1. Write a normal Python function with Pydantic input/output models.
2. Call an LLM and inspect its raw response.
3. Parse and validate the response.
4. Add one bounded retry.
5. Add one deterministic tool.
6. Test malformed JSON and invalid tool results.

Treat the LLM as an untrusted external service, not as a function whose return type can be assumed.
