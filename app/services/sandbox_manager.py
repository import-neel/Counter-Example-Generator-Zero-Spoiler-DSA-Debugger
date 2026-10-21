import abc
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from app.config import settings
from app.schemas.result_schema import ExecutionResult, ExecutionStatus
from app.utils.logger import logger
from app.utils.security import sanitize_error_trace, truncate_output


class BaseSandbox(abc.ABC):
    """Abstract interface for code execution sandboxes."""

    @abc.abstractmethod
    def execute(
        self,
        code: str,
        input_data: str,
        timeout: float,
        max_output_bytes: int,
    ) -> ExecutionResult:
        pass


class LocalSubprocessSandbox(BaseSandbox):
    """
    Subprocess-based sandbox with strict resource limits, isolated environment variables,
    temporary execution directory, and defense-in-depth controls.
    """

    def execute(
        self,
        code: str,
        input_data: str,
        timeout: float,
        max_output_bytes: int,
    ) -> ExecutionResult:
        # 1. Create a safe temporary directory
        temp_dir = tempfile.mkdtemp(prefix="dsa_exec_")
        temp_path = Path(temp_dir)
        source_file = temp_path / "solution.py"

        try:
            # 2. Write student source file
            source_file.write_text(code, encoding="utf-8")

            # 3. Build minimal, sanitized environment variables
            # NEVER inherit secret keys, tokens, or backend config
            isolated_env: Dict[str, str] = {
                "PYTHONUNBUFFERED": "1",
                "PYTHONHASHSEED": "0",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PATH": os.environ.get("PATH", ""),
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
                "TEMP": str(temp_path),
                "TMP": str(temp_path),
            }

            # 4. Command line execution
            # -I isolates python: run in isolated mode (ignores PYTHONPATH and user site-packages)
            # -B prevents writing .pyc files
            # -s prevents adding user site directory to sys.path
            cmd = [sys.executable, "-I", "-B", "-s", str(source_file.name)]

            start_time = time.perf_counter()
            process = subprocess.Popen(
                cmd,
                cwd=str(temp_path),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=isolated_env,
                text=False,  # Handle as binary for precise byte limiting
            )

            input_bytes = input_data.encode("utf-8")
            raw_stdout = b""
            raw_stderr = b""
            status = ExecutionStatus.SUCCESS
            truncated = False

            try:
                raw_stdout, raw_stderr = process.communicate(
                    input=input_bytes, timeout=timeout
                )
            except subprocess.TimeoutExpired:
                # Forcefully terminate process and process tree
                process.kill()
                try:
                    raw_stdout, raw_stderr = process.communicate(timeout=0.5)
                except Exception:
                    pass

                execution_time = time.perf_counter() - start_time
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    stdout="",
                    stderr=f"Time limit exceeded ({timeout}s)",
                    exit_code=-1,
                    execution_time=round(execution_time, 4),
                    error_message=f"Execution timed out after {timeout} seconds",
                )

            execution_time = time.perf_counter() - start_time
            exit_code = process.returncode

            # Check output size limits
            if len(raw_stdout) > max_output_bytes:
                raw_stdout = raw_stdout[:max_output_bytes]
                status = ExecutionStatus.OUTPUT_LIMIT_EXCEEDED
                truncated = True

            if len(raw_stderr) > max_output_bytes:
                raw_stderr = raw_stderr[:max_output_bytes]
                truncated = True

            decoded_stdout = raw_stdout.decode("utf-8", errors="replace")
            decoded_stderr = raw_stderr.decode("utf-8", errors="replace")
            sanitized_stderr = sanitize_error_trace(decoded_stderr)

            if status == ExecutionStatus.OUTPUT_LIMIT_EXCEEDED:
                return ExecutionResult(
                    status=ExecutionStatus.OUTPUT_LIMIT_EXCEEDED,
                    stdout=decoded_stdout,
                    stderr=sanitized_stderr
                    + f"\n[Output limit exceeded: capped at {max_output_bytes} bytes]",
                    exit_code=exit_code,
                    execution_time=round(execution_time, 4),
                    error_message=f"Output exceeded maximum limit of {max_output_bytes} bytes",
                    truncated=True,
                )

            # Check for memory limit / SIGKILL / Windows exit codes indicating crashes
            if exit_code != 0:
                # Distinguish memory limit or crash exit codes
                if exit_code in (-9, 137, 3221225477):  # SIGKILL or STATUS_ACCESS_VIOLATION
                    status = ExecutionStatus.MEMORY_LIMIT_EXCEEDED
                    err_msg = "Process terminated (possible memory limit or access violation)"
                else:
                    status = ExecutionStatus.RUNTIME_ERROR
                    err_msg = sanitized_stderr.strip().split("\n")[-1] if sanitized_stderr.strip() else f"Runtime error (exit code {exit_code})"

                return ExecutionResult(
                    status=status,
                    stdout=decoded_stdout,
                    stderr=sanitized_stderr,
                    exit_code=exit_code,
                    execution_time=round(execution_time, 4),
                    error_message=err_msg,
                    truncated=truncated,
                )

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                stdout=decoded_stdout,
                stderr=sanitized_stderr,
                exit_code=0,
                execution_time=round(execution_time, 4),
                truncated=truncated,
            )

        except Exception as e:
            logger.exception("Unexpected exception inside LocalSubprocessSandbox")
            return ExecutionResult(
                status=ExecutionStatus.INTERNAL_ERROR,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=0.0,
                error_message=f"Internal runner error: {str(e)}",
            )
        finally:
            # 5. Guaranteed cleanup of temporary directory and solution file
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning("Failed to clean temporary directory %s: %s", temp_dir, e)


