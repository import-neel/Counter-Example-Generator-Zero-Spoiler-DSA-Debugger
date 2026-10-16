import os
import requests

from dotenv import load_dotenv

from frontend.services.hint_generator import fallback_hint


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)


def debug_submission(
    problem_id,
    language,
    code,
    hint_level
):

    payload = {
        "problem_id": problem_id,
        "language": language,
        "code": code,
        "hint_level": hint_level
    }

    # --------------------------------
    # TRY REAL BACKEND
    # --------------------------------

    try:

        response = requests.post(
            f"{BACKEND_URL}/submissions/debug",
            json=payload,
            timeout=20
        )

        if response.ok:
            return response.json()

    except requests.RequestException:

        pass


    # --------------------------------
    # TEMPORARY MOCK RESPONSE
    # --------------------------------

    return mock_debug_result(
        problem_id,
        hint_level
    )


def mock_debug_result(
    problem_id,
    hint_level
):

    if problem_id == "two_sum_001":

        return {

            "status":
                "wrong_answer",

            "failure_type":
                "duplicate_handling",

            "counterexample": {

                "input":
                    "3\n2 2 1\n4",

                "expected_output":
                    "0 1",

                "actual_output":
                    "-1"
            },

            "hint":
                fallback_hint(
                    hint_level,
                    "duplicate_handling"
                ),

            "next_hint_available":
                hint_level < 5
        }


    return {

        "status":
            "wrong_answer",

        "failure_type":
            "boundary_condition",

        "counterexample": {

            "input":
                "1\n5\n5",

            "expected_output":
                "0",

            "actual_output":
                "-1"
        },

        "hint":
            fallback_hint(
                hint_level,
                "boundary_condition"
            ),

        "next_hint_available":
            hint_level < 5
    }