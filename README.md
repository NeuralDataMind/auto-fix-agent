# Auto-Fix Agent

Auto-Fix Agent is an AI-assisted code repair pipeline that runs inside GitHub Actions.

It runs the test suite, captures failures, retrieves the most relevant source file using ChromaDB, sends the file and error log to an LLM, applies the generated fix, and verifies the result by running tests again.

This project is closer to a deterministic RAG repair pipeline than a fully autonomous agent. It follows a fixed flow: test, retrieve, patch, verify.

## What It Does

1. Runs `pytest`.
2. If tests fail, captures the error output.
3. Uses ChromaDB to search the indexed codebase.
4. Retrieves the file most related to the failure.
5. Sends the file content and error log to a Groq-hosted Llama model.
6. Writes the generated fix back to the file.
7. Runs tests again.
8. If tests pass, GitHub Actions can commit the fix.

## Architecture

```text
GitHub Actions
    ↓
Run pytest
    ↓
Capture error log
    ↓
Query ChromaDB
    ↓
Retrieve relevant source file
    ↓
Send code + error to LLM
    ↓
Generate fixed code
    ↓
Overwrite file
    ↓
Run tests again
    ↓
Commit fix if successful