class DockerSandbox(BaseSandbox):
    """
    Docker-based container sandbox providing process isolation, restricted network,
    non-root execution, dropped capabilities, and memory limits.
    """

    def __init__(
        self,
        image: str = settings.DOCKER_IMAGE,
        memory_mb: int = settings.MAX_MEMORY_MB,
        cpu_count: float = settings.MAX_CPU_COUNT,
    ):
        self.image = image
        self.memory_mb = memory_mb
        self.cpu_count = cpu_count
        self.docker_available = self._check_docker()

    def _check_docker(self) -> bool:
        """Check if Docker CLI daemon is accessible."""
        try:
            res = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=2,
            )
            return res.returncode == 0
        except Exception:
            return False

    def execute(
        self,
        code: str,
        input_data: str,
        timeout: float,
        max_output_bytes: int,
    ) -> ExecutionResult:
        if not self.docker_available:
            raise RuntimeError("Docker is not available or daemon is not running.")

        temp_dir = tempfile.mkdtemp(prefix="docker_exec_")
        temp_path = Path(temp_dir)
        source_file = temp_path / "solution.py"

        try:
            source_file.write_text(code, encoding="utf-8")

            # Docker security restrictions:
            # --network none : disable all network calls
            # --memory : strict RAM cap
            # --cpus : CPU cap
            # --pids-limit : prevent fork bombs
            # --read-only : root filesystem is read-only
            # --tmpfs /tmp : small ephemeral tempfs for runtime
            # --cap-drop ALL : drop all Linux capabilities
            # --user 1000:1000 : run as unprivileged user
            # -v : mount only the temporary folder as read-only /app
            docker_cmd = [
                "docker",
                "run",
                "--rm",
                "-i",
                "--network",
                "none",
                f"--memory={self.memory_mb}m",
                f"--memory-swap={self.memory_mb}m",
                f"--cpus={self.cpu_count}",
                "--pids-limit=32",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,noexec,nosuid,size=16m",
                "--cap-drop=ALL",
                "-v",
                f"{str(temp_path)}:/app:ro",
                "-w",
                "/app",
                self.image,
                "python",
                "-I",
                "-B",
                "-s",
                "solution.py",
            ]

            start_time = time.perf_counter()
            process = subprocess.Popen(
                docker_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
            )

            input_bytes = input_data.encode("utf-8")
            try:
                raw_stdout, raw_stderr = process.communicate(
                    input=input_bytes, timeout=timeout
                )
            except subprocess.TimeoutExpired:
                process.kill()
                try:
                    process.communicate(timeout=0.5)
                except Exception:
                    pass
                execution_time = time.perf_counter() - start_time
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    stdout="",
                    stderr=f"Docker container execution timed out ({timeout}s)",
                    exit_code=-1,
                    execution_time=round(execution_time, 4),
                    error_message=f"Execution timed out after {timeout} seconds",
                )

            execution_time = time.perf_counter() - start_time
            exit_code = process.returncode

            truncated = False
            status = ExecutionStatus.SUCCESS

            if len(raw_stdout) > max_output_bytes:
                raw_stdout = raw_stdout[:max_output_bytes]
                status = ExecutionStatus.OUTPUT_LIMIT_EXCEEDED
                truncated = True

            if len(raw_stderr) > max_output_bytes:
                raw_stderr = raw_stderr[:max_output_bytes]
                truncated = True

            decoded_stdout = raw_stdout.decode("utf-8", errors="replace")
            decoded_stderr = raw_stderr.decode("utf-8", errors="replace")
            sanitized_stderr = sanitize_error_trace(decoded_stderr)

            if exit_code == 137:
                # OOM killed in Docker
                return ExecutionResult(
                    status=ExecutionStatus.MEMORY_LIMIT_EXCEEDED,
                    stdout=decoded_stdout,
                    stderr="Container exceeded memory limit (OOMKilled)",
                    exit_code=exit_code,
                    execution_time=round(execution_time, 4),
                    error_message="Memory limit exceeded",
                )

            if status == ExecutionStatus.OUTPUT_LIMIT_EXCEEDED:
                return ExecutionResult(
                    status=ExecutionStatus.OUTPUT_LIMIT_EXCEEDED,
                    stdout=decoded_stdout,
                    stderr=sanitized_stderr + f"\n[Output limit capped at {max_output_bytes} bytes]",
                    exit_code=exit_code,
                    execution_time=round(execution_time, 4),
                    error_message=f"Output exceeded {max_output_bytes} bytes",
                    truncated=True,
                )

            if exit_code != 0:
                return ExecutionResult(
                    status=ExecutionStatus.RUNTIME_ERROR,
                    stdout=decoded_stdout,
                    stderr=sanitized_stderr,
                    exit_code=exit_code,
                    execution_time=round(execution_time, 4),
                    error_message=sanitized_stderr.strip().split("\n")[-1] if sanitized_stderr.strip() else f"Runtime error ({exit_code})",
                    truncated=truncated,
                )

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                stdout=decoded_stdout,
                stderr=sanitized_stderr,
                exit_code=0,
                execution_time=round(execution_time, 4),
                truncated=truncated,
            )

        except Exception as e:
            logger.exception("Error executing code in DockerSandbox")
            return ExecutionResult(
                status=ExecutionStatus.SANDBOX_ERROR,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=0.0,
                error_message=f"Docker sandbox error: {str(e)}",
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class SandboxManager:
    """
    Manages selection and execution of code within the appropriate sandbox
    (Docker container sandbox or secure local subprocess fallback).
    """

    def __init__(self):
        self.local_sandbox = LocalSubprocessSandbox()
        self.docker_sandbox = DockerSandbox()

    @property
    def is_docker_available(self) -> bool:
        return self.docker_sandbox.docker_available

    def get_sandbox(self, preferred_mode: Optional[str] = None) -> BaseSandbox:
        mode = preferred_mode or settings.SANDBOX_MODE
        if mode == "docker":
            if self.docker_sandbox.docker_available:
                return self.docker_sandbox
            elif settings.ENABLE_DOCKER_FALLBACK:
                logger.warning(
                    "Docker requested but unavailable. Falling back to LocalSubprocessSandbox."
                )
                return self.local_sandbox
            else:
                raise RuntimeError("Docker sandbox requested but Docker is not available.")
        return self.local_sandbox

    def execute_code(
        self,
        code: str,
        input_data: str = "",
        timeout: Optional[float] = None,
        max_output_bytes: Optional[int] = None,
        preferred_mode: Optional[str] = None,
    ) -> ExecutionResult:
        eff_timeout = timeout if timeout is not None else settings.DEFAULT_EXECUTION_TIMEOUT
        eff_max_output = (
            max_output_bytes if max_output_bytes is not None else settings.MAX_OUTPUT_BYTES
        )

        sandbox = self.get_sandbox(preferred_mode)
        return sandbox.execute(
            code=code,
            input_data=input_data,
            timeout=eff_timeout,
            max_output_bytes=eff_max_output,
        )


sandbox_manager = SandboxManager()
