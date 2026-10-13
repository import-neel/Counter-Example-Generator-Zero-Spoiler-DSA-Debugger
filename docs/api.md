# REST API Specification

**Counter-Example Generator & Zero-Spoiler DSA Debugger**  
**FastAPI Backend Endpoints**

---

## 1. Health Check

### `GET /health`
Returns the operational status of the backend and the current execution engine mode.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "environment": "development",
  "sandbox_mode": "local",
  "docker_available": "False"
}
```

---

## 2. Submissions API

### `POST /submissions/run`
Executes submitted Python code safely against standard input and stores the submission telemetry.

**Request Body**:
```json
{
  "problem_id": "two_sum_001",
  "language": "python",
  "code": "import sys\narr = list(map(int, sys.stdin.readline().split()))\nprint(sum(arr))",
  "input": "1 2 3 4 5\n",
  "timeout": 2.0
}
```

**Response `201 Created`**:
```json
{
  "submission_id": "3f9c6d36-8a7e-4be2-a8ce-78a06e902b8d",
  "problem_id": "two_sum_001",
  "language": "python",
  "result": {
    "status": "success",
    "stdout": "15\n",
    "stderr": "",
    "exit_code": 0,
    "execution_time": 0.038,
    "error_message": null,
    "truncated": false
  },
  "created_at": "2026-10-13T15:30:00Z"
}
```

**Possible Execution Statuses**:
- `success`: Code ran to completion with exit code 0.
- `syntax_error`: Code failed static AST parsing prior to execution.
- `runtime_error`: Process terminated abnormally with non-zero exit code or exception traceback.
- `timeout`: Code execution exceeded the specified timeout limit.
- `output_limit_exceeded`: Code output exceeded the maximum allowed byte cap (64 KB).
- `memory_limit_exceeded`: Execution exceeded memory thresholds.
- `sandbox_error`: Sandbox daemon or container runtime error.
- `internal_error`: Unhandled runner exception.

---

### `GET /submissions/{submission_id}`
Retrieves a previously stored submission and its complete execution telemetry.

**Response `200 OK`**:
```json
{
  "id": "3f9c6d36-8a7e-4be2-a8ce-78a06e902b8d",
  "problem_id": "two_sum_001",
  "language": "python",
  "code": "import sys...",
  "status": "success",
  "stdout": "15\n",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.038,
  "created_at": "2026-10-13T15:30:00Z"
}
```

**Response `404 Not Found`**:
```json
{
  "detail": "Submission with ID '3f9c6d36-8a7e-4be2-a8ce-78a06e902b8d' not found"
}
```

---

## 3. Problems Catalog API (Contract Stubs)

### `GET /problems`
Returns the list of available DSA problems.

**Response `200 OK`**:
```json
[
  {
    "id": "two_sum_001",
    "title": "Two Sum",
    "description": "Find indices of the two numbers that add up to target.",
    "input_format": "N\\nArray elements\\nTarget",
    "output_format": "Index1 Index2",
    "constraints": "2 <= N <= 10^5",
    "difficulty": "Easy",
    "category": "Arrays",
    "sample_test_cases": []
  }
]
```

### `GET /problems/{problem_id}`
Returns the details and constraints for a single problem.

**Response `200 OK`**:
```json
{
  "id": "two_sum_001",
  "title": "Two Sum",
  "description": "Find indices of the two numbers that add up to target.",
  "difficulty": "Easy",
  "category": "Arrays"
}
```
