import os
from pathlib import Path
from app.services.sandbox_manager import sandbox_manager
from app.schemas.result_schema import ExecutionStatus


def test_sandbox_cleanup():
    """Verify that after execution, temporary execution folders are completely removed."""
    code = "import os\nprint(os.getcwd())"
    result = sandbox_manager.execute_code(code)
    assert result.status == ExecutionStatus.SUCCESS
    executed_dir = result.stdout.strip()
    assert os.path.isabs(executed_dir)
    # The directory should no longer exist
    assert not Path(executed_dir).exists(), f"Directory {executed_dir} was not cleaned up!"


def test_sandbox_local_mode_fallback():
    sandbox = sandbox_manager.get_sandbox("local")
    result = sandbox.execute("print('sandbox ok')", "", 2.0, 65536)
    assert result.status == ExecutionStatus.SUCCESS
    assert result.stdout.strip() == "sandbox ok"
