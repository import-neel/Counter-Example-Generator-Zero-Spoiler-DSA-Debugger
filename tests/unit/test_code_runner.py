import pytest
from app.services.code_runner import run_code
from app.schemas.result_schema import ExecutionStatus


def test_normal_execution():
    code = "print('Hello, world!')"
    result = run_code(code)
    assert result.status == ExecutionStatus.SUCCESS
    assert result.stdout.strip() == "Hello, world!"
    assert result.exit_code == 0
    assert result.execution_time >= 0.0


def test_stdin_processing():
    code = """
import sys
data = sys.stdin.read().split()
a, b = int(data[0]), int(data[1])
print(a + b)
"""
    result = run_code(code, input_data="15 27\n")
    assert result.status == ExecutionStatus.SUCCESS
    assert result.stdout.strip() == "42"
    assert result.exit_code == 0


def test_syntax_error():
    code = "def bad_syntax(:\n    pass"
    result = run_code(code)
    assert result.status == ExecutionStatus.SYNTAX_ERROR
    assert "SyntaxError" in result.stderr
    assert result.exit_code == 1


def test_runtime_division_by_zero():
    code = "x = 10 / 0"
    result = run_code(code)
    assert result.status == ExecutionStatus.RUNTIME_ERROR
    assert "ZeroDivisionError" in result.stderr
    assert result.exit_code != 0


def test_runtime_index_error():
    code = "arr = [1, 2]\nprint(arr[5])"
    result = run_code(code)
    assert result.status == ExecutionStatus.RUNTIME_ERROR
    assert "IndexError" in result.stderr


def test_timeout_infinite_loop():
    code = "while True:\n    pass"
    result = run_code(code, timeout=0.8)
    assert result.status == ExecutionStatus.TIMEOUT
    assert "Time limit exceeded" in result.stderr


def test_output_limit_protection():
    code = "print('A' * 200000)"
    result = run_code(code, max_output_bytes=1024)
    assert result.status == ExecutionStatus.OUTPUT_LIMIT_EXCEEDED
    assert len(result.stdout.encode("utf-8")) <= 1024
    assert result.truncated is True


def test_empty_code_submission():
    result = run_code("")
    assert result.status == ExecutionStatus.RUNTIME_ERROR
    assert "empty" in result.stderr.lower()
