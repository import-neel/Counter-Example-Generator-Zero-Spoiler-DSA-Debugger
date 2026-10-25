
import requests

BASE_URL = "http://127.0.0.1:8000"


def get_problems():
    response = requests.get(
        f"{BASE_URL}/problems",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def debug_submission(
    problem_id,
    language,
    code,
    input_data=None,
    timeout=2,
    hint_level=1
):
    payload = {
        "problem_id": str(problem_id),
        "language": language,
        "code": code,
        "input": input_data,
        "timeout": timeout,
        "hint_level": hint_level
    }

    response = requests.post(
        f"{BASE_URL}/submissions/run",
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    return response.json()
