import ast
import re
from typing import Tuple, Optional


def check_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """
    Check if Python code parses without syntax errors before execution.
    Returns (is_valid, error_message).
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        msg = f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"
        return False, msg
    except Exception as e:
        return False, f"Parse error: {str(e)}"


def truncate_output(text: str, max_bytes: int) -> Tuple[str, bool]:
    """
    Safely truncate string to maximum allowed byte size without throwing decoding errors.
    Returns (truncated_text, was_truncated).
    """
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= max_bytes:
        return text, False
    truncated_bytes = encoded[:max_bytes]
    # Decode back safely
    truncated_text = truncated_bytes.decode("utf-8", errors="ignore")
    return truncated_text, True


def sanitize_error_trace(stderr: str) -> str:
    """
    Remove local system file paths from traceback messages to prevent internal structure leakage.
    """
    # Replace absolute system paths pointing to temp directories
    sanitized = re.sub(r'File ".*?[\\/]([^\\/]+\.py)"', r'File "\1"', stderr)
    return sanitized
