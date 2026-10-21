# Counter-Example Generator & Zero-Spoiler DSA Debugger
## Execution, Backend, and Security Subsystem

[![Tests](https://img.shields.io/badge/pytest-22%20passed-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)]()

This repository contains the **Execution, Backend, and Security** subsystem for the *Counter-Example Generator & Zero-Spoiler DSA Debugger* (built as part of Teammate 1 responsibilities).

---

## Architecture Overview

```
Teammate 3 (Streamlit Frontend)
       |
       |  REST API (/submissions/run, /submissions/{id}, /health)
       v
FastAPI Backend (app/main.py)
       |
       +---> SQLite/PostgreSQL Database (app/database.py)
       |
       v
Code Runner Engine (app/services/code_runner.py) <--- Teammate 2 (Differential Testing)
       |
       v
Sandbox Manager (app/services/sandbox_manager.py)
  ├── LocalSubprocessSandbox (Isolated environment, timeout kill, output cap)
  └── DockerSandbox (--network none, --memory=128m, --read-only, non-root)
```

---

## Key Features

1. **Deterministic Program Execution**:
   - Executes arbitrary student Python code safely.
   - Pushes stdin, captures stdout and stderr, reports exit codes and accurate execution time.
2. **Strict Security Sandboxing**:
   - Zero `exec()` / `eval()` execution inside the FastAPI backend.
   - Pre-execution AST syntax check.
   - Environment variable scrubbing: child processes cannot see server secrets, API keys, or database URLs.
   - Ephemeral directory allocation with guaranteed post-run cleanup.
   - Binary output bomb protection (capped at 64 KB).
   - Strict process timeouts for infinite loop protection (`while True: pass`).
   - Docker container execution with `--network none`, `--memory=128m`, and `--read-only` root filesystem.
3. **Database Persistence**:
   - SQLAlchemy 2.0 ORM with SQLite for development and seamless PostgreSQL production readiness.
   - Persistent `Submission`, `DebuggingSession`, `Problem`, and `TestCase` models.
4. **Integration Interfaces**:
   - **For Teammate 2 (Differential Testing / Counter-examples)**:  
     Direct functional interface:
     ```python
     from app.services.code_runner import run_code

     result = run_code(student_code, test_input, timeout=2.0)
     # result.status, result.stdout, result.stderr, result.exit_code, result.execution_time
     ```
   - **For Teammate 3 (Frontend / UI / AI)**:  
     CORS-enabled REST endpoints for submission runs and telemetry.

---

## Setup & Running

### 1. Prerequisites
- Python 3.12+
- (Optional for container isolation) Docker & Docker Compose

### 2. Installation
```bash
git clone <repo-url>
cd counterexample-debugger
python -m pip install -r requirements.txt
cp .env.example .env
```

### 3. Run FastAPI Backend
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI documentation will be accessible at: `http://localhost:8000/docs`

### 4. Run Complete Test Suite
```bash
pytest -v
```

### 5. Run with Docker Compose
```bash
docker compose up --build
```

---

## Documentation

- [System Architecture](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Security Model & Mitigations](docs/security.md)
- [Testing Strategy](docs/testing_strategy.md)
