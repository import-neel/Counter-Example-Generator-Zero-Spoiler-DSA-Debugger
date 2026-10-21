# Architecture & System Design — Backend, Execution, and Security

**Counter-Example Generator & Zero-Spoiler DSA Debugger**  
**Role:** Teammate 1 — Execution, Backend, and Security Engineer

---

## 1. High-Level Architecture Overview

The system adheres strictly to the core architectural invariant:
> **Program execution determines correctness.** The backend and sandbox provide objective empirical execution telemetry. Neither the FastAPI server nor the AI layer independently decides whether student code is correct.

```
                           +----------------------------+
                           |  Teammate 3 (Frontend/UI)  |
                           |   (Streamlit / Web App)    |
                           +--------------+-------------+
                                          |
                                          | HTTP REST (JSON)
                                          v
+---------------------------------------------------------------------------------+
|                       FastAPI Backend (app/main.py)                             |
|                                                                                 |
|  [Routers]                                                                      |
|  - GET  /health                                                                 |
|  - POST /submissions/run                                                        |
|  - GET  /submissions/{id}                                                       |
|  - GET  /problems                                                               |
|                                                                                 |
|  [Database Engine] (app/database.py)                                            |
|  - SQLite (Dev/Test) / PostgreSQL (Prod)                                        |
|  - Tables: Submissions, DebuggingSessions, Problems, TestCases                 |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
|                      Code Runner (app/services/code_runner.py)                  |
|                                                                                 |
|  - Pre-execution AST Syntax check (`check_syntax`)                              |
|  - Telemetry & Execution time profiling                                         |
|  - Output truncation & sanitization                                             |
|  - Direct functional entrypoint for Teammate 2:                                 |
|       `result = run_code(student_code, test_input, ...)`                        |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
|                  Sandbox Manager (app/services/sandbox_manager.py)              |
|                                                                                 |
|             +-------------------------+-------------------------+               |
|             |                                                   |               |
|             v                                                   v               |
|  [LocalSubprocessSandbox]                            [DockerSandbox]            |
|  - Ephemeral temp dir (mkdtemp)                      - Network disabled (none)  |
|  - Stripped environment (no secrets)                 - Read-only root FS        |
|  - Process kill on timeout                           - Memory limit (128MB)     |
|  - Guaranteed cleanup in `finally`                   - Dropped caps (ALL)       |
|                                                      - Non-root user (1000)     |
+---------------------------------------------------------------------------------+
```

---

## 2. Execution Lifecycle

Every submission follows a deterministic, guarded lifecycle:

1. **Submission Ingestion:** Received via `POST /submissions/run` with problem ID, language, source code, and stdin input.
2. **Pre-Execution AST Validation:** AST parsing checks for syntax errors in micro-seconds before creating subprocesses.
3. **Sandbox Provisioning:**
   - A unique ephemeral directory (`dsa_exec_xxxxxx`) is allocated in the system temp directory.
   - Student code is written to `solution.py` within this isolated directory.
4. **Isolated Execution:**
   - Python is executed in isolated mode (`-I -B -s`), ignoring system `PYTHONPATH` and user package paths.
   - Environment variables are scrubbed; no application configuration or database credentials are passed.
   - In Docker mode: `--network none`, `--memory=128m`, `--pids-limit=32`, and `--read-only` constraints are enforced.
5. **Telemetry & Safeguards:**
   - Stdin is pumped into the child process.
   - Real execution duration is captured using `time.perf_counter()`.
   - Process is forcefully killed if `timeout` is reached.
   - Output byte limits (default: 64 KB) prevent output bomb denial of service.
6. **Sanitization & Cleanup:**
   - Internal temp paths in stack traces are scrubbed to prevent system disclosure.
   - The ephemeral execution directory is deleted recursively inside a `finally` block.
7. **Persistence & Response:**
   - Execution status, exit code, runtime, and sanitized output are stored in the database.
   - Structured JSON response is returned to the client.

---

## 3. Database Schema

The persistence layer uses SQLAlchemy 2.0 with portable declarative schemas:

- **`submissions`**:
  - `id`: UUID (String) primary key.
  - `problem_id`: String indexed problem identifier.
  - `language`: Target runtime (e.g. `python`).
  - `code`: Student source code text.
  - `status`: Execution status enum string.
  - `stdout`, `stderr`: Truncated outputs.
  - `exit_code`: Integer exit status.
  - `execution_time`: Measured execution seconds.
  - `created_at`: UTC timestamp.
- **`debugging_sessions`**:
  - `id`: UUID primary key.
  - `user_id`: String user identifier.
  - `problem_id`: String problem foreign link.
  - `current_hint_level`: Current zero-spoiler hint level unlocked.
  - `counterexample_input`, `counterexample_expected`, `counterexample_actual`: Minimized counterexample fields.
  - `status`: `in_progress`, `resolved`, `given_up`.
- **`problems` & `test_cases`**:
  - Normalized tables for problem definitions and input/output fixtures for Teammate 2.
