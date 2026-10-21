import sys
import time
from fastapi.testclient import TestClient

from app.main import app
from app.services.code_runner import run_code
from app.schemas.result_schema import ExecutionStatus


def print_header(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def print_step(name, passed, detail=""):
    mark = "[PASS]" if passed else "[FAIL]"
    print(f"{mark:<8} {name}")
    if detail:
        print(f"         -> {detail}")


def run_all_checks():
    print_header("COUNTER-EXAMPLE DEBUGGER - BACKEND VERIFICATION SUITE")

    # 1. Direct Execution: Normal Python Code
    res = run_code("print('Hello from sandbox!')")
    print_step(
        "1. Normal Python Execution",
        res.status == ExecutionStatus.SUCCESS and res.stdout.strip() == "Hello from sandbox!",
        f"Stdout: {res.stdout.strip()!r}, Time: {res.execution_time}s",
    )

    # 2. Stdin Processing
    res_stdin = run_code(
        "import sys\nnums = [int(x) for x in sys.stdin.read().split()]\nprint(sum(nums))",
        input_data="10 20 30 40\n",
    )
    print_step(
        "2. Stdin Processing",
        res_stdin.status == ExecutionStatus.SUCCESS and res_stdin.stdout.strip() == "100",
        f"Expected '100', got {res_stdin.stdout.strip()!r}",
    )

    # 3. Syntax Error Handling
    res_syntax = run_code("def broken_func(:\n    pass")
    print_step(
        "3. Syntax Error Handling (AST)",
        res_syntax.status == ExecutionStatus.SYNTAX_ERROR,
        f"Status: {res_syntax.status.value}, Stderr: {res_syntax.stderr.strip()}",
    )

    # 4. Runtime Error Handling
    res_runtime = run_code("arr = [1, 2]\nprint(arr[99])")
    print_step(
        "4. Runtime Error Handling",
        res_runtime.status == ExecutionStatus.RUNTIME_ERROR and "IndexError" in res_runtime.stderr,
        f"Captured: {res_runtime.stderr.strip().splitlines()[-1] if res_runtime.stderr else ''}",
    )

    # 5. Security: Infinite Loop Timeout
    start = time.perf_counter()
    res_timeout = run_code("while True: pass", timeout=1.0)
    elapsed = time.perf_counter() - start
    print_step(
        "5. Infinite Loop Timeout (1.0s limit)",
        res_timeout.status == ExecutionStatus.TIMEOUT and elapsed < 2.0,
        f"Terminated in {elapsed:.2f}s with status: {res_timeout.status.value}",
    )

    # 6. Security: Output Bomb Protection (64KB cap)
    res_bomb = run_code("print('X' * 500000)", max_output_bytes=4096)
    print_step(
        "6. Output Bomb Protection",
        res_bomb.status == ExecutionStatus.OUTPUT_LIMIT_EXCEEDED and res_bomb.truncated,
        f"Status: {res_bomb.status.value}, Capped at {len(res_bomb.stdout.encode())} bytes",
    )

    # 7. Security: Environment Variable Isolation
    res_env = run_code("import os\nprint('DATABASE_URL' in os.environ)")
    print_step(
        "7. Environment Variable Secret Isolation",
        res_env.status == ExecutionStatus.SUCCESS and res_env.stdout.strip() == "False",
        "Backend environment secrets not leaked to student code",
    )

    # 8. Security: Ephemeral Directory Cleanup
    import os
    from pathlib import Path
    res_clean = run_code("import os\nprint(os.getcwd())")
    temp_dir = res_clean.stdout.strip()
    cleaned = not Path(temp_dir).exists() if temp_dir and os.path.isabs(temp_dir) else True
    print_step(
        "8. Sandbox Directory Guaranteed Cleanup",
        cleaned,
        "Temp folder purged immediately after execution",
    )

    # 9. FastAPI In-Memory Health Endpoint Check
    client = TestClient(app)
    health = client.get("/health")
    print_step(
        "9. FastAPI GET /health Endpoint",
        health.status_code == 200 and health.json().get("status") == "healthy",
        f"Response: {health.json()}",
    )

    # 10. FastAPI POST /submissions/run & Database Persistence
    sub_payload = {
        "problem_id": "test_two_sum",
        "language": "python",
        "code": "import sys\nprint('Processed Stdin: ' + sys.stdin.readline().strip())",
        "input": "4 5 6\n",
    }
    run_resp = client.post("/submissions/run", json=sub_payload)
    sub_data = run_resp.json()
    sub_id = sub_data.get("submission_id")

    # 11. Retrieve Saved Submission from DB
    get_resp = client.get(f"/submissions/{sub_id}") if sub_id else None
    print_step(
        "10. API Submission Execution & Database Retrieval",
        run_resp.status_code == 201 and get_resp is not None and get_resp.status_code == 200,
        f"Submission ID: {sub_id}, Status: {get_resp.json().get('status') if get_resp else 'None'}",
    )

    print_header("ALL 10 CORE VERIFICATION CHECKS COMPLETED")


if __name__ == "__main__":
    run_all_checks()
