from typing import Optional
from app.config import settings
from app.schemas.result_schema import ExecutionResult, ExecutionStatus
from app.services.sandbox_manager import sandbox_manager
from app.utils.logger import logger
from app.utils.security import check_syntax


class CodeRunner:
    """
    Reusable execution engine for running submitted Python programs safely.
    Adheres strictly to the architectural contract for Teammate 2 & Teammate 3 integration.
    """

    def __init__(self, manager=None):
        self.manager = manager or sandbox_manager

    def run_code(
        self,
        code: str,
        input_data: str = "",
        timeout: Optional[float] = None,
        max_output_bytes: Optional[int] = None,
        sandbox_mode: Optional[str] = None,
    ) -> ExecutionResult:
        """
        Executes submitted Python code safely against standard input.

        Parameters:
        - code: Student source code
        - input_data: Stdin string passed to the process
        - timeout: Maximum allowed execution time in seconds
        - max_output_bytes: Maximum allowed bytes for stdout/stderr
        - sandbox_mode: 'local' or 'docker' (defaults to config settings)

        Returns:
        - ExecutionResult schema (status, stdout, stderr, exit_code, execution_time)
        """
        # 1. Input validation & sanity checks
        if not code or not code.strip():
            return ExecutionResult(
                status=ExecutionStatus.RUNTIME_ERROR,
                stdout="",
                stderr="Error: Code submission is empty.",
                exit_code=-1,
                execution_time=0.0,
                error_message="Empty code submission",
            )

        # 2. Pre-execution AST Syntax check
        is_valid_syntax, syntax_error = check_syntax(code)
        if not is_valid_syntax:
            logger.info("Submission syntax error detected prior to execution")
            return ExecutionResult(
                status=ExecutionStatus.SYNTAX_ERROR,
                stdout="",
                stderr=syntax_error or "SyntaxError in submitted code",
                exit_code=1,
                execution_time=0.0,
                error_message=syntax_error,
            )

        # 3. Execution inside sandbox
        logger.info(
            "Executing code submission (size=%d chars, input_size=%d chars)",
            len(code),
            len(input_data),
        )

        result = self.manager.execute_code(
            code=code,
            input_data=input_data,
            timeout=timeout,
            max_output_bytes=max_output_bytes,
            preferred_mode=sandbox_mode,
        )

        logger.info(
            "Execution completed with status=%s, exit_code=%d, time=%.3fs",
            result.status.value,
            result.exit_code,
            result.execution_time,
        )

        return result


code_runner = CodeRunner()


def run_code(
    code: str,
    input_data: str = "",
    timeout: Optional[float] = None,
    max_output_bytes: Optional[int] = None,
    sandbox_mode: Optional[str] = None,
) -> ExecutionResult:
    """
    Direct functional entrypoint for Teammate 2 differential testing & counterexample generators:
    result = run_code(student_code, test_input)
    """
    return code_runner.run_code(
        code=code,
        input_data=input_data,
        timeout=timeout,
        max_output_bytes=max_output_bytes,
        sandbox_mode=sandbox_mode,
    )
