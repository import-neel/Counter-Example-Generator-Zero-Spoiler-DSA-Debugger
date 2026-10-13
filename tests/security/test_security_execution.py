import os
import pytest
from app.schemas.result_schema import ExecutionStatus
from app.services.code_runner import run_code


def test_security_infinite_loop_timeout():
    """Verify infinite loop terminates properly and does not hang."""
    code = """
while True:
    pass
"""
    result = run_code(code, timeout=0.8)
    assert result.status == ExecutionStatus.TIMEOUT
    assert result.exit_code == -1


def test_security_environment_variable_isolation():
    """Verify backend environment secrets are NOT leaked to student process."""
    code = """
import os
print(list(os.environ.keys()))
"""
    result = run_code(code)
    assert result.status == ExecutionStatus.SUCCESS
    # Check that sensitive backend config is NOT leaked
    stdout = result.stdout
    assert "DATABASE_URL" not in stdout
    assert "SECRET_KEY" not in stdout
    assert "AWS_ACCESS_KEY_ID" not in stdout
    assert "OPENAI_API_KEY" not in stdout


def test_security_excessive_output_bomb():
    """Verify that output bomb does not crash process or exceed max output byte limit."""
    code = """
print("A" * 10000000)
"""
    result = run_code(code, max_output_bytes=4096)
    assert result.status == ExecutionStatus.OUTPUT_LIMIT_EXCEEDED
    assert len(result.stdout.encode("utf-8")) <= 4096
    assert result.truncated is True


def test_security_file_writing_contained_or_isolated():
    """
    Verify that creating a file occurs inside the isolated temporary sandbox folder
    and does not survive cleanup.
    """
    code = """
with open("test.txt", "w") as f:
    f.write("malicious payload")
print("file written")
"""
    result = run_code(code)
    assert result.status == ExecutionStatus.SUCCESS
    # File must NOT be written in backend current directory
    assert not os.path.exists("test.txt")


def test_security_memory_exhaustion_attempt():
    """Verify memory allocation attempt is handled without freezing."""
    code = """
try:
    a = [0] * (10 ** 8)
    print("allocated")
except MemoryError:
    print("MemoryError caught")
"""
    result = run_code(code, timeout=2.0)
    assert result.status in [
        ExecutionStatus.SUCCESS,
        ExecutionStatus.RUNTIME_ERROR,
        ExecutionStatus.TIMEOUT,
        ExecutionStatus.MEMORY_LIMIT_EXCEEDED,
    ]


def test_security_socket_import_handling():
    """Verify code attempting to open network connection can execute or fail gracefully without crashing server."""
    code = """
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.5)
try:
    s.connect(("127.0.0.1", 9999))
    print("connected")
except Exception as e:
    print(f"connection failed: {type(e).__name__}")
"""
    result = run_code(code, timeout=2.0)
    assert result.status == ExecutionStatus.SUCCESS
    assert "connection failed" in result.stdout
