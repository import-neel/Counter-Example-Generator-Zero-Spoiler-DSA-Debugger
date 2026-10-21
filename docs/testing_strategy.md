# Testing Strategy & Verification Report

**Counter-Example Generator & Zero-Spoiler DSA Debugger**  
**Role:** Teammate 1 — Execution, Backend, and Security Engineer

---

## 1. Testing Hierarchy

Our testing suite is divided into three distinct validation suites:

1. **Unit Tests (`tests/unit/`)**:
   - Verification of the core execution engine (`CodeRunner`).
   - Normal code execution and stdout capture.
   - Multiline stdin feeding.
   - Syntax error detection via AST parser.
   - Runtime error tracebacks (e.g., `ZeroDivisionError`, `IndexError`).
   - Timeout termination.
   - Output buffer truncation and flags.
   - Ephemeral working directory cleanup.

2. **Integration Tests (`tests/integration/`)**:
   - Verification of FastAPI HTTP endpoints.
   - Endpoint `/health` status check.
   - Endpoint `POST /submissions/run` end-to-end execution and database persistence.
   - Endpoint `GET /submissions/{id}` record retrieval.
   - Request schema validation (HTTP 422).
   - Problem catalog contract endpoints.

3. **Security Tests (`tests/security/`)**:
   - Verification against infinite loop freezing (`while True: pass`).
   - Verification of environment variable sanitization (no secret leakage from host).
   - Verification of output bombs (`print("A" * 10**7)`).
   - Verification of isolated file access (no host directory contamination).
   - Verification of network socket restrictions.
   - Verification of excessive memory allocation attempts.

---

## 2. Test Execution Command

Run all tests via pytest from the project root:

```bash
pytest -v
```

All 22 test cases execute synchronously in approximately 5 seconds.
